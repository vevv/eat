from pathlib import Path
from typing import Any, Optional

from eat.encoders._dee import DeeEncoder


ALLOWED_BITRATES = [
    # Standard profile
    32, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120, 128, 144, 160, 176, 192, 200, 208, 216, 224, 232, 240, 248,
    256, 272, 288, 304, 320, 336, 352, 368, 384, 400, 448, 512, 576, 640, 704, 768, 832, 896, 960, 1008, 1024,
    # Blu-ray profile
    1280, 1536, 1664
]


class Encoder(DeeEncoder):
    """Dolby Digital Plus (E-AC-3) encoder class"""
    extension: str = '.ec3'
    extension_bd: str = '.eb3'
    supported_sample_rates = [48000]
    _allowed_bitrates = ALLOWED_BITRATES
    _minimal_bitrates = {6: 192, 8: 384}

    def _configure(
        self,
        *,
        input_path: Path,
        output_path: Path,
        bitrate: Optional[int],
        channels: int,
        temp_dir: Path,
        remix: bool = False,
        **_: Any
    ) -> None:
        self._load_xml(self._config_dir / 'ddp.xml')

        config = self._config['job_config']
        self._temp_dir = temp_dir

        # Configure encoder
        bitrate = self._clamp_bitrate(
            bitrate=bitrate or self._get_default_bitrate(channels),
            channels=channels
        )

        mix = self._get_mix(channels)
        if remix:
            self.logger.warning('Remixing audio to %s', mix)

        # Upmix to 7.1 requires different encoder mode and extension
        if mix == '7.1':
            config['filter']['audio']['pcm_to_ddp']['encoder_mode'] = 'ddp71'
            mix = 'off'
        else:
            config['filter']['audio']['pcm_to_ddp']['encoder_mode'] = 'ddp'

        # Bitrates above 1024k are only supported with Blu-ray profile
        if bitrate > 1024:
            config['filter']['audio']['pcm_to_ddp']['encoder_mode'] = 'bluray'
            output_path = output_path.with_suffix(self.extension_bd)

        # Set bitrate/channel configuration
        config['filter']['audio']['pcm_to_ddp']['data_rate'] = bitrate
        config['filter']['audio']['pcm_to_ddp']['downmix_config'] = mix

        # Configure input paths
        config['input']['audio']['wav']['file_name'] = '"%s"' % input_path.name
        config['input']['audio']['wav']['storage']['local']['path'] = '"%s"' % input_path.resolve().parent
        # Configure output paths
        config['output']['ec3']['file_name'] = '"%s"' % output_path.name
        config['output']['ec3']['storage']['local']['path'] = '"%s"' % output_path.resolve().parent
        # Configure temp file location
        config['misc']['temp_dir']['path'] = '"%s"' % temp_dir

        self._config['job_config'] = config
        self._filename = output_path.name

    def _clamp_bitrate(self, bitrate: int, channels: int = 0) -> int:
        """Clamps bitrate to the nearest allowed value"""
        nearest = min(self._allowed_bitrates, key=lambda abr: abs(abr - bitrate))
        minimal = self._minimal_bitrates.get(channels, 0)
        selected = max(minimal, nearest)
        if nearest < minimal or bitrate < self._allowed_bitrates[0]:
            self.logger.info(
                'Selected bitrate is too low for %s channels, using %s kbps',
                channels, selected
            )
        elif selected != bitrate:
            self.logger.info('Rounding bitrate to %s kbps', selected)

        return selected

    @staticmethod
    def _get_default_bitrate(channels: int) -> int:
        """Returns default bitrate for a given channel configuration"""
        return {
            1: 128,
            2: 224,
            5: 1024,
            8: 1536
        }.get(channels, 1024)

    @staticmethod
    def _get_mix(channels: int) -> str:
        """Return downmix_config value for a given channel count"""
        return {
            1: 'mono',
            2: 'stereo',
            5: '5.1',
            8: '7.1'
        }.get(channels, 'off')
