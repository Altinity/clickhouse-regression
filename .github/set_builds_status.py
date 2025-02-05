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

# Get log summary
status_message = (
    subprocess.getoutput("tfs transform new-fails raw.log").strip() or "Job completed"
)

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
    exit(1)
