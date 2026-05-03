"""`boreddocs new <dir>` — copy the bundled sample-district scaffold."""

import shutil
from importlib import resources
from pathlib import Path


def scaffold(target: Path) -> Path:
    target = Path(target).resolve()
    if target.exists() and any(target.iterdir()):
        raise FileExistsError(f"Target exists and is not empty: {target}")
    target.mkdir(parents=True, exist_ok=True)

    src = resources.files("boreddocs") / "_scaffold" / "sample-district"
    src_path = Path(str(src))
    if not src_path.exists():
        # Fallback for editable installs: walk the repo `examples/` dir.
        repo_root = Path(__file__).resolve().parents[2]
        src_path = repo_root / "examples" / "sample-district"
    if not src_path.exists():
        raise FileNotFoundError("sample-district scaffold not found in package")

    for p in src_path.rglob("*"):
        rel = p.relative_to(src_path)
        dst = target / rel
        if p.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
    return target
