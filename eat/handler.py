import argparse
import importlib
import logging
import platform
from pathlib import Path
from shutil import which
from typing import List, Optional

from rich.logging import RichHandler
from rich.prompt import Confirm

from eat.config import Config
from eat.encoders._base import BaseEncoder
from eat.encoders._dee import DeeEncoder
from eat.encoders._ffmpeg import FFmpegEncoder
from eat.utils.ffprobe import FFprobe
from eat.utils.processor import ProcessingError
from eat.utils.tempfile import get_temp_file


class Handler:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        logging.basicConfig(
            format='%(message)s',
            datefmt='',
            level=logging.DEBUG if args.debug else logging.INFO,
            handlers=[RichHandler()]
        )
        self.logger = logging.getLogger(__name__)
        self.config = Config().load()
        self.probe = FFprobe(self.config['binaries']['ffprobe'])
        self._to_remove: List[Path] = []

    def main(self) -> None:
        """Processes given input files"""
        if not self.args.input:
            self.logger.error('No files provided to process')
            return

        self.args.output_dir.mkdir(exist_ok=True)

        for input_path in self.args.input:
            if not input_path.exists():
                self.logger.error('"%s" doesn\'t exist!', input_path)
                continue

            self.logger.info('Processing "%s"...', input_path)
            for encoder in self.args.encoder:
                if len(self.args.encoder) > 1:
                    self.logger.info('Encoding "%s" to %s...', input_path.name, encoder)
                self._encode_format(input_path, encoder)
                self._clean_temp_files()

    def _encode_format(self, input_path: Path, encoder_name: str) -> None:
        rf64e = self._get_encoder('rf64')
        encoder = self._get_encoder(encoder_name)
        output_path = self.args.output_dir / input_path.with_suffix(encoder.extension).name

        # Check if output path exists
        if output_path.exists() \
                and not self.args.allow_overwrite \
                and not Confirm.ask(prompt=f'{output_path} exists. Overwrite?'):
            self.logger.error('"%s" exists, skipping', output_path)
            return

        if input_path == output_path:
            self.logger.error('Cannot convert "%s" to "%s"', input_path, output_path)
            return

        # Run ffprobe for file info
        try:
            file_info = self.probe(input_path)
        except ProcessingError:
            self.logger.error('ffprobe failed to recognize "%s", skipping', input_path)
            return

        # Check for broken files
        if file_info.channels == 0:
            self.logger.error('Zero channels detected, file likely broken, skipping')
            return

        # Prevent crashing on 2.0 -> 5.1/7.1 downmix
        if self.args.channels \
                and file_info.channels <= 2 and self.args.channels > 2:
            self.logger.error('Upmixing from mono/stereo not supported')
            return

        # Prevent crashing with wrong channel layouts for DEE
        if isinstance(encoder, DeeEncoder) \
                and file_info.channels not in (1, 2, 6, 8):
            self.logger.error('Only supported channel configurations '
                              'for DEE are 1.0, 2.0, 5.1, 7.1')
            return

        # Warn against mono/stereo DD/P
        if (file_info.channels <= 2
                or (self.args.channels and self.args.channels <= 2)) \
                and self.args.encoder in ('ddp', 'dd'):
            self.logger.warning(
                'Using DD/P for mono and stereo is not recommended,\n'
                'consider using qaac or opus'
            )

        # Warn against bad transcodes
        if file_info.codec in ('aac', 'opus', 'ac3', 'eac3') \
            or (file_info.codec == 'dts'  # DTS, DTS HD-HR, etc...
                and file_info.profile[-2:] not in ('MA', ':X', ' X')):
            self.logger.warning(
                'Input file "%s" is lossy, re-encoding is not recommended',
                input_path.name
            )

        # Set correct sample rate
        resample_rate: Optional[int] = None
        if encoder.supported_sample_rates \
                and file_info.sample_rate not in encoder.supported_sample_rates:
            resample_rate = min(
                encoder.supported_sample_rates,
                key=lambda val: abs(file_info.sample_rate - val)
            )

        # Convert all formats to rf64 before passing them to encoders
        if not file_info.codec.startswith('pcm_') \
                and file_info.codec not in encoder.supported_inputs \
                and not isinstance(encoder, FFmpegEncoder):
            temp_path = get_temp_file(
                suffix=rf64e.extension,
                directory=self.config['temp_path']
            )
            self._to_remove.append(temp_path)

            rf64e(
                input_path=input_path,
                output_path=temp_path,
                bitdepth=file_info.bitdepth,
                duration=file_info.duration,
                sample_rate=resample_rate
            )
            input_path = temp_path
            resample_rate = None  # avoid resampling twice

        encoder(
            input_path=input_path,
            output_path=output_path,
            bitdepth=file_info.bitdepth,
            sample_rate=self.args.sample_rate or resample_rate,
            resample_fmt=self.args.bit_depth,
            duration=file_info.duration,
            bitrate=self.args.bitrate,
            channels=self.args.channels or file_info.channels,
            remix=bool(self.args.channels),
            temp_dir=self.config['temp_path']
        )
        self._to_remove.extend(encoder._to_remove)

    def _clean_temp_files(self) -> None:
        for file in self._to_remove:
            if file.exists():
                file.unlink()
            self._to_remove.remove(file)

    def _get_encoder(self, encoder: str) -> BaseEncoder:
        """Returns initialized encoder class for a given encoder name"""
        module = importlib.import_module('eat.encoders.%s' % encoder)
        encoder_path = self.config['binaries'].get(
            module.Encoder.binary_name, which(module.Encoder.binary_name)
        )
        if platform.system() == 'Linux' \
                and encoder == 'thd' and not encoder_path.endswith('.exe'):
            self.logger.warning('Linux version of DEE detected, '
                                'TrueHD encoding will not work')

        if not encoder_path:
            self.logger.error('Path for %s not found!', module.Encoder.binary_name)
            raise SystemExit

        return module.Encoder(Path(encoder_path))  # type: ignore[no-any-return]
