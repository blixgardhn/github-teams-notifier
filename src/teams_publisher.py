import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import requests
import json

from jinja2 import Environment, FileSystemLoader


class TeamsPublisher:
    def __init__(self, webhook_url:str):
        self.webhook_url = webhook_url

    def send_pull_request_notification(self, data):
        """
        Send a notification to the webhook URL about a new pull request.
        """
        template_path = template_path = os.path.join(os.path.dirname(__file__), "templates")
        template_file = 'adaptive_card_template.json.j2'        
        env = Environment(loader=FileSystemLoader(template_path))
        template = env.get_template(template_file)
 
        pr = data["pr"]
        adaptive_card_message = template.render(
            repo_name=data['repo'],
            card_preview=f'Pull request - {{ repo_name }}',
            body_title=f'Pull request - {{ repo_name }}',
            body=pr['body'] or "No description provided.",
            action_title='View Pull Request',
            action_url=pr['html_url'],
            user_login=pr['user']['login'],
            user_url=pr['user']['html_url'],
            user_avatar_url=pr['user']['avatar_url'],
            created_at=datetime.strptime(pr['created_at'], '%Y-%m-%dT%H:%M:%SZ').astimezone(ZoneInfo("Europe/Oslo")).strftime('%Y-%m-%dT%H:%M:%SZ'),
            updated_at=datetime.strptime(pr['updated_at'], '%Y-%m-%dT%H:%M:%SZ').astimezone(ZoneInfo("Europe/Oslo")).strftime('%Y-%m-%dT%H:%M:%SZ')
        )

        try:
            adaptive_card_message = json.loads(adaptive_card_message)
        except Exception as e:
            print(f"Failed to serialize pull request {pr.get('title')} in {data.get('repo')} with message: \n{adaptive_card_message} \nAnd exception: {e}")

        # pr_data = {'text': 'Text for teams from Github Action'}
        return self.send_to_webhook(adaptive_card_message)
    
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