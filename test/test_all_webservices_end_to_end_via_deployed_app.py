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
        self.assertEqual(201, signup_response_status_code, msg="Failed to hit the endpoint at {uri} as we got the status code of {status_code}".format(uri=signup_uri, status_code=signup_response_status_code))
        signup_response_json_string = signup_response.content
        signup_response_dict = json.loads(signup_response_json_string)
        self.assertTrue('token' in signup_response_dict, msg="We got an unexpected result from the endpoint at {uri} as we got {result}".format(uri=signup_uri, result=signup_response_dict))
        access_token = signup_response_dict['token']

        # Get User Info
        # Edit User Info
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
