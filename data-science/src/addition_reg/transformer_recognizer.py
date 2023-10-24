import logging
import copy
from typing import Optional, List, Tuple, Set
import torch
from presidio_analyzer import (
    RecognizerResult,
    EntityRecognizer,
    AnalysisExplanation,
)
from presidio_analyzer.nlp_engine import NlpArtifacts
logger = logging.getLogger("presidio-analyzer")

try:
    from transformers import (
        AutoTokenizer,
        AutoModelForTokenClassification,
        pipeline,
        models,
        TokenClassificationPipeline
    )

except ImportError:
    logger.error("transformers is not installed")


class TransformersRecognizer(EntityRecognizer):
    """
    Wrapper for a transformers model, if needed to be used within Presidio Analyzer.
    :example:
    >from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
    >transformers_recognizer = TransformersRecognizer()
    >transformers_recognizer.load()
    >registry = RecognizerRegistry()
    >registry.add_recognizer(transformers_recognizer)
    >analyzer = AnalyzerEngine(registry=registry)
    >results = analyzer.analyze(
    >    "My name is Christopher and I live in Irbid.",
    >    language="en",
    >    return_decision_process=True,
    >)
    >for result in results:
    >    print(result)
    >    print(result.analysis_explanation)
    """

    def __init__(
        self,
        supported_entities: Optional[List[str]
                                     ],
        check_label_groups: Optional[Tuple[Set, Set]] = None,
        pipeline: Optional[TokenClassificationPipeline] = None,
        model_path: Optional[str] = None,
    ):
        self.pipeline = pipeline
        self.model_path = model_path
        self.check_label_groups = check_label_groups

        super().__init__(
            supported_entities=supported_entities, name="Transformers Analytics",)
        self.is_loaded = False

    def load_transformer(self, **kwargs) -> None:
        """Load the model, and additional key arguments
        """
        self.entity_mapping = kwargs.get('DATASET_TO_PRESIDIO_MAPPING', {})
        self.model_to_presidio_mapping = kwargs.get(
            'MODEL_TO_PRESIDIO_MAPPING', {})
        self.ignore_labels = kwargs.get('LABELS_TO_IGNORE', ["O"])
        self.aggregation_mechanism = kwargs.get(
            'SUB_WORD_AGGREGATION', 'simple')
        self.default_explanation = kwargs.get('DEFAULT_EXPLANATION', None)

        if not self.pipeline:
            if not self.model_path:
                self.model_path = 'obi/deid_roberta_i2b2'
                logger.warning(
                    f"Both 'model' and 'model_path' arguments are None. Using default model_path={self.model_path}")

        self._load_pipeline()

    def _load_pipeline(self) -> None:
        """Initialize NER transformers pipeline using the model_path provided"""

        logging.debug(
            f"Initializing NER pipeline using {self.model_path} path")
        device = 0 if torch.cuda.is_available() else -1
        self.pipeline = pipeline(
            "ner",
            model=AutoModelForTokenClassification.from_pretrained(
                self.model_path),
            tokenizer=AutoTokenizer.from_pretrained(self.model_path),
            # Will attempt to group sub-entities to word level
            aggregation_strategy=self.aggregation_mechanism,
            device=device,
            framework='pt',
            ignore_labels=self.ignore_labels
        )

        self.is_loaded = True

    def get_supported_entities(self) -> List[str]:
        """
        Return supported entities by this model.
        :return: List of the supported entities.
        """
        return self.supported_entities

    # Class to use transformers with Presidio as an external recognizer.
    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts = None
    ) -> List[RecognizerResult]:
        """
        Analyze text using transformers model to produce NER tagging.
        :param text(str) : The text for analysis.
        :param entities(List[str]): Not working properly for this recognizer.
        :param nlp_artifacts: Not used by this recognizer.
        :return: The list of Presidio RecognizerResult constructed from the recognized
            transformers detections.
        """

        results = list()
        # Run transformer model on the provided text
        ner_results = self._get_ner_results_for_text(text)

        for res in ner_results:
            res['entity_group'] = self.__check_label_transformer(
                res["entity_group"])
            textual_explanation = self.default_explanation.format(
                res["entity_group"]
            )
            explanation = self.build_transformers_explanation(
                round(res["score"], 2), textual_explanation, res["word"]
            )
            transformers_result = self._convert_to_recognizer_result(
                res, explanation
            )

            results.append(transformers_result)

        return results

    @ staticmethod
    def split_text_to_word_chunks(input_length: int, chunk_length: int, overlap_length: int) -> List[List]:
        """The function calculates chunks of text with size chunk_length. Each chunk has overlap_length number of
        words to create context and continuity for the model

        Args:
            input_length (int): Length of input_ids for a given text
            chunk_length (int): Length of each chunk of input_ids. Should match the max input length of the transformer model
            overlap_length (int): Number of overlapping words in each chunk

        Returns:
            List[List]: List of start and end position for each text chunk
        """
        return [[i, min([i+chunk_length, input_length])] for i in range(0, input_length, chunk_length-overlap_length)]

    def _get_ner_results_for_text(self, text: str) -> List[dict]:
        """The function runs model inference on the provided text.
        If length of text > max_length tokens, the text is split into chunks with n = 40 overlapping characters
        The results are aggregated and duplicates are removed.

        Args:
            text (str): The text to run inference on

        Returns:
            List[dict]: List of NER predictions on the word level
        """

        model_max_length = self.pipeline.tokenizer.model_max_length
        # calculate inputs based on the text
        text_length = len(text)
        if text_length <= model_max_length*2:
            return self.pipeline(text)

        # split text into chunks
        logger.info(
            f'splitting the text into chunks, length {text_length} > {model_max_length*2}')
        predictions = list()
        chunk_indexes = TransformersRecognizer.split_text_to_word_chunks(
            text_length, model_max_length*2, 40)
        for chunk in chunk_indexes:
            chunk_text = text[chunk[0]:chunk[1]]
            chunk_preds = self.pipeline(chunk_text)

            # align indexes to match full text - add to each position the index of chunk's start
            aligned_predictions = list()
            for prediction in chunk_preds:
                prediction_tmp = copy.deepcopy(prediction)
                prediction_tmp['start'] += chunk[0]
                prediction_tmp['end'] += chunk[0]
                aligned_predictions.append(prediction_tmp)

            predictions.extend(aligned_predictions)

        # remove duplicates
        predictions = [dict(t)
                       for t in {tuple(d.items()) for d in predictions}]
        return predictions

    def _convert_to_recognizer_result(self, res, explanation) -> RecognizerResult:

        transformers_results = RecognizerResult(
            entity_type=res['entity_group'],
            start=res["start"],
            end=res["end"],
            score=round(res["score"], 2),
            analysis_explanation=explanation,
        )

        return transformers_results

    def build_transformers_explanation(
        self, original_score: float, explanation: str, pattern: str,
    ) -> AnalysisExplanation:
        """
        Create explanation for why this result was detected.
        :param original_score: Score given by this recognizer
        :param explanation: Explanation string
        :return:
        """
        explanation = AnalysisExplanation(
            recognizer=self.__class__.__name__,
            original_score=original_score,
            textual_explanation=explanation,
            pattern=pattern
        )
        return explanation

    def __check_label_transformer(self, label: str) -> bool:
        """The function validates the predicted label and converts the string into a Presidio representation

        Args:
            label (str): Predicted label by the model

        Returns:
            bool: If label is found in mapping dictionary and supported by Presidio entities
        """
        if label == 'O':
            return label
        # convert model label to presidio label
        entity = self.model_to_presidio_mapping.get(label, None)

        if entity is None:
            logger.warning(
                f"Found unrecognized label {label}, returning entity as 'O'")
            return "O"

        if entity not in self.supported_entities:
            logger.warning(
                f"Found entity {entity} which is not supported by Presidio")
            return "O"
        return entity


if __name__ == "__main__":

    from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

    transformers_recognizer = (
        TransformersRecognizer()
    )  # This would download a large (~500Mb) model on the first run

    registry = RecognizerRegistry()
    registry.add_recognizer(transformers_recognizer)

    analyzer = AnalyzerEngine(registry=registry)

    results = analyzer.analyze(
        "My name is Christopher and I live in Irbid.",
        language="en",
        return_decision_process=True,
    )
    for result in results:
        print(result)
        print(result.analysis_explanation)
