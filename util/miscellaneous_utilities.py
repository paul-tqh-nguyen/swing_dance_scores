#!/usr/bin/python3

"""

Misc. utilities for https://github.com/paul-tqh-nguyen/swing_dance_scores/

Owner : paul-tqh-nguyen

Created : 09/06/2019

File Name : miscellaneous_utilities.py

File Organization:
* Imports
* Misc. Utilities
* Main Runner

"""

###########
# Imports #
###########

import subprocess
import signal
import random
from contextlib import contextmanager
import warnings
import sys
import logging
import socket
import time
from typing import List

###################
# Misc. Utilities #
###################

@contextmanager
def timeout(time: int, functionToExecuteOnTimeout=None):
    '''NB: This cannot be nested.'''
    signal.signal(signal.SIGALRM, _raise_timeout)
    assert isinstance(time, int), "timeout not currently supported for non-integer time limits."
    signal.alarm(time)
    try:
        yield
    except TimeoutError:
        if functionToExecuteOnTimeout is not None:
            functionToExecuteOnTimeout()
    finally:
        signal.signal(signal.SIGALRM, signal.SIG_IGN)

def _raise_timeout(signum, frame):
    raise TimeoutError

def random_string():
    return str(random.randint(0,2**32))

def remove_duplicates(items: list) -> list:
    '''Non-destructive uniquifier that preserves order.'''
    seen_items = set()
    new_items = []
    for item in items:
        if item not in seen_items:
            new_items.append(item)
            seen_items.add(item)
    return new_items

def noop(*args, **kws):
    return None

def current_timestamp_string() -> str:
    return time.strftime("%Y_%m_%d_%H_%M_%S")

DEBUGGING_LOGGER_NAME = "debuggingLogger"
logging.basicConfig(stream=sys.stderr)
logging.getLogger(DEBUGGING_LOGGER_NAME).setLevel(logging.DEBUG)

def debug_log(input_to_log='') -> None:
    log = logging.getLogger(DEBUGGING_LOGGER_NAME)
    dwimmed_input_to_log = str(input_to_log)
    lines = dwimmed_input_to_log.split("\n")
    lines_with_machine_name_appended = map(lambda line: socket.gethostname()+': '+line, lines)
    log.debug('\n'.join(lines_with_machine_name_appended)+'\n')
    return None

def extract_stdout_from_subprocess(subprocess, time_limit: int=3) -> List[str]:
    """subprocess is of the type returned by subprocess.Popen"""
    lines = []
    with timeout(time_limit, lambda: warnings.warn("Time limit of {time_limit} seconds reached when trying to extract the STDOUT from {subprocess} at {timestamp}.".format(time_limit=time_limit, subprocess=subprocess, timestamp=current_timestamp_string()))):
        while True:
            line = subprocess.stdout.readline()
            if not line:
                break
            lines.append(line)
    stdout_text = ''.join(lines)
    return stdout_text

###############
# Main Runner #
###############

if __name__ == '__main__':
    print("This is a suite of misc. utilities used in https://github.com/paul-tqh-nguyen/swing_dance_scores/")
 
