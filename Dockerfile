FROM python:2.7

ARG http_proxy
ARG https_proxy
ARG no_proxy
ARG PIP_INDEX_URL
ARG PIP_TRUSTED_HOST

RUN mkdir -p /tmp
WORKDIR /tmp

COPY setup.py .
COPY requirements.txt .
COPY dcsh/ . 

RUN python setup.py install \
 && pip install -r requirements.txt \
 && rm -rf /tmp/*
