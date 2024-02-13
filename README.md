# Cronicle

This is a project I worked on in the summer of 2023. Cronicle is a multi-stage system for collecting articles from the web, uploading to cloud, and ultimately serving curated emails based on AI predictions. This repo is arranged largely as a collection of jupyter notebooks, python files, and scripts - from the stages of data collection to final product. 

Key technologies/libraries: 
- [GCP](https://cloud.google.com/)
  - BigQuery
  - GCS
  - Dataflow
  - Cloud Functions
- [Docker](https://www.docker.com/)
- [Bash](https://www.gnu.org/software/bash/) 
- [PyTorch](https://pytorch.org/)
- [HuggingFace](https://huggingface.co/)
- [SendGrid](https://sendgrid.com/en-us)

## Overview

graphic goes here

This illustrates the Cronicle data flow. 
- Scrapers collect data from a number of sites
- Initial processing, data is dumped to object storage (GCS)
- Further processing - a Dataflow job is triggered by Pubsub to perform ETL, uploading to BQ
- A containerized process can then be run to:
  - query BQ
  - run AI model inference
  - publish emails based on model results

## Collection
link to notebooks, scrapeit module

## Storage and Preprocessing
link to dataflow and talk about cloud functions

## Inference and delivery 
discuss tools used for inference
