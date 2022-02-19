import os
import tempfile
from pathlib import Path
from typing import Optional


def get_temp_file(suffix: Optional[str], directory: Optional[Path]):
    fd, path = tempfile.mkstemp(suffix=suffix, dir=directory)
    os.close(fd)  # we don't need this
    return Path(path)
