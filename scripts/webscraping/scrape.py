"""Program for performing various webscraping operations."""
import argparse
import json
import csv
from datetime import datetime, timezone
from pathlib import Path
from scrapers import ScrapeIt


DEFAULT_CHECKPOINT_PATH = 'checkpoints.json'
NOW = datetime.now(timezone.utc).strftime('%Y%m%d%H%M')


def write_csv(stem, articles):
    """Write a collection of articles to a timestamped csv."""
    with open('{}-{}.csv'.format(stem, NOW), 'w', newline='') as csvfile:
        fieldnames = articles[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in articles:
            writer.writerow(row)


parser = argparse.ArgumentParser()
parser.add_argument(
    'mode',
    default='all',
    help='''
    Which type of scraping to perform. 'all' indicates a full scrape,
    'fast' scrapes only regularly (more than daily) updated pages, and
    'fastest' indicates very frequently updated pages
    '''
)
parser.add_argument(
    '-c',
    '--checkpoint',
    default='checkpoints.json',
    dest='checkpoint',
    help='Filepath to a JSON file of checkpoints for sequential feeds'
)

args = parser.parse_args()

checkpoint_path = Path(args.checkpoint)
checkpoints = {}

if checkpoint_path.exists():
    checkpoint_path = Path(args.checkpoint)
    with open(checkpoint_path, 'r') as fp:
        checkpoints = json.load(fp)
    scraper = ScrapeIt(checkpoints)
else:
    checkpoint_path = DEFAULT_CHECKPOINT_PATH
    scraper = ScrapeIt()


if args.mode == 'all':
    # Scrape every site sequentially, updating checkpoints and
    # writing new csv files
    arxiv = scraper.arxiv()
    if arxiv:
        write_csv('arxiv', arxiv)
        checkpoints['arxiv'] = arxiv[0]['url']
    hackernews = scraper.hackernews()
    if hackernews:
        write_csv('hackernews', hackernews)
    techmeme = scraper.techmeme()
    if techmeme:
        write_csv('techmeme', techmeme)
    lwl = scraper.lwl()
    if lwl:
        write_csv('lwl', lwl)
        checkpoints['lwl'] = lwl[0]['url']
    rogerebert = scraper.rogerebert()
    if rogerebert:
        write_csv('rogerebert', rogerebert)
        checkpoints['rogerebert'] = rogerebert[0]['url']
    hollywood_reporter = scraper.hollywood_reporter()
    if hollywood_reporter:
        write_csv('hollywood_reporter', hollywood_reporter)
        checkpoints['hollywood_reporter'] = hollywood_reporter[0]['url']
    npr_books = scraper.npr_books()
    if npr_books:
        write_csv('npr_books', npr_books)
        checkpoints['npr_books'] = npr_books[0]['url']
    nyt_books = scraper.nyt_books()
    if nyt_books:
        write_csv('nyt_books', nyt_books)
        checkpoints['nyt_books'] = nyt_books[0]['url']

elif args.mode == 'fast':
    # Scrape somewhat frequently updated sites
    arxiv = scraper.arxiv()
    if arxiv:
        write_csv('arxiv', arxiv)
        checkpoints['arxiv'] = arxiv[0]['url']
    hackernews = scraper.hackernews()
    if hackernews:
        write_csv('hackernews', hackernews)
    techmeme = scraper.techmeme()
    if techmeme:
        write_csv('techmeme', techmeme)

elif args.mode == 'fastest':
    # Scrape the most frequently updated sites
    hackernews = scraper.hackernews()
    if hackernews:
        write_csv('hackernews', hackernews)
    techmeme = scraper.techmeme()
    if techmeme:
        write_csv('techmeme', techmeme)
else:
    print('Argument \'mode\' must be \'all\', \'fast\', or \'fastest\'.')
    raise SystemExit(22)


with open(checkpoint_path, 'w') as fp:
    json.dump(checkpoints, fp)
