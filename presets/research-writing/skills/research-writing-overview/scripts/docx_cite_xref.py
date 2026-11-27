#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""docx_cite_xref.py — 让正文 [n] 引用与文末参考文献互相跳转（Word 交叉引用）

为什么需要它
------------
顺序编码制的正文里写 [12]、文末写 "[12] 作者. 题名[J]…"，如果两处都是纯文本，
Word 里点不动、PDF 里点不动，读者找一条文献要翻半天；审稿人还会认为你没做交叉引用。
Word 的原生做法有两种：

  1) 内部超链接：文末每条加隐藏书签 _Ref12，正文 [12] 变成指向它的 w:hyperlink；
  2) REF 域：正文插 { REF _Ref12 \\h }，配合文末的 SEQ 域自动编号，F9 更新。

本脚本两种都给，用 --style 选：

  reffield（默认，推荐给会手工增删文献的人）
      文末 "[12] …" → "[{ SEQ _refnum }] …"，书签 _Ref12 只包住那个 SEQ 域；
      正文 [12] → "[{ REF _Ref12 \\h }]"，[3-5] → "[{REF3}-{REF5}]"（渲染出来都是 [12]、[3-5]）。
      插一条文献、F9 更新，后面编号与正文引用一起自动后移；导出 PDF 仍是可点内链。
      代价：编号是域结果（投稿要纯文本时用 Ctrl+Shift+F9 一次性转文本）；不更新域会显示旧号；
      页面上看到的是 "[12]"，域代码只在“显示域代码”时才出现。

  hyperlink（静态备用）
      只有书签 + 超链接，点得动，但编号是死文本，增删文献要重跑脚本。

它做什么
--------
1. 找到「参考文献」标题（可 --ref-heading 指定），其后形如 “[12] …” 的段落，逐条处理。
2. 标题之前的正文（含表格单元格）里，把所有 [12]、[3-5]、[6,9] 逐个数字换成域或超链接，
   括号、逗号、连字符保持原样。
3. 只处理编号落在 1..参考文献条数 内的方括号，避免误伤 [2020]、[0,1] 这类文本。
4. 保留原有字体字号；域与链接都设为黑色无下划线（印刷体不该是蓝色）。

用法
----
    python docx_cite_xref.py 稿件.docx                  # reffield，输出 稿件_xref.docx
    python docx_cite_xref.py 稿件.docx -o 稿件.docx      # 原地覆盖（先自己留备份）
    python docx_cite_xref.py 稿件.docx --check           # 只体检：多少已链接、有没有断链
    python docx_cite_xref.py 稿件.docx --style hyperlink # 改回静态超链接
    python docx_cite_xref.py 稿件.docx --json

转完必须让 Word 更新一次域，否则 reffield 的编号停在缓存值：

    $w = New-Object -ComObject Word.Application
    $d = $w.Documents.Open("稿件_xref.docx"); 1..2 | %{ $d.Fields.Update() }; $d.Save(); $d.Close()

验收（--check，reffield）应满足：plain_markers = 0、unresolved = 0、refs_numbered = refs、
ref_fields = 正文标记数。Word 的 Hyperlinks 集合统计不到域式引用，所以 DOCX 侧看 Fields.Count，
PDF 侧用 PyMuPDF 的 get_links() 数 kind=1 的内链。
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
    """返回 (段落文本, 每个字符是否已“交叉引用”过)。

    超链接内的字符、以及域结果（separate 之后、end 之前）都算已链接：
    reffield 模式下 [12] 的数字是 REF 域的结果，不能当成没做交叉引用的纯文本。
    """
    chars, flags = [], []
    state = {"in_result": False}

    def visit(el, in_link):
        for c in el:
            tag = c.tag
            if tag == qn("w:fldChar"):
                kind = c.get(qn("w:fldCharType"))
                if kind == "separate":
                    state["in_result"] = True
                elif kind == "end":
                    state["in_result"] = False
            elif tag == qn("w:t"):
                for ch in (c.text or ""):
                    chars.append(ch)
                    flags.append(state["in_result"] or in_link)
            elif tag == qn("w:hyperlink"):
                visit(c, True)
            else:
                visit(c, in_link)

    visit(p_el, False)
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


# ------------------------------------------------------- 域（reffield 模式）

SEQ_ID = "_refnum"          # SEQ 序列名：文末编号靠它逐条自增
REF_INSTR = " REF {bm} \\h "
SEQ_INSTR = " SEQ " + SEQ_ID + " \\* ARABIC "


def plain_rpr(rpr):
    """复制 rPr 并强制黑色、无下划线——域结果不该是蓝色超链接的样子。"""
    new_rpr = copy.deepcopy(rpr) if rpr is not None else OxmlElement("w:rPr")
    for tag in ("w:rStyle",):
        for old in new_rpr.findall(qn(tag)):
            new_rpr.remove(old)
    set_rpr_child(new_rpr, "w:color", {"w:val": "auto"})
    set_rpr_child(new_rpr, "w:u", {"w:val": "none"})
    return new_rpr


def make_field_runs(instr: str, cached: str, rpr) -> list:
    """begin / instrText / separate / 缓存结果 / end 五个 run。"""
    runs = []
    for kind in ("begin", "instr", "separate", "text", "end"):
        r = OxmlElement("w:r")
        new_rpr = plain_rpr(rpr)
        if len(new_rpr):
            r.append(new_rpr)
        if kind == "instr":
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = instr
            r.append(it)
        elif kind == "text":
            t = OxmlElement("w:t")
            t.text = cached
            r.append(t)
        else:
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), kind)
            r.append(fc)
        runs.append(r)
    return runs


def _bookmark_name(el) -> str:
    return el.get(qn("w:name")) or ""


def materialize(p_el, items, bid: int) -> int:
    """把 [('zw',el) | ('t',text,rpr) | ('f',instr,cached,rpr,bm)] 写回段落。

    返回下一个可用的书签 id。文本按 rPr 归并成 run，域各自成组，
    书签（若给了 bm）只包住域本身——这样 REF 取到的就是那个编号，不含方括号。
    """
    pPr = p_el.find(qn("w:pPr"))
    for child in list(p_el):
        if child is not pPr:
            p_el.remove(child)
    for item in items:
        if item[0] == "zw":
            p_el.append(item[1])
            continue
        if item[0] == "t":
            _, text, rpr = item
            if text:
                p_el.append(make_run(text, rpr))
            continue
        _, instr, cached, rpr, bm = item
        runs = make_field_runs(instr, cached, rpr)
        if bm:
            start = OxmlElement("w:bookmarkStart")
            start.set(qn("w:id"), str(bid))
            start.set(qn("w:name"), bm)
            p_el.append(start)
        for r in runs:
            p_el.append(r)
        if bm:
            end = OxmlElement("w:bookmarkEnd")
            end.set(qn("w:id"), str(bid))
            p_el.append(end)
            bid += 1
    return bid


def flatten_segments(segs):
    """→ (chars[(字符, rPr)], zws[(字符下标, 元素)])"""
    chars, zws = [], []
    for it in segs:
        if it[0] == "zw":
            zws.append((len(chars), it[1]))
        else:
            chars.append((it[1], it[2]))
    return chars, zws


def reffield_entry_items(p_el, bm: str, cached: str):
    """文末条目：「[12] 作者. 题名…」→ 「[{SEQ}] 作者. 题名…」，书签包住 SEQ。

    bm 是这条文献的稳定书签名（_Ref7 之类）；显示编号由 SEQ 按文档顺序自动生成，
    所以书签名与显示编号不必相等——插入新条目后编号整体后移，正文 REF 仍指向同一条文献。
    """
    segs = paragraph_segments(p_el)
    if segs is None:
        return None
    # 上一轮 hyperlink 模式留下的 _Ref 书签先摘掉，否则会套两个书签
    segs = [
        it for it in segs
        if not (it[0] == "zw" and it[1].tag in (qn("w:bookmarkStart"), qn("w:bookmarkEnd"))
                and _bookmark_name(it[1]).startswith("_Ref"))
    ]
    chars, zws = flatten_segments(segs)
    text = "".join(c for c, _ in chars)
    m = ENTRY_RE.match(text)
    if not m:
        return None
    bracket = m.start() + text[m.start():].index("[")
    rpr = chars[bracket][1]
    skip = len(m.group(1)) + 2          # 原 "[12]" 的总长
    items = []
    zw_iter = iter(zws)
    nxt = next(zw_iter, None)
    i = 0
    while i < len(chars):
        while nxt is not None and nxt[0] == i:
            items.append(("zw", nxt[1]))
            nxt = next(zw_iter, None)
        if i == bracket:
            items.append(("t", "[", rpr))
            items.append(("f", SEQ_INSTR, cached, rpr, bm))
            items.append(("t", "]", rpr))
            i = bracket + skip
        else:
            items.append(("t", chars[i][0], chars[i][1]))
            i += 1
    while nxt is not None:
        items.append(("zw", nxt[1]))
        nxt = next(zw_iter, None)
    return items


def reffield_body_items(p_el, pos_to_bm: dict):
    """正文段落：[12] → [REF]，[3-5] → [REF-REF]，[6,9] → [REF,REF]。返回 (items, 标记数)。

    正文里的数字是读者看到的当前编号，按 pos_to_bm 换成对应书签；
    查不到的（编号越界）整处跳过，保持原样。
    """
    segs = paragraph_segments(p_el)
    if segs is None:
        return None, 0
    chars, zws = flatten_segments(segs)
    text = "".join(c for c, _ in chars)
    markers: dict[int, int] = {}
    for m in CITE_RE.finditer(text):
        nums = [int(x) for x in DIGIT_RE.findall(m.group(0))]
        if not nums or any(n not in pos_to_bm for n in nums):
            continue
        markers[m.start()] = m.end()
    if not markers:
        return None, 0
    items = []
    zw_iter = iter(zws)
    nxt = next(zw_iter, None)
    i = 0
    while i < len(chars):
        while nxt is not None and nxt[0] == i:
            items.append(("zw", nxt[1]))
            nxt = next(zw_iter, None)
        if i in markers:
            end = markers[i]
            items.append(("t", "[", chars[i][1]))
            j = i + 1
            while j < end - 1:
                ch, rpr = chars[j]
                if ch.isdigit():
                    k = j
                    while k < end - 1 and chars[k][0].isdigit():
                        k += 1
                    num = int("".join(chars[x][0] for x in range(j, k)))
                    items.append(("f", REF_INSTR.format(bm=pos_to_bm[num]), str(num), rpr, None))
                    j = k
                else:
                    items.append(("t", ch, rpr))
                    j += 1
            items.append(("t", "]", chars[end - 1][1]))
            i = end
        else:
            items.append(("t", chars[i][0], chars[i][1]))
            i += 1
    while nxt is not None:
        items.append(("zw", nxt[1]))
        nxt = next(zw_iter, None)
    return items, len(markers)


def existing_ref_bookmark(p_el):
    """段落里已有的 _Ref 书签名（说明这条已经编号过）。"""
    for b in p_el.iter(qn("w:bookmarkStart")):
        name = _bookmark_name(b)
        if name.startswith("_Ref"):
            return name
    return None


def convert_reffield(doc, entry_list, body, report: dict, check_only: bool) -> None:
    """entry_list 按文档顺序给出 (原编号, 段落)。"""
    bid = next_bookmark_id(doc)
    used = [int(m.group(1)) for n in bookmark_names(doc)
            if (m := re.fullmatch(r"_Ref(\d+)", n or ""))]
    next_id = (max(used) + 1) if used else 1
    pos_to_bm: dict[int, str] = {}

    for pos, (_num, p_el) in enumerate(entry_list, start=1):
        bm = existing_ref_bookmark(p_el)
        if bm and p_el.find(".//" + qn("w:fldChar")) is not None:
            # 已经编号过：书签不动，显示编号由它在序列中的位置决定
            report["refs_numbered"] += 1
            report["refs_bookmarked"] += 1
            pos_to_bm[pos] = bm
            continue
        if bm is None:
            bm = f"_Ref{next_id}"
            next_id += 1
        items = reffield_entry_items(p_el, bm, str(pos))
        if items is None:
            report["paragraphs_skipped"] += 1
            continue
        pos_to_bm[pos] = bm
        report["refs_bookmarked"] += 1
        report["ref_fields"] += 0
        if not check_only:
            bid = materialize(p_el, items, bid)
        report["refs_numbered"] += 1

    for p_el in body:
        text = paragraph_text(p_el)
        if not CITE_RE.search(text):
            continue
        if p_el.find(".//" + qn("w:fldChar")) is not None:
            report["paragraphs_skipped"] += 1   # 已转成域，不重复处理
            continue
        items, count = reffield_body_items(p_el, pos_to_bm)
        if not items:
            continue
        report["paragraphs_scanned"] += 1
        report["markers_linked"] += count
        report["links_created"] += count
        report["ref_fields"] += sum(1 for it in items if it[0] == "f")
        if not check_only:
            materialize(p_el, items, bid)
        unknown = sorted({int(x) for m in CITE_RE.finditer(text)
                          for x in DIGIT_RE.findall(m.group(0))
                          if int(x) not in pos_to_bm})
        report["unknown_numbers"].extend(unknown)


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

    # 1) 参考文献条目 → 段落（entry_list 保持文档顺序，reffield 按位置编号）
    entries: dict[int, object] = {}
    entry_list: list[tuple[int, object]] = []
    for p_el in tail:
        m = ENTRY_RE.match(paragraph_text(p_el))
        if m:
            num = int(m.group(1))
            entries.setdefault(num, p_el)
            entry_list.append((num, p_el))   # 允许编号重复（手工插入新条目后常见），按位置算
    max_ref = max(len(entry_list), max(entries) if entries else 0)

    report = {
        "file": str(src),
        "ref_heading_index": head_idx,
        "refs": len(entry_list),
        "max_ref": max_ref,
        "refs_bookmarked": 0,
        "refs_numbered": 0,
        "ref_fields": 0,
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
        instrs = [t.text or "" for t in doc.element.body.iter(qn("w:instrText"))]
        report["refs_numbered"] = sum(1 for t in instrs if SEQ_ID in t and " SEQ " in t)
        report["ref_fields"] = sum(1 for t in instrs if "_Ref" in t and " REF " in t)
        targets = set()
        for t in instrs:
            targets.update(re.findall(r"REF\s+(_Ref\d+)", t))
        report["unresolved"] = sorted(t for t in targets if t not in names)
        if not targets:      # hyperlink 模式：锚点在 w:hyperlink@w:anchor
            anchors = {hl.get(qn("w:anchor")) for hl in doc.element.body.iter(qn("w:hyperlink"))}
            anchors = {a for a in anchors if a and a.startswith("_Ref")}
            report["unresolved"] = sorted(a for a in anchors if a not in names)
            report["links_created"] = len(anchors)
            report["ref_fields"] = len(anchors)
        else:
            report["links_created"] = report["ref_fields"]
        report["refs_bookmarked"] = sum(
            1 for _num, p_el in entry_list if existing_ref_bookmark(p_el)
        )
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

    # 2) 逐条处理参考文献条目 + 正文
    if link_style == "reffield":
        convert_reffield(doc, entry_list, body, report, check_only=False)
    else:
        names = bookmark_names(doc)
        bid = next_bookmark_id(doc)
        for num, p_el in sorted(entries.items()):
            name = f"_Ref{num}"
            if name in names:
                continue
            add_bookmark(p_el, name, bid)
            bid += 1
            report["refs_bookmarked"] += 1

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
    ap.add_argument("--style", choices=["reffield", "hyperlink", "plain"], default="reffield",
                    help="reffield=SEQ/REF 域，编号随增删自动变（默认）；"
                         "hyperlink=静态内部超链接；plain=超链接但不改颜色")
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
        print(f"参考文献：{report['refs']} 条（最大编号 {report['max_ref']}），"
              f"已加书签 {report['refs_bookmarked']} 条，SEQ 编号 {report['refs_numbered']} 条")
        if args.check:
            print(f"正文标记：已链接 {report['markers_linked']} 处，未链接 {report['plain_markers']} 处")
            print(f"引用域/锚点：{report['links_created']} 个（REF 域 {report['ref_fields']} 个）")
            print(f"断链（指向不存在的书签）：{len(report['unresolved'])} {report['unresolved'][:10]}")
        else:
            print(f"正文段落：处理 {report['paragraphs_scanned']} 个，跳过 {report['paragraphs_skipped']} 个")
            print(f"生成引用 {report['links_created']} 个（REF 域 {report['ref_fields']} 个），"
                  f"覆盖正文标记 {report['markers_linked']} 处")
            print(f"输出：{dst}")
            if args.style == "reffield":
                print("下一步：Word 打开 → 全选 F9（或跑两次 Fields.Update）→ 保存；"
                      "投稿要纯文本时 Ctrl+Shift+F9 把域转成文本")
        if report["unknown_numbers"]:
            print(f"提示：以下编号在正文出现但文末无对应条目，已跳过：{report['unknown_numbers'][:20]}")

    if args.check and (report["plain_markers"] or report["unresolved"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
