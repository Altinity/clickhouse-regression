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
echo "artifact_s3_bucket_path=$artifact_s3_bucket_path" >> $GITHUB_ENV
echo "confidential=$confidential" >> $GITHUB_ENV
