#!/bin/bash

cd ~/Desktop/projects/python/pb/scripts/webscraping
source venv/bin/activate

python3 scrape.py fast

gcloud auth login --cred-file=$CRED_FILE
gcloud storage cp --recursive ./*.csv $ARTICLE_BUCKET
gcloud auth revoke --all

sudo mkdir -p ~/Desktop/archive/articles/$(date +%s)
sudo mv ./*.csv $_
deactivate
