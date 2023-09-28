FROM python:3.11.5

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
