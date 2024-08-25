# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


# Dictionary containing the configuration entity mapping for the dataset entities with the Presidio model entities
# Key: Dataset entity, Value: Presidio entity
PRESIDIO_CONFIGURATION = {
    # Mapping between dataset entities and Presidio entities. 
    # Key: Dataset entity, Value: Presidio entity
    'DATASET_TO_PRESIDIO_MAPPING': {"STREET_ADDRESS": "LOCATION",
                                    "PERSON": "PERSON",
                                    "GPE": "LOCATION",
                                    "ORGANIZATION": "ORGANIZATION",
                                    "PHONE_NUMBER": "PHONE_NUMBER",
                                    "DATE_TIME": "DATE_TIME",
                                    "TITLE": "O",
                                    "CREDIT_CARD": "CREDIT_CARD",
                                    "US_SSN": "US_SSN",
                                    "AGE": "O",
                                    "NRP": "LOCATION",
                                    "ZIP_CODE": "O",
                                    "EMAIL_ADDRESS": "EMAIL_ADDRESS",
                                    "DOMAIN_NAME": "URL",
                                    "IP_ADDRESS": "IP_ADDRESS",
                                    "IBAN_CODE": "IBAN_CODE",
                                    "US_DRIVER_LICENSE": "US_DRIVER_LICENSE"
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
