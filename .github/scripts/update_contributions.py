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


def get_repo_metadata(repo_name, username, token, cache):
    if not repo_name:
        return None

    owner = repo_name.split("/", 1)[0]
    if owner.casefold() == username.casefold():
        return None

    if repo_name not in cache:
        try:
            repo = api_get(f"/repos/{repo_name}", token)
            if repo.get("private", True):
                cache[repo_name] = None
            else:
                cache[repo_name] = {
                    "stars": int(repo.get("stargazers_count") or 0),
                }
        except RuntimeError as exc:
            # Fail closed: if visibility cannot be verified, do not publish it.
            print(f"Skipping {repo_name}: {exc}", file=sys.stderr)
            cache[repo_name] = None

    return cache[repo_name]


def is_public_external_repo(repo_name, username, token, cache):
    return get_repo_metadata(repo_name, username, token, cache) is not None


def normalize_title(title):
    return " ".join((title or "").replace("\r", " ").replace("\n", " ").split())


def first_line(message):
    return normalize_title((message or "").splitlines()[0] if message else "")


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


def recent_closed_prs(repo_name, token, cache):
    if repo_name in cache:
        return cache[repo_name]

    pulls = []
    for page in range(1, 11):
        batch = api_get(
            f"/repos/{repo_name}/pulls",
            token,
            {
                "state": "closed",
                "sort": "updated",
                "direction": "desc",
                "per_page": 100,
                "page": page,
            },
        )
        pulls.extend(batch)
        if len(batch) < 100:
            break

    cache[repo_name] = pulls
    return pulls


def user_commit_messages(commits, username):
    messages = set()
    for commit in commits:
        author = commit.get("author") or {}
        if author.get("login", "").casefold() != username.casefold():
            continue
        message = first_line((commit.get("commit") or {}).get("message"))
        if message:
            messages.add(message)
    return messages


def linked_replayed_landing_pr(
    repo_name,
    source_item,
    source_commits,
    username,
    token,
    closed_pr_cache,
    commit_cache,
):
    source_number = source_item["number"]
    source_title = normalize_title(source_item.get("title"))
    source_url = source_item.get("html_url") or ""
    source_messages = user_commit_messages(source_commits, username)

    if not source_messages:
        return None

    source_ref = f"#{source_number}"
    candidates = []

    for pr in recent_closed_prs(repo_name, token, closed_pr_cache):
        number = pr.get("number")
        if not number or number == source_number or not pr.get("merged_at"):
            continue

        if (pr.get("user") or {}).get("login", "").casefold() == username.casefold():
            continue

        body = pr.get("body") or ""
        title = normalize_title(pr.get("title"))

        # A maintainer promotion/replay should explicitly point back to the
        # original PR, or preserve its title. This prevents unrelated PRs that
        # happen to contain one similarly named commit from being counted.
        linked = source_ref in body or source_url in body or title == source_title
        if not linked:
            continue

        cache_key = (repo_name, number)
        if cache_key not in commit_cache:
            try:
                commit_cache[cache_key] = pull_commits(repo_name, number, token)
            except RuntimeError as exc:
                print(f"Skipping candidate {repo_name}#{number}: {exc}", file=sys.stderr)
                commit_cache[cache_key] = []

        candidate_messages = user_commit_messages(commit_cache[cache_key], username)
        overlap = source_messages & candidate_messages
        if not overlap:
            continue

        # An explicit reference to the original PR plus at least one matching
        # user-authored commit is strong evidence. If there is no explicit
        # reference, require every original user-authored commit message to be
        # present in the maintainer PR.
        explicitly_linked = source_ref in body or source_url in body
        if not explicitly_linked and not source_messages.issubset(candidate_messages):
            continue

        candidates.append(pr)

    if not candidates:
        return None

    # Prefer the earliest merged PR that absorbed the contribution. Later ones
    # may simply be backports or follow-up cherry-picks.
    return min(
        candidates,
        key=lambda pr: (pr.get("merged_at") or "9999", pr.get("number") or 10**12),
    )


def promoted_contributions(username, token, visibility_cache):
    items = search_prs(f"author:{username} is:pr is:closed -is:merged", token)
    contributions = []
    closed_pr_cache = {}
    commit_cache = {}

    for item in items:
        if item.get("author_association") == "OWNER":
            continue

        repo_name = repo_name_from_api_url(item.get("repository_url", ""))
        if not is_public_external_repo(repo_name, username, token, visibility_cache):
            continue

        source_number = item["number"]
        try:
            source_commits = pull_commits(repo_name, source_number, token)
        except RuntimeError as exc:
            print(f"Skipping {repo_name}#{source_number}: {exc}", file=sys.stderr)
            continue

        # First prefer exact commit identity. This is the strongest possible
        # signal when a maintainer PR carries the original commits unchanged.
        exact_candidates = {}
        for commit in source_commits:
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
                if (pr.get("user") or {}).get("login", "").casefold() == username.casefold():
                    continue
                exact_candidates[number] = pr

        if exact_candidates:
            landed = min(
                exact_candidates.values(),
                key=lambda pr: (pr.get("merged_at") or "9999", pr.get("number") or 10**12),
            )
        else:
            # Rebases/cherry-picks change SHAs. Fall back to a stricter replay
            # check: original-PR linkage plus commits still attributed by
            # GitHub to this user with matching first-line commit messages.
            landed = linked_replayed_landing_pr(
                repo_name,
                item,
                source_commits,
                username,
                token,
                closed_pr_cache,
                commit_cache,
            )

        if not landed:
            continue

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
    repo_metadata_cache = {}

    contributions = direct_contributions(username, token, repo_metadata_cache)
    contributions.extend(promoted_contributions(username, token, repo_metadata_cache))

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

    projects = []
    for repo_name, prs in grouped.items():
        metadata = get_repo_metadata(
            repo_name,
            username,
            token,
            repo_metadata_cache,
        )
        if metadata is None:
            continue

        projects.append(
            {
                "repo": repo_name,
                "stars": metadata["stars"],
                "contributions": len(prs),
                "prs": prs,
            }
        )

    # Rank projects by public impact first, then contribution depth.
    projects.sort(
        key=lambda project: (
            -project["stars"],
            -project["contributions"],
            project["repo"].casefold(),
        )
    )

    lines = []
    for project in projects:
        repo_name = project["repo"]
        repo_url = f"https://github.com/{repo_name}"
        count = project["contributions"]
        stars_badge = (
            f"https://img.shields.io/github/stars/{repo_name}"
            "?style=flat-square&logo=github&label=stars"
        )
        contributions_badge = (
            "https://img.shields.io/badge/"
            f"contributions-{count}-8B5CF6?style=flat-square"
        )
        stars_url = f"{repo_url}/stargazers"

        lines.append(
            f'#### [\`{repo_name}\`]({repo_url}) &nbsp;&nbsp; '
            f'[![Stars]({stars_badge})]({stars_url}) &nbsp; '
            f'![Contributions]({contributions_badge})'
        )
        lines.append("")

        # Within a project, sort by the contributor's original PR number.
        prs = sorted(project["prs"], key=lambda pr: pr["number"], reverse=True)

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
