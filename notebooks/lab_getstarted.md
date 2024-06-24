# Notebooks

This folder contains a series of Jupyter notebooks that demonstrate various aspects of using Presidio for data privacy and security. These notebooks serve as interactive tutorials and provide hands-on experience with the tool.

## Structure
- `001-lab-pii-deidentification-with-presidio.ipynb`: This notebook provides an introduction to using Presidio for data anonymization. It covers the basics of detecting and anonymizing personally identifiable information (PII) in text data.

- `002-lab-data-generation-with-presidio.ipynb`: This notebook showcases how to generate synthetic data using Presidio. It demonstrates how to create new data that mimics the structure and statistical properties of the original data, but without any real PII.

## Getting Started

To run these notebooks, you need to have python and jupyter installed on your machine. You can install it by the steps below:

```bash
# Create conda environment
conda create --name presidio-lab python=3.9
# Activate conda environment
conda activate presidio-lab
# Install dependencies
pip install -r requirements.txt
