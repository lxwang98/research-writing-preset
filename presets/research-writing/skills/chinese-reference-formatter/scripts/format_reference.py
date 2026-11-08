#!/usr/bin/env python3
"""Format normalized metadata as Chinese academic references and BibTeX."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from typing import Any


STOP_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "into",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
    "via",
    "vs",
}


TYPE_MARKS = {
    "article": "J",
    "journal": "J",
    "inproceedings": "C",
    "conference": "C",
    "proceedings": "C",
    "book": "M",
    "monograph": "M",
    "thesis": "D",
    "dissertation": "D",
    "mastersthesis": "D",
    "phdthesis": "D",
    "report": "R",
    "standard": "S",
    "patent": "P",
    "newspaper": "N",
    "chapter": "M",
    "online": "EB/OL",
    "web": "EB/OL",
}


BIB_TYPES = {
    "article": "article",
    "journal": "article",
    "inproceedings": "inproceedings",
    "conference": "inproceedings",
    "proceedings": "inproceedings",
    "book": "book",
    "monograph": "book",
    "thesis": "misc",
    "dissertation": "misc",
    "mastersthesis": "mastersthesis",
    "phdthesis": "phdthesis",
    "report": "techreport",
    "standard": "misc",
    "patent": "misc",
    "newspaper": "misc",
    "chapter": "incollection",
    "online": "misc",
    "web": "misc",
}


def has_cjk(text: str) -> bool:
    return bool(re.search(r"[\u3400-\u9fff]", text))


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def clean(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def strip_trailing_period(value: str) -> str:
    return value.rstrip().rstrip(".。")


def title_for_reference(title: str) -> str:
    # Verified metadata is the authority for proper nouns and deliberate case.
    return clean(title)


NAME_SUFFIXES = {"jr", "sr", "ii", "iii", "iv"}


def western_name_parts(name: str) -> tuple[str, str, str]:
    """Read explicit family/suffix forms or a natural given-name-first name."""
    name = clean(name)
    if not name:
        return "", "", ""
    suffix = ""
    if "," in name:
        parts = [part.strip() for part in name.split(",", 2)]
        if len(parts) == 3:
            # BibTeX's explicit form is Family, Suffix, Given.
            family, suffix, given = parts
            if (
                given.rstrip(".").lower() in NAME_SUFFIXES
                and suffix.rstrip(".").lower() not in NAME_SUFFIXES
            ):
                # Also accept Family, Given, Jr. and normalize it for BibTeX.
                given, suffix = suffix, given
        else:
            family, given = parts
            if given.rstrip(".").lower() in NAME_SUFFIXES and " " in family:
                # Natural form: John Smith, Jr.
                return western_name_parts(f"{family} {given}")
    else:
        parts = name.split()
        if len(parts) > 1 and parts[-1].rstrip(".").lower() in NAME_SUFFIXES:
            suffix = parts.pop()
        if len(parts) == 1:
            return parts[0], "", suffix
        # Preserve lowercase surname particles (e.g. Ludwig van Beethoven).
        family_start = next(
            (index for index in range(1, len(parts) - 1) if parts[index][0].islower()),
            len(parts) - 1,
        )
        family = " ".join(parts[family_start:])
        given = " ".join(parts[:family_start])
    return family, given, suffix


def western_author_name(name: str) -> str:
    family, given, suffix = western_name_parts(name)
    # Splitting on periods keeps both initials in T.N. instead of collapsing to TN.
    given_parts = re.split(r"[\s.\-]+", given)
    initials = " ".join(part[:1].upper() for part in given_parts if part)
    return " ".join(part for part in [family, initials, suffix.rstrip(".")] if part)


def author_display(author: Any) -> str:
    if isinstance(author, dict):
        literal = clean(author.get("literal"))
        if literal:
            return literal
        family = clean(author.get("family"))
        given = clean(author.get("given"))
        if has_cjk(family + given):
            return family + given
        if family and given:
            suffix = clean(author.get("suffix"))
            name = f"{family}, {suffix}, {given}" if suffix else f"{family}, {given}"
            return western_author_name(name)
        return family or given or author_display(clean(author.get("name")))
    name = clean(author)
    if has_cjk(name):
        return name
    return western_author_name(name)


def format_authors(authors: list[Any], language: str = "") -> str:
    names = [name for author in authors if (name := author_display(author))]
    if not names:
        return ""
    rendered = names[:3]
    english = not any(has_cjk(name) for name in rendered)
    if language:
        english = not language.lower().startswith("zh")
    if len(names) > 3:
        rendered.append("et al" if english else "等")
    return (", " if english else "，").join(rendered)


def original_authors_for_bibtex(authors: list[Any]) -> str:
    rendered = []
    for author in authors:
        if isinstance(author, dict):
            literal = clean(author.get("literal"))
            if literal:
                rendered.append("{" + bibtex_escape(literal) + "}")
                continue
            family = clean(author.get("family"))
            given = clean(author.get("given"))
            suffix = clean(author.get("suffix"))
            if family and suffix:
                name = f"{family}, {suffix}, {given}"
            else:
                name = f"{family}, {given}".strip(", ") or clean(author.get("name"))
        else:
            name = clean(author)
        if name and not has_cjk(name):
            family, given, suffix = western_name_parts(name)
            if suffix:
                name = f"{family}, {suffix}, {given}"
        rendered.append(bibtex_escape(name))
    return " and ".join(author for author in rendered if author)


def append_pages(segment: str, pages: str) -> str:
    if pages:
        return f"{segment}:{pages}"
    return segment


def normalized_doi(item: dict[str, Any]) -> str:
    return re.sub(
        r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)",
        "",
        clean(item.get("doi")),
        flags=re.I,
    )


def year_part(item: dict[str, Any]) -> str:
    year = clean(item.get("year"))
    volume = clean(item.get("volume"))
    issue = clean(item.get("issue") or item.get("number"))
    segment = year
    if volume:
        segment += f", {volume}"
    if issue:
        segment += f"({issue})"
    return segment


def reference_body(item: dict[str, Any], number: int) -> str:
    title = clean(item.get("title"))
    if clean(item.get("status")) == "not_found":
        return f"未找到与“{title}”明确对应的公开文献。"
    if clean(item.get("status")) == "ambiguous":
        note = clean(item.get("note")) or "多个来源信息冲突，无法确定唯一对应文献。"
        return f"无法确定“{title}”的唯一对应文献：{note}"

    kind = clean(item.get("type")).lower() or "article"
    mark = clean(item.get("mark")) or TYPE_MARKS.get(kind, "J")
    language = clean(item.get("language")) or ("zh" if has_cjk(title) else "")
    authors = format_authors(
        as_list(item.get("authors") or item.get("author")), language
    )
    title_ref = title_for_reference(title)
    prefix = f"[{number}] "
    author_prefix = f"{authors}. " if authors else ""
    pages = clean(item.get("pages"))

    if kind in {"article", "journal"}:
        journal = clean(item.get("journal") or item.get("container"))
        segment = append_pages(f"{journal}, {year_part(item)}", pages)
        ref = f"{prefix}{author_prefix}{title_ref}[{mark}]. {segment}."
        return ref

    if kind in {"inproceedings", "conference", "proceedings"}:
        booktitle = clean(item.get("booktitle") or item.get("container"))
        place = clean(item.get("place") or item.get("address"))
        publisher = clean(item.get("publisher"))
        if publisher:
            pub = f"{place}:{publisher}" if place else publisher
            segment = append_pages(
                f"{booktitle}. {pub}, {clean(item.get('year'))}", pages
            )
            return f"{prefix}{author_prefix}{title_ref}[{mark}]//{segment}."
        segment = append_pages(f"{booktitle}, {clean(item.get('year'))}", pages)
        return f"{prefix}{author_prefix}{title_ref}[{mark}]. {segment}."

    if kind in {"book", "monograph"}:
        edition = clean(item.get("edition") or item.get("version"))
        edition_part = "" if edition in {"", "1", "1st", "第一版"} else f"{edition}. "
        translators = format_authors(
            as_list(item.get("translators") or item.get("translator"))
        )
        translator_part = f"{translators}, 译. " if translators else ""
        place = clean(item.get("place") or item.get("address"))
        publisher = clean(item.get("publisher"))
        pub = f"{place}:{publisher}" if place and publisher else publisher or place
        segment = append_pages(f"{pub}, {clean(item.get('year'))}", pages)
        return f"{prefix}{author_prefix}{title_ref}[{mark}]. {translator_part}{edition_part}{segment}."

    if kind in {"thesis", "dissertation", "mastersthesis", "phdthesis"}:
        place = clean(item.get("place") or item.get("address"))
        school = clean(item.get("school") or item.get("institution"))
        pub = f"{place}:{school}" if place and school else school or place
        segment = append_pages(f"{pub}, {clean(item.get('year'))}", pages)
        return f"{prefix}{author_prefix}{title_ref}[{mark}]. {segment}."

    if kind == "report":
        place = clean(item.get("place") or item.get("address"))
        institution = clean(item.get("institution") or item.get("publisher"))
        pub = (
            f"{place}:{institution}" if place and institution else institution or place
        )
        segment = append_pages(f"{pub}, {clean(item.get('year'))}", pages)
        return f"{prefix}{author_prefix}{title_ref}[{mark}]. {segment}."

    if kind == "patent":
        country = clean(item.get("country"))
        patent_type = clean(item.get("patent_type"))
        patent_number = clean(item.get("patent_number") or item.get("number"))
        date = clean(item.get("published_date") or item.get("date"))
        parts = ", ".join(
            part for part in [country, patent_type, patent_number] if part
        )
        tail = f"{parts}. {date}" if date else parts
        return f"{prefix}{author_prefix}{title_ref}[{mark}]. {tail}."

    if kind == "standard":
        code = clean(item.get("standard_code") or item.get("code"))
        place = clean(item.get("place") or item.get("address"))
        publisher = clean(item.get("publisher"))
        year = clean(item.get("year"))
        pub = f"{place}:{publisher}" if place and publisher else publisher or place
        heading = ". ".join(part for part in [code, title_ref] if part)
        tail = ", ".join(part for part in [pub, year] if part)
        return f"{prefix}{author_prefix}{heading}[{mark}]." + (
            f" {tail}." if tail else ""
        )

    if kind == "newspaper":
        newspaper = clean(item.get("newspaper") or item.get("container"))
        date = clean(item.get("published_date") or item.get("date"))
        edition = clean(item.get("edition"))
        date_part = f"{date}({edition})" if edition else date
        return f"{prefix}{author_prefix}{title_ref}[{mark}]. {newspaper}, {date_part}."

    if kind == "chapter":
        booktitle = clean(item.get("booktitle") or item.get("container"))
        book_authors = format_authors(
            as_list(item.get("book_authors") or item.get("editors"))
        )
        place = clean(item.get("place") or item.get("address"))
        publisher = clean(item.get("publisher"))
        year = clean(item.get("year"))
        pub = f"{place}:{publisher}" if place and publisher else publisher or place
        container = f"{book_authors}. {booktitle}" if book_authors else booktitle
        segment = append_pages(f"{container}. {pub}, {year}", pages)
        return f"{prefix}{author_prefix}{title_ref}[{mark}]//{segment}."

    published = clean(item.get("published_date") or item.get("date"))
    access = clean(item.get("access_date"))
    url = clean(item.get("url"))
    date_part = ""
    if published:
        date_part += f"({published})"
    if access:
        date_part += f"[{access}]"
    return f"{prefix}{author_prefix}{title_ref}[{mark}]. {date_part}. {url}."


def reference_line(item: dict[str, Any], number: int) -> str:
    reference = reference_body(item, number)
    if clean(item.get("status")) in {"not_found", "ambiguous"}:
        return reference
    kind = clean(item.get("type")).lower() or "article"
    mark = clean(item.get("mark")) or TYPE_MARKS.get(kind, "J")
    doi = normalized_doi(item)
    if "/OL" in mark and kind not in {"online", "web"}:
        access = clean(item.get("access_date"))
        url = clean(item.get("url")) or (f"https://doi.org/{doi}" if doi else "")
        reference = strip_trailing_period(reference)
        if access:
            reference += f"[{access}]"
        reference += "."
        if url:
            reference += f" {url}."
    if doi:
        reference += f" DOI:{doi}."
    return reference


def slug(text: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?", text.lower())
    words = [word for word in words if word not in STOP_WORDS]
    return "-".join(words[:3])


def first_author_slug(authors: list[Any]) -> str:
    authors = [author for author in authors if author_display(author)]
    if not authors:
        return "ref"
    first = authors[0]
    if isinstance(first, dict):
        family = clean(first.get("family") or first.get("literal"))
        if not family:
            family = western_name_parts(clean(first.get("name")))[0]
    else:
        name = clean(first)
        family = western_name_parts(name)[0]
    candidate = slug(family)
    return candidate or "ref"


def bib_key(item: dict[str, Any]) -> str:
    authors = as_list(item.get("authors") or item.get("author"))
    year = clean(item.get("year") or item.get("published_date") or "nd")[:4] or "nd"
    title = clean(item.get("title"))
    title_slug = slug(title)
    base = "-".join(
        part for part in [first_author_slug(authors), year, title_slug] if part
    )
    # Include the full title and authors, rather than only the displayed slug.
    identity = json.dumps(
        [title, original_authors_for_bibtex(authors), year, normalized_doi(item)],
        ensure_ascii=False,
    )
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]
    return f"{base}-{digest}" if base else f"ref-{digest}"


def bibtex_escape(value: str) -> str:
    escapes = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\textbraceleft{}",
        "}": r"\textbraceright{}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(escapes.get(char, char) for char in value)


def bibtex_entry(item: dict[str, Any], citation_key: str = "") -> str:
    if clean(item.get("status")) in {"not_found", "ambiguous"}:
        return ""
    kind = clean(item.get("type")).lower() or "article"
    bib_type = BIB_TYPES.get(kind, "misc")
    if kind in {"thesis", "dissertation"}:
        degree = clean(item.get("degree")).lower()
        if degree in {"master", "masters", "mastersthesis", "硕士"}:
            bib_type = "mastersthesis"
        elif degree in {"phd", "doctor", "doctoral", "phdthesis", "博士"}:
            bib_type = "phdthesis"
    item = dict(item)
    if bib_type == "article":
        item["journal"] = item.get("journal") or item.get("container")
    elif bib_type in {"inproceedings", "incollection"}:
        item["booktitle"] = item.get("booktitle") or item.get("container")
    elif bib_type == "techreport":
        item["institution"] = item.get("institution") or item.get("publisher")
    elif kind in {"thesis", "dissertation"} and bib_type == "misc":
        item["howpublished"] = item.get("school") or item.get("institution")
    if kind == "standard":
        item["number"] = (
            item.get("standard_code") or item.get("code") or item.get("number")
        )
    elif kind == "patent":
        item["number"] = item.get("patent_number") or item.get("number")
    elif kind == "newspaper":
        item["howpublished"] = item.get("newspaper") or item.get("container")
    item["doi"] = normalized_doi(item)
    fields: list[tuple[str, str]] = []
    authors = original_authors_for_bibtex(
        as_list(item.get("authors") or item.get("author"))
    )
    if authors:
        fields.append(("author", authors))
    for key, candidates in [
        ("title", ["title"]),
        ("journal", ["journal"]),
        ("booktitle", ["booktitle"]),
        ("publisher", ["publisher"]),
        ("edition", ["edition", "version"]),
        ("howpublished", ["howpublished"]),
        ("address", ["place", "address"]),
        ("school", ["school", "institution"]),
        ("institution", ["institution"]),
        ("year", ["year"]),
        ("date", ["published_date", "date"]),
        ("volume", ["volume"]),
        ("number", ["issue", "number"]),
        ("pages", ["pages"]),
        ("doi", ["doi"]),
        ("url", ["url"]),
        ("note", ["note"]),
    ]:
        value = ""
        for candidate in candidates:
            value = clean(item.get(candidate))
            if value:
                break
        if value and (key != "journal" or bib_type == "article"):
            if key == "booktitle" and bib_type not in {"inproceedings", "incollection"}:
                continue
            if key == "school" and bib_type not in {"phdthesis", "mastersthesis"}:
                continue
            if key == "institution" and bib_type != "techreport":
                continue
            if key in {"url", "doi"}:
                # Machine-readable identifiers must retain URL syntax, not TeX escapes.
                value = (
                    value.replace("{", "%7B").replace("}", "%7D").replace("\\", "%5C")
                )
            else:
                value = bibtex_escape(value)
            if key == "title":
                value = "{" + value + "}"
            if key == "pages":
                value = re.sub(r"(?<=\d)[–—-]+(?=\d)", "--", value)
            fields.append((key, value))
    if clean(item.get("access_date")):
        fields.append(("urldate", bibtex_escape(clean(item.get("access_date")))))
    if item.get("editors"):
        fields.append(("editor", original_authors_for_bibtex(as_list(item["editors"]))))
    lines = [f"@{bib_type}{{{citation_key or bib_key(item)},"]
    for idx, (field, value) in enumerate(fields):
        comma = "," if idx < len(fields) - 1 else ""
        lines.append(f"  {field} = {{{value}}}{comma}")
    lines.append("}")
    return "\n".join(lines)


def sources_line(item: dict[str, Any]) -> str:
    sources = [
        clean(source) for source in as_list(item.get("sources")) if clean(source)
    ]
    if not sources:
        if clean(item.get("url")):
            sources.append(clean(item.get("url")))
        elif clean(item.get("doi")):
            sources.append(f"DOI:{clean(item.get('doi'))}")
    return "核验来源：" + ("; ".join(sources) if sources else "未提供")


def render_item(item: dict[str, Any], number: int, citation_key: str = "") -> str:
    ref = reference_line(item, number)
    if clean(item.get("status")) in {"not_found", "ambiguous"}:
        if clean(item.get("status")) == "ambiguous" and item.get("sources"):
            return f"{ref}\n{sources_line(item)}"
        return ref
    bib = bibtex_entry(item, citation_key)
    return f"标准参考文献：{ref}\nBibTeX：\n```bibtex\n{bib}\n```\n{sources_line(item)}"


def load_payload(args: argparse.Namespace) -> Any:
    if args.input:
        with open(args.input, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return json.load(sys.stdin)


def normalize_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict) and "items" in payload:
        if not isinstance(payload["items"], list):
            raise ValueError("items must be a list of objects.")
        items = payload["items"]
    elif isinstance(payload, dict):
        items = [payload]
    else:
        raise ValueError(
            "Input JSON must be an object, an object with items, or a list."
        )
    for index, item in enumerate(items, 1):
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("title"), str)
            or not clean(item["title"])
        ):
            raise ValueError(
                f"Item {index} must be an object with a non-empty title string."
            )
        status = clean(item.get("status"))
        if status not in {"", "confirmed", "not_found", "ambiguous"}:
            raise ValueError(f"Item {index}: unknown status {status!r}.")
        if status in {"not_found", "ambiguous"}:
            continue
        kind = clean(item.get("type")).lower() or "article"
        if kind not in TYPE_MARKS:
            raise ValueError(f"Item {index}: unsupported type {kind!r}.")
    return items


def render_items(items: list[dict[str, Any]], start: int = 1) -> str:
    used_keys: set[str] = set()
    rendered = []
    for index, item in enumerate(items, start):
        citation_key = ""
        if clean(item.get("status")) not in {"not_found", "ambiguous"}:
            base = bib_key(item)
            citation_key = base
            suffix = 2
            while citation_key in used_keys:
                citation_key = f"{base}-{suffix}"
                suffix += 1
            used_keys.add(citation_key)
        rendered.append(render_item(item, index, citation_key))
    return "\n\n".join(rendered)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", help="Path to normalized metadata JSON. Defaults to stdin."
    )
    parser.add_argument(
        "--start", type=int, default=1, help="Starting reference number."
    )
    args = parser.parse_args()

    if args.start < 1:
        parser.error("--start must be a positive integer.")
    try:
        items = normalize_payload(load_payload(args))
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(render_items(items, args.start))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
