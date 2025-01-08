FROM python:3.10

WORKDIR /app

COPY server.py /app/server.py

RUN pip3 install bottle==0.13.2

EXPOSE 8080

CMD ["python", "server.py", "8080"]
