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

import os
import signal
import unittest
from util.miscellaneous_utilities import *
from .test_utilities import *
from .test_all_webservices_end_to_end import testAllWebServicesEndToEnd
from .test_all_webservices_wrt_authentication import testAllWebServicesWrtAuthentication

###############
# Main Runner #
###############

class UnexpectedBashOutputError(Exception):
    pass

def _get_info_of_process_using_port_number(port_number: int) -> dict:
    lsof_pid_column_command = "lsof -i :{port_number} | awk '{{print $1, $2, $3}}'".format(port_number=port_number)
    lsof_pid_column_process = subprocess.Popen(lsof_pid_column_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout_string, stderr_string = lsof_pid_column_process.communicate()
    if stderr_string is not None:
        raise UnexpectedBashOutputError("We encountered an error while attempting to find the process using port {port_number} via this bash command:\n\n{command}\n\nThe error message was:\n\n{error}".format(command=lsof_pid_column_command, error=stderr_string))
    stdout_lines_with_possible_duplicates = stdout_string.decode("utf-8").split('\n')
    stdout_lines = remove_duplicates(stdout_lines_with_possible_duplicates)
    if len(stdout_lines)==1:
        return dict()
    elif len(stdout_lines)==3 and stdout_lines[0]=="COMMAND PID USER" and stdout_lines[2]=='':
        command, pid_string, user = stdout_lines[1].split(" ")
        pid = int(pid_string)
        return {
            "command": command,
            "pid": pid,
            "user": user
        }
    else:
        raise UnexpectedBashOutputError("We got unexpected output when attempting to find the process using port {port_number} via this bash command:\n\n{command}\n\nThe error message was:\n\n{error}".format(port_number=port_number, command=lsof_pid_column_command, error=stderr_string))
    return dict()

def _possibly_kill_process_using_port_number(port_number: int) -> None:
    port_use_info = _get_info_of_process_using_port_number(port_number)
    if len(port_use_info) != 0:
        command = port_use_info["command"]
        pid = port_use_info["pid"]
        user = port_use_info["user"]
        user_desires_to_kill_process = None
        while user_desires_to_kill_process == None:
            raw_input = input('''
Port {port_number} is in use by the process {command} with PID {pid} owned by the user {user}. 
We need that port to start tests. 
Should we kill it [yes/no]? '''.format(port_number=port_number, command=command, pid=pid, user=user))
            if raw_input.lower() in ["yes","y"]:
                user_desires_to_kill_process = True
            elif raw_input.lower() in ["no","n"]:
                user_desires_to_kill_process = False
            else:
                print("Please respond with 'yes' or 'no' (or 'y' or 'n').")
        if user_desires_to_kill_process:
            print("We will now kill process {pid}.".format(pid=pid))
            os.kill(pid, signal.SIGTERM)
    return None

def run_all_tests():
    _possibly_kill_process_using_port_number(5001)
    _possibly_kill_process_using_port_number(9090)
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
