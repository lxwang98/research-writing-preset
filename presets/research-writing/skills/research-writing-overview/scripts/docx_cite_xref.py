#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""docx_cite_xref.py — 让正文 [n] 引用与文末参考文献互相跳转（Word 交叉引用）

为什么需要它
------------
顺序编码制的正文里写 [12]、文末写 "[12] 作者. 题名[J]…"，如果两处都是纯文本，
Word 里点不动、PDF 里点不动，读者找一条文献要翻半天；审稿人还会认为你没做交叉引用。
Word 的原生做法有两种：

  1) 内部超链接：文末每条加隐藏书签 _Ref12，正文 [12] 变成指向它的 w:hyperlink；
  2) REF 域：正文插 { REF _Ref12 \\h }，需要 F9 更新，转 PDF/给别人易出现“错误！未定义书签”。

本脚本用第 1 种：静态、不需要更新域、导出 PDF 后链接仍可点。

它做什么
--------
1. 找到「参考文献」标题（可 --ref-heading 指定），其后形如 “[12] …” 的段落，
   在段首/段尾各插一个隐藏书签 _Ref12（整条文献都可作为跳转落点）。
2. 标题之前的正文（含表格单元格）里，把所有 [12]、[3-5]、[6,9] 中的每个数字
   包成 <w:hyperlink w:anchor="_Ref12">，括号、逗号、连字符保持原样。
3. 只处理编号落在 1..参考文献条数 内的方括号，避免误伤 [2020]、[0,1] 这类文本。
4. 保留原有字体字号；默认不改颜色、不加下划线（印刷体难看），加 --style hyperlink 才用蓝色下划线。

用法
----
    python docx_cite_xref.py 稿件.docx                 # 输出 稿件_xref.docx，不动原件
    python docx_cite_xref.py 稿件.docx -o 稿件.docx     # 原地覆盖（先自己留备份）
    python docx_cite_xref.py 稿件.docx --check          # 只体检：已有多少链接、有没有断链
    python docx_cite_xref.py 稿件.docx --style hyperlink --json

验收（--check）应满足：plain_markers = 0、unresolved = 0、refs_with_bookmark = refs。
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree

CITE_RE = re.compile(r"\[\s*(\d{1,3}(?:\s*[-–—,，]\s*\d{1,3})*)\s*\]")
DIGIT_RE = re.compile(r"\d{1,3}")
ENTRY_RE = re.compile(r"^\s*\[(\d{1,3})\]")

RPR_ORDER = [
    "w:rStyle", "w:rFonts", "w:b", "w:bCs", "w:i", "w:iCs", "w:caps", "w:smallCaps",
    "w:strike", "w:dstrike", "w:outline", "w:shadow", "w:emboss", "w:imprint", "w:noProof",
    "w:snapToGrid", "w:vanish", "w:webHidden", "w:color", "w:spacing", "w:w", "w:kern",
    "w:position", "w:sz", "w:szCs", "w:highlight", "w:u", "w:effect", "w:bdr", "w:shd",
    "w:fitText", "w:vertAlign", "w:rtl", "w:cs", "w:em", "w:lang", "w:eastAsianLayout",
    "w:specVanish", "w:oMath",
]
RPR_ORDER_Q = [qn(t) for t in RPR_ORDER]

# 零宽元素：重排正文时要按原位置保留（用户手工书签、拼写标记）
ZW_TAGS_Q = {qn("w:bookmarkStart"), qn("w:bookmarkEnd"), qn("w:proofErr")}


# ---------------------------------------------------------------- rPr 工具

def set_rpr_child(rpr, tag: str, attrs: dict[str, str]) -> None:
    """按 OOXML 规定的顺序插入/替换 rPr 子元素，避免 Word 报“无法读取的内容”。"""
    q = qn(tag)
    for old in rpr.findall(q):
        rpr.remove(old)
    el = OxmlElement(tag)
    for k, v in attrs.items():
        el.set(qn(k), v)
    idx = RPR_ORDER_Q.index(q) if q in RPR_ORDER_Q else len(RPR_ORDER_Q)
    pos = 0
    for i, child in enumerate(rpr):
        if child.tag in RPR_ORDER_Q and RPR_ORDER_Q.index(child.tag) < idx:
            pos = i + 1
    rpr.insert(pos, el)


# ---------------------------------------------------------------- 段落结构

def paragraph_segments(p_el):
    """把段落拆成 [('ch', 字符, rPr) | ('zw', 元素)]。

    零宽元素（书签、拼写标记）按原位置保留——用户手工加的跳转书签不能被重建过程吃掉。
    遇到域、图、换行、已有超链接等无法安全重排的结构返回 None。
    """
    items = []
    for child in p_el:
        if child.tag == qn("w:pPr"):
            continue
        if child.tag in ZW_TAGS_Q:
            items.append(("zw", child))
            continue
        if child.tag != qn("w:r"):
            return None
        rpr = child.find(qn("w:rPr"))
        for sub in child:
            if sub.tag in (qn("w:rPr"), qn("w:lastRenderedPageBreak")):
                continue
            if sub.tag != qn("w:t"):
                return None
            for ch in (sub.text or ""):
                items.append(("ch", ch, rpr))
    return items


def text_with_flags(p_el):
    """返回 (段落文本, 每个字符是否已在超链接内)，用于 --check 统计未加链接的标记。"""
    chars, flags = [], []
    for child in p_el:
        if child.tag == qn("w:r"):
            for sub in child:
                if sub.tag == qn("w:t"):
                    for ch in (sub.text or ""):
                        chars.append(ch)
                        flags.append(False)
        elif child.tag == qn("w:hyperlink"):
            for sub in child.iter(qn("w:t")):
                for ch in (sub.text or ""):
                    chars.append(ch)
                    flags.append(True)
    return "".join(chars), flags


def make_run(text: str, rpr, anchor: int | None = None, link_style: str = "plain"):
    r = OxmlElement("w:r")
    if rpr is not None:
        new_rpr = copy.deepcopy(rpr)
    else:
        new_rpr = OxmlElement("w:rPr")
    if anchor is not None and link_style in ("plain", "hyperlink"):
        for tag in ("w:rStyle",):
            for old in new_rpr.findall(qn(tag)):
                new_rpr.remove(old)
        if link_style == "hyperlink":
            set_rpr_child(new_rpr, "w:color", {"w:val": "0563C1"})
            set_rpr_child(new_rpr, "w:u", {"w:val": "single"})
        else:
            set_rpr_child(new_rpr, "w:color", {"w:val": "auto"})
            set_rpr_child(new_rpr, "w:u", {"w:val": "none"})
    if len(new_rpr):
        r.append(new_rpr)
    t = OxmlElement("w:t")
    t.text = text
    t.set(qn("xml:space"), "preserve")
    r.append(t)
    return r


def rebuild_paragraph(p_el, items, link_style: str) -> int:
    """按 items 重建段落内容（保留 pPr）；返回生成的超链接数。"""
    pPr = p_el.find(qn("w:pPr"))
    for child in list(p_el):
        if child is not pPr:
            p_el.remove(child)
    links = 0
    for item in items:
        if item[0] == "zw":
            p_el.append(item[1])
            continue
        kind, text, rpr, anchor = item
        if kind == "link":
            hl = OxmlElement("w:hyperlink")
            hl.set(qn("w:anchor"), f"_Ref{anchor}")
            hl.append(make_run(text, rpr, anchor, link_style))
            p_el.append(hl)
            links += 1
        else:
            p_el.append(make_run(text, rpr))
    return links


def group_items(segs, linked: dict[int, int], sig_cache: dict[int, bytes]):
    items = []
    cur = None  # [kind, sig, rpr, anchor, chars]
    idx = 0
    for it in segs:
        if it[0] == "zw":
            if cur:
                items.append((cur[0], "".join(cur[4]), cur[2], cur[3]))
                cur = None
            items.append(("zw", it[1]))
            continue
        _, ch, rpr = it
        kind = "link" if idx in linked else "text"
        sig = sig_cache.setdefault(id(rpr), etree.tostring(rpr) if rpr is not None else b"")
        anchor = linked.get(idx) if kind == "link" else None
        if cur and cur[0] == kind and cur[1] == sig and cur[3] == anchor:
            cur[4].append(ch)
        else:
            if cur:
                items.append((cur[0], "".join(cur[4]), cur[2], cur[3]))
            cur = [kind, sig, rpr, anchor, [ch]]
        idx += 1
    if cur:
        items.append((cur[0], "".join(cur[4]), cur[2], cur[3]))
    return items


def link_paragraph(p_el, max_ref: int, link_style: str):
    segs = paragraph_segments(p_el)
    if segs is None:
        return None
    text = "".join(it[1] for it in segs if it[0] == "ch")
    linked: dict[int, int] = {}
    for m in CITE_RE.finditer(text):
        nums = [int(x) for x in DIGIT_RE.findall(m.group(0))]
        if not nums or any(n < 1 or n > max_ref for n in nums):
            continue  # 不是参考文献编号（如 [2020]、[0,1]）
        for dm in DIGIT_RE.finditer(m.group(0)):
            num = int(dm.group(0))
            for pos in range(m.start() + dm.start(), m.start() + dm.end()):
                linked[pos] = num
    if not linked:
        return 0
    items = group_items(segs, linked, {})
    return rebuild_paragraph(p_el, items, link_style)


# ---------------------------------------------------------------- 书签

def add_bookmark(p_el, name: str, bid: int) -> None:
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(bid))
    start.set(qn("w:name"), name)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(bid))
    pPr = p_el.find(qn("w:pPr"))
    if pPr is not None:
        pPr.addnext(start)
    else:
        p_el.insert(0, start)
    p_el.append(end)


def bookmark_names(doc) -> set[str]:
    return {b.get(qn("w:name")) for b in doc.element.body.iter(qn("w:bookmarkStart"))}


def next_bookmark_id(doc) -> int:
    ids = [int(b.get(qn("w:id"))) for b in doc.element.body.iter(qn("w:bookmarkStart"))
           if (b.get(qn("w:id")) or "").lstrip("-").isdigit()]
    return (max(ids) + 1) if ids else 0


# ---------------------------------------------------------------- 结构定位

def paragraph_text(p_el) -> str:
    return "".join(t.text or "" for t in p_el.iter(qn("w:t")))


def find_ref_heading(paragraphs: list, heading: str):
    hits = []
    for i, p_el in enumerate(paragraphs):
        if re.fullmatch(rf"\s*{re.escape(heading)}\s*", paragraph_text(p_el)):
            hits.append(i)
    if not hits:
        return None
    # 目录里的同名条目会带页码/域，纯文本相等的基本只有正文标题；取最后一个最稳
    return hits[-1]


def run(src: Path, dst: Path, heading: str, link_style: str, check_only: bool) -> dict:
    doc = Document(str(src))
    paragraphs = list(doc.element.body.iter(qn("w:p")))
    head_idx = find_ref_heading(paragraphs, heading)
    if head_idx is None and not check_only:
        raise SystemExit(f"找不到「{heading}」标题段落；用 --ref-heading 指定参考文献标题的实际写法")

    body = paragraphs[:head_idx] if head_idx is not None else paragraphs
    tail = paragraphs[head_idx + 1:] if head_idx is not None else []

    # 1) 参考文献条目编号 → 段落
    entries: dict[int, object] = {}
    for p_el in tail:
        m = ENTRY_RE.match(paragraph_text(p_el))
        if m:
            num = int(m.group(1))
            entries.setdefault(num, p_el)
    max_ref = max(entries) if entries else 0

    report = {
        "file": str(src),
        "ref_heading_index": head_idx,
        "refs": len(entries),
        "max_ref": max_ref,
        "refs_bookmarked": 0,
        "paragraphs_scanned": 0,
        "paragraphs_skipped": 0,
        "markers_linked": 0,
        "links_created": 0,
        "plain_markers": 0,
        "unresolved": [],
        "unknown_numbers": [],
    }

    if check_only:
        names = bookmark_names(doc)
        anchors = set()
        for hl in doc.element.body.iter(qn("w:hyperlink")):
            a = hl.get(qn("w:anchor"))
            if a:
                anchors.add(a)
        report["refs_bookmarked"] = sum(1 for n in entries if f"_Ref{n}" in names)
        report["links_created"] = len([a for a in anchors if a.startswith("_Ref")])
        report["unresolved"] = sorted(a for a in anchors if a not in names)
        for p_el in body:
            text, flags = text_with_flags(p_el)
            for m in CITE_RE.finditer(text):
                nums = [int(x) for x in DIGIT_RE.findall(m.group(0))]
                if not nums or any(n < 1 or n > max_ref for n in nums):
                    continue
                digits = [i for i in range(m.start(), m.end()) if text[i].isdigit()]
                if digits and all(flags[i] for i in digits):
                    report["markers_linked"] += 1
                else:
                    report["plain_markers"] += 1
        return report

    # 2) 给每个条目加隐藏书签（已存在则跳过）
    names = bookmark_names(doc)
    bid = next_bookmark_id(doc)
    for num, p_el in sorted(entries.items()):
        name = f"_Ref{num}"
        if name in names:
            continue
        add_bookmark(p_el, name, bid)
        bid += 1
        report["refs_bookmarked"] += 1

    # 3) 正文（含表格单元格）里的 [n] → 内部超链接
    allowed = set(entries)
    for p_el in body:
        if p_el.find(qn("w:hyperlink")) is not None:
            report["paragraphs_skipped"] += 1  # 已加过链接的段落整段跳过，避免重复包裹
            continue
        text = paragraph_text(p_el)
        if not CITE_RE.search(text):
            continue
        report["paragraphs_scanned"] += 1
        for m in CITE_RE.finditer(text):
            for dm in DIGIT_RE.finditer(m.group(0)):
                num = int(dm.group(0))
                if num and num not in allowed:
                    report["unknown_numbers"].append(num)
        added = link_paragraph(p_el, max_ref, link_style)
        if added is None:
            report["paragraphs_skipped"] += 1
            continue
        report["links_created"] += added
        report["markers_linked"] += len(CITE_RE.findall(text))

    report["unknown_numbers"] = sorted(set(report["unknown_numbers"]))
    dst.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(dst))
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="给 DOCX 正文 [n] 与参考文献建立交叉引用")
    ap.add_argument("docx", help="输入 .docx")
    ap.add_argument("-o", "--out", help="输出路径；默认 <原名>_xref.docx")
    ap.add_argument("--ref-heading", default="参考文献", help="参考文献标题文字，默认“参考文献”")
    ap.add_argument("--style", choices=["plain", "hyperlink"], default="plain",
                    help="plain=保持黑色无下划线（印刷体，默认）；hyperlink=蓝色下划线")
    ap.add_argument("--check", action="store_true", help="只体检当前文件，不写新文件")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出报告")
    args = ap.parse_args(argv)

    src = Path(args.docx)
    if not src.exists():
        raise SystemExit(f"找不到文件：{src}")
    dst = Path(args.out) if args.out else src.with_name(f"{src.stem}_xref.docx")

    report = run(src, dst, args.ref_heading, args.style, args.check)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"文件：{report['file']}")
        print(f"参考文献：{report['refs']} 条（最大编号 {report['max_ref']}），已加书签 {report['refs_bookmarked']} 条")
        if args.check:
            print(f"正文标记：已链接 {report['markers_linked']} 处，未链接 {report['plain_markers']} 处")
            print(f"书签锚点：{report['links_created']} 个")
            print(f"断链（指向不存在的书签）：{len(report['unresolved'])} {report['unresolved'][:10]}")
        else:
            print(f"正文段落：处理 {report['paragraphs_scanned']} 个，跳过 {report['paragraphs_skipped']} 个")
            print(f"生成超链接 {report['links_created']} 个，覆盖正文标记 {report['markers_linked']} 处")
            print(f"输出：{dst}")
        if report["unknown_numbers"]:
            print(f"提示：以下编号在正文出现但文末无对应条目，已跳过：{report['unknown_numbers'][:20]}")

    if args.check and (report["plain_markers"] or report["unresolved"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
