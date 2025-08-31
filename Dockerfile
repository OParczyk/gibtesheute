FROM python:slim

WORKDIR /usr/app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt ./

RUN apt-get update && \
    apt-get install gcc libexpat1 -y && \
    pip install --no-cache-dir -r requirements.txt \
    && apt-get purge gcc -y \
    && apt-get autoremove -y \
    && apt-get clean

COPY gibtesheute gibtesheute
COPY wsgi.py wsgi.py

EXPOSE 8000
ENTRYPOINT ["uwsgi", "--http", "0.0.0.0:8000", "--master", "-p", "4", "-w", "wsgi:app"]
