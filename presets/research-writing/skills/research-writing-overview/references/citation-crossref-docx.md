# 正文引用与参考文献的交叉引用（DOCX）

适用：中文期刊版 DOCX、系列综述合订本、学位论文送审版——凡是正文里写了 `[12]`、而文末又有编号参考文献表的地方。

## 1. 为什么“看起来有引用”不等于“有交叉引用”

`[12]` 用普通文本打出来，版面上和交叉引用一模一样：黑字、方括号、无需下划线。差别在三点，评审和读者都会碰到：

1. **点不动。** 交叉引用是可点击的内部链接，读者从正文跳到文献条目；纯文本只能靠翻页。
2. **对不上。** 参考文献表重排、增删条目后，纯文本编号不会跟着变，只能全文搜一遍手改；这正是稿件里出现 `[47]` 但文献表只有 46 条的常见原因。
3. **下游不通。** 期刊投稿系统的 HTML 版、二次排版（XML 转换、重排）与编辑部检查都按结构读引用关系；纯文本 `[12]` 在结构上不存在，一律判为“未建立引用关系”。

GB/T 7714-2015 顺序编码制只规定编号与著录格式，并不要求文档内超链接。预设把它设为期刊版交付的默认项，是为了让评审用 PDF 能点、让作者自己增删文献后编号能自动跟上，而不是逐句搜改。

## 2. 两种实现，选一种

| | reffield（默认） | hyperlink（静态备用） |
|---|---|---|
| 文献条目 | `[` + `SEQ _refnum \* ARABIC` 域 + `]` | `[12]` 纯文本 + `_Ref12` 书签 |
| 正文引用 | `[` + `REF _Ref12 \h` 域 + `]` | `<w:hyperlink w:anchor="_Ref12">` |
| 增删文献后编号 | **更新域即自动重排**，正文引用一起跟着变 | 不跟随，必须重跑脚本 |
| 打开即正确 | 需要一次 `Fields.Update()`（脚本会提示；也会写入缓存值） | 是 |
| DOCX 结构统计 | `Fields.Count` / `w:instrText` | `w:hyperlink` |
| PDF 内链 | 有（`kind == 1`） | 有 |
| 适用 | 作者还会继续加文献、要送审改稿 | 版式定稿、只求能点 |

**默认用 reffield。** 唯一要记住的动作是：改完文献表在 Word 里 `Ctrl+A` + `F9`（或 `Fields.Update()` 跑两遍）。域里存的是缓存值，不更新就会停在旧编号——这是域方案的代价，也是它唯一的要求。

### reffield 为什么能自动重编号

- 文献条目的编号来自 `SEQ _refnum` 域：同一个 SEQ 序列名在文档里按出现顺序逐个自增，插一条进去，后面全部加一。
- 正文引用是 `REF _Ref12 \h` 域：它不自带编号，只是去 `_Ref12` 这个书签那里取“当前内容”，而书签包住的正是那条文献的 SEQ 域。
- 因此**书签名是稳定标识，不等于显示编号**：把一条新文献插到第 5 位，它的书签可能叫 `_Ref69`，但显示为 `[5]`；原来的第 5 条变成 `[6]`，正文里所有引用它的地方一起变成 `[6]`。
- `\h` 让 REF 同时生成可点击链接，所以 PDF 里仍然能点。**不要加 `\n`**：`\n` 取的是“段落编号”，对没有启用自动编号的段落返回 0；有人给文献段落挂了自动编号再用 `\n`，结果正文变成 `[3]-[5]` 这种带方括号的拼接（SEQ 的 lvlText 已经含括号，外面再套一层就多出来）。

## 3. 用脚本补（推荐，构建后一步）

```bash
python scripts/docx_cite_xref.py 稿件.docx                        # 默认 reffield：REF/SEQ 域
python scripts/docx_cite_xref.py 稿件.docx --style hyperlink       # 退回静态内部超链接
python scripts/docx_cite_xref.py 稿件_xref.docx --check            # 体检：已链接/未链接/断链/域数
python scripts/docx_cite_xref.py 稿件.docx --ref-heading "引用文献"  # 文献表标题不是“参考文献”时
```

脚本行为（reffield）：

1. 定位 `--ref-heading`（默认“参考文献”）段落，其后每个 `[n] 文献` 段落算一条，按文档顺序编号 1..N（手工插入后出现重复编号没关系，按位置算）。
2. 把条目的 `[n]` 换成 `[{SEQ _refnum \* ARABIC}]`，并给这个 SEQ 域套上书签 `_Ref<k>`；`k` 取当前未占用的最小可用号，**已有书签的条目原样保留**，所以重跑不会打乱身份。
3. 正文逐段识别 `[12]`、`[3,7]`、`[12-15]`、`[4，9]`（全角逗号也行），把每个数字换成 `{REF _Ref<k> \h}`；编号必须对得上某条文献，`[2020]`、`[注]` 不会被误伤。
4. 已含域（`w:fldChar`）的段落重跑时整段跳过，不会二次包裹；方括号、逗号、连字符始终是纯文本，版面上仍是 `[12]`。
5. 域 run 一律写 `w:color auto` + `w:u none`，不出现蓝色下划线。

`--check` 只读，报告：`plain_markers`（还没链的标记数）、`unresolved`（指向不存在书签的断链）、`refs_numbered`（已编号条目数）、`ref_fields`（REF 域数）、`refs_bookmarked`。有未链接或断链时退出码 1。

## 4. 构建阶段直接写（自己在 `build_docx.py` 里做）

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import copy

BID = [9000]

def make_run(text, rpr=None):
    r = OxmlElement("w:r")
    if rpr is not None:
        r.append(copy.deepcopy(rpr))
    t = OxmlElement("w:t"); t.text = text; t.set(qn("xml:space"), "preserve")
    r.append(t)
    return r

def field_runs(instr, cached, rpr=None):
    """begin / instrText / separate / 缓存结果 / end"""
    out = []
    for kind in ("begin", "instr", "separate", "text", "end"):
        r = OxmlElement("w:r")
        if rpr is not None:
            r.append(copy.deepcopy(rpr))
        if kind == "instr":
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve"); it.text = instr; r.append(it)
        elif kind == "text":
            r.append(make_run(cached, rpr).find(qn("w:t")))
        else:
            fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), kind); r.append(fc)
        out.append(r)
    return out

def add_ref_entry(p, n, bm):
    """参考文献段落：'[' + {SESSION SEQ} + ']' + 正文；书签只包 SEQ。"""
    BID[0] += 1
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(BID[0])); start.set(qn("w:name"), bm)
    p._p.append(make_run("["))
    p._p.append(start)
    for r in field_runs(" SEQ _refnum \\* ARABIC ", str(n)):
        p._p.append(r)
    end = OxmlElement("w:bookmarkEnd"); end.set(qn("w:id"), str(BID[0]))
    p._p.append(end)
    p._p.append(make_run("] " + citation_text))

def add_cite_run(p, bm, cached):
    """正文放一个可点击的 [n]：'[' + {REF} + ']'。"""
    p._p.append(make_run("["))
    for r in field_runs(f" REF {bm} \\h ", cached):
        p._p.append(r)
    p._p.append(make_run("]"))
```

按字符拆 run 是为了让区间 `[12-15]`、并列 `[3,7]` 里的每个数字各自是一个域；整串 `[12]` 放一个域也能显示，但 `[12,13]` 会变成“一个链接跳到第 12 条”，第二条点不到。

## 5. 与目录规则的关系（最容易踩）

`journal-docx-format.md` 第 6 节要求删掉 `_Toc*` 书签，因为它们在“显示书签/编辑标记”下是黑色方块。**这条只针对 `_Toc*`。** 若照旧清单“把 `bookmarkStart` 全清零”，`_Ref*` 会一并消失，正文引用全部变成“错误！未定义书签”。

正确顺序：

1. 构建 DOCX → 跑 `docx_three_line_table.py`（表格）→ 跑 `docx_cite_xref.py`（引用）；
2. Word 里 `Fields.Update()` 两次 → 更新 TOC → 设 10.5 pt/单倍行距/黑色/无下划线 → `Unlink()` → 删 `_Toc*`；
3. 保存、导出 PDF；
4. 验收：`_Toc*` = 0，`_Ref*` = 参考文献条数，`REF` 域数 = 引用处数字个数，`SEQ` 域数 = 文献条数。

## 6. 验收

```python
import zipfile, re, pymupdf

x = zipfile.ZipFile("稿件_v3.docx").read("word/document.xml").decode()
names = re.findall(r'<w:bookmarkStart[^>]*w:name="([^"]+)"', x)
print("_Ref:", sum(n.startswith("_Ref") for n in names),
      "_Toc:", sum(n.startswith("_Toc") for n in names),
      "REF 域:", len(re.findall(r"REF\s+(_Ref\d+)", x)),
      "SEQ 域:", len(re.findall(r"SEQ\s+_refnum", x)))

pdf = pymupdf.open("稿件_v3.pdf")
links = [l for pg in pdf for l in pg.get_links() if l.get("kind") == 1]
print("PDF 内链:", len(links), "目标页:", sorted({l["page"] + 1 for l in links})[:5])
```

通过标准：`REF` 域数 = 正文引用处数字个数（`[3-5]` 算 2 个）、`SEQ` 域数 = 文献条数、`_Toc*` = 0、PDF 内链数与 REF 域数一致、参考文献起始页出现在目标页集合里、全文搜“错误！未定义书签”为 0。

Word 内另可看 `ActiveDocument.Fields.Count`（应为 REF + SEQ 之和），以及按住 Ctrl 点 `[12]` 是否落到对应条目。

**投稿要纯文本时再降级**：Word 里 `Ctrl+A` + `Ctrl+Shift+F9` 把所有域转成文字，此时编号定死、链接消失——只在期刊系统不收域、或审稿要匿名文本版时做，别把这一步留在正常交付里。

## 7. 已知边界

- 只认阿拉伯数字方括号。作者-年份制（APA）的 `(Smith, 2020)` 不在处理范围；此时应改用书签锚的 `(Smith, 2020)` 链接，脚本不支持。
- 不判断编号是否指向“正确”的那条文献——那是内容问题，靠 `claim-source-verification` 和人工核。脚本只保证“点得动、编号对得上”。
- 手工在 Word 里插入的新条目，如果只是纯文本 `[5] …`，**再跑一次脚本**才会变成 SEQ 域；不跑的话它不参与计数，可能出现两个 `[5]`。同理，正文里手打的新编号 `[69]` 要重跑脚本才成域。
- 合并 PDF（`merge_pdfs.py`）会保留页内链接，但**页码目标会失效**：内链指向原分册的页码，合并后页码变了。要么在合并前转成文字，要么在合并后按“文献标题”重建链接；系列综述合订本建议以分册 PDF 交付为主。
- 参考文献表若用制表符/表格排版，书签仍能加，但 Word 的“跳转”只能定位到行首，观感略差；优先用普通段落 + 悬挂缩进。
