# settings
$ErrorActionPreference = "Stop"

# set those env variables if you need to access Azure via proxy
#$env:HTTP_PROXY = "..."
#$env:HTTPS_PROXY = "..."

$AZURE_SUBSCRIPTION_ID = $env:AZURE_SUBSCRIPTION_ID
$RESOURCE_GROUP = "AzureMLSpikesAndDemos"
$WORKSPACE = "AzureMLSpikesAndDemos"
$LOCATION = "westeurope"
$ENDPOINT_NAME = "sap-ibp-aml-moe-jzdwra4x"  # please use your own unique name here
$DEPLOYMENT_NAME = "default"
$DEPLOYMENT_INSTANCE_TYPE = "Standard_F2s_v2"
$DEPLOYMENT_INSTANCE_COUNT = 1
$DEPLOYMENT_APP_INSIGHTS_ENABLED = $TRUE
$ENVIRONMENT_NAME = "AzureML-sklearn-1.0-ubuntu20.04-py38-cpu"

# initialization
Write-Host "Initializing script..."
#Write-Host "Login to Azure..."
## note: use whatever login type suits best in your deployment setup
#az login
Write-Host "Setting subscription..."
az account set -s $AZURE_SUBSCRIPTION_ID
Write-Host "Setting default values for Azure CLI..."
az configure --scope local --defaults group=$RESOURCE_GROUP workspace=$WORKSPACE location=$LOCATION

# # create environment
# # note: in this example, we use a so-called "curated" environment, which is provided and managed by Microsoft.
# #       therefore, we don't need to create our own environment. if you need to create & use your own environment,
# #       for example because you need special packages or a special Docker image, check out
# #       https://docs.microsoft.com/en-us/azure/machine-learning/how-to-manage-environments-v2. The contained files
# #       and command below give you an example how custom environments can be created.
# Write-Host "Creating environment..."
# az ml environment create -n $ENVIRONMENT_NAME -f webservice/environment/environment.yml --set name=$ENVIRONMENT_NAME

# # deploy model
# # note: in this scenario, we train our models on-the-fly. in case you want to use a pre-trained model in your scoring
# #       script, you can register & use it by
# #       - placing the files forming your model in the model folder
# #       - register the model with a command like below (don't forget to set $MODEL_NAME)
# #       - add a reference to the model in your deployment
# #       - access the model files in your score.py under the path contained in env variable AZUREML_MODEL_DIR
# az ml model create -n $MODEL_NAME -f webservice/model/model.yml --set name=$MODEL_NAME

# deploy endpoint if not exists
Write-Host "Deploying endpoint..."
$endpoint_exists_already = ![string]::IsNullOrEmpty((az ml online-endpoint list `
    --query "[?name=='$ENDPOINT_NAME']" -o tsv))
if (!$endpoint_exists_already) {
    az ml online-endpoint create -n $ENDPOINT_NAME -f endpoint.yml --set name=$ENDPOINT_NAME
} else {
    Write-Host "Endpoint exists already."
}

# deploy deployment
# notes: - always using latest deployed environment and model using "@latest" postfix
#        - use multiple deployments for minimal/no downtimes, the example here uses only one deployment
#        - updating or creating, depending if exists already
Write-Host "Deploying deployment..."
$deployment_exists_already = ![string]::IsNullOrEmpty((az ml online-deployment list -e $ENDPOINT_NAME `
            --query "[?endpoint_name=='$ENDPOINT_NAME']" -o tsv))
$create_or_update = $deployment_exists_already ? "update" : "create"
if ($create_or_update -eq "create") {
    Write-Host "Creating deployment..."
}
if ($create_or_update -eq "update") {
    Write-Host "Updating existing deployment..."
}
az ml online-deployment $create_or_update -n $DEPLOYMENT_NAME --endpoint $ENDPOINT_NAME -f deployment.yml `
    --set endpoint_name=$ENDPOINT_NAME `
    --set environment="azureml:$ENVIRONMENT_NAME@latest" `
    --set instance_type=$DEPLOYMENT_INSTANCE_TYPE `
    --set instance_count=$DEPLOYMENT_INSTANCE_COUNT `
    --set app_insights_enabled=$DEPLOYMENT_APP_INSIGHTS_ENABLED
az ml online-endpoint update -n $ENDPOINT_NAME --traffic "$DEPLOYMENT_NAME=100"

# query deployment
#Write-Host "Querying deployment..."
#az ml online-deployment show -n $DEPLOYMENT_NAME --endpoint $ENDPOINT_NAME

# get deployment logs
#Write-Host "Querying deployment logs..."
#az ml online-deployment get-logs -n $DEPLOYMENT_NAME --endpoint $ENDPOINT_NAME

# cleanup
# deployment
#Write-Host "Deleting deployment..."
#az ml online-deployment delete -n $DEPLOYMENT_NAME --endpoint $ENDPOINT_NAME -y
# endpoint
#Write-Host "Deleting endpoint..."
#az ml online-endpoint delete -n $ENDPOINT_NAME -y
