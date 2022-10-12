FROM registry.gitlab.com/altinity-public/container-images/test/clickhouse-integration-test:21.12

RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN apt-get update
RUN apt-get -y install postgresql

RUN pip install pyarrow