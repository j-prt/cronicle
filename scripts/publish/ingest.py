"""Functions for data ingestion and processing"""

from google.cloud import bigquery
import random
from model_utils import rank_articles

def get_table_data(table):
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


def process_table(table, test_sites, article_count, batch_size, target_emotion):
    rows = get_table_data(table)
    if not rows:
        print(f'No data for {table}.')
        return None

    if table in test_sites:
        articles = process_table_ab(
            table,
            rows,
            article_count,
            batch_size,
            target_emotion
        )

    else:
        articles = [dict(row) for row in rows]

    #### TODO ####
    # Call to URL click-tracking API

    return {table: articles}


def process_table_ab(table, rows, article_count, batch_size, target_emotion):
    ab = round(random.random())

    if ab == 1:
        #### TODO ####
        # Add some logging to indicate this was the control
        print(f'Unranked articles for {table}')
        articles = rows_control(table, article_count)
    else:
        print(f'Ranked articles for {table}')
        articles = rank_articles(
            table,
            rows,
            article_count=article_count,
            batch_size=batch_size,
            target_emotion=target_emotion
            )

    return {table: articles}


def rows_control(table, article_count):
    # Unpack the row iterator into a list
    articles = [dict(row) for row in table]
    if table == 'hackernews':
        # Select top articles by points
        articles = sorted(articles, key=lambda x: x['points'], reverse=True)
        return articles
    else:
        # Select articles at random
        articles = random.sample(articles, k=article_count)
        return articles
