import logging
import re
import subprocess
import sys


class ProcessingError(RuntimeError):
    pass


class Processor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def call_process(self, params, success_codes=(0,)):
        """Calls process without surpressing the output"""
        sys.tracebacklimit = 0  # set traceback limit for neater errors
        self.logger.debug('Starting %s with params:', params[0])
        self.logger.debug(params)

        process = subprocess.Popen(params)
        ret_code = process.wait()

        if ret_code not in success_codes:
            raise ProcessingError('Process at %s exited with return code %s' % (
                params[0],
                ret_code
            ))

        del sys.tracebacklimit

    def call_process_output(self, params, output_handler=None, success_codes=(0,)):
        """
        Calls process surpressing the output,
        optionally piping it to a provided handler function
        """
        sys.tracebacklimit = 0  # set traceback limit for neater errors
        self.logger.debug('Starting %s with params:', params[0])
        self.logger.debug(params)

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

        del sys.tracebacklimit
