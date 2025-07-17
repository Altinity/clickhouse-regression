FROM altinity/clickhouse-server:23.8.5.17.altinitytest

COPY runner.sh runner.sh
COPY sqlalchemy.patch sqlalchemy.patch

CMD ./runner.sh
