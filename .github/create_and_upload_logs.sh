#!/bin/bash

set -x
sudo chown -R $(whoami):$(whoami) $SUITE/

if [[ $artifacts == 'internal' ]];
then
    artifact_s3_bucket_path="altinity-internal-test-reports"
    artifact_s3_dir="clickhouse/$version/$GITHUB_RUN_ID/testflows"
    confidential="--confidential"
elif [[ $artifacts == 'public' ]];
then
    artifact_s3_bucket_path="altinity-test-reports"
    artifact_s3_dir="clickhouse/$version/$GITHUB_RUN_ID/testflows"
    confidential=""
elif [[ $artifacts == 'builds' ]];
then
    artifact_s3_bucket_path="altinity-build-artifacts"
    confidential=""
    if [[ $event_name == "pull_request" ]];
    then
        artifact_s3_dir="$pr_number/$build_sha/regression"
    elif [[ $event_name == "release" || $event_name == "push" ]];
    then
        artifact_s3_dir="0/$build_sha/regression"
    fi
    
fi

echo $version > version.log.txt
echo "https://gitlab.com/altinity-qa/clickhouse/cicd/clickhouse-regression/-/pipelines/$GITHUB_RUN_ID" > pipeline_url.log.txt
tfs --debug --no-colors transform compact raw.log compact.log
tfs --debug --no-colors transform nice raw.log nice.log.txt 
tfs --debug --no-colors transform short raw.log short.log.txt
tfs --debug --no-colors transform brisk-new-fails raw.log brisk-new-fails.log.txt
tfs --debug --no-colors transform nice-new-fails raw.log nice-new-fails.log.txt
tfs --debug --no-colors report coverage - raw.log - $confidential --copyright "Altinity Inc." --logo ./altinity.png | tfs --debug --no-colors document convert > coverage.html
tfs --debug --no-colors report results -a "https://$artifact_s3_bucket_path.s3.amazonaws.com/index.html#$artifact_s3_dir/" raw.log - $confidential --copyright "Altinity Inc." --logo ./altinity.png | tfs --debug --no-colors document convert > report.html
tfs --debug --no-colors report compare results --log compact.log --order-by version $confidential --copyright "Altinity Inc." --logo ./altinity.png | tfs --debug --no-colors document convert > compare.html

#Specify whether logs should be uploaded.
if [[ $1 == 1 ]];
then
    echo "::notice title=$SUITE$STORAGE $(uname -i) s3 logs and reports::https://$artifact_s3_bucket_path.s3.amazonaws.com/index.html#$artifact_s3_dir/$(uname -i)/$SUITE$STORAGE/"
    ./retry.sh 5 30 aws s3 cp pipeline_url.log.txt s3://$artifact_s3_bucket_path/$artifact_s3_dir/pipeline_url.log.txt --content-type "text/plain; charset=utf-8"
    ./retry.sh 5 30 aws s3 cp version.log.txt s3://$artifact_s3_bucket_path/$artifact_s3_dir/$(uname -i)/$SUITE$STORAGE/version.log.txt --content-type "text/plain; charset=utf-8"
    ./retry.sh 5 30 aws s3 cp raw.log s3://$artifact_s3_bucket_path/$artifact_s3_dir/$(uname -i)/$SUITE$STORAGE/raw.log
    ./retry.sh 5 30 aws s3 cp compact.log s3://$artifact_s3_bucket_path/$artifact_s3_dir/$(uname -i)/$SUITE$STORAGE/compact.log
    ./retry.sh 5 30 aws s3 cp nice.log.txt s3://$artifact_s3_bucket_path/$artifact_s3_dir/$(uname -i)/$SUITE$STORAGE/nice.log.txt --content-type "text/plain; charset=utf-8"
    ./retry.sh 5 30 aws s3 cp short.log.txt s3://$artifact_s3_bucket_path/$artifact_s3_dir/$(uname -i)/$SUITE$STORAGE/short.log.txt --content-type "text/plain; charset=utf-8"
    ./retry.sh 5 30 aws s3 cp brisk-new-fails.log.txt s3://$artifact_s3_bucket_path/$artifact_s3_dir/$(uname -i)/$SUITE$STORAGE/brisk-new-fails.log.txt --content-type "text/plain; charset=utf-8" --metadata-directive REPLACE
    ./retry.sh 5 30 aws s3 cp nice-new-fails.log.txt s3://$artifact_s3_bucket_path/$artifact_s3_dir/$(uname -i)/$SUITE$STORAGE/nice-new-fails.log.txt --content-type "text/plain; charset=utf-8" --metadata-directive REPLACE
    ./retry.sh 5 30 aws s3 cp report.html s3://$artifact_s3_bucket_path/$artifact_s3_dir/$(uname -i)/$SUITE$STORAGE/report.html
    ./retry.sh 5 30 aws s3 cp compare.html s3://$artifact_s3_bucket_path/$artifact_s3_dir/$(uname -i)/$SUITE$STORAGE/compare.html   
    ./retry.sh 5 30 aws s3 cp coverage.html s3://$artifact_s3_bucket_path/$artifact_s3_dir/$(uname -i)/$SUITE$STORAGE/coverage.html
    sudo rm --recursive --force $SUITE/_instances/*/database/
    ./retry.sh 5 30 'aws s3 cp --recursive . s3://'"$artifact_s3_bucket_path"'/'"$artifact_s3_dir"'/'"$(uname -i)"'/'"$SUITE$STORAGE"'/ --exclude "*" --include "*/_instances/*.log" --content-type "text/plain; charset=utf-8" --no-follow-symlinks'
fi
