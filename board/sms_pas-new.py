import requests
import json
from config import *
import time


grant_type= 'grant_type=refresh_token'
refresh_token ='refresh_token=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.pXXZieAtnQsN8_P5OAgkYQQ3i0biDOGGzTsl33bTxIMFsTZ-GVrjJcP8JJ5u6VAnm5F9zgor-ZX5FmkIcBfqOXgjiDTJtyM6iiRhGcfm54GZ55td81etGbv7VUjDMlUdb9PQKV47_Y1XEU8sF2HX3TC9vcWndcnwb_q8AWpUZmPARzawFTStRo3uC_fg2mXx0_EK5wHb2t5Api-Pl71Z9kftbigMyYInJu3DEuoOUEk2l9ghGzkTpLwzP8-OtsbqFWMgHtr9wHdjiUFF25b90oPr-buxw4EorY2OPvDBxMMr9deg1l4dUFhBDFNbRpoKjG0huGSsbkGqdoUHPVeg2w.PPhY5Vvnj_-_WkyY.QgnR2xUsqvnJ33yBJHafHcqpVOjEVgOTAV842xd6AIIaVf34hKdLCzJ8uvwMEttbjIN-GNNQ3Z_Lk3RFyLo7CFHy0w0UAw7gnQ2OJ4wLBkdw1RlBv-lPFv1bUGSdIJny_8TdEg4ECqpwGPjgef3GOdC7m2VwDWjrsk5RES4Va5hbkSOc3_wg7Ns03d4L6KuZAc_Veblm_QlhncIJ_JSvLha5U4gCdLzHWi9YUizfyusPJFziOJYE8DArILV0cqanwC7TY-4R4AeTsggiSWiWtTuDHrkY6VU-_mxg1A5kI3vrnJ6IKpscj4uCjI3apuwTXME0pvjr3R5vuKOowWEENFlTMo35KWYSU2gbRyRFRiGr-8799NgoNOlMGO0TesnzbcE2i4AMX7MZPtLQZ6W-bnARVsQn9L-c0ChaUyStRNQYeLUPSSGA3GeQyFbqnvjOdubTOvsPvEi_sc04gJ76bAkiAZvE_1kRu2Gqqo_X0eGl25IYHaFFOOd8cTpolpxSwJwS--BcYesJYJw1kt_tYB3HITDUH5vO7Oz2zJ_-EP04eBqe71Mzp0RSWL1ClKtIgWcSelHfPxfpE9CuUR8xTPP8lwZ9D7OiKjQXbbg0kKxik4LqiGabMOZAAExIT5en5RCFiCJdEpaKJLL_w3b6jtIVgce9VLtz_CZiHHRFYOmscof51AKcjR3F2szCQVMLzQzOvxS1qWlt1IkVW3PCuwrxsdDD2iyqtV-_nxjzkLkWZZFJiBP8sNjx5Ir84nQ-fepcf5-1c2MQu75otz2-qB6F6Y5ytoae0hSfFHqmGghMFfvDaJPRHDhnLf-x0TN-2Ku39hsJ_Mqz-5YGoN7bNUdxYYZFfkF5msRIXzvV4ISdH4wEe_zofIED33m7WkNxx1wykRw0Zx0pjE6tKXOyMeFrMVEVUmdI4lds4HZGp6dIFOxNTjr_bUuMsDjqHyMFM8Wp6pWL6VA_xMJCV6R4lcJeIINshJ7HoO057boneBvgN_SQ4HB5GhcxuMbhWtqYD5R-RO6qR9Ea3WlLuxHkJTsRQ-X0ulNLVIXNhM28KnMlkJ0rXGxSGaXkggbXE3Wx1yTglWi5TvmJ2FFwCKChkVC4r_FCEd84lxRDFVfRFDvt8DZuy4RkQtSNOzQahtlhZXXVik2JYEx5AKCKERD0ZNkE7dGlVNVYYYCbKVqhNtce96LmgrVFEQiCMZ5HpEY0Jn9cc95e_7AlRG9JG6ASoxuofRfpRb7EGaEoKT_AImUXNvXevxrSRHjDTE5ZuiNfAwqIYwHCLd5324z7GGxYtR7o4ui4RNoXrOaYxoDB9j8wbsWGAtKyqp-dnLuM3BJPwrwhcLKIGn0md7pkqtbZ5MsYLWreeg.QWAVwkhfj8ZTAenuyWYHcg'
client_id='client_id=7sb283elponmv5p9lnerjppch4'

#payload ='client_id=7sb283elponmv5p9lnerjppch4' + '&'+'refresh_token=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.pXXZieAtnQsN8_P5OAgkYQQ3i0biDOGGzTsl33bTxIMFsTZ-GVrjJcP8JJ5u6VAnm5F9zgor-ZX5FmkIcBfqOXgjiDTJtyM6iiRhGcfm54GZ55td81etGbv7VUjDMlUdb9PQKV47_Y1XEU8sF2HX3TC9vcWndcnwb_q8AWpUZmPARzawFTStRo3uC_fg2mXx0_EK5wHb2t5Api-Pl71Z9kftbigMyYInJu3DEuoOUEk2l9ghGzkTpLwzP8-OtsbqFWMgHtr9wHdjiUFF25b90oPr-buxw4EorY2OPvDBxMMr9deg1l4dUFhBDFNbRpoKjG0huGSsbkGqdoUHPVeg2w.PPhY5Vvnj_-_WkyY.QgnR2xUsqvnJ33yBJHafHcqpVOjEVgOTAV842xd6AIIaVf34hKdLCzJ8uvwMEttbjIN-GNNQ3Z_Lk3RFyLo7CFHy0w0UAw7gnQ2OJ4wLBkdw1RlBv-lPFv1bUGSdIJny_8TdEg4ECqpwGPjgef3GOdC7m2VwDWjrsk5RES4Va5hbkSOc3_wg7Ns03d4L6KuZAc_Veblm_QlhncIJ_JSvLha5U4gCdLzHWi9YUizfyusPJFziOJYE8DArILV0cqanwC7TY-4R4AeTsggiSWiWtTuDHrkY6VU-_mxg1A5kI3vrnJ6IKpscj4uCjI3apuwTXME0pvjr3R5vuKOowWEENFlTMo35KWYSU2gbRyRFRiGr-8799NgoNOlMGO0TesnzbcE2i4AMX7MZPtLQZ6W-bnARVsQn9L-c0ChaUyStRNQYeLUPSSGA3GeQyFbqnvjOdubTOvsPvEi_sc04gJ76bAkiAZvE_1kRu2Gqqo_X0eGl25IYHaFFOOd8cTpolpxSwJwS--BcYesJYJw1kt_tYB3HITDUH5vO7Oz2zJ_-EP04eBqe71Mzp0RSWL1ClKtIgWcSelHfPxfpE9CuUR8xTPP8lwZ9D7OiKjQXbbg0kKxik4LqiGabMOZAAExIT5en5RCFiCJdEpaKJLL_w3b6jtIVgce9VLtz_CZiHHRFYOmscof51AKcjR3F2szCQVMLzQzOvxS1qWlt1IkVW3PCuwrxsdDD2iyqtV-_nxjzkLkWZZFJiBP8sNjx5Ir84nQ-fepcf5-1c2MQu75otz2-qB6F6Y5ytoae0hSfFHqmGghMFfvDaJPRHDhnLf-x0TN-2Ku39hsJ_Mqz-5YGoN7bNUdxYYZFfkF5msRIXzvV4ISdH4wEe_zofIED33m7WkNxx1wykRw0Zx0pjE6tKXOyMeFrMVEVUmdI4lds4HZGp6dIFOxNTjr_bUuMsDjqHyMFM8Wp6pWL6VA_xMJCV6R4lcJeIINshJ7HoO057boneBvgN_SQ4HB5GhcxuMbhWtqYD5R-RO6qR9Ea3WlLuxHkJTsRQ-X0ulNLVIXNhM28KnMlkJ0rXGxSGaXkggbXE3Wx1yTglWi5TvmJ2FFwCKChkVC4r_FCEd84lxRDFVfRFDvt8DZuy4RkQtSNOzQahtlhZXXVik2JYEx5AKCKERD0ZNkE7dGlVNVYYYCbKVqhNtce96LmgrVFEQiCMZ5HpEY0Jn9cc95e_7AlRG9JG6ASoxuofRfpRb7EGaEoKT_AImUXNvXevxrSRHjDTE5ZuiNfAwqIYwHCLd5324z7GGxYtR7o4ui4RNoXrOaYxoDB9j8wbsWGAtKyqp-dnLuM3BJPwrwhcLKIGn0md7pkqtbZ5MsYLWreeg.QWAVwkhfj8ZTAenuyWYHcg' +'&' +grant_type





refresh_token_statusCode=''
def refresh_token():
    print ("=========refresh_token==========")
    url = "https://nonprod-otosensesms.auth.eu-west-1.amazoncognito.com/oauth2/token"
    
    payload ='client_id=7sb283elponmv5p9lnerjppch4' + '&'+'refresh_token=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.pXXZieAtnQsN8_P5OAgkYQQ3i0biDOGGzTsl33bTxIMFsTZ-GVrjJcP8JJ5u6VAnm5F9zgor-ZX5FmkIcBfqOXgjiDTJtyM6iiRhGcfm54GZ55td81etGbv7VUjDMlUdb9PQKV47_Y1XEU8sF2HX3TC9vcWndcnwb_q8AWpUZmPARzawFTStRo3uC_fg2mXx0_EK5wHb2t5Api-Pl71Z9kftbigMyYInJu3DEuoOUEk2l9ghGzkTpLwzP8-OtsbqFWMgHtr9wHdjiUFF25b90oPr-buxw4EorY2OPvDBxMMr9deg1l4dUFhBDFNbRpoKjG0huGSsbkGqdoUHPVeg2w.PPhY5Vvnj_-_WkyY.QgnR2xUsqvnJ33yBJHafHcqpVOjEVgOTAV842xd6AIIaVf34hKdLCzJ8uvwMEttbjIN-GNNQ3Z_Lk3RFyLo7CFHy0w0UAw7gnQ2OJ4wLBkdw1RlBv-lPFv1bUGSdIJny_8TdEg4ECqpwGPjgef3GOdC7m2VwDWjrsk5RES4Va5hbkSOc3_wg7Ns03d4L6KuZAc_Veblm_QlhncIJ_JSvLha5U4gCdLzHWi9YUizfyusPJFziOJYE8DArILV0cqanwC7TY-4R4AeTsggiSWiWtTuDHrkY6VU-_mxg1A5kI3vrnJ6IKpscj4uCjI3apuwTXME0pvjr3R5vuKOowWEENFlTMo35KWYSU2gbRyRFRiGr-8799NgoNOlMGO0TesnzbcE2i4AMX7MZPtLQZ6W-bnARVsQn9L-c0ChaUyStRNQYeLUPSSGA3GeQyFbqnvjOdubTOvsPvEi_sc04gJ76bAkiAZvE_1kRu2Gqqo_X0eGl25IYHaFFOOd8cTpolpxSwJwS--BcYesJYJw1kt_tYB3HITDUH5vO7Oz2zJ_-EP04eBqe71Mzp0RSWL1ClKtIgWcSelHfPxfpE9CuUR8xTPP8lwZ9D7OiKjQXbbg0kKxik4LqiGabMOZAAExIT5en5RCFiCJdEpaKJLL_w3b6jtIVgce9VLtz_CZiHHRFYOmscof51AKcjR3F2szCQVMLzQzOvxS1qWlt1IkVW3PCuwrxsdDD2iyqtV-_nxjzkLkWZZFJiBP8sNjx5Ir84nQ-fepcf5-1c2MQu75otz2-qB6F6Y5ytoae0hSfFHqmGghMFfvDaJPRHDhnLf-x0TN-2Ku39hsJ_Mqz-5YGoN7bNUdxYYZFfkF5msRIXzvV4ISdH4wEe_zofIED33m7WkNxx1wykRw0Zx0pjE6tKXOyMeFrMVEVUmdI4lds4HZGp6dIFOxNTjr_bUuMsDjqHyMFM8Wp6pWL6VA_xMJCV6R4lcJeIINshJ7HoO057boneBvgN_SQ4HB5GhcxuMbhWtqYD5R-RO6qR9Ea3WlLuxHkJTsRQ-X0ulNLVIXNhM28KnMlkJ0rXGxSGaXkggbXE3Wx1yTglWi5TvmJ2FFwCKChkVC4r_FCEd84lxRDFVfRFDvt8DZuy4RkQtSNOzQahtlhZXXVik2JYEx5AKCKERD0ZNkE7dGlVNVYYYCbKVqhNtce96LmgrVFEQiCMZ5HpEY0Jn9cc95e_7AlRG9JG6ASoxuofRfpRb7EGaEoKT_AImUXNvXevxrSRHjDTE5ZuiNfAwqIYwHCLd5324z7GGxYtR7o4ui4RNoXrOaYxoDB9j8wbsWGAtKyqp-dnLuM3BJPwrwhcLKIGn0md7pkqtbZ5MsYLWreeg.QWAVwkhfj8ZTAenuyWYHcg' +'&'+grant_type
    #print (payload)
    headers = {
          'Content-Type': 'application/x-www-form-urlencoded',
	  'Authorization': 'Basic N3NiMjgzZWxwb25tdjVwOWxuZXJqcHBjaDQ6MWcwc21hNzJ2MDNjamlpdHNxMGdwNjB1aDg0dTI0c3BtYnNoazdvNm4zOTFrM2cyMWk5dA=='
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    refresh_token_statusCode = response.status_code
    print ("response:",refresh_token_statusCode)
    
    json_dump = json.dumps(response.json())
    
    json_load = json.loads(json_dump)
##    print ("=============",json_load)
##    with open("refresh_token.json", "a+", encoding='utf-8') as f_write:
##        json.dump(response, f_write, ensure_ascii=False, indent=4)
##        f_write.write("\n\n")
    print ("=========refresh_token==========")
    return json_load

 
    

def Create_TokenViaJWT_Standard():
    #if refresh_token_statusCode != 200:
    #   return
    
    id_token = refresh_token()
    print ("=========Start JWT==========")
    token_url = "https://349h1lay75.execute-api.eu-west-1.amazonaws.com/nonprod/tokens"
    payload="{\n\t\"name\": \"standard\",\n\t\"tenantId\": \"adi.ff2def\",\n\t\"serviceCode\": \"sms\"\n}"
    
    headers = {
      'Content-Type': 'application/json',
      'Authorization': id_token['id_token']
    }
    
    response = requests.request("POST", token_url, headers=headers, data = payload)
    print ("respns in JWT:",response.text)
    json_dump = json.dumps(response.json())
    json_load = json.loads(json_dump)
##    with open("ASTtoken.json", "a+", encoding='utf-8') as f_write:
##        json.dump(response, f_write, ensure_ascii=False, indent=4)
##        f_write.write("\n\n")
    print ("=========End JWT==========")
    return json_load

    
def createjob(ota_file,device):
    service_token = Create_TokenViaJWT_Standard()
    create_job_url = "https://349h1lay75.execute-api.eu-west-1.amazonaws.com/nonprod/registry/jobs/adi.ff2def"
    payload = "{\n\t\"payloadId\": " + "\"" + ota_file + "\"" + ",\n\t\"description\": \"Job description\",\n\t\"targets\" : [ " + "\"" + device + "\"" + " ]\n}"
    headers = {
    'Authorization': service_token['serviceToken'],
    'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", create_job_url, headers=headers, data = payload).json()
    print ("response:",response)
    print ("=========End JOBID==========")
def getjobstatus():
    url = "https://349h1lay75.execute-api.eu-west-1.amazonaws.com/nonprod/registry/jobs/adi.ff2def//status"

    payload={}
    headers = {
      'Authorization': 'AST YWQ4N2FhZDAtNjNkMi00ZWE4LTllOGMtYzk5MmU2YTVmNDM4.OgjP4OlUGKlBSilLfF2Tv3VLLCgUZKqU0tecvn8MtmDVXm/bG4C3ntzxfPMju2Wv.0T28+v4/yPAioK5+hnc1oqclmU8BHn+zIT/wAXaxfG+xmqqluDjpPFDP2c3XWgsd+M3quUPQK7ZPXcfChZSHhhQzLKw=.MjAyMC0xMi0wOFQyMDoyMzo1Ny4wMDBa'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)

##    json_dump = json.dumps(response)
##    json_load = json.loads(json_dump)
##    with open("job_details.json", "a+") as f_write:
##        json.dump(response, f_write, ensure_ascii=False, indent=4)
##        f_write.write("\n\n")
##    return json_load["jobId"]
    

   
    


##refresh_token()
##time.sleep(2)
##Create_TokenViaJWT_Standard()
##time.sleep(2)
createjob("ADSMS-00-v1_0_4","00000894J")
getjobstatus()


