import argparse
import importlib
import logging
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
        self.config: dict = Config().load()
        self.probe: FFprobe = FFprobe(self.config['binaries']['ffprobe'])
        self._to_remove: List[Path] = []

    def main(self) -> None:
        """Processes given input files"""
        rf64e = self._get_encoder('rf64')
        encoder = self._get_encoder(self.args.encoder)

        if not self.args.input:
            self.logger.error('No files provided to process')

        for file in self.args.input:
            self.logger.info('Processing %s...', file)

            # Set paths
            input_path = file
            output_path = file.with_suffix(encoder.extension)

            # Check if input/output files exist
            if not input_path.exists():
                self.logger.error('%s doesn\'t exist!', input_path)
                continue

            if output_path.exists() \
                    and not self.args.allow_overwrite \
                    and not Confirm.ask(prompt=f'{output_path} exists. Overwrite?'):
                self.logger.error('%s exists, skipping', output_path)
                continue

            if input_path == output_path:
                self.logger.error('Cannot convert %s to %s', input_path, output_path)
                continue

            # Run ffprobe for file info
            try:
                file_info = self.probe(input_path)['streams'][0]
            except ProcessingError:
                self.logger.error('ffprobe failed to recognize %s, skipping', input_path)
                continue

            codec = file_info['codec_name']
            bitdepth = int(file_info.get('bits_per_sample') or file_info.get('bits_per_raw_sample', 32))
            # ffmpeg progress output has duration in microseconds, but ffprobe returns seconds
            duration = float(file_info.get('duration', -1)) * 1000000

            # Check for broken files
            if file_info['channels'] == 0:
                self.logger.error('Zero channels detected, file likely broken, skipping')
                continue

            # Prevent crashing on 2.0 -> 5.1/7.1 downmix
            if self.args.channels \
                    and file_info['channels'] <= 2 and self.args.channels > 2:
                self.logger.error('Upmixing from mono/stereo not supported')
                continue

            # Prevent crashing with wrong channel layouts for DEE
            if isinstance(encoder, DeeEncoder) \
                    and file_info['channels'] not in (1, 2, 6, 8):
                self.logger.error('Only supported channel configurations '
                                  'for DEE are 1.0, 2.0, 5.1, 7.1')
                continue

            # Warn against mono/stereo DD/P
            if (file_info['channels'] <= 2
                    or (self.args.channels and self.args.channels <= 2)) \
                    and self.args.encoder in ('ddp', 'dd'):
                self.logger.warning(
                    'Using DD/P for mono and stereo is not recommended,\n'
                    'consider using qaac or opus'
                )

            # Warn against bad transcodes
            if codec in ('aac', 'opus', 'ac3', 'eac3') \
                or (codec == 'dts'  # DTS, DTS HD-HR, etc...
                    and file_info.get('profile')[-2:] not in ('MA', ':X', ' X')):
                self.logger.warning(
                    'Input file %s is lossy, re-encoding is not recommended',
                    input_path.name
                )

            # Convert all formats to rf64 before passing them to encoders
            if not codec.startswith('pcm_') and codec not in encoder.supported_inputs \
                    and not isinstance(encoder, FFmpegEncoder):
                input_path = get_temp_file(
                    suffix=rf64e.extension,
                    directory=self.config['temp_path']
                )
                self._to_remove.append(input_path)

                rf64e(
                    input_path=file,
                    output_path=input_path,
                    bitdepth=bitdepth,
                    duration=duration
                )

            encoder(
                input_path=input_path,
                output_path=output_path,
                bitdepth=bitdepth,
                duration=duration,
                bitrate=self.args.bitrate,
                channels=self.args.channels or file_info.get('channels'),
                remix=bool(self.args.channels),
                temp_dir=self.config['temp_path']
            )
            self._to_remove.extend(encoder._to_remove)

        for file in self._to_remove:
            if file.exists():
                file.unlink()

    def _get_encoder(self, encoder: str) -> BaseEncoder:
        """Returns initialized encoder class for a given encoder name"""
        if encoder == 'thd+ac3':
            encoder = 'thdac3'

        module = importlib.import_module('eat.encoders.%s' % encoder)
        encoder_path = self.config['binaries'].get(
            module.Encoder.binary_name, which(module.Encoder.binary_name)
        )
        if not encoder_path:
            self.logger.error('Path for %s not found!', module.Encoder.binary_name)
            raise SystemExit

        return module.Encoder(Path(encoder_path))  # type: ignore[no-any-return]
