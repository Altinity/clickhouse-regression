FROM ubuntu:24.04

RUN apt-get update
RUN apt install -y wget
RUN wget https://github.com/Altinity/parquet-regression/releases/download/1.0.5/parquetify_1.0.5_amd64.deb
RUN apt install -y ./parquetify_*_amd64.deb