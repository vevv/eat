import os
import tempfile
from pathlib import Path
from typing import Optional


def get_temp_file(suffix: Optional[str], directory: Optional[Path]) -> Path:
    """Returns a temp file Path"""
    fd, path = tempfile.mkstemp(suffix=suffix, dir=directory)
    os.close(fd)  # we don't need this
    return Path(path)
