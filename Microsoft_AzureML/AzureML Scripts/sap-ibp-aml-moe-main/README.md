# Forecasting on SAP IBP data using Azure Machine Learning

Brief example to demonstrate the development and deployment of an Azure Machine Learning Managed Online Endpoint (REST
webservice) that forecasts on data from SAP Integrated Business Planning (IBP).
  
## Prerequisites

1. An Azure subscription
2. An Azure Machine Learning workspace in Azure, see [here](https://docs.microsoft.com/en-us/azure/machine-learning/quickstart-create-resources) 
   for instructions; a Compute Instance or Compute Cluster are NOT needed for this example.
3. To deploy the web service as an Azure ML Managed Online Endpoint:
    - Azure Commandline Interface (Az CLI) installed on your machine, see [here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
      for instructions. Note that Windows, macOS and Linux are supported.
    - ml extension for the Azure CLI. See [here](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-configure-cli?tabs=public)
      for instructions.
    - To leverage the deployment script written in PowerShell: [PowerShell](https://github.com/PowerShell/PowerShell).
      Note: PowerShell is meanwhile also available for macOS and Linux (besides Windows).
    - Before running the deployment script, please make sure that your commandline is signed-in to Azure. You can
      sign-in by running an `az login` command and follow the instructions there.

*For development*:
- VS.Code incl.
    * Python extension
    * Azure Machine Learning extension
- conda
- a conda environment with the packages installed in `dev-conda.yml`. Run `conda env create --name sap-ibp-aml-moe --file dev-conda.yml`
  to create it.
- a REST client to send requests against a web service (for testing/debugging)


## Steps to Deploy

1. Clone the repo.
2. Edit the `deploy-azure.ps1` file and update the configuration (on top of the script) to your needs.

> IMPORTANT: Please make sure that you use a unique name for variable `$ENDPOINT_NAME` to ensure that you are not
>            stealing someone else's name.

3. Open a PowerShell terminal.
4. Go to folder `webservice`.
5. Run the deployment script by running the following command: `.\deploy-azure.ps1`.

Note: If you have no PowerShell installed, you can also deploy the solution by running the individual `az ml ...`
commands contained in the deployment script. Besides, Azure ML assets can also be deployed directly from VS.Code by
clicking on the Azure ML icon on top right when a YAML file defining an Azure ML asset is opened. For convenience, we
recommend to use the deployment script, however.


## Hints for Development

- The script handling incoming requests is the `score.py` script. To implement your own forecasting algorithm, you need
  to adjust that script.
- This example does not use a pretrained model or a custom environment (in which the scoring script runs). There are
  hints in the deployment script as well as the scoring script explaining how you could use your own models and/or
  environments. For further infos, you can also refer to the [Azure ML documentation](https://docs.microsoft.com/en-us/azure/machine-learning).


## Documentation
[SAP IBP External Forecasting](https://api.sap.com/api/IBP_ExternalForecast_ODataService/overview)
<br/>
[Azure ML documentation](https://docs.microsoft.com/en-us/azure/machine-learning)


## Disclaimer

As always, the code is provided "as is". Feel free to use it but don't blame me if things go wrong!
