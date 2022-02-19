import logging
import sys
from typing import Optional
from pathlib import Path

import xmltodict

from eat.utils.processor import Processor


class BaseEncoder:
    extension: str
    binary_name: str
    supported_inputs: list = ['pcm']
    _temp_dir: Optional[Path] = None
    _to_remove: list = []

    def __init__(self, path: Path):
        self._path = path
        self._processor = Processor()
        self.logger = logging.getLogger(sys.modules[self.__module__].__name__)

    def __call__(self, *args, **kwargs):
        self._configure(*args, **kwargs)
        self._encode()

    def _configure(self):
        """Configures encoding params"""
        raise NotImplementedError

    def _encode(self):
        """Starts an encoding process"""
        raise NotImplementedError
