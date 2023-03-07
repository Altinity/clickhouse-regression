#!/bin/bash

set -x
aws s3 cp pipeline_url.log.txt s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/pipeline_url.log.txt --content-type "text/plain; charset=utf-8"
aws s3 cp version.log.txt s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/example/version.log.txt --content-type "text/plain; charset=utf-8"
aws s3 cp raw.log s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/example/raw.log
aws s3 cp compact.log s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/example/compact.log
aws s3 cp nice.log.txt s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/example/nice.log.txt --content-type "text/plain; charset=utf-8"
aws s3 cp short.log.txt s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/example/short.log.txt --content-type "text/plain; charset=utf-8"
aws s3 cp report.html s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/example/report.html
aws s3 cp compare.html s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/example/compare.html
aws s3 cp coverage.html s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/example/coverage.html
rm --recursive --force example/_instances/*/database/
aws s3 cp . s3://$artifact_s3_bucket_path/clickhouse/$version/$GITHUB_RUN_ID/testflows/example/ --recursive --exclude "*" --include "*/_instances/*/logs/*.log" --content-type "text/plain; charset=utf-8"
