import requests
import json

# Replace 'YOUR_API_TOKEN' with your actual PagerDuty API token
api_token = 'YOUR_API_TOKEN'
# Replace 'YOUR_SERVICE_ID' with the actual service ID where the incidents should be created
service_id = 'YOUR_SERVICE_ID'
# Replace 'MESSAGE' with the actual incident message
message_copy = 'MESSAGE'

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Token token={api_token}'
}

# Replace with your PagerDuty members API endpoint
members_endpoint = 'https://api.pagerduty.com/users'
# Replace with your PagerDuty incidents API endpoint
incidents_endpoint = 'https://api.pagerduty.com/incidents'


def get_pagerduty_members():
    response = requests.get(members_endpoint, headers=headers)
    if response.status_code == 200:
        return response.json()['users']
    else:
        print(f"Failed to retrieve PagerDuty members. Status code: {response.status_code}, Error: {response.text}")
        return None

def create_incident_for_member(member_id, service_id, summary):
    payload = {
        'incident': {
            'type': 'incident',
            'title': summary,
            'service': {
                'id': service_id,
                'type': 'service_reference'
            },
            'assignments': [
                {
                    'assignee': {
                        'id': member_id,
                        'type': 'user_reference'
                    }
                }
            ]
        }
    }

    response = requests.post(incidents_endpoint, headers=headers, data=json.dumps(payload))

    if response.status_code == 201:
        print(f"Incident created successfully for member {member_id}. Incident ID: {response.json()['incident']['id']}")
    else:
        print(f"Failed to create incident for member {member_id}. Status code: {response.status_code}, Error: {response.text}")

# Example usage
members = get_pagerduty_members()
print(members)
# if members:
#     for member in members:
#         create_incident_for_member(member['id'], service_id, message_copy)
