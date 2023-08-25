"""Functions for applying the text classifier"""

import torch
from transformers import (
    AutoTokenizer,
    RobertaForSequenceClassification
)


tokenizer = AutoTokenizer.from_pretrained("./model")
model = RobertaForSequenceClassification.from_pretrained("./model")


def tokenize_rows(rows):
    pass


def classify(batch):
    pass
