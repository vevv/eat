from pathlib import Path
from typing import Any, Optional

from eat.encoders._ffmpeg import FFmpegEncoder


class Encoder(FFmpegEncoder):
    extension = '.wav'
    _codec_name = 'rf64'
    _extra_params = ['-rf64', 'always', '-fflags', '+bitexact']
    _bitrate = '0'  # bitrate irrelevant for a lossless codec

    def _configure(self, *,
        input_path: Path,
        output_path: Path,
        duration: Optional[int],
        bitdepth: Optional[int],
        **_: Any
    ) -> None:
        """Configures encoding params"""
        self._input_file = input_path
        self._output_file = output_path
        self._codec = 'pcm_s%sle' % bitdepth or '16'
        self._duration = duration
