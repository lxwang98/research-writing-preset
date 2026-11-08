from pathlib import Path
import re

import yaml


SKILL_ROOT = Path(__file__).resolve().parents[1]


def test_skill_has_no_school_specific_text():
    banned = [
        "".join(["B", "J", "T", "U"]),
        "".join(["b", "j", "t", "u"]),
        " ".join(["Beijing", "Jiaotong"]),
        "\u5317\u4eac\u4ea4\u901a\u5927\u5b66",
        "\u5317\u4ea4\u5927",
    ]
    checked = [
        SKILL_ROOT / "SKILL.md",
        SKILL_ROOT / "references" / "chinese-reference-rules.md",
        SKILL_ROOT / "scripts" / "format_reference.py",
        SKILL_ROOT / "agents" / "openai.yaml",
    ]

    for path in checked:
        assert path.exists(), f"Missing expected skill file: {path}"
        text = path.read_text(encoding="utf-8")
        for phrase in banned:
            assert phrase not in text, f"{phrase!r} remains in {path}"


def test_skill_identity_is_generic_chinese_reference_formatter():
    skill_md = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert "name: chinese-reference-formatter-skill" in skill_md
    assert "license: MIT" in skill_md
    assert (
        "repository: https://github.com/Zechang-Xiong/chinese-reference-formatter-skill"
        in skill_md
    )
    assert "通用中文参考文献" in skill_md
    assert "GB/T 7714" in skill_md


def test_frontmatter_follows_agent_skills_specification():
    # https://agentskills.io/specification includes compatibility as an optional field.
    text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    header = yaml.safe_load(text.split("---", 2)[1])
    assert set(header) <= {
        "name",
        "description",
        "license",
        "compatibility",
        "metadata",
        "allowed-tools",
    }
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", header["name"])
    assert len(header["name"]) <= 64
    assert 0 < len(header["description"]) <= 1024
    assert 0 < len(header["compatibility"]) <= 500
    assert all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in header["metadata"].items()
    )
    assert re.fullmatch(r"\d+\.\d+\.\d+", header["metadata"]["version"])
    ui = yaml.safe_load((SKILL_ROOT / "agents/openai.yaml").read_text(encoding="utf-8"))
    assert f'${header["name"]}' in ui["interface"]["default_prompt"]
