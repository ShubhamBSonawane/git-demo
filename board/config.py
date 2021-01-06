import sms_bas


# Test framework version.
version = "1.2.0"

# Host:Port config.
URL = "http://192.168.0.62"


# PAS
# Token URL
config_token_url = "https://2vyxr7tv9h.execute-api.eu-west-1.amazonaws.com/qa/tokens"
# Job URL
config_job_url = "https://2vyxr7tv9h.execute-api.eu-west-1.amazonaws.com/qa/registry/jobs/adiu.4e4bca"


# Author Shubham Sonawane, changes made on 29-12-2020
def calculate_hibernate_count():
    res = int(sms_bas.sleep_timer)
    result = res - 4
    result = int(result / 20)
    print(result + 1)
    return result + 1
