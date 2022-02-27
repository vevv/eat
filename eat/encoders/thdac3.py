import re
from pathlib import Path
from typing import Any, cast

from rich.progress import Progress

from eat.encoders._dee import DeeEncoder
from eat.encoders.dd import Encoder as DDEncoder
from eat.encoders.thd import Encoder as THDEncoder


class Encoder(DeeEncoder):
    """Dolby TrueHD with "core" encoder class"""
    extension: str = '.thd+ac3'

    def _configure(
        self,
        *,
        input_path: Path,
        output_path: Path,
        channels: int,
        temp_dir: Path,
        remix: bool = False,
        **_: Any
    ) -> None:
        self._thd_encoder = THDEncoder(self._path)
        self._dd_encoder = DDEncoder(self._path)

        # Change progress bar messages
        self._thd_encoder._get_task_name = lambda: f'Encoding TrueHD with DEE'  # type: ignore[assignment]
        self._dd_encoder._get_task_name = lambda: f'Encoding AC-3 "core" with DEE'  # type: ignore[assignment]

        self._args = dict(
            input_path=input_path,
            output_path=output_path,
            bitrate=640,
            channels=channels,
            remix=remix,
            temp_dir=temp_dir
        )

    def _encode(self) -> None:
        for encoder in (self._thd_encoder, self._dd_encoder):
            args = self._args.copy()
            args['output_path'] = cast(Path, args['output_path']).with_suffix(encoder.extension)
            encoder(**args)
