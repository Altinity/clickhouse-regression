#!/usr/bin/env python3
"""One-shot Step 0: from an error-message token to mechanism, culprit PR and blast radius.

Collapses what would otherwise be four to six sequential rounds of API calls into a
single run, with the independent lookups issued in parallel. Wall-clock cost of a
source investigation is round-trips, not requests - this exists to remove them.

Usage
  source_forensics.py --token "<distinctive string from the error>"
  source_forensics.py --token s3_allow_server_credentials_in_user_queries
  source_forensics.py --token "Maybe you meant" --pr 110633
  source_forensics.py --token "<tok>" --path src/Core/Settings.cpp --refs a b c

Needs `gh` authenticated. Everything is read-only; nothing is cloned or fetched.
"""
import argparse, json, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

UPSTREAM = "ClickHouse/ClickHouse"
FORK = "Altinity/ClickHouse"
DEFAULT_REFS = [
    f"{UPSTREAM}:master",
    f"{FORK}:antalya-26.6",
    f"{FORK}:antalya-25.8",
    f"{FORK}:25.8",
]


def gh(*args):
    try:
        out = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60)
        return out.stdout if out.returncode == 0 else ""
    except Exception:
        return ""


def raw(repo, ref, path):
    """Fetch a file at a ref. Uses raw, not the contents API, which caps at 1 MB."""
    url = f"https://raw.githubusercontent.com/{repo}/{ref}/{path}"
    try:
        out = subprocess.run(["curl", "-sfL", url], capture_output=True, text=True, timeout=60)
        return out.stdout if out.returncode == 0 else None
    except Exception:
        return None


def find_files(token):
    """Which files contain this? Code search indexes the default branch only."""
    out = gh("api", "-X", "GET", "search/code", "-f",
             f"q={token} repo:{UPSTREAM}", "--jq", ".items[].path")
    paths = [p for p in out.splitlines() if p]
    # Source first: docs mention every setting and drown the file that implements it.
    src = [p for p in paths if p.startswith("src/")]
    other = [p for p in paths if not p.startswith("src/") and not p.startswith("docs/")]
    docs = [p for p in paths if p.startswith("docs/")]
    return (src + other + docs)[:10], len(src)


def find_prs(token):
    out = gh("api", "-X", "GET", "search/issues", "-f",
             f"q=repo:{UPSTREAM} {token} type:pr", "-f", "per_page=50", "--jq",
             '.items[] | "\\(.number)\\t\\(.closed_at // "open")\\t\\(.title)"')
    rows = [l.split("\t") for l in out.splitlines() if l]
    # The PR that INTRODUCED a name is the earliest merged one that mentions it;
    # relevance ranking puts unrelated open PRs on top.
    merged = sorted([r for r in rows if r[1] != "open"], key=lambda r: r[1])
    return merged, [r for r in rows if r[1] == "open"]


def pr_detail(number):
    out = gh("api", f"repos/{UPSTREAM}/pulls/{number}", "--jq",
             '{n:.number, merged:.merged_at, sha:.merge_commit_sha, title:.title}')
    try:
        return json.loads(out)
    except Exception:
        return None


def changelog_for_pr(number):
    """Which release shipped it, in the project's own words.

    Lists the changelog files first - guessing a release filename wastes a round and
    the names are not predictable.
    """
    names = [n for n in gh("api", f"repos/{UPSTREAM}/contents/docs/changelogs",
                           "--jq", ".[].name").splitlines() if n.startswith("v")]

    def ver_key(n):
        m = re.match(r"v(\d+)\.(\d+)\.(\d+)\.(\d+)", n)
        return tuple(int(x) for x in m.groups()) if m else (0, 0, 0, 0)

    hits = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        cands = sorted(names, key=ver_key, reverse=True)[:25]
        for name, body in zip(cands, ex.map(
                lambda n: raw(UPSTREAM, "master", f"docs/changelogs/{n}"), cands)):
            if body and f"#{number}" in body:
                for line in body.splitlines():
                    if f"/{number}" in line or f"#{number}" in line:
                        hits.append((name, line.strip()))
                        break
    return sorted(hits, key=lambda h: ver_key(h[0]))[:3]


def blast_radius(token, path, refs):
    def probe(spec):
        repo, ref = spec.split(":", 1)
        body = raw(repo, ref, path)
        if body is None:
            return spec, "no such ref or path"
        return spec, ("PRESENT - affected" if token in body else "absent - not affected")

    with ThreadPoolExecutor(max_workers=8) as ex:
        return list(ex.map(probe, refs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", required=True, help="distinctive string from the error")
    ap.add_argument("--pr", type=int, help="PR number, if already known")
    ap.add_argument("--path", help="file to probe for blast radius (default: first code-search hit)")
    ap.add_argument("--refs", nargs="*", default=DEFAULT_REFS, help="repo:ref pairs")
    a = ap.parse_args()

    with ThreadPoolExecutor(max_workers=3) as ex:
        f_files = ex.submit(find_files, a.token)
        f_prs = ex.submit(find_prs, a.token)
        (files, n_src), (prs, open_prs) = f_files.result(), f_prs.result()

    print(f"# token: {a.token}\n")
    print("## Files (default branch, source first)")
    print("\n".join(f"  {p}" for p in files) or "  (none - try a shorter or more distinctive token)")
    if files and not n_src:
        print("  ! no src/ hit - the token may be documentation-only, or too generic")

    print("\n## Merged PRs mentioning it, oldest first (the first is usually the one that introduced it)")
    for n, closed, title in prs[:8]:
        print(f"  #{n:<8} {closed[:10]:<12} {title[:76]}")
    if open_prs:
        print(f"  ({len(open_prs)} open PR(s) also mention it - ignored for attribution)")

    # `closed_at` from search does not distinguish merged from closed-unmerged, and a
    # rejected PR sorts first just as easily. Confirm before attributing.
    generic = len(prs) + len(open_prs) > 20
    if generic and a.pr is None:
        print(f"\n  ! '{a.token}' matches {len(prs) + len(open_prs)} PRs - too generic to attribute.")
        print("    Narrow the token to the exact new wording, or pick from the list and re-run")
        print("    with --pr <n>. Blast radius below is also unreliable for a generic token:")
        print("    it can only tell you the phrase is present, not that this change is.")

    pr = a.pr
    if pr is None and prs and not generic:
        with ThreadPoolExecutor(max_workers=4) as ex:
            for cand, det in zip(prs[:4], ex.map(lambda r: pr_detail(int(r[0])), prs[:4])):
                if det and det.get("merged"):
                    pr = int(cand[0])
                    break
        if pr is None:
            pr = int(prs[0][0])
            print("\n  ! none of the top candidates was actually merged - verify attribution by hand")

    if pr:
        with ThreadPoolExecutor(max_workers=2) as ex:
            f_d, f_c = ex.submit(pr_detail, pr), ex.submit(changelog_for_pr, pr)
            d, chg = f_d.result(), f_c.result()
        print(f"\n## PR #{pr}")
        if d:
            print(f"  title:     {d['title']}")
            print(f"  merged at: {d['merged']}   (use THIS date, not the commit's author date)")
            print(f"  merge sha: {d['sha']}")
        print("  changelog:")
        for name, line in (chg or []):
            print(f"    {name}\n      {line[:150]}")
        if not chg:
            print("    (not found in the 25 most recent changelogs)")

    path = a.path or (files[0] if files else None)
    if path:
        print(f"\n## Blast radius ({path})")
        for spec, state in blast_radius(a.token, path, a.refs):
            print(f"  {spec:<42} {state}")
    else:
        print("\n## Blast radius: skipped (no path - pass --path)")


if __name__ == "__main__":
    main()
