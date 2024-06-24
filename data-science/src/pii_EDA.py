# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Evaluates trained ML model using test dataset.
Saves predictions, evaluation results and deploy flag.
"""

import os
import argparse
import logging
from pathlib import Path
from typing import List
from collections import Counter
import matplotlib.pyplot as plt
from copy import deepcopy
import pandas as pd
import mlflow

from presidio_evaluator import InputSample

logging.basicConfig(level=logging.INFO)


def data_analysis(input_data: List[InputSample], title) -> pd.DataFrame():
    """Pure analysis of raw data
    :param transformed_data: folder path of transformed data of raw clinial notes
    :param evaluation_output: folder path of results
    :return: evaluation data in InputSample format"""
    logging.info("Number of samples in evaluation data: %d", len(input_data))
    # Count the number of entities in the test data
    entity_counter = Counter()
    for sample in input_data:
        for tag in sample.tags:
            entity_counter[tag] += 1

    # Visualize the number of entities in the test data
    common_entities = pd.DataFrame(entity_counter.most_common())
    common_entities.columns = ["Entity", "Count"]
    plot = (
        common_entities.query("Entity != 'O'")
        .set_index("Entity")
        .plot(kind="bar", title=f"{title}", figsize=(15, 5), legend=True, color="gray")
    )
    plt.xticks(rotation=45, ha='right')  # Rotate labels
    plt.tight_layout()  # Adjust layout
    mlflow.log_figure(plot.figure, f"{title}.png")
    # Close the plot to free up memory
    plt.close(plot.figure)
    logging.info("Number of sample in dataset: %d", len(input_data))
    logging.info("Count per entity: %s", entity_counter.most_common())
    logging.info("Min and max number of tokens in dataset")
    logging.info(f"Min: {min([len(sample.tokens) for sample in input_data])},")
    logging.info(f"Max: {max([len(sample.tokens) for sample in input_data])}")
    logging.info("Min and max sentence length in dataset:")
    logging.info("Min: {min([len(sample.full_text) for sample in evaluation_data])}")
    logging.info("Max: {max([len(sample.full_text) for sample in evaluation_data])}")
    return common_entities


def parse_args():
    """Parse input arguments"""

    parser = argparse.ArgumentParser("pii_eda")
    parser.add_argument(
        "--raw-data", type=str, help="Path of raw data folder"
    )
    parser.add_argument("--raw-file-name", type=str, help="Name of raw data file")
    args = parser.parse_args()

    return args

def main(args):
    """Read evaluation dataset, evaluate PII solution and save result"""
    # Load the test data
    data_path = os.path.join(args.raw_data, args.raw_file_name)
    data = InputSample.read_dataset_json(data_path)

    data_analysis(data, "PII_EDA")


if __name__ == "__main__":

    args = parse_args()

    mlflow.start_run()
    lines = [
        f"Raw data: {args.raw_data}",
        f"Raw file name: {args.raw_file_name}"
    ]

    for line in lines:
        logging.info(line)
    main(args)
    mlflow.end_run()
