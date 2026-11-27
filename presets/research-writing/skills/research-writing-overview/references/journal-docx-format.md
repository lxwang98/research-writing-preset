# 中文期刊版 DOCX 排版规范

适用于中文综述、中文期刊论文、系列综述的期刊版交付。学校学位论文有模板的，以学校模板为先；本规范只解决“没有模板、但要排到期刊发表级”的场景。

## 1. 页面与页眉页脚

| 项目 | 规格 |
|---|---|
| 纸张 | A4，21.0 × 29.7 cm |
| 页边距 | 左右 2.6 cm，上下 2.5 cm |
| 页眉 | 9 pt，居中，内容为“课题名（一）/（二）……” |
| 页脚 | 9 pt，居中，`— PAGE —`，页码用 Word PAGE 域 |
| 分栏 | 单栏（综述类；目标期刊要求双栏时另按模板） |

## 2. 字体与字号

中文用**楷体**，西文用 **Times New Roman**。每个 run 同时设置 `w:eastAsia`（楷体）与 `w:ascii`/`w:hAnsi`（Times New Roman），不要只设一个，否则中文会回退成宋体或等线。

| 部件 | 字号 | 样式 |
|---|---|---|
| 中文标题 | 18 pt | 加粗、居中，段前 0、段后 12 pt |
| 中文摘要、关键词 | 12 pt | 1.5 倍行距，首行缩进 24 pt；“摘要：”“关键词：”标签加粗 |
| 英文标题 | 14 pt | 加粗、居中 |
| 英文摘要、Keywords | 12 pt | 1.5 倍行距，首行缩进 24 pt；标签加粗 |
| 一级标题（一、） | 14 pt | 加粗，段前 12 pt、段后 6 pt |
| 二级标题（（一）） | 12 pt | 加粗，段前 6 pt、段后 3 pt |
| 正文 | 12 pt（小四） | 1.5 倍行距，首行缩进 24 pt（2 字符），两端对齐 |
| 表格文字 | 10.5 pt（五号） | 单倍行距，单元格垂直居中 |
| 表题、图题 | 10.5 pt | 加粗、居中；表题在表上，图题在图下 |
| 数据来源 | 10.5 pt | 表下，左对齐或与表宽对齐 |
| 参考文献 | 10.5 pt | 悬挂缩进 24 pt，左对齐（不要两端对齐，否则 URL 会拉大字距） |
| 目录 | 10.5 pt | 单倍行距，段前段后 0，一级/二级 |

正文里的英文缩写、基因名、单位保持原样；不要为了“看起来整齐”给中文词加空格。

## 3. 中文混排：三个必须关掉的“自动间距”

Word 默认会给中文与西文、中文与数字之间自动加空隙。楷体下这些空隙会变成肉眼可见的方形空洞，必须显式关闭：

```python
from docx.oxml.ns import qn

for tag in ("w:autoSpaceDE", "w:autoSpaceDN"):
    el = pPr.find(qn(tag))
    if el is None:
        el = pPr.makeelement(qn(tag), {})
        pPr.append(el)
    el.set(qn("w:val"), "0")
```

规则：

1. **禁止全角空格 `U+3000`。** “摘　要”“目　录”“[1]　文献”里的全角空格在楷体下就是空心方框。一律写成“摘要：”“目录”“[1] 文献”。
2. **正文中文字符之间不插空格。** “35 岁”“HPV 疫苗”“2100 万”这类写法要么删除空格，要么交给 Word 自动间距；既然自动间距已关闭，就统一不留空格。
3. **只保留两类半角空格**：表题/图题的“表 1 ”“图 1 ”；数字与单位之间（`75 g OGTT`、`200 mg`、`5.1 mmol/L`）。单位后的中文不再加空格。
4. 中文标点用全角，英文术语内部用半角；不要把英文句号塞进中文句子。
5. **纪年与数字里的零一律写「零」，不写 `〇`。** `一九二〇年`/`一九二O年` 都不行：U+3007「〇」在楷体下就是一个裸圆环，和拉丁大写 O、圆圈符号 ○（U+25CB）、◯（U+25EF）、全角 Ｏ 在版面上无法区分，读者会读成英文字母，检索也匹配不到。写 `一九二零年`，或整篇改阿拉伯数字 `1920 年`。同一篇里汉字纪年与阿拉伯纪年不要混用（`1920 年代` 与 `二十世纪二十年代` 二选一）。
6. 全角数字 `０-９` 一律改半角。

第 5 条不要靠肉眼把关，跑 `scripts/numeral_lint.py`（见第 11 节）。

## 4. 文档结构

固定顺序：

1. 中文标题
2. 中文摘要（单段）
3. 中文关键词（3–6 个，分号分隔）
4. 英文标题
5. 英文摘要（单段）
6. 英文关键词
7. 目录（只列一级、二级标题）
8. 正文（引言 → 分主题章节 → 小结）
9. 参考文献

标题层级统一为“一、”“（一）”“1.”。不要同时出现“第一章”“1.”“1.1”三套编号。

## 5. 表格与图

### 表格

- **一律用三线表**，不用满格网格。顶线、底线各 1.5 pt（两条粗线粗细相同），表头下的栏目线 0.75 pt（约为粗线一半）；不画竖线，也不画其余横线。GB/T 7713.1—2006 只写“建议采用国际通行的三线表”，不规定磅值；1.5/0.75 是期刊与多数高校学位论文模板的通行值（常州大学、上海交大等模板明文写“标题行上框线 1.5 磅、下框线 0.75 磅”）。学校或期刊模板另有规定时以模板为准，脚本用 `--thick` / `--thin` 改。
- 实现方式：**删掉 `tblStyle`（尤其 `Table Grid`）与 `tblLook`**，逐单元格写 `tcBorders`（首行 top 粗、首行 bottom 细、末行 bottom 粗、其余 `none`、左右 `none`），并逐行删掉 `tblPrEx`。
- 三线表在 Word 里“自己做一遍就好了、一保存又变回网格”，原因只有三个，都与磅值无关：
  1. **`none` 边上写了 `w:sz="0"`**。`w:sz` 的下限是 2，Word 读到 0 会把整个 `tcBorders`/`tblBorders` 当坏数据丢掉，于是按默认样式重刷成 0.5 pt 网格。`none` 只写 `w:val="none"`（加 `space`/`color`）。
  2. **存在行级 `w:tblPrEx`**。Word 保存时会往 `w:trPr` 里写 `tblPrEx/tblBorders`（0.5 pt 全网格），它的优先级高于表级 `tblBorders`，必须逐行删除。
  3. **留着 `w:tblLook`**。带 `firstRow`/banded 条件格式标记时，Word 一保存就把 `insideH`/`insideV` 算回来；删掉 `tblLook` 后再保存，`insideH` 保持 `none`（同一文件对照实验已验证）。
- **顺序要求**：Word 更新域（`Fields.Update()`）会按默认表样式重刷边框，所以三线表必须放在 Word 收尾**之后**——先更新域、更新目录、删 `_Toc*`、保存，最后跑一次 `scripts/docx_three_line_table.py`，再从这份成品导出 PDF（导出时只读打开、不再保存）。反过来做，交付件里的表一定退回网格。
- 交付件已按上面这条链跑过以后，作者日后在 Word 里加文献、`Ctrl+A` + F9 不会毁掉三线表（已验证）；只有“重新用 `build_docx.py` 生成、还没跑三线表脚本”的文件才会是网格。
- 不要用文本框拼表；外层 1×1 排版表**不加**三线，脚本会自动跳过 1×1 表。
- **整表不跨页，不靠 `keepNext`。** 把真正的表格放进一个 1×1 无边框外层表：外层行设 `w:cantSplit`，表题也放在外层单元格内、内层表之前。这样整表（含表题）会一起移到下一页，而不会出现标题左侧的黑方块。
- 内层表首行设 `w:tblHeader`（万一超长仍可重复表头），每一行设 `w:cantSplit`。
- **禁止在表题、单元格、表后空段上设置 `w:keepNext`、`w:keepLines`、`w:pageBreakBefore`。** 这三者都会在 Word/WPS 中显示为黑色小方块。
- 表题在表上方，居中；数据来源在表下方，与表同宽。
- 列宽按内容分配，总宽不超过版心 15.8 cm；不要平均分列，否则“项目/女性/男性/目的”这类表会出现大量折行。
- 表内文字 10.5 pt；数字右对齐或居中，文字左对齐。
- 三线表不要靠肉眼确认：跑 `scripts/docx_three_line_table.py --check`（见第 11 节）。

### 分页与黑块

Word/WPS 在“显示编辑标记”打开时，会给以下段落画一个**左侧黑色小方块**：

- `w:keepNext`（与下段同页）；
- `w:keepLines`（段中不分页）；
- `w:pageBreakBefore`（段前分页）。

因此标题样式、表题、图题、表格单元格、表后空段都**不得**设置这三项。正确做法：

1. 标题不锁“与下段同页”；重建后检查每个标题是否落在页底，若是，在标题前插入**手动分页符**（`doc.add_page_break()`，或 Markdown 标记 `<!-- pagebreak -->`）。
2. 表格用上面的 1×1 外层表 + `cantSplit` 保持整表，不用 `keepNext`。
3. 图题不锁“与下段同页”；图与图题之间不要插空段。
4. 不要用 `pageBreakBefore` 制造章节起页，改用手动分页符。

验收时 DOCX 正文 XML 的 `w:keepNext`、`w:keepLines`、`w:pageBreakBefore` 计数都应为 0；这比“PDF 里看不见”可靠。

### 图

- 位图 300 dpi 起，优先 PNG/PDF/SVG；图中文字 9–11 pt，缩到 15 cm 宽后仍可读。
- 图内不要放标题；标题写在文档的图题里（“图 1 ……”）。
- 图题在图下，居中；数据来源另起一行。
- 插入宽度默认 15 cm；高宽比大于 1.25 时改为 12.5 cm，避免独占一页。

## 6. 目录：静态、无 `_Toc` 书签、无黑块

这是最容易返工的一步。Word 的 TOC 域依赖 `_Toc` 书签；书签在“显示书签/编辑标记”打开时会显示成黑色方块。直接删除书签又会让目录变成“错误！未定义书签。”。

要删的是 `_Toc*`，不是所有书签：正文引用与参考文献之间的交叉引用依赖 `_Ref<n>` 隐藏书签（第 7 节、`citation-crossref-docx.md`），这类书签必须保留。验收时看的是“`_Toc*` 计数为 0”，不是“书签总数为 0”。

正确顺序：

1. 插入 TOC 域，`\o "1-2"`，只收一级、二级标题。
2. 更新整个目录（`TablesOfContents.Item(1).Update()`）。
3. 把 `TOC 1` / `TOC 2` 段落设为 10.5 pt、单倍行距、段前段后 0、黑色、无下划线。
4. **先转静态，再删书签**：`TablesOfContents.Item(1).Range.Fields.Item(1).Unlink()`。
5. `Bookmarks.ShowHidden = true`，删除所有 `_Toc*` 书签。
6. 保存，导出 PDF；检查目录页码仍在、没有“错误！未定义书签”、DOCX 中 `_Toc*` 书签计数为 0（`_Ref*` 交叉引用书签保留，见第 7 节）。

代价：目录不再自动更新。正文改动后必须重新生成目录，再重复上述步骤。这是为“无黑块”付出的确定性代价；不要既想自动更新又想没有书签。

## 7. 构建流程（参考实现）

源文件用 Markdown，front matter 写 `title` / `abstract` / `keywords` / `title_en` / `abstract_en` / `keywords_en` / `running`；正文用 `[[key]]` 占位引用，由脚本按首次出现编号，生成 GB/T 7714 参考文献表。

```text
project/
├─ 01-主题.md
├─ refs.json
├─ assets/
└─ tools/
   ├─ build_docx.py
   └─ merge_pdfs.py
```

步骤：

1. `python tools/build_docx.py "01-主题.md" refs.json "01-主题.docx"`
2. `python <预设>/research-writing-overview/scripts/docx_cite_xref.py "01-主题.docx"` —— 默认 `--style reffield`：文献条目变成 `[` + `SEQ` 域 + `]` 并加 `_Ref` 书签，正文 `[n]` 变成 `REF` 域；插入新文献后更新域即自动重编号（说明见 `citation-crossref-docx.md`）。
3. Word COM 打开 DOCX：`Fields.Update()` 两次（域里是缓存值，不更新就是旧编号），再更新 TOC，按第 6 节转静态、只删 `_Toc*`，保存；`ExportAsFixedFormat(pdf, 17)` 先出一版整册 PDF 备查。
4. **最后**跑 `python <预设>/research-writing-overview/scripts/docx_three_line_table.py "01-主题.docx"` —— 把 `Table Grid` 网格表改成三线表（顶线=底线 1.5 pt、栏目线 0.75 pt），1×1 排版外层表自动跳过（规范与三个根因见第 5 节）。这一步必须在第 3 步之后。
5. 用第 4 步的成品**只读**打开 Word 再导一次 PDF（`Documents.Open(path, false, true)`，不 `Save()`），这份 PDF 才是交付件；此时表格线不会再被重刷。
6. `python tools/merge_pdfs.py` 合并各分册，写入一级书签。
7. 用 PyMuPDF 渲染 2–3 页抽查：摘要页、表格页、参考文献页；再点名抽查几条 `[n]`，看链接是否跳到对应文献条目。

`build_docx.py` 至少要实现：

- A4、页边距、页眉页脚；
- 中西文字体分别设置；
- `autoSpaceDE`/`autoSpaceDN` 置 0；
- 标题/正文/表格/参考文献样式；
- `[[key]]` 编号与 GB/T 7714 参考文献表；
- 表格按三线表写（逐单元格 `tcBorders`，`none` 边不写 `sz`，删 `tblStyle`/`tblLook`/`tblPrEx`），并且**在 Word 更新域之后**再跑一次 `scripts/docx_three_line_table.py` 收口；构建期直接写边框的版本会被 Word 重刷（见第 5 节）。
- 正文引用与参考文献条目的交叉引用，优先构建后跑 `scripts/docx_cite_xref.py`（REF/SEQ 域，编号自动跟随）；纯版式需求才退回 `--style hyperlink`；
- 表格 1×1 无边框外层表 + 内层三线表，`cantSplit`、`tblHeader`、列宽按内容分配；
- 标题/表题/图题/单元格不写 `keepNext`/`keepLines`/`pageBreakBefore`；孤行标题用 `<!-- pagebreak -->` 手动分页；
- 图片按高宽比限宽。

## 8. 交付前验收清单

- [ ] 纸张 A4，页边距 2.6/2.5 cm
- [ ] 中文楷体、英文 Times New Roman，正文 12 pt、1.5 倍行距、首行缩进 24 pt
- [ ] 标题 18 pt，英文标题 14 pt，H1 14 pt，H2 12 pt
- [ ] 表格 10.5 pt，整表不跨页（1×1 外层表 + `cantSplit`），表题在上、来源在下
- [ ] 表格是三线表：无 `tblStyle`（尤其 `Table Grid`）、无 `tblLook`、无行级 `tblPrEx`，顶线=底线 1.5 pt、栏目线 0.75 pt，`insideH`/`insideV`/`left`/`right` 均为 `none`（`scripts/docx_three_line_table.py --check` 输出里 `tblPrEx 0 行` 且退出码 0）
- [ ] 三线表这一步发生在 Word 更新域、删 `_Toc*`、保存**之后**；交付 PDF 由这份成品只读导出（不在 Word 里再保存）
- [ ] 参考文献 10.5 pt、悬挂缩进 24 pt、左对齐
- [ ] 源码与 DOCX 中 `U+3000` 计数为 0
- [ ] 源码与 DOCX 中 `U+3007`（〇）、`○`、`◯`、全角数字计数为 0；纪年写作「一九二零」或「1920」，全篇纪年体例统一
- [ ] 正文没有“35 岁”“HPV 疫苗”这类多余空格；数字+单位保留一个半角空格
- [ ] 目录页码正确，无“错误！未定义书签”，无蓝色下划线
- [ ] DOCX 中 `_Toc*` 书签计数为 0（`_Ref*` 交叉引用书签要保留，数量 = 参考文献条数）
- [ ] 正文 `[n]`/`[n,m]`/`[n-m]` 都能点，指向对应文献条目：REF 域数 = 引用处数字个数、SEQ 域数 = 文献条数、断链为 0（`scripts/docx_cite_xref.py --check` 退出码 0）
- [ ] 自动编号成立：在 Word 里插入一条文献、全选 F9，后续编号与正文引用一起后移
- [ ] DOCX 中 `w:keepNext`、`w:keepLines`、`w:pageBreakBefore` 计数均为 0
- [ ] PDF 渲染抽查无空心方框、无黑色方块、无表格跨页断裂

## 9. 常见故障

| 现象 | 根因 | 处理 |
|---|---|---|
| “摘□要”“[1]□文献” | 用了 U+3000 全角空格 | 改成“摘要：”“[1] 文献” |
| 中文与数字之间有空方形 | Word 自动间距 + 楷体 | 关闭 `autoSpaceDE`/`autoSpaceDN`，并清理源码空格 |
| 标题左侧/右侧黑方块 | `_Toc` 书签、`keepNext`、`keepLines` 或 `pageBreakBefore` | 先 unlink TOC 并删 `_Toc*`；再清掉标题/表题/单元格/空段的 keepNext 等属性；分页改手动分页符 |
| 目录全是“错误！未定义书签” | 删书签时 TOC 域还在 | 重新生成 TOC，先 unlink 再删 |
| 目录蓝色带下划线 | TOC 超链接样式 | 设 `Font.Color = auto`、`Underline = none` |
| 表题与表分页 | 表格行允许跨页 / 表题与表分离 | 外层 1×1 无边框表 + 行 `cantSplit`，表题放外层单元格内；不要用 keepNext |
| 表格被切成两页、只剩一行 | 移除 keepNext 后表格可在行间分页 | 用 1×1 外层表包住整表；若仍放不下，在表前补正文或手动分页 |
| 表格前大片空白 | 整表被推到下一页 | 可接受；在表前补足正文，或把表移到更合适的位置；不要用 keepNext 硬锁 |
| 参考文献 URL 字距被拉大 | 段落两端对齐 | 参考文献改左对齐 |
| “一九二O年”“一九二〇年” | 纪年里的零用了 `U+3007` 〇（或拉丁 O、○ U+25CB） | 源码改「零」；整篇也可改阿拉伯数字，但不要一半汉字一半阿拉伯；跑 `scripts/numeral_lint.py` |
| 表格是满格网格、有竖线 | 用了 `Table Grid`，或边框容器被 Word 丢掉后按默认样式重刷 | 跑 `scripts/docx_three_line_table.py`：顶/底 1.5 pt、栏目线 0.75 pt、其余 `none` |
| 三线表“编辑时对、保存后又变网格” | ① `none` 边写了 `w:sz="0"`（非法值，整个边框容器被丢弃）；② 行级 `tblPrEx` 覆盖表级边框；③ 留着 `w:tblLook` 触发重算 | 脚本已同时处理这三条；确认跑的是当前版本，且这一步在 Word 更新域之后 |
| 三线表跑完、Word 一按 F9 又变网格 | 三线表在更新域之前做，Word 按默认样式重刷了 | 顺序改成“更新域/目录 → 保存 → 三线表 → 只读导出 PDF” |
| 三线表栏目线跟顶线一样粗 | 表头行没写 `tcBorders/w:bottom`，或把 0.75 写成 1.5 | 栏目线 0.75 pt，顶线/底线 1.5 pt（学校模板另规定时按其值） |
| 正文 `[12]` 点了不跳转 | 引用是纯文本，没有书签与超链接/域 | 跑 `scripts/docx_cite_xref.py`（默认 `--style reffield`） |
| 点引用提示“错误！未定义书签” | `_Ref*` 书签被删（例如按旧清单把 `bookmarkStart` 全部清掉），或 REF 指向的书签不存在 | 只删 `_Toc*`，保留 `_Ref*`；断了就重跑脚本 |
| 插入新文献后正文编号错位 | 正文是纯文本或 `\n` 段落编号，没有 SEQ/REF 域 | 用 reffield 方案；加完文献在 Word 里 Ctrl+A、F9 更新域 |
| 引用显示的是旧编号 | 加了文献却没更新域（域里是缓存值） | `Fields.Update()` 两次，或全选 F9 |

## 10. 英文版（English edition）

以下是“没有目标刊模板”时的默认值；有 Author Guidelines 时以期刊模板为先。

| 部件 | 规格 |
|---|---|
| 正文 | Times New Roman 12 pt，1.5 倍行距，首行缩进 0.5 英寸（36 pt），两端对齐 |
| 英文标题 | Times New Roman 16–18 pt，加粗、居中 |
| 一级标题 | Times New Roman 14 pt，加粗 |
| 二级标题 | Times New Roman 12 pt，加粗 |
| 摘要 / Keywords | Times New Roman 12 pt；标签用 `Abstract:` / `Keywords:` |
| 表格与参考文献 | Times New Roman 10.5 pt；参考文献悬挂缩进 0.5 英寸、左对齐 |
| 表题 / 图题 | `Table 1 ...` 在表上，`Figure 1 ...` 在图下，10.5 pt，居中 |

英文版同样要处理的两件事：

1. **TOC 书签黑块与语言无关。** 只要用 Word 的 TOC 域，就会生成 `_Toc` 书签；显示编辑标记时同样出现黑色方块。英文 DOCX 也按第 6 节执行：更新 → 设 10.5 pt/单倍行距/黑色/无下划线 → `Unlink()` → 删除 `_Toc*`。
2. **英文中夹中文时，中文自动间距仍会作怪。** 作者名、中文参考文献、中文术语前后可能出现方形空洞；此时 `eastAsia` 用宋体或楷体，并关闭 `w:autoSpaceDE`/`w:autoSpaceDN`，同时检查 `U+3000`。
3. **`keepNext`/`keepLines`/`pageBreakBefore` 的黑方块与语言无关。** 英文标题、`Table 1` 题注、表格单元格同样不要设置这三项；表格用 1×1 外层表 + `cantSplit`，孤行标题用显式分页符。

纯英文段落没有“中文/数字自动间距”问题，但仍要检查：

- 数字与单位之间只留一个半角空格（`75 g`、`200 mg`、`5.1 mmol/L`）；
- 英文标点后一个空格，句号后两个空格不是必须，全文统一即可；
- 不要用全角空格做缩进或对齐；
- 英文标题不要用中文书名号，改用斜体或引号（按目标刊）；
- 表格中的 `Table 1` 与正文引用 `Table 1` 大小写一致。

英文版的验收清单与第 8 节相同，另加一条：**通读英文标点与空格，确认没有中文全角空格、没有中英文混排造成的方形空洞。**

## 11. 配套脚本（本技能 `scripts/` 目录）

排版规范里“能查、能改”的部分不靠肉眼，也不靠模型自觉，落成三个脚本，构建前后各跑一次。

### `numeral_lint.py` —— 纪年与数字扫描

```bash
python scripts/numeral_lint.py 01-主题.md          # 查源文件
python scripts/numeral_lint.py 01-主题.docx        # 查成品（Word 里手改过的也能查出来）
python scripts/numeral_lint.py 项目目录 -r          # 递归查整个项目
python scripts/numeral_lint.py 01-主题.md --fix     # 把 〇/○ 换成「零」，另存 *_fixed，不动原件
```

检查项：`E3007`（U+3007 〇）、`ECIRCLE`（○ U+25CB / ◯ U+25EF）、`ELATIN_O`（汉字数字旁的拉丁 O/o）、`EDIGIT_O`（`192O` 这类）、`EFULL_O`（全角 Ｏ）、`W_FULLDIG`（全角数字）、`W_ERA`（汉字纪年与阿拉伯纪年混用的警告，不计入退出码）。有 error 时退出码为 1，可直接接进构建脚本。

### `docx_three_line_table.py` —— 表格改三线表

```bash
python scripts/docx_three_line_table.py 01-主题.docx                 # 输出 01-主题_3line.docx
python scripts/docx_three_line_table.py 01-主题.docx --check          # 只体检，不合规退出码 1
python scripts/docx_three_line_table.py 01-主题.docx --thick 2.25 --thin 1.5   # 按学校模板改磅值
python scripts/docx_three_line_table.py 01-主题.docx --header-rows 2  # 两行表头，栏目线画在第二行下
```

做法：删掉 `tblStyle`（`Table Grid` 就是它让表格变成满格网格）、`tblLook`，逐行删 `tblPrEx`；逐单元格写 `tcBorders`——首行 top=粗、首行 bottom=细、末行 bottom=粗、其余 `none`、左右 `none`；`none` 边只写 `w:val="none"` 不写 `w:sz`（写 0 会被 Word 当坏数据整块丢弃，见第 5 节）；顺手补 `cantSplit` 与 `tblHeader`。1×1 排版外层表自动跳过，不会把外层框线也变成粗线。`--check` 读的是“有效边框”（单元格优先、回退表级），并额外报 `tblPrEx` 行数，`>0` 也算不合规。

**什么时候跑**：整份文档 Word 收尾（更新域、更新目录、删 `_Toc*`、保存）**之后**再跑这一次，然后从这份成品只读导出 PDF。脚本幂等，重跑不会把已经合规的表改坏。

### `docx_cite_xref.py` —— 引用与参考文献交叉引用

```bash
python scripts/docx_cite_xref.py 01-主题.docx                    # 默认 reffield：REF/SEQ 域，编号自动跟随
python scripts/docx_cite_xref.py 01-主题.docx --style hyperlink   # 退回静态内部超链接（蓝色下划线）
python scripts/docx_cite_xref.py 01-主题_xref.docx --check        # 复查：已链接/未链接/断链/域数
```

reffield 做法：参考文献第 *n* 条改成 `[` + `SEQ _refnum \* ARABIC` 域 + `]`，隐藏书签 `_Ref<n>` 只包住那个 SEQ 域；正文 `[n]` 变成 `[` + `REF _Ref<n> \h` + `]`，`[3-5]` 变成两个 REF 中间夹连字符，版面上仍显示 `[12]`、`[3-5]`。**书签名是稳定标识、不等于显示编号**：插入一条新文献并更新域后，新条目接在序列里，后续编号与正文引用一起后移。只处理编号落在 1..文献条数 范围内的方括号，`[2020]` 不会误伤；已转成域的段落重跑时跳过，不会重复包裹。

`--style hyperlink` 是静态备用：书签 + `w:hyperlink w:anchor`，点得动但编号是死文本，增删文献要重跑脚本。

局限与范围详见 `citation-crossref-docx.md`。
