import json
import subprocess
from pathlib import Path
from typing import cast, Optional, TextIO

from eat.utils.processor import Processor


class FFprobe:
    """ffprobe reading utility class"""

    def __init__(self, path: Path):
        self._path: Path = path
        self._processor: Processor = Processor()
        self._log: Optional[dict] = None

    def __call__(self, file: Path) -> dict:
        self._processor.call_process_output(
            params=[
                self._path,
                '-v', 'quiet',
                '-select_streams', 'a:0',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file
            ],
            output_handler=self._reader
        )
        return cast(dict, self._log)

    def _reader(self, process: subprocess.Popen) -> None:
        process.wait()
        with cast(TextIO, process.stdout) as stdout:
            self._log = json.loads(stdout.read())
