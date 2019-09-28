#!/usr/bin/python3

"""

Test suite for https://github.com/paul-tqh-nguyen/swing_dance_scores/

This module is mostly a test declaration file that imports tests from elsewhere to indicate that they are worth running. 

Owner : paul-tqh-nguyen

Created : 09/02/2019

File Name : test_all.py

File Organization:
* Test Imports
* Main Runner

"""

################
# Test Imports #
################

import unittest
from .test_all_webservices_end_to_end import testAllWebServicesEndToEnd
from .test_all_webservices_wrt_authentication import testAllWebServicesWrtAuthentication

###############
# Main Runner #
###############

def run_all_tests():
    # to kill all java processes (that may be running and old Firebase emulator), run
    # kill $(ps -e | grep java | awk '{print $1}')
    # be sure to wait some amount of time or sleep in order to make sure that the processes have been properly shut down
    print()
    print("Running our test suite.")
    print()
    loader = unittest.TestLoader()
    tests = [
        loader.loadTestsFromTestCase(testAllWebServicesEndToEnd),
        loader.loadTestsFromTestCase(testAllWebServicesWrtAuthentication),
    ]
    suite = unittest.TestSuite(tests)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
    print()
    print("Test run complete.")
    print()
    return None

if __name__ == '__main__':
    print("This is the test suite for https://github.com/paul-tqh-nguyen/swing_dance_scores/ ; please see the top-level CLI for instructions on how to run these tests.")
    run_all_tests()
