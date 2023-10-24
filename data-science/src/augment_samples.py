# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Generate the samples from the orginal data
"""

import os
import argparse
from pathlib import Path
import json
import logging
import mlflow

from presidio_evaluator import InputSample

from _config._data_augmented_config import (
    DATASET_TO_FAKER,
    FAKER_TO_PRESIDIO_TRANSLATION,
)
from data_generator.data_generator import DataGenerator

logging.basicConfig(level=logging.INFO)


def parse_args():
    """Parse input arguments"""

    parser = argparse.ArgumentParser("data_augment")
    parser.add_argument("--raw-data", type=str, help="Path to raw data")
    parser.add_argument(
        "--number-samples", type=int, help="Number of samples to generate"
    )
    parser.add_argument(
        "--output-path", type=str, help="Path to save output of the job"
    )

    args = parser.parse_args()
    return args


def main(args):
    """Read orginal data, augmente them, and save as json file"""
    orginal_data = InputSample.read_dataset_json(Path(args.raw_data, "input_samples.json"))
    print(len(orginal_data))
    # data_analysis(orginal_data, "original data")
    data_generator = DataGenerator(
        input_samples=orginal_data,
        dataset_to_faker_config=DATASET_TO_FAKER,
        faker_to_presidio_config=FAKER_TO_PRESIDIO_TRANSLATION,
        number_of_samples=args.number_samples,
    )

    augmented_data = data_generator.data_generate()
    # Save the transformed data in InputSample format to json file
    json_dataset = [example.to_dict() for example in augmented_data]
    output_path = os.path.join(args.output_path, "augmented_samples.json")
    with open("{}".format(output_path), "w+", encoding="utf-8") as f:
        json.dump(json_dataset, f, ensure_ascii=False, indent=4)
    mlflow.log_metric("Orginal data size", len(orginal_data))
    mlflow.log_metric("Augemented data size", len(augmented_data))


if __name__ == "__main__":

    mlflow.start_run()

    # ---------- Parse Arguments ----------- #
    # -------------------------------------- #

    args = parse_args()

    lines = [
        f"Raw data path: {args.raw_data}",
        f"Output path: {args.output_path}",
        f"Number of sample to generate: {args.number_samples}",
    ]

    for line in lines:
        logging.info(line)

    main(args)

    mlflow.end_run()
