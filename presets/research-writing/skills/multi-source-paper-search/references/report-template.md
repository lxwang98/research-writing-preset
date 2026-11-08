# Report template — cited cross-source synthesis

The report is the product. It is not a paper dump; it is the *cross-source
reasoning* a reader can't get from any single search engine. Lead with what the
sources agree on, make disagreement impossible to miss, and credit each source
for what only it found.

Write in the user's language (match the query). Plain markdown, no images —
the reader pastes this straight into Feishu. Cite inline as `[Author Year]` or
`[title]`, and resolve every citation in the final reference list.

Use this structure:

```markdown
# 多源检索综述：<原始问题>

## 检索概况
- 查询变体：<list the 1–3 query strings actually run>
- 用了 **X / 4 源**：<sources_used>；跳过：<skipped + one-line reason each>
- 召回：去重前 <n_raw> → 去重后 <n_deduped> 篇
> 若 X < 4：提示读者「consensus 计数是相对已跑的 X 源而言」。

## 共识发现
被 ≥2 源印证、或高引 + 多源命中的核心结论。每条带引用。
这是报告的主干——把跨源都站得住的结论讲清楚。

## 分歧 / 矛盾高亮
跨源不一致的 claim：数字打架、结论相反、某源独家主张而别源未提及/反对。
没有分歧就明说「未发现跨源矛盾」——不要硬造。
（仅当 top-3 高共识/高引论文间出现 claim 冲突时，才去拉那几篇全文复核后再下判断。）

## 每源独有贡献（覆盖度补全）
| 源 | 独家捞到的代表论文 | 为什么别源没覆盖到 |
|---|---|---|
说清每个源的盲区与价值：arXiv 偏预印本、OpenAlex/S2 偏已发表、Perplexity 偏近期 web。

## 论文排名表
| # | 论文 | 年份 | 命中源 | 引用数 | consensus |
|---|---|---|---|---|---|
按 consensus 降序、再按引用降序。consensus = 命中的不同源数。
标出 per_source_unique 的条目（只有单源命中，需谨慎对待）。

## 参考文献
统一编号列表，每条含可点链接（DOI / arXiv / url）。
```

## 写作纪律

- **不要把 Perplexity 叙事当成已证结论**——它是 web 合成，需被其他源印证才进「共识」；只被它单独提的进「分歧」或「独有贡献」。
- **consensus 是相对量**：3 源跑出的 consensus=2 和 4 源跑出的 consensus=2 含义不同，概况里交代清楚口径。
- **诚实优先**：召回稀疏、源跳过多、共识薄弱时如实写，不堆砌也不粉饰。
