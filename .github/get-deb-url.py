import os
import sys
import json

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
        "--report-path",
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

    assert args.report_path is not None, "report path must be set"
    assert args.github_env is not None, "github env must be set"

    report_path = os.getenv("REPORT_PATH")
    github_env = os.getenv("GITHUB_ENV")

    with open(os.path.join(report_path, "build_urls_package_release"), "r", encoding="utf-8") as file_handler:
        build_report = json.load(file_handler)

    for url in build_report["build_urls"]:
        if "clickhouse-common-static" in url and "deb" in url:
            with open(github_env, "a") as f:
                f.write("version=" + url.split("/")[-1].split("_")[1])
            sys.stdout.write(url)
            sys.exit(0)
