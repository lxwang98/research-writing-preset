#!/usr/bin/env python3
"""Check Markdown note metadata, empty sections and local resource links.

Usage: python reading_note_quality.py <note.md>
Requires PyYAML. This is a format check, not evidence or reasoning validation.
Exit 0: pass; exit 2: invalid note or unavailable validator dependency.
"""

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


def validate(path):
    import yaml

    content = path.read_text(encoding="utf-8-sig")
    errors = []
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", content, re.S)
    if not match:
        return ["Missing or unclosed YAML frontmatter"]
    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return [f"Invalid YAML: {exc}"]
    if not isinstance(metadata, dict):
        return ["YAML frontmatter must be a mapping"]
    for key in ("title", "paper_type", "reading_depth", "source_language", "tags"):
        if key not in metadata or metadata[key] is None or metadata[key] == "":
            errors.append(f"Missing metadata: {key}")
    if "tags" in metadata and not isinstance(metadata["tags"], list):
        errors.append("tags must be a YAML list")
    if metadata.get("reading_depth") not in ("scan", "understand", "reconstruct"):
        errors.append("reading_depth must be scan, understand or reconstruct")

    body = content[match.end():]
    # Ignore fenced code when checking headings and inline links.
    visible = re.sub(r"(?ms)^(`{3,}|~{3,})[^\n]*\n.*?^\1\s*$", "", body)
    if not visible.strip():
        errors.append("Note body is empty")
    headings = list(re.finditer(r"(?m)^#{1,6}\s+(.+)$", visible))
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(visible)
        section = visible[heading.end():end].strip()
        # A heading with child headings is a valid container.
        if not section and (index + 1 == len(headings) or
                            len(headings[index + 1].group(0).split()[0]) <=
                            len(heading.group(0).split()[0])):
            errors.append(f"Empty section: {heading.group(1)}")

    for target in re.findall(r"!?\[[^\]\n]*\]\((<[^>]+>|[^\s)]+)(?:\s+\"[^\"]*\")?\)", visible):
        target = target.strip("<>")
        parts = urlsplit(target)
        if parts.scheme or parts.netloc or not parts.path:
            continue
        local = path.parent / unquote(parts.path)
        if not local.exists():
            errors.append(f"Missing local link target: {target}")
    return errors


def main():
    if len(sys.argv) != 2:
        print("Usage: python reading_note_quality.py <note.md>")
        return 2
    path = Path(sys.argv[1])
    try:
        errors = validate(path)
    except (OSError, UnicodeError, ImportError) as exc:
        print(f"Cannot validate note: {exc}")
        return 2
    for error in errors:
        print(f"ERROR: {error}")
    print(f"{'FAIL' if errors else 'PASS'}: {len(errors)} format errors")
    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
