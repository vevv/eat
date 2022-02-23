import logging
import subprocess
from pathlib import Path
from typing import Callable, cast, List, Optional, Tuple, Union


class ProcessingError(RuntimeError):
    pass


class Processor:
    """Utility wrapper around subprocess"""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def call_process(self,
        params: List[Union[str, Path]],
        success_codes: Tuple[int] = (0,)
    ) -> None:
        """Calls process without surpressing the output"""
        self.logger.debug('Starting %s with params:', params[0])
        self.logger.debug([*map(str, params)])

        process = subprocess.Popen(params)
        ret_code = process.wait()

        if ret_code not in success_codes:
            raise ProcessingError('Process at %s exited with return code %s' % (
                params[0],
                ret_code
            ))

    def call_process_output(self,
        params: List[Union[str, Path]],
        output_handler: Optional[Callable[[subprocess.Popen], None]] = None,
        success_codes: Tuple[int] = (0,)
    ) -> None:
        """
        Calls process surpressing the output,
        optionally piping it to a provided handler function
        """
        self.logger.debug('Starting %s with params:', params[0])
        self.logger.debug([*map(str, params)])

        process = subprocess.Popen(
            params,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding='utf-8',
            errors='ignore'
        )
        if output_handler:
            output_handler(process)

        ret_code = process.wait()

        if ret_code not in success_codes:
            raise ProcessingError('Process at %s exited with return code %s' % (
                params[0],
                ret_code
            ))
