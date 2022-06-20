import math
from random import randrange
import datetime
import json
import asyncio
from typing import List, Union
import numpy

from google.cloud import aiplatform_v1 
from google.cloud import aiplatform_v1beta1
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value

custIds = [100, 101, 102, 103]
prdIds  = ["PRD_0001", "PRD_0002", "PRD_0003", "PRD_0004"]

# dataset_id = "ibp"
dataset_id = "ibp_eft"
inputTableName = "demand_qty_py01"
scoreTableName = "score_demand_py01"
project = "sap-ibpexternalforecast01"
location = "europe-west4"
bigquery_source_uri = "bq://" + project + "." + dataset_id + "." + inputTableName
bigquery_score_uri = f"bq://{project}.{dataset_id}.{scoreTableName}"
bigquery_target_folder = "bq://sap-ibpexternalforecast01.ibp_eft"
dataset_display_name = 'ibp_eft_py01' 
batch_prediction_display_name = "ibp_eft_py01"
# projects/459663093113/locations/europe-west4/models/8724369679704915968@1
model_name = "ibp_eft_py01"
api_endpoint = "europe-west4-aiplatform.googleapis.com"
predictions_format = "bigquery"

# Specifies the location of the api endpoint
client_options = {"api_endpoint": api_endpoint}
parent = f"projects/{project}/locations/{location}"


def get_random_qty(min, max):
    min = math.ceil(min)
    max = math.floor(max)
    return math.floor(randrange(min, max) * (max - min)) + min

def new_product(prd_id, cust_id, start_event, is_score):
    # cdemandQty = str('nan')

    if(is_score == 0):
        cdemandQty = get_random_qty(50,100)
        return {
            "prdid": str(prd_id),
            "locid": "001",
            "custid": str(cust_id),
            "timestamp": str(start_event),
            "cdemandQty": cdemandQty
        }
    else:
        return {
            "prdid": str(prd_id),
            "locid": "001",
            "custid": str(cust_id),
            "timestamp": str(start_event) 
        } 

def generate_data(start_event, stop_event, is_score):
    i = 0
    day_count = 0
    jsonobj = []
    prepare_to_score = is_score
    while i < 6:
        
        start_day = start_event.day + day_count
        start_month = start_event.month
        start_year = start_event.year

        today = datetime.datetime.today()

        if(start_event > today):
            prepare_to_score = True
        else:
            prepare_to_score = False
        
        day_count += 1
        for c in custIds:
            for p in prdIds:
                rg = new_product(p, c, start_event, prepare_to_score)
                jsonobj.append(rg)
                

        start_event += datetime.timedelta(days=1)        
        if(start_event > stop_event):
            i = 7
            print("IBP data generation finished..")
            # print(jsonobj)

    return jsonobj
# - end of generate_data


def create_bq_dataset(dataset_id) -> None:
    
    from google.cloud import bigquery 

    # Construct a BigQuery client object.
    bq_client = bigquery.Client()
    
    ds = bq_client.create_dataset(dataset_id)
    print(
        "Created dataset {}.{}".format(ds.project, ds.dataset_id)
    )
# [END Create dataset in Big Query]

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


async def create_batch_prediction(batch_prediction_display_name, model_name, predictions_format, source_folder, target_folder, p, l):  
    

    # the inputs should be formatted according to the training_task_definition yaml file
    # model is working, but model_name is not working
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

async def start_process():

    # create_bq_dataset(dataset_id)
    
    # STEP 1 - Create Table in BigQuery. Assume you have a dataset. If not create one. - Works!
    # create_table(inputTableName, dataset_id)
    # create_table(scoreTableName, dataset_id)

    # STEP 2a - Generate IBP Data - Works!
    # start_event = datetime.datetime(2018, 5, 15)  
    # stop_event  = datetime.datetime(2022, 5, 20)  
    
    #  We simulate data here. Ideally you should send your own IBP Planning data to the BQ Table. You can use the ibp_scoring_payload from the data_transformation.ps as a reference.
    # ibp_data = generate_data(start_event, stop_event, True)

    # STEP 2b - Insert IBP Data into the created table. - Works!
    # insert_bq_table(inputTableName, dataset_id, ibp_data) 
    # insert_bq_table(scoreTableName, dataset_id, ibp_data) 
    
    # STEP 3 - Create a new dataset in Google Vertex AI  - Works!
    # await create_vi_dataset(dataset_display_name, bigquery_source_uri)

    # STEP 4 - Train the data in a Pipeline to create a model - Works!
    # pipeline_display_name, model_display_name, dataset_id, project, location
    # await create_vi_model(model_name, model_name, "5459616191628705792", project, location)

    # STEP 5 - Create a Batch prediction Job using the model we created - works with model_name !
    # batch_prediction_display_name, model_name, predictions_format, source_folder, target_folder, p, l
    # await create_batch_prediction(batch_prediction_display_name, "projects/459663093113/locations/europe-west4/models/2334184020931248128", predictions_format, bigquery_score_uri, bigquery_target_folder, project, location)

loop = asyncio.get_event_loop()
loop.run_until_complete(start_process())
