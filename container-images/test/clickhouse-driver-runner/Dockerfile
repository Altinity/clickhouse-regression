FROM altinityinfra/clickhouse-server:0-25.8.16.10001.altinitytest

COPY runner.sh runner.sh
COPY diff-0.2.1.patch diff-0.2.1.patch
COPY diff-0.2.2.patch diff-0.2.2.patch
COPY diff-0.2.3.patch diff-0.2.3.patch
COPY diff-0.2.9.patch diff-0.2.9.patch
COPY diff-0.2.9-totals.patch diff-0.2.9-totals.patch
COPY diff-0.2.9-cert.patch diff-0.2.9-cert.patch
COPY diff-0.2.9-progress.patch diff-0.2.9-progress.patch
COPY diff-0.2.9-json.patch diff-0.2.9-json.patch


CMD ["./runner.sh"]
