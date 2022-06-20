
async def create_vi_dataset(dataset_display_name, bigquery_source_uri):  

    # The AI Platform services require regional API endpoints.    
    vi_ds_client = aiplatform_v1.DatasetServiceAsyncClient(client_options=client_options)
    
    metadata_dict = {"input_config": {"bigquery_source": {"uri": bigquery_source_uri}}}
    metadata = json_format.ParseDict(metadata_dict, Value())

    # Initialize request argument(s)
    dataset = aiplatform_v1.Dataset()
    dataset.display_name = dataset_display_name
    dataset.metadata_schema_uri = "gs://google-cloud-aiplatform/schema/dataset/metadata/time_series_1.0.0.yaml"
    dataset.metadata =  metadata

    request = aiplatform_v1.CreateDatasetRequest(
        parent=parent,
        dataset=dataset,
    )

    # Make the request
    operation = await vi_ds_client.create_dataset(request=request)

    print("Waiting for dataset to be created to complete...")

    response = await operation.result()

    print(response) 
# [END vertex_create_dataset] 