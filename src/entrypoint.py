import os
import requests
import json 

from teams_publisher import TeamsPublisher

DEBUG = os.getenv("DEBUG", False)

def prepare_event_data_and_call_notifier():
    # Full repo name
    full_repo_name = os.getenv("GITHUB_REPOSITORY")

    # Load the pull request event data from the GitHub event payload file
    event_path = os.getenv("GITHUB_EVENT_PATH")
    
    with open(event_path, 'r') as f:
        event_data = json.load(f)

    http_response_status_code = 0

    if DEBUG: print(event_data)
    if DEBUG: print(event_data.keys())
    if DEBUG: print(event_data.get("event", {}).keys())


    if "review" in event_data.keys():
        # Retrieve the webhook URL from the environment variable
        webhook_url_pr = os.getenv("WEBHOOK_URL_PR")
        teams_publisher_pr = TeamsPublisher(webhook_url_pr)
        
        # Prepare the payload to send to the webhook
        review = event_data.get("review")
        pull_request = event_data.get("pull_request")
        data = {
            "event_type_name": f'PR {review.get("state", "unset")}',
            "action_title": 'Gå til pull request',
            "event": pull_request,
            "repo": full_repo_name.split('/', 2)[1],
            "body_post": f'\nReviewer: {review.get("user").get("login")}',
            "mention_users": [pull_request.get("user")]
        }
        http_response_status_code = teams_publisher_pr.send_notification(data)

    elif "pull_request" in event_data.keys():
        # Retrieve the webhook URL from the environment variable
        webhook_url_pr = os.getenv("WEBHOOK_URL_PR")
        teams_publisher_pr = TeamsPublisher(webhook_url_pr)

        # Prepare the payload to send to the webhook
        pull_request = event_data.get("pull_request"),
        data = {
            "event_type_name": "Pull request",
            "action_title": 'Gå til pull request',
            "event": pull_request,
            "repo": full_repo_name.split('/', 2)[1],
            "mention_users": pull_request.get('requested_reviewers', [])
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
