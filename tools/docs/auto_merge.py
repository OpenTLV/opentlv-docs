# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Opt in to GitHub auto-merge only when the Docs PR gate is a required rule."""

import json
import os
import re
import subprocess

REPO = "OpenTLV/opentlv-docs"


def required_gate(rules):
    return any(rule.get("type") == "required_status_checks"
               and rule.get("parameters", {}).get("strict_required_status_checks_policy") is True
               and any(check.get("context") == "Docs PR gate"
                       for check in rule.get("parameters", {}).get("required_status_checks", []))
               for rule in rules)


def api(path):
    return json.loads(subprocess.check_output(["gh", "api", "repos/" + REPO + path], text=True))


def main():
    number, head = os.environ["PR_NUMBER"], os.environ["PR_HEAD"]
    if not number.isdigit() or not re.fullmatch(r"[0-9a-f]{40}", head):
        raise ValueError("Auto-merge requires an exact PR and head SHA")
    if not api("").get("allow_auto_merge"):
        raise ValueError("Enable repository auto-merge before DOCS_UPDATES_AUTOMERGE")
    # This endpoint covers active rulesets. Classic protection is checked too.
    rules = api("/rules/branches/main")
    protected = required_gate(rules)
    if not protected:
        checks = api("/branches/main/protection/required_status_checks")
        protected = checks.get("strict") is True and (
            "Docs PR gate" in checks.get("contexts", [])
            or any(item.get("context") == "Docs PR gate" for item in checks.get("checks", [])))
    if not protected:
        raise ValueError("Require Docs PR gate and an up-to-date branch before enabling source auto-merge")
    pr = api("/pulls/" + number)
    if (pr["head"]["sha"] != head or pr["head"]["repo"]["full_name"] != REPO
            or not re.fullmatch(r"automation/component-[a-z][a-z0-9_-]*", pr["head"]["ref"])
            or pr["base"]["ref"] != "main" or pr["draft"] or pr["state"] != "open"):
        raise ValueError("Auto-merge is restricted to the exact generated source proposal")
    files, page = [], 1
    while True:
        batch = api(f"/pulls/{number}/files?per_page=100&page={page}")
        files.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    if not files or any(
            item["filename"] != "docs-sources.json"
            and not re.fullmatch(r"compatibility/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.json", item["filename"])
            for item in files):
        raise ValueError("Auto-merge only accepts source pins and compatibility JSON")
    subprocess.run(["gh", "pr", "merge", number, "--repo", REPO, "--auto", "--squash",
                    "--match-head-commit", head], check=True)


if __name__ == "__main__":
    main()
