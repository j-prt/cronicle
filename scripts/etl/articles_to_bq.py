import argparse
import logging
import json
import csv
import io


import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io.gcp.bigquery_tools import parse_table_schema_from_json

schema_file = 'schemas.json'
# Used for holding the dictionary keys
class DataPreparation:
    table_keys = []

    def read_csv_file(self, file):
        with beam.io.filesystems.FileSystems.open(file) as gcs_file:
            reader = csv.reader(io.TextIOWrapper(gcs_file))

            # Get keys from header
            table_keys = next(reader)+['create_time']
            DataPreparation.table_keys.extend(table_keys)
            for row in reader:
                yield row

    def get_schema(self, schema_file, source_site):
        # Read the schema file into bq format
        with open(schema_file, 'r') as f:
            all_schemas = json.load(f)
            target_schema = json.dumps(all_schemas[source_site])
            schema = parse_table_schema_from_json(target_schema)
        return schema

    def parse_filename(self, filename):
        filename = filename.split('/')[-1]
        source_site = filename.split('-')[0]
        timestamp = filename.split('-')[1].split('.')[0]
        timestamp = (
            timestamp[:4]
            + '-'
            + timestamp[4:6]
            + '-'
            + timestamp[6:8]
            + 'T'
            + timestamp[8:10]
            + ':00:00'
        )
        return source_site, timestamp


def run(argv=None):
    """The main function which creates the pipeline and runs it."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input',
        dest='input',
        required=False,
        help='Input file to read. This can be a local file or '
        'a file in a Google Storage Bucket.',
        default='gs://pb-datalake/articles/arxiv-202306080106.csv'
    )
    parser.add_argument(
        '--output',
        dest='output',
        required=False,
        help='Output title',
        default='test'
    )

    # Collect argparse args as known_args, other args
    # (to be used for pipeline options) as pipeline_args
    known_args, pipeline_args = parser.parse_known_args(argv)

    # Set this up so a path to a schema_file can be passed as one
    # of the known args registered to the parser
    dataprep = DataPreparation()

    source_site, timestamp = dataprep.parse_filename(known_args.input)
    schema = dataprep.get_schema(schema_file, source_site)
    print(source_site, timestamp)

    p = beam.Pipeline(options=PipelineOptions(pipeline_args))
    (p
         | 'Load url' >> beam.Create([known_args.input])
         | 'Read csv' >> beam.FlatMap(lambda f: dataprep.read_csv_file(f))
        #  | 'Test write' >> beam.io.WriteToText('fasdfa', '.txt')
         | 'Convert to dict' >> beam.Map(
               lambda row: dict(zip(DataPreparation.table_keys, row+[timestamp]))
           )
        #  | 'Test write' >> beam.io.WriteToText('fasdfa', '.txt')
         | 'Write to bigquery' >> beam.io.WriteToBigQuery(
               table='test_arxiv_4',
               dataset='arxiv_0',
               project='article-source',
               schema=schema,
               create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
               write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
               custom_gcs_temp_location='gs://pb-datalake'
           )
    )
    p.run().wait_until_finish()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
