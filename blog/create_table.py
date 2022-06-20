
def create_table(table_name, dataset_id) -> None:
    
    from google.cloud import bigquery 

    schema = [
        bigquery.SchemaField("prdid", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("locid", "STRING"),
        bigquery.SchemaField("custid", "STRING"),
        bigquery.SchemaField("timestamp", "TIMESTAMP"), 
        bigquery.SchemaField("cdemandQty", "INTEGER"), 
    ] 

    table_id = str(project + "." + dataset_id + "." + table_name)
    table = bigquery.Table(table_id, schema=schema)        

    # Construct a BigQuery client object.
    bq_client = bigquery.Client()
    
    table = bq_client.create_table(table)  # Make an API request.
    print(
        "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
    )
# [END bigquery_create_table]