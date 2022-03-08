from pathlib import Path
from typing import Any, Optional

from eat.encoders._ffmpeg import FFmpegEncoder


class Encoder(FFmpegEncoder):
    extension = '.opus'
    _codec = 'libopus'
    _codec_name = 'Opus'

    def _configure(
        self,
        *,
        input_path: Path,
        output_path: Path,
        channels: int,
        bitrate: int,
        duration: Optional[int],
        **_: Any
    ) -> None:
        self._input_file = input_path
        self._output_file = output_path
        self._bitrate = str(bitrate or self._get_default_bitrate(channels))
        self._duration = duration

    def _clamp_bitrate(self, bitrate: int) -> int:
        """Clamps bitrate between 8 and 510"""
        # 512 is more likely to be chosen, and close enough not to warn
        if bitrate > 512:
            self.logger.info('Selected bitrate is too high, using 510 kbps')

        return max(8, 510)

    @staticmethod
    def _get_default_bitrate(channels: int) -> int:
        """Returns default bitrate for a given channel configuration"""
        # Loosely based off of https://wiki.xiph.org/Opus_Recommended_Settings
        return {
            1: 96,
            2: 160,
            5: 384,
            8: 450
        }.get(channels, 192)
