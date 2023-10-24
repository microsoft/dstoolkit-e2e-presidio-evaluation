import pandas as pd
import plotly.express as px
from pathlib import Path
from presidio_evaluator.evaluation import Evaluator
from presidio_evaluator.evaluation import ModelError


class Plotter:
    """
    Plot scores (f2, precision, recall) and errors (false-positivies, false-negatives) 
    for a PII detection model evaluated via Evaluator

    :param model: Instance of a fitted model (of base type BaseModel)
    :param results: results given by evaluator.calculate_score(evaluation_results)
    :param output_folder: folder to store plots and errors in
    :param model_name: name of the model to be used in the plot title
    :param beta: a float with the beta parameter of the F measure,
    which gives more or less weight to precision vs. recall
    """

    def __init__(self, model, results, output_folder: Path, model_name: str, beta: float):
        self.model = model
        self.results = results
        self.output_folder = output_folder
        self.model_name = model_name.replace("/", "-")
        self.errors = results.model_errors
        self.beta = beta

    def plot_scores(self) -> None:
        """
        Plots per-entity recall, precision, or F2 score for evaluated model. 
        :param plot_type: which metric to graph (default is F2 score)
        """
        scores = {}
        scores['entity'] = list(self.results.entity_recall_dict.keys())
        scores['recall'] = list(self.results.entity_recall_dict.values())
        scores['precision'] = list(self.results.entity_precision_dict.values())
        scores['count'] = list(self.results.n_dict.values())
        scores[f"f{self.beta}_score"] = [Evaluator.f_beta(precision=precision, recall=recall, beta=self.beta)
                                for recall, precision in zip(scores['recall'], scores['precision'])]
        df = pd.DataFrame(scores)
        df['model'] = self.model_name
        f2_score = self._plot(df, plot_type="f2_score")
        precision = self._plot(df, plot_type="precision")
        recall = self._plot(df, plot_type="recall")
        return f2_score, precision, recall

    def _plot(self, df, plot_type) -> None:
        fig = px.bar(df, text_auto=".2", y='entity', orientation="h",
                        x=plot_type, color='count', barmode='group', title=f"Per-entity {plot_type} for {self.model_name}")
        fig.update_layout(barmode='group', yaxis={
            'categoryorder': 'total ascending'})
        fig.update_layout(yaxis_title=f"{plot_type}", xaxis_title="PII Entity")
        fig.update_traces(textfont_size=12, textangle=0,
                            textposition="outside", cliponaxis=False)
        fig.update_layout(
            plot_bgcolor="#FFF",
            xaxis=dict(
                title="PII entity",
                linecolor="#BCCCDC",  # Sets color of X-axis line
                showgrid=False  # Removes X-axis grid lines
            ),
            yaxis=dict(
                title=f"{plot_type}",
                linecolor="#BCCCDC",  # Sets color of X-axis line
                showgrid=False  # Removes X-axis grid lines
            ),
        )
        #fig.show()
        return fig

    def plot_most_common_tokens(self) -> None:
        """Graph most common false positive and false negative tokens for each entity."""
        ModelError.most_common_fp_tokens(self.errors)
        fps_frames = []
        fns_frames = []
        for entity in self.model.entity_mapping.values():
            fps_df = ModelError.get_fps_dataframe(self.errors, entity=[entity])
            if fps_df is not None:
                fps_path = self.output_folder / \
                    f"{self.model_name}-{entity}-fps.csv"
                fps_df.to_csv(fps_path)
                fps_frames.append(fps_path)
            fns_df = ModelError.get_fns_dataframe(self.errors, entity=[entity])
            if fns_df is not None:
                fns_path = self.output_folder / \
                    f"{self.model_name}-{entity}-fns.csv"
                fns_df.to_csv(fns_path)
                fns_frames.append(fns_path)

        def group_tokens(df):
            return df.groupby(['token', 'annotation']).size().to_frame(
            ).sort_values([0], ascending=False).head(3).reset_index()

        def generate_graph(title, tokens_df):
            fig = px.histogram(tokens_df, x=0, y="token", orientation='h', color='annotation',
                                title=f"Most common {title} for {self.model_name}")

            fig.update_layout(yaxis_title=f"count", xaxis_title="PII Entity")
            fig.update_traces(textfont_size=12, textangle=0,
                                textposition="outside", cliponaxis=False)
            fig.update_layout(
                plot_bgcolor="#FFF",
                xaxis=dict(
                    title="Count",
                    linecolor="#BCCCDC",  # Sets color of X-axis line
                    showgrid=False  # Removes X-axis grid lines
                ),
                yaxis=dict(
                    title=f"Tokens",
                    linecolor="#BCCCDC",  # Sets color of X-axis line
                    showgrid=False  # Removes X-axis grid lines
                ),
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            # fig.show()
        if len(fps_frames) > 0:
            fps_tokens_df = pd.concat(
                [group_tokens(pd.read_csv(df_path)) for df_path in fps_frames])
            fps_plot = generate_graph(title="false-positives", tokens_df=fps_tokens_df)
        else:
            fps_plot = None
        if len(fns_frames) > 0:
            fns_tokens_df = pd.concat(
                [group_tokens(pd.read_csv(df_path)) for df_path in fns_frames])
            fns_plot = generate_graph(title="false-negatives", tokens_df=fns_tokens_df)
        else:
            fns_plot = None
        return fns_plot, fps_plot
    