
def create_bq_dataset(dataset_id) -> None:
    
    from google.cloud import bigquery 

    # Construct a BigQuery client object.
    bq_client = bigquery.Client()
    
    ds = bq_client.create_dataset(dataset_id)
    print(
        "Created dataset {}.{}".format(ds.project, ds.dataset_id)
    )
# [END Create dataset in Big Query]