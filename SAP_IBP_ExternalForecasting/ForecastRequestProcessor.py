import requests
import json
import urllib3
from typing import List
from Algorithms import calculate_forecast
from data_transformations import ibp_payload
import os
from configparser import ConfigParser

urllib3.disable_warnings()
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Read config file
config_object = ConfigParser()
config_object.read("server.cfg")

# User credentials and server url
SERVER_URL = config_object["SERVICECONFIG"]["SERVER_URL"]
SERVICE_PATH = config_object["SERVICECONFIG"]["SERVICE_PATH"]
USERNAME = config_object["AUTHCONFIG"]["USERNAME"]
PASSWORD = config_object["AUTHCONFIG"]["PASSWORD"]

TASK_URL = f"https://{SERVER_URL}/{SERVICE_PATH}/Request"
RESULT_URL = f"https://{SERVER_URL}/{SERVICE_PATH}/Result"
DATA_URL = f"https://{SERVER_URL}/{SERVICE_PATH}/Input"


def get_remaining_data(planning_objects: List, url: str, cookies: object) -> List:
    """Requests the next datachunk until all data arrived

    Args:
        planning_objects (List): List of planning objects
        url (str): URL of the next data chunk
        cookies (object): Authorization cookies

    Returns:
        List: List of planning objects
    """
    data_get = requests.get(
        url, headers={"accept": "application/json"}, cookies=cookies, verify=False)

    if data_get.status_code == 200:
        if data_get.json()["value"]:
            planning_objects.extend(data_get.json()["value"])
        else:
            return planning_objects

        if "@odata.nextLink" in data_get.json().keys():
            return get_remaining_data(planning_objects,
                                      f"https://{SERVER_URL}{data_get.json()['@odata.nextLink']}", cookies)
        else:
            return planning_objects
    else:
        print(
            f"Failed to retrieve forecast data! Status code: {data_get.status_code}.", flush=True)
        raise ConnectionError


def process_forecast_request(request_id: int):
    """Runs the forecasting process on the request.

    Request JSON:
    {
        "RequestID": Integer,
        "AlgorithmName": String,
        "AlgorithmParameter": String("ParameterName, ParameterType("integer", "double", "text"), ParameterValue"),
        "HistoricalPeriods": Integer,
        "ForecastPeriods": Integer,
    }

    Data JSON:
    {
        "@odata.context": String containing the metadata information,
        "@odata.metadataEtag": String containing the aggregation level, and datetime stamp. "W/\"20220303095028\"",
        "value":
        [
            {
                "RequestID": Integer,
                "GroupID": Integer,
                "_AlgorithmDataInput": 
                    [
                        {
                            "RequestID": Integer, 
                            "GroupID": Integer, 
                            "SemanticKeyFigure": "HISTORY" or "INDEPENDENT001" - "INDEPENDENT999", 
                            "TimeSeries": Timeseries in string format with ";" separator character,
                        }
                    ], 
                "_MasterData": 
                    [
                        {
                            "RequestID": Integer, 
                            "GroupID": Integer, 
                            "AttributeID": Planning attribute name string, 
                            "AttributeValue": Planning attribute value string,
                        }
                    ]
            }
        ]
        "@odata.nextLink": String containing the next url path to the next data chunk,
    }

    Results JSON:
    {
        "RequestID": Integer,
        "_AlgorithmDataOutput": [
            {
                "RequestID": Integer,
                "GroupID": Integer,
                "SemanticKeyFigure": "EXPOST" or "FORECAST",
                "ResultData": List of result strings,
            }
        ],
        "_Message": [
            {
                "RequestID": Integer,
                "GroupID": Integer,
                "MessageSequence": Integer,
                "MessageType": "I" or "E",
                "MessageText": String,
            }
        ]
    }

    Args:
        request_id (int): ID number of the request to be processed

    """
    print(
        f"Processing forecast request for id {request_id} started.", flush=True)

    request_get = requests.get(f"{TASK_URL}?$filter=RequestID%20eq%20{request_id}",
                               headers={"accept": "application/json"}, auth=(USERNAME, PASSWORD), verify=False)
    
    if request_get.status_code == 200:
        request_data = request_get.json()["value"][0]
        cookies = request_get.cookies

        algorithm_name = request_data["AlgorithmName"]

        parameters = {}
        if request_data["AlgorithmParameter"]:
            param_list = []
            for parameter in request_data["AlgorithmParameter"].split(";"):
                if "=" in parameter:
                    param_list.append(map(str.strip, parameter.split('=', 1)))
            parameters = dict(param_list)

        historical_periods = request_data["HistoricalPeriods"]
        forecast_periods = request_data["ForecastPeriods"]
        print('Historical periods: ' + str(historical_periods))
        print('Forecast periods: ' + str(forecast_periods))

        data_get = requests.get(f"{DATA_URL}?$filter=RequestID%20eq%20{request_id}&$expand=_AlgorithmDataInput,_MasterData",
                                headers={"accept": "application/json"}, cookies=cookies, verify=False)

        results = {}
        if data_get.status_code == 200:
            planning_objects = data_get.json()["value"]
            if "@odata.nextLink" in data_get.json().keys():
                try:
                    planning_objects = get_remaining_data(
                        planning_objects, f"https://{SERVER_URL}{data_get.json()['@odata.nextLink']}", cookies)
                except ConnectionError:
                    return

            # Output format
            output = {
                "RequestID": request_id,
                "_AlgorithmDataOutput": [],
                "_Message": [],
            }

            # print(planning_objects)

            for planning_object in planning_objects:

                # Use this to calculate your own forecast localy.
                # results = calculate_forecast(planning_object, algorithm_name, parameters, historical_periods, forecast_periods)

                # Use this to calculate forecast using Google Vertex AI.
                results = ibp_payload(planning_object, historical_periods, forecast_periods, [])
                # If you want to use the Google Vertex AI, use the results object to send the data to Big Query table, start a batch prediction and then import the results from the BQ Table.


                if len(results.keys()):

                    # Output Key Figures
                    for key_figure_name, key_figure_result in results.items():
                        key_figure_data = {
                            "RequestID": request_id,
                            "GroupID": planning_object["GroupID"],
                            "SemanticKeyFigure": key_figure_name,
                            "ResultData": key_figure_result,
                        }
                        output["_AlgorithmDataOutput"].append(key_figure_data)

                    # Message
                    message = {
                        "RequestID": request_id,
                        "GroupID": planning_object["GroupID"],
                        "MessageSequence": 1,
                        "MessageType": "I",
                        "MessageText": "Okay",
                    }
                    output["_Message"].append(message)

            # Header message
            if len(results.keys()):
                msg_header = {
                    "RequestID": request_id,
                    "GroupID": -1,
                    "MessageSequence": 1,
                    "MessageType": "I",
                    "MessageText": f"{algorithm_name}",
                }
                output["_Message"].append(msg_header)
            else:
                msg_header = {
                    "RequestID": request_id,
                    "GroupID": -1,
                    "MessageSequence": 1,
                    "MessageType": "E",
                    "MessageText": f"Forecast calculation failed! Algorithm: {algorithm_name} .",
                }
                output["_Message"].append(msg_header)

            output_json = json.dumps(output)

            token_request = requests.get(RESULT_URL, headers={"x-csrf-token": "fetch", "accept": "application/json"},
                                         cookies=cookies, verify=False)

            if token_request.status_code == 200:

                result_send_post = requests.post(RESULT_URL, str(output_json), cookies=cookies,
                                                headers={"x-csrf-token": token_request.headers["x-csrf-token"],
                                                        "Content-Type": "application/json", "OData-Version": "4.0"}, verify=False)

                print(
                    f"Forecast result for id {request_id} sent back to IBP system! Status code: {result_send_post.status_code}.", flush=True)
            else:
                print(
                f"Failed to retrieve x-csrf token! Status code: {token_request.status_code}.", flush=True)
        else:
            print(
                f"Failed to retrieve forecast data! Status code: {data_get.status_code}.", flush=True)
    else:
        print(
            f"Failed to retrieve forecast model details! Status code: {request_get.status_code}", flush=True)
