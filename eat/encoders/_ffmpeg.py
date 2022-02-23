import subprocess
from typing import Any, Optional, cast, TextIO
from pathlib import Path

from rich.progress import Progress

from eat.encoders._base import BaseEncoder


class FFmpegEncoder(BaseEncoder):
    """FFmpeg encoder base class"""
    extension: str
    binary_name: str = 'ffmpeg'
    supported_inputs: list = ['all']
    _codec_name: str  # display only
    _codec: str  # ffmpeg codec value
    _extra_params: list = []
    _duration: Optional[int]  # microseconds

    def __init__(self, path: Path) -> None:
        super().__init__(path)

    def _encode(self) -> None:
        """Starts an encoding process"""
        self._processor.call_process_output(
            params=[
                self._path,
                '-loglevel', 'panic',
                '-stats',
                '-y',
                '-progress', 'pipe:1',
                '-drc_scale', '0',
                '-i', self._input_file,
                '-c:a', self._codec,
                *self._extra_params,
                '-b:a', f'{self._bitrate}k',
                self._output_file
            ],
            output_handler=self._rich_handler
        )

    def _rich_handler(self, process: subprocess.Popen) -> None:
        """Handles Rich progress bar"""
        if not self._duration or self._duration < 0:
            return self._simple_handler(process)

        with Progress() as pb:
            task = pb.add_task(
                f'Converting {self._input_file.name} to {self._codec_name}',
                total=self._duration
            )

            with cast(TextIO, process.stdout) as stdout:
                for _ in iter(stdout.readline, ''):
                    line = stdout.readline()
                    if '=' not in line:
                        continue
                    key, val = line.split('=')
                    if key == 'out_time_us':
                        pb.update(task_id=task, completed=int(val))

            # Manually update to 100% in case last progress update was outdated
            pb.update(task_id=task, completed=self._duration)

        with cast(TextIO, process.stderr) as stderr:
            for line in iter(stderr.readline, ''):
                self.logger.debug(line.strip())
                if 'error' in line.lower():
                    self.logger.error(line.rstrip())

    def _simple_handler(self, process: subprocess.Popen) -> None:
        """Handles simple (native ffmpeg) progress output"""
        self.logger.info(f'Converting {self._input_file.name} to {self._codec_name}')
        with cast(TextIO, process.stderr) as stderr:
            for line in iter(stderr.readline, ''):
                if 'error' in line.lower():
                    self.logger.error(line.rstrip())
                else:
                    print(line.rstrip(), end='\r')
