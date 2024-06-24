# E2E Presidio evaluation toolkit.

Welcome to the e2e Presidio evaluation toolkit. This project contains two main components: 
- A series of notebook labs for Presidio located in the `notebook` folder, 
- An orchestration project that provides a streamlined end-to-end pipeline for generating sample data from the original dataset and evaluating PII detection of different off-the-shelf models, such as Hugging Face transformers and Azure AI Language, in both the original and generated datasets. This project uses Azure Machine Learning to track and manage different versions of the data and is orchestrated by a Github Action pipeline.

# Project structure
This accelerator provides a modular end-to-end approach for evaluating different PII detection models. The project directory structure is as follows:

- `data_samples`: Contains the sample input data for the project.
- `data-science/`: Contains the data science code and defined Python environment for PII evaluation.
  - `evironment/`: Contains the predefined Conda environment file used for the project.
  - `src/`: Contains the Python source code for the project.
    -`_config`: Configuration files for the project.
    -`addition_reg`: Additional regular expressions used in the project.
    -`data_generator`: Code related to synthetic data generation.
    -`experiment_tracking/`: Code related to tracking and managing experiments.
- `mlops/`: Contains all the YAML files (CLI v2) to orchestrate the evaluation process.
  - `components/`: Contains the individual components of the MLOps pipeline. 
  - `data/`: Contains predefined datasets configuration for MLOps pipeline.
  - `environments/`: Contains environment configuration files for the MLOps pipeline.
  - `evaluation_pipeline.yml`: The defined machine learning pipeline in a YAML file.
-`notebooks`: A series of notebook labs for Presidio
- `README.md`: This file, which provides an overview and instructions for the project.

# Get started
- For the Presidio labs, please refer to the detailed instructions in the [Presidio Labs Setup Walkthrough](docs/presidio_labs_setup_walkthrough.md).
- For the end-to-end evaluation pipeline, follow the detailed instructions in the [Evaluation Pipeline Setup Walkthrough](docs/evaluation_pipeline_setup_walkthrough.md).

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
