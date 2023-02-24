#!/usr/bin/env python3
import os
import json
import time
import requests

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
        "--token",
        type=str,
        help="token with admin privileges to access GitHub API, default: GH_ROBOT_TOKEN env variable",
        default=os.getenv("GH_ROBOT_TOKEN"),
    )

    parser.add_argument(
        "--repo",
        type=str,
        help="repository from which to list online runners, default: RUNNER_REPO env variable",
        default=os.getenv("RUNNER_REPO"),
    )

    return parser


if __name__ == "__main__":
    args = argparser().parse_args()

    assert args.token is not None, "token must be set"
    assert args.repo is not None, "repository must be set"

    start_time = time.time()
    timeout = 60
    retry_delay=10
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {args.token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    while True:
        response = requests.get(
            f"https://api.github.com/repos/altinity/{args.repo}/actions/runners",
            headers=headers,
        )

        response_content = response.content.decode("utf-8")

        if response.status_code == 200:
            for runner in json.loads(response_content)["runners"]:
                if runner["status"] == "online":
                    print(f"    Runner\033[94m {runner['name']}\033[0m is online \033[92m\u2714\033[0m")

        else:
            print("API get request failed")
            print(response_content)
            print("Retrying...")
            time.sleep(retry_delay)

            if time.time() - start_time > timeout:
                break

        break
