import os
import re
import subprocess
from pathlib import Path
from typing import Optional, TextIO, cast

import xmltodict
from rich.progress import Progress

from eat.encoders._base import BaseEncoder
from eat.utils.tempfile import get_temp_file


class DeeEncoder(BaseEncoder):
    """Dolby Encoding Engine encoder base class"""
    extension: str
    binary_name: str = 'dee'
    _config: dict
    _temp_dir: Path
    _filename: str  # display only

    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self._config_dir = Path(__file__).resolve().parent.parent / 'data' / 'xml'

    def _load_xml(self, config_path: Path) -> None:
        """Loads config xml into an editable dict"""
        self._config = xmltodict.parse(
            config_path.read_text(),
            dict_constructor=dict
        )

    def _encode(self) -> None:
        """Starts an encoding process"""
        file = get_temp_file(suffix='.xml', directory=self._temp_dir)
        with file.open(mode='w', encoding='utf-8') as f:
            f.write(self._export_xml(self._config))

        self._processor.call_process_output(
            params=[
                self._path,
                '--xml', str(file),
                '--verbose', 'info',
                '--progress-interval', '500',  # update progress every 500 ms (minimum allowed)
                '--diagnostics-interval', "%01d" % 9e9,  # 0/-1 don't work to shut it up
            ],
            output_handler=self._rich_handler
        )
        file.unlink()

    def _rich_handler(self, process: subprocess.Popen) -> None:
        """Handles Rich progress bar"""
        with Progress() as pb:
            task = pb.add_task(self._get_task_name(), total=100)

            with cast(TextIO, process.stdout) as stdout:
                for line in iter(stdout.readline, ''):
                    self.logger.debug(line.split(']', 1)[-1].strip())
                    if 'error' in line.lower():
                        self.logger.error(line.rstrip().split(': ', 1)[1])

                    progress = re.search(
                        r'Overall progress: ([0-9]+\.[0-9])',
                        line
                    )
                    if progress:
                        pb.update(task_id=task, completed=float(progress[1]))

            # Manually update to 100% in case last progress update was outdated
            pb.update(task_id=task, completed=100)

    def _get_task_name(self) -> str:
        """Returns task name for Rich progress bar"""
        return f'Encoding "{self._filename}"" with DEE'

    @staticmethod
    def _export_xml(xml_data: dict) -> str:
        """Exports config dict to a DEE-readable XML file"""
        return cast(str, xmltodict.unparse(xml_data, pretty=True, indent=' ' * 4))
