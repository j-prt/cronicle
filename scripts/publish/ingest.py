from google.cloud import bigquery
import random
from model_utils import tokenize_rows, classify

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


def _get_table_data(table):
    client = bigquery.Client()
    if table == 'arxiv':
        opts = 'title, url, summary'
    elif table == 'hackernews':
        opts = 'title, url, detail_url, comments, points'
    else:
        opts = 'title, url'

    query = (f'''SELECT {opts}
            FROM `article-source.article_views.{table}`''')
    query_job = client.query(query)
    rows = query_job.result()

    if rows.total_rows == 0:
        return None
    return rows

# for site in SITE_LIST:
#     rows = _get_table_data(site)
#     if rows.total_rows == 0:
#         print('Empty today')
#         continue
#     print(next(rows))
#     print('\n\n')


def process_table(table):
    if table in TEST_SITES:
        return process_table_test(table)

    rows = _get_table_data(table)
    if not rows:
        print(f'No data for {table}.')
        return None

    #### TODO ####
    # Call to URL click-tracking API

    articles = [dict(row) for row in rows]

    return {table: articles}


def process_table_test(table):
    ab = round(random.random())

    if ab == 1:
        #### TODO ####
        # Add some logging to indicate this was a test
        articles = rows_ab_test(table)
    else:
        tokenized_articles = tokenize_rows(table=table)
        articles = classify(tokenized_articles, article_count=ARTICLE_COUNT)

    return {table: articles}


def rows_ab_test(table):
    # Unpack the row iterator into a list
    articles = [dict(row) for row in table]
    if table == 'hackernews':
        # Select top articles by points
        articles = sorted(articles, key=lambda x: x['points'], reverse=True)
        return articles
    else:
        # Select articles at random
        articles = random.sample(articles, k=ARTICLE_COUNT)
        return articles
