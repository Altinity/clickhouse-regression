#!/bin/bash
sudo chown -R $(whoami):$(whoami) $SUITE/

if [[ $artifacts == 'internal' ]]; then
    artifact_s3_bucket_path="altinity-internal-test-reports"
    artifact_s3_dir="clickhouse/$version/$GITHUB_RUN_ID/testflows"
    confidential="--confidential"
elif [[ $artifacts == 'public' ]]; then
    artifact_s3_bucket_path="altinity-test-reports"
    artifact_s3_dir="clickhouse/$version/$GITHUB_RUN_ID/testflows"
    confidential=""
elif [[ $artifacts == 'builds' ]]; then
    artifact_s3_bucket_path="altinity-build-artifacts"
    confidential=""
    if [[ $event_name == "pull_request" ]]; then
        artifact_s3_dir="$pr_number/$build_sha/regression"
    elif [[ $event_name == "release" || $event_name == "push" ]]; then
        artifact_s3_dir="0/$build_sha/regression"
    fi

fi

link="https://$artifact_s3_bucket_path.s3.amazonaws.com/index.html#$artifact_s3_dir/"
echo $link
