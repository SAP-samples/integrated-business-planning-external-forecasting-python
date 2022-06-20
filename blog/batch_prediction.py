
async def create_batch_prediction(batch_prediction_display_name, model_name, predictions_format, source_folder, target_folder, p, l):  
    

    # the inputs should be formatted according to the training_task_definition yaml file
    batch_prediction_job = {
        "display_name": batch_prediction_display_name, 
        "model": model_name,
        "input_config": {
            "instances_format": predictions_format,
            "bigquery_source": {"input_uri": source_folder},
        },
        "output_config": {
            "predictions_format": predictions_format,
            "bigquery_destination": {"output_uri": target_folder},
        },
    } 

    batch_prediction_inputs = json_format.ParseDict(batch_prediction_job, Value())

    
    # The AI Platform services require regional API endpoints.    
    vi_job_client = aiplatform_v1beta1.JobServiceClient(client_options=client_options)  

    parent = f"projects/{p}/locations/{l}"

    print("Waiting model creation...")

    response = vi_job_client.create_batch_prediction_job(
        parent=parent, batch_prediction_job=batch_prediction_job 
    )
    print("response:", response) 
# [END Start Batch prediction job VI] 