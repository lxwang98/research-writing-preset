#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""numeral_lint.py — 中文稿件「数字 / 纪年 / 易混字符」体检

为什么需要它
------------
中文正文里「一九二〇年」的 〇 是 U+3007。它在楷体、宋体里就是一个空心圆环，
字形和拉丁大写 O 无法区分：排出来、转成 PDF、截图给别人看，读者读到的都是
「一九二O年」。同理，OCR/WPS 还会把 〇 换成 ○（U+25CB）、把 0 换成 Ｏ（全角），
或者直接写成字母 O（如 2O20）。这些都不是错别字，是字符选错了，肉眼很难发现，
但投出去就是硬伤。

本脚本检查：
  E3007     正文出现 U+3007 〇（应写「零」或阿拉伯数字）
  ECIRCLE   正文出现 ○ U+25CB / ◯ U+25EF（同上）
  ELATIN_O  汉字数字旁的拉丁 O/o（一九二O年、二O年代、一九O〇年）
  EDIGIT_O  数字中的字母 O（2O20、1O0）
  EFULL_O   全角 Ｏ/ｏ（一九二Ｏ年）
  W_ERA     全文同时出现汉字纪年与阿拉伯纪年（体例不统一，需人工确认）
  W_FULLDIG 全角数字 ０-９

用法
----
    python numeral_lint.py 稿件.md
    python numeral_lint.py 稿件.docx
    python numeral_lint.py 目录/ --recursive
    python numeral_lint.py 稿件.md --json
    python numeral_lint.py 稿件.md --fix          # 〇/○ → 零，输出 稿件_fixed.md

退出码：有 error → 1；只有 warning → 0。适合放进构建脚本当 gate。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CJK_DIGITS = "〇零一二三四五六七八九十百千两"
CJK_NUM = f"[{CJK_DIGITS}]"

# (code, severity, pattern, message, hint)
CHECKS = [
    (
        "E3007",
        "error",
        re.compile("\u3007"),
        "使用了 U+3007（〇）",
        "楷体下就是一个空心圆，与拉丁大写 O 无法区分；纪年写「零」，其余写阿拉伯数字 0",
    ),
    (
        "ECIRCLE",
        "error",
        re.compile("[\u25cb\u25ef]"),
        "使用了 ○ / ◯ 圆圈符号",
        "这是符号不是数字；改成「零」或 0",
    ),
    (
        "ELATIN_O",
        "error",
        re.compile(f"{CJK_NUM}[Oo]|[Oo](?={CJK_NUM})"),
        "汉字数字旁出现拉丁字母 O/o",
        "改成「零」或阿拉伯数字，例如 一九二〇年 → 一九二零年 / 1920年",
    ),
    (
        "EDIGIT_O",
        "error",
        re.compile(r"\d[Oo]\d"),
        "数字中间夹了字母 O",
        "改成 0，例如 2O20 → 2020",
    ),
    (
        "EFULL_O",
        "error",
        re.compile("[\uff2f\uff4f]"),
        "使用了全角 Ｏ / ｏ",
        "改成半角 0 或对应汉字",
    ),
    (
        "W_FULLDIG",
        "warning",
        re.compile("[\uff10-\uff19]"),
        "使用了全角数字",
        "中文正文里数字用半角，避免与全角标点混排时字距异常",
    ),
]

CJK_YEAR = re.compile(f"{CJK_NUM}{{2,4}}年")
ARABIC_YEAR = re.compile(r"(?:1[0-9]{3}|20[0-9]{2})年")


class Finding:
    __slots__ = ("path", "line", "col", "code", "severity", "message", "hint", "context")

    def __init__(self, path, line, col, code, severity, message, hint, context):
        self.path = path
        self.line = line
        self.col = col
        self.code = code
        self.severity = severity
        self.message = message
        self.hint = hint
        self.context = context

    def as_text(self):
        loc = f"{self.path}:{self.line}:{self.col}" if self.line else f"{self.path}"
        return f"{loc}  {self.code} {self.message}\n      …{self.context}…\n      → {self.hint}"

    def as_dict(self):
        return {
            "path": str(self.path),
            "line": self.line,
            "col": self.col,
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "hint": self.hint,
            "context": self.context,
        }


def snippet(text: str, pos: int, width: int = 14) -> str:
    a = max(0, pos - width)
    b = min(len(text), pos + width)
    return text[a:b].replace("\n", " ")


def scan_text(text: str, path: str, line_no: int | None, base_col: int = 0) -> list[Finding]:
    out: list[Finding] = []
    for code, severity, pattern, message, hint in CHECKS:
        if pattern is None or message is None:
            continue
        for m in pattern.finditer(text):
            out.append(
                Finding(path, line_no or 0, base_col + m.start() + 1, code, severity,
                        message, hint, snippet(text, m.start()))
            )
    return out


def scan_mixed_era(lines: list[tuple[int, str]], path: str) -> list[Finding]:
    """全文同时出现两种纪年体例时给一次 warning（不是错误，人文类常有意为之）。"""
    cjk, arab = [], []
    for line_no, text in lines:
        for m in CJK_YEAR.finditer(text):
            cjk.append((line_no, m.group(0)))
        for m in ARABIC_YEAR.finditer(text):
            arab.append((line_no, m.group(0)))
    if cjk and arab:
        sample = "、".join(sorted({y for _, y in cjk})[:3] + sorted({y for _, y in arab})[:3])
        return [
            Finding(
                path, cjk[0][0], 0, "W_ERA", "warning",
                f"全文纪年体例混用（汉字纪年 {len(cjk)} 处，阿拉伯纪年 {len(arab)} 处）",
                f"挑一种贯穿全文；例：{sample}。人文类可全用汉字纪年，其余建议统一阿拉伯数字",
                "见文件开头",
            )
        ]
    return []


def read_md(path: Path) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8")
    return list(enumerate(text.splitlines(), start=1))


def read_docx(path: Path) -> list[tuple[int, str]]:
    from docx import Document
    from docx.oxml.ns import qn

    doc = Document(str(path))
    out: list[tuple[int, str]] = []
    idx = 0
    for p_el in doc.element.body.iter(qn("w:p")):
        idx += 1
        text = "".join(t.text or "" for t in p_el.iter(qn("w:t")))
        if text:
            out.append((idx, text))
    return out


def load(path: Path) -> list[tuple[int, str]]:
    suffix = path.suffix.lower()
    if suffix in {".md", ".markdown", ".txt"}:
        return read_md(path)
    if suffix == ".docx":
        return read_docx(path)
    raise SystemExit(f"不支持的文件类型：{path}（只处理 .md / .txt / .docx）")


def fix_text(text: str) -> str:
    return text.replace("\u3007", "零").replace("\u25cb", "零").replace("\u25ef", "零")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="中文稿件数字/纪年写法体检")
    ap.add_argument("paths", nargs="+", help="一个或多个 .md/.txt/.docx 文件，或目录")
    ap.add_argument("--recursive", "-r", action="store_true", help="目录递归")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--fix", action="store_true", help="把 〇/○ 替换为「零」（仅 .md/.txt，输出 *_fixed）")
    args = ap.parse_args(argv)

    files: list[Path] = []
    for raw in args.paths:
        p = Path(raw)
        if p.is_dir():
            pattern = "**/*" if args.recursive else "*"
            files += [q for q in sorted(p.glob(pattern)) if q.suffix.lower() in {".md", ".markdown", ".txt", ".docx"}]
        elif p.exists():
            files.append(p)
        else:
            print(f"[skip] 找不到 {p}", file=sys.stderr)

    findings: list[Finding] = []
    fixed: list[tuple[Path, Path]] = []
    for path in files:
        try:
            lines = load(path)
        except Exception as exc:  # noqa: BLE001
            print(f"[skip] 读取失败 {path}: {exc}", file=sys.stderr)
            continue
        for line_no, text in lines:
            findings += scan_text(text, str(path), line_no)
        findings += scan_mixed_era(lines, str(path))
        if args.fix and path.suffix.lower() in {".md", ".markdown", ".txt"}:
            raw = path.read_text(encoding="utf-8")
            new = fix_text(raw)
            if new != raw:
                dst = path.with_name(f"{path.stem}_fixed{path.suffix}")
                dst.write_text(new, encoding="utf-8")
                fixed.append((path, dst))

    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    if args.json:
        print(json.dumps(
            {"files": [str(p) for p in files], "errors": len(errors), "warnings": len(warnings),
             "findings": [f.as_dict() for f in findings], "fixed": [[str(a), str(b)] for a, b in fixed]},
            ensure_ascii=False, indent=2))
    else:
        for f in findings:
            print(f.as_text())
            print()
        for src, dst in fixed:
            print(f"[fix] {src} → {dst}")
        print(f"检查 {len(files)} 个文件：{len(errors)} 个 error，{len(warnings)} 个 warning。")
        if errors:
            print("处理建议：纪年统一用阿拉伯数字（1920 年），必须用汉字时写「一九二零」，不要出现 U+3007 / ○ / 拉丁 O。")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
