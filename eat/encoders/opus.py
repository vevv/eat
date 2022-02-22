from eat.encoders._ffmpeg import FFmpegEncoder


class Encoder(FFmpegEncoder):
    extension = '.opus'
    _codec = 'libopus'
    _codec_name = 'Opus'

    def _configure(self, *args, **kwargs):
        self._input_file = kwargs['input_path']
        self._output_file = kwargs['output_path']
        self._bitrate = kwargs['bitrate'] or self._get_default_bitrate(kwargs['channels'])

    @staticmethod
    def _clamp_bitrate(bitrate: int) -> int:
        """Clamps bitrate between 8 and 510"""
        # 510 kbps is max possible for 2.0
        # and I don't think anyone will want to go above 512 kbps for 7.1 anyway
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
