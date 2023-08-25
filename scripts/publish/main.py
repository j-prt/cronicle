"""Main script to ingest, process, and publish emails."""
import os
from processing import process_table
from publishing import publish


FROM_EMAIL=os.environ['FROM_EMAIL']
TO_EMAIL=os.environ['TO_EMAIL']
SENDGRID_API_KEY=os.environ['SENDGRID_API_KEY']

SITE_LIST = [
    'arxiv',
    'hackernews',
    'techmeme',
    'lwl',
    'rogerebert',
    'hollywood_reporter',
    'npr_books',
    'nyt_books',
]
TEST_SITES = [
    'arxiv',
    'hackernews',
    'techmeme',
]
ARTICLE_COUNT = 5
TARGET_EMOTION = 7  # 7 = Curiosity
BATCH_SIZE = 16


def main():
    pass
