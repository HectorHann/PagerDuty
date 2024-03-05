import requests
import json
import time
import os
import Constant
from dotenv import load_dotenv
load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
print(f"API Token: {API_TOKEN}")
headers = {
    'Authorization': f'Token {API_TOKEN}',
    'Content-Type': 'application/json',
}


def update_pagerduty_user(target_user):
    current_user = get_current_user(target_user)
    user_pool = target_user['user_pool']
    next_user_info = user_pool[0]
    for i, user_info in enumerate(user_pool):
        email = user_info.get('email')
        if email == current_user['user']['email']:
            next_index = (i + 1) % len(user_pool)
            next_user_info = user_pool[next_index]
            break

    print(f"Current user: {current_user['user']['email']}")
    print(f"Next user: {next_user_info}")
    update_user(target_user, next_user_info)
    update_contact(target_user, next_user_info)


def get_current_user(target_user):
    user_url = f'https://api.pagerduty.com/users/{target_user["user_id"]}'
    response = requests.get(user_url, headers=headers)

    if response.status_code != 200:
        handle_error(response)
        return None

    user_data = response.json()
    return user_data


def update_user(target_user, user_info):
    user_url = f'https://api.pagerduty.com/users/{target_user["user_id"]}'

    response = requests.get(user_url, headers=headers)

    if response.status_code != 200:
        handle_error(response)
        return

    user_data = response.json()
    user_data['user']['name'] = target_user['user_name_prefix'] + user_info['name']
    user_data['user']['email'] = user_info['email']

    # 更新用户信息
    update_response = requests.put(user_url, headers=headers, data=json.dumps(user_data))

    if update_response.status_code != 200:
        handle_error(update_response)

    print(f"User {user_info} updated successfully.")


def update_contact(target_user, user_info):
    email_contact_url = f'https://api.pagerduty.com/users/{target_user["user_id"]}/contact_methods/{target_user["email_contact_id"]}'
    phone_contact_url = f'https://api.pagerduty.com/users/{target_user["user_id"]}/contact_methods/{target_user["phone_contact_id"]}'
    sms_contact_url = f'https://api.pagerduty.com/users/{target_user["user_id"]}/contact_methods/{target_user["sms_contact_id"]}'

    update_contact_method(email_contact_url, user_info['email'])
    update_contact_method(phone_contact_url, user_info['phone'])
    update_contact_method(sms_contact_url, user_info['phone'])

    print(f"Contact for user {target_user['user_id']} updated successfully.")


def update_contact_method(url, new_address):
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        handle_error(response)
        return

    contact_data = response.json()
    contact_data['contact_method']['address'] = new_address

    update_response = requests.put(url, headers=headers, data=json.dumps(contact_data))
    
    if update_response.status_code != 200:
        handle_error(update_response)


def handle_error(response):
    print(f"Error: {response.status_code}")
    print(f"Unhandled error. {response.text}")


update_pagerduty_user(Constant.target_user_primary_oncall)
