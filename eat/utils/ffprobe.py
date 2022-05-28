import json
import subprocess
from pathlib import Path
from typing import Optional, TextIO, cast

from eat.utils.processor import ProcessingError, Processor


class AudioInfo:
    """Utility class parsing ffprobe results into an easier to read form"""
    codec: str
    sample_rate: int
    bitdepth: int
    channels: int
    profile: str = ''  # mainly for DTS
    duration: float  # microseconds

    def __init__(self, log: dict) -> None:
        if not log['streams']:
            raise ProcessingError('No streams found')

        stream = log['streams'][0]
        self.codec = stream['codec_name']
        self.container = log['format']['format_name']
        self.sample_rate = int(stream['sample_rate'])
        self.bitdepth = int(
            stream.get('bits_per_sample', 0) or stream.get('bits_per_raw_sample', 32)
        )
        self.channels = stream.get('channels', 0)
        self.profile = stream.get('profile', '')
        # convert seconds to microseconds for ffmpeg compatibility
        self.duration = float(stream.get('duration', -1)) * 1000000


class FFprobe:
    """ffprobe reading utility class"""

    def __init__(self, path: Path) -> None:
        self._path: Path = path
        self._processor: Processor = Processor()
        self._log: Optional[dict] = None

    def __call__(self, file: Path) -> AudioInfo:
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
        return AudioInfo(cast(dict, self._log))

    def _reader(self, process: subprocess.Popen) -> None:
        process.wait()
        with cast(TextIO, process.stdout) as stdout:
            self._log = json.loads(stdout.read())
