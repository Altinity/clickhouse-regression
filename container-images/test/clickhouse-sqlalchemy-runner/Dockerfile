FROM altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest

ENV TZ=Europe/Moscow

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY runner.sh runner.sh
COPY sqlalchemy.patch sqlalchemy.patch
COPY diff_0_2_9.patch diff_0_2_9.patch

#https://github.com/xzkostyan/clickhouse-sqlalchemy/issues/393
COPY diff-asynch-soft-close.patch diff-asynch-soft-close.patch 


CMD ["./runner.sh"]
