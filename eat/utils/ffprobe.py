import json
from eat.utils.processor import Processor


class FFprobe:
    """ffprobe reading utility class"""

    def __init__(self, path):
        self._path = path
        self._processor = Processor()
        self._log = None

    def __call__(self, file):
        self._processor.call_process_output(
            params=[
                'ffprobe',
                '-v', 'quiet',
                '-select_streams', 'a:0',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file
            ],
            output_handler=self._reader
        )
        return self._log

    def _reader(self, process):
        process.wait()
        self._log = json.loads(process.stdout.read())
