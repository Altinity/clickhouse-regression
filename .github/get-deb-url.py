#! /usr/bin/env python3
import os
import re
import sys
import json
import platform

from argparse import ArgumentParser, RawTextHelpFormatter
from urllib.parse import urlparse

import boto3
import requests

_S3_VIRTUAL_HOST = re.compile(
    r"^(?P<bucket>[^.]+)\.s3(?:[.-](?P<region>[^.]+))?\.amazonaws\.com$"
)

description = """Get the deb url from the builds report for the builds pipeline.
"""

ARCH = platform.uname()[-1]


def argparser():
    """Command line argument parser."""
    parser = ArgumentParser(
        "Altinity GitHub Actions Get Deb Url",
        description=description,
        formatter_class=RawTextHelpFormatter,
    )

    parser.add_argument(
        "--reports-path",
        type=str,
        help="Specify the report path where build_urls_package_release.json is located, for workflow<25.4, default: /home/ubuntu/actions-runner/_work/_temp/reports_dir",
        default="/home/ubuntu/actions-runner/_work/_temp/reports_dir",
    )

    parser.add_argument(
        "--github-env",
        type=str,
        help="repository from which to list online runners, default: GITHUB_ENV",
        default=os.getenv("GITHUB_ENV"),
    )

    group = parser.add_argument_group("25.4+ workflow parameters")
    group.add_argument(
        "--workflow-config-file", type=str, help="Workflow config file", default=None
    )
    group.add_argument("--s3-base-url", type=str, help="S3 base url", default=None)
    group.add_argument("--pr-number", type=int, help="PR number", default=None)
    group.add_argument("--branch-name", type=str, help="Branch name", default=None)
    group.add_argument("--commit-hash", type=str, help="Commit hash", default=None)
    group.add_argument(
        "--binary", action="store_true", help="Return binary url instead of deb url"
    )

    return parser


def get_build_url(s3_base_url, pr_number, branch, commit_hash, build="release"):
    if ARCH == "x86_64":
        build_file = f"build_amd_{build}/artifact_report_build_amd_{build}.json"
    elif ARCH == "aarch64":
        build_file = f"build_arm_{build}/artifact_report_build_arm_{build}.json"

    if pr_number == 0 or pr_number is None:
        return f"{s3_base_url.rstrip('/')}/REFs/{branch}/{commit_hash}/{build_file}"
    else:
        return f"{s3_base_url.rstrip('/')}/PRs/{pr_number}/{commit_hash}/{build_file}"


def get_cached_build_url(workflow_config_file, s3_base_url):
    with open(workflow_config_file, "r") as f:
        workflow_config = json.load(f)

    if ARCH == "x86_64":
        build_arch = "amd"
    elif ARCH == "aarch64":
        build_arch = "arm"
    else:
        raise Exception("Only x86_64 and ARM are supported.")

    for build_type in ["release", "binary"]:
        print(f"Checking cache for {build_arch}_{build_type}")
        cache_details = workflow_config["cache_artifacts"].get(
            f"Build ({build_arch}_{build_type})"
        )
        if cache_details is None or cache_details["type"] != "success":
            continue

        return get_build_url(
            s3_base_url,
            cache_details["pr_number"],
            cache_details["branch"],
            cache_details["sha"],
            build_type,
        )

    return None


def has_aws_creds():
    return bool(os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"))


def parse_s3_http_url(url):
    parsed = urlparse(url)
    match = _S3_VIRTUAL_HOST.match(parsed.netloc)
    if match:
        return match.group("bucket"), parsed.path.lstrip("/")
    path = parsed.path.lstrip("/")
    bucket, _, key = path.partition("/")
    if not bucket or not key:
        raise ValueError(f"Not an S3 HTTP URL: {url}")
    return bucket, key


def fetch_json(url):
    if has_aws_creds():
        print(f"AWS creds set; fetching {url} with signed S3")
        bucket, key = parse_s3_http_url(url)
        body = boto3.client("s3").get_object(Bucket=bucket, Key=key)["Body"].read()
        return json.loads(body)

    print(f"No AWS creds; fetching {url} anonymously")
    response = requests.get(url, timeout=60)
    assert (
        response.status_code == 200
    ), f"Failed to get build report from {url}\n{response.status_code}\n{response.text}"
    return response.json()


def materialize_artifact(url):
    """Return a local path for a private S3 object.

    A presigned URL contains '&'. The regression workflow inserts
    clickhouse_path unquoted, and the downloader uses everything after the
    last '/' as the output filename, so the query string breaks both.

    The file must also sit inside this repo. Docker build context is the
    repo root, and the package path is passed to COPY. A file under the
    runner temp directory is outside that context, so the image build fails
    and the cluster does not start. helpers/cluster.py stores URL downloads
    in binaries/.
    """
    if not has_aws_creds():
        return url
    bucket, key = parse_s3_http_url(url)
    filename = os.path.basename(key)
    if not filename or filename in (".", ".."):
        raise ValueError(f"Cannot derive a local filename from {url}")
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dest_dir = os.path.join(repo_root, "binaries")
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, filename)
    if os.path.isfile(dest) and os.path.getsize(dest) > 0:
        return dest
    partial = dest + ".partial"
    print(f"Downloading s3://{bucket}/{key} to {dest}", file=sys.stderr)
    boto3.client("s3").download_file(bucket, key, partial)
    os.replace(partial, dest)
    return dest


if __name__ == "__main__":
    args = argparser().parse_args()

    assert args.github_env is not None, "github env must be set"
    github_env = args.github_env

    if ARCH == "x86_64":
        build_url = "build_report_package_release.json"
    elif ARCH == "aarch64":
        build_url = "build_report_package_aarch64.json"
    else:
        raise Exception("Only x86_64 and ARM are supported.")

    if args.workflow_config_file is not None:
        assert args.pr_number is not None, "pr number must be set"
        assert args.branch_name is not None, "branch name must be set"
        assert args.commit_hash is not None, "commit hash must be set"
        assert args.s3_base_url is not None, "s3 base url must be set"

        url = get_cached_build_url(args.workflow_config_file, args.s3_base_url)
        if url is None:
            url = get_build_url(
                args.s3_base_url,
                args.pr_number,
                args.branch_name,
                args.commit_hash,
                # This is a good heuristic
                "binary" if args.binary else "release",
            )
        build_report = fetch_json(url)
    else:
        assert args.reports_path is not None, "reports path must be set"
        reports_path = args.reports_path
        with open(
            os.path.join(reports_path, build_url),
            "r",
            encoding="utf-8",
        ) as file_handler:
            build_report = json.load(file_handler)

    if args.binary:
        is_desired_file = lambda url: url.endswith("/clickhouse")
    else:
        is_desired_file = (
            lambda url: "clickhouse-common-static_" in url and "deb" in url
        )

    for url in build_report["build_urls"]:
        if is_desired_file(url):
            artifact_url = materialize_artifact(url)
            with open(github_env, "a") as f:
                f.write("clickhouse_path=" + artifact_url + "\n")
                if not args.binary:  # cannot get version from binary url
                    f.write("version=" + url.split("/")[-1].split("_")[1] + "\n")
            sys.stdout.write(artifact_url)
            sys.exit(0)
