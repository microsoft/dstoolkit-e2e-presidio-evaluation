# Introduction
This walkthrough aims to set up your own evaluation process as quickly and easily as possible. 
## Local run
## Run in Azure Machine Learning
### 1. Prerequis
1. An Azure subscription. If you don't have an Azure subscription, create a free account before you begin.
2. Azure CLI
3. GitHub client
4. Git bash, WSL, or another shell script editor on your local machine
### 2. Configure The GitHub Environment
1. Replicate dstoolkit-e2e-presidio-evaluation repositories in your GitHub organization
Go to ... to fork the repository in your Github org. 
2. Configure GitHub Action Secrets
This step create a service principal and github secrets to allow the GitHub action workflows to create and interact with Azure Machine Learning Workspace resources
From the command line, execute the following Azure CLI command with your choice of a service principal name:

> `# az ad sp create-for-rbac --name <service_principal_name> --role contributor --scopes /subscriptions/<subscription_id> --sdk-auth`

You will get output similar to below:
>`{`  
> `"clientId": "<service principal client id>",`  
> `"clientSecret": "<service principal client secret>",`  
> `"subscriptionId": "<Azure subscription id>",`  
> `"tenantId": "<Azure tenant id>",`  
> `"activeDirectoryEndpointUrl": "https://login.microsoftonline.com",`  
> `"resourceManagerEndpointUrl": "https://management.azure.com/",`  
> `"activeDirectoryGraphResourceId": "https://graph.windows.net/",`  
> `"sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",`  
> `"galleryEndpointUrl": "https://gallery.azure.com/",`  
> `"managementEndpointUrl": "https://management.core.windows.net/"`  
> `}`

Copy all of this output, braces included
