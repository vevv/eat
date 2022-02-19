from eat.encoders.ddp import Encoder as DDPEncoder


class Encoder(DDPEncoder):
    """Dolby Digital (AC-3) encoder class"""
    extension: str = '.ac3'

    def _configure(self, *args, **kwargs):
        super()._configure(*args, **kwargs)
        config = self._config.job_config
        config.filter.audio.pcm_to_ddp.encoder_mode = 'dd'
        if kwargs.get('surround_ex', False):
            config.filter.audio.pcm_to_ddp.dolby_surround_ex_mode = 'yes'

        if kwargs['channels'] > 6:
            config.filter.audio.pcm_to_ddp.downmix_config = '5.1'

        config.output.ac3 = config.output.ec3
        del config.output['ec3']
        self._config.job_config = config

    @staticmethod
    def _get_default_bitrate(channels: int) -> int:
        return {
            1: 128,
            2: 224,
            6: 640,
        }.get(channels, 640)
