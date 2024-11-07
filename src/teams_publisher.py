import os
import requests


class TeamsPublisher:
    def __init__(self, webhook_url:str):
        self.webhook_url = webhook_url

    def send_pull_request_notification(self, data):
        return self.send_to_webhook(data)
    
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