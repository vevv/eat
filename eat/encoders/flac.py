from pathlib import Path
from typing import Any, List, Optional, overload

from eat.encoders._base import BaseEncoder


class Encoder(BaseEncoder):
    """Free Lossless Audio Codec (FLAC) encoder class"""
    extension = '.flac'
    binary_name: str = 'sox'
    supported_inputs: List['str'] = ['pcm', 'rf64', 'flac', 'aiff', 'mp3']
    _params: List[str] = []

    def __init__(self, path: Path):
        super().__init__(path)

    def _configure(
        self,
        *,
        input_path: Path,
        output_path: Path,
        duration: Optional[int],
        **_: Any
    ) -> None:
        self._input_file = input_path
        self._output_file = output_path
        self._duration = duration

    def _encode(self) -> None:
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
