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

import unittest
import subprocess
import os
import signal
import random
from contextlib import contextmanager

###################
# Misc. Utilities #
###################

@contextmanager
def timeout(time, functionToExecuteOnTimeout=None):
    '''NB: This cannot be nested.'''
    signal.signal(signal.SIGALRM, _raise_timeout)
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

def noop(*args, **kws):
    return None

###############
# Main Runner #
###############

if __name__ == '__main__':
    print("This is a suite of misc. utilities used in https://github.com/paul-tqh-nguyen/swing_dance_scores/")
 
