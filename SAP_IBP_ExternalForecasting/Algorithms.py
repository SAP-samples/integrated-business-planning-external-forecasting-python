from typing import List, Dict

def create_result_string(results: List) -> str:
    """Concatenates the results with ';' to a string.

    Args:
        results (List): List of the algorithm results

    Returns:
        str: Concatenated results
    """

    return f"{''.join(str(x)+';' for x in results)}"[:-1]


def average_calulation(planning_object_data: Dict, parameters: Dict, historical_periods: int, forecast_periods: int) -> Dict:
    """Calculates Average Forecast

    Args:
        planning_object_data (Dict): Dictionary containing the timeseries of the planning object
        parameters (Dict): Dictionary of the algorithm parameters
        historical_periods (int): Historical periods number
        forecast_periods (int): Forecast periods number

    Returns:
        Dict: Dictionary containing the expost and forecast
    """

    demand = planning_object_data["HISTORY"]

    mean_value = sum(demand) / historical_periods

    expost = historical_periods * [mean_value]
    forecast = forecast_periods * [mean_value]

    result_dict = {"EXPOST": create_result_string(expost),
                    "FORECAST": create_result_string(forecast)}

    if "ErrorInPeriod" in parameters.keys():
        error_in_periods = [abs(history_value-expost_value)
                            for history_value, expost_value in zip(demand, expost)]
        result_dict.update({"INDEPENDENT_RES01": create_result_string(error_in_periods)})

    return result_dict


def weighted_moving_average_calculation(planning_object_data: Dict, parameters: Dict, historical_periods: int, forecast_periods: int) -> Dict:
    """Calculates Average Forecast

    Args:
        planning_object_data (Dict): Dictionary containing the timeseries of the planning object
        parameters (Dict): Dictionary of the algorithm parameters
        historical_periods (int): Historical periods number
        forecast_periods (int): Forecast periods number

    Returns:
        Dict: Dictionary containing the expost and forecast
    """

    demand = planning_object_data["HISTORY"]
    window = int(parameters["Window"])
    weights = []
    if len(planning_object_data["INDEPENDENT001"]) == historical_periods:
        weights = planning_object_data["INDEPENDENT001"] + \
            [planning_object_data["INDEPENDENT001"][-1]] * forecast_periods
    else:
        weights = planning_object_data["INDEPENDENT001"]

    weighted_past = [x*w for x, w in zip(demand, weights[:historical_periods])]

    sumed_past_moving_windows = []
    sumed_weight_moving_windows = []

    for index in range(0, historical_periods - window + 1):
        sumed_past_moving_windows.append(
            sum(weighted_past[index: index + window]))
        sumed_weight_moving_windows.append(
            sum(weights[index: index + window]))

    result = [x/w for x,
              w in zip(sumed_past_moving_windows, sumed_weight_moving_windows)]

    expost = ["NULL"]*window + list(result[:-1])

    forecast = []
    if "Extend" in parameters.keys():

        demand.append(result[-1])
        for i in range(historical_periods, historical_periods+forecast_periods-1):
            weighted_past.append(demand[-1] * weights[i])
            result.append(sum(
                weighted_past[-window:]) / sum(weights[i-window+1:i+1]))
            demand.append(result[-1])

        forecast = result[-forecast_periods:]

    else:
        forecast = [result[-1]] * forecast_periods

    result_dict = {"EXPOST": create_result_string(expost), "FORECAST": create_result_string(forecast)}

    if "ErrorInPeriod" in parameters.keys():
        error_in_periods = [abs(history_value-expost_value)
                            for history_value, expost_value in zip(demand, expost)]
        result_dict.update({"INDEPENDENT_RES01": create_result_string(error_in_periods)})    

    return result_dict


def calculate_forecast(planning_object: Dict, alogrithm_name: str, parameters: Dict,
                       historical_periods: int, forecast_periods: int) -> Dict:
    """Forecast calculation function

    Args:
        planning_object (Dict): Dictionary of the timeseries for one planning object
        alogrithm_name (str): Name of the algortihm
        parameters (Dict): Dictionary of the algorithm parameters
        historical_periods (int): Number of historical periods
        forecast_periods (int): Number of forecast periods

    Returns:
        Dict: Dictionry of result strings
    """

    planning_object_data = {}

    for data in planning_object["_AlgorithmDataInput"]:
        if data["SemanticKeyFigure"] == "HISTORY":
            planning_object_data.update(
                {"HISTORY": [float(x) for x in data["TimeSeries"].split(';')][:historical_periods]})

        else:
            planning_object_data.update(
                {data["SemanticKeyFigure"]: [float(x) for x in data["TimeSeries"].split(';')]})

    results = {}

    if alogrithm_name == "Average":

        results = average_calulation(
            planning_object_data, parameters, historical_periods, forecast_periods)

    elif alogrithm_name == "Weighted MA":

        results = weighted_moving_average_calculation(
            planning_object_data, parameters, historical_periods, forecast_periods)

    return results
