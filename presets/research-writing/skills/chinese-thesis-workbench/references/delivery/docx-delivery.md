# DOCX Delivery

用于将论文源稿转成 `.docx`，或在用户明确选择时填充学校模板副本、局部编辑已有初稿。核心原则是：能复制/编辑就保留原 DOCX 格式，不能复制时再生成结构清晰、素材完整、可复制粘贴的 Word 文档。

## Supported Scope

默认 DOCX 只负责内置格式：

- 题目
- 摘要 / Abstract
- 关键词 / Keywords
- 目录标题或目录占位
- 一级、二级、三级标题
- 正文
- 图题、表题
- 表格
- 公式
- 参考文献
- 致谢
- 附录
- 代码块
- 缺失素材占位

如果学校要求严格模板格式，优先选择 M3 模板副本填充；它复制学校模板文件后只插入或替换文本，仍需用户在 Word 中人工核对目录、封面、图表和页面布局。

## Delivery Modes

- M1 default style generation: creates a new DOCX from Markdown using built-in styles.
- M2 sample style generation: creates a new DOCX from Markdown while applying high-confidence styles from `--sample-analysis`.
- M3 template copy fill: copies a school template DOCX and fills text into the copy. Use this when school formatting fidelity matters most.
- M4 existing draft edit: edits paragraph text in an existing draft with unique anchors.

M3 does not rebuild the table of contents, replace figures/tables, or guarantee every cover-field placeholder will be found. The user should update the TOC in Word and manually verify cover fields, figures, tables, and page layout.

## Default Command

```powershell
python scripts/docx/generate_thesis_docx.py thesis.md output/thesis.docx --image-map image-map.json
```

样文版式贴近生成：

```powershell
python scripts/docx/generate_thesis_docx.py thesis.md output/thesis.docx --sample-analysis paper-context/workflow/sample-docx-analysis.json
```

学校模板副本填充：

```powershell
python scripts/docx/apply_textual_edits.py --from-template school-template.docx --thesis-md paper-output/thesis.md --spec thesis-ai-standard/templates/thesis-ai-spec.yaml --out paper-output/thesis.docx
```

公式默认保留为 LaTeX 文本，便于用户后续手动转 Word 公式：

```powershell
python scripts/docx/generate_thesis_docx.py thesis.md output/thesis.docx --formula-mode latex_text
```

如果用户已经提供渲染好的公式图片，并在 image map 中用公式文本作为 key，可以选择图片模式：

```powershell
python scripts/docx/generate_thesis_docx.py thesis.md output/thesis.docx --image-map image-map.json --formula-mode formula_image
```

生成器不提供学校模板匹配参数。样文版式贴近只是高置信样式值合并，不是模板复刻。学校模板应走 `--from-template` 副本填充路径。

## 引用与参考文献的交叉引用

生成器输出的是纯文本标号 `[12]`。送审版、盲审版以及多数学校的提交要求里，正文标号要能跳到文献表，所以生成后补一步：

```powershell
python <预设>/research-writing-overview/scripts/docx_cite_xref.py output/thesis.docx
python <预设>/research-writing-overview/scripts/docx_cite_xref.py output/thesis_xref.docx --check
```

第二条命令应报"未链接 0 / 断链 0"。文献表标题不是"参考文献"时加 `--ref-heading`。脚本只加隐藏书签 `_Ref<n>` 与内部超链接，不改字号、行距、缩进；M1/M3 生成后都能跑。

配合 Word 的收尾顺序：更新目录 → 转静态 → **只删 `_Toc*` 书签**，`_Ref*` 必须保留，否则链接会变成"错误！未定义书签"。做法、验收命令与已知边界见 `research-writing-overview/references/citation-crossref-docx.md`。

纪年与数字同样在交稿前扫一遍：

```powershell
python <预设>/research-writing-overview/scripts/numeral_lint.py output/thesis.docx
```

`〇`、`○`、`◯`、全角数字的计数都应为 0；纪年写作"一九二零"或"1920"，全篇不要混用。

## Asset Rules

- 截图、图表和公式图片通过 image map 插入。
- Markdown 表格应尽量转成 Word 表格。
- 无法解析为表格时，保留文本或明确占位，不能静默丢失。
- Mermaid / PlantUML / draw.io 源码仍进入附件 DOCX。

## Markdown Cleanup

导出前必须确认正文已经清理掉 Markdown 痕迹，例如：

- `**加粗**`
- `` `code` ``
- `[链接文字](https://example.com)`

这些不能原样进入最终 `.docx`，但 LaTeX 公式源码在 `latex_text` 模式下可以保留。
