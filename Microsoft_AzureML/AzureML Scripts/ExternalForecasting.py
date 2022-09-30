import json 
import pandas as pd
import datetime 
    
def row_details(prd_id, loc_id, cust_id, forecast, ibp_time_stamp, is_score): 

    if(is_score == 0): 
        return {
            "prdid"     : str(prd_id),
            "locid"     : str(loc_id),
            "custid"    : str(cust_id),
            "timestamp" : str(ibp_time_stamp),
            "cdemandQty": forecast
        }
    else:
        return {
            "prdid"     : str(prd_id),
            "locid"     : str(loc_id),
            "custid"    : str(cust_id),
            "timestamp" : str(ibp_time_stamp) 
        } 


def ibp_scoring_payload(ibp_payload, historical_periods, forecast_periods, payload_array): 

    # Today
    start_event = datetime.datetime.today()
    # past 5 days
    days = datetime.timedelta(historical_periods)
    # Date on the earliest historical day
    earliest_date = start_event - days
    # print(earliest_date)
    df = pd.read_json('from_ibp.json')
    forecast_count = 0
    historical_count = historical_periods
    
    # Loop over the master data
    for master_data, input_data in zip(ibp_payload['_MasterData'], ibp_payload['_AlgorithmDataInput']):
        md_df = pd.DataFrame(master_data)['AttributeValue']
        ip_df = pd.DataFrame(input_data)['TimeSeries']
        # Loop over the time series data for a specific master data record 
        for ip_val in ip_df.values:
            ip_val = ip_val.split(";")
            for ip in ip_val: 
                # Calculate the time stamp based on historical periods and future periods.    
                if (historical_count != 0):
                    # Use your own location and customer IDs
                    row_json = row_details(md_df.values[0], "100", "101", ip, earliest_date, False) 
                    historical_count -= 1                
                    days = datetime.timedelta(historical_count)
                    # the next historical day
                    earliest_date = start_event - days
                elif (forecast_count <= forecast_periods):
                    # Use your own location and customer IDs
                    row_json = row_details(md_df.values[0], "100", "101", ip, earliest_date, True)                
                    forecast_count += 1                
                    days = datetime.timedelta(forecast_count)
                    # the next forecast day
                    earliest_date = start_event + days
                else:
                    break
                
                # Store the result to a JSON Array
                payload_array.append(row_json) 

        # reset the counters
        forecast_count = 0
        historical_count = historical_periods

    return payload_array

# Test
odf = pd.read_json('from_ibp.json')
# print(df['_MasterData']) 
historical_periods = 50
forecast_periods   = 6 

vi_data = ibp_scoring_payload(odf, historical_periods, forecast_periods, [])
print(vi_data)