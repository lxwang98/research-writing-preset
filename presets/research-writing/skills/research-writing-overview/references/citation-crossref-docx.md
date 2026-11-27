# 正文引用与参考文献的交叉引用（DOCX）

适用：中文期刊版 DOCX、系列综述合订本、学位论文送审版——凡是正文里写了 `[12]`、而文末又有编号参考文献表的地方。

## 1. 为什么“看起来有引用”不等于“有交叉引用”

`[12]` 用普通文本打出来，版面上和交叉引用一模一样：黑字、方括号、无需下划线。差别在三点，评审和读者都会碰到：

1. **点不动。** 交叉引用是可点击的内部链接，读者从正文跳到文献条目；纯文本只能靠翻页。
2. **对不上。** 参考文献表重排、增删条目后，纯文本编号不会跟着变，只能全文搜一遍手改；这正是稿件里出现 `[47]` 但文献表只有 46 条的常见原因。
3. **下游不通。** 期刊投稿系统的 HTML 版、二次排版（XML 转换、重排）与编辑部检查都按结构读引用关系；纯文本 `[12]` 在结构上不存在，一律判为“未建立引用关系”。

GB/T 7714-2015 顺序编码制只规定编号与著录格式，并不要求文档内超链接。预设把它设为期刊版交付的默认项，是为了让评审用 PDF 能点、让编号变动能被脚本一次性修正，而不是逐句搜改。

## 2. 实现方式：隐藏书签 + 内部超链接

Word 的“交叉引用”功能底层是 REF 域：域里缓存一份显示结果，靠书签取编号。它有两个毛病：

- 书签被删或改名后，域不更新就显示“错误！未定义书签。”；而更新域要靠 `Fields.Update()`，别人的机器上不会替你按 F9；
- 域是“文字 + 书签引用”，转 PDF 后是链接还是死文字取决于导出时域是否已展开，不同 Word 版本表现不一致。

预设改用更稳的组合：

| 位置 | 元素 |
|---|---|
| 参考文献第 *n* 条的整段 | `<w:bookmarkStart w:id="9001" w:name="_Ref1"/>` … `<w:bookmarkEnd w:id="9001"/>` |
| 正文 `[12]` | `<w:hyperlink w:anchor="_Ref12"><w:r>…1…</w:r><w:r>…2…</w:r></w:hyperlink>` |

书签 `_Ref<n>` 以 `_` 开头，Word 默认不显示（`ShowHidden = false` 时看不见），不会像 `_Toc` 那样在“显示书签”时冒出灰方块；超链接做成与正文同色、无下划线（`--style plain`），版面上就是普通 `[12]`。

代价：**编号是硬编码的。** 参考文献表增删条目后必须重跑脚本，或在构建阶段就按最终编号生成。接受这个代价，是因为它换来“打开即正确、转 PDF 即正确”，不依赖任何人手动按 F9。

## 3. 用脚本补（推荐，构建后一步）

```bash
python scripts/docx_cite_xref.py 稿件.docx                       # → 稿件_xref.docx
python scripts/docx_cite_xref.py 稿件.docx --style hyperlink      # 蓝色下划线版（给线上阅读）
python scripts/docx_cite_xref.py 稿件_xref.docx --check           # 体检：已链接/未链接/断链
python scripts/docx_cite_xref.py 稿件.docx --ref-heading "引用文献"  # 文献表标题不是“参考文献”时
```

脚本行为：

1. 找到 `--ref-heading`（默认“参考文献”）所在段落之后的所有 `[n] 文献` 段落，按出现顺序给每条加 `_Ref<n>` 书签；已存在同号书签则跳过。
2. 逐段扫描正文，识别 `[12]`、`[3,7]`、`[12-15]`、`[4，9]`（全角逗号也行）；编号必须落在 `1..文献条数` 内，`[2020]`、`[注]` 不会被误链。
3. 每个数字单独包一个 `w:hyperlink w:anchor="_Ref<n>"`，方括号/逗号/连字符/`-` 保持纯文本；同一段内原有加粗、下标等格式按 run 保留。
4. 已是超链接、含域（`w:fldChar`）、含图片、或位于表格单元格里的段落跳过，并计入 `skipped`。
5. `--check` 只读不写：报 `plain_markers`（还没链的标记数）、`unresolved`（指向不存在书签的断链）、`refs_bookmarked`（已加书签的条目数）。

退出码：存在断链或书签条目数少于编号最大值时返回 1。

## 4. 构建阶段直接写（自己在 `build_docx.py` 里做）

按首次出现编号的构建脚本有天然优势：编号在生成时就定了，可以在写 run 的同时写元素。

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

BID = [9000]

def add_ref_bookmark(p, n):
    """给参考文献段落 p 加 _Ref<n> 书签，包住整段。"""
    BID[0] += 1
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(BID[0]))
    start.set(qn("w:name"), f"_Ref{n}")
    pPr = p._p.pPr
    if pPr is not None:
        pPr.addnext(start)          # 必须在 pPr 之后，否则 Word 报文档损坏
    else:
        p._p.insert(0, start)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(BID[0]))
    p._p.append(end)

def add_cite_run(p, n, text="[" + str(n) + "]"):
    """正文里放一个可点击的 [n]。"""
    hl = OxmlElement("w:hyperlink")
    hl.set(qn("w:anchor"), f"_Ref{n}")
    for ch in text:
        r = OxmlElement("w:r")
        rPr = OxmlElement("w:rPr")
        color = OxmlElement("w:color"); color.set(qn("w:val"), "auto"); rPr.append(color)
        u = OxmlElement("w:u"); u.set(qn("w:val"), "none"); rPr.append(u)
        r.append(rPr)
        t = OxmlElement("w:t"); t.text = ch; t.set(qn("xml:space"), "preserve")
        r.append(t)
        hl.append(r)
    p._p.append(hl)
```

按字符拆 run 是为了让每个数字都能单独定位；整串 `[12]` 放一个 run 也能链，但相邻的 `[12][13]` 会粘成一个链接。

## 5. 与目录规则的关系（最容易踩）

`journal-docx-format.md` 第 6 节要求删掉 `_Toc*` 书签，因为它们在“显示书签/编辑标记”下是黑色方块。**这条只针对 `_Toc*`。** 若照旧清单“把 `bookmarkStart` 全清零”，`_Ref*` 会一并消失，正文链接全部变成“错误！未定义书签”。

正确顺序：

1. 构建 DOCX → 跑 `docx_cite_xref.py`；
2. Word 里更新 TOC → 设 10.5 pt/单倍行距/黑色/无下划线 → `Unlink()` → 删 `_Toc*`；
3. 保存、导出 PDF；
4. 验收：`_Toc*` = 0，`_Ref*` = 参考文献条数，`w:hyperlink` ≥ 引用标记处数。

## 6. 验收

```python
import zipfile, re, pymupdf

x = zipfile.ZipFile("稿件_v2.docx").read("word/document.xml").decode()
names = re.findall(r'<w:bookmarkStart[^>]*w:name="([^"]+)"', x)
print("_Ref:", sum(n.startswith("_Ref") for n in names),
      "_Toc:", sum(n.startswith("_Toc") for n in names),
      "hyperlink:", x.count("<w:hyperlink"))

pdf = pymupdf.open("稿件_v2.pdf")
links = [l for pg in pdf for l in pg.get_links() if l.get("kind") == 1]
print("PDF 内链:", len(links), "目标页:", sorted({l["page"] + 1 for l in links})[:5])
```

通过标准：DOCX 内 `w:hyperlink` 与正文标记处数相当（区间 `[12-15]` 会产生多个链接，因此通常略多）；PDF 内链数与之相符；参考文献起始页出现在目标页集合里；全文搜“错误！未定义书签”为 0。

Word 内另可看 `ActiveDocument.Hyperlinks.Count`，以及按住 Ctrl 点 `[12]` 是否落到对应条目。

## 7. 已知边界

- 只认阿拉伯数字方括号。作者-年份制（APA）的 `(Smith, 2020)` 不在处理范围；此时应改用书签锚的 `(Smith, 2020)` 链接，脚本不支持。
- 不判断编号是否指向“正确”的那条文献——那是内容问题，靠 `claim-source-verification` 和人工核。脚本只保证“点得动、不落空”。
- 合并 PDF（`merge_pdfs.py`）会保留页内链接，但**页码目标会失效**：内链指向原分册的页码，合并后页码变了。要么在合并前转成文字，要么在合并后按“文献标题”重建链接；系列综述合订本建议以分册 PDF 交付为主。
- 参考文献表若用制表符/表格排版，书签仍能加，但 Word 的“跳转”只能定位到行首，观感略差；优先用普通段落 + 悬挂缩进。
