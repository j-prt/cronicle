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
<br>
Further details below!

## Overview

<div align=center>
  <img src="https://i.imgur.com/b8yts2G.jpeg">
  
  The Cronicle data flow.</div>
<br>
1. Scrapers collect data from a number of sites
2. Initial processing, data is dumped to object storage (GCS)
3. Further processing - a Dataflow job is triggered by Pubsub to perform ETL, uploading to BQ
4. A containerized process can then be run to:
    * query BQ
    * run AI model inference
    * publish emails based on model results

### Collection
I selected a number of interesting sites regarding topics I enjoyed (tech news, movies, books) and wrote scraping scripts to collect data from each. The experimental process can be viewed in [the notebooks](./data/collection). I compiled these into [a module](./scripts/webscraping) to facilitate easy scraping with some args to customize the process. Scripts are run on a schedule, scraping and then uploading to GCS. 

### Storage and Preprocessing
Uploading to Cloud Storage triggers a Cloud Function (via PubSub) to run a Dataflow job that uploads processed articles as rows to BQ tables. This scales indefinitely as jobs are run in parallel. Scripts and templates used are in the [etl](./scripts/etl) folder.


### Inference and delivery 
First, the inference script queries BQ. From there, it's set up to pretty much drop in any NLP inference model from the huggingface transformers library. The implementation available uses a BERT-based model to measure prominent emotions among the comments in [hackernews](https://news.ycombinator.com/) posts. After filtering, an email is published with links to the articles selected in inference.

These scripts can be found in the [publish](./scripts/publish) folder.
