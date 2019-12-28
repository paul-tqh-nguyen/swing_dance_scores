#!/usr/bin/python3

"""

This module contains an end-to-end integration test intended to verify that all the webservices for https://github.com/paul-tqh-nguyen/swing_dance_scores/ work as intended via the deployed webservices and database.

Owner : paul-tqh-nguyen

Created : 10/12/2019

File Name : test_all_webservices_end_to_end_via_deployed_app.py

File Organization:
* Imports
* Tests
* Main Runner

"""

###########
# Imports #
###########

# @todo sweep these
import sys; sys.path.append(".."); from util.miscellaneous_utilities import *
from .test_utilities import *
import unittest
# import subprocess
# import os
# import signal
import requests
import urllib.parse
import json
# import time

#########
# Tests #
#########

class testAllWebServicesEndToEndViaDeployedApp(unittest.TestCase): 
    def testAllWebServicesEndToEndViaDeployedApp(self):
        api_base_uri_string = "https://us-central1-swing-dance-scores.cloudfunctions.net/api/"

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
        self.assertEqual(201, signup_response_status_code, msg="""Failed to hit the endpoint at {uri} as we got the status code of {status_code}. 
The post body used was {post_body}. 
The headers used were {headers}.""".format(uri=signup_uri, status_code=signup_response_status_code, post_body=json.dumps(signup_body), headers=json.dumps(signup_headers)))
        signup_response_json_string = signup_response.content
        signup_response_dict = json.loads(signup_response_json_string)
        self.assertTrue('token' in signup_response_dict, msg="We got an unexpected result from the endpoint at {uri} as we got {result}".format(uri=signup_uri, result=signup_response_dict))
        access_token = signup_response_dict['token']
        
        # Get User Info
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
        self.assertFalse("organizationName" in user_details_dict, msg="We got an unexpected result from the endpoint at {uri} as we got the unexpected key \"organizationName\" in the returned result {result}".format(uri=get_user_details_uri, result=user_details_dict))
        
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
        update_user_details_response = requests.post(url=update_user_details_uri, data=update_user_details_body, headers=update_user_details_headers)
        update_user_details_response_status_code = update_user_details_response.status_code
        update_user_details_json_string = update_user_details_response.content
        self.assertEqual(200, update_user_details_response_status_code, msg="""Failed to hit the endpoint at {uri} as we got the status code of {status_code}. 
The headers used were {headers}.
The body used was {body}.
The returned content was {content}.""".format(uri=update_user_details_uri, status_code=update_user_details_response_status_code, headers=json.dumps(update_user_details_headers), body=json.dumps(update_user_details_body), content=update_user_details_json_string.decode('utf-8')))
        user_details_dict = json.loads(update_user_details_json_string)
        self.assertTrue(isinstance(user_details_dict,dict), msg="The response from the endpoint at {update_user_details_uri} didn't return JSON content of the correct type (we expected a dictionary). We got the following: \n\n{update_user_details_json_string}\n\n".format(update_user_details_uri=update_user_details_uri, update_user_details_json_string=update_user_details_json_string))
        self.assertTrue("organizationName" in user_details_dict, msg="We got an unexpected result from the endpoint at {uri} as we expected the key \"organizationName\" in the returned result {result}".format(uri=update_user_details_uri, result=user_details_dict)) 
        self.assertEqual(user_details_dict["organizationName"], test_organization_name, msg="Unexpected organizationName value for our test user in {result}.".format(result=user_details_dict))
        
        # Get User Info
        # Create Competition
        # Get all competitions owned by user
        # Get competition by id
        # Create Competition
        # Get all competitions owned by user
        # Get competition by id
        # Edit Competition
        # Get all competitions owned by user
        # Get competition by id
        # Delete Competition
        # Get all competitions owned by user
        # Get competition by id
        # Delete User
        
        # Test that we didn't pollute the DB with an unecessary number of users
        delete_test_user_from_production_db_via_email(test_email)
        self.assertTrue(len(list(all_test_user_emails_in_production_db())) < MAX_NUMBER_OF_TOLERABLE_TEST_USERS,
                        "There are too many test users in the production database. A clean up is necessary.")

###############
# Main Runner #
###############

if __name__ == '__main__':
    print("This module contains an end-to-end integration test intended to verify that all the webservices for https://github.com/paul-tqh-nguyen/swing_dance_scores/ work as intended via the deployed webservices and database.")
