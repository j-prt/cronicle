import argparse
import logging
import csv
import json
import io


import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io.gcp.bigquery_tools import parse_table_schema_from_json


# Used for holding the dictionary keys
table_keys = []


def read_csv_file(file):
    with beam.io.filesystems.FileSystems.open(file) as gcs_file:
        reader = csv.reader(io.TextIOWrapper(gcs_file))

        # Get keys from header
        table_keys.extend(next(reader))
        for row in reader:
            yield row

# Read the schema file into bq format
with open('schema_arxiv.json', 'r') as f:
    schema_raw = f.read()
    schema = parse_table_schema_from_json(schema_raw)


def run(argv=None):
    """The main function which creates the pipeline and runs it."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input',
        dest='input',
        required=False,
        help='Input file to read. This can be a local file or '
        'a file in a Google Storage Bucket.',
        default='articles_arxiv-202307101305.csv')
    parser.add_argument('--output',
                        dest='output',
                        required=False,
                        help='Output title',
                        default='test')

    # Collect argparse args as known_args, other args
    # (to be used for pipeline options) as pipeline_args
    known_args, pipeline_args = parser.parse_known_args(argv)


    p = beam.Pipeline(options=PipelineOptions(pipeline_args))
    (p
         | 'Load url' >> beam.Create([known_args.input])
         | 'Read csv' >> beam.FlatMap(read_csv_file)
         | 'Convert to dict' >> beam.Map(lambda row: dict(zip(table_keys, row)))
         | 'String to text file' >> beam.io.WriteToText(known_args.output, file_name_suffix='.txt')
    )
    p.run().wait_until_finish()

print(schema)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
