#!/usr/bin/python3

"""

This module contains a basic unit test case intended to verify that https://us-central1-swing-dance-scores.cloudfunctions.net/api/modifiableCompetitions and https://us-central1-swing-dance-scores.cloudfunctions.net/api/visibleCompetitions work as intended. The authentication is handled by our production DB, but storage is tested by a local firestore emulator.

Owner : paul-tqh-nguyen

Created : 12/28/2019

File Name : test_find_visible_and_modifiable_competitions_webservice_via_local_firestore_emulator.py

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

class testFindVisibleAndModifiableCompetitionsWebserviceViaLocalFirestoreEmulator(unittest.TestCase):
    def testFindVisibleAndModifiableCompetitionsWebserviceViaLocalFirestoreEmulator(self):
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
  
            first_user_test_handle, first_user_test_email, first_user_test_password = generate_new_test_email_and_password_and_user_handle()      
          
            # Test signup endpoint
            signup_uri = urllib.parse.urljoin(api_base_uri_string, "signup")
            signup_body = {
                "email": first_user_test_email,
                "password": first_user_test_password,
                "confirmPassword": first_user_test_password,
                "handle": first_user_test_handle,
            }
            signup_headers = {'Content-Type': 'application/json'}
            signup_response = requests.post(signup_uri, data=json.dumps(signup_body), headers=signup_headers)
            signup_response_status_code = signup_response.status_code
            self.assertEqual(201, signup_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}.".format(uri=signup_uri, status_code=signup_response_status_code))
            signup_response_json_string = signup_response.content
            signup_response_dict = json.loads(signup_response_json_string)
            self.assertTrue('token' in signup_response_dict, msg="We got an unexpected result from the endpoint at {uri} as we got {result}".format(uri=signup_uri, result=signup_response_dict))
            first_user_access_token = signup_response_dict['token']
          
            # Test createCompetition endpoint by creating a private competition
            create_competition_uri = urllib.parse.urljoin(api_base_uri_string, "createCompetition")
            private_competition_name = "first_user_private_competition_{random_string}".format(random_string=random_string())
            private_competition_category = "finals"
            private_competition_judges = ["Alice", "Bob", "Cartman",]
            private_competition_privacy = "private"
            private_competition_competitor_info = []
            create_private_competition_body = {
    	        "competitionName": private_competition_name,
    	        "creatorHandle": first_user_test_handle,
                "category": private_competition_category,
                "judges": private_competition_judges,
                "usersWithModificationPrivileges": [first_user_test_handle],
                "privacy": private_competition_privacy,
                "competitorInfo": private_competition_competitor_info,
            }
            create_private_competition_headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {token}".format(token=first_user_access_token)
            }  
            create_private_competition_response = requests.post(create_competition_uri, data=json.dumps(create_private_competition_body), headers=create_private_competition_headers)
            create_private_competition_response_status_code = create_private_competition_response.status_code
            create_private_competition_response_json_string = create_private_competition_response.content
            create_private_competition_response_result_dict = json.loads(create_private_competition_response_json_string)
            first_user_private_competition_id = create_private_competition_response_result_dict["competitionId"]
            self.assertEqual(201, create_private_competition_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}. The contents of the response were:\n\n{contents}".format(uri=create_competition_uri, status_code=create_private_competition_response_status_code, contents=create_private_competition_response_json_string.decode('utf-8')))
  
            # Test that we have exactly 1 competition via visibleCompetitions with proper authentication
            all_competitions_uri = urllib.parse.urljoin(api_base_uri_string, "visibleCompetitions")
            all_competitions_headers = create_private_competition_headers
            all_competitions_response = requests.get(url=all_competitions_uri, headers=all_competitions_headers)
            all_competitions_response_status_code = all_competitions_response.status_code
            self.assertEqual(200, all_competitions_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}".format(uri=all_competitions_uri, status_code=all_competitions_response_status_code))
            all_competitions_json_string = all_competitions_response.content
            competition_dicts = json.loads(all_competitions_json_string)
            self.assertTrue(isinstance(competition_dicts,list), msg="The response from the endpoint at {all_competitions_uri} didn't return JSON content of the correct type (we expected a list). We got the following: \n\n{all_competitions_json_string}\n\n".format(all_competitions_uri=all_competitions_uri, all_competitions_json_string=all_competitions_json_string))
            self.assertEqual(len(competition_dicts), 1, msg="The response from the endpoint at {all_competitions_uri} didn't return a singleton list. We expect there to be only one competition so far as we only created one competition since the firestore emulator was just initialized.".format(all_competitions_uri=all_competitions_uri))
            only_competition = competition_dicts[0]
            self.assertTrue("competitionName" in only_competition, msg="Competition malformed as no competition name was specified. The competition info is {result}.".format(result=only_competition))
            self.assertEqual(only_competition["competitionName"], private_competition_name,
                             msg="Unexpected competitionName value for the first competition created in {result}.".format(result=only_competition))
            self.assertTrue("creatorHandle" in only_competition, msg="Competition malformed as no creator handle was specified. The competition info is {result}.".format(result=only_competition))
            self.assertEqual(only_competition["creatorHandle"], first_user_test_handle, msg="Unexpected creatorHandle value for the first competition created in {result}.".format(result=only_competition))
            self.assertTrue("category" in only_competition and only_competition["category"]==private_competition_category, msg="We could not gather the competition category set (i.e. {category}) when we created the competition. The competition data is {competition_data} ".format(category=private_competition_category, competition_data=json.dumps(only_competition)))
            self.assertTrue("judges" in only_competition and set(only_competition["judges"])==set(private_competition_judges),
                            msg="We could not gather the judges set (i.e. {judges}) when we created the competition. The competition data is {competition_data} ".format(judges=", ".join(private_competition_judges), competition_data=json.dumps(only_competition)))
            self.assertTrue("usersWithModificationPrivileges" in only_competition and only_competition["usersWithModificationPrivileges"]==[first_user_test_handle],
                            msg="We could not gather the users with modification privileges set (i.e. {user}) when we created the competition. The competition data is {competition_data} ".format(user=first_user_test_handle, competition_data=json.dumps(only_competition)))
            self.assertTrue("privacy" in only_competition and only_competition["privacy"]==private_competition_privacy, msg="We could not gather the privacy set (i.e. {privacy}) when we created the competition. The competition data is {competition_data} ".format(privacy=private_competition_privacy, competition_data=json.dumps(only_competition)))
            self.assertTrue("competitorInfo" in only_competition and only_competition["competitorInfo"]==private_competition_competitor_info, msg="We could not gather the competitor information set (i.e. {competitorInfo}) when we created the competition. The competition data is {competition_data} ".format(competitorInfo=private_competition_competitor_info, competition_data=json.dumps(only_competition)))
            self.assertTrue("competitionId" in only_competition and only_competition["competitionId"]==first_user_private_competition_id, msg="We could not gather the competition ID retrieved (i.e. {competition_id}) when we created the competition. The competition data is {competition_data} ".format(competition_id=first_user_private_competition_id, competition_data=json.dumps(only_competition)))
          
            # Test that we have exactly 0 competitions via visibleCompetitions with no authentication
            all_competitions_uri = urllib.parse.urljoin(api_base_uri_string, "visibleCompetitions")
            all_competitions_headers = {'Content-Type': 'application/json'}
            all_competitions_response = requests.get(url=all_competitions_uri, headers=all_competitions_headers)
            all_competitions_response_status_code = all_competitions_response.status_code
            self.assertEqual(200, all_competitions_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}".format(uri=all_competitions_uri, status_code=all_competitions_response_status_code))
            all_competitions_json_string = all_competitions_response.content
            competition_dicts = json.loads(all_competitions_json_string)
            self.assertTrue(isinstance(competition_dicts,list), msg="The response from the endpoint at {all_competitions_uri} didn't return JSON content of the correct type (we expected a list). We got the following: \n\n{all_competitions_json_string}\n\n".format(all_competitions_uri=all_competitions_uri, all_competitions_json_string=all_competitions_json_string))
            self.assertEqual(len(competition_dicts), 0, msg="The response from the endpoint at {all_competitions_uri} didn't return an empty list. We expect there to be no competitions so far as we only created one competition since no authentication was used.".format(all_competitions_uri=all_competitions_uri))
          
            # Test createCompetition endpoint by creating a public competition
            create_competition_uri = urllib.parse.urljoin(api_base_uri_string, "createCompetition")
            public_competition_name = "first_user_public_competition_{random_string}".format(random_string=random_string())
            public_competition_category = "prelims"
            public_competition_judges = ["Donnell", "Edith", "Fred",]
            public_competition_privacy = "public"
            public_competition_competitor_info = []
            create_public_competition_body = {
    	        "competitionName": public_competition_name,
    	        "creatorHandle": first_user_test_handle,
                "category": public_competition_category,
                "judges": public_competition_judges,
                "usersWithModificationPrivileges": [first_user_test_handle],
                "privacy": public_competition_privacy,
                "competitorInfo": public_competition_competitor_info,
            }
            create_public_competition_headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {token}".format(token=first_user_access_token)
            }
            create_public_competition_response = requests.post(create_competition_uri, data=json.dumps(create_public_competition_body), headers=create_public_competition_headers)
            create_public_competition_response_status_code = create_public_competition_response.status_code
            create_public_competition_response_json_string = create_public_competition_response.content
            create_public_competition_response_result_dict = json.loads(create_public_competition_response_json_string)
            public_competition_id = create_public_competition_response_result_dict["competitionId"]
            self.assertEqual(201, create_public_competition_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}. The contents of the response were:\n\n{contents}".format(uri=create_competition_uri, status_code=create_public_competition_response_status_code, contents=create_public_competition_response_json_string.decode('utf-8')))
          
            # Test that we have exactly 2 competitions via visibleCompetitions with proper authentication
            all_competitions_uri = urllib.parse.urljoin(api_base_uri_string, "visibleCompetitions")
            all_competitions_headers = create_public_competition_headers
            all_competitions_response = requests.get(url=all_competitions_uri, headers=all_competitions_headers)
            all_competitions_response_status_code = all_competitions_response.status_code
            self.assertEqual(200, all_competitions_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}".format(uri=all_competitions_uri, status_code=all_competitions_response_status_code))
            all_competitions_json_string = all_competitions_response.content
            competition_dicts = json.loads(all_competitions_json_string)
            self.assertTrue(isinstance(competition_dicts,list), msg="The response from the endpoint at {all_competitions_uri} didn't return JSON content of the correct type (we expected a list). We got the following: \n\n{all_competitions_json_string}\n\n".format(all_competitions_uri=all_competitions_uri, all_competitions_json_string=all_competitions_json_string))
            self.assertEqual(len(competition_dicts), 2, msg="The response from the endpoint at {all_competitions_uri} didn't return a doubleton list. We expect there to be only 2 competitions so far as we only created two competitions. We got the following competitions {competition_data}.".format(all_competitions_uri=all_competitions_uri, competition_data=all_competitions_json_string))
            public_competition = None
            private_competition = None
            for competition_dict in competition_dicts:
                self.assertTrue(competition_dict['privacy'] in ['public',  'private'], msg="We got the following unexpected from competition from the DB: {competition}".format(competition=json.dumps(competition_dict)))
                if competition_dict['privacy'] == 'public':
                    public_competition = competition_dict
                elif competition_dict['privacy'] == 'private':
                    private_competition = competition_dict
            first_user_public_competition_id = public_competition["competitionId"]
            first_user_private_competition_id = private_competition["competitionId"]
            # Verify the private competition is as expected
            self.assertTrue("competitionName" in private_competition, msg="Competition malformed as no competition name was specified. The competition info is {result}.".format(result=private_competition))
            self.assertEqual(private_competition["competitionName"], private_competition_name,
                             msg="Unexpected competitionName value for the first competition created in {result}.".format(result=private_competition))
            self.assertTrue("creatorHandle" in private_competition, msg="Competition malformed as no creator handle was specified. The competition info is {result}.".format(result=private_competition))
            self.assertEqual(private_competition["creatorHandle"], first_user_test_handle, msg="Unexpected creatorHandle value for the first competition created in {result}.".format(result=private_competition))
            self.assertTrue("category" in private_competition and private_competition["category"]==private_competition_category, msg="We could not gather the competition category set (i.e. {category}) when we created the competition. The competition data is {competition_data} ".format(category=private_competition_category, competition_data=json.dumps(private_competition)))
            self.assertTrue("judges" in private_competition and set(private_competition["judges"])==set(private_competition_judges),
                            msg="We could not gather the judges set (i.e. {judges}) when we created the competition. The competition data is {competition_data} ".format(judges=", ".join(private_competition_judges), competition_data=json.dumps(private_competition)))
            self.assertTrue("usersWithModificationPrivileges" in private_competition and private_competition["usersWithModificationPrivileges"]==[first_user_test_handle],
                            msg="We could not gather the users with modification privileges set (i.e. {user}) when we created the competition. The competition data is {competition_data} ".format(user=first_user_test_handle, competition_data=json.dumps(private_competition)))
            self.assertTrue("privacy" in private_competition and private_competition["privacy"]==private_competition_privacy, msg="We could not gather the privacy set (i.e. {privacy}) when we created the competition. The competition data is {competition_data} ".format(privacy=private_competition_privacy, competition_data=json.dumps(private_competition)))
            self.assertTrue("competitorInfo" in private_competition and private_competition["competitorInfo"]==private_competition_competitor_info, msg="We could not gather the competitor information set (i.e. {competitorInfo}) when we created the competition. The competition data is {competition_data} ".format(competitorInfo=private_competition_competitor_info, competition_data=json.dumps(private_competition)))
            self.assertTrue("competitionId" in private_competition and private_competition["competitionId"]==first_user_private_competition_id, msg="We could not gather the competition ID retrieved (i.e. {competition_id}) when we created the competition. The competition data is {competition_data} ".format(competition_id=first_user_private_competition_id, competition_data=json.dumps(private_competition)))
            # Verify the public competition is as expected
            self.assertTrue("competitionName" in public_competition, msg="Competition malformed as no competition name was specified. The competition info is {result}.".format(result=public_competition))
            self.assertEqual(public_competition["competitionName"], public_competition_name,
                             msg="Unexpected competitionName value for the first competition created in {result}.".format(result=public_competition))
            self.assertTrue("creatorHandle" in public_competition, msg="Competition malformed as no creator handle was specified. The competition info is {result}.".format(result=public_competition))
            self.assertEqual(public_competition["creatorHandle"], first_user_test_handle, msg="Unexpected creatorHandle value for the first competition created in {result}.".format(result=public_competition))
            self.assertTrue("category" in public_competition and public_competition["category"]==public_competition_category, msg="We could not gather the competition category set (i.e. {category}) when we created the competition. The competition data is {competition_data} ".format(category=public_competition_category, competition_data=json.dumps(public_competition)))
            self.assertTrue("judges" in public_competition and set(public_competition["judges"])==set(public_competition_judges),
                            msg="We could not gather the judges set (i.e. {judges}) when we created the competition. The competition data is {competition_data} ".format(judges=", ".join(public_competition_judges), competition_data=json.dumps(public_competition)))
            self.assertTrue("usersWithModificationPrivileges" in public_competition and public_competition["usersWithModificationPrivileges"]==[first_user_test_handle],
                            msg="We could not gather the users with modification privileges set (i.e. {user}) when we created the competition. The competition data is {competition_data} ".format(user=first_user_test_handle, competition_data=json.dumps(public_competition)))
            self.assertTrue("privacy" in public_competition and public_competition["privacy"]==public_competition_privacy, msg="We could not gather the privacy set (i.e. {privacy}) when we created the competition. The competition data is {competition_data} ".format(privacy=public_competition_privacy, competition_data=json.dumps(public_competition)))
            self.assertTrue("competitorInfo" in public_competition and public_competition["competitorInfo"]==public_competition_competitor_info, msg="We could not gather the competitor information set (i.e. {competitorInfo}) when we created the competition. The competition data is {competition_data} ".format(competitorInfo=public_competition_competitor_info, competition_data=json.dumps(public_competition)))
            self.assertTrue("competitionId" in public_competition and public_competition["competitionId"]==public_competition_id, msg="We could not gather the competition ID retrieved (i.e. {competition_id}) when we created the competition. The competition data is {competition_data} ".format(competition_id=public_competition_id, competition_data=json.dumps(public_competition)))
          
            # Test that we have exactly 1 competition via visibleCompetitions with no authentication
            all_competitions_uri = urllib.parse.urljoin(api_base_uri_string, "visibleCompetitions")
            all_competitions_headers = {'Content-Type': 'application/json'}
            all_competitions_response = requests.get(url=all_competitions_uri, headers=all_competitions_headers)
            all_competitions_response_status_code = all_competitions_response.status_code
            self.assertEqual(200, all_competitions_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}".format(uri=all_competitions_uri, status_code=all_competitions_response_status_code))
            all_competitions_json_string = all_competitions_response.content
            competition_dicts = json.loads(all_competitions_json_string)
            self.assertTrue(isinstance(competition_dicts,list), msg="The response from the endpoint at {all_competitions_uri} didn't return JSON content of the correct type (we expected a list). We got the following: \n\n{all_competitions_json_string}\n\n".format(all_competitions_uri=all_competitions_uri, all_competitions_json_string=all_competitions_json_string))
            self.assertEqual(len(competition_dicts), 1, msg="The response from the endpoint at {all_competitions_uri} didn't return an empty list. We expect there to be no competitions so far as we only created one competition since no authentication was used.".format(all_competitions_uri=all_competitions_uri))
            public_competition = competition_dicts[0]
            self.assertTrue("competitionName" in public_competition, msg="Competition malformed as no competition name was specified. The competition info is {result}.".format(result=public_competition))
            self.assertEqual(public_competition["competitionName"], public_competition_name,
                             msg="Unexpected competitionName value for the first competition created in {result}.".format(result=public_competition))
            self.assertTrue("creatorHandle" in public_competition, msg="Competition malformed as no creator handle was specified. The competition info is {result}.".format(result=public_competition))
            self.assertEqual(public_competition["creatorHandle"], first_user_test_handle, msg="Unexpected creatorHandle value for the first competition created in {result}.".format(result=public_competition))
            self.assertTrue("category" in public_competition and public_competition["category"]==public_competition_category, msg="We could not gather the competition category set (i.e. {category}) when we created the competition. The competition data is {competition_data} ".format(category=public_competition_category, competition_data=json.dumps(public_competition)))
            self.assertTrue("judges" in public_competition and set(public_competition["judges"])==set(public_competition_judges),
                            msg="We could not gather the judges set (i.e. {judges}) when we created the competition. The competition data is {competition_data} ".format(judges=", ".join(public_competition_judges), competition_data=json.dumps(public_competition)))
            self.assertTrue("usersWithModificationPrivileges" in public_competition and public_competition["usersWithModificationPrivileges"]==[first_user_test_handle],
                            msg="We could not gather the users with modification privileges set (i.e. {user}) when we created the competition. The competition data is {competition_data} ".format(user=first_user_test_handle, competition_data=json.dumps(public_competition)))
            self.assertTrue("privacy" in public_competition and public_competition["privacy"]==public_competition_privacy, msg="We could not gather the privacy set (i.e. {privacy}) when we created the competition. The competition data is {competition_data} ".format(privacy=public_competition_privacy, competition_data=json.dumps(public_competition)))
            self.assertTrue("competitorInfo" in public_competition and public_competition["competitorInfo"]==public_competition_competitor_info, msg="We could not gather the competitor information set (i.e. {competitorInfo}) when we created the competition. The competition data is {competition_data} ".format(competitorInfo=public_competition_competitor_info, competition_data=json.dumps(public_competition)))
            self.assertTrue("competitionId" in public_competition and public_competition["competitionId"]==public_competition_id, msg="We could not gather the competition ID retrieved (i.e. {competition_id}) when we created the competition. The competition data is {competition_data} ".format(competition_id=public_competition_id, competition_data=json.dumps(public_competition)))
          
            second_user_test_handle, second_user_test_email, second_user_test_password = generate_new_test_email_and_password_and_user_handle()
          
            # Test signup endpoint by creating second user
            signup_uri = urllib.parse.urljoin(api_base_uri_string, "signup")
            signup_body = {
                "email": second_user_test_email,
                "password": second_user_test_password,
                "confirmPassword": second_user_test_password,
                "handle": second_user_test_handle,
            }
            signup_headers = {'Content-Type': 'application/json'}
            signup_response = requests.post(signup_uri, data=json.dumps(signup_body), headers=signup_headers)
            signup_response_status_code = signup_response.status_code
            self.assertEqual(201, signup_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}.".format(uri=signup_uri, status_code=signup_response_status_code))
            signup_response_json_string = signup_response.content
            signup_response_dict = json.loads(signup_response_json_string)
            self.assertTrue('token' in signup_response_dict, msg="We got an unexpected result from the endpoint at {uri} as we got {result}".format(uri=signup_uri, result=signup_response_dict))
            second_user_access_token = signup_response_dict['token']
          
            # Test createCompetition endpoint by creating a public competition via the second user's credentials
            create_competition_uri = urllib.parse.urljoin(api_base_uri_string, "createCompetition")
            second_user_public_competition_name = "second_user_public_competition_{random_string}".format(random_string=random_string())
            second_user_public_competition_category = "prelims"
            second_user_public_competition_judges = ["Gerald", "Herald", "Ingrid",]
            second_user_public_competition_privacy = "public"
            second_user_public_competition_competitor_info = []
            create_second_user_public_competition_body = {
    	        "competitionName": second_user_public_competition_name,
    	        "creatorHandle": second_user_test_handle,
                "category": second_user_public_competition_category,
                "judges": second_user_public_competition_judges,
                "usersWithModificationPrivileges": [second_user_test_handle],
                "privacy": second_user_public_competition_privacy,
                "competitorInfo": second_user_public_competition_competitor_info,
            }
            create_second_user_public_competition_headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {token}".format(token=second_user_access_token)
            }
            create_second_user_public_competition_response = requests.post(create_competition_uri, data=json.dumps(create_second_user_public_competition_body), headers=create_second_user_public_competition_headers)
            create_second_user_public_competition_response_status_code = create_second_user_public_competition_response.status_code
            create_second_user_public_competition_response_json_string = create_second_user_public_competition_response.content
            create_second_user_public_competition_response_result_dict = json.loads(create_second_user_public_competition_response_json_string)
            second_user_public_competition_id = create_second_user_public_competition_response_result_dict["competitionId"]
            self.assertEqual(201, create_second_user_public_competition_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}. The contents of the response were:\n\n{contents}".format(uri=create_competition_uri, status_code=create_second_user_public_competition_response_status_code, contents=create_second_user_public_competition_response_json_string.decode('utf-8')))
            # Find this most recent competition
            find_competition_uri = urllib.parse.urljoin(api_base_uri_string, "competition/{competition_id}".format(competition_id=second_user_public_competition_id))
            find_competition_headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {token}".format(token=second_user_access_token)
            }
            find_competition_response = requests.get(find_competition_uri, headers=find_competition_headers)
            find_competition_response_status_code = find_competition_response.status_code
            find_competition_response_json_string = find_competition_response.content
            second_user_public_competition = json.loads(find_competition_response_json_string)
            self.assertTrue("competitionName" in second_user_public_competition, msg="Competition malformed as no competition name was specified. The competition info is {result}.".format(result=second_user_public_competition))
            self.assertEqual(second_user_public_competition["competitionName"], second_user_public_competition_name,
                             msg="Unexpected competitionName value for the first competition created in {result}.".format(result=second_user_public_competition))
            self.assertTrue("creatorHandle" in second_user_public_competition, msg="Competition malformed as no creator handle was specified. The competition info is {result}.".format(result=second_user_public_competition))
            self.assertEqual(second_user_public_competition["creatorHandle"], second_user_test_handle, msg="Unexpected creatorHandle value for the first competition created in {result}.".format(result=second_user_public_competition))
            self.assertTrue("category" in second_user_public_competition and second_user_public_competition["category"]==second_user_public_competition_category, msg="We could not gather the competition category set (i.e. {category}) when we created the competition. The competition data is {competition_data} ".format(category=second_user_public_competition_category, competition_data=json.dumps(second_user_public_competition)))
            self.assertTrue("judges" in second_user_public_competition and set(second_user_public_competition["judges"])==set(second_user_public_competition_judges),
                            msg="We could not gather the judges set (i.e. {judges}) when we created the competition. The competition data is {competition_data} ".format(judges=", ".join(second_user_public_competition_judges), competition_data=json.dumps(second_user_public_competition)))
            self.assertTrue("usersWithModificationPrivileges" in second_user_public_competition and second_user_public_competition["usersWithModificationPrivileges"]==[second_user_test_handle],
                            msg="We could not gather the users with modification privileges set (i.e. {user}) when we created the competition. The competition data is {competition_data} ".format(user=second_user_test_handle, competition_data=json.dumps(second_user_public_competition)))
            self.assertTrue("privacy" in second_user_public_competition and second_user_public_competition["privacy"]==second_user_public_competition_privacy, msg="We could not gather the privacy set (i.e. {privacy}) when we created the competition. The competition data is {competition_data} ".format(privacy=second_user_public_competition_privacy, competition_data=json.dumps(second_user_public_competition)))
            self.assertTrue("competitorInfo" in second_user_public_competition and second_user_public_competition["competitorInfo"]==second_user_public_competition_competitor_info, msg="We could not gather the competitor information set (i.e. {competitorInfo}) when we created the competition. The competition data is {competition_data} ".format(competitorInfo=second_user_public_competition_competitor_info, competition_data=json.dumps(second_user_public_competition)))
          
            # Make sure first user can only modify two competitions
            find_modifiable_competitions_uri = urllib.parse.urljoin(api_base_uri_string, "modifiableCompetitions")
            first_user_find_modifiable_competition_headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {token}".format(token=first_user_access_token)
            }
            first_user_find_modifiable_competition_response = requests.get(find_modifiable_competitions_uri, headers=first_user_find_modifiable_competition_headers)
            first_user_find_modifiable_competition_response_status_code = first_user_find_modifiable_competition_response.status_code
            first_user_find_modifiable_competition_response_json_string = first_user_find_modifiable_competition_response.content
            first_user_modifiable_competitions = json.loads(first_user_find_modifiable_competition_response_json_string)
            self.assertEqual(len(first_user_modifiable_competitions), 2, msg="We expected to only have two modifiable competitions for the user with handle {handle}, but we got {result}.".format(handle=first_user_test_handle, result=first_user_find_modifiable_competition_response_json_string))
            first_user_modifiable_public_competition = None
            first_user_modifiable_private_competition = None
            for competition_dict in first_user_modifiable_competitions:
                self.assertTrue(competition_dict['privacy'] in ['public',  'private'], msg="We got the following unexpected from competition from the DB: {competition}".format(competition=json.dumps(competition_dict)))
                if competition_dict['privacy'] == "public":
                    first_user_modifiable_public_competition = competition_dict
                elif competition_dict['privacy'] == "private":
                    first_user_modifiable_private_competition = competition_dict
            self.assertEqual(first_user_modifiable_public_competition["competitionId"], first_user_public_competition_id, msg="We expected the only modifiable competition for the user with handle {handle} to have competitionId {competition_id}, but we got {result}.".format(handle=first_user_test_handle, competition_id=first_user_public_competition_id, result=first_user_find_modifiable_competition_response_json_string))
            self.assertEqual(first_user_modifiable_private_competition["competitionId"], first_user_private_competition_id, msg="We expected the only modifiable competition for the user with handle {handle} to have competitionId {competition_id}, but we got {result}.".format(handle=first_user_test_handle, competition_id=first_user_private_competition_id, result=first_user_find_modifiable_competition_response_json_string))
          
            # Make sure second user can only modify one competition
            find_modifiable_competitions_uri = urllib.parse.urljoin(api_base_uri_string, "modifiableCompetitions")
            second_user_find_modifiable_competition_headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {token}".format(token=second_user_access_token)
            }
            second_user_find_modifiable_competition_response = requests.get(find_modifiable_competitions_uri, headers=second_user_find_modifiable_competition_headers)
            second_user_find_modifiable_competition_response_status_code = second_user_find_modifiable_competition_response.status_code
            second_user_find_modifiable_competition_response_json_string = second_user_find_modifiable_competition_response.content
            second_user_modifiable_competitions = json.loads(second_user_find_modifiable_competition_response_json_string)
            self.assertEqual(len(second_user_modifiable_competitions), 1, msg="We expected to only have one modifiable competition for the user with handle {handle}, but we got {result}.".format(handle=second_user_test_handle, result=second_user_find_modifiable_competition_response_json_string))
            second_user_modifiable_competition = second_user_modifiable_competitions[0]
            self.assertEqual(second_user_modifiable_competition["competitionId"], second_user_public_competition_id, msg="We expected the only modifiable competition for the user with handle {handle} to have competitionId {competition_id}, but we got {result}.".format(handle=second_user_test_handle, competition_id=second_user_public_competition_id, result=second_user_find_modifiable_competition_response_json_string))
          
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
            delete_test_user_from_production_db_via_email(first_user_test_email)
            delete_test_user_from_production_db_via_email(second_user_test_email)
            self.assertTrue(len(list(all_test_user_emails_in_production_db())) < MAX_NUMBER_OF_TOLERABLE_TEST_USERS,
                            "There are too many test users in the production database. A clean up is necessary.")
        except AssertionError as error:
            print("Below is the output of the local firestore:\n\n{firestore_stdout}".format(firestore_stdout=extract_stdout_from_subprocess(firestore_emulation_process)))
            raise error

###############
# Main Runner #
###############

if __name__ == '__main__':
    print("""This module contains a basic unit test case intended to verify that the "sign up" or "create user" webservices for https://github.com/paul-tqh-nguyen/swing_dance_scores/ works as intended. The authentication is handled by our production DB, but storage is tested by a local firestore emulator.""")
