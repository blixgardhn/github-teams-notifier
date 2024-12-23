# github-teams-notifier
A Github Action that listens to events and sends notifications to teams

### Mapping Github usernames to Teams usernames
An environment variable containing json on the following format must be provided for users that require a mapping from the Github user to the Teams user.


```json
[
   {"github_login": "blixgardhn", "ad_login": "blixgardhn_ad", "name": "Blixgard HN", "id": "blixgardhn_ad@seriousworkmail.com"},
   {"github_login": "goodergitter", "ad_login": "goodgitter_ad", "name": "Good R. Gitter", "id": "gooder@gitter.com"}
]
```

### Content within \<details>-tag ignored
Content in the body text that is enclosed in the \<details>-tag will not be displayed in the Teams message.

