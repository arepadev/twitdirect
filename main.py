# -*- coding: utf-8 -*-

""" Script based on libturpial to handle bot account in Twitter to adopt
puppies in Venezuela """
#
# Author: Wil Alvarez (aka Satanas)
# Dic 16, 2011

import time
import logging

from optparse import OptionParser

from libturpial.api.core import Core

POLLING_TIME = 5 #min
ACCOUNT = 'AdoptaVe-twitter'

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
        response = self.core.get_followers(ACCOUNT)
        if response.code > 0:
            self.log.error("Error getting followers list:", response.errmsg)
        else:
            self.followers = response.items
    
    def get_following(self):
        response = self.core.get_following(ACCOUNT)
        if response.code > 0:
            self.log.error("Error getting following list:", response.errmsg)
        else:
            self.following = response.items
    
    def process_follow_back(self):
        for item in self.followers:
            if item not in self.following:
                response = self.core.follow(ACCOUNT, str(item), by_id=True)
                if response.code > 0:
                    self.log.error("Error following to %i" % item)
                else:
                    self.log.debug("Follow back to %i" % item)
                    self.following.append(item)
        
    def main(self):
        while True:
            try:
                # Processing followbacks
                self.get_followers()
                self.get_following()
                self.process_follow_back()
                
                # Processing DMs
                
                time.sleep(POLLING_TIME * 60)
                
            except KeyboardInterrupt:
                break
        self.log.debug('Bye')

if __name__ == "__main__":
    adopta = Adopta()
