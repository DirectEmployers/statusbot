#!/usr/bin/env python2.7

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
sc = SlackClient(token=slack_token,ssl=True)


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

        # get the user list
        user_list = sc.api_call("users.list")

        # look at each user status and assign that user to a bucket based on the value
        for user in user_list['members']:
            if (
                "remote" in user['profile']['status_text'].lower() or
                "wfh" in user['profile']['status_text'].lower()
                ):
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
                            urllib.quote(user['profile']['status_text'].encode('utf8')),
                            urllib.quote(user['profile']['status_emoji'])]
                            )
                except:
                    pass

        #build the response message
        msg = ""
        if (
            flags == "" or
            "remote" in flags or
            "simple" in flags or
            "wfh" in flags
            ):
            msg += ":house_with_garden: *People working remote today:*\n"
            for remote in remote_list:
                msg += "    %s\n" % remote

        if flags == "" or "pto" in flags or "simple" in flags:
            msg += "\n:palm_tree: *People on PTO today:*\n"
            for pto in pto_list:
                msg += "    %s\n" % pto

        if flags == "" or "sick" in flags or "simple" in flags:
            msg += "\n*:face_with_thermometer: People out sick today:*\n"
            for pto in sick_list:
                msg += "    %s\n" % pto

        if (flags == "" or "other" in flags) and "simple" not in flags:
            msg += "\n*Other statuses: *\n"
            for status in other_status:
                user_name = status[0]
                user_status = status[1]
                user_emoji = status[2]
                msg = msg.encode('utf8')
                msg += "    %s %s - %s\n" % (user_emoji,user_name,user_status)

        the_url = nvps['response_url']
        webhook_url = urllib.parse.unquote(the_url)

        # write the json paylod. Set to "ephemeral" so only requester gets a response
        msg = urllib.parse.unquote(msg)
        msg = msg.replace('"','\\"') #quotes break the json
        the_json = '{"response_type":"ephemeral","text":"%s"}' % msg

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
