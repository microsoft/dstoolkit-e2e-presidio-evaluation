# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Evaluates trained ML model using test dataset.
Saves predictions, evaluation results and deploy flag.
"""

import os
import argparse
import logging
import json
import time
from pathlib import Path
from typing import List
from collections import Counter
import matplotlib.pyplot as plt
from copy import deepcopy
import pandas as pd
import mlflow

from presidio_evaluator import InputSample
from presidio_evaluator.evaluation import Evaluator
from presidio_evaluator.models import PresidioAnalyzerWrapper
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

from _config import _ner_model_config_data_sample2 as _ner_model_config
from addition_reg.transformer_recognizer import TransformersRecognizer
from experiment_tracking.experiment_tracker import LocalExperimentTracker
from plotter import Plotter

logging.basicConfig(level=logging.INFO)


def parse_args():
    """Parse input arguments"""

    parser = argparse.ArgumentParser("evaluate")
    parser.add_argument(
        "--raw-data", type=str, help="Path of raw data folder"
    )
    parser.add_argument("--raw-file-name", type=str, help="Name of raw data file")
    parser.add_argument("--evaluation-output", type=str, help="Path of eval results")
    parser.add_argument(
        "--beta-value", type=float, default=2, help="Beta parameter for F measure"
    )
    parser.add_argument(
        "--experiment-name", default="presidio", help="Name of the experiment"
    )

    args = parser.parse_args()

    return args


def initialize_analyzer_engine(model_config=None) -> PresidioAnalyzerWrapper():
    """
    Initialize analyzer engine based on model configuration
    :param model_config: model configuration dictionary from _ner_model_config
    :return: PresidioAnalyzerWrapper() object
    """
    entity_mapping = _ner_model_config.PRESIDIO_CONFIGURATION.get(
        "DATASET_TO_PRESIDIO_MAPPING"
    )
    if model_config is not None:
        transformers_recognizer = TransformersRecognizer(
            model_path=model_config["DEFAULT_MODEL_PATH"],
            supported_entities=model_config["PRESIDIO_SUPPORTED_ENTITIES"],
        )
        # This would download a large (~500Mb) model on the first run
        transformers_recognizer.load_transformer(**model_config)
        # Add transformers model to the registry
        registry = RecognizerRegistry()
        registry.add_recognizer(transformers_recognizer)
        analyzer = AnalyzerEngine(registry=registry)
        wrapper = PresidioAnalyzerWrapper(
            analyzer_engine=analyzer,
            labeling_scheme="IO",
            entity_mapping=entity_mapping,
        )
        return wrapper
    else:  # Default
        return PresidioAnalyzerWrapper(entity_mapping=entity_mapping)


def evaluate_experiment(
    experiment_name: str,
    evaluation_data: List[InputSample],
    wrapper: PresidioAnalyzerWrapper,
    beta: float,
):
    """
    Evaluate a Presidio analyzer based on the evaluation data
    :param experiment_name: The name of the experiment
    :param evaluation_data: evaluation data in InputSample format
    :param experiment_dir: path of experiment directory
    :return: evaluation results
    """
    start_time = time.time()
    logging.info(f"Start evaluating the model {experiment_name}")
    # Initialize experiment tracker
    # Set up experiment tracking
    experiment_dir = Path(args.evaluation_output)
    experiment = LocalExperimentTracker(experiment_dir, experiment_name)
    # Run evalutation
    evaluator = Evaluator(model=wrapper)
    # dataset = Evaluator.align_entity_types(
    #     deepcopy(evaluation_data), entities_mapping=PresidioAnalyzerWrapper.presidio_entities_map
    # )
    print(evaluation_data[132].tags)
    print(evaluation_data[133].tags)
    evaluation_results = evaluator.evaluate_all(evaluation_data)
    results = evaluator.calculate_score(evaluation_results, beta=beta)
    end_time = time.time()
    execution_time = end_time - start_time
    # Plot the results
    plotter = Plotter(
        model=wrapper,
        results=results,
        output_folder=experiment_dir,
        model_name=experiment_name,
        beta=2,
    )
    f2_score, precision, recall = plotter.plot_scores()
    fns_plot, fps_plot = plotter.plot_most_common_tokens()
    if f2_score is not None:
        f2_score.write_image(
            os.path.join(experiment_dir, f"{experiment_name}/f2_score.png")
        )
    if precision is not None:
        precision.write_image(
            os.path.join(experiment_dir, f"{experiment_name}/precision.png")
        )
    if recall is not None:
        recall.write_image(
            os.path.join(experiment_dir, f"{experiment_name}/recall.png")
        )
    if fns_plot is not None:
        fns_plot.write_image(
            os.path.join(experiment_dir, f"{experiment_name}/fns_plot.png")
        )
    if fps_plot is not None:
        fps_plot.write_image(
            os.path.join(experiment_dir, f"{experiment_name}/fps_plot.png")
        )

    entities, confmatrix = results.to_confusion_matrix()

    experiment.log_confusion_matrix_table(matrix=confmatrix, labels=entities)
    # log model errors for future analysis
    errors = results.model_errors
    experiment.log_errors(errors)
    # Log single model evaluation output
    single_model_output = results.to_log()
    single_model_output["model_name"] = experiment_name
    single_model_output["execution_time"] = execution_time
    with open(f"{experiment_dir}/{experiment_name}/evaluation_result.json", "w+") as f:
        json.dump(single_model_output, f)
    mlflow.log_artifacts(f"{experiment_dir}/{experiment_name}")
    mlflow.log_metric(f"f{beta}_score", results.to_log()["pii_f"])


def plot_result(df_result):
    # y_axis_selected = [i for i in df_result.columns if i.str.contains('precision|recall|pii_f')]
    y_axis_selected = df_result.filter(regex="precision|recall|pii_f").columns.tolist()
    # Set the plot style
    plt.style.use("ggplot")
    # Create the bar chart
    fig, ax = plt.subplots(figsize=(8, 6))
    df_result.plot(x="model_name", y=y_axis_selected, kind="bar", ax=ax)
    ax.set_ylabel("Score")
    ax.set_ylim([0, 1])
    ax.set_title("Comparison of Model Performance")
    ax.set_xticklabels(df_result["model_name"])
    ax.grid(axis="y", alpha=0.5)
    mlflow.log_figure(fig.figure, "compare_performance.png")

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
        .plot(kind="bar", title=f"{title}", figsize=(15, 5), legend=True)
    )
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


def main(args):
    """Read evaluation dataset, evaluate PII solution and save result"""
    # Load the test data
    data_path = os.path.join(args.raw_data, args.raw_file_name)
    data = InputSample.read_dataset_json(data_path)

    if args.experiment_name == "Presidio":
        # Evaluate presidio based model
        logging.info("Running evaluation for model presidio")
        wrapper = initialize_analyzer_engine()
    elif args.experiment_name == "StanfordAIMI":
        logging.info("Running evaluation for stanford model")
        wrapper = initialize_analyzer_engine(_ner_model_config.STANFORD_CONFIGURATION)
    elif args.experiment_name == "BertDEID":
        logging.info("Running evaluation for deid_roberta_i2b2 model")
        wrapper = initialize_analyzer_engine(_ner_model_config.BERT_DEID_CONFIGURATION)
    else:
        raise ValueError(f"Experiment name {args.experiment_name} is not supported")
    evaluate_experiment(args.experiment_name, deepcopy(data), wrapper, args.beta_value)


if __name__ == "__main__":

    mlflow.start_run()

    args = parse_args()

    lines = [
        f"Raw data: {args.raw_data}",
        f"Raw file name: {args.raw_file_name}"
        f"Evaluation result path: {args.evaluation_output}",
        f"Experiment name: {args.experiment_name}",
        f"Beta: {args.beta_value}",
    ]

    for line in lines:
        logging.info(line)
    main(args)
    mlflow.end_run()
