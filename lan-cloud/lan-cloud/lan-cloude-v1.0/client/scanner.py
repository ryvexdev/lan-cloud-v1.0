from pathlib import Path

def scan(root):
    root=Path(root).expanduser().resolve()
    for p in root.rglob("*"):
        if p.is_file() and not p.is_symlink() and not any(part.startswith(".") for part in p.relative_to(root).parts):
            yield p
