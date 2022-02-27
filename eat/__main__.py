import argparse
import sys
from multiprocessing import cpu_count
from pathlib import Path
from typing import IO, Optional

import rich

from eat.handler import Handler

__version__ = '0.3.1'


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
        '-f', '--format',
        type=str.lower,
        default='ddp',
        dest='encoder',
        choices=('dd', 'ddp', 'thd', 'thd+ac3', 'opus', 'flac', 'aac'),
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
