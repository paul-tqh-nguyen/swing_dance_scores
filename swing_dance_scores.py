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
import test.test_driver as test
import unittest
import re
import datetime
import time
from util.miscellaneous_utilities import *

###############
# Main Runner #
###############

def _deploy():
    print()
    print("Deploying back end...")
    print()
    back_end_deployment_command = "cd back_end && firebase deploy"
    subprocess.check_call(back_end_deployment_command, shell=True)
    print()
    print("Deploying front end...")
    print()
    raise NotImplementedError("Support for -deploy is not yet implemented for the front end...")
    return None

def _start_development_servers():
    print()
    print("Please use a keyboard interrupt at anytime to exit.")
    print()
    back_end_development_server_initialization_command = "cd back_end && firebase emulators:start"
    front_end_development_server_initialization_command = "cd front_end && npm start"
    back_end_development_server_process = None
    front_end_development_server_process = None
    back_end_process_output_total_text = ""
    front_end_process_output_total_text = ""
    def _shut_down_development_servers():
        print("\n\n")
        print("Shutting down development servers.")
        if back_end_development_server_process is not None:
            os.killpg(os.getpgid(back_end_development_server_process.pid), signal.SIGTERM)
        if front_end_development_server_process is not None:
            os.killpg(os.getpgid(front_end_development_server_process.pid), signal.SIGTERM)
        print("Development servers have been shut down.")
    def _raise_system_exit_exception_on_server_initilization_error(reason):
        raise SystemExit("Failed to start front or back end server for the following reason: {reason}".format(reason=reason))
    def _raise_system_exit_exception_on_server_initilization_time_out_error():
        _raise_system_exit_exception_on_server_initilization_error("Server initialization timedout.")
    try:
        print("Installing libraries necessary for back end...")
        subprocess.check_call("cd back_end/ && npm install", shell=True)
        print("Installing libraries necessary for front end...")
        subprocess.check_call("cd front_end/ && npm install", shell=True)
        print("Starting front and back end server...")
        back_end_development_server_process = subprocess.Popen(back_end_development_server_initialization_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True, preexec_fn=os.setsid)
        front_end_development_server_process = subprocess.Popen(front_end_development_server_initialization_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True,
                                                                preexec_fn=os.setsid)
        # start back end server
        with timeout(30, _raise_system_exit_exception_on_server_initilization_time_out_error):
            back_end_initialization_has_completed = False
            while (not back_end_initialization_has_completed):
                back_end_output_line = back_end_development_server_process.stdout.readline()
                back_end_process_output_total_text += back_end_output_line
                if "All emulators started, it is now safe to connect." in back_end_output_line:
                    back_end_initialization_has_completed = True
                elif "could not start firestore emulator" in back_end_output_line:
                    reason = "Could not start back end server.\n\nThe following was the output of the back end server initialization process:\n{process_output_text}".format(
                        process_output_text=back_end_process_output_total_text)
                    _raise_system_exit_exception_on_server_initilization_error(reason)
        # start front end server        
        with timeout(30, _raise_system_exit_exception_on_server_initilization_time_out_error):
            front_end_initialization_has_completed = False
            local_front_end_url = None
            network_front_end_url = None
            while (not front_end_initialization_has_completed):
                front_end_output_line = front_end_development_server_process.stdout.readline()
                front_end_process_output_total_text += front_end_output_line
                local_url_line_pattern = " +Local: +.*"
                local_url_line_pattern_matches = re.findall(local_url_line_pattern, front_end_output_line)
                if len(local_url_line_pattern_matches) == 1:
                    local_front_end_url = local_url_line_pattern_matches[0].replace("Local:","").strip()
                    print("The front end can be found locally at {local_front_end_url}".format(local_front_end_url=local_front_end_url))
                    continue
                network_url_line_pattern = " +On Your Network: +.*"
                network_url_line_pattern_matches = re.findall(network_url_line_pattern, front_end_output_line)
                if len(network_url_line_pattern_matches) == 1:
                    network_front_end_url = network_url_line_pattern_matches[0].replace("On Your Network:","").strip()
                    print("The front end can be found on your network at {network_front_end_url}".format(network_front_end_url=network_front_end_url))
                    front_end_initialization_has_completed = True
        print("\nBack end and front end servers initialized at {time}".format(time=datetime.datetime.now()))
        print("\n\nHere's the back end server initialization output:\n\n{back_end_process_output_total_text}\n\n".format(back_end_process_output_total_text=back_end_process_output_total_text))
        print("\n\nHere's the front end server initialization output:\n\n{front_end_process_output_total_text}\n\n".format(front_end_process_output_total_text=front_end_process_output_total_text))
        start_time=time.time()
        time_of_last_ping = start_time
        while True:
            elapsed_time_since_last_ping = time.time() - time_of_last_ping
            if elapsed_time_since_last_ping > 3600:
                print("It has been {num_hours} hours since the front and back end servers started.".format(num_hours=int((time.time()-start_time)/3600)))
                time_of_last_ping = time.time()
        print()
    except SystemExit as error:
        print('''We encountered an error.

{error}

Perhaps the output of the back end server initialization might be helpful...

{back_end_process_output_total_text}

Perhaps the output of the front end server initialization might be helpful...

{front_end_process_output_total_text}
'''.format(error=error, back_end_process_output_total_text=back_end_process_output_total_text, front_end_process_output_total_text=front_end_process_output_total_text))
        _shut_down_development_servers()
        sys.exit(1)
    except KeyboardInterrupt as err:
        _shut_down_development_servers()
    return None

def _run_tests():
    test.run_all_tests()
    return None

VALID_SPECIFIABLE_PROCESSES_TO_RELEVANT_PROCESS_METHOD_MAP = {
    "start_development_servers": _start_development_servers,
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
    parser.add_argument('-start-development-servers', action='store_true', help="Start our back end and front end servers for development purposes.")
    parser.add_argument('-run-tests', action='store_true', help="To run all of the tests.")
    parser.add_argument('-deploy', action='store_true', help="To deploy local changes to our demo site at https://paul-tqh-nguyen.github.io/swing_dance_scores/.")
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
