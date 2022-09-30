[![REUSE status](https://api.reuse.software/badge/github.com/SAP-samples/integrated-business-planning-external-forecasting-python)](https://api.reuse.software/info/github.com/SAP-samples/integrated-business-planning-external-forecasting-python)

# Using External Forecasting Algorithms via APIs in SAP Integrated Business Planning for Supply Chain 


## Description
The Repo contains three main folders which contain different platforms used to do external forecasting. The user can decide which of the platforms he would like to use for his scenario. This repository serves as a collection of code examples for using APIs that are part of SAP Integrated Business Planning (SAP IBP) for Supply Chain. These samples are not part of the product but created for developers to understand how to consume the APIs or use them to integrate with their processes. The focus is on integrating with external forecasting APIs.

### The SAP_IBP_ExternalForeasting
This folder contains Python scripts which can be downloaded and modified to calculate the forecasts using Python on his local computer or on a hosted environment where Python is running.

###  Google_Vertex_AI 
Some of our experiments with Google Vertex AI are saved in the folder Google_Vertex_AI which can be used as a reference for storing External forecast data on a Big Query table and later use the Vertex AI Platform for calculating the forecasts. A [Blog](https://saviodomnic.medium.com/google-vertex-ai-for-supply-chain-planning-a39039ad9c6b) reflects the use of this code from this repository as reference

### Microsoft_AzureML
Additionally the Microsoft_AzureML folder provides content where the SAP Cloud Integration Suite is used as a middleware to capture the notifcation from SAP IBP, prepare the data and send it over to a Python algorithim that you could implement using Micrisoft's Azure ML Studio. The Python code needs to be exposed as an endpoint and configured in a HTTP request for the SAP Cloud Integration Suite. If you plan to use Micrisift Azure ML as a platform for calculating your forecasts externally, you might consider the artifacts in this folder as a reference.


## Requirements
Python 3 and above.

## Download and Installation
Download the best practice planning view template that fits to your need here.

For more information have a look at [SAP note 3170544.](https://launchpad.support.sap.com/#/notes/3170544).

If you like to visualize your planning view via Excel, then you might intall the Excel add-in and configure the access to an SAP IBP system.

## Additional Information
To learn more about the External Forecasting API, [this blog](https://blogs.sap.com/2022/05/11/how-to-forecast-using-custom-external-algorithms) might be interesting.
If you wish to use Google's Vertex AI, perhaps you may want to [refer here](https://cloud.google.com/vertex-ai).

## Known Issues
None

## How to obtain support 
These sample code repo is provided "as-is", no support is provided. These source codes are not meant for production use, rather it is intented as a reference for learning. They are supposed to help you get started. For additional support, you might post your question in the [SAP Community](https://answers.sap.com/questions/ask.html)
 
## License
Copyright (c) 2022 SAP SE or an SAP affiliate company. All rights reserved. This project is licensed under the Apache Software License, version 2.0 except as noted otherwise in the [LICENSE](LICENSE) file.
