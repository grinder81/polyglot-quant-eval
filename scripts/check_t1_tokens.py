"""T1 GGUF vocabulary-only identity/roundtrip check; no model inference."""
import argparse
import json
from pathlib import Path
from scripts.t1_baselines import read, require, validate_lock
from scripts.run_scoring_variants import sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('lock','model','runtime','output'):
        p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args()
    require(not a.output.exists(),'Output must be new')
    rows=validate_lock(read(a.lock))
    from llama_cpp import Llama, llama_cpp as native
    import llama_cpp._internals as internals
    import llama_cpp.llama as wrapper
    runtime=read(a.runtime)
    required=(a.model,native._lib._name,internals.__file__,wrapper.__file__)
    require(all(str(f) in runtime['files'] and sha(f)==runtime['files'][str(f)] for f in required),
            'Vocabulary environment is not the pinned runtime; set LLAMA_CPP_LIB_PATH')
    model=Llama(model_path=str(a.model),vocab_only=True,n_gpu_layers=0,verbose=False)
    failures=[]
    for row in rows:
        for i,(text,expected) in enumerate(zip([row['prompt']]+[row['prompt']+c for c in row['candidates']],
                [row['model_context_ids']]+row['model_token_ids'],strict=True)):
            actual=model.tokenize(text.encode(),add_bos=True,special=True)
            if actual!=expected or actual[0]!=model.token_bos() or model.detokenize(actual[1:],special=True).decode()!=text:
                failures.append(dict(language=row['language'],index=row['index'],candidate=i-1))
    report=dict(scope='vocab_only=True, n_gpu_layers=0; no inference',lock_sha256=sha(a.lock),
        runtime_sha256=sha(a.runtime),contexts=900,candidates=3600,failures=failures,model=str(a.model),
        files={str(f):sha(f) for f in (a.model,native._lib._name,internals.__file__,wrapper.__file__,__file__)})
    with a.output.open('x',encoding='utf-8') as f:
        json.dump(report,f,indent=2,allow_nan=False)
    require(not failures,'T1 vocabulary check failed')
    print('900 contexts + 3600 candidates passed; no inference')


if __name__=='__main__':
    main()
