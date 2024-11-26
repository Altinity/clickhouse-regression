FROM ubuntu:24.04

RUN apt-get update
RUN apt-get install -y wget
RUN wget https://github.com/Altinity/parquet-regression/releases/download/1.0.9/parquetify_1.0.9_amd64.deb
RUN apt-get install -y ./parquetify_*_amd64.deb