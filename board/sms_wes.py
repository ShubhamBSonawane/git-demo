#!/usr/bin/env python3

# Importing required modules
import json
import requests
from config import *


# this code is edited by shubham. Basically it will ping the WES server running on the raspberry pi.
# function to check WES server on Raspberry Pi.
def ping_wes_server():
    port = ":3000"
    route = "/api/v1//ping"
    try:
        response = requests.get(URL + port + route)
    except requests.exceptions.ConnectionError:
        return False
    return response.text
# End of the Edit.


def set_network_params(iface, loss, delay, jitter, rate, direction="outgoing", corrupt="0%", duplicate="0%"):
    api_url = URL + ":3000" + "/api/v1/setNetworkParams/" + iface
    headers = {"Content-Type": "application/json"}
    params = json.dumps({"direction": direction,
                         "delay": delay,
                         "loss": loss,
                         "corrupt": corrupt,
                         "duplicate": duplicate,
                         "jitter": jitter,
                         "rate": rate})
    try:
        ret_val = requests.post(api_url, data=params, headers=headers).json()
    except requests.exceptions.ConnectionError:
        return False
    json_dump = json.dumps(ret_val)
    json_load = json.loads(json_dump)
    # print(json_load['status'])
    return json_load['status']


def get_network_params(iface):
    api_url = URL + ":3000" + "/api/v1/getNetworkParams/" + iface
    headers = {"Content-Type": "application/json"}
    try:
        ret_val = requests.get(api_url, headers=headers).json()
    except requests.exceptions.ConnectionError:
        return False
    json_dump = json.dumps(ret_val)
    json_load = json.loads(json_dump)
    # print(json_load)
    return json_load['status']


def reset_network_params(iface):
    api_url = URL + ":3000" + "/api/v1/resetNetworkParams/" + iface
    headers = {"Content-Type": "application/json"}
    try:
        ret_val = requests.get(api_url, headers=headers).json()
    except requests.exceptions.ConnectionError:
        return False
    json_dump = json.dumps(ret_val)
    json_load = json.loads(json_dump)
    # print(json_load['status'])
    return json_load['status']


# set_network_params("eth0", "0%", "1000ms", "100Mbps", "0ms")
# get_network_params("eth0")
# reset_network_params("eth0")
