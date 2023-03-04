FROM python:3.10.0-slim-buster

ENV Telegram_Dev DEFAULT_VALUE_IS_BAD
ENV DATABASE_HOST DEFAULT_VALUE_IS_BAD
ENV DATAVASE_USER DEFAULT_VALUE_IS_BAD
ENV DATABASE_PASS DEFAULT_VALUE_IS_BAD
ENV DATABASE_NAME DEFAULT_VALUE_IS_BAD

COPY requirements.txt /tmp/requirements.txt
COPY . /
RUN python3 -m pip install -r /tmp/requirements.txt

CMD ["python3", "main.py"]