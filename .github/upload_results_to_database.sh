
#!/bin/bash

set -x

if [[ $1 == 1 ]];
then
    ./.github/upload_results_to_database.py -o nice-new-fails --log-file raw.log --db-name="gh-data" --db-port=9440 --secure --no-verify --table="clickhouse_regression_results" --log uploader.log
    aws s3 cp uploader.log $SUITE_REPORT_BUCKET_PATH/uploader.log
fi
