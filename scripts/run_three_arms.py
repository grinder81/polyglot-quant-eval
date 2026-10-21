"""Sequential, logged local baseline execution using the existing upstream servers."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    selection = p.add_mutually_exclusive_group()
    selection.add_argument('--local-q4-only', action='store_true',
                   help='Evaluate the approved local control without rerunning the existing arms')
    selection.add_argument('--bf16-gguf-only', action='store_true',
                          help='Run only the matched BF16 GGUF reference')
    p.add_argument('--start', type=int, default=0)
    p.add_argument('--count', type=int, default=50)
    args = p.parse_args()
    root, output = args.root, args.output
    output.mkdir(parents=True, exist_ok=True)
    runner = Path(__file__).with_name('run_shards.py')
    lib = root / 'llama-tokenizer-pinned-fix/build/bin'
    original = root / 'models/tiny-aya-global'
    models = [('q4', root / 'models/tiny-aya-global-GGUF/tiny-aya-global-q4_k_m.gguf'),
              ('bf16-gguf', root / 'models/tiny-aya-global-control-bf16.gguf'),
              ('bf16-vllm', original)]
    if args.local_q4_only:
        models = [('local-q4', root / 'models/tiny-aya-global-local-q4_k_m.gguf')]
    elif args.bf16_gguf_only:
        models = [models[1]]
    for arm, model in models:
        is_vllm = arm == 'bf16-vllm'
        env = os.environ.copy()
        python = root / ('vllm/bin/python' if is_vllm else 'llama-python-compat/bin/python')
        if is_vllm:
            env['VLLM_USE_V2_MODEL_RUNNER'] = '0'
            env['PATH'] = str(root / 'vllm/bin') + ':/usr/local/cuda/bin:/usr/bin:/bin'
            server = [str(root / 'vllm/bin/vllm'), 'serve', str(model),
                      '--served-model-name', 'tiny-aya-global', '--dtype', 'bfloat16',
                      '--max-model-len', '8192', '--gpu-memory-utilization', '0.5',
                      '--enforce-eager', '--host', '127.0.0.1', '--port', '8098']
        else:
            env['LLAMA_CPP_LIB_PATH'] = str(lib)
            server = [str(python), '-m', 'llama_cpp.server', '--model', str(model),
                      '--n_gpu_layers', '-1', '--n_ctx', '8192', '--logits_all', 'true',
                      '--host', '127.0.0.1', '--port', '8098', '--verbose', 'false']
        files = sorted(model.glob('*.safetensors')) + sorted(model.glob('*.json')) if is_vllm else [model]
        if not is_vllm:
            files += [lib / 'libllama.so', root / 'llama-python-compat/lib/python3.13/site-packages/llama_cpp/llama.py',
                      root / 'llama-python-compat/lib/python3.13/site-packages/llama_cpp/_internals.py']
        manifest = output / (arm + '-runtime.json')
        identity = {'arm': arm, 'server_command': server,
                    'files': {str(f): sha(f) for f in files},
                    'packages': subprocess.check_output([str(python), '-c',
                        "import importlib.metadata as m; print('\\n'.join(sorted(d.metadata['Name']+'=='+d.version for d in m.distributions())))"], text=True)}
        if manifest.exists():
            assert json.loads(manifest.read_text()) == identity, 'Runtime changed'
        else:
            manifest.write_text(json.dumps(identity, indent=2))
        with (output / (arm + '-server.log')).open('a') as log:
            process = subprocess.Popen(server, env=env, stdout=log, stderr=subprocess.STDOUT)
            try:
                for _ in range(300):
                    if process.poll() is not None:
                        raise RuntimeError(f'{arm} server exited; see log')
                    try:
                        with urllib.request.urlopen('http://127.0.0.1:8098/v1/models', timeout=2):
                            break
                    except OSError:
                        time.sleep(1)
                else:
                    raise TimeoutError('Server not ready')
                client_env = env.copy()
                client_python = python if is_vllm else root / 'eval/bin/python'
                if is_vllm:
                    client_env['PYTHONPATH'] = str(root / 'eval/lib/python3.13/site-packages')
                command = [str(client_python), str(runner), '--lock', str(root / 'pilot/sample-lock.json'),
                           '--runtime-manifest', str(manifest), '--directory', str(output / arm),
                           '--arm', arm, '--start', str(args.start), '--count', str(args.count),
                           '--base-url', 'http://127.0.0.1:8098' + ('/v1/completions' if is_vllm else '')]
                if is_vllm:
                    command += ['--backend', 'local-completions', '--tokenizer', str(original)]
                subprocess.run(command, env=client_env, check=True)
            finally:
                process.terminate()
                try:
                    process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


if __name__ == '__main__':
    main()
