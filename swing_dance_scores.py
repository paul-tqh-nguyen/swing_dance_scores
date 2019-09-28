#!/usr/bin/python3

"""

Top Level Interface for swing_dance_scores

Run this file directly and see the CLI's --help documentation for further details.

Owner : paul-tqh-nguyen

Created : 08/25/2019

File Name : swing_dance_scores.py

File Organization:
* Imports
* Main Runner

"""

###########
# Imports #
###########

import argparse
import sys
import subprocess
import test.test_all as test
import unittest

###############
# Main Runner #
###############

def _deploy():
    raise NotImplementedError("Support for -deploy is not yet implemented.")
    return None

def _start_front_end_development_server():
    print()
    print("Please use a keyboard interrupt at anytime to exit.")
    print()
    try:
        print("Installing libraries necessary for front end...")
        subprocess.check_call("cd front_end/ && npm install", shell=True)
        print("Starting front end server...")
        print()
        print("Front end interface will be available at http://localhost:3000/")
        subprocess.check_call("cd front_end/ && npm start", shell=True)
    except KeyboardInterrupt as err:
        print("\n\n")
        print("Exiting front end interface.")
    return None

def _run_tests():
    test.run_all_tests()
    return None

VALID_SPECIFIABLE_PROCESSES_TO_RELEVANT_PROCESS_METHOD_MAP = {
    "start_front_end_development_server": _start_front_end_development_server,
    "deploy": _deploy,
    "run_tests": _run_tests,
}

def _determine_all_processes_specified_by_script_args(args):
    arg_to_value_map = vars(args)
    processes_specified = []
    for arg, value in arg_to_value_map.items():
        if value == True: 
            if (arg in VALID_SPECIFIABLE_PROCESSES_TO_RELEVANT_PROCESS_METHOD_MAP):
                processes_specified.append(arg)
            else:
                raise SystemExit("Cannot handle input arg {bad_arg}.".format(bad_arg=arg))
    return processes_specified

def _determine_single_process_specified_by_args(args):
    processes_specified = _determine_all_processes_specified_by_script_args(args)
    number_of_processes_specified = len(processes_specified)
    single_process_specified_by_args = None
    if number_of_processes_specified > 1:
        first_processes_string = ", ".join(processes_specified[:-1])
        last_process_string = ", or {last_process}".format(last_process=processes_specified[-1])
        processes_string = "{first_processes_string}{last_process_string}".format(first_processes_string=first_processes_string, last_process_string=last_process_string)
        raise SystemExit("The input args specified multiple conflicting processes. Please select only one of {processes_string}.".format(processes_string=processes_string))
    elif number_of_processes_specified == 0:
        all_possible_processes = list(VALID_SPECIFIABLE_PROCESSES_TO_RELEVANT_PROCESS_METHOD_MAP.keys())
        first_processes_string = ", ".join(all_possible_processes[:-1])
        last_process_string = ", or {last_process}".format(last_process=all_possible_processes[-1])
        string_for_all_possible_processes = "{first_processes_string}{last_process_string}".format(first_processes_string=first_processes_string, last_process_string=last_process_string)
        raise SystemExit("No process was specified. Please specify one of {string_for_all_possible_processes}.".format(string_for_all_possible_processes=string_for_all_possible_processes))
    elif number_of_processes_specified == 1:
        single_process_specified_by_args = processes_specified[0]
    else:
        raise SystemExit("Unexpected case reached. Please report an issue to https://github.com/paul-tqh-nguyen/swing_dance_scores stating that _determine_single_process_specified_by_args({args}) reached an unexpected case.".format(args=args))
    return single_process_specified_by_args

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-start-front-end-development-server', action='store_true', help="To use our front end interface.")
    parser.add_argument('-run-tests', action='store_true', help="To run all of the tests.")
    parser.add_argument('-deploy', action='store_true', help="To deploy local front end changes to our demo site at https://paul-tqh-nguyen.github.io/swing_dance_scores/.")
    args = parser.parse_args()
    try:
        process = _determine_single_process_specified_by_args(args)
    except SystemExit as error:
        print(error)
        print()
        parser.print_help()
        sys.exit(1)
    if not process in VALID_SPECIFIABLE_PROCESSES_TO_RELEVANT_PROCESS_METHOD_MAP:
        raise SystemExit("Input args to swing_dance_scores.py are invalid.")
    else:
        VALID_SPECIFIABLE_PROCESSES_TO_RELEVANT_PROCESS_METHOD_MAP[process]()
    return None

if __name__ == '__main__':
    main()
