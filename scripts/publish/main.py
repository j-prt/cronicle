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
    """
    Loops through each site in the site list, following
    the steps from data ingestion to model inference.
    After collecting all the articles picked for publishing,
    uses SendGrid to send an email to the supplied address(es).
    """

    all_articles = {}
    for site in SITE_LIST:
        articles = process_table(
            table=site,
            test_sites=TEST_SITES,
            article_count=ARTICLE_COUNT,
            batch_size=BATCH_SIZE,
            target_emotion=TARGET_EMOTION,
        )
        if not articles:
            print(f'No articles for {site}')
            articles = {site: [{'title': 'No new articles today'}]}

        print(f'Articles for {site} complete.')
        all_articles.update(articles)

    publish(
        all_articles,
        from_email=FROM_EMAIL,
        to_email=TO_EMAIL,
        sendgrid_api_key=SENDGRID_API_KEY
    )

    print('All done!')

if __name__ == '__main__':
    main()
