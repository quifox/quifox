#!/usr/bin/env python3

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

API_ROOT = "https://api.github.com"
START = "<!-- OSS-CONTRIBUTIONS:START -->"
END = "<!-- OSS-CONTRIBUTIONS:END -->"
README_PATH = Path("README.md")


def api_get(path, token, params=None):
    url = API_ROOT + path
    if params:
        url += "?" + urllib.parse.urlencode(params)

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "profile-contributions-updater",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {exc.code} for {url}: {body}") from exc


def search_prs(query, token):
    items = []

    # GitHub's Search API exposes at most the first 1,000 matching results.
    for page in range(1, 11):
        data = api_get(
            "/search/issues",
            token,
            {
                "q": query,
                "per_page": 100,
                "page": page,
                "sort": "updated",
                "order": "desc",
            },
        )
        batch = data.get("items", [])
        items.extend(batch)

        if len(batch) < 100 or len(items) >= min(data.get("total_count", 0), 1000):
            break

    return items


def repo_name_from_api_url(repository_url):
    prefix = API_ROOT + "/repos/"
    if not repository_url.startswith(prefix):
        return None
    return repository_url[len(prefix):]


def is_public_external_repo(repo_name, username, token, cache):
    if not repo_name:
        return False

    owner = repo_name.split("/", 1)[0]
    if owner.casefold() == username.casefold():
        return False

    if repo_name not in cache:
        try:
            repo = api_get(f"/repos/{repo_name}", token)
            cache[repo_name] = not bool(repo.get("private", True))
        except RuntimeError as exc:
            # Fail closed: if visibility cannot be verified, do not publish it.
            print(f"Skipping {repo_name}: {exc}", file=sys.stderr)
            cache[repo_name] = False

    return cache[repo_name]


def normalize_title(title):
    return " ".join((title or "").replace("\r", " ").replace("\n", " ").split())


def direct_contributions(username, token, visibility_cache):
    items = search_prs(f"author:{username} is:pr is:merged", token)
    contributions = []

    for item in items:
        pull = item.get("pull_request") or {}
        if not pull.get("merged_at"):
            continue

        if item.get("author_association") == "OWNER":
            continue

        repo_name = repo_name_from_api_url(item.get("repository_url", ""))
        if not is_public_external_repo(repo_name, username, token, visibility_cache):
            continue

        contributions.append(
            {
                "repo": repo_name,
                "number": item["number"],
                "title": normalize_title(item.get("title")),
                "url": item.get("html_url"),
                "landed_number": None,
                "landed_url": None,
            }
        )

    return contributions


def pull_commits(repo_name, pr_number, token):
    commits = []
    for page in range(1, 11):
        batch = api_get(
            f"/repos/{repo_name}/pulls/{pr_number}/commits",
            token,
            {"per_page": 100, "page": page},
        )
        commits.extend(batch)
        if len(batch) < 100:
            break
    return commits


def merged_prs_for_commit(repo_name, sha, token):
    pulls = api_get(f"/repos/{repo_name}/commits/{sha}/pulls", token)
    return [pr for pr in pulls if pr.get("merged_at")]


def promoted_contributions(username, token, visibility_cache):
    # A contribution can land through a maintainer-authored PR while preserving
    # the contributor's original commits. Detect that case using exact commit
    # identity, rather than assuming that similar code or a mention is enough.
    items = search_prs(f"author:{username} is:pr is:closed -is:merged", token)
    contributions = []

    for item in items:
        if item.get("author_association") == "OWNER":
            continue

        repo_name = repo_name_from_api_url(item.get("repository_url", ""))
        if not is_public_external_repo(repo_name, username, token, visibility_cache):
            continue

        source_number = item["number"]
        try:
            commits = pull_commits(repo_name, source_number, token)
        except RuntimeError as exc:
            print(f"Skipping {repo_name}#{source_number}: {exc}", file=sys.stderr)
            continue

        candidates = {}
        for commit in commits:
            sha = commit.get("sha")
            if not sha:
                continue

            try:
                associated = merged_prs_for_commit(repo_name, sha, token)
            except RuntimeError as exc:
                print(f"Skipping commit {sha[:12]} in {repo_name}: {exc}", file=sys.stderr)
                continue

            for pr in associated:
                number = pr.get("number")
                if not number or number == source_number:
                    continue

                # If the user authored the merged PR too, the direct path will
                # already show it. This branch is specifically for maintainer
                # promotions / re-submissions that preserve the user's commits.
                if (pr.get("user") or {}).get("login", "").casefold() == username.casefold():
                    continue

                candidates[number] = pr

        if not candidates:
            continue

        # Prefer the earliest merged PR containing the preserved commit(s);
        # later PRs may simply be backports of the same change.
        landed = min(
            candidates.values(),
            key=lambda pr: (pr.get("merged_at") or "9999", pr.get("number") or 10**12),
        )

        contributions.append(
            {
                "repo": repo_name,
                "number": source_number,
                "title": normalize_title(item.get("title")),
                "url": item.get("html_url"),
                "landed_number": landed["number"],
                "landed_url": landed.get("html_url"),
            }
        )

    return contributions


def build_markdown(username, token):
    grouped = defaultdict(list)
    visibility_cache = {}

    contributions = direct_contributions(username, token, visibility_cache)
    contributions.extend(promoted_contributions(username, token, visibility_cache))

    # Deduplicate by the contributor's original PR. The original PR number is
    # also the stable sorting key for both direct and maintainer-landed changes.
    unique = {}
    for contribution in contributions:
        key = (contribution["repo"].casefold(), contribution["number"])
        unique[key] = contribution

    for contribution in unique.values():
        grouped[contribution["repo"]].append(contribution)

    if not grouped:
        return "_No merged external public pull requests found._"

    lines = []
    for repo_name in sorted(grouped, key=str.casefold):
        repo_url = f"https://github.com/{repo_name}"
        lines.append(f"#### [{repo_name}]({repo_url})")
        lines.append("")

        # Sort by the contributor's original PR number, newest/highest first.
        prs = sorted(grouped[repo_name], key=lambda pr: pr["number"], reverse=True)

        for pr in prs:
            if pr["landed_number"]:
                pr_label = (
                    f'[#{pr["number"]}]({pr["url"]}) → '
                    f'[#{pr["landed_number"]}]({pr["landed_url"]})'
                )
            else:
                pr_label = f'[#{pr["number"]}]({pr["url"]})'

            lines.append(f'- {pr_label} — {pr["title"]}')

        lines.append("")

    return "\n".join(lines).rstrip()


def update_readme(generated):
    if not README_PATH.exists():
        raise RuntimeError("README.md not found")

    content = README_PATH.read_text(encoding="utf-8")
    block = f"{START}\n{generated}\n{END}"

    if START in content and END in content:
        pattern = re.compile(
            re.escape(START) + r".*?" + re.escape(END),
            flags=re.DOTALL,
        )
        updated = pattern.sub(block, content, count=1)
    else:
        updated = content.rstrip() + "\n\n### Open Source Contributions\n\n" + block + "\n"

    if updated != content:
        README_PATH.write_text(updated, encoding="utf-8")


def main():
    username = os.environ.get("GITHUB_USERNAME")
    token = os.environ.get("GITHUB_TOKEN")

    if not username:
        raise RuntimeError("GITHUB_USERNAME is required")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required")

    generated = build_markdown(username, token)
    update_readme(generated)


if __name__ == "__main__":
    main()
