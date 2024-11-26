import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import requests
import json

from jinja2 import Environment, FileSystemLoader

DEBUG = os.getenv("DEBUG", False)

class TeamsPublisher:
    def __init__(self, webhook_url:str):
        self.webhook_url = webhook_url
        self.ad_user_mappings = json.loads(os.getenv("AD_USER_MAPPINGS", "[]"))


    def send_notification(self, data):
        """
        Send a notification to the webhook URL about a new event
        """
        if DEBUG: print("Inside TeamsPublisher.send_notification()")
        if DEBUG: print(data.keys())
        if DEBUG: print(data)

        template_path = template_path = os.path.join(os.path.dirname(__file__), "templates")
        template_file = 'adaptive_card_template.json.j2'        
        env = Environment(loader=FileSystemLoader(template_path))
        template = env.get_template(template_file)
 
        if DEBUG: print(data.get("mention_users"))

        ev = data["event"]
        mentions=self.get_mentions(data.get("mention_users", []))
        if len(mentions) > 0:
            mentions_names = ", ".join(mention.get("text", "") for mention in mentions)
        else:
            mentions_names = ""

        if DEBUG: print(mentions_names)

        body = ev.get("body", None) or "Ingen beskrivelse"
        if DEBUG: print(body)
        body_post = data.get("body_post", None) or ""
        if DEBUG: print(body_post)

        if DEBUG: print(body)

        adaptive_card_message = template.render(
            card_title=json.dumps(f'{ data.get("event_type_name")} - { data.get("repo") }'),
            body_title=json.dumps(ev.get("title")),
            body=json.dumps(f'{body} {body_post}'),
            action_title=json.dumps(f'{ data.get("action_title")}'),
            action_url=ev['html_url'],
            user_login=ev['user']['login'],
            user_url=ev['user']['html_url'],
            user_avatar_url=ev['user']['avatar_url'],
            mentions=json.dumps(mentions),
            mentions_names = mentions_names,
            created_at=datetime.strptime(ev['created_at'], '%Y-%m-%dT%H:%M:%SZ').astimezone(ZoneInfo("Europe/Oslo")).strftime('%Y-%m-%dT%H:%M:%SZ'),
            updated_at=datetime.strptime(ev['updated_at'], '%Y-%m-%dT%H:%M:%SZ').astimezone(ZoneInfo("Europe/Oslo")).strftime('%Y-%m-%dT%H:%M:%SZ')
        )

        try:
            adaptive_card_message = json.loads(adaptive_card_message)
        except Exception as e:
            print(f"Failed to serialize data {data} with message: \n{adaptive_card_message} \nAnd exception: {e}")

        return self.send_to_webhook(adaptive_card_message)
    

    def get_mentions(self, user_list):
        mentions = []
        for usr in user_list:
            print(f'reviewer: {usr}')
            usr['name'] = usr['login']
            if len(self.ad_user_mappings) == 0:
                usr = usr
            else:
                for user in self.ad_user_mappings:
                    if user['github_login'] == usr['login']:
                        usr['login'] = user['ad_login']
                        usr['id'] = user['id']
                        usr['name'] = user['name']
                        break
                        

            mentions.append({
                "type": "mention",
                "text": f"<at>{usr['login']}</at>",
                "mentioned": {
                    "id": usr['id'],
                    "name": usr['name']
                }
            })
        
        print(f'Returning mentions like so: {mentions}')
        return mentions


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