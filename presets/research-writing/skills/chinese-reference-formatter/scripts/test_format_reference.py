import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
from pybtex.database import parse_string

SCRIPT = Path(__file__).with_name("format_reference.py")
EXAMPLES = SCRIPT.parent.parent / "examples" / "metadata.json"


def run_formatter(payload, start=1):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--start", str(start)],
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        capture_output=True,
        check=True,
    )
    return proc.stdout


def test_iclr_example_uses_conference_metadata():
    output = run_formatter(json.loads(EXAMPLES.read_text(encoding="utf-8"))[0])
    assert (
        "Networks[C]. International Conference on Learning Representations, 2017."
        in output
    )
    assert "@inproceedings{kipf-2017-semi-supervised-classification-graph-" in output
    assert "author = {Kipf, Thomas N and Welling, Max}" in output
    assert "journal =" not in output
    assert "10.48550" not in output
    assert "核验来源：https://openreview.net/forum?id=SJU4ayYgl" in output


def test_limits_more_than_three_english_authors():
    output = run_formatter(
        {
            "type": "inproceedings",
            "title": "Focal loss for dense object detection",
            "authors": [
                "Lin, Tsung-Yi",
                "Goyal, Priya",
                "Girshick, Ross",
                "He, Kaiming",
                "Dollár, Piotr",
            ],
            "booktitle": "Proceedings of the IEEE International Conference on Computer Vision",
            "year": 2017,
            "pages": "2980-2988",
        }
    )

    assert (
        "Lin T Y, Goyal P, Girshick R, et al. Focal loss for dense object detection[C]. Proceedings of the IEEE International Conference on Computer Vision, 2017:2980-2988."
        in output
    )
    assert "pages = {2980--2988}" in output


def test_formats_chinese_journal():
    output = run_formatter(
        {
            "type": "article",
            "title": "理想的图书馆员和信息专家的素质与形象",
            "authors": ["李炳穆"],
            "journal": "图书情报工作",
            "year": 2000,
            "issue": "2",
            "pages": "5-8",
        }
    )

    assert "标准参考文献：[1] 李炳穆. 理想的图书馆员和信息专家的素质与形象[J]. 图书情报工作, 2000(2):5-8." in output
    assert "5-8.." not in output
    assert "title = {{理想的图书馆员和信息专家的素质与形象}}" in output


def test_formats_online_resource_with_access_date():
    output = run_formatter(
        {
            "type": "online",
            "title": "出版业信息化驶入快车道",
            "authors": ["萧玉"],
            "published_date": "2001-12-19",
            "access_date": "2002-04-15",
            "url": "http://www.creader.com/news/200112-19/200112-190019.html",
        }
    )

    assert (
        "萧玉. 出版业信息化驶入快车道[EB/OL]. (2001-12-19)[2002-04-15]. http://www.creader.com/news/200112-19/200112-190019.html."
        in output
    )


def test_reports_unmatched_title():
    output = run_formatter(
        {"title": "definitely not a real paper title", "status": "not_found"}
    )

    assert "未找到与“definitely not a real paper title”明确对应的公开文献。" in output


def test_formats_standard_with_marker_before_publication():
    output = run_formatter(
        {
            "type": "standard",
            "title": "示例标准",
            "standard_code": "TEST 1-2026",
            "place": "北京",
            "publisher": "示例出版社",
            "year": 2026,
        }
    )
    assert "[1] TEST 1-2026. 示例标准[S]. 北京:示例出版社, 2026." in output
    assert "number = {TEST 1-2026}" in output


@pytest.mark.parametrize(
    "kind, fields, mark",
    [
        (
            "article",
            {"journal": "示例期刊", "volume": "4", "issue": "2", "pages": "1-9"},
            "J/OL",
        ),
        ("inproceedings", {"booktitle": "示例会议"}, "C/OL"),
        ("book", {"publisher": "示例出版社"}, "M/OL"),
        ("thesis", {"school": "示例大学"}, "D/OL"),
        ("report", {"institution": "示例机构"}, "R/OL"),
        ("standard", {"standard_code": "TEST 1"}, "S/OL"),
        ("patent", {"patent_number": "TEST123", "date": "2026-01-01"}, "P/OL"),
        ("newspaper", {"newspaper": "示例报", "date": "2026-01-01"}, "N/OL"),
        ("chapter", {"booktitle": "示例书", "publisher": "示例出版社"}, "M/OL"),
    ],
)
def test_online_carrier_keeps_url_and_access_date(kind, fields, mark):
    output = run_formatter(
        {
            "type": kind,
            "title": "示例文献",
            "mark": mark,
            "year": 2026,
            "access_date": "2026-09-14",
            "url": "https://example.org/paper",
            **fields,
        }
    )
    reference = output.splitlines()[0]
    assert f"[{mark}]" in reference
    assert "[2026-09-14]. https://example.org/paper." in reference
    assert "urldate = {2026-09-14}" in output


def test_journal_online_exact_format_and_doi_normalization():
    output = run_formatter(
        {
            "type": "article",
            "title": "示例论文",
            "journal": "示例期刊",
            "year": 2026,
            "volume": 4,
            "issue": 2,
            "pages": "1-9",
            "mark": "J/OL",
            "access_date": "2026-09-14",
            "doi": "https://doi.org/10.1234/example",
        }
    )
    assert output.splitlines()[0] == (
        "标准参考文献：[1] 示例论文[J/OL]. 示例期刊, 2026, 4(2):1-9[2026-09-14]. "
        "https://doi.org/10.1234/example. DOI:10.1234/example."
    )


def test_conference_keeps_publisher_place_and_doi():
    output = run_formatter(
        {
            "type": "inproceedings",
            "title": "示例论文",
            "booktitle": "示例会议录",
            "place": "北京",
            "publisher": "示例出版社",
            "year": 2026,
            "pages": "1-9",
            "doi": "10.1234/example",
        }
    )
    assert "示例论文[C]//示例会议录. 北京:示例出版社, 2026:1-9. DOI:10.1234/example." in output


def test_preserves_proper_nouns_and_protects_bibtex_title_case():
    title = "DeepSeek and eBPF with arXiv"
    output = run_formatter({"title": title, "journal": "Example Journal", "year": 2026})
    assert f"{title}[J]" in output
    assert f"title = {{{{{title}}}}}" in output


def citation_keys(output):
    return re.findall(r"^@\w+\{([^,]+),", output, flags=re.M)


def test_distinct_titles_get_stable_distinct_keys_in_any_order():
    items = [
        {
            "title": f"Learning representations with graphs for {subject}",
            "authors": ["Smith, Jane"],
            "year": 2026,
        }
        for subject in ("chemistry", "physics")
    ]
    keys = citation_keys(run_formatter(items))
    assert len(set(keys)) == 2
    assert citation_keys(run_formatter(items[::-1])) == keys[::-1]
    assert citation_keys(run_formatter(items[0])) == keys[:1]


def test_repeated_records_still_have_unique_batch_keys():
    item = {"title": "示例论文", "authors": ["张三"], "year": 2026}
    assert len(set(citation_keys(run_formatter([item, item, item])))) == 3


@pytest.mark.parametrize(
    "kind, degree, expected",
    [
        ("thesis", "master", "mastersthesis"),
        ("thesis", "phd", "phdthesis"),
        ("thesis", "", "misc"),
        ("dissertation", "硕士", "mastersthesis"),
        ("mastersthesis", "", "mastersthesis"),
        ("phdthesis", "", "phdthesis"),
    ],
)
def test_thesis_degree_is_not_guessed(kind, degree, expected):
    output = run_formatter(
        {
            "type": kind,
            "degree": degree,
            "title": "示例论文",
            "school": "示例大学",
            "place": "北京",
            "year": 2026,
        }
    )
    assert "示例论文[D]. 北京:示例大学, 2026." in output
    assert f"@{expected}" in output
    assert "示例大学}" in output


@pytest.mark.parametrize(
    "kind, fields, expected",
    [
        (
            "book",
            {"publisher": "示例出版社", "place": "北京", "edition": "2"},
            "示例文献[M]. 2. 北京:示例出版社, 2026.",
        ),
        ("report", {"institution": "示例机构", "place": "北京"}, "示例文献[R]. 北京:示例机构, 2026."),
        (
            "patent",
            {"country": "中国", "patent_number": "TEST123", "date": "2026-01-01"},
            "示例文献[P]. 中国, TEST123. 2026-01-01.",
        ),
        (
            "newspaper",
            {"newspaper": "示例报", "date": "2026-01-01", "edition": "02"},
            "示例文献[N]. 示例报, 2026-01-01(02).",
        ),
        (
            "chapter",
            {"booktitle": "示例书", "publisher": "示例出版社", "place": "北京", "pages": "1-9"},
            "示例文献[M]//示例书. 北京:示例出版社, 2026:1-9.",
        ),
    ],
)
def test_remaining_document_types(kind, fields, expected):
    assert expected in run_formatter(
        {"type": kind, "title": "示例文献", "year": 2026, **fields}
    )


def test_ambiguity_preserves_competing_sources_without_bibtex():
    output = run_formatter(
        {
            "title": "示例论文",
            "status": "ambiguous",
            "note": "年份存在冲突。",
            "sources": ["https://example.org/a", "https://example.org/b"],
        }
    )
    assert "年份存在冲突。" in output
    assert "核验来源：https://example.org/a; https://example.org/b" in output
    assert "BibTeX" not in output


def test_language_controls_author_truncation():
    output = run_formatter(
        {"title": "Example", "language": "en", "authors": ["张三", "李四", "王五", "赵六"]}
    )
    assert "张三, 李四, 王五, et al." in output
    output = run_formatter(
        {"title": "示例", "authors": ["A, Amy", "B, Bob", "C, Cam", "D, Dan"]}
    )
    assert "A A，B B，C C，等." in output


def test_literal_author_and_tex_special_characters():
    output = run_formatter(
        {
            "title": "R&D at 50%: {x_y}",
            "authors": [{"literal": "Research and Development"}],
            "journal": "Example Journal",
            "year": 2026,
        }
    )
    assert "Research and Development. R&D at 50%: {x_y}[J]" in output
    assert "author = {{Research and Development}}" in output
    assert r"title = {{R\&D at 50\%: \textbraceleft{}x\_y\textbraceright{}}}" in output


@pytest.mark.parametrize(
    "title", ["Unmatched { brace", "Unmatched } brace", "R&D: 50% of x_y"]
)
def test_special_characters_produce_parseable_bibtex(title):
    output = run_formatter(
        {"title": title, "authors": [{"literal": "Research and Development"}]}
    )
    bib = output.split("```bibtex\n", 1)[1].split("\n```", 1)[0]
    parsed = parse_string(bib, "bibtex")
    assert len(parsed.entries) == 1
    entry = next(iter(parsed.entries.values()))
    assert len(entry.persons["author"]) == 1
    assert title.split()[-1].replace("_", r"\_") in entry.fields["title"]


def test_url_and_doi_preserve_machine_readable_characters():
    url = "https://example.org/a_b?first=1&second=50%25"
    doi = "10.1234/a_b"
    output = run_formatter({"title": "Example", "url": url, "doi": doi})
    bib = output.split("```bibtex\n", 1)[1].split("\n```", 1)[0]
    entry = next(iter(parse_string(bib, "bibtex").entries.values()))
    assert entry.fields["url"] == url
    assert entry.fields["doi"] == doi


def test_family_only_author_is_not_dropped():
    output = run_formatter({"title": "Example", "authors": [{"family": "Smith"}]})
    assert "[1] Smith. Example[J]" in output
    assert "author = {Smith}" in output


def parsed_bibtex_entries(output):
    entries = [part.split("\n```", 1)[0] for part in output.split("```bibtex\n")[1:]]
    return list(parse_string("\n".join(entries), "bibtex").entries.values())


@pytest.mark.parametrize("authors", [[""], [None], [" \t ", {}], []])
def test_empty_authors_do_not_abort_a_batch(authors):
    output = run_formatter(
        [
            {
                "title": "First",
                "authors": ["Smith, Jane"],
                "journal": "Example Journal",
                "year": 2026,
            },
            {
                "title": "Second",
                "authors": authors,
                "journal": "Example Journal",
                "year": 2026,
            },
        ]
    )
    assert "[1] Smith J. First[J]" in output
    assert "[2] Second[J]" in output
    first, second = parsed_bibtex_entries(output)
    assert len(first.persons["author"]) == 1
    assert "author" not in second.persons


def test_empty_author_placeholders_do_not_change_keys_or_truncation():
    item = {
        "title": "Example",
        "authors": ["Smith, Jane", "Doe, John", "Li, Wei"],
        "year": 2026,
    }
    expected = run_formatter(item)
    actual = run_formatter(
        {**item, "authors": ["", None, "Smith, Jane", {}, "Doe, John", " ", "Li, Wei"]}
    )
    assert actual == expected
    assert "et al" not in actual


@pytest.mark.parametrize(
    "author, expected",
    [
        ("Kipf, T.N.", "Kipf T N"),
        ("T.N. Kipf", "Kipf T N"),
        ({"family": "Kipf", "given": "T.N."}, "Kipf T N"),
        ({"name": "T.N. Kipf"}, "Kipf T N"),
        ("Lin, Tsung-Yi", "Lin T Y"),
        ("Ludwig van Beethoven", "van Beethoven L"),
        ("Charles de La Vallée Poussin", "de La Vallée Poussin C"),
    ],
)
def test_western_names_keep_initials_and_surname_particles(author, expected):
    output = run_formatter({"title": "Example", "authors": [author]})
    assert f"[1] {expected}. Example[J]" in output
    assert len(parsed_bibtex_entries(output)[0].persons["author"]) == 1


@pytest.mark.parametrize(
    "author",
    [
        "Smith, Jr., John",
        "Smith, John, Jr.",
        "John Smith, Jr.",
        "John Smith Jr.",
        {"name": "John Smith Jr."},
        {"family": "Smith", "given": "John", "suffix": "Jr."},
    ],
)
def test_name_suffix_is_preserved_in_reference_and_bibtex(author):
    output = run_formatter({"title": "Example", "authors": [author], "year": 2026})
    assert "[1] Smith J Jr. Example[J]" in output
    assert citation_keys(output)[0].startswith("smith-2026-")
    person = parsed_bibtex_entries(output)[0].persons["author"][0]
    assert person.last_names == ["Smith"]
    assert person.first_names == ["John"]
    assert person.lineage_names == ["Jr."]


@pytest.mark.parametrize("booktitle", [None, "Primary book"])
def test_chapter_container_alias_matches_bibtex(booktitle):
    output = run_formatter(
        {
            "type": "chapter",
            "title": "Example chapter",
            "container": "Fallback book",
            "booktitle": booktitle,
            "publisher": "Example Press",
            "year": 2026,
        }
    )
    expected = booktitle or "Fallback book"
    assert f"[M]//{expected}. Example Press, 2026." in output
    assert parsed_bibtex_entries(output)[0].fields["booktitle"] == expected


@pytest.mark.parametrize("institution", [None, "Primary Institute"])
def test_report_publisher_alias_fills_bibtex_institution(institution):
    output = run_formatter(
        {
            "type": "report",
            "title": "Example report",
            "publisher": "Fallback Institute",
            "institution": institution,
            "year": 2026,
        }
    )
    expected = institution or "Fallback Institute"
    assert f"[R]. {expected}, 2026." in output
    assert parsed_bibtex_entries(output)[0].fields["institution"] == expected


def test_container_alias_and_web_alias_keep_bibtex_fields():
    output = run_formatter({"title": "Example", "container": "Example Journal"})
    assert "journal = {Example Journal}" in output
    output = run_formatter(
        {
            "type": "web",
            "title": "Example",
            "url": "https://example.org",
            "published_date": "2026-01-01",
            "access_date": "2026-09-14",
        }
    )
    assert "urldate = {2026-09-14}" in output
    assert "date = {2026-01-01}" in output


def test_batch_wrapper_preserves_order_and_start():
    output = run_formatter(
        {"items": [{"title": "First"}, {"title": "Second"}]}, start=8
    )
    assert output.index("[8] First") < output.index("[9] Second")


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [None],
        {"items": "bad"},
        {},
        {"title": 123},
        {"title": "Example", "type": "articel"},
        {"title": "Example", "status": "unverified"},
    ],
)
def test_invalid_metadata_fails_cleanly(payload):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
    )
    assert proc.returncode != 0
    assert "error:" in proc.stderr
    assert "Traceback" not in proc.stderr
    assert proc.stdout == ""


def test_invalid_json_and_start_fail_cleanly():
    for args, data in [([], "{"), (["--start", "0"], '{"title":"Example"}')]:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            input=data,
            text=True,
            capture_output=True,
        )
        assert proc.returncode != 0
        assert "Traceback" not in proc.stderr


def test_readme_output_matches_runnable_example():
    output = run_formatter(json.loads(EXAMPLES.read_text(encoding="utf-8")))
    readme = (SCRIPT.parent.parent / "README.md").read_text(encoding="utf-8")
    assert output.strip() in readme
