#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""docx_three_line_table.py — 把 DOCX 里的表格改成三线表

为什么需要它
------------
三线表只有三条横线：顶线、栏目线（表头下）、底线，没有竖线，也没有行间横线。
预设此前的表格用的是 `Table Grid` 样式，导出来是满格网格，投稿时会被要求返工。

线宽取期刊与高校模板的通行值（GB/T 7713.1—2006 建议“采用国际通行的三线表”，
具体磅值由各刊/各校自定）：

    顶线  1.5 pt   ┐ 粗线，上下两条等粗
    栏目线 0.75 pt  │ 细线，约为粗线的一半
    底线  1.5 pt   ┘

学校或期刊另有规定时，用 --thick / --thin 覆盖：两者保持“粗线一致、栏目线更浅”的关系即可。

它做什么
--------
1. 找出文档里的“真表格”（行数 ≥2 或列数 ≥2），跳过 1×1 的排版用外层表；
2. 去掉 `Table Grid` 之类带网格的表样式，写入显式 `w:tblBorders`：
   上/下单线粗线、左右与 insideH/insideV 一律 none；
3. 表头最后一行（`--header-rows`，默认 1）的每个单元格加 0.75 pt 下边框：这就是栏目线；
4. 顺手补上 `w:cantSplit`（整行不跨页）与表头 `w:tblHeader`（跨页重复表头）；
5. `--check` 只体检不写文件，列出每张表的上下线、栏目线、竖线情况。

用法
----
    python docx_three_line_table.py 稿件.docx                  # 输出 稿件_3line.docx
    python docx_three_line_table.py 稿件.docx -o 稿件.docx      # 原地覆盖（先备份）
    python docx_three_line_table.py 稿件.docx --check           # 体检
    python docx_three_line_table.py 稿件.docx --thick 1 --thin 0.5 --header-rows 2
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# OOXML 规定的子元素顺序：插错位置 Word 会报“无法读取的内容”
TBLPR_ORDER = [
    "w:tblStyle", "w:tblpPr", "w:tblOverlap", "w:bidiVisual", "w:tblStyleRowBandSize",
    "w:tblStyleColBandSize", "w:tblW", "w:jc", "w:tblCellSpacing", "w:tblInd",
    "w:tblBorders", "w:shd", "w:tblLayout", "w:tblCellMar", "w:tblLook",
    "w:tblCaption", "w:tblDescription",
]
TCPR_ORDER = [
    "w:cnfStyle", "w:tcW", "w:gridSpan", "w:hMerge", "w:vMerge", "w:tcBorders",
    "w:shd", "w:noWrap", "w:tcMar", "w:textDirection", "w:tcFitText", "w:vAlign", "w:hideMark",
]
TRPR_ORDER = [
    "w:cnfStyle", "w:divId", "w:gridBefore", "w:gridAfter", "w:wBefore", "w:wAfter",
    "w:cantSplit", "w:trHeight", "w:tblHeader", "w:tblCellSpacing", "w:jc", "w:hidden",
]

TBL_EDGES = ["w:top", "w:left", "w:bottom", "w:right", "w:insideH", "w:insideV"]


def insert_ordered(parent, child, order: list[str]) -> None:
    """按 OOXML 顺序把 child 插到 parent 里正确的位置。"""
    tag = child.tag
    names = [qn(t) for t in order]
    if tag not in names:
        parent.append(child)
        return
    idx = names.index(tag)
    for i, existing in enumerate(parent):
        if existing.tag in names and names.index(existing.tag) > idx:
            parent.insert(i, child)
            return
    parent.append(child)


def replace_child(parent, child, order: list[str]) -> None:
    for old in parent.findall(child.tag):
        parent.remove(old)
    insert_ordered(parent, child, order)


def pt_to_eighths(pt: float) -> int:
    return max(1, int(round(pt * 8)))


def border_el(tag: str, val: str, sz_pt: float | None = None) -> OxmlElement:
    el = OxmlElement(tag)
    el.set(qn("w:val"), val)
    if val == "none":
        el.set(qn("w:sz"), "0")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "auto")
    else:
        el.set(qn("w:sz"), str(pt_to_eighths(sz_pt or 1.0)))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "000000")
    return el


def table_shape(tbl) -> tuple[int, int]:
    rows = tbl.findall(qn("w:tr"))
    cols = 0
    for tr in rows:
        cols = max(cols, len(tr.findall(qn("w:tc"))))
    return len(rows), cols


def is_layout_wrapper(tbl) -> bool:
    """1×1 的外层表是排版用的外壳（装表题+内层表），不该加三线。"""
    rows, cols = table_shape(tbl)
    return rows <= 1 and cols <= 1


def apply_three_line(tbl, thick: float, thin: float, header_rows: int) -> None:
    tblPr = tbl.find(qn("w:tblPr"))
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        tbl.insert(0, tblPr)

    # 去掉网格表样式，避免样式里的竖线/行间线盖过显式边框
    for old in tblPr.findall(qn("w:tblStyle")):
        tblPr.remove(old)

    borders = OxmlElement("w:tblBorders")
    for edge, val in (("w:top", "single"), ("w:left", "none"), ("w:bottom", "single"),
                      ("w:right", "none"), ("w:insideH", "none"), ("w:insideV", "none")):
        borders.append(border_el(edge, val, thick if val == "single" else None))
    replace_child(tblPr, borders, TBLPR_ORDER)

    rows = tbl.findall(qn("w:tr"))
    for i, tr in enumerate(rows):
        trPr = tr.find(qn("w:trPr"))
        if trPr is None:
            trPr = OxmlElement("w:trPr")
            tr.insert(0, trPr)
        if trPr.find(qn("w:cantSplit")) is None:
            insert_ordered(trPr, OxmlElement("w:cantSplit"), TRPR_ORDER)
        if i < header_rows and trPr.find(qn("w:tblHeader")) is None:
            insert_ordered(trPr, OxmlElement("w:tblHeader"), TRPR_ORDER)

    header_line_rows = range(min(header_rows, len(rows)))
    for i in header_line_rows:
        for tc in rows[i].findall(qn("w:tc")):
            tcPr = tc.find(qn("w:tcPr"))
            if tcPr is None:
                tcPr = OxmlElement("w:tcPr")
                tc.insert(0, tcPr)
            tcBorders = tcPr.find(qn("w:tcBorders"))
            if tcBorders is None:
                tcBorders = OxmlElement("w:tcBorders")
                replace_child(tcPr, tcBorders, TCPR_ORDER)
                tcBorders = tcPr.find(qn("w:tcBorders"))
            for old in tcBorders.findall(qn("w:bottom")):
                tcBorders.remove(old)
            # 只写 bottom：其余三边继续沿用表格级边框
            tcBorders.append(border_el("w:bottom", "single", thin))


def inspect_table(tbl, index: int) -> dict:
    rows, cols = table_shape(tbl)
    tblPr = tbl.find(qn("w:tblPr"))
    info = {
        "index": index,
        "rows": rows,
        "cols": cols,
        "wrapper": is_layout_wrapper(tbl),
        "tblStyle": None,
        "top_pt": None,
        "bottom_pt": None,
        "insideH": None,
        "insideV": None,
        "header_bottom_pt": None,
        "cantSplit_all": True,
    }
    if tblPr is None:
        return info
    style = tblPr.find(qn("w:tblStyle"))
    if style is not None:
        info["tblStyle"] = style.get(qn("w:val"))
    borders = tblPr.find(qn("w:tblBorders"))
    if borders is not None:
        for edge, key in (("w:top", "top_pt"), ("w:bottom", "bottom_pt")):
            el = borders.find(qn(edge))
            if el is not None and el.get(qn("w:val")) not in (None, "none"):
                info[key] = int(el.get(qn("w:sz")) or 0) / 8
            elif el is not None:
                info[key] = 0.0
        for edge, key in (("w:insideH", "insideH"), ("w:insideV", "insideV")):
            el = borders.find(qn(edge))
            info[key] = el.get(qn("w:val")) if el is not None else None
    trs = tbl.findall(qn("w:tr"))
    for tr in trs:
        trPr = tr.find(qn("w:trPr"))
        if trPr is None or trPr.find(qn("w:cantSplit")) is None:
            info["cantSplit_all"] = False
    if trs:
        bottoms = []
        for tc in trs[0].findall(qn("w:tc")):
            tcPr = tc.find(qn("w:tcPr"))
            tcBorders = tcPr.find(qn("w:tcBorders")) if tcPr is not None else None
            bottom = tcBorders.find(qn("w:bottom")) if tcBorders is not None else None
            if bottom is not None and bottom.get(qn("w:val")) not in (None, "none"):
                bottoms.append(int(bottom.get(qn("w:sz")) or 0) / 8)
        if bottoms:
            info["header_bottom_pt"] = max(bottoms)
    return info


def run(src: Path, dst: Path, thick: float, thin: float, header_rows: int, check_only: bool) -> dict:
    doc = Document(str(src))
    tables = list(doc.element.body.iter(qn("w:tbl")))
    report = {
        "file": str(src),
        "tables": len(tables),
        "converted": 0,
        "wrappers_skipped": 0,
        "thin_skipped": 0,
        "items": [],
    }
    for i, tbl in enumerate(tables):
        rows, cols = table_shape(tbl)
        if is_layout_wrapper(tbl):
            report["wrappers_skipped"] += 1
            report["items"].append(inspect_table(tbl, i))
            continue
        if rows < 2 and cols < 2:
            report["thin_skipped"] += 1
            continue
        if not check_only:
            apply_three_line(tbl, thick, thin, header_rows)
            report["converted"] += 1
        report["items"].append(inspect_table(tbl, i))
    if not check_only:
        dst.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(dst))
        report["out"] = str(dst)
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="把 DOCX 表格改成三线表")
    ap.add_argument("docx", help="输入 .docx")
    ap.add_argument("-o", "--out", help="输出路径；默认 <原名>_3line.docx")
    ap.add_argument("--thick", type=float, default=1.5, help="顶线/底线磅值，默认 1.5")
    ap.add_argument("--thin", type=float, default=0.75, help="栏目线磅值，默认 0.75（粗线的一半）")
    ap.add_argument("--header-rows", type=int, default=1, help="表头行数，栏目线画在其下方，默认 1")
    ap.add_argument("--check", action="store_true", help="只体检，不写文件")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出报告")
    args = ap.parse_args(argv)

    src = Path(args.docx)
    if not src.exists():
        raise SystemExit(f"找不到文件：{src}")
    dst = Path(args.out) if args.out else src.with_name(f"{src.stem}_3line.docx")

    report = run(src, dst, args.thick, args.thin, max(1, args.header_rows), args.check)

    real = [it for it in report["items"] if not it["wrapper"]]
    bad = [
        it for it in real
        if it["top_pt"] != args.thick
        or it["bottom_pt"] != args.thick
        or it["header_bottom_pt"] != args.thin
        or it["insideV"] not in (None, "none")
        or it["insideH"] not in (None, "none")
        or it["tblStyle"]
    ]

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"文件：{report['file']}")
        print(f"表格：{report['tables']} 个（外层排版表 {report['wrappers_skipped']} 个已跳过）")
        if not args.check:
            print(f"已转三线表：{report['converted']} 个 → {report['out']}")
        for it in real:
            print(
                f"  表{it['index']}  {it['rows']}×{it['cols']}  "
                f"顶线 {it['top_pt']} pt / 底线 {it['bottom_pt']} pt / "
                f"栏目线 {it['header_bottom_pt']} pt / "
                f"insideH {it['insideH']} / insideV {it['insideV']} / "
                f"style {it['tblStyle']}"
            )
        if bad:
            print(f"不合规表格：{len(bad)} 个（应为 顶线=底线={args.thick} pt、栏目线={args.thin} pt、无竖线）")

    if args.check and bad:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
