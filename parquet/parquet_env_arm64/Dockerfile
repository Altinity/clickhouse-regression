FROM ubuntu:24.04

RUN apt-get update
RUN apt-get install -y wget
RUN wget https://github.com/Altinity/parquet-regression/releases/download/1.0.5/parquetify_1.0.5_arm64.deb
RUN apt-get install -y ./parquetify_*_arm64.deb