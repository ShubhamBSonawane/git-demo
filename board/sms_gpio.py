#!/usr/bin/env python3

# Importing required modules
import json
import time
import requests
import config


# This edited by shubham on 4/9/2020. Function to check relay server on Raspberry pi
def ping_relay_server():
    port = ":5000"
    route = "/ping"
    try:
        response = requests.get(config.URL + port + route)
    except requests.exceptions.ConnectionError:
        return False
    return response.status_code


# End of code.
def set_relay_state(relay, state):
    api_url = config.URL + ":5000" + "/" + relay
    headers = {"Content-Type": "application/json"}
    if state in ('ON', 'on', 'On', 'oN'):
        params = json.dumps({"state": "0"})
    else:
        params = json.dumps({"state": "1"})
    try:
        ret_val = requests.post(api_url, data=params, headers=headers).json()
    except requests.exceptions.ConnectionError:
        return False
    # ret_val = requests.post(api_url, data=params, headers=headers).json()
    json_dump = json.dumps(ret_val)
    json_load = json.loads(json_dump)
    # print(json_load['status'])
    return json_load['status']


def get_relay_status(relay):
    api_url = config.URL + "5000" + "/" + relay
    headers = {"Content-Type": "application/json"}
    try:
        ret_val = requests.get(api_url, headers=headers).json()
    except requests.exceptions.ConnectionError:
        return False
    json_dump = json.dumps(ret_val)
    json_load = json.loads(json_dump)
    # print(json_load)
    if json_load[relay] == 0:
        # print("On")
        return {"state": "On"}
    else:
        # print("Off")
        return {"state": "Off"}


#  code added by shubham on 24-09-2020.
def resetting_sms_board(relay):
    set_relay_state(relay, "off")
    time.sleep(0.5)
    set_relay_state(relay, "on")
    return True


# ret = resetting_sms_board("relay1")
# print(ret)
# ret = set_relay_status("relay1", "off")
# get_relay_status("relay1")
