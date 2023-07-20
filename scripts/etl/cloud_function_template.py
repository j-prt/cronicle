# requirements file:
# functions-framework==3.*
# google-auth
# google-api-python-client

import functions_framework
import base64
import google.auth
import json
import os

from googleapiclient.discovery import build

CLOUD_PROJECT=os.environ['CLOUD_PROJECT']
TEMP_LOCATION=os.environ['TEMP_LOCATION']
DATASET=os.environ['DATASET']
BUCKET=os.environ['BUCKET']
TABLE=os.environ['TABLE']
SCHEMA_FILE=os.environ['SCHEMA_FILE']


def hello_pubsub(cloud_event, context):
    new_article = cloud_event['attributes']['objectId']
    # Only works for csvs !
    article_name = new_article.split('/')[-1][:-4]
    table = article_name.split('-')[0]

    credentials, _ = google.auth.default()
    dataflow = build('dataflow', 'v1b3', credentials=credentials)

    request = dataflow.projects().locations().flexTemplates().launch(
        projectId=CLOUD_PROJECT,
        location='us-west3',
        body={
            'launchParameter': {
                'jobName': f'article-upload-{article_name.replace("_", "-")}',
                'containerSpecGcsPath': BUCKET+'templates/article_df_flex.json',
                'parameters': {
                    'input': BUCKET+new_article,
                    'dataset': DATASET,
                    'table': table,
                    'schema_file': SCHEMA_FILE,
                },
            }
        }
    )

    response = request.execute()
    print(response)
