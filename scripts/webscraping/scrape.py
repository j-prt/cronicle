"""Program for performing various webscraping operations."""
import argparse
import json
import csv
from datetime import datetime, timezone
from pathlib import Path
from scrapers import ScrapeIt

DEFAULT_CHECKPOINT_PATH = 'checkpoints.json'


def write_csv(stem, articles):
    """Write a collection of articles to a timestamped csv."""
    now = datetime.now(timezone.utc).strftime('%Y%M%d%H%M')
    with open('{}-{}.csv'.format(stem, now), 'w', newline='') as csvfile:
        fieldnames = articles[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in articles:
            writer.writerow(row)

parser = argparse.ArgumentParser()

parser.add_argument(
    'mode',
    help='''
    Which type of scraping to perform. 'all' indicates a full scrape,
    'fast' scrapes only regularly (more than daily) updated pages, and
    'fastest' indicates very frequently updated pages
    '''
)
parser.add_argument(
    '-c',
    '--checkpoint',
    dest='checkpoint',
    help='Filepath to a JSON file of checkpoints for sequential feeds'
)

args = parser.parse_args()

checkpoint_path = Path(args.checkpoint)

if checkpoint_path.exists():
    checkpoint_path = Path(args.checkpoint)
    with open(checkpoint_path, 'r') as fp:
        checkpoints = json.load(fp)
    scraper = ScrapeIt(checkpoints)
else:
    checkpoint_path = DEFAULT_CHECKPOINT_PATH
    scraper = ScrapeIt()

new_checkpoints = {}

if args.mode == 'all':
    # TODO
    arxiv = scraper.arxiv()
    if arxiv:
        write_csv('arxiv', arxiv)
        new_checkpoints['arxiv'] = arxiv[0]['url']
elif args.mode == 'fast':
    # TODO
    pass
elif args.mode == 'fastest':
    # TODO
    pass
else:
    print('Argument \'mode\' must be \'all\', \'fast\', or \'fastest\'.')
    raise SystemExit(22)


with open(checkpoint_path, 'w') as fp:
    json.dump(new_checkpoints, fp)
