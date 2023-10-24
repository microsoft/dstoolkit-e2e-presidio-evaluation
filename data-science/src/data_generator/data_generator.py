# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.



import logging
from typing import List
import pandas as pd
from tqdm import tqdm
import requests
from copy import deepcopy
from functools import reduce
from faker.providers import BaseProvider

from presidio_evaluator import InputSample, Span
from presidio_evaluator.data_generator import PresidioDataGenerator
from presidio_evaluator.data_generator.faker_extensions import (
    RecordsFaker,
    IpAddressProvider,
    NationalityProvider,
    OrganizationProvider,
    AgeProvider,
    AddressProviderNew,
    PhoneNumberProviderNew,
    FakerSpansResult,
)

logging.basicConfig(level=logging.INFO)


class DataGenerator:
    def __init__(
        self,
        input_samples: List[InputSample],
        dataset_to_faker_config: dict[str, str],
        faker_to_presidio_config: dict[str, str],
        number_of_samples: int = 5,
    ):
        self.input_samples = input_samples
        self.dataset_to_faker_config = dataset_to_faker_config
        self.faker_to_presidio_config = faker_to_presidio_config
        self.number_of_samples = number_of_samples

    @staticmethod
    def apply_mask(text: str, span: Span, shift: int, dataset_to_faker_config):
        """ """
        if span.entity_type != "DATE":
            entity_name = dataset_to_faker_config.get(span.entity_type, "unknown")
        else:
            return text, shift
        if entity_name == "unknown":
            logging.warning(f"Entity {span.entity_type} not found in faker")

        new_text = f" {{{{{entity_name}}}}} ".join(
            [
                text[: span.start_position + shift - 1],
                text[span.end_position + shift + 1 :],
            ]
        )
        new_shift = len(entity_name) - len(span.entity_value) + shift + 4
        return new_text, new_shift

    def mask_text(self, text: str, spans: List):
        """Replace annotated text with the relevant entity name

        :param text: The source text to be replaces
        :type text: str
        :param spans: List of spans which contain the entity type, start and end position of the entity value
        :type spans: List[Span]
        :shift counter storing shifts in position based on the difference between the length of the entity values and the length of the entity
        :type shift: int
        """
        local_spans = spans.copy()
        local_spans.sort(key=lambda x: x.start_position, reverse=False)
        local_text = text
        shift = 0
        if len(spans) == 0:
            return text

        for t_span in local_spans:
            local_text, shift = self.apply_mask(
                local_text, t_span, shift, self.dataset_to_faker_config
            )
        return local_text

    @staticmethod
    def update_entity_types(
        dataset: List[FakerSpansResult], entity_mapping: dict[str, str]
    ):
        """Replace entity types using a translator dictionary."""
        modified_dataset = []
        for sample in dataset:
            # update entity types on spans
            for span in sample.spans:
                span.type = entity_mapping.get(span.type, span.type)
        modified_dataset.append(sample)
        return modified_dataset

    @staticmethod
    def align_spans(original_spans, fake_spans, entity_to_align="DATE"):
        """
        Add DATE_TIME entities to the list of spans since we didn't generate new data for it
        The way to do this is to use the template_id as the common key. We will iterate through the spans and calculate
        the shif i.e the difference between the original span value and the fake span value. After which we will the shift to the
        original DATE spans.
        """
        if len(original_spans) == len(fake_spans):
            return fake_spans

        original_spans.sort(key=lambda x: x.start_position, reverse=False)
        fake_spans.sort(key=lambda x: x.start_position, reverse=False)
        fake_spans = deepcopy(fake_spans)
        shift = 0
        for i, span in enumerate(original_spans):
            if span.entity_type == entity_to_align:
                missing_span = deepcopy(span)
                missing_span.start_position += shift
                missing_span.end_position += shift
                fake_spans.insert(i, missing_span)
            if span.entity_type in (
                [
                    "PATIENT",
                    "DOCTOR",
                    "HOSPITAL",
                    "IDNUM",
                    "MEDICALRECORD",
                    "DEVICE",
                    "ORGANIZATION",
                ]
            ):
                try:
                    fake_spans[i].entity_type = span.entity_type
                except:
                    print(i, span.entity_type, len(original_spans), len(fake_spans))

            shift += len(fake_spans[i].entity_value) - len(span.entity_value)
        if len(original_spans) != len(fake_spans):
            print("failed to align spans")
            print(len(original_spans), len(fake_spans))
        return fake_spans

    def data_generate(self):
        """
        In this case the actual PII will be replaced with {{faker provider}}
        example: "Johhny lives in NY" will become "John lives in {{city}}"
        """
        all_templates = list()
        for _, sample in tqdm(enumerate(self.input_samples)):
            template = self.mask_text(sample.full_text, sample.spans)
            all_templates.append(template)

        # Read FakeNameGenerator data
        fake_data_df = pd.read_csv(
            "https://raw.githubusercontent.com/microsoft/presidio-research/master/presidio_evaluator/data_generator/raw_data/FakeNameGenerator.com_3000.csv"
        )
        # Convert column names to lower case
        fake_data_df = PresidioDataGenerator.update_fake_name_generator_df(fake_data_df)
        fake = RecordsFaker(fake_data_df, local="en_US")
        data_generator = PresidioDataGenerator(custom_faker=fake, lower_case_ratio=0)
        # Add presidio and faker providers
        provider_list = [
            HospitalProvider,
            IpAddressProvider,
            NationalityProvider,
            AgeProvider,
            AddressProviderNew,
            PhoneNumberProviderNew,
            OrganizationProvider,
        ]
        for provider in provider_list:
            fake.add_provider(provider)
        # Gererate fake data
        fake_records = data_generator.generate_fake_data(
            templates=all_templates, n_samples=5
        )
        fake_records = list(fake_records)
        # fake_records_modified = self.update_entity_types(fake_records,
        #                                                  entity_mapping=self.faker_to_presidio_config)
        # Convert to InputSample format
        fake_input_samples = [
            InputSample.from_faker_spans_result(faker_spans_result=fake_record)
            for fake_record in tqdm(fake_records)
        ]
        # Keep only fake samples which don't have an error
        bad_indexes = list()
        for i, fake_record in enumerate(fake_input_samples):
            matching_span = deepcopy(self.input_samples[fake_record.template_id])
            # check if the spans were parsed correctly and only the DATE span is missing
            if len([x for x in matching_span.spans if x.entity_type == "DATE"]) + len(
                fake_record.spans
            ) != len(matching_span.spans):
                if len(fake_record.spans) == len(matching_span.spans):
                    continue
                # append indexes and templates where the Spans are not parsed correctly and ignore those templates
                bad_indexes.append(
                    {"fake_index": i, "original_dataset_ind": fake_record.template_id}
                )
                continue
            # add the missing DATE spans to the fake template
            aligned_spans = self.align_spans(
                matching_span.spans, fake_input_samples[i].spans, entity_to_align="DATE"
            )
            fake_input_samples[i].spans = deepcopy(aligned_spans)

        bad_index_list = [x["fake_index"] for x in bad_indexes]

        # remove the samples that failed to parse correctly
        for index in sorted(bad_index_list, reverse=True):
            del fake_input_samples[index]
        return fake_input_samples


class HospitalProvider(BaseProvider):
    def __init__(self, generator, hospital_file: str = None):
        super().__init__(generator=generator)
        self.hospital_list = self.load_hospitals(hospital_file)

    def load_hospitals(self, hospital_file: str):
        """Loads a list of hospital names based in the US.
        If a static file with hospital names is provided, the hospital names should be under a
        column named "name". If a nothing is provided then,
        the information will be retrieved from WikiData.

        :param hospital_file: Path to static file containing hospital names
        :type hospital_file: str
        """
        if hospital_file:
            self.hospitals = pd.read_csv(hospital_file)
            if "name" not in self.hospitals:
                print(
                    "Unable to retrieve hospital names, file is missing column named 'name'"
                )
                self.hospitals = list()
                return
            self.hospitals = self.hospitals["name"].to_list()
        else:
            self.hospitals = self.load_wiki_hospitals()

    def hospital_name(self):
        return self.random_element(self.hospitals)

    def load_wiki_hospitals(
        self,
    ):
        """Executes a query on WikiData and extracts a list of US based hospitals"""
        url = "https://query.wikidata.org/sparql"
        query = """
        SELECT DISTINCT ?label_en
        WHERE 
        { ?item wdt:P31/wdt:P279* wd:Q16917; wdt:P17 wd:Q30
        OPTIONAL { ?item p:P31/ps:P31 wd:Q64578911 . BIND(wd:Q64578911 as ?status1) } BIND(COALESCE(?status1,wd:Q64624840) as ?status)
        OPTIONAL { ?item wdt:P131/wdt:P131* ?ac . ?ac wdt:P5087 [] }
        optional { ?item rdfs:label ?label_en FILTER((LANG(?label_en)) = "en") }   
        }

        """
        r = requests.get(url, params={"format": "json", "query": query})
        if r.status_code != 200:
            print("Unable to read hospitals from WikiData, returning an empty list")
            return list()
        data = r.json()
        bindings = data["results"].get("bindings", [])
        hospitals = [self.deep_get(x, ["label_en", "value"]) for x in bindings]
        hospitals = [x for x in hospitals if "no key" not in x]
        return hospitals

    def deep_get(self, dictionary: dict, keys: List[str]):
        """Retrieve values from a nested dictionary for specific nested keys
        > example:
        > d = {"key_a":1, "key_b":{"key_c":2}}
        > deep_get(d, ["key_b","key_c"])
        > ... 2

        > deep_get(d, ["key_z"])
        > ... "no key key_z"
        :param dictionary: Nested dictionary to search for keys
        :type dictionary: dict
        :param keys: list of keys, each value should represent the next level of nesting
        :type keys: List
        :return: The value of the nested keys
        """

        return reduce(
            lambda dictionary, key: dictionary.get(key, f"no key {key}")
            if isinstance(dictionary, dict)
            else f"no key {key}",
            keys,
            dictionary,
        )
