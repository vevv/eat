from eat.encoders.ddp import Encoder as DDPEncoder


class Encoder(DDPEncoder):
    """Dolby Digital (AC-3) encoder class"""
    extension: str = '.ac3'
    supported_sample_rates = [48000]

    def _configure(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super()._configure(*args, **kwargs)
        config = self._config['job_config']
        config['filter']['audio']['pcm_to_ddp']['encoder_mode'] = 'dd'

        if kwargs['channels'] > 6:
            config['filter']['audio']['pcm_to_ddp']['downmix_config'] = '5.1'

        config['output']['ac3'] = config['output']['ec3']
        del config['output']['ec3']
        self._config['job_config'] = config

    @staticmethod
    def _get_default_bitrate(channels: int) -> int:
        """Returns default bitrate for a given channel configuration"""
        return {
            1: 128,
            2: 224,
            6: 640,
        }.get(channels, 640)
