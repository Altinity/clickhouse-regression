#!/bin/bash

set -x
echo $version > version.log.txt
echo "https://gitlab.com/altinity-qa/clickhouse/cicd/clickhouse-regression/-/pipelines/$GITHUB_RUN_ID" > pipeline_url.log.txt
tfs --debug --no-colors transform compact raw.log compact.log
tfs --debug --no-colors transform nice raw.log nice.log.txt 
tfs --debug --no-colors transform short raw.log short.log.txt
tfs --debug --no-colors report coverage - raw.log - $confidential --copyright "Altinity Inc." --logo ./altinity.png | tfs --debug --no-colors document convert > coverage.html
tfs --debug --no-colors report results -a "https://$artifacts_s3_bucket_path.s3.amazonaws.com/index.html#clickhouse/$version/$GITHUB_RUN_ID/testflows/" raw.log - $confidential --copyright "Altinity Inc." --logo ./altinity.png | tfs --debug --no-colors document convert > report.html
tfs --debug --no-colors report compare results --log compact.log --order-by version $confidential --copyright "Altinity Inc." --logo ./altinity.png | tfs --debug --no-colors document convert > compare.html
