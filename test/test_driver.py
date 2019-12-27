#!/usr/bin/python3

"""

Test suite for https://github.com/paul-tqh-nguyen/swing_dance_scores/

This module is mostly a test declaration file that imports tests from elsewhere to indicate that they are worth running. 

Owner : paul-tqh-nguyen

Created : 09/02/2019

File Name : test_driver.py

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
from .test_all_webservices_end_to_end_via_local_firestore_emulator import testAllWebServicesEndToEndViaLocalFireStoreEmulator
from .test_all_webservices_wrt_authentication_via_local_firestore_emulator import testAllWebServicesWrtAuthenticationViaLocalFireStoreEmulator
from .test_all_webservices_end_to_end_via_deployed_app import testAllWebServicesEndToEndViaDeployedApp
from .test_db_has_few_test_user_accounts import testDBHasFewTestUserAccounts
from .test_sign_up_webservice_via_local_firestore_emulator import testSignUpWebserviceViaLocalFirestoreEmulator

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

def _solicit_yes_or_no_from_user(prompt: str) -> bool:
    boolean_value_of_explicitly_given_user_input = None
    while boolean_value_of_explicitly_given_user_input == None:
            raw_input = input(prompt)
            if raw_input.lower() in ["yes","y"]:
                boolean_value_of_explicitly_given_user_input = True
            elif raw_input.lower() in ["no","n"]:
                boolean_value_of_explicitly_given_user_input = False
            else:
                print("Please respond with 'yes' or 'no' (or 'y' or 'n').")
    return boolean_value_of_explicitly_given_user_input

def _possibly_kill_process_using_port_number(port_number: int) -> None:
    port_use_info = _get_info_of_process_using_port_number(port_number)
    if len(port_use_info) != 0:
        command = port_use_info["command"]
        pid = port_use_info["pid"]
        user = port_use_info["user"]
        user_desires_to_kill_process = _solicit_yes_or_no_from_user('''
Port {port_number} is in use by the process {command} with PID {pid} owned by the user {user}. 
We need that port to start tests. 
Should we kill it [yes/no]? '''.format(port_number=port_number, command=command, pid=pid, user=user))
        
        if user_desires_to_kill_process:
            print("We will now kill process {pid}.".format(pid=pid))
            os.kill(pid, signal.SIGTERM)
    return None

def _possibly_remove_all_test_users_from_production_db():
    test_users_exist_in_production_db = False
    for _ in all_test_user_emails_in_production_db():
        test_users_exist_in_production_db = True
        break
    if test_users_exist_in_production_db:
        user_desires_test_user_removal = _solicit_yes_or_no_from_user('There are test users in the production DB. Should we remove them before running tests [yes/no]? ')
        if user_desires_test_user_removal:
            for test_user_email in all_test_user_emails_in_production_db():
                delete_test_user_from_production_db_via_email(test_user_email)
    return None

def run_all_tests():
    _possibly_kill_process_using_port_number(5001)
    _possibly_kill_process_using_port_number(9090)
    _possibly_remove_all_test_users_from_production_db()
    print()
    print("Running our test suite.")
    print()
    loader = unittest.TestLoader()
    tests = [
        loader.loadTestsFromTestCase(testSignUpWebserviceViaLocalFirestoreEmulator),
        loader.loadTestsFromTestCase(testAllWebServicesEndToEndViaLocalFireStoreEmulator),
        loader.loadTestsFromTestCase(testAllWebServicesWrtAuthenticationViaLocalFireStoreEmulator),
        loader.loadTestsFromTestCase(testAllWebServicesEndToEndViaDeployedApp),
        loader.loadTestsFromTestCase(testDBHasFewTestUserAccounts),
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
