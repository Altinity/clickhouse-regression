#!/bin/bash

set -x
sudo chown -R $(whoami):$(whoami) $SUITE/

echo $version > version.log.txt
tfs --debug --no-colors transform nice-new-fails raw.log nice-new-fails.log.txt
tfs --debug --no-colors transform fails raw.log fails.log.txt
tfs --debug --no-colors report results -a "$JOB_REPORT_INDEX" raw.log - $confidential --copyright "Altinity Inc." --logo ./altinity.png | tfs --debug --no-colors document convert > report.html
echo "Re-compress the raw.log"
cat raw.log | xzcat | xz -z -T $(nproc) - > raw.log.2
mv raw.log.2 raw.log

if [[ "$artifacts" == "hetzner" ]]; then
  export AWS_ACCESS_KEY_ID="$HETZNER_S3_KEY_ID"
  export AWS_SECRET_ACCESS_KEY="$HETZNER_S3_ACCESS_KEY"
  export AWS_DEFAULT_REGION="$HETZNER_S3_REGION"
fi

#Specify whether logs should be uploaded.
if [[ $1 == 1 ]];
then
    echo "::notice title=$SUITE$STORAGE $(uname -i) s3 logs and reports::$REPORT_INDEX_URL"
    ./retry.sh 5 30 aws $aws_endpoint_args s3 cp version.log.txt $SUITE_REPORT_BUCKET_PATH/version.log.txt --content-type "\"text/plain; charset=utf-8\""
    ./retry.sh 5 30 aws $aws_endpoint_args s3 cp raw.log $SUITE_REPORT_BUCKET_PATH/raw.log
    ./retry.sh 5 30 aws $aws_endpoint_args s3 cp nice-new-fails.log.txt $SUITE_REPORT_BUCKET_PATH/nice-new-fails.log.txt --content-type "\"text/plain; charset=utf-8\""
    ./retry.sh 5 30 aws $aws_endpoint_args s3 cp fails.log.txt $SUITE_REPORT_BUCKET_PATH/fails.log.txt --content-type "\"text/plain; charset=utf-8\""
    ./retry.sh 5 30 aws $aws_endpoint_args s3 cp report.html $SUITE_REPORT_BUCKET_PATH/report.html
    sudo rm --recursive --force $SUITE/_instances/*/database/
    ./retry.sh 5 30 "aws $aws_endpoint_args s3 cp --recursive . $SUITE_REPORT_BUCKET_PATH/"' --exclude "*" --include "*/_instances/*.log" --content-type "\"text/plain; charset=utf-8\"" --no-follow-symlinks'
    ./retry.sh 5 30 "aws $aws_endpoint_args s3 cp --recursive $SUITE/_service_logs/ $SUITE_REPORT_BUCKET_PATH/_service_logs/"' --exclude "*" --include "*.log" --content-type "\"text/plain; charset=utf-8\""'
fi
