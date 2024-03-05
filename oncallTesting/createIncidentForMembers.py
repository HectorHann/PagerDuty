import requests
import json
import Constant

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Token token={Constant.API_TOKEN}'
}

# Replace with your PagerDuty members API endpoint
members_endpoint = 'https://api.pagerduty.com/users'
# Replace with your PagerDuty incidents API endpoint
incidents_endpoint = 'https://api.pagerduty.com/incidents'


def get_pagerduty_members():
    params = {'offset': 0, 'limit': 100}
    response = requests.get(members_endpoint, headers=headers, params=params)
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
        print(
            f"Failed to create incident for member {member_id}. Status code: {response.status_code}, Error: {response.text}")


# Example usage
members = get_pagerduty_members()
print("Original Size: " + str(len(members)))
# Exclude the US oncall members
if members:
    # Create a new list excluding members with specific IDs
    members = [member for member in members if member['id'] not in Constant.US_ONCALL]
print("Final Size: " + str(len(members)))

# Start create incidents for each member
print(">>>>>>>>>>>>>>>>> Start the PagerDuty Test Work >>>>>>>>>>>>>>>>>")
if members:
    for member in members:
        print(member['id'] + '\t' + member['name'])
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # create_incident_for_member(member['id'], Constant.SERVICE_ID, Constant.INCIDENT_TITLE + member['name'])
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

print("<<<<<<<<<<<<<<<<< PagerDuty Test Work Finished <<<<<<<<<<<<<<<<<")
print("Notify Size: " + str(len(members)))
