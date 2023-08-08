import json 
import uuid
import requests
import time
import jmespath
from typing import List
import os
from configparser import ConfigParser

 
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Read config file
config_object = ConfigParser()
config_object.read("server.cfg")

# User credentials and server url
SERVER_URL = config_object["SERVICECONFIG"]["SERVER_URL"]
SERVICE_PATH = config_object["SERVICECONFIG"]["SERVICE_PATH"]
PLANNING_AREA = config_object["SERVICECONFIG"]["PLANNING_AREA"] 
READ_QUERY = config_object["SERVICECONFIG"]["READ_QUERY"] 
METADATA_URL = config_object["SERVICECONFIG"]["METADATA_URL"]  
FIELD_STRING = config_object["SERVICECONFIG"]["FIELD_STRING"] 

USERNAME = config_object["AUTHCONFIG"]["USERNAME"]
PASSWORD = config_object["AUTHCONFIG"]["PASSWORD"] 

KF_SERVICE = f"https://{SERVER_URL}/{SERVICE_PATH}/{PLANNING_AREA}"  
POST_URL   = f"{KF_SERVICE}Trans"
RESULT_URL = f"https://{SERVER_URL}/{SERVICE_PATH}/getExportResult?P_TransactionID="
MSG_URL    = f"{KF_SERVICE}Message?$filter=Transactionid eq "
 

# GET CALL TO READ DATA FROM IBP USING KEY FIGURE API
def read_key_figure():
    
    print(f"Processing request readKF  started.", flush=True)
    try:   
        request_get = requests.get(f"{KF_SERVICE}?{READ_QUERY}", 
                                   headers={"accept": "application/json", "x-csrf-token" : "fetch"}, 
                                   auth=(USERNAME, PASSWORD), 
                                   verify=False)    
           
        if request_get.status_code == 200:              
            request_data = json.loads(request_get.text)
            cookies = request_get.cookies
            print(request_data)
        elif request_get.status_code > 200:  
            print(request_get.text)
    except ValueError:  # includes simplejson.decoder.JSONDecodeError
        print("Error doing request")
         

# POST CALL TO WRITE DATA TO IBP USING KEY FIGURE API
def writeKF():
    print(f"Processing request for writeKF started.", flush=True)
    # Fetch a CSRF token
    try:   
        req_token = requests.get(f"https://{SERVER_URL}/{SERVICE_PATH}/{METADATA_URL}", 
                                   headers={"x-csrf-token" : "fetch"}, 
                                   auth=(USERNAME, PASSWORD), 
                                   verify=False)    
         # Store the CSRF token for later use
        if req_token.status_code == 200:              
            csrf_token = req_token.headers["x-csrf-token"]
            cookies = req_token.cookies
            # Generate a UUID as a transaction ID
            transaction_id = uuid.uuid4().hex
            # Prepare data to write to IBP
            f = open('sample_data.json')
            sample_data = json.load(f)
            out_json = {
                "Transactionid" : f"{transaction_id}",
                "AggregationLevelFieldsString" :  f"{FIELD_STRING}",     
                "DoCommit" : bool(1),    # Change this if you want to POST in batches. Do the commit in the last batch       
                "Nav"+ f"{PLANNING_AREA}" : sample_data["kf_data"]
            }
            #print(out_json) 
            post_data = json.dumps(out_json)
            #print(POST_URL)
             # write data to IBP
            req_post = requests.post(POST_URL, str(post_data), cookies=cookies,
                                                headers={"x-csrf-token": csrf_token,
                                                        "Content-Type": "application/json", "OData-Version": "4.0"}, 
                                                auth=(USERNAME, PASSWORD), 
                                                verify=False)
            if req_post.status_code == 201: 
                print(f"Post to IBP system! using transaction id: {transaction_id} Status code: {req_post.status_code}. Sleeping for 60 now..", flush=True)
                time.sleep(20) # Wait for the Post processing to complete if you are setting DoCommit = true
                print("Trying to get export status....")
                # # Check for transaction ID. check the status for different situations - PROCESSING, PROCESSED WITH ERRORS
                check_status(f"{transaction_id}", cookies, csrf_token) 
            elif req_post.status_code > 201:  
                print(req_post.text)
        elif req_token.status_code > 200:  
            print(req_token.text)
     
    except ValueError:  # includes simplejson.decoder.JSONDecodeError
        print("Error doing request")   

# Function to check the status of the POST call
def check_status(transaction_id, cookies, csrf_token):
    exit = 0
    
    try:   
        req_RESULT = requests.get(RESULT_URL +  "\'" + f"{transaction_id}" + "\'&$format=json", cookies=cookies,
                                                headers={"x-csrf-token": csrf_token, "Accept" : "application/json, application/xml",}, 
                                                auth=(USERNAME, PASSWORD), 
                                                verify=False)
        if req_RESULT.status_code == 200:              
            status_data = json.loads(req_RESULT.text)
            value_data = jmespath.search("d.results[0].Value", status_data)
                
            if value_data == "PROCESSED" :
                print(value_data)
                exit = 2
            else:  
                while exit < 1:
                    print(MSG_URL +  "\'" + f"{transaction_id}" + "\'")
                    req_MESSAGE = requests.get(MSG_URL +  "\'" + f"{transaction_id}" + "\'", cookies=cookies,
                                            headers={"x-csrf-token": csrf_token, "Accept" : "application/json, application/xml",}, 
                                            auth=(USERNAME, PASSWORD), 
                                            verify=False)
                    print(req_MESSAGE.text)
                    if req_MESSAGE.status_code == 200:              
                        msg_data = json.loads(req_MESSAGE.text)
                        status_value_data = jmespath.search("d.results[0].Value", msg_data)
                        print(status_value_data)
                        if status_value_data != "PROCESSING" :                            
                            exit = 2
                        else :
                            time.sleep(10)
                            exit = 0
                    elif req_MESSAGE.status_code > 200:  
                        print(req_MESSAGE.text)
                        exit = 2 
        elif req_RESULT.status_code > 200:  
            print(req_RESULT.text)
            exit = 2 
    except ValueError:  # includes simplejson.decoder.JSONDecodeError
        print("Error doing request")

  
