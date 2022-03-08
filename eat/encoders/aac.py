import re
import subprocess
from pathlib import Path
from typing import Any, Optional, TextIO, cast

from rich.progress import Progress

from eat.encoders._base import BaseEncoder


class Encoder(BaseEncoder):
    """AAC (Advanced Audio Coding) encoder class"""
    extension = '.m4a'
    binary_name: str = 'qaac'
    supported_inputs: list = ['pcm', 'rf64', 'alac', 'mp3', 'aac']

    def __init__(self, path: Path) -> None:
        super().__init__(path)

    def _configure(
        self,
        *,
        input_path: Path,
        output_path: Path,
        bitrate: Optional[int] = None,
        **_: Any
    ) -> None:
        self._input_file = input_path
        self._output_file = output_path
        self._filename = output_path.name
        self._quality = self._clamp_quality_level(bitrate or 127)

    def _encode(self) -> None:
        self._processor.call_process_output(
            params=[
                self._path,
                '-V', self._quality,
                '--no-delay',
                self._input_file,
                '-o',
                self._output_file
            ],
            output_handler=self._rich_handler
        )

    def _clamp_quality_level(self, user_level: int) -> str:
        """Clamps quality level to usable values"""
        # This is technically not necessary as qaac does this internally
        # but it's good to give user a warning
        levels = [0, 9, 18, 27, 36, 45, 54, 63, 73, 82, 91, 100, 109, 118, 127]

        quality_level = min(levels, key=lambda level: abs(user_level - level))
        if user_level not in levels:
            self.logger.info('Quality level %s will be rounded to %s',
                             user_level, quality_level)

        return str(quality_level)

    def _rich_handler(self, process: subprocess.Popen) -> None:
        """Handles Rich progress bar"""
        with Progress() as pb:
            task = pb.add_task(f'Encoding {self._filename} with qaac', total=100)

            with cast(TextIO, process.stderr) as stderr:
                for _ in iter(stderr.readline, ''):
                    line = stderr.readline()
                    self.logger.debug(line.strip())
                    if 'Overall bitrate' in line:
                        pb.update(task_id=task, completed=100)
                        break

                    if 'error' in line.lower():
                        self.logger.error(line.rstrip().split(': ', 1)[1])

                    progress = re.search(r'\[([0-9]+\.[0-9]+)%\]', line)
                    if progress:
                        pb.update(task_id=task, completed=float(progress[1]))

            # Manually update to 100% in case last progress update was outdated
            pb.update(task_id=task, completed=100)
