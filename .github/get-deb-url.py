#! /usr/bin/env python3
import os
import sys
import json
import platform

from argparse import ArgumentParser, RawTextHelpFormatter

import requests

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

    return parser


def get_build_url(s3_base_url, pr_number, branch, commit_hash):
    if ARCH == "x86_64":
        build_file = "build_amd_release/artifact_report_build_amd_release.json"
    elif ARCH == "aarch64":
        build_file = "build_arm_release/artifact_report_build_arm_release.json"

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
        )

    return None

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
                args.s3_base_url, args.pr_number, args.branch_name, args.commit_hash
            )
        build_report = requests.get(url)
        assert (
            build_report.status_code == 200
        ), f"Failed to get build report from {url}\n{build_report.status_code}\n{build_report.text}"
        build_report = build_report.json()
    else:
        assert args.reports_path is not None, "reports path must be set"
        reports_path = args.reports_path
        with open(
            os.path.join(reports_path, build_url),
            "r",
            encoding="utf-8",
        ) as file_handler:
            build_report = json.load(file_handler)

    for url in build_report["build_urls"]:
        if "clickhouse-common-static_" in url and "deb" in url:
            with open(github_env, "a") as f:
                f.write("version=" + url.split("/")[-1].split("_")[1] + "\n")
                f.write("clickhouse_path=" + url + "\n")
            sys.stdout.write(url)
            sys.exit(0)
