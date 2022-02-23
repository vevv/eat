import logging
import sys
from typing import Any, Optional
from pathlib import Path

import xmltodict

from eat.utils.processor import Processor


class BaseEncoder:
    extension: str
    binary_name: str
    supported_inputs: list[str] = ['pcm']
    _input_file: Path
    _output_file: Path
    _bitrate: str = '0'  # can't parse int to subprocess, use 0 for lossless
    _temp_dir: Path
    _to_remove: list[Path] = []

    def __init__(self, path: Path) -> None:
        self._path = path
        self._processor = Processor()
        self.logger = logging.getLogger(sys.modules[self.__module__].__name__)

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        self._configure(*args, **kwargs)
        self._encode()

    # Each encoder takes different params, BaseEncoder lists all possible ones
    def _configure(self,
        input_path: Path,
        output_path: Path,
        bitdepth: int,
        duration: Optional[int],
        bitrate: Optional[int],
        channels: int,
        temp_dir: Path,
        remix: bool = False,
        surround_ex: bool = False
    ) -> None:
        """Configures encoding params"""
        raise NotImplementedError


    def _encode(self) -> None:
        """Starts an encoding process"""
        raise NotImplementedError
