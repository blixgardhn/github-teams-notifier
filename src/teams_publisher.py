import os
import datetime
import requests

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
        print(env)
        template = env.get_template(template_file)
 

        data = {
            "pr_number": event_data["number"],
            "pr": event_data["pull_request"],
            "pr_title": event_data["pull_request"]["title"],
            "pr_body": event_data["pull_request"]["body"],
            "pr_user": event_data["pull_request"]["user"]["login"],
            "pr_url": event_data["pull_request"]["html_url"]
        }

        pr = data["pr"]
        adaptive_card_message = template.render(
            repo_name=pr['repo'].split('/', 2)[1],
            pr_title=pr['title'],
            pr_body=pr['body'] or "No description provided.",
            pr_url=pr['html_url'],
            user_login=pr['user']['login'],
            user_url=pr['user']['html_url'],
            user_avatar_url=pr['user']['avatar_url'],
            created_at=datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'), #pr.created_at.astimezone(ZoneInfo("Europe/Oslo")).strftime('%Y-%m-%dT%H:%M:%SZ'),
            updated_at=datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') #pr.updated_at.astimezone(ZoneInfo("Europe/Oslo")).strftime('%Y-%m-%dT%H:%M:%SZ')
        )

        try:
            adaptive_card_message = json.loads(adaptive_card_message)
        except Exception as e:
            print(f"Failed to serialize pull request {pr.title} in {repo_name} with message: \n{adaptive_card_message} \nAnd exception: {e}")

        pr_data = {'text': 'Text for teams from Github Action'}
        return self.send_to_webhook(pr_data)
    
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