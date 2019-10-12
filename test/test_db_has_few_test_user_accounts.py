#!/usr/bin/python3

"""

This module contains a sweep test that verifies that we don't have many test users in the DB at the moment. This will make DB maintenance easier. We will tolerate a small number of test users as there may be multiple test runs going simultaneously.  

Owner : paul-tqh-nguyen

Created : 10/12/2019

File Name : test_db_has_few_test_user_accounts.py

File Organization:
* Imports
* Tests
* Main Runner

"""

###########
# Imports #
###########

from .test_utilities import *
import unittest
import firebase_admin

#########
# Tests #
#########

class testDBHasFewTestUserAccounts(unittest.TestCase):
    def testDBHasFewTestUserAccounts(self):
        self.assertTrue(len(list(all_test_user_emails_in_production_db())) < MAX_NUMBER_OF_TOLERABLE_TEST_USERS,
                        "There are too many test users in the production database. A clean up is necessary.")

###############
# Main Runner #
###############

if __name__ == '__main__':
    print("This module contains a sweep test to ensure that the production DB used for https://github.com/paul-tqh-nguyen/swing_dance_scores/ contains few automatically generated test users.")
