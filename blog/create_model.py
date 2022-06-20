
async def create_vi_model(pipeline_display_name, model_display_name, dataset_id, p, l):  
    # set the columns used for training and their data types
    transformations = [       
        {"timestamp": {"column_name": "timestamp", "invalidValuesAllowed": "false"}},
        {"auto": {"column_name": "cdemandQty"}},
    ]

    data_granularity = {"unit": "day", "quantity": 1}

    # the inputs should be formatted according to the training_task_definition yaml file
    training_task_inputs_dict = {
        # required inputs
        "targetColumn": "cdemandQty",
        "timeSeriesIdentifierColumn": "prdid",
        "timeColumn": "timestamp",
        "transformations": transformations,
        "dataGranularity": data_granularity,
        "optimizationObjective": "minimize-rmse",
        "trainBudgetMilliNodeHours": 8000, 
        "unavailableAtForecastColumns": ['cdemandQty', 'locid', 'custid'],
        "availableAtForecastColumns": ['timestamp'],
        "forecastHorizon": 10,
    }

    training_task_inputs = json_format.ParseDict(training_task_inputs_dict, Value())

    
    # The AI Platform services require regional API endpoints.    
    vi_pipe_client = aiplatform_v1.PipelineServiceClient(client_options=client_options) 

    training_pipeline = {
        "display_name": pipeline_display_name,
        "training_task_definition": "gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_forecasting_1.0.0.yaml",
        "training_task_inputs": training_task_inputs,
        "input_data_config": {
            "dataset_id": dataset_id,
            "fraction_split": {
                "training_fraction": 0.8,
                "validation_fraction": 0.1,
                "test_fraction": 0.1,
            },
        },
        "model_to_upload": {"display_name": model_display_name},
    }
    parent = f"projects/{p}/locations/{l}"

    print("Waiting model creation...")

    response = vi_pipe_client.create_training_pipeline(
        parent=parent, training_pipeline=training_pipeline
    )
    print("response:", response) 
# [END create model on VI] 