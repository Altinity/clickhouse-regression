# docker build -t clickhouse/stateful-test .
FROM registry.gitlab.com/altinity-public/container-images/test/stateless_arm64:21.12
# aws CLI comes from stateless

RUN apt-get update -y \
    && env DEBIAN_FRONTEND=noninteractive \
        apt-get install --yes --no-install-recommends \
        python3-requests \
        llvm-9

# COPY s3downloader /s3downloader, no need to download this every single time, besides some issues when downloading

RUN curl -O https://datasets.clickhouse.com/hits/partitions/hits_v1.tar
RUN curl -O https://datasets.clickhouse.com/visits/partitions/visits_v1.tar

RUN apt-get clean

COPY run.sh /
CMD ["/bin/bash", "/run.sh"]
