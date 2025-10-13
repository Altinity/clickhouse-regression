FROM ubuntu:22.04

ENV TZ=Europe/Moscow

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY runner.sh runner.sh
COPY sqlalchemy.patch sqlalchemy.patch

CMD ["./runner.sh"]
