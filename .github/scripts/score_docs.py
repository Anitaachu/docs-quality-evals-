"""
Docs Quality Check — reference scoring script

Identifies markdown files changed in a pull request, scores each one
against the rubric in judge_prompt.md using Claude, and posts the
results as a PR comment.

This is a reference implementation. Adapt for your environment.

For production use, consider adding:
  - Retry logic with exponential backoff on API failures
  - Concurrency for scoring multiple files in parallel
  - Cost guardrails (max files per PR, max tokens per call)
  - Caching keyed on file content hash to avoid re-scoring unchanged pages
  - Status checks (the green/red icon next to the PR title)
  - Storage of scores in a database for trend tracking
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import requests
from anthropic import Anthropic, APIError

# ---------- Configuration ----------

# Adjust these for your environment.
MODEL = "claude-sonnet-4-5"
MAX_TOKENS = 2000
PROMPT_PATH = Path(".github/scripts/judge_prompt.md")
DOCS_PATH_PATTERN = re.compile(r"^docs/.+\.(md|mdx)$")

# Score below which a dimension is flagged for review.
SCORE_THRESHOLD = 3.5

# Soft cap on files per PR to limit API costs.
# If a PR touches more files than this, the script scores the first N and
# notes the limit in the comment. Adjust based on your team's needs.
MAX_FILES_PER_PR = 10

# ---------- Helpers ----------

def get_changed_docs(base_sha: str, head_sha: str) -> list[str]:
    """Use git diff to find markdown files changed in the PR."""
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_sha}...{head_sha}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [
        path
        for path in result.stdout.strip().split("\n")
        if DOCS_PATH_PATTERN.match(path) and Path(path).exists()
    ]


def load_prompt_template() -> str:
    """Load the judge prompt template from disk."""
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(
            f"Judge prompt not found at {PROMPT_PATH}. "
            "See judge_prompt.md for the expected format."
        )
    return PROMPT_PATH.read_text()


def score_page(client: Anthropic, prompt_template: str, page_content: str) -> dict:
    """Send a single page to Claude and return the parsed JSON scores."""
    full_prompt = prompt_template.replace(
        "<<<PASTE THE FULL DOCS PAGE BELOW THIS LINE>>>",
        page_content,
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": full_prompt}],
    )

    text = response.content[0].text

    # Strip optional markdown code fences in case the model adds them
    # despite the prompt instructing it not to. Defensive parsing.
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    return json.loads(text)


def format_comment(file_scores: dict[str, dict], skipped_count: int = 0) -> str:
    """Format scoring results as a markdown PR comment."""
    lines = ["## Docs quality check", ""]

    for file_path, scores in file_scores.items():
        lines.append(f"### `{file_path}`")
        lines.append("")
        lines.append("| Dimension | Score | Status |")
        lines.append("|---|---|---|")

        dimensions = [
            ("Task completion", "task_completion"),
            ("Technical accuracy", "technical_accuracy"),
            ("Scannability", "scannability"),
            ("Voice and audience", "voice_and_audience"),
            ("Jargon discipline", "jargon_discipline"),
        ]

        for label, key in dimensions:
            score = scores[key]["score"]
            status = "OK" if score >= SCORE_THRESHOLD else "Review"
            lines.append(f"| {label} | {score} | {status} |")

        triage = scores.get("triage_recommendation", "UNKNOWN")
        assessment = scores.get("overall_assessment", "")

        lines.append("")
        lines.append(f"**Triage:** `{triage}`")
        if assessment:
            lines.append("")
            lines.append(assessment)
        lines.append("")

    if skipped_count:
        lines.append(
            f"_Note: {skipped_count} additional file(s) were not scored to limit "
            f"API costs. Adjust `MAX_FILES_PER_PR` in the script to change this._"
        )
        lines.append("")

    lines.append("---")
    lines.append(
        "_This is an automated docs quality check. "
        "The judge surfaces issues; a human decides what to do._"
    )

    return "\n".join(lines)


def post_pr_comment(repo: str, pr_number: str, body: str, token: str) -> None:
    """Post a comment on the pull request."""
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.post(url, headers=headers, json={"body": body})
    response.raise_for_status()


# ---------- Main ----------

def main() -> None:
    # Read configuration from environment (set by GitHub Actions).
    try:
        api_key = os.environ["ANTHROPIC_API_KEY"]
        github_token = os.environ["GITHUB_TOKEN"]
        pr_number = os.environ["PR_NUMBER"]
        repo = os.environ["REPO"]
        base_sha = os.environ["BASE_SHA"]
        head_sha = os.environ["HEAD_SHA"]
    except KeyError as e:
        print(f"Missing required environment variable: {e}", file=sys.stderr)
        sys.exit(1)

    # Find the docs files changed in this PR.
    changed = get_changed_docs(base_sha, head_sha)

    if not changed:
        print("No docs files changed. Skipping.")
        return

    # Soft cap on number of files scored per PR.
    skipped_count = max(0, len(changed) - MAX_FILES_PER_PR)
    to_score = changed[:MAX_FILES_PER_PR]

    print(f"Scoring {len(to_score)} docs file(s) (skipping {skipped_count})...")

    client = Anthropic(api_key=api_key)
    prompt_template = load_prompt_template()

    file_scores: dict[str, dict] = {}

    for doc_path in to_score:
        print(f"  Scoring {doc_path}...")
        try:
            content = Path(doc_path).read_text()
            file_scores[doc_path] = score_page(client, prompt_template, content)
        except APIError as e:
            print(f"  API error scoring {doc_path}: {e}", file=sys.stderr)
        except json.JSONDecodeError as e:
            print(f"  Could not parse judge response for {doc_path}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"  Unexpected error scoring {doc_path}: {e}", file=sys.stderr)

    if not file_scores:
        print("No files were successfully scored.")
        return

    comment = format_comment(file_scores, skipped_count)
    post_pr_comment(repo, pr_number, comment, github_token)
    print(f"Posted PR comment for {len(file_scores)} file(s).")


if __name__ == "__main__":
    main()
