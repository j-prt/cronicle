ARG TAG=latest
FROM gcr.io/dataflow-templates-base/python3-template-launcher-base:${TAG}

ARG WORKDIR=/dataflow/template
RUN mkdir -p ${WORKDIR}
WORKDIR ${WORKDIR}

COPY requirements.txt .

ENV FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE="${WORKDIR}/requirements.txt"
ENV FLEX_TEMPLATE_PYTHON_PY_FILE="${WORKDIR}/articles_df_flex.py"
ENV FLEX_TEMPLATE_PYTHON_SETUP_FILE="/${WORKDIR}/setup.py"

# Install apache-beam and other dependencies to launch the pipeline
RUN pip install "apache-beam[gcp]"
RUN pip install -U -r ./requirements.txt

COPY articles_df_flex.py .
COPY setup.py .
# COPY . .
