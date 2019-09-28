#!/usr/bin/python3

"""

Test suite for https://github.com/paul-tqh-nguyen/swing_dance_scores/

Owner : paul-tqh-nguyen

Created : 09/02/2019

File Name : test_utilities.py

File Organization:
* Imports
* Test Utilities
* Main Runner

"""

###########
# Imports #
###########

import sys; sys.path.append(".."); from util.miscellaneous_utilities import *
import subprocess
import re

##################
# Test Utilities #
##################

def get_current_number_of_node_processes():
    ps_e_bash_output = subprocess.run(["ps","-e"], capture_output=True, text=True).stdout
    ps_e_bash_output_lines = ps_e_bash_output.split('\n')
    ps_e_bash_output_lines_without_defunct_node_processes = [line for line in ps_e_bash_output_lines if "node" in line and "defunct" not in line]
    return len(ps_e_bash_output_lines_without_defunct_node_processes)

def extract_firestore_emulator_initialization_info(firestore_emulation_process, timeout_callback):
    firestore_emulation_initialization_has_completed = False
    firestore_emulation_process_text_output_total_text = ''
    api_base_uri_string = None
    with timeout(30, timeout_callback):
        while (not firestore_emulation_initialization_has_completed):
            firestore_emulation_process_text_output_line = firestore_emulation_process.stdout.readline()
            #print("firestore_emulation_process_text_output: {firestore_emulation_process_text_output}".format(firestore_emulation_process_text_output=firestore_emulation_process_text_output))
            firestore_emulation_process_text_output_total_text += firestore_emulation_process_text_output_line
            if "All emulators started, it is now safe to connect." in firestore_emulation_process_text_output_line:
                firestore_emulation_initialization_has_completed = True
            elif "could not start firestore emulator" in firestore_emulation_process_text_output_line:
                break
            else:
                candidate_regular_expression_pattern = "\\x1b\[1m\x1b\[32m✔  functions\[api\]:\\x1b\[39m\\x1b\[22m \\x1b\[1mhttp\\x1b\[22m function initialized \(.*\)\.\n"
                neighborhoods_of_api_base_uri_string_candidates = re.findall(candidate_regular_expression_pattern, firestore_emulation_process_text_output_line)
                if len(neighborhoods_of_api_base_uri_string_candidates) == 1:
                    neightborhood = neighborhoods_of_api_base_uri_string_candidates[0]
                    open_paren_index = neightborhood.find("(")
                    close_paren_index = neightborhood.find(")")
                    api_base_uri_string = neightborhood[open_paren_index+1:close_paren_index]+'/'
    return firestore_emulation_initialization_has_completed, firestore_emulation_process_text_output_total_text, api_base_uri_string

###############
# Main Runner #
###############

if __name__ == '__main__':
    print("This is a library of miscellaneous testing utilities for https://github.com/paul-tqh-nguyen/swing_dance_scores/")
