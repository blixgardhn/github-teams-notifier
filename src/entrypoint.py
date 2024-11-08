import os
import requests
import json 

from teams_publisher import TeamsPublisher


def prepare_event_data_and_call_notifier():
    # Full repo name
    full_repo_name = os.getenv("GITHUB_REPOSITORY")

    # Load the pull request event data from the GitHub event payload file
    event_path = os.getenv("GITHUB_EVENT_PATH")
    
    with open(event_path, 'r') as f:
        event_data = json.load(f)

    http_response_status_code = 0
    if "pull_request" in event_data.keys():
        # Retrieve the webhook URL from the environment variable
        webhook_url_pr = os.getenv("WEBHOOK_URL_PR")
        teams_publisher_pr = TeamsPublisher(webhook_url_pr)

        # Prepare the payload to send to the webhook
        data = {
            "action_title:": 'Vis pull request',
            "event_number": event_data["number"],
            "event": event_data.get("pull_request", {}),
            "repo": full_repo_name.split('/', 2)[1]
        }
        
        http_response_status_code = teams_publisher_pr.send_notification(data)
    else:
        print(f'Unknown event inside event_data. Not in list [pull_request]')
        
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
