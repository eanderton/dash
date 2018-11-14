FROM python:2.7

ARG http_proxy
ARG https_proxy
ARG no_proxy
ARG PIP_INDEX_URL
ARG PIP_TRUSTED_HOST


RUN env && export && pip install flake8
