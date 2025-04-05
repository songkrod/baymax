from pathlib import Path
import json

def ensure_file(path: str, default_content=None):
    """
    Ensures a file exists at the given path.
    If default_content is None, creates an empty file.
    If default_content is provided, treats it as JSON content.
    """
    fpath = Path(path)
    fpath.parent.mkdir(parents=True, exist_ok=True)
    
    if not fpath.exists():
        with open(fpath, "w", encoding="utf-8") as f:
            if default_content is not None:
                json.dump(default_content, f, ensure_ascii=False, indent=2)
            # If default_content is None, just create an empty file
    
    return fpath