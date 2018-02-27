import secrets
from slackclient import SlackClient

slack_token = secrets.SLACK_BOT_TOKEN
sc = SlackClient(slack_token)



#print user_list['members'][0]

class statusBot():
    def __init__(self):
        self.status_list()
        #self.set_status('jasonsole','remote test',':house_with_garden:')
    
    def set_status(self,username,status,emoji):
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
        print test
        """
            profile=slack_user_id,
            status_text=status,
            status_emoji=emoji
        """
        
    def status_list(self):
        remote_list = []
        pto_list = []
        other_status = []
        user_list = sc.api_call(
            "users.list",
            presence="true"
        )
        for user in user_list['members']:
            #print "%s - %s" % (user['profile']['real_name'],user['profile']['status_text'])
            if user['profile']['status_text'] == "Working remotely":
                remote_list.append(user['profile']['real_name'])
            elif user['profile']['status_text'] == "PTO":
                pto_list.append(user['profile']['real_name'])
            else:
                if user['profile']['status_text'] != "":
                    other_status.append(
                        [user['profile']['real_name'],
                        user['profile']['status_text']]
                        )
        
        msg = ""
        msg += "People working remote today:\n"
        for remote in remote_list:
            msg += "    %s\n" % remote
        
        msg += "\nPeople on PTO today:\n"
        for pto in pto_list:
            msg += "    %s\n" % pto
        
        msg += "\nOther statuses:\n"
        for status in other_status:
            msg += "    %s - %s\n" % (status[0],status[1])
            
        sc.api_call(
          "chat.postMessage",
          channel="#open-test",
          text=msg
        )
    
