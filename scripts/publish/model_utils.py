"""Functions for applying the text classifier"""


import math
import torch
from transformers import (
    AutoTokenizer,
    RobertaForSequenceClassification
)


tokenizer = AutoTokenizer.from_pretrained("./model")
model = RobertaForSequenceClassification.from_pretrained("./model")


def _tokenize(rows):
    inputs = tokenizer(
    rows,
    truncation=True,
    padding=True,
    max_length=512,
    return_tensors="pt"
    )
    return inputs


def _classify(inputs, target_emotion):
    with torch.no_grad():
        logits = model(**inputs).logits[:,target_emotion]
    return logits


def rank_articles(table, rows, article_count, batch_size, target_emotion):
    scored_rows = []
    # Score posts by score of the comments, averaged.
    if table == 'hackernews':
        for row in rows:
            row_dict = {}
            row_dict['url'] = row['detail_url']
            row_dict['title'] = row['title']
            row_dict['comments'] = row['comments']
            comments_len = len(row['comments'])

            if comments_len <= batch_size:
                inputs = _tokenize(row_dict['comments'])
                logits = _classify(inputs, target_emotion)
            else:
                logits = torch.empty((0))
                batches = math.ceil(comments_len / batch_size)
                for i in range(batches):
                    comments = row.comments[i*batch_size:(i+1)*batch_size]
                    inputs = _tokenize(comments)
                    batch_logits = _classify(inputs, target_emotion)
                    logits = torch.cat((logits, batch_logits), dim=0)
            scores = torch.exp(logits)
            row_dict['score'] = torch.mean(scores).item()
            scored_rows.append(row_dict)
    # Score posts by score of the title and summary, averaged.
    elif table == 'arxiv':
        for row in rows:
            row_dict = {}
            row_dict['url'] = row['url']
            row_dict['title'] = row['title']
            row_dict['summary'] = row['summary']

            inputs = _tokenize([row['title'], row['summary']])
            logits = _classify(inputs, target_emotion)
            scores = torch.exp(logits)
            row_dict['score'] = torch.mean(scores).item()
            scored_rows.append(row_dict)
    # Score articles by the score of the title alone.
    else:
        for row in rows:
            row_dict = {}
            row_dict['url'] = row['url']
            row_dict['title'] = row['title']

            inputs = _tokenize([row['title']])
            logits = _classify(inputs)
            scores = torch.exp(logits)
            row_dict['score'] = scores.item()
            scored_rows.append(row_dict)

    # Sort the results.
    articles = sorted(scored_rows, key=lambda x: x['score'], reverse=True)
    return articles[:article_count]
