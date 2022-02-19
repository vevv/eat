from eat.encoders._ffmpeg import FFmpegEncoder


class Encoder(FFmpegEncoder):
    extension = '.opus'
    _codec = 'libopus'
    _codec_name = 'Opus'

    def _configure(self, *args, **kwargs):
        """Configures encoding params"""
        self._input_file = kwargs['input_path']
        self._output_file = kwargs['output_path']
        self._bitrate = kwargs['bitrate'] or self._get_default_bitrate(kwargs['channels'])

    @staticmethod
    def _get_default_bitrate(channels: int) -> int:
        return {
            1: 96,
            2: 160,
            5: 384,
            8: 512
        }.get(channels, 192)
