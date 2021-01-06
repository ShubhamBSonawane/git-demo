import requests
import json
from config import *


def create_token():
  token_url = config_token_url
  payload = "{\n\t\"name\": \"standard\",\n\t\"tenantId\": \"adiu.4e4bca\",\n\t\"serviceCode\": \"sms\"\n}"
  headers = {
    'Content-Type': 'application/json',
    'Authorization': 'AKT QUsxRDA1MDk2OTdBODI4RDJF.RnhlQWx4N0c2YW8rYUlLVWp0REcvYkdCblVkckdML3kxUDhyOGl5UUxCZWtGTGI3ZEh6LzY4MVBZZzNGYUorMA=='
  }
  response = requests.request("POST", token_url, headers=headers, data = payload).json()
  json_dump = json.dumps(response)
  json_load = json.loads(json_dump)
  with open("token.json", "a+", encoding='utf-8') as f_write:
    json.dump(response, f_write, ensure_ascii=False, indent=4)
    f_write.write("\n\n")
  return json_load


def create_ota_job(device, ota_file):
  service_token = create_token()
  create_job_url = config_job_url
  payload = "{\n\t\"payloadId\": " + "\"" + ota_file + "\"" + ",\n\t\"description\": \"Job description\",\n\t\"targets\" : [ " + "\"" + device + "\"" + " ]\n}"
  headers = {
    'Authorization': service_token['serviceToken'],
    'Content-Type': 'application/json'
  }
  response = requests.request("POST", create_job_url, headers=headers, data = payload).json()
  json_dump = json.dumps(response)
  json_load = json.loads(json_dump)
  with open("job_details.json", "a+") as f_write:
    json.dump(response, f_write, ensure_ascii=False, indent=4)
    f_write.write("\n\n")
  return json_load["jobId","00000894J"]


# create_ota_job("00000478R", "RC2-version-ADSMS-00-v0.9.23_packaged")

