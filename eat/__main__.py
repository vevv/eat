import argparse
from multiprocessing import cpu_count
from pathlib import Path

from eat.handler import Handler

__version__ = 'eat 0.1'


def main():
    parser = argparse.ArgumentParser()
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

    # for future use
    parser.add_argument(
        '-t', '--threads',
        type=int,
        default=cpu_count() - 1,
        # help=f'number of threads to use for batch encoding, (default: {cpu_count()-1})',
        help=argparse.SUPPRESS
    )
    args = parser.parse_args()
    handler = Handler(args)
    handler.main()


if __name__ == "__main__":
    main()
