#! /usr/bin/env python3
"""
Set commit status on GitHub based on the outcome of a regression test.
Used by the builds pipeline.
"""
import os
import subprocess
import requests

# Get environment variables
token = os.getenv("GITHUB_TOKEN")
repo_name = os.getenv("GITHUB_REPOSITORY")
sha = os.getenv("build_sha")
job_outcome = os.getenv("JOB_OUTCOME", "pending")
suite = os.getenv("SUITE_NAME")
target_url = f"{os.getenv('SUITE_LOG_FILE_PREFIX_URL')}/report.html"

# Map job outcomes to commit status states
state = {
    "success": "success",
    "failure": "failure",
    "cancelled": "error",
}.get(job_outcome, "pending")


def make_status_message():
    # Get log summary
    # 140 characters max
    status_message = (
        subprocess.getoutput("tfs --no-color show totals raw.log").strip()
        or "Job completed"
    )

    # Keep the first 3 lines and the last line of tfs show totals
    status_lines = status_message.splitlines()
    if len(status_lines) > 4:
        status_message = "\n".join(status_lines[:3] + status_lines[-1:])

    return status_message[:140]


if state == "error":
    status_message = "Job did not complete"
else:
    status_message = make_status_message()

# GitHub API request to set commit status
response = requests.post(
    f"https://api.github.com/repos/{repo_name}/statuses/{sha}",
    headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    },
    json={
        "state": state,
        "context": suite,
        "description": status_message,
        "target_url": target_url,
    },
)

# Print result
if response.status_code == 201:
    print(f"✅ Commit status set: {suite} - {state}")
else:
    print(f"❌ Failed to set commit status: {response.text}")
    print(f"Headers sent: {response.request.headers}")
    print(f"Headers received: {response.headers}")
    exit(1)
