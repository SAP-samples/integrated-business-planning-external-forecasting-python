
def insert_bq_table(table_name, dataset_id, ibp_data) -> None: 
    
    
    from google.cloud import bigquery 
    # Set the table ID
    table_id = str(project + "." + dataset_id + "." + table_name)

    # Construct a BigQuery client object.
    bq_client = bigquery.Client()

    # Make an API request.
    errors = bq_client.insert_rows_json(table_id, ibp_data)  
    if errors == []:
        print("IBP data is inserted.")
    else:
        print("Errors while inserting rows: {}".format(errors))
# [END bigquery_table_insert_rows]