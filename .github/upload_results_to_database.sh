
#!/bin/bash

set -x

aws_endpoint_args=""
if [[ -n "${S3_CLI_ENDPOINT_URL:-}" ]]; then
    aws_endpoint_args="--endpoint-url $S3_CLI_ENDPOINT_URL"
fi

if [[ $1 == 1 ]];
then
    ./retry.sh 5 30 timeout 8m ./.github/upload_results_to_database.py -o nice --log-file raw.log --db-name="gh-data" --db-port=8443 --secure --no-verify --table="clickhouse_regression_results" --log uploader.log || echo "Failed ($?) to upload results to database"
    aws $aws_endpoint_args s3 cp uploader.log $SUITE_REPORT_BUCKET_PATH/uploader.log
fi
