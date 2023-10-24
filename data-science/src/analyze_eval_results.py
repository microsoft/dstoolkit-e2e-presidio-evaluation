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
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import mlflow


def parse_args():
    """Parse input arguments"""

    parser = argparse.ArgumentParser("evaluate")
    parser.add_argument(
        "--presidio-output", type=str, help="Path of presidio evaluation output"
    )
    parser.add_argument(
        "--stanford-output", type=str, help="Path of stanford evaluation output"
    )
    parser.add_argument(
        "--bert-deid-output", type=str, help="Path of bert-deid evaluation output"
    )
    parser.add_argument(
        "--final-output-path", default="str", help="Path of final evaluation output"
    )

    args = parser.parse_args()

    return args


def load_result(json_path):
    with open(json_path, "r") as f:
        result = json.load(f)
    return result


def plot_results(df_result, metric):
    ylabel = metric
    data = df_result.filter(regex=f"{ylabel}|model_name").set_index("model_name")
    if metric != "execution_time":
        data.columns = data.columns.str.replace(f"_{metric}", "")
        formatter = lambda x: f"{x:.0%}"
    else:
        formatter = lambda x: f"{x:.2f}"
    labels = data.columns
    model_names = data.index
    # Define the figure and axes
    fig, ax = plt.subplots(figsize=(10, 6))
    # Define the color map
    cmap = plt.get_cmap("tab20")

    # Define the width of each bar
    bar_width = 0.2

    # Define the y positions of the bars
    y_pos = np.arange(len(labels))

    # Plot each group of bars
    for i, model_name in enumerate(model_names):
        ax.barh(
            y_pos + i * bar_width,
            data.loc[model_name],
            height=bar_width,
            label=model_name,
            color=cmap(i),
        )

        # Add percentage labels above each bar
        for j, val in enumerate(data.loc[model_name]):
            ax.text(
                val + 0.01,
                y_pos[j] + i * bar_width,
                f"{formatter(val)}",
                va="center",
                fontsize=7,
                color="black",
            )
    # Set the x-axis label and limits
    ax.set_xlabel(metric, color="black")
    if metric != "execution_time":
        # Set the y-axis labels and tick marks
        ax.set_yticks(y_pos + bar_width * (len(labels) - 1) / 2)
        ax.set_yticklabels(labels, fontsize=7, color="black")
        ax.set_xlim([0, 1])
        # Set the x-axis label and limits
        ax.set_xlabel(f"{metric} (%)", color="black")
    else:
        ax.set_xlabel(f"Execution time (s)", color="black")

    ax.set_ylabel("Entity", color="black")

    # Add a legend
    ax.legend()

    # Return plot
    return fig


def main(args):
    # Load presidio output
    presidio_result = load_result(
        os.path.join(args.presidio_output, "Presidio", "evaluation_result.json")
    )
    # Load stanford output
    stanford_result = load_result(
        os.path.join(args.stanford_output, "StanfordAIMI", "evaluation_result.json")
    )
    # Load bert-deid output
    bert_deid_result = load_result(
        os.path.join(args.bert_deid_output, "BertDEID", "evaluation_result.json")
    )
    df_result = pd.DataFrame([presidio_result, stanford_result, bert_deid_result])
    fig_precision = plot_results(df_result, "precision")
    fig_recall = plot_results(df_result, "recall")
    fig_execution_time = plot_results(df_result, "execution_time")
    if fig_precision is not None:
        fig_precision.savefig(
            os.path.join(args.final_output_path, "precision_score.png")
        )
    if fig_recall is not None:
        fig_recall.savefig(os.path.join(args.final_output_path, "recall_score.png"))
    if fig_execution_time is not None:
        fig_execution_time.savefig(
            os.path.join(args.final_output_path, "execution_time.png")
        )

    mlflow.log_artifacts(args.final_output_path)


if __name__ == "__main__":

    mlflow.start_run()

    args = parse_args()

    lines = [
        f"Presidio evaluation output: {args.presidio_output}",
        f"Stanfort evaluation output: {args.stanford_output}",
        f"bert_deid_output: {args.bert_deid_output}",
        f"Output path: {args.final_output_path}",
    ]

    for line in lines:
        logging.info(line)
    main(args)
    mlflow.end_run()
