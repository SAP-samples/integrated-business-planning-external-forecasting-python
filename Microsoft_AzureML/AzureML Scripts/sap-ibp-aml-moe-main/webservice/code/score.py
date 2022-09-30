"""
Scoring script for the prediction webservice.

To run/debug this script locally, start the "Debug score.py" launch configuration in VS.Code.

Use the deploy-azure.ps1 script to deploy this to a Managed Online Endpoint in Azure Machine Learning.
"""

import json

import numpy as np
from sklearn.linear_model import LinearRegression


def init():
    """Is invoked whenever the service is started."""
    # note: usually, we would load our model(s) here to avoid later delays during inferencing. however, because we train
    #       our models on the fly, there is no need to load any models here.
    #
    #       in case you still need to use a pretrained model, you need to register it and reference it in this
    #       webservice's deployment (as described in deploy-azure.ps1). Afterwards, this script can load the model's
    #       files from the directory stored in environment variable AZUREML_MODEL_DIR.
    pass


def run(body):
    """
    Is invoked whenever a REST request for prediction(s) is made.
    """

    # get input JSON
    input_json = json.loads(body)

    # capture (relevant) metadata
    algorithm_name = input_json["Metadata"][0]["AlgorithmName"]
    historical_periods = int(input_json["Metadata"][0]["HistoricalPeriods"])
    forecast_periods = int(input_json["Metadata"][0]["ForecastPeriods"])

    valid_algorithm_names = ["Average", "LinearRegression"]
    if algorithm_name not in valid_algorithm_names:
        raise ValueError(
            (
                f"The given algorithm name '{algorithm_name}' is not supported. Ensure that the given algorithm name "
                f"is one of the following: {valid_algorithm_names}."
            )
        )

    # get result skeleton
    request_id = input_json["value"][0]["RequestID"]
    result = {"RequestID": request_id, "_AlgorithmDataOutput": [], "_Message": []}

    # iterate through requested forecasts and add results to skeleton
    appended_group_ids = set()
    for value in input_json["value"]:
        for master_data_index, master_data in enumerate(value["_MasterData"]):
            # capture master data
            group_id = master_data["GroupID"]
            # capture historical data
            algorithm_data_input = value["_AlgorithmDataInput"][master_data_index]
            semantic_key_figure = algorithm_data_input["SemanticKeyFigure"]
            time_series_string = algorithm_data_input["TimeSeries"]
            historical_data = [value for value in time_series_string.split(";")[:historical_periods]]
            historical_data_length = len(historical_data)

            if algorithm_name == "Average":
                # most simple forecast method -- simply forecasting the average of the historical periods
                mean = np.mean(np.array([float(item) for item in historical_data]))
                forecast = np.repeat(mean, forecast_periods)

            elif algorithm_name == "LinearRegression":
                # train model
                # note: this uses a very simple linear regression with negative values set to zero. for the sake of the
                #       demo, the algorithm used here is not overly complex. in a real-world use case you might want to
                #       use a more sophisticated forecasting algorithm, maybe also involving external data.
                X = np.array(range(len(historical_data))).reshape(-1, 1)
                y = np.array(historical_data).reshape(-1, 1)
                model = LinearRegression().fit(X, y)
                # do forecast
                forecast = model.predict(
                    np.array(range(historical_data_length, historical_data_length + forecast_periods)).reshape(-1, 1)
                ).flatten()

            else:
                raise NotImplementedError(
                    (
                        f"Algorithm '{algorithm_name}' is not implemented. If you encounter this error, you have found "
                        f"a bug."
                    )
                )

            # add forecast to result
            forecast_as_string = ";".join([f"{value}" for value in forecast])
            result_data = f"{forecast_as_string}"
            result["_AlgorithmDataOutput"].append(
                {
                    "RequestID": request_id,
                    "GroupID": group_id,
                    "SemanticKeyFigure": "FORECAST",
                    "ResultData": result_data,
                }
            )
            if group_id not in appended_group_ids:
                result["_Message"].append(
                    {
                        "RequestID": request_id,
                        "GroupID": group_id,
                        "MessageSequence": 1,
                        "MessageType": "I",
                        "MessageText": "Okay",
                    }
                )
                appended_group_ids.add(group_id)

    # return result
    return result
