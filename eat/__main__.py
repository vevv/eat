import argparse
from multiprocessing import cpu_count
from pathlib import Path
from typing import IO, Optional

import rich

from eat.handler import Handler

__version__ = 'eat 0.2'


class RichParser(argparse.ArgumentParser):
    def _print_message(self, message: str, file: Optional[IO[str]] = None) -> None:
        rich.print(message, file=file)


def main():
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
        choices=('dd', 'ddp', 'thd', 'thd+ac3', 'opus', 'flac'),
        help='output codec'
    )

    parser.add_argument(
        '-b', '--bitrate',
        type=int,
        help='output bitrate for lossy codecs'
    )

    parser.add_argument(
        '-m', '--mix',
        type=int,
        choices=(1, 2, 6, 8),
        dest='channels',
        help='specify down/upmix, support varies by codec (default: none)'
    )

    parser.add_argument(
        '--ex',
        default=False,
        action='store_true',
        dest='surround_ex',
        help='use Dolby Surround EX'
    )

    parser.add_argument(
        '-y', '--allow-overwrite',
        default=False,
        action='store_true',
        help='allow file overwrite'
    )

    args = parser.parse_args()

    handler = Handler(args)
    handler.main()


if __name__ == "__main__":
    main()
