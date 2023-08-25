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

client = bigquery.Client()

def _get_table_data(table):
    if table == 'arxiv':
        opts = 'title, url, summary'
    elif table == 'hackernews':
        opts = 'title, url, detail_url, comments'
    else:
        opts = 'title, url'

    query = (f'''SELECT {opts}
            FROM `article-source.article_views.{table}`''')
    query_job = client.query(query)
    rows = query_job.result()

    if rows.total_rows == 0:
        return None
    return rows

for site in SITE_LIST:
    rows = _get_table_data(site)
    if rows.total_rows == 0:
        print('Empty today')
        continue
    print(next(rows))
    print('\n\n')


def process_table(table):
    if table in TEST_SITES:
        return process_table_test(table)

    rows = _get_table_data(table)
    if not rows:
        print(f'No data for {table}.')
        return None

    #### TODO ####
    # Call to URL click-tracking API

    rows = [dict(row) for row in rows]

    return {table: rows}



def process_table_test(table):
    ab = round(random.random())

    if ab == 1:
        return randomize_rows(table)

    inputs = tokenize_rows(table=table)




def randomize_rows(table):
    pass

def tokenize_rows(table):
    pass
