import requests
from datetime import datetime, timedelta
import Constant

# Replace with your PagerDuty incidents API endpoint
incidents_endpoint = 'https://api.pagerduty.com/incidents'
past_hours = 24

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Token {Constant.API_TOKEN}'
}

def get_pagerduty_incidents():
    all_incidents = []
    # Calculate the start date and time for the past 24 hours
    since_time = datetime.utcnow() - timedelta(hours=past_hours)
    since_time_str = since_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Define the parameters for the API request
    params = {'since': since_time_str, 'service_ids[]': Constant.SERVICE_ID}
    response = requests.get(incidents_endpoint, headers=headers, params=params)

    if response.status_code == 200:
        incidents_data = response.json()['incidents']
        all_incidents.extend(incidents_data)
    else:
        print(f"Failed to retrieve PagerDuty incidents. Status code: {response.status_code}, Error: {response.text}")
        return None

    return all_incidents

# Get the recent incidents list
recent_incidents = get_pagerduty_incidents()

if recent_incidents:
    for incident in recent_incidents:
        incident_id = incident['id']
        incident_summary = incident['summary']

        # Function to get ACK duration for an incident
        def get_pagerduty_incident_ack_duration(incident_id):
            log_entries_endpoint = f'https://api.pagerduty.com/incidents/{incident_id}/log_entries'
            response = requests.get(log_entries_endpoint, headers=headers)

            if response.status_code == 200:
                log_entries = response.json()['log_entries']

                if log_entries:
                    sorted_log_entries = sorted(log_entries, key=lambda entry: entry['created_at'])

                    ack_timestamp = None
                    created_timestamp = None

                    for log_entry in sorted_log_entries:
                        if log_entry['type'] == 'acknowledge_log_entry':
                            ack_timestamp = datetime.strptime(log_entry['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                            break

                        if log_entry['type'] == 'trigger_log_entry':
                            created_timestamp = datetime.strptime(log_entry['created_at'], "%Y-%m-%dT%H:%M:%SZ")

                    if ack_timestamp and created_timestamp:
                        ack_duration = ack_timestamp - created_timestamp
                        print(f"Incident:{incident_summary} \tACK Duration: {int(ack_duration.total_seconds() / 60)} min(s)")
                    else:
                        print(f"Incident:{incident_summary} \tNo ACK")
                else:
                    print(f"Incident:{incident_summary} \tNo Logs")
            else:
                print(f"Failed to retrieve log entries for the incident. Status code: {response.status_code}, Error: {response.text}")

        # Get ACK duration for the incident
        get_pagerduty_incident_ack_duration(incident_id)
else:
    print("Recent incidents list is empty.")
