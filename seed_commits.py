import os
import random
import subprocess
import sys
from datetime import datetime, timedelta


REALISTIC_MESSAGES = [
    "chore: initialize project structure",
    "docs: add README with setup instructions",
    "feat: add basic CLI entry point",
    "feat: implement core service layer",
    "refactor: extract utils into separate module",
    "fix: resolve edge case in date parsing",
    "test: add unit tests for parser",
    "ci: add github actions workflow for tests",
    "feat: support configuration via environment variables",
    "perf: memoize expensive computation",
    "feat: add logging and debug flags",
    "fix: handle Windows path separators correctly",
    "refactor: simplify error handling",
    "docs: update contributing guidelines",
    "feat: add cache layer with eviction policy",
    "style: apply formatting and lint fixes",
    "feat: add command to export report",
    "fix: prevent crash on empty input",
    "chore: bump dependencies",
    "feat: add support for JSON output"
]


def run(cmd, env=None, cwd=None):
    result = subprocess.run(cmd, env=env, cwd=cwd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result.stdout.strip()


def ensure_repo(root_dir: str):
    if not os.path.isdir(os.path.join(root_dir, ".git")):
        run("git init", cwd=root_dir)
    # Ensure at least one file exists
    readme = os.path.join(root_dir, "README.md")
    if not os.path.exists(readme):
        with open(readme, "w", encoding="utf-8") as f:
            f.write("# Project\n\nInitialized by seed_commits.py\n")
        run("git add README.md", cwd=root_dir)
        run("git commit -m \"chore: initial commit\"", cwd=root_dir)


def random_datetime_between(start: datetime, end: datetime) -> datetime:
    delta_seconds = int((end - start).total_seconds())
    offset = random.randint(0, delta_seconds)
    return start + timedelta(seconds=offset)


def make_commit(root_dir: str, message: str, when: datetime, author: str, email: str):
    # Modify a tracked file or create a temp file to change content
    target_file = os.path.join(root_dir, "CHANGELOG.md")
    line = f"- {when.strftime('%Y-%m-%d')}: {message}\n"
    with open(target_file, "a", encoding="utf-8") as f:
        f.write(line)
    run("git add .", cwd=root_dir)

    env = os.environ.copy()
    iso = when.strftime("%Y-%m-%d %H:%M:%S")
    env["GIT_AUTHOR_DATE"] = iso
    env["GIT_COMMITTER_DATE"] = iso
    env["GIT_AUTHOR_NAME"] = author
    env["GIT_AUTHOR_EMAIL"] = email
    env["GIT_COMMITTER_NAME"] = author
    env["GIT_COMMITTER_EMAIL"] = email

    # Use --allow-empty-message false by default; message provided
    run(f"git commit -m \"{message}\"", env=env, cwd=root_dir)


def main():
    root_dir = os.path.abspath(os.path.dirname(__file__))
    ensure_repo(root_dir)

    # Author identity (customize if needed via env vars)
    author = "oliveira-mtcode"
    email = "matheusoliveiradev083@outlook.com"

    # Number of commits
    min_commits = int(os.environ.get("SEED_MIN", 10))
    max_commits = int(os.environ.get("SEED_MAX", 20))
    num_commits = random.randint(min_commits, max_commits)

    # Time range: from 2 years ago to 1 year ago
    now = datetime.now()
    end = now - timedelta(days=365)
    start = now - timedelta(days=365 * 2)

    # Generate unique, sorted commit times to keep history tidy
    commit_times = sorted({random_datetime_between(start, end) for _ in range(num_commits * 2)})[:num_commits]

    # Pick messages without obvious repetition
    messages = random.sample(REALISTIC_MESSAGES, k=min(num_commits, len(REALISTIC_MESSAGES)))
    # If we need more than unique messages available, extend with suffixed variants
    while len(messages) < num_commits:
        base = random.choice(REALISTIC_MESSAGES)
        messages.append(f"{base} ({random.randint(2, 9)})")

    # Pair times and messages
    for when, message in zip(commit_times, messages):
        make_commit(root_dir, message, when, author, email)

    print(f"Created {len(commit_times)} backdated commits from {start.date()} to {end.date()}.")
    print("Example: git log --pretty=format:'%h %ad %s' --date=short --reverse | cat")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


