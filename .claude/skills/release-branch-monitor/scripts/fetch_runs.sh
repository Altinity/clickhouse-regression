#!/usr/bin/env bash
# Fetch the latest N MasterCI workflow runs for a given branch.
#
# Usage: fetch_runs.sh <branch> [num_runs]
# Example: fetch_runs.sh antalya-26.1 3
#
# Outputs TSV: run_id<TAB>commit_sha<TAB>created_at<TAB>conclusion<TAB>title
# Requires: gh CLI authenticated to Altinity/ClickHouse.

set -euo pipefail

BRANCH="${1:?branch required, e.g. antalya-26.1}"
N="${2:-3}"

gh api -H "Accept: application/vnd.github+json" \
  "repos/Altinity/ClickHouse/actions/workflows/master.yml/runs?branch=${BRANCH}&per_page=${N}" \
  --jq '.workflow_runs[] | [.id, .head_sha, .created_at, (.conclusion // "in_progress"), .display_title] | @tsv'
