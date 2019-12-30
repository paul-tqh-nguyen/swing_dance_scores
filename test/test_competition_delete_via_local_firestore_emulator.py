#!/usr/bin/python3

"""

This module contains a test intended to verify that the webservice to edit competitions works as intended via a local firestore emulator.

Owner : paul-tqh-nguyen

Created : 12/29/2009

File Name : test_competition_edit_via_local_firestore_emulator.py

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

class testCompetitionDeleteViaLocalFirestoreEmulator(unittest.TestCase):
    def testCompetitionDeleteViaLocalFirestoreEmulator(self):
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

            # Test createCompetition endpoint by creating a private competition
            create_competition_uri = urllib.parse.urljoin(api_base_uri_string, "createCompetition")
            competition_name = "competition_{random_string}".format(random_string=random_string())
            competition_category = "finals"
            competition_judges = ["Alice", "Bob", "Cartman",]
            old_competition_privacy = "public"
            competition_competitor_info = []
            create_competition_body = {
    	        "competitionName": competition_name,
    	        "creatorHandle": test_handle,
                "category": competition_category,
                "judges": competition_judges,
                "usersWithModificationPrivileges": [test_handle],
                "privacy": old_competition_privacy,
                "competitorInfo": competition_competitor_info,
            }
            create_competition_headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {token}".format(token=access_token)
            }
            create_competition_response = requests.post(create_competition_uri, data=json.dumps(create_competition_body), headers=create_competition_headers)
            create_competition_response_status_code = create_competition_response.status_code
            create_competition_response_json_string = create_competition_response.content
            create_competition_response_result_dict = json.loads(create_competition_response_json_string)
            competition_id = create_competition_response_result_dict["competitionId"]
            self.assertEqual(201, create_competition_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}. The contents of the response were:\n\n{contents}".format(uri=create_competition_uri, status_code=create_competition_response_status_code, contents=create_competition_response_json_string.decode('utf-8')))
            
            # Verify that we have exactly 1 competition via visibleCompetitions
            all_competitions_uri = urllib.parse.urljoin(api_base_uri_string, "visibleCompetitions")
            all_competitions_headers = create_competition_headers
            all_competitions_response = requests.get(url=all_competitions_uri, headers=all_competitions_headers)
            all_competitions_response_status_code = all_competitions_response.status_code
            self.assertEqual(200, all_competitions_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}".format(uri=all_competitions_uri, status_code=all_competitions_response_status_code))
            all_competitions_json_string = all_competitions_response.content
            competition_dicts = json.loads(all_competitions_json_string)
            self.assertTrue(isinstance(competition_dicts,list), msg="The response from the endpoint at {all_competitions_uri} didn't return JSON content of the correct type (we expected a list). We got the following: \n\n{all_competitions_json_string}\n\n".format(all_competitions_uri=all_competitions_uri, all_competitions_json_string=all_competitions_json_string))
            self.assertEqual(len(competition_dicts), 1, msg="The response from the endpoint at {all_competitions_uri} didn't return a singleton list. We expect there to be only one competition so far as we only created one competition since the firestore emulator was just initialized.".format(all_competitions_uri=all_competitions_uri))
            only_competition = competition_dicts[0]
            self.assertTrue("competitionName" in only_competition, msg="Competition malformed as no competition name was specified. The competition info is {result}.".format(result=only_competition))
            self.assertEqual(only_competition["competitionName"], competition_name,
                             msg="Unexpected competitionName value for the first competition created in {result}.".format(result=only_competition))
            self.assertTrue("creatorHandle" in only_competition, msg="Competition malformed as no creator handle was specified. The competition info is {result}.".format(result=only_competition))
            self.assertEqual(only_competition["creatorHandle"], test_handle, msg="Unexpected creatorHandle value for the first competition created in {result}.".format(result=only_competition))
            self.assertTrue("category" in only_competition and only_competition["category"]==competition_category, msg="We could not gather the competition category set (i.e. {category}) when we created the competition. The competition data is {competition_data} ".format(category=competition_category, competition_data=json.dumps(only_competition)))
            self.assertTrue("judges" in only_competition and set(only_competition["judges"])==set(competition_judges),
                            msg="We could not gather the judges set (i.e. {judges}) when we created the competition. The competition data is {competition_data} ".format(judges=", ".join(competition_judges), competition_data=json.dumps(only_competition)))
            self.assertTrue("usersWithModificationPrivileges" in only_competition and only_competition["usersWithModificationPrivileges"]==[test_handle],
                            msg="We could not gather the users with modification privileges set (i.e. {user}) when we created the competition. The competition data is {competition_data} ".format(user=test_handle, competition_data=json.dumps(only_competition)))
            self.assertTrue("privacy" in only_competition and only_competition["privacy"]==old_competition_privacy, msg="We could not gather the privacy set (i.e. {privacy}) when we created the competition. The competition data is {competition_data} ".format(privacy=old_competition_privacy, competition_data=json.dumps(only_competition)))
            self.assertTrue("competitorInfo" in only_competition and only_competition["competitorInfo"]==competition_competitor_info, msg="We could not gather the competitor information set (i.e. {competitorInfo}) when we created the competition. The competition data is {competition_data} ".format(competitorInfo=competition_competitor_info, competition_data=json.dumps(only_competition)))
            self.assertTrue("competitionId" in only_competition and only_competition["competitionId"]==competition_id, msg="We could not gather the competition ID retrieved (i.e. {competition_id}) when we created the competition. The competition data is {competition_data} ".format(competition_id=competition_id, competition_data=json.dumps(only_competition)))

            # Verify that we cannot delete the competition without authentication
            delete_competition_uri = urllib.parse.urljoin(api_base_uri_string, "competition/{competition_id}".format(competition_id=competition_id))
            delete_competition_headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {token}".format(token=access_token[::-1])
            }  
            delete_competition_response = requests.delete(url=delete_competition_uri, headers=delete_competition_headers)
            delete_competition_response_status_code = delete_competition_response.status_code
            self.assertEqual(403, delete_competition_response_status_code, msg="We got an unexpected status code of {status_code} via the endpoint at {uri} as we expect to not be able to delete any competitions without the proper credentials.".format(uri=delete_competition_uri, status_code=delete_competition_response_status_code))

            # Verify that we can delete the competition with the access token
            delete_competition_uri = urllib.parse.urljoin(api_base_uri_string, "competition/{competition_id}".format(competition_id=competition_id))
            delete_competition_headers = create_competition_headers
            delete_competition_response = requests.delete(url=delete_competition_uri, headers=delete_competition_headers)
            delete_competition_response_status_code = delete_competition_response.status_code
            self.assertEqual(200, delete_competition_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}".format(uri=delete_competition_uri, status_code=delete_competition_response_status_code))
            
            # Verify that we have exactly 0 competitions via visibleCompetitions
            all_competitions_uri = urllib.parse.urljoin(api_base_uri_string, "visibleCompetitions")
            all_competitions_headers = create_competition_headers
            all_competitions_response = requests.get(url=all_competitions_uri, headers=all_competitions_headers)
            all_competitions_response_status_code = all_competitions_response.status_code
            self.assertEqual(200, all_competitions_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}".format(uri=all_competitions_uri, status_code=all_competitions_response_status_code))
            all_competitions_json_string = all_competitions_response.content
            competition_dicts = json.loads(all_competitions_json_string)
            self.assertTrue(isinstance(competition_dicts,list), msg="The response from the endpoint at {all_competitions_uri} didn't return JSON content of the correct type (we expected a list). We got the following: \n\n{all_competitions_json_string}\n\n".format(all_competitions_uri=all_competitions_uri, all_competitions_json_string=all_competitions_json_string))
            self.assertEqual(len(competition_dicts), 0, msg="The response from the endpoint at {all_competitions_uri} didn't return an empty list after we deleted the one competition that existed.".format(all_competitions_uri=all_competitions_uri))
            
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
