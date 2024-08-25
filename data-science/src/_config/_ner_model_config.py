# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


# Dictionary containing the configuration entity mapping for the dataset entities with the Presidio model entities
# Key: Dataset entity, Value: Presidio entity
PRESIDIO_CONFIGURATION = {
    'DATASET_TO_PRESIDIO_MAPPING': {"DATE": "DATE_TIME",
                                    "DOCTOR": "PERSON",
                                    "PATIENT": "PERSON",
                                    "HOSPITAL": "LOCATION",
                                    "MEDICALRECORD": "ID",
                                    "IDNUM": "ID",
                                    "ORGANIZATION": "ORGANIZATION",
                                    "ZIP": "O",
                                    "PHONE": "PHONE_NUMBER",
                                    "USERNAME": "O",
                                    "STREET": "O",
                                    "PROFESSION": "O",
                                    "COUNTRY": "LOCATION",
                                    "CITY": "LOCATION",
                                    "LOCATION-OTHER": "LOCATION",
                                    "FAX": "PHONE_NUMBER",
                                    "EMAIL": "EMAIL",
                                    "STATE": "LOCATION",
                                    "DEVICE": "O",
                                    "ORG": "ORGANIZATION",
                                    "AGE": "O"
                                    }
}

STANFORD_CONFIGURATION = {
    'DEFAULT_MODEL_PATH': "StanfordAIMI/stanford-deidentifier-base",
    'PRESIDIO_SUPPORTED_ENTITIES': [
        "LOCATION",
        "PERSON",
        "ORGANIZATION",
        "AGE",
        "ID",
        "PHONE_NUMBER",
        "EMAIL",
        "DATE_TIME",

    ],
    'LABELS_TO_IGNORE': ["O"],
    'DEFAULT_EXPLANATION': "Identified as {} by transformers's Named Entity Recognition",
    'SUB_WORD_AGGREGATION': 'simple',
    'DATASET_TO_PRESIDIO_MAPPING': {"DATE": "DATE_TIME",
                                    "DOCTOR": "PERSON",
                                    "PATIENT": "PERSON",
                                    "HOSPITAL": "LOCATION",
                                    "MEDICALRECORD": "ID",
                                    "IDNUM": "ID",
                                    "ORGANIZATION": "ORGANIZATION",
                                    "ZIP": "O",
                                    "PHONE": "PHONE_NUMBER",
                                    "USERNAME": "O",
                                    "STREET": "O",
                                    "PROFESSION": "O",
                                    "COUNTRY": "LOCATION",
                                    "LOCATION-OTHER": "LOCATION",
                                    "FAX": "PHONE_NUMBER",
                                    "EMAIL": "EMAIL",
                                    "STATE": "LOCATION",
                                    "DEVICE": "O",
                                    "ORG": "ORGANIZATION",
                                    "AGE": "O"
                                    },
    'MODEL_TO_PRESIDIO_MAPPING': {
        "PER": "PERSON",
        "PERSON": "PERSON",
        "LOC": "LOCATION",
        "ORG": "ORGANIZATION",
        "AGE": "AGE",
        "ID": "ID",
        "PATIENT": "PERSON",
        "HCW": "PERSON",
        "HOSPITAL": "LOCATION",
        "PATORG": "ORGANIZATION",
        "DATE": "DATE_TIME",
        "PHONE": "PHONE_NUMBER",
        "VENDOR": "ORGANIZATION"
    }
}

BERT_DEID_CONFIGURATION = {'PRESIDIO_SUPPORTED_ENTITIES': [
    "LOCATION",
    "PERSON",
    "ORGANIZATION",
    "AGE",
    "ID",
    "PHONE_NUMBER",
    "EMAIL",
    "DATE_TIME",
],
    'LABELS_TO_IGNORE': ["O"],
    'DEFAULT_EXPLANATION': "Identified as {} by transformers's Named Entity Recognition",
    'SUB_WORD_AGGREGATION': 'simple',

    'DATASET_TO_PRESIDIO_MAPPING': {"DATE": "DATE_TIME",
                                    "DOCTOR": "PERSON",
                                    "PATIENT": "PERSON",
                                    "HOSPITAL": "ORGANIZATION",
                                    "MEDICALRECORD": "ID",
                                    "IDNUM": "ID",
                                    "ORGANIZATION": "ORGANIZATION",
                                    "ZIP": "O",
                                    "PHONE": "PHONE_NUMBER",
                                    "USERNAME": "O",
                                    "STREET": "O",
                                    "PROFESSION": "O",
                                    "COUNTRY": "LOCATION",
                                    "LOCATION-OTHER": "LOCATION",
                                    "FAX": "PHONE_NUMBER",
                                    "EMAIL": "EMAIL",
                                    "STATE": "LOCATION",
                                    "DEVICE": "O",
                                    "ORG": "ORGANIZATION",
                                    "AGE": "O"
                                    },

    'MODEL_TO_PRESIDIO_MAPPING': {
    "PER": "PERSON",
    "LOC": "LOCATION",
    "ORG": "ORGANIZATION",
    "AGE": "AGE",
    "ID": "ID",
    "EMAIL": "EMAIL",
    "PATIENT": "PERSON",
    "STAFF": "PERSON",
    "HOSP": "ORGANIZATION",
    "PATORG": "ORGANIZATION",
    "DATE": "DATE_TIME",
    "PHONE": "PHONE_NUMBER",
},
    'DEFAULT_MODEL_PATH': "obi/deid_roberta_i2b2"
}
