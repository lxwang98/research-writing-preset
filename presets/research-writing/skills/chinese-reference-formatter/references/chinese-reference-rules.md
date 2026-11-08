# Chinese Reference Rules

Use this reference when formatting 通用中文论文参考文献. The formatter implements the common numeric bibliography templates below. User-specified journal, university, publisher, or standard-edition rules take precedence.

## Standard Version Scope

GB/T 7714—2025 was published on 2025-12-02 and took effect on 2026-07-01. See the [official standard record](https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=C6CE52E55AC09B9C79A20AEA77CEDD14).

Version 1.1.x provides a common formatting baseline, not complete conformance to either the 2015 or 2025 edition. It supports sequential numeric references; author-date citations, in-text citation management, and exhaustive 2025 document-type coverage are not implemented. Do not infer the applicable edition from the current date. If the user requests a specific edition, consult its authoritative text or the supplied style guide, adapt the output to those rules, and state any remaining unverified requirements. Keep an explicitly requested older institutional style.

## Core Principles

- Use sequential numeric labels such as `[1]`, `[2]`, `[3]` unless the user asks for another numbering mode.
- Preserve the user's input order unless the user asks to sort or merge with an existing bibliography.
- Verify metadata from public sources before formatting.
- Prefer original and official sources over aggregators.
- If a work has a formal published version, cite that version unless the user explicitly asks for the preprint.
- If no clear match exists, output `未找到与“<title>”明确对应的公开文献。`
- If sources conflict and the conflict cannot be resolved from authoritative metadata, state the ambiguity and list the competing sources.
- Keep titles and author names in the source language. Do not translate titles unless the source itself provides a translated title or the user asks for translation.

## Type and Carrier Codes

| Type | Code |
| --- | --- |
| 普通图书 | M |
| 会议录、论文集、会议论文 | C |
| 汇编 | G |
| 报纸 | N |
| 期刊 | J |
| 学位论文 | D |
| 报告 | R |
| 标准 | S |
| 专利 | P |
| 数据库 | DB |
| 计算机程序 | CP |
| 电子公告 | EB |

| Electronic carrier | Code |
| --- | --- |
| 磁带 | MT |
| 磁盘 | DK |
| 光盘 | CD |
| 联机网络 | OL |

Use combined marks such as `[J/OL]`, `[C/OL]`, `[M/OL]`, or `[EB/OL]` when the item is primarily accessed online and the style requires an access path.

## Author and Language Rules

- Up to three authors: list all.
- More than three authors: list the first three followed by `等` for Chinese works or `et al` for English works.
- Chinese author names are written as they appear in the source.
- Western personal names use family name first and initials after it, with no periods in initials, e.g. `Einstein A`.
- Preserve verified source title capitalization, including proper nouns such as DeepSeek, eBPF, and arXiv. Do not apply automatic title case. If a supplied style requires case changes, retain proper nouns.
- Use the document's `language` when supplied to choose `等` or `et al`; otherwise infer Chinese from the title, then fall back to author script.
- Volume, issue, page range, edition, and year use Arabic numerals.

## Main Formats

Use `[序号]` as the prefix in final entries.

### Journal Article

`[序号] 作者. 题名[J]. 期刊名, 年, 卷(期):页码.`

Example:

`[1] 李炳穆. 理想的图书馆员和信息专家的素质与形象[J]. 图书情报工作, 2000(2):5-8.`

### Conference Paper or Proceedings Paper

`[序号] 作者. 题名[C]//会议录或论文集名. 出版地:出版者, 出版年:页码.`

If detailed publication place and publisher are unavailable, use the confirmed venue/proceedings name and year:

`[序号] 作者. 题名[C]. 会议录或论文集名, 年:页码.`

### Book or Monograph

`[序号] 作者. 书名[M]. 版本项. 出版地:出版社, 出版年:页码.`

Omit the edition for first editions when the source does not explicitly list edition information.

### Chapter or Extracted Work

`[序号] 析出文献作者. 析出文献题名[文献类型标志]//专著作者. 专著题名. 出版地:出版者, 出版年:页码.`

### Thesis or Dissertation

`[序号] 作者. 题名[D]. 保存地:保存单位, 年份:页码.`

For BibTeX, verified master's and doctoral theses use `@mastersthesis` and `@phdthesis`. If the degree is unknown, preserve the `[D]` reference and use `@misc` with the institution in `howpublished`; do not guess a doctoral degree.

### Report

`[序号] 作者. 题名[R]. 出版地或保存地:机构, 年份:页码.`

### Patent

`[序号] 专利申请者. 专利题名[P]. 国别, 专利号. 发布日期.`

Include patent type when an authoritative source provides it.

### Standard

`[序号] 起草责任者. 标准编号. 标准名称[S]. 出版地:出版者, 出版年.`

### Newspaper

`[序号] 作者. 题名[N]. 报纸名, 年-月-日(版次).`

### Online Resource

`[序号] 作者. 题名[EB/OL]. (发布日期)[引用日期]. URL.`

For online versions of traditional publications, use the combined code:

`[序号] 作者. 题名[J/OL]. 期刊名, 年, 卷(期):页码[引用日期]. URL.`

The formatter retains the access date and URL for all traditional types with an explicit `/OL` mark, and retains a verified DOI for all types. Supply access dates from actual verification; the offline formatter does not invent them. A DOI URL can provide the access path when no separate URL is available.

## BibTeX Input and Keys

Metadata strings are plain text. The formatter escapes TeX special characters and protects title capitalization and literal organization names. Keep publication metadata from one version together. Pass all items in a batch together: keys include a digest of the complete title, authors, year, and DOI; any remaining batch collision receives a numeric suffix. Existing manuscript keys should be preserved when updating an established `.bib` file.
