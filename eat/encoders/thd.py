from pathlib import Path
from typing import Any

from eat.encoders._dee import DeeEncoder


class Encoder(DeeEncoder):
    """Dolby TrueHD encoder class"""
    extension: str = '.thd'

    def _configure(
        self,
        *,
        input_path: Path,
        output_path: Path,
        temp_dir: Path,
        **_: Any
    ) -> None:
        self._load_xml(self._config_dir / 'thd.xml')

        config = self._config['job_config']
        self._temp_dir = temp_dir

        # Configure input paths
        config['input']['audio']['wav']['storage']['local']['path'] = '"%s"' % temp_dir
        config['input']['audio']['wav']['file_name'] = '"%s"' % input_path.name
        # Configure output paths
        config['output']['mlp']['file_name'] = '"%s"' % output_path.name
        config['output']['mlp']['storage']['local']['path'] = '"%s"' % Path.cwd()

        # Configure temp file location
        config['misc']['temp_dir']['path'] = '"%s"' % temp_dir

        self._config['job_config'] = config
        self._filename = output_path.name

        # Remove log and config files
        self._to_remove.extend((
            output_path.with_suffix('.thd.log'),
            output_path.with_suffix('.thd.mll'),
        ))
