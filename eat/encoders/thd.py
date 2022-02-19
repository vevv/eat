from pathlib import Path

from eat.encoders._dee import DeeEncoder


class Encoder(DeeEncoder):
    """Dolby TrueHD encoder class"""
    extension: str = '.thd'

    def _configure(self, *args, **kwargs):
        self._load_xml(self._config_dir / 'thd.xml')

        config = self._config.job_config
        self._temp_dir = kwargs.get('temp_dir')

        # Configure input paths
        config.input.audio.wav.storage.local.path = '"%s"' % self._temp_dir
        config.input.audio.wav.file_name = '"%s"' % kwargs['input_path'].name
        # Configure output paths
        config.output.mlp.file_name = '"%s"' % kwargs['output_path'].name
        config.output.mlp.storage.local.path = '"%s"' % Path.cwd()

        # Configure temp file location
        config.misc.temp_dir.path = '"%s"' % self._temp_dir

        self._config.job_config = config
        self._filename = kwargs['output_path'].name

        # Remove log and config files
        self._to_remove.extend((
            kwargs['output_path'].with_suffix('.thd.log'),
            kwargs['output_path'].with_suffix('.thd.mll'),
        ))
