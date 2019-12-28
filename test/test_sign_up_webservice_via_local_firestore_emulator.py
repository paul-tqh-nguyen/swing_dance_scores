#!/usr/bin/python3

"""

This module contains a basic unit test case intended to verify that the "sign up" or "create user" webservices for https://github.com/paul-tqh-nguyen/swing_dance_scores/ works as intended. The authentication is handled by our production DB, but storage is tested by a local firestore emulator.

Owner : paul-tqh-nguyen

Created : 12/26/2019

File Name : test_sign_up_webservice_via_local_firestore_emulator.py

File Organization:
* Imports
* Tests
* Main Runner

"""

###########
# Imports #
###########

import sys; sys.path.append(".."); from util.miscellaneous_utilities import *
from .test_utilities import *
import unittest
import subprocess
import os
import signal
import requests
import urllib.parse
import json

#########
# Tests #
#########

class testSignUpWebserviceViaLocalFirestoreEmulator(unittest.TestCase):
    def testSignUpWebserviceViaLocalFirestoreEmulator(self):
        number_of_node_processes_before = get_current_number_of_node_processes()
        
        # Test firestore initilization
        firestore_emulation_initialization_command = "cd back_end && firebase emulators:start"
        firestore_emulation_process = subprocess.Popen(firestore_emulation_initialization_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True, preexec_fn=os.setsid)
        firestore_emulation_initialization_has_timed_out = False
        def _note_firestore_emulation_initialization_timeout():
            firestore_emulation_initialization_has_timed_out = True
        firestore_emulation_initialization_has_completed, firestore_emulation_process_text_output_total_text, api_base_uri_string = \
            extract_firestore_emulator_initialization_info(firestore_emulation_process, _note_firestore_emulation_initialization_timeout)
        self.assertFalse(firestore_emulation_initialization_has_timed_out,msg="Initialization of the firestore emulator timed out.")
        self.assertTrue(firestore_emulation_initialization_has_completed, msg="Could not start firebase emulator. The output was: \n\n{output}\n\nCheck if there are any java processes around hogging the desired port (lsof can be useful here).".format(output=firestore_emulation_process_text_output_total_text))
        self.assertTrue(isinstance(api_base_uri_string,str), msg="Could not find the API base URI. The output was: \n{output}".format(output=firestore_emulation_process_text_output_total_text))
        
        number_of_node_processes_during = get_current_number_of_node_processes()

        test_handle, test_email, test_password = generate_new_test_email_and_password_and_user_handle()
        
        # Test signup endpoint
        signup_uri = urllib.parse.urljoin(api_base_uri_string, "signup")
        signup_body = {
            "email": test_email,
            "password": test_password,
            "confirmPassword": test_password,
            "handle": test_handle,
        }
        signup_headers = {'Content-Type': 'application/json'}
        signup_response = requests.post(signup_uri, data=json.dumps(signup_body), headers=signup_headers)
        signup_response_status_code = signup_response.status_code
        self.assertEqual(201, signup_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}.".format(uri=signup_uri, status_code=signup_response_status_code))
        firestore_emulation_process
        
        signup_response_json_string = signup_response.content
        signup_response_dict = json.loads(signup_response_json_string)
        self.assertTrue('token' in signup_response_dict, msg="We got an unexpected result from the endpoint at {uri} as we got {result}".format(uri=signup_uri, result=signup_response_dict))
                
        # Shut down firestore emulator
        os.killpg(os.getpgid(firestore_emulation_process.pid), signal.SIGTERM)
        with timeout(1, noop):
            while (get_current_number_of_node_processes() != number_of_node_processes_before): # @hack wait until things sync up
                noop()
        number_of_node_processes_after = get_current_number_of_node_processes()

        # Test that we have no lingering processes
        self.assertEqual(number_of_node_processes_before, number_of_node_processes_after, msg="There is a differnet number of node.js processes existing before and after this test, which may signal that the firebase emulator used during this test is still running.")
        self.assertNotEqual(number_of_node_processes_during, number_of_node_processes_before, msg="The number of node.js processes during the test run and before the test run is the same, which may signal that the firebase emulator was not initialized during the test run.")
        self.assertNotEqual(number_of_node_processes_during, number_of_node_processes_after, msg="The number of node.js processes during the test run and after the test run is the same, which may signal that the firebase emulator was not initialized during the test run.")
        
        # Test that we didn't pollute the DB with an unecessary number of users
        delete_test_user_from_production_db_via_email(test_email)
        self.assertTrue(len(list(all_test_user_emails_in_production_db())) < MAX_NUMBER_OF_TOLERABLE_TEST_USERS,
                        "There are too many test users in the production database. A clean up is necessary.")

###############
# Main Runner #
###############

if __name__ == '__main__':
    print("""This module contains a basic unit test case intended to verify that the "sign up" or "create user" webservices for https://github.com/paul-tqh-nguyen/swing_dance_scores/ works as intended. The authentication is handled by our production DB, but storage is tested by a local firestore emulator.""")
