from google.cloud import bigquery

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

client = bigquery.Client()

def get_table_data(table):
    QUERY = (
        f'SELECT * FROM `article-source.article_views.{table}`')
    query_job = client.query(QUERY)
    rows = query_job.result()
    return rows

for site in SITE_LIST:
    rows = get_table_data(site)
    if rows.total_rows == 0:
        print('Empty today')
        continue
    print(next(rows))
    print('\n\n')
