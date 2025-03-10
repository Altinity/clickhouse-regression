import os
import sys
import json
import platform

from argparse import ArgumentParser, RawTextHelpFormatter


description = """List online GitHub Actions runners from specified repository.
"""


def argparser():
    """Command line argument parser."""
    parser = ArgumentParser(
        "Altinity GitHub Actions online runner list",
        description=description,
        formatter_class=RawTextHelpFormatter,
    )

    parser.add_argument(
        "--reports-path",
        type=str,
        help="Specify the report path where build_urls_package_release.json is located, default: /home/ubuntu/actions-runner/_work/_temp/reports_dir",
        default="/home/ubuntu/actions-runner/_work/_temp/reports_dir",
    )

    parser.add_argument(
        "--github-env",
        type=str,
        help="repository from which to list online runners, default: GITHUB_ENV",
        default=os.getenv("GITHUB_ENV"),
    )

    return parser


if __name__ == "__main__":
    args = argparser().parse_args()

    assert args.reports_path is not None, "reports path must be set"
    assert args.github_env is not None, "github env must be set"

    reports_path = args.reports_path
    github_env = args.github_env

    arch = platform.uname()[-1]
    if arch == "x86_64":
        build_url = "build_report_package_release.json"
    elif arch == "aarch64":
        build_url = "build_report_package_aarch64.json"
    else:
        raise Exception("Only x86_64 and ARM are supported.")

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
