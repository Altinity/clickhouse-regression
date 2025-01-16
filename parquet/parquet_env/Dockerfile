FROM ubuntu:24.04

RUN apt-get update
RUN apt-get install -y wget
RUN wget https://github.com/Altinity/parquet-regression/releases/download/1.1.1/parquetify_1.1.1_amd64.deb
RUN apt-get install -y ./parquetify_*_amd64.deb