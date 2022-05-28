import argparse
import sys
from multiprocessing import cpu_count
from pathlib import Path
from typing import IO, Optional

import rich

from eat.handler import Handler

__version__ = '0.4.6'


class RichParser(argparse.ArgumentParser):
    def _print_message(self, message: str, file: Optional[IO[str]] = None) -> None:
        rich.print(message, file=file)


def main() -> None:
    parser = RichParser()
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=__version__,
        help='shows version'
    )

    parser.add_argument(
        '-i', '--input',
        nargs='*',
        default=[],
        type=Path,
        help='audio file(s)'
    )

    parser.add_argument(
        '-o', '--output-dir',
        default=Path.cwd(),
        type=Path,
        dest='output_dir',
        help='output directory (default: cwd)'
    )

    parser.add_argument(
        '-f', '--format',
        nargs='*',
        type=str.lower,
        default=['ddp'],
        dest='encoder',
        choices=('rf64', 'dd', 'ddp', 'thd', 'opus', 'flac', 'aac'),
        help='output codec'
    )

    parser.add_argument(
        '-b', '-q', '--bitrate',
        type=int,
        help='output bitrate (quality value for aac) for lossy codecs'
    )

    parser.add_argument(
        '-m', '--mix',
        type=int,
        choices=(1, 2, 6, 8),
        dest='channels',
        help='specify down/upmix, support varies by codec (default: none)'
    )

    parser.add_argument(
        '--sample-rate',
        type=int,
        choices=[44100, 48000, 96000],
        dest='sample_rate',
        help='change output sample rate (FLAC only)'
    )

    parser.add_argument(
        '--bit-depth',
        '--bitdepth',
        type=int,
        choices=[16, 24],
        dest='bit_depth',
        help='change output bit depth (FLAC only)'
    )

    parser.add_argument(
        '-y', '--allow-overwrite',
        default=False,
        action='store_true',
        help='allow file overwrite'
    )

    parser.add_argument(
        '-d', '--debug',
        default=False,
        action='store_true',
        help='Print debug statements'
    )

    args = parser.parse_args()
    if not args.debug:
        sys.tracebacklimit = 0  # set traceback limit for neater errors

    handler = Handler(args)
    handler.main()


if __name__ == "__main__":
    main()
