#! /usr/bin/env python3
"""
Set commit status on GitHub based on the outcome of a regression test.
Used by the builds pipeline.
"""
import os
import subprocess
from github import Github

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

# Run generate_message.sh and get output
status_message = (
    subprocess.getoutput("tfs transform new-fails raw.log").strip() or "Job completed"
)

# Set commit status using PyGithub
Github(token).get_repo(repo_name).get_commit(sha).create_status(
    state=state,
    description=status_message,
    context=suite,
    target_url=target_url,
)

print(f"✅ Commit status set: {suite} - {state}")
