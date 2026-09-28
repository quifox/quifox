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


def search_merged_prs(username, token):
    items = []
    query = f"author:{username} is:pr is:merged"

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


def build_markdown(items, username, token):
    grouped = defaultdict(list)
    visibility_cache = {}

    for item in items:
        pull = item.get("pull_request") or {}
        if not pull.get("merged_at"):
            continue

        # OWNER is the strongest signal that this PR belongs to one of the
        # user's own repositories, including repositories not named after the
        # current login.
        if item.get("author_association") == "OWNER":
            continue

        repo_name = repo_name_from_api_url(item.get("repository_url", ""))
        if not is_public_external_repo(repo_name, username, token, visibility_cache):
            continue

        grouped[repo_name].append(
            {
                "number": item["number"],
                "title": normalize_title(item.get("title")),
                "url": item.get("html_url"),
                "merged_at": pull.get("merged_at") or "",
            }
        )

    if not grouped:
        return "_No merged external public pull requests found._"

    lines = []
    for repo_name in sorted(grouped, key=str.casefold):
        repo_url = f"https://github.com/{repo_name}"
        lines.append(f"#### [{repo_name}]({repo_url})")
        lines.append("")

        prs = sorted(
            grouped[repo_name],
            key=lambda pr: (pr["merged_at"], pr["number"]),
            reverse=True,
        )
        for pr in prs:
            lines.append(f'- [#{pr["number"]}]({pr["url"]}) — {pr["title"]}')
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

    items = search_merged_prs(username, token)
    generated = build_markdown(items, username, token)
    update_readme(generated)


if __name__ == "__main__":
    main()
