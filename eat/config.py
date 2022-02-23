import logging
import shutil
import sys
from pathlib import Path

import toml


class Config:
    _config_dir: Path = Path('~/.eat').expanduser()
    _config_path: Path = _config_dir / 'config.toml'
    _example_config: Path = Path(__file__).resolve().parent / 'data' / 'config.toml.example'

    def __init__(self) -> None:
        self.logger = logging.getLogger(sys.modules[self.__module__].__name__)
        self._config_dir.mkdir(exist_ok=True)

        if not self._config_path.exists():
            example_path = (self._config_dir / 'config.toml.example')
            self.logger.error(
                'Configuration file not found, created an example file at %s',
                example_path
            )
            shutil.copy(self._example_config, example_path)
            raise SystemExit

    def load(self) -> dict:
        with self._config_path.open(mode='r', encoding='utf-8') as f:
            config = toml.load(f)

        return config
