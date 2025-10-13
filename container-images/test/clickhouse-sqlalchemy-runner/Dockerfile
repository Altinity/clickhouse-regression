FROM altinityinfra/clickhouse-server:0-25.8.9.20024.altinitytest

ENV TZ=Europe/Moscow

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY runner.sh runner.sh
COPY sqlalchemy.patch sqlalchemy.patch
COPY diff_0_2_9.patch diff_0_2_9.patch

CMD ["./runner.sh"]
