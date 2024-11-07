import os
import requests
import json 

from teams_publisher import TeamsPublisher


def prepare_event_data_and_call_notifier():
    # Retrieve the webhook URL from the environment variable
    webhook_url = os.getenv("WEBHOOK_URL")

    # Load the pull request event data from the GitHub event payload file
    event_path = os.getenv("GITHUB_EVENT_PATH")
    with open(event_path, 'r') as f:
        event_data = json.load(f)

    teams_publisher = TeamsPublisher(webhook_url)

    http_response_status_code = 0

    if "pull_request" in event_data.keys():

        # Prepare the payload to send to the webhook
        data = {
            "pr_number": event_data["number"],
            "pr_title": event_data["pull_request"]["title"],
            "pr_body": event_data["pull_request"]["body"],
            "pr_user": event_data["pull_request"]["user"]["login"],
            "pr_url": event_data["pull_request"]["html_url"]
        }
        
        http_response_status_code = teams_publisher.send_pull_request_notification(data)
        
    # Write output to the GitHub environment file for other workflow steps
    write_output_response_code(http_response_status_code)
    return http_response_status_code


def write_output_response_code(output_string:str):
    with open(os.getenv("GITHUB_OUTPUT"), "a") as output_file:
        output_file.write(f"response_code={output_string}\n")


def main():
    prepare_event_data_and_call_notifier()

if __name__ == "__main__":
    main()
