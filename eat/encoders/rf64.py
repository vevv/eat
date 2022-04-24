from pathlib import Path
from typing import Any, Optional

from eat.encoders._ffmpeg import FFmpegEncoder


class Encoder(FFmpegEncoder):
    extension = '.wav'
    _codec_name = 'rf64'
    _extra_params = ['-rf64', 'always', '-fflags', '+bitexact']
    _bitrate = '0'  # bitrate irrelevant for a lossless codec

    def _configure(
        self,
        *,
        input_path: Path,
        output_path: Path,
        duration: Optional[int],
        bitdepth: Optional[int],
        sample_rate: Optional[int],
        filter_complex: Optional[str] = None,
        **_: Any
    ) -> None:
        """Configures encoding params"""
        self._input_file = input_path
        self._output_file = output_path
        self._codec = 'pcm_s%sle' % bitdepth or '16'
        self._duration = duration
        if sample_rate:
            self.logger.info('Resampling to %s Hz', sample_rate)
            self._extra_params.extend(self._resample_params(sample_rate))

        if filter_complex:
            self.logger.debug('Running filter_complex: "%s"', filter_complex)
            self._extra_params.extend(['-filter_complex', filter_complex])
