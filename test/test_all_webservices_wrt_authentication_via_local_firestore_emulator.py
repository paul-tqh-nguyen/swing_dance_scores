#!/usr/bin/python3

"""

This module contains unit test cases intended to verify that all the webservices for https://github.com/paul-tqh-nguyen/swing_dance_scores/ that require authentication actually require authentication. The authentication is handled by our production DB, but storage is tested by a local firestore emulator.

Owner : paul-tqh-nguyen

Created : 09/02/2019

File Name : test_all_webservices_wrt_authentication_via_local_firestore_emulator.py

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
import time

#########
# Tests #
#########

class testAllWebServicesWrtAuthenticationViaLocalFireStoreEmulator(unittest.TestCase):
    def testAllWebServicesWrtAuthenticationViaLocalFireStoreEmulator(self):
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
        bad_credentials_handle = random_string()
        bad_credentials_token  = random_string()
        get_all_competitions_uri = urllib.parse.urljoin(api_base_uri_string, "competitions")
        
        # Test createCompetition endpoint fails for bad authentication
        create_competition_uri = urllib.parse.urljoin(api_base_uri_string, "createCompetition")
        competition_1_name = "competition_{random_string}".format(random_string=random_string())
        create_competition_body = {
	    "competitionName": competition_1_name,
	    "creatorHandle": bad_credentials_handle
        }
        create_competition_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {bad_credentials_token}".format(bad_credentials_token=bad_credentials_token)
        }
        create_competition_response = requests.post(create_competition_uri, data=json.dumps(create_competition_body), headers=create_competition_headers)
        create_competition_response_status_code = create_competition_response.status_code
        # Test that we have exactly 0 competitions
        all_competitions_response = requests.get(url=get_all_competitions_uri)
        all_competitions_response_status_code = all_competitions_response.status_code
        self.assertEqual(200, all_competitions_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}".format(uri=get_all_competitions_uri, status_code=all_competitions_response_status_code))
        all_competitions_json_string = all_competitions_response.content
        all_competitions = json.loads(all_competitions_json_string)
        self.assertTrue(isinstance(all_competitions,list), msg="The response from the endpoint at {get_all_competitions_uri} didn't return JSON content of the correct type (we expected a list). We got the following: \n\n{all_competitions_json_string}\n\n".format(get_all_competitions_uri=get_all_competitions_uri, all_competitions_json_string=all_competitions_json_string))
        self.assertEqual(len(all_competitions), 0, msg="The response from the endpoint at {get_all_competitions_uri} didn't return an empty list. We expect there to be zero competitions so far as we attempted to created one competition with invalid credentials and since the firestore emulator was just initialized.".format(get_all_competitions_uri=get_all_competitions_uri))

        valid_handle, valid_email, valid_password = generate_new_test_email_and_password_and_user_handle()

        # Test signup endpoint (in order to access valid authentication credentials)
        signup_uri = urllib.parse.urljoin(api_base_uri_string, "signup")
        signup_body = {
            "email": valid_email,
            "password": valid_password,
            "confirmPassword": valid_password,
            "handle": valid_handle
        }
        signup_headers = {'Content-Type': 'application/json'}
        signup_response = requests.post(signup_uri, data=json.dumps(signup_body), headers=signup_headers)
        signup_response_status_code = signup_response.status_code
        self.assertEqual(201, signup_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}".format(uri=get_all_competitions_uri, status_code=signup_response_status_code))
        signup_response_json_string = signup_response.content
        signup_response_dict = json.loads(signup_response_json_string)
        self.assertTrue('token' in signup_response_dict, msg="We got an unexpected result from the endpoint at {uri} as we got {result}".format(uri=signup_uri, result=signup_response_dict))
        valid_access_token = signup_response_dict['token']
        
        # Test createCompetition endpoint with valid authentication
        create_competition_uri = urllib.parse.urljoin(api_base_uri_string, "createCompetition")
        competition_1_name = "competition_{random_string}".format(random_string=random_string())
        create_competition_body = {
	    "competitionName": competition_1_name,
	    "creatorHandle": valid_handle
        }
        create_competition_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {token}".format(token=valid_access_token)
        }
        create_competition_response = requests.post(create_competition_uri, data=json.dumps(create_competition_body), headers=create_competition_headers)
        create_competition_response_status_code = create_competition_response.status_code
        self.assertEqual(201, create_competition_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}".format(uri=create_competition_uri, status_code=create_competition_response_status_code))
        # Test that we have exactly 1 competition
        all_competitions_response = requests.get(url=get_all_competitions_uri)
        all_competitions_response_status_code = all_competitions_response.status_code
        self.assertEqual(200, all_competitions_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}".format(uri=get_all_competitions_uri, status_code=all_competitions_response_status_code))
        all_competitions_json_string = all_competitions_response.content
        all_competitions = json.loads(all_competitions_json_string)
        self.assertTrue(isinstance(all_competitions,list), msg="The response from the endpoint at {get_all_competitions_uri} didn't return JSON content of the correct type (we expected a list). We got the following: \n\n{all_competitions_json_string}\n\n".format(get_all_competitions_uri=get_all_competitions_uri, all_competitions_json_string=all_competitions_json_string))
        self.assertEqual(len(all_competitions), 1, msg="The response from the endpoint at {get_all_competitions_uri} didn't return a singleton list. We expect there to be only one competition so far as we only created one competition since the firestore emulator was just initialized.".format(get_all_competitions_uri=get_all_competitions_uri))
        only_competition = all_competitions[0]
        self.assertEqual(only_competition["competitionName"], competition_1_name,
                         msg="Unexpected competitionName value for the first competition created in {result}.".format(result=only_competition))
        self.assertEqual(only_competition["creatorHandle"], valid_handle, msg="Unexpected creatorHandle value for the first competition created in {result}.".format(result=only_competition))
        
        # Test competition delete endpoint fails for bad authentication
        competition_to_delete = only_competition
        competition_to_delete_id = competition_to_delete["competitionId"]
        delete_competition_uri = urllib.parse.urljoin(api_base_uri_string, "competition/"+competition_to_delete_id)
        delete_competition_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {bad_credentials_token}".format(bad_credentials_token=bad_credentials_token)
        }
        delete_competition_response = requests.delete(delete_competition_uri, headers=delete_competition_headers)
        # Test competition deletion failed
        all_competitions_response = requests.get(url=get_all_competitions_uri)
        all_competitions_response_status_code = all_competitions_response.status_code
        self.assertEqual(200, all_competitions_response_status_code, msg="Failed to hit the endpoint at {uri} after deleting a competition as we got the status code of {status_code}".format(uri=get_all_competitions_uri, status_code=all_competitions_response_status_code))
        all_competitions_json_string = all_competitions_response.content
        all_competitions = json.loads(all_competitions_json_string)
        self.assertTrue(isinstance(all_competitions,list), msg="The response from the endpoint at {get_all_competitions_uri} didn't return JSON content of the correct type (we expected a list). We got the following: \n\n{all_competitions_json_string}\n\n".format(get_all_competitions_uri=get_all_competitions_uri, all_competitions_json_string=all_competitions_json_string))
        self.assertEqual(len(all_competitions), 1, msg="The response from the endpoint at {get_all_competitions_uri} didn't return a singleton list. We expect there to be exactly one competition since we created one with valid authentication and attempted to delete it with invalid authentication.".format(get_all_competitions_uri=get_all_competitions_uri))
        
        organization_name = "organization_{num}".format(num=random_string())
        
        # Test addUserDetails endpoint fails for bad authentication 
        add_user_details_uri = urllib.parse.urljoin(api_base_uri_string, "users/addUserDetails")
        add_user_details_body = {
	    "organizationName": organization_name
        }
        add_user_details_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {bad_credentials_token}".format(bad_credentials_token=bad_credentials_token)
        }
        add_user_details_response = requests.post(add_user_details_uri, data=json.dumps(add_user_details_body), headers=add_user_details_headers)
        add_user_details_response_status_code = add_user_details_response.status_code
        # Test getUserDetails endpoint (in order to verify that the addUserDetails endpoint hit with bad authentication failed)
        get_user_details_uri = urllib.parse.urljoin(api_base_uri_string, "users/getUserDetails")
        get_user_details_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {token}".format(token=valid_access_token)
        }
        get_user_details_response = requests.get(url=get_user_details_uri, headers=get_user_details_headers)
        get_user_details_response_status_code = get_user_details_response.status_code
        self.assertEqual(200, get_user_details_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}".format(uri=get_user_details_uri, status_code=get_user_details_response_status_code))
        get_user_details_json_string = get_user_details_response.content
        user_details_dict = json.loads(get_user_details_json_string)
        self.assertTrue(isinstance(user_details_dict,dict), msg="The response from the endpoint at {get_user_details_uri} didn't return JSON content of the correct type (we expected a dictionary). We got the following: \n\n{get_user_details_json_string}\n\n".format(get_user_details_uri=get_user_details_uri, get_user_details_json_string=get_user_details_json_string))
        self.assertFalse("organizationName" in user_details_dict, msg="We got an unexpected result from the endpoint at {get_user_details_uri} as we got {result} since we did not expect our previous attempt to hit the {add_user_details_uri} with bad credentials to succeed.".format(get_user_details_uri=get_user_details_uri, result=user_details_dict, add_user_details_uri=add_user_details_uri))
        
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
        delete_test_user_from_production_db_via_email(valid_email)
        self.assertTrue(len(list(all_test_user_emails_in_production_db())) < MAX_NUMBER_OF_TOLERABLE_TEST_USERS,
                        "There are too many test users in the production database. A clean up is necessary.")

###############
# Main Runner #
###############

if __name__ == '__main__':
    print("This module contains unit test cases intended to verify that all the webservices for https://github.com/paul-tqh-nguyen/swing_dance_scores/ that require authentication actually require authentication. The authentication is handled by our production DB, but storage is tested by a local firestore emulator.")
