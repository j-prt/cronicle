"""Program for performing various webscraping operations."""
import argparse
import json
from pathlib import Path
from scrapers import ScrapeIt

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

print(args)

if args.mode == 'all':
    # TODO
    pass
elif args.mode == 'fast':
    # TODO
    pass
elif args.mode == 'fastest':
    # TODO
    pass
else:
    print('Argument \'mode\' must be \'all\', \'fast\', or \'fastest\'.')
    raise SystemExit(22)
