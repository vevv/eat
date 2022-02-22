import subprocess
from io import BytesIO
from typing import Optional, cast
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
    _extra_params: Optional[list] = []

    def __init__(self, path: Path):
        super().__init__(path)

    def __call__(self, *args, **kwargs):
        self._duration = kwargs.get('duration')  # microseconds
        super().__call__(*args, **kwargs)

    def _configure(self, *args, **kwargs):
        """Configures encoding params"""
        raise NotImplementedError

    def _encode(self):
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
                '-b:a', '%sk' % self._bitrate,
                self._output_file
            ],
            output_handler=self._rich_handler
        )

    def _rich_handler(self, process):
        """Handles Rich progress bar"""
        if not self._duration or self._duration < 0:
            return self._simple_handler(process)

        with Progress() as pb:
            task = pb.add_task(
                f'Converting {self._input_file.name} to {self._codec_name}',
                total=self._duration
            )

            with cast(BytesIO, process.stdout):
                for _ in iter(process.stdout.readline, ''):
                    line = process.stdout.readline()
                    if '=' not in line:
                        continue
                    key, val = line.split('=')
                    if key == 'out_time_us':
                        pb.update(task_id=task, completed=int(val))

            # Manually update to 100% in case last progress update was outdated
            pb.update(task_id=task, completed=self._duration)

        with cast(BytesIO, process.stderr):
            for line in iter(process.stderr.readline, ''):
                if 'error' in line.lower():
                    self.logger.error(line.rstrip())

    def _simple_handler(self, process):
        """Handles simple (native ffmpeg) progress output"""
        self.logger.info(f'Converting {self._input_file.name} to {self._codec_name}')
        with cast(BytesIO, process.stderr):
            for line in iter(process.stderr.readline, ''):
                if 'error' in line.lower():
                    self.logger.error(line.rstrip())
                else:
                    print(line.rstrip(), end='\r')
