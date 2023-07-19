import logging
import os

CLOUD_PROJECT=os.environ['CLOUD_PROJECT']
TEMP_LOCATION=os.environ['TEMP_LOCATION']
DATASET=os.environ['DATASET']
TABLE=os.environ['TABLE']
SCHEMA_FILE=os.environ['SCHEMA_FILE']

class DataPreparation:
    """Utility class for data transformations"""

    # Used for holding dictionary keys (field names). Set as
    # a class attribute because the individual instance state doesn't
    # seem to be preserved during pipeline execution
    table_keys = []

    def read_csv_file(self, file):
        """Function for reading csv files. Used instead of
        the builtin beam csv reader due to newlines in fields."""
        import apache_beam as beam
        import csv
        import io

        with beam.io.filesystems.FileSystems.open(file) as gcs_file:
            reader = csv.reader(io.TextIOWrapper(gcs_file))

            # Get keys from header
            table_keys = next(reader)+['create_time']
            DataPreparation.table_keys.extend(table_keys)

            # Read in the rows
            for row in reader:
                yield row

    def get_schema(self, schema_file, source_site):
        """Function for getting the appropriate schema for the
        supplied csv file, based on the filename."""
        import json
        import apache_beam as beam
        from apache_beam.io.gcp.bigquery_tools import parse_table_schema_from_json

        with beam.io.filesystems.FileSystems.open(schema_file) as f:
            all_schemas = json.load(f)
            target_schema = json.dumps(all_schemas[source_site])
            schema = parse_table_schema_from_json(target_schema)
        return schema

    def parse_filename(self, filename):
        """Function for both getting the article source name (to
        match schemas) as well as parsing datetimes to bq format."""

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

    def row_to_dict(self, row, keys, source_site, timestamp):
        """Function for dealing with corner cases: where
        fields need to be uploaded as repeated arrays in bq."""
        import ast

        if source_site == 'hackernews':
            comments = ast.literal_eval(row.pop())
            comments = [{'comment':item} for item in comments]
            return dict(zip(keys, row+[comments]+[timestamp]))

        if source_site == 'rogerebert':
            tags = ast.literal_eval(row.pop())
            tags = [{'tag':item} for item in tags]
            return dict(zip(keys, row+[tags]+[timestamp]))

        # Simple case (no repeated fields)
        return dict(zip(keys, row+[timestamp]))

from apache_beam.options.pipeline_options import PipelineOptions

class ArticleOptions(PipelineOptions):
    """Docstring"""

    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_value_provider_argument(
            '--input',
            help='Path to article in GCS bucket',
            required=True,
        )
        # parser.add_value_provider_argument(
        #     '--temp_location',
        #     help='Path to temp storage in GCS',
        #     required=True,
        # )
        # parser.add_value_provider_argument(
        #     '--cloud_project',
        #     help='Project name',
        #     required=True,
        # )
        parser.add_value_provider_argument(
            '--schema_file',
            help='Path to JSON file with schemas',
            required=True,
        )
        parser.add_value_provider_argument(
            '--dataset',
            help='BQ Dataset name',
            required=True,
        )
        parser.add_value_provider_argument(
            '--table',
            help='Table name',
            required=True,
        )


def run(argv=None, save_main_session=True):
    """The main function which creates the pipeline and runs it."""
    import apache_beam as beam
    from apache_beam.options.pipeline_options import PipelineOptions

    options = PipelineOptions(
        region= 'us-west3',
        save_main_session=save_main_session
    )
    p = beam.Pipeline(options=options)

    user_options = options.view_as(ArticleOptions)
    dataprep = DataPreparation()

    print(type(user_options.input.value))

    source_site, timestamp = dataprep.parse_filename(user_options.input.value)
    schema = dataprep.get_schema(user_options.schema_file.value, source_site)



    (p
         | 'Load url' >> beam.Create([user_options.input.value])
         | 'Read csv' >> beam.FlatMap(lambda f: dataprep.read_csv_file(f))
         | 'Convert to dict' >> beam.Map(
               lambda row: dataprep.row_to_dict(
                   row,
                   DataPreparation.table_keys,
                   source_site,
                   timestamp
               )
           )
         | 'Write to bigquery' >> beam.io.WriteToBigQuery(
               table=user_options.table.value,
               dataset=user_options.dataset.value,
               schema=schema,
               create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
               write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
           )
    )
    p.run().wait_until_finish()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
