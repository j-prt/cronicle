import logging

def run(argv=None):
    """The main function which creates the pipeline and runs it."""
    import argparse
    import apache_beam as beam
    from apache_beam.options.pipeline_options import PipelineOptions

    from my_utils.dataprep import DataPreparation

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input',
        dest='input',
        help='Input article from the GCS bucket.',
        required=True,
    )
    parser.add_argument(
        '--schema_file',
        dest='schema_file',
        help='Path to JSON file with schemas',
        required=True,
    )
    parser.add_argument(
        '--dataset',
        dest='dataset',
        help='BQ Dataset name',
        required=True,
    )
    parser.add_argument(
        '--table',
        dest='table',
        help='Table name',
        required=True,
    )


    # Collect argparse args as known_args, other args
    # (to be used for pipeline options) as pipeline_args
    known_args, pipeline_args = parser.parse_known_args(argv)

    # Set this up so a path to a schema_file can be passed as one
    # of the known args registered to the parser
    dataprep = DataPreparation()

    source_site, timestamp = dataprep.parse_filename(known_args.input)
    schema = dataprep.get_schema(known_args.schema_file, source_site)

    options = PipelineOptions(
        pipeline_args,
    )

    p = beam.Pipeline(options=options)
    (p
         | 'Load url' >> beam.Create([known_args.input])
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
               table=known_args.table,
               dataset=known_args.dataset,
               schema=schema,
               create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
               write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
           )
    )
    p.run().wait_until_finish()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
