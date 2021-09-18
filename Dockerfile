FROM python:3.7-alpine

RUN export HTTP_PROXY="http://192.168.49.1:8282" \
    && export http_proxy="http://192.168.49.1:8282" \
    https_proxy="http://192.168.49.1:8282" \
    && pip install ply==3.11

WORKDIR /usr/src/app
