import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import requests
import json

from jinja2 import Environment, FileSystemLoader


class TeamsPublisher:
    def __init__(self, webhook_url:str):
        self.webhook_url = webhook_url
        self.ad_user_mappings = json.loads(os.getenv("AD_USER_MAPPINGS", "[]"))


    def send_notification(self, data):
        """
        Send a notification to the webhook URL about a new event
        """
        template_path = template_path = os.path.join(os.path.dirname(__file__), "templates")
        template_file = 'adaptive_card_template.json.j2'        
        env = Environment(loader=FileSystemLoader(template_path))
        template = env.get_template(template_file)

 
        ev = data["event"]
        adaptive_card_message = template.render(
            repo_name=data['repo'],
            card_title=f'Pull request - { data.get("repo") }',
            body_title=ev.get("title"),
            body=ev['body'] or "Ingen beskrivelse gitt.",
            action_title=f'{data.get("action_title")}',
            action_url=ev['html_url'],
            user_login=ev['user']['login'],
            user_url=ev['user']['html_url'],
            user_avatar_url=ev['user']['avatar_url'],
            mentions=self.get_mentions(data),
            created_at=datetime.strptime(ev['created_at'], '%Y-%m-%dT%H:%M:%SZ').astimezone(ZoneInfo("Europe/Oslo")).strftime('%Y-%m-%dT%H:%M:%SZ'),
            updated_at=datetime.strptime(ev['updated_at'], '%Y-%m-%dT%H:%M:%SZ').astimezone(ZoneInfo("Europe/Oslo")).strftime('%Y-%m-%dT%H:%M:%SZ')
        )

        try:
            adaptive_card_message = json.loads(adaptive_card_message)
        except Exception as e:
            print(f"Failed to serialize data {data} with message: \n{adaptive_card_message} \nAnd exception: {e}")

        return self.send_to_webhook(adaptive_card_message)
    

    def get_mentions(self, data):
        mentions = []
        if 'requested_reviewers' in data.keys():
            for rev in data['requested_reviewers']:
                rev['name'] = rev['login']
                if len(self.ad_user_mappings) == 0:
                    usr = rev
                else:
                    for user in self.ad_user_mappings:
                        if user['github_login'] == rev['login']:
                            rev['login'] = user['login']
                            rev['id'] = user['id']
                            rev['name'] = user['name']
                            

                mentions.append({
                    "type": "mention",
                    "text": f"<at>{rev['login']}</at>",
                    "mentioned": {
                        "id": rev['id'],
                        "name": rev['name']
                    }
                })
        return json.dumps(mentions)


    def send_to_webhook(self, payload):
        # Send the request to the webhook
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            print(f"Response from webhook: {response.status_code}")

            return response.status_code

        except requests.exceptions.RequestException as e:
            print(f"Error sending request: {e}")
            exit(1)