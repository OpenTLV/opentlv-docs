# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Render owner-supplied examples with exact, scoped compatibility evidence."""

import hashlib
import html
import json
from pathlib import PurePosixPath
import re
from urllib.parse import quote, urlsplit

from mkdocs.exceptions import PluginError

LANGUAGES = {"c": ("C", "c"), "cpp": ("C++", "cpp"), "rust": ("Rust", "rust"),
             "python": ("Python", "python"), "lua": ("Lua", "lua"), "go": ("Go", "go"), "js": ("JavaScript / WebAssembly", "javascript")}
IDENTIFIER = re.compile(r"[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*\Z")
START = re.compile(r"<!-- opentlv-examples: ([a-z][a-z0-9._-]*) -->\Z")
END = "<!-- /opentlv-examples -->"
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def fail(message):
    raise PluginError("Language examples: " + message)


def identifier(value):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        fail(f"invalid feature identifier {value!r}")
    return value


def plain(value):
    if not isinstance(value, str) or not value.strip() or any(ord(c) < 32 for c in value):
        fail("expected nonempty single-line text")
    return value


def escape(value):
    # Prevent owner metadata becoming Markdown, HTML, or a block directive.
    return re.sub(r"[`*_{}\[\]\\]", lambda match: f"&#{ord(match[0])};", html.escape(str(value)))


def source_file(root, name, allowed):
    if (not isinstance(name, str) or not name or "\\" in name or ":" in name
            or any(ord(c) < 32 for c in name) or PurePosixPath(name).is_absolute()
            or any(p in ("", ".", "..") for p in name.split("/"))):
        fail(f"unsafe source path {name!r}")
    path = root / name
    if (name not in allowed or not path.is_file() or not path.resolve().is_relative_to(root)
            or any(p.is_symlink() for p in (path, *path.parents) if p != root)):
        fail(f"source must be a tracked regular file inside its repository: {name}")
    return path


def settings(item):
    value = item.get("examples", {})
    if not isinstance(value, dict) or set(value) - {"manifest", "languages", "results"}:
        fail(f"{item['id']}: invalid examples settings")
    languages = value.get("languages", [])
    if (not isinstance(languages, list) or not all(isinstance(x, str) and x in LANGUAGES for x in languages)
            or len(set(languages)) != len(languages)):
        fail(f"{item['id']}: invalid or duplicate languages")
    if "compatibility" in item:
        if not languages:
            fail(f"{item['id']}: compatibility selection requires explicit example languages")
        if "results" in value:
            fail(f"{item['id']}: compatibility selection cannot use inline example results")
    return value


def results(value):
    records = {}
    if not isinstance(value, list):
        fail("results must be a list")
    for record in value:
        if not isinstance(record, dict):
            fail("result must be an object")
        required = {"feature", "language", "component_commit", "core_commit", "core_version",
                    "result", "evidence", "platform", "configuration"}
        if set(record) != required:
            fail("result requires feature, language, exact commits, Core version, result, evidence, platform and configuration")
        feature = identifier(record["feature"])
        language = record["language"]
        if not isinstance(language, str) or language not in LANGUAGES:
            fail("unknown result language")
        for field in ("component_commit", "core_commit"):
            if not isinstance(record[field], str) or not re.fullmatch(r"[0-9a-f]{40}", record[field]):
                fail(f"{field} must be a full lowercase commit SHA")
        if record["result"] not in ("passed", "failed", "untested"):
            fail("result must be passed, failed or untested")
        for field in ("core_version", "platform", "configuration", "evidence"):
            plain(record[field])
        url = urlsplit(record["evidence"])
        if url.scheme != "https" or not url.netloc or url.username or url.password:
            fail("evidence must be an HTTPS URL")
        key = (feature, language)
        if key in records:
            fail(f"duplicate result for {feature}/{language}; select one platform/configuration explicitly")
        records[key] = record
    return records


class Catalog:
    def __init__(self, selected, git):
        self.core = next(item for _, item in selected if item["id"] == "core")
        self.providers = {}
        self.inputs = []
        for root, item in selected:
            config = settings(item)
            evidence = results(config.get("results", []))
            languages = config.get("languages", [])
            entries = {}
            selection = item.get("compatibility_result", {})
            selected_record = (selection.get("record")
                               if selection.get("status") == "verified" else None)
            version = (selected_record["component"]["version"] if selected_record
                       else "none selected" if "compatibility" in item else item["revision"])
            if item["included"]:
                args = ["ls-files", "-z", "--cached"]
                if item["local"]:
                    args += ["--others", "--exclude-standard"]
                allowed = set(filter(None, git(root, *args).split("\0")))
                name = config.get("manifest", "docs-examples.json")
                if "manifest" in config or name in allowed:
                    path = source_file(root, name, allowed)
                    try:
                        data = json.loads(path.read_text(encoding="utf-8"))
                    except (ValueError, OSError) as error:
                        fail(f"{item['id']}: cannot read example manifest: {error}")
                    if (not isinstance(data, dict) or set(data) - {"version", "component_version", "examples"}
                            or type(data.get("version")) is not int or data["version"] != 1
                            or not isinstance(data.get("examples"), list)):
                        fail(f"{item['id']}: invalid version 1 example manifest")
                    catalog_version = plain(data.get("component_version", version))
                    if selected_record:
                        if (not item["local"]
                                and catalog_version.removeprefix("v") != version.removeprefix("v")):
                            fail(f"{item['id']}: catalog component version does not match the selected release")
                        if item["local"]:
                            version = catalog_version
                    else:
                        version = catalog_version
                    self.inputs.append({"source": item["id"], "path": name,
                                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
                    for entry in data["examples"]:
                        if not isinstance(entry, dict) or set(entry) - {"feature", "language", "status", "path", "reason"}:
                            fail("invalid example entry")
                        feature = identifier(entry.get("feature"))
                        language = entry.get("language")
                        if not isinstance(language, str) or language not in LANGUAGES:
                            fail("unknown example language")
                        if languages and language not in languages:
                            fail(f"{language} is not declared by {item['id']}")
                        key = (feature, language)
                        if key in entries:
                            fail(f"duplicate example {feature}/{language}")
                        status = entry.get("status")
                        if status == "supported":
                            if "reason" in entry:
                                fail("supported example cannot have an unsupported reason")
                            path = source_file(root, entry.get("path"), allowed)
                            try:
                                code = path.read_text(encoding="utf-8")
                            except (ValueError, OSError) as error:
                                fail(f"cannot read example {path.name}: {error}")
                            self.inputs.append({"source": item["id"], "path": entry["path"],
                                                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
                            entries[key] = dict(entry, code=code)
                        elif status == "unsupported":
                            if "path" in entry:
                                fail("unsupported example cannot declare a source path")
                            plain(entry.get("reason"))
                            entries[key] = entry
                        else:
                            fail("example status must be supported or unsupported")
                    if not languages:
                        languages = [lang for lang in LANGUAGES if any(key[1] == lang for key in entries)]
                    for key in evidence:
                        if key not in entries or entries[key]["status"] != "supported":
                            fail("result references an absent or unsupported example")
                elif evidence:
                    fail("verification results require an example catalog")
            for language in languages:
                if language in self.providers:
                    fail(f"multiple repositories provide {language}")
                self.providers[language] = (item, version, entries, evidence)

    def render(self, feature):
        blocks = []
        for language, (label, lexer) in LANGUAGES.items():
            if language not in self.providers:
                continue
            item, version, entries, evidence = self.providers[language]
            entry = entries.get((feature, language))
            text = [f"/// tab | {label}", "", f"Component version: {escape(version)}.  ",
                    f"Selected revision: {escape(item.get('revision', 'none selected'))}.", ""]
            if "compatibility" in item:
                text += self.render_compatibility(item, entry, feature, language, lexer)
            elif not item["included"]:
                text += ["Repository unavailable; example not included."]
            elif entry is None:
                text += ["No example supplied for this feature; support is unknown."]
            elif entry["status"] == "unsupported":
                text += ["Unsupported: " + escape(entry["reason"])]
            else:
                record = evidence.get((feature, language))
                matches = (record and record["component_commit"] == item["commit"]
                           and record["core_commit"] == self.core["commit"]
                           and not item["local"] and not self.core["local"])
                if matches:
                    url = quote(record["evidence"], safe=":/?=&%#@+;,$-_.!~*")
                    if record["result"] == "passed":
                        text += [f"Verified Core: {escape(record['core_version'])} "
                                 f"({record['core_commit']}).  "]
                    else:
                        text += [f"Verified Core: none. Test result: {record['result']}.  "]
                    text += [f"Platform: {escape(record['platform'])}; configuration: {escape(record['configuration'])}.  ",
                             f"[Verification evidence]({url})", ""]
                else:
                    reason = "no result supplied" if record is None else "result does not match this checkout or local preview"
                    text += [f"Verified Core: not established ({reason}).", ""]
                if matches and record["result"] != "passed":
                    text += ["Example withheld for this unverified combination."]
                else:
                    text += self.render_source(item, entry, lexer)
            text += ["", "///"]
            blocks.append("\n".join(text))
        return "\n\n".join(blocks)

    @staticmethod
    def render_source(item, entry, lexer):
        url = item["repository"].rstrip("/") + "/blob/" + item["commit"] + "/" + quote(entry["path"], safe="/")
        # Longer fences protect source containing Markdown and block delimiters.
        code = entry["code"].removesuffix("\n")
        fence = "`" * max(3, 1 + max((len(m[0]) for m in re.finditer(r"`+", code)), default=0))
        return [f"[Example source]({url})", "", fence + lexer, code, fence]

    def render_compatibility(self, item, entry, feature, language, lexer):
        selection = item.get("compatibility_result", {})
        record = selection.get("record")
        core = selection.get("core", {})
        core_commit = self.core["commit"]
        core_version = (core.get("version") if core.get("commit") == core_commit else None)
        if not core_version and record and record["core"]["commit"] == core_commit:
            core_version = record["core"]["version"]
        text = [f"Selected Core: {escape(core_version or 'version unknown')} ({core_commit}).  "]
        if not core_version:
            text += [f"Core revision: {escape(self.core['revision'])}.  "]
        if record:
            text += [f"Declared Core dependency: {escape(record['declared_core'])}.  "]
            if selection.get("status") != "verified":
                text += [f"Candidate component: {escape(record['component']['version'])} "
                         f"({record['component']['commit']}).  "]
            elif item["local"]:
                text += [f"Selected release: {escape(record['component']['version'])} "
                         f"({record['component']['commit']}).  "]
            text += [f"Tested Core: {escape(record['core']['version'])} ({record['core']['commit']}).  ",
                     f"Build: {record['build']}; tests: {record['test']}.  "]
        scope = item["compatibility"]
        text += [f"Platform: {escape(scope['platform'])}; configuration: {escape(scope['configuration'])}.  "]
        if record:
            url = quote(record["evidence"], safe=":/?=&%#@+;,$-_.!~*")
            text += [f"[Verification evidence]({url})"]
        text += [""]
        status = selection.get("status", "missing")
        if status != "verified":
            reason = {"missing": "no compatibility result supplied for this Core and scope",
                      "failed": "compatibility build or tests failed",
                      "untested": "this combination has not passed both build and tests"}[status]
            text += [f"Verified Core: not established ({reason}).",
                     "Example withheld; no verified component release was selected."]
            return text
        if not item["included"]:
            text += ["Selected component unavailable: " + escape(item.get("reason", "checkout missing")),
                     "Example not included."]
            return text
        matches = (record and record["component"]["commit"] == item.get("commit") == item.get("revision")
                   and record["core"]["commit"] == core_commit
                   and record["component"]["repository"] == item["repository"]
                   and record["core"]["repository"] == self.core["repository"]
                   and record["build"] == "passed" and record["test"] == "passed"
                   and record["platform"] == scope["platform"]
                   and record["configuration"] == scope["configuration"]
                   and not any(source.get("local") or source.get("dirty") for source in (item, self.core)))
        if not matches:
            return text + ["Verified Core: not established (result does not match this checkout or local preview).",
                           "Example withheld for this unverified combination."]
        text += [f"Verified Core: {escape(record['core']['version'])} ({core_commit}).", ""]
        support = next((value for value in record["features"] if value["id"] == feature), None)
        if support is None or support["support"] == "unknown":
            return text + ["Feature support is unknown for the selected component; example withheld."]
        if support["support"] == "unsupported":
            return text + ["Unsupported: this feature is not supported by the selected component."]
        if entry is None:
            return text + ["No example supplied for this feature by the selected component."]
        if entry["status"] == "unsupported":
            return text + ["Unsupported: " + escape(entry["reason"])]
        proof = next((value for value in support["examples"]
                      if value["language"] == language and value["path"] == entry["path"]), None)
        if proof is None:
            return text + ["No verification result for this example; example withheld."]
        if proof["result"] != "passed":
            return text + [f"Example test result: {proof['result']}; example withheld."]
        return text + self.render_source(item, entry, lexer)

    def transform(self, markdown):
        """Replace paired slots outside code fences, keeping fallback text without providers."""
        output, fallback = [], None
        feature, fence = None, None
        for line in markdown.splitlines(keepends=True):
            stripped = line.rstrip("\r\n")
            match = FENCE.match(stripped)
            if fence:
                if match and match[1][0] == fence[0] and len(match[1]) >= len(fence) and not match[2].strip():
                    fence = None
            elif match:
                fence = match[1]
            elif stripped.startswith("<!-- opentlv-examples:") or stripped == END:
                if stripped == END:
                    if fallback is None:
                        fail("example slot has an unmatched closing marker")
                    output.append(self.render(feature) or "".join(fallback))
                    output.append("\n")
                    fallback, feature = None, None
                else:
                    start = START.fullmatch(stripped)
                    if not start or fallback is not None:
                        fail("invalid or nested example slot")
                    feature, fallback = identifier(start[1]), []
                continue
            (output if fallback is None else fallback).append(line)
        if fallback is not None:
            fail("unclosed example slot")
        return "".join(output)
