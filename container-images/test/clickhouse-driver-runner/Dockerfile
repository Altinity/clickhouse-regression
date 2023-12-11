FROM altinity/clickhouse-server:23.8.5.17.altinitytest

ENV TZ=Europe/Moscow

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY runner.sh runner.sh
COPY diff-0.2.1.patch diff-0.2.1.patch
COPY diff-0.2.2.patch diff-0.2.2.patch
COPY diff-0.2.3.patch diff-0.2.3.patch
COPY clickhouse-driver.patch clickhouse-driver.patch

CMD ./runner.sh
