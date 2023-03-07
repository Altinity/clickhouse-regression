#!/bin/bash

set -x

if [[ $artifacts == 'internal' ]];
then
    artifact_s3_bucket_path="altinity-internal-test-reports"
    confidential="--confidential"
elif [[ $artifacts == 'public' ]];
then
    artifact_s3_bucket_path="altinity-test-reports"
    confidential=""
fi

echo $version > version.log.txt
echo "https://gitlab.com/altinity-qa/clickhouse/cicd/clickhouse-regression/-/pipelines/$GITHUB_RUN_ID" > pipeline_url.log.txt
tfs --debug --no-colors transform compact raw.log compact.log
tfs --debug --no-colors transform nice raw.log nice.log.txt 
tfs --debug --no-colors transform short raw.log short.log.txt
tfs --debug --no-colors report coverage - raw.log - $confidential --copyright "Altinity Inc." --logo ./altinity.png | tfs --debug --no-colors document convert > coverage.html
tfs --debug --no-colors report results -a "https://$artifacts_s3_bucket_path.s3.amazonaws.com/index.html#clickhouse/$version/$GITHUB_RUN_ID/testflows/" raw.log - $confidential --copyright "Altinity Inc." --logo ./altinity.png | tfs --debug --no-colors document convert > report.html
tfs --debug --no-colors report compare results --log compact.log --order-by version $confidential --copyright "Altinity Inc." --logo ./altinity.png | tfs --debug --no-colors document convert > compare.html

if [[ $UPLOAD_LOGS == 1 ]];
then
    aws s3 cp pipeline_url.log.txt s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/pipeline_url.log.txt --content-type "text/plain; charset=utf-8"
    aws s3 cp version.log.txt s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/$SUITE/version.log.txt --content-type "text/plain; charset=utf-8"
    aws s3 cp raw.log s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/$SUITE/raw.log
    aws s3 cp compact.log s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/$SUITE/compact.log
    aws s3 cp nice.log.txt s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/$SUITE/nice.log.txt --content-type "text/plain; charset=utf-8"
    aws s3 cp short.log.txt s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/$SUITE/short.log.txt --content-type "text/plain; charset=utf-8"
    aws s3 cp report.html s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/$SUITE/report.html
    aws s3 cp compare.html s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/$SUITE/compare.html
    aws s3 cp coverage.html s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/$SUITE/coverage.html
    rm --recursive --force $SUITE/_instances/*/database/
    aws s3 cp . s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/$SUITE/ --recursive --exclude "*" --include "*/_instances/*/logs/*.log" --content-type "text/plain; charset=utf-8"
    aws s3 cp . s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/$SUITE/ --recursive --exclude "*" --include "*/_instances/*.log" --content-type "text/plain; charset=utf-8"
fi
