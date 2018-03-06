#!/usr/bin/env python

import cgi;
import cgitb;cgitb.enable()

print "Content-type: application/json"
print ""

import secrets
from slackclient import SlackClient
import os, sys
import requests
import urllib

slack_token = secrets.SLACK_BOT_TOKEN
sc = SlackClient(slack_token)


class statusBot():
    def __init__(self):
        self.query_params = self.parseQS()
        self.status_list()

    def status_list(self):
        '''
        Retrives the user list and assigns each user to a bucket based on their status. Using
        the post response_url, it then posts a message back to slack with the buckets.
        If a user's status is blank, it gets ignored.

        TODO:
        - Request a specific bucket
        - Broadcast to entire channel
        - only list users of the given channel 

        '''
        remote_list = []
        sick_list = []
        pto_list = []
        other_status = []
        # read post variables so that we can post pack to the correct channel.
        qs=sys.stdin.read()
        nvps = self.parseQS(qs)
        try:
            flags = nvps['text']
        except KeyError:
            flags = ""
            
        user_list = sc.api_call(
            "users.list",
            presence="true"
        )

        # look at each user status and assign that user to a bucket based on the value
        for user in user_list['members']:
            if "remote" in user['profile']['status_text'].lower():
                remote_list.append(user['profile']['real_name'])
            elif "pto" in user['profile']['status_text'].lower():
                pto_list.append(user['profile']['real_name'])
            elif "sick" in user['profile']['status_text'].lower():
                sick_list.append(user['profile']['real_name'])
            else:   
                # Prevent failure if people people wierd stuff in the status.
                try:
                    if user['profile']['status_text'] != "":
                        other_status.append(
                            [urllib.quote(user['profile']['real_name']),
                            urllib.quote(user['profile']['status_text']),
                            urllib.quote(user['profile']['status_emoji'])]
                            )
                except:
                    pass

        #build the response message        
        msg = ""
        msg += ":house_with_garden: *People working remote today:*\n"
        for remote in remote_list:
            msg += "    %s\n" % remote

        msg += "\n:palm_tree: *People on PTO today:*\n"
        for pto in pto_list:
            msg += "    %s\n" % pto

        msg += "\n*:face_with_thermometer: People out sick today:*\n"
        for pto in sick_list:
            msg += "    %s\n" % pto
        
        if flags != "simple":
            msg += "\n*Other statuses: *\n"
            for status in other_status:
                msg += "    %s %s - %s\n" % (status[2],status[0],status[1])

        the_url = nvps['response_url']
        webhook_url = urllib.unquote(the_url)

        # write the json paylod. Set to "ephemeral" so only requester gets a response
        the_json = '{"response_type":"ephemeral","text":"%s"}' % urllib.unquote(msg)

        # post  amessage back to channel where it was requested
        requests.post(url=webhook_url, data=the_json)


    def parseQS(self,qs=False):
        '''
        Given a query string (qs), parse it and return it as a dict.

        '''
        if qs==False:
            qs = os.environ['QUERY_STRING']
        nvps = {}
        if qs:
             qs_array = qs.split("&")
             nvdict = {}
             for qsa in qs_array:
                 pairs = qsa.split("=")
                 nvps[pairs[0]]=pairs[1]
        else: #if all else fails, post back to general
            nvps['channel']='general'
        return nvps
        
    def set_status(self,username,status,emoji):
        '''
        prototype code. sets requesting user's status.
        '''
        user_list = sc.api_call(
            "users.list"
        )
        slack_user_id = ""
        for user in user_list['members']:
            if user['name']==username:
                slack_user_id=user["id"]
        #print slack_user_id
        slack_user = sc.api_call(
            "users.info",
            user=slack_user_id
            )
        test = sc.api_call(
            "users.profile.set",
            profile='{"status_text": "Working remotely","status_emoji": ":house_with_garden:"}'
            )
        #print slack_user
        #print test
        """
            profile=slack_user_id,
            status_text=status,
            status_emoji=emoji
        """
statusBot()

    
