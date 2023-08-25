"""Functions for applying the text classifier"""

import math
import torch
from transformers import (
    AutoTokenizer,
    RobertaForSequenceClassification
)


TARGET_EMOTION = 7  # 7 = Curiosity
BATCH_SIZE = 16


tokenizer = AutoTokenizer.from_pretrained("./model")
model = RobertaForSequenceClassification.from_pretrained("./model")


def tokenize(table, rows):
    inputs = tokenizer(
    rows,
    truncation=True,
    padding=True,
    max_length=512,
    return_tensors="pt"
    )
    return inputs


def classify(inputs, batch, batch_size=BATCH_SIZE):
    if batch == False:
        with torch.no_grad():
            logits = model(**inputs).logits[:,TARGET_EMOTION]
    else:
        pass

    return logits



def rank_articles(table, rows, article_count):
    scored_rows = []
    if table == 'hackernews':
        pass
    elif table == 'arxiv':

        row_dict = {}
        row_dict['url'] = row['url']
        row_dict['title'] = row['title']
        row_dict['summary'] = row['summary']

        # Single item predictions - using 'all_logits' for consistency
        inputs = tokenize([row['title'], row['summary']])
        logits = classify(inputs)
        scores = torch.exp(logits)
        row_dict['score'] = torch.mean(scores).item()
        scored_rows.append(row_dict)
    else:
        for row in rows:
            row_dict = {}
            row_dict['url'] = row['url']
            row_dict['title'] = row['title']

            # Single item predictions - using 'all_logits' for consistency
            inputs = tokenize([row['title']])
            logits = classify(inputs)
            scores = torch.exp(logits)
            row_dict['score'] = torch.mean(scores).item()
            scored_rows.append(row_dict)
