
#!/bin/bash

set -x

if [[ "$artifacts" == "hetzner" ]]; then
  export AWS_ACCESS_KEY_ID="$HETZNER_S3_KEY_ID"
  export AWS_SECRET_ACCESS_KEY="$HETZNER_S3_ACCESS_KEY"
  export AWS_DEFAULT_REGION="$HETZNER_S3_REGION"
fi

if [[ $1 == 1 ]];
then
    ./retry.sh 5 30 timeout 8m ./.github/upload_results_to_database.py -o nice --log-file raw.log --db-name="gh-data" --db-port=8443 --secure --no-verify --table="clickhouse_regression_results" --log uploader.log || echo "Failed ($?) to upload results to database"
    aws $aws_endpoint_args s3 cp uploader.log $SUITE_REPORT_BUCKET_PATH/uploader.log
fi
