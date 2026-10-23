"""Render stored, complete T1 estimates; does not rerun scientific analysis."""
from pathlib import Path
import gzip, hashlib, json
import matplotlib.pyplot as plt
root = Path(__file__).resolve().parent
raw = gzip.decompress((root / "evidence/validated-report.json.gz").read_bytes())
assert hashlib.sha256(raw).hexdigest() == "c1ffee6b6030b1d5beb6c6afe3d855c1e1703df3e2fd6329270b06d55a1941a1"
r = json.loads(raw)["fresh_paired_GGUF"]["languages"]
fig, axes = plt.subplots(1, 2, figsize=(10, 3.7), layout="constrained")
for ax, key, bound, title in zip(axes,
    ["accuracy_delta_candidate_minus_reference", "delta_minus_english_delta"],
    ["paired_cluster_95_delta_interval", "paired_cluster_95_delta_minus_english_interval"],
    ["Q4 minus BF16 GGUF accuracy", "Compression delta minus English delta"]):
    for y, (lang, name) in enumerate(zip(["eng_Latn","ben_Beng","hin_Deva"], ["English","Bangla","Hindi"])):
        if key == "delta_minus_english_delta" and y == 0:
            ax.text(6.1,y,"Reference",va="center",fontsize=9)
            continue
        v=r[lang]; x=100*v[key]; lo,hi=[100*z for z in v[bound]]
        ax.plot([lo,hi],[y,y],color="#275C8A",lw=2)
        ax.plot(x,y,"o",color="#275C8A")
        ax.text(6.1,y,f"{x:+.2f} [{lo:+.2f}, {hi:+.2f}]",va="center",fontsize=9)
    ax.axvline(0,color="#555555",lw=1,ls="--")
    ax.set(yticks=[0,1,2],yticklabels=["English","Bangla","Hindi"],ylim=(2.5,-.5),xlim=(-6,13),xticks=[-5,0,5],xlabel="Percentage points",title=title)
    ax.spines[["top","right"]].set_visible(False)
fig.suptitle("Fresh T1: original-order Belebele development comparison",fontsize=13)
fig.supxlabel("300 questions/language; 250 shared source clusters; paired 95% bootstrap intervals (10,000 draws, seed 42)",fontsize=9)
fig.savefig(root / "fresh-compression.png",dpi=180)
fig.savefig(root / "fresh-compression.svg")
