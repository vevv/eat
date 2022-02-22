from pathlib import Path

from eat.encoders._dee import DeeEncoder


class Encoder(DeeEncoder):
    """Dolby Digital Plus (E-AC-3) encoder class"""
    extension: str = '.ec3'
    extension_bd: str = '.eb3'

    def _configure(self, *args, **kwargs):
        self._load_xml(self._config_dir / 'ddp.xml')

        config = self._config.job_config
        self._temp_dir = kwargs.get('temp_dir')

        # Configure encoder
        bitrate = self._clamp_bitrate(
            kwargs['bitrate'] or self._get_default_bitrate(kwargs['channels'])
        )
        mix = self._get_dmix(kwargs['channels'])
        if kwargs.get('remix', False):
            self.logger.warning('Remixing audio to %s', mix)

        # Upmix to 7.1 requires different encoder mode and extension
        if mix == '7.1':
            config.filter.audio.pcm_to_ddp.encoder_mode = 'ddp71'
            mix = 'off'
        else:
            config.filter.audio.pcm_to_ddp.encoder_mode = 'ddp'

        # Bitrates above 1024k are only supported with Blu-ray profile
        if bitrate > 1024:
            config.filter.audio.pcm_to_ddp.encoder_mode = 'bluray'
            kwargs['output_path'] = kwargs['output_path'].with_suffix(self.extension_bd)

        # Set bitrate/channel configuration
        config.filter.audio.pcm_to_ddp.data_rate = bitrate
        config.filter.audio.pcm_to_ddp.downmix_config = mix

        # Enable Dolby Surround EX
        if kwargs.get('surround_ex', False):
            config.filter.audio.pcm_to_ddp.dolby_surround_ex_mode = 'yes'

        # Configure input paths
        config.input.audio.wav.file_name = '"%s"' % kwargs['input_path'].name
        config.input.audio.wav.storage.local.path = '"%s"' % self._temp_dir
        # Configure output paths
        config.output.ec3.file_name = '"%s"' % kwargs['output_path'].name
        config.output.ec3.storage.local.path = '"%s"' % Path.cwd()
        # Configure temp file location
        config.misc.temp_dir.path = '"%s"' % self._temp_dir

        self._config.job_config = config
        self._filename = kwargs['output_path'].name

    @staticmethod
    def _clamp_bitrate(bitrate: int) -> int:
        """Clamps bitrate to a multiply of 8 between 32 and 1664"""
        return max(32, min(8 * round(bitrate / 8), 1664))

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
