# E2E PII evaluation in AzureML demo

Welcome to the e2e Presidio evaluation toolkit. This project seamlessly integrates with Presidio, providing a streamlined end-to-end pipeline for generating sample data from the original dataset and evaluating PII detection of different off-the-shelf models (such as Presidio and Azure Languages Service) in both the original and generated datasets. This project uses Azure Machine Learning to track and manage different versions of the data and is orchestrated by a Github Action pipeline.

![architecture](/docs/images/e2e%20evaluation%20architecture%20diagram.png)

# Project structure
This accelerator provides a modular end-to-end approach for evaluating different PII detection models. The project directory structure is as follows:

- `data_samples/sample_set1`: Contains the sample input data for the project.
  - `input_samples.json`: The sample input data file.
- `data-science/`: Data science code and defined python environment for PII evaluation 
  - `evironment/`: Predefined conda environment file used for project
  - `src/`: python source code for the project.
    -`_config/`: configuration files 
    -`addition_reg/`: 
    -`data_generator/`: 
    -`experiment_tracking/`:
- `mlops/`: all the yml file (CLI v2) to orchestrate evaluation process
  - `components/`: this is the component directory which contains the 
  - `data/`: predefined dataset in yml file
  - `environments/`: 
  - `evaluation_pipeline.yml`: the defined machine learning pipeline in yaml file
- `README.md`: This file.

# Get started
This project is supported to run in both local and Azure ML environment. All pipelines are orchestrated by GitHub Action. Follow the walkthrough [here](docs/setup_walkthrough.md) for detailed instructions.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
