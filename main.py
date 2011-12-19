# -*- coding: utf-8 -*-

""" Script based on libturpial to handle bot account in Twitter to adopt
puppies in Venezuela """
#
# Authors: Wil Alvarez (aka satanas), Carlos Guerrero (aka guerrerocarlos)
# Dic 16, 2011

# Setup the Django environment
import os
import sys
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from adoptave.webui.models import Tweet

import time
import logging

from optparse import OptionParser

from libturpial.api.core import Core
from libturpial.common import ColumnType

POLLING_TIME = 5 #min
ACCOUNT = 'AdoptaVe-twitter'
MAX_FOLLOW = 3

class Adopta:
    def __init__(self):
        parser = OptionParser()
        parser.add_option('-d', '--debug', dest='debug', action='store_true',
            help='show debug info in shell during execution', default=False)
        
        (options, args) = parser.parse_args()
        
        if options.debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        
        self.core = Core()
        self.followers = []
        self.following = []
        self.last_dm = None
        self.log = logging.getLogger('Server')
        self.start_login()
    
    def start_login(self):
        self.core.register_account(ACCOUNT.split('-')[0], ACCOUNT.split('-')[1], '')
        response = self.core.login(ACCOUNT)
        if response.code > 0:
            print "Login error:", response.errmsg
            return
        
        auth_obj = response.items
        if auth_obj.must_auth():
            print "Please visit %s, authorize Turpial and type the pin returned" % auth_obj.url
            pin = self.user_input('Pin: ')
            self.core.authorize_oauth_token(ACCOUNT, pin)
        
        rtn = self.core.auth(ACCOUNT)
        if rtn.code > 0:
            print rtn.errmsg
        else:
            self.log.debug('Logged in with account %s' % ACCOUNT.split('-')[0])
            self.main()
        
    def user_input(self, message, blank=False):
        while 1:
            text = raw_input(message)
            if text == '' and not blank:
                print "You can't leave this field blank"
                continue
            break
        return text
    
    def get_followers(self):
        response = self.core.get_followers(ACCOUNT, True)
        if response.code > 0:
            self.log.error("Error getting followers list:", response.errmsg)
        else:
            self.followers = response.items
    
    def get_following(self):
        response = self.core.get_following(ACCOUNT, True)
        if response.code > 0:
            self.log.error("Error getting following list:", response.errmsg)
        else:
            self.following = response.items
    
    def process_follow_back(self):
        temp = []
        for item in self.followers:
            if item not in self.following:
                if len(temp) < MAX_FOLLOW:
                    temp.append(item)
                else:
                    break
        
        for item in temp:
            response = self.core.follow(ACCOUNT, str(item), by_id=True)
            if response.code > 0:
                self.log.error("Error following to %s: %s" % (item, response.errmsg))
            else:
                self.log.debug("Follow back to %s" % item)
                self.following.append(item)
    
    def process_dms(self):
        response = self.core.get_column_statuses(ACCOUNT, ColumnType.DIRECTS, 200)
        if response.code > 0:
            self.log.error("Error fetching DMs: %s" % response.errmsg)
        else:
            for dm in response.items:
                msg_id = dm.id_
                valid = self.validate_dm(dm)
                if not valid:
                    continue
                
                via = ' (via @%s)' % dm.username
                text = dm.text
                length = len(text) + len(via)
                if length > 140:
                    text = text[:len(text) - len(via)]
                message = text + via
                message.encode('utf-8')
                rtn = self.core.update_status(ACCOUNT, message)
                if rtn.code > 0:
                    self.log.error("Error posting message '%s': %s" % (message, rtn.errmsg))
                else:
                    self.register_message(dm)
    
    def validate_dm(self, dm):
        # TODO: Search in database for msg_id, if exist then return False
        # otherwiser return True
        if len(Tweet.objects.filter(status_id=dm.id_)) > 0:
            return False 
        else:
            return True
    
    def register_message(self, dm):
        # TODO: Add dm to database
        t = Tweet(status_id=dm.id_,username=dm.username,content=dm.text)
        t.save()
        pass
    
    def main(self):
        while True:
            try:
                # Processing followbacks
                self.get_followers()
                self.get_following()
                self.process_follow_back()
                
                # Processing DMs
                self.process_dms()
                time.sleep(POLLING_TIME * 60)
                
            except KeyboardInterrupt:
                break
        self.log.debug('Bye')

if __name__ == "__main__":
    adopta = Adopta()
