from typing import Optional
from pathlib import Path

from eat.encoders._base import BaseEncoder


class Encoder(BaseEncoder):
    """Free Lossless Audio Codec (FLAC) encoder class"""
    extension = '.flac'
    binary_name: str = 'sox'
    supported_inputs: list = ['pcm', 'rf64', 'flac', 'aiff']
    _bitrate = '0'  # bitrate irrelevant for a lossless codec
    _params: Optional[list] = []

    def __init__(self, path: Path):
        super().__init__(path)

    def _configure(self, *args, **kwargs):
        self._input_file = kwargs['input_path']
        self._output_file = kwargs['output_path']

    def _encode(self):
        # sox progress is not easily readable from subprocess
        # so don't surpress output
        self._processor.call_process(
            params=[
                self._path,
                '-V0',
                '--show-progress',
                self._input_file,
                '--compression', '8',
                self._output_file,
                *self._params
            ],
        )
