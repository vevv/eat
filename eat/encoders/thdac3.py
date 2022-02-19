import re
from pathlib import Path

from rich.progress import Progress

from eat.encoders._dee import DeeEncoder
from eat.encoders.dd import Encoder as DDEncoder
from eat.encoders.thd import Encoder as THDEncoder


class Encoder(DeeEncoder):
    """Dolby TrueHD with "core" encoder class"""
    extension: str = '.thd+ac3'

    def _configure(self, *args, **kwargs):
        self._thd_encoder = THDEncoder(self._path)
        self._dd_encoder = DDEncoder(self._path)

        # Change progress bar messages
        self._thd_encoder._get_task_name = \
            lambda: f'Encoding TrueHD with DEE'

        self._dd_encoder._get_task_name = \
            lambda: f'Encoding AC-3 "core" with DEE'

        self._args = dict(
            input_path=kwargs['input_path'],
            output_path=kwargs['output_path'],
            bitrate=640,
            channels=kwargs['channels'],
            remix=kwargs['remix'],
            temp_dir=kwargs['temp_dir'],
            surround_ex=kwargs['channels'] == 8
        )

    def _encode(self):
        for encoder in (self._thd_encoder, self._dd_encoder):
            args = self._args.copy()
            args['output_path'] = args['output_path'].with_suffix(encoder.extension)
            encoder(**args)
