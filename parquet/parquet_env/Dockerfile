FROM ubuntu:24.04

RUN apt-get update
RUN apt install -y wget
RUN wget https://github.com/Altinity/parquet-regression/releases/download/0.0.2/parquetify_0.0.2_amd64.deb
RUN apt install -y ./parquetify_*_amd64.deb