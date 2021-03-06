#!/usr/bin/python3

"""

This module contains a test intended to verify that the webservice https://us-central1-swing-dance-scores.cloudfunctions.net/api/users/updateUserDetails work as intended via a local firestore emulator.

Owner : paul-tqh-nguyen

Created : 12/28/2019

File Name : test_update_user_details_via_local_firestore_emulator.py

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

class testUpdateUserDetailsViaLocalFirestoreEmulator(unittest.TestCase):
    def testUpdateUserDetailsViaLocalFirestoreEmulator(self):
        try:
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
                "handle": test_handle
            }
            signup_headers = {'Content-Type': 'application/json'}
            signup_response = requests.post(signup_uri, data=json.dumps(signup_body), headers=signup_headers)
            signup_response_status_code = signup_response.status_code
            self.assertEqual(201, signup_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}".format(uri=signup_uri, status_code=signup_response_status_code))
            signup_response_json_string = signup_response.content
            signup_response_dict = json.loads(signup_response_json_string)
            self.assertTrue('token' in signup_response_dict, msg="We got an unexpected result from the endpoint at {uri} as we got {result}".format(uri=signup_uri, result=signup_response_dict))
            access_token = signup_response_dict['token']
            
            # Test getUserDetails endpoint
            get_user_details_uri = urllib.parse.urljoin(api_base_uri_string, "users/getUserDetails")
            get_user_details_headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {token}".format(token=access_token)
            }
            get_user_details_response = requests.get(url=get_user_details_uri, headers=get_user_details_headers)
            get_user_details_response_status_code = get_user_details_response.status_code
            self.assertEqual(200, get_user_details_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}".format(uri=get_user_details_uri, status_code=get_user_details_response_status_code))
            get_user_details_json_string = get_user_details_response.content
            user_details_dict = json.loads(get_user_details_json_string)
            self.assertTrue(isinstance(user_details_dict,dict), msg="The response from the endpoint at {get_user_details_uri} didn't return JSON content of the correct type (we expected a dictionary). We got the following: \n\n{get_user_details_json_string}\n\n".format(get_user_details_uri=get_user_details_uri, get_user_details_json_string=get_user_details_json_string))
            self.assertFalse("organizationName" in user_details_dict, msg="We got an unexpected result from the endpoint at {uri} as we got the key \"organizationName\" in {result}".format(uri=get_user_details_uri, result=user_details_dict))

            # Edit User Info
            test_organization_name = "Test Organization 1"
            update_user_details_uri = urllib.parse.urljoin(api_base_uri_string, "users/updateUserDetails")
            update_user_details_headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {token}".format(token=access_token)
            }
            update_user_details_body = {
                "organizationName": "Test Organization 1",
            }
            update_user_details_response = requests.post(url=update_user_details_uri, data=json.dumps(update_user_details_body), headers=update_user_details_headers)
            update_user_details_response_status_code = update_user_details_response.status_code
            update_user_details_json_string = update_user_details_response.content
            self.assertEqual(200, update_user_details_response_status_code, msg="""Failed to hit the endpoint at {uri} as we got the status code of {status_code}. 
The headers used were {headers}.
The body used was {body}.
The returned content was {content}.""".format(uri=update_user_details_uri, status_code=update_user_details_response_status_code, headers=json.dumps(update_user_details_headers), body=json.dumps(update_user_details_body), content=update_user_details_json_string.decode('utf-8')))
            user_details_dict = json.loads(update_user_details_json_string)
            
            # Test getUserDetails endpoint
            get_user_details_uri = urllib.parse.urljoin(api_base_uri_string, "users/getUserDetails")
            get_user_details_headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {token}".format(token=access_token)
            }
            get_user_details_response = requests.get(url=get_user_details_uri, headers=get_user_details_headers)
            get_user_details_response_status_code = get_user_details_response.status_code
            self.assertEqual(200, get_user_details_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}".format(uri=get_user_details_uri, status_code=get_user_details_response_status_code))
            get_user_details_json_string = get_user_details_response.content
            user_details_dict = json.loads(get_user_details_json_string)
            self.assertTrue(isinstance(user_details_dict,dict), msg="The response from the endpoint at {get_user_details_uri} didn't return JSON content of the correct type (we expected a dictionary). We got the following: \n\n{get_user_details_json_string}\n\n".format(get_user_details_uri=get_user_details_uri, get_user_details_json_string=get_user_details_json_string))
            self.assertTrue("organizationName" in user_details_dict, msg="We got an unexpected result from the endpoint at {uri} as we got {result}".format(uri=get_user_details_uri, result=user_details_dict))
            self.assertEqual(user_details_dict["organizationName"], test_organization_name, msg="Unexpected organizationName value for our test user in {result}.".format(result=user_details_dict))
            
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
        except AssertionError as error:
            print("Below is the output of the local firestore:\n\n{firestore_stdout}".format(firestore_stdout=extract_stdout_from_subprocess(firestore_emulation_process)))
            raise error

###############
# Main Runner #
###############

if __name__ == '__main__':
    print("This module contains an end-to-end integration test intended to verify that all the webservices for https://github.com/paul-tqh-nguyen/swing_dance_scores/ work as intended via a local firestore emulator.")
