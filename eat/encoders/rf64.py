from eat.encoders._ffmpeg import FFmpegEncoder


class Encoder(FFmpegEncoder):
    extension = '.wav'
    _codec_name = 'rf64'
    _extra_params = ['-rf64', 'always']
    _bitrate = '0'  # bitrate irrelevant for a lossless codec

    def _configure(self, *args, **kwargs):
        """Configures encoding params"""
        self._input_file = kwargs['input_path']
        self._output_file = kwargs['output_path']
        self._codec = 'pcm_s%02dle' % kwargs.get('bitdepth', 16)
