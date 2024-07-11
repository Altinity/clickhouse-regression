#!/bin/bash

set -x
sudo chown -R $(whoami):$(whoami) $SUITE/

echo $version > version.log.txt
echo "https://gitlab.com/altinity-qa/clickhouse/cicd/clickhouse-regression/-/pipelines/$GITHUB_RUN_ID" > pipeline_url.log.txt
tfs --debug --no-colors transform compact raw.log compact.log
tfs --debug --no-colors transform nice raw.log nice.log.txt 
tfs --debug --no-colors transform short raw.log short.log.txt
tfs --debug --no-colors transform brisk-new-fails raw.log brisk-new-fails.log.txt
tfs --debug --no-colors transform nice-new-fails raw.log nice-new-fails.log.txt
tfs --debug --no-colors report coverage - raw.log - $confidential --copyright "Altinity Inc." --logo ./altinity.png | tfs --debug --no-colors document convert > coverage.html
tfs --debug --no-colors report results -a "$JOB_REPORT_INDEX" raw.log - $confidential --copyright "Altinity Inc." --logo ./altinity.png | tfs --debug --no-colors document convert > report.html
tfs --debug --no-colors report compare results --log compact.log --order-by version $confidential --copyright "Altinity Inc." --logo ./altinity.png | tfs --debug --no-colors document convert > compare.html

#Specify whether logs should be uploaded.
if [[ $1 == 1 ]];
then
    echo "::notice title=$SUITE$STORAGE $(uname -i) s3 logs and reports::$REPORT_INDEX_URL"
    ./retry.sh 5 30 aws s3 cp pipeline_url.log.txt $JOB_S3_ROOT/pipeline_url.log.txt --content-type "\"text/plain; charset=utf-8\""
    ./retry.sh 5 30 aws s3 cp version.log.txt $SUITE_REPORT_BUCKET_PATH/version.log.txt --content-type "\"text/plain; charset=utf-8\""
    ./retry.sh 5 30 aws s3 cp raw.log $SUITE_REPORT_BUCKET_PATH/raw.log
    ./retry.sh 5 30 aws s3 cp compact.log $SUITE_REPORT_BUCKET_PATH/compact.log
    ./retry.sh 5 30 aws s3 cp nice.log.txt $SUITE_REPORT_BUCKET_PATH/nice.log.txt --content-type "\"text/plain; charset=utf-8\""
    ./retry.sh 5 30 aws s3 cp short.log.txt $SUITE_REPORT_BUCKET_PATH/short.log.txt --content-type "\"text/plain; charset=utf-8\""
    ./retry.sh 5 30 aws s3 cp brisk-new-fails.log.txt $SUITE_REPORT_BUCKET_PATH/brisk-new-fails.log.txt --content-type "\"text/plain; charset=utf-8\""
    ./retry.sh 5 30 aws s3 cp nice-new-fails.log.txt $SUITE_REPORT_BUCKET_PATH/nice-new-fails.log.txt --content-type "\"text/plain; charset=utf-8\""
    ./retry.sh 5 30 aws s3 cp report.html $SUITE_REPORT_BUCKET_PATH/report.html
    ./retry.sh 5 30 aws s3 cp compare.html $SUITE_REPORT_BUCKET_PATH/compare.html
    ./retry.sh 5 30 aws s3 cp coverage.html $SUITE_REPORT_BUCKET_PATH/coverage.html
    sudo rm --recursive --force $SUITE/_instances/*/database/
    ./retry.sh 5 30 "aws s3 cp --recursive . $SUITE_REPORT_BUCKET_PATH/"' --exclude "*" --include "*/_instances/*.log" --content-type "\"text/plain; charset=utf-8\"" --no-follow-symlinks'
fi
