# 技能来源与许可（SOURCES）

本预设收录 82 个技能，全部来自 GitHub 开源仓库，原样收录（仅规范化 `SKILL.md` 的 YAML frontmatter、剔除超大示例资源）。

**分发边界**：本仓库只直接分发可以再分发的技能（MIT / Apache-2.0 / MulanPSL-2.0 / LGPL-3.0，共 75 个）；
标记为「不随仓库分发」的 7 个技能，其上游许可是 CC BY-NC 4.0 或未声明许可证，由 `install-extra.ps1` 在你自己的机器上从上游拉取。
各仓库许可原文见 `LICENSES/`；使用前请遵守上游条款。

| 技能 | 上游仓库 | 许可 | 说明 |
|---|---|---|---|
| `research-writing-overview` | 本预设自带（原创） | 本预设原创（MIT） | 总览与路由：把科研全流程映射到本预设的具体技能，并给出反编造引用规则 |
| `academic-paper` | https://github.com/Imbad0202/academic-research-skills | CC BY-NC 4.0，不随仓库分发（install-extra.ps1 拉取） | 12-agent 学术论文写作流水线：11 种模式（全文/大纲/修订/摘要/文献综述/引用核查/回复审稿人）、6 类论文、5 种引用格式、双语摘要、LaTeX/DOCX/PDF 输出 |
| `academic-pipeline` | https://github.com/Imbad0202/academic-research-skills | CC BY-NC 4.0，不随仓库分发（install-extra.ps1 拉取） | 从选题到定稿的端到端论文流水线编排（研究→写作→审稿→修订→定稿） |
| `deep-research` | https://github.com/Imbad0202/academic-research-skills | CC BY-NC 4.0，不随仓库分发（install-extra.ps1 拉取） | 深度调研：把研究问题拆成可检索的子问题，多轮检索并综合成带出处的调研报告 |
| `paper-review-pipeline` | https://github.com/Imbad0202/academic-research-skills | CC BY-NC 4.0，不随仓库分发（install-extra.ps1 拉取） | 模拟期刊审稿：多角色评审意见、评分表与修改清单 |
| `systematic-review-screener` | https://github.com/Imbad0202/academic-research-skills | CC BY-NC 4.0，不随仓库分发（install-extra.ps1 拉取） | 系统综述筛查：PRISMA 流程下的标题/摘要与全文纳排筛选 |
| `academic-writing` | https://github.com/WenyuChiou/academic-writing-skills | MIT | 英文期刊写作分节训练（摘要/引言/方法/结果/讨论）＋语言润色＋期刊适配，带 evals |
| `academic-writing-zh` | https://github.com/WenyuChiou/academic-writing-skills | MIT | 同上技能的中文版（中文讲解英文写作规范，适合中文母语作者） |
| `paper-spine` | https://github.com/wubing2023/paperspine | MIT | PaperSpine 双语 10-skill 套件：论文骨架搭建、章节扩写、图表与叙事线 |
| `research-paper-writing` | https://github.com/Master-cai/Research-Paper-Writing-Skills | MIT | 科研论文写作方法论笔记（选题、贡献陈述、写作顺序、常见退稿原因） |
| `paper-polish-sentence-bank` | https://github.com/yzy1996/english-writing | 上游未声明许可证，不随仓库分发（install-extra.ps1 拉取） | 英文学术写作分节句式库与润色替换表 |
| `journal-adapt-writing` | https://github.com/wantongc/journal-adapt-writing-skill | MIT | 按目标期刊的已发表语料适配行文风格、篇幅与结构 |
| `latex-paper-skills` | https://github.com/yunshenwuchuxun/latex-paper-skills | MIT | LaTeX 论文从零到编译：选题、模板、图表、参考文献编译验证 |
| `nature-paper-workflow` | https://github.com/boom5426/nature-paper-skills | MIT | Nature 系论文工作流总调度：从故事线到投稿的阶段划分与检查点 |
| `nature-scientific-writing` | https://github.com/boom5426/nature-paper-skills | MIT | 顶刊科学写作规范：叙事结构、段落功能、时态与措辞 |
| `nature-prose-style` | https://github.com/boom5426/nature-paper-skills | MIT | 科学文风打磨：去冗余、去防御性写作、提高信息密度 |
| `write-scientific-manuscript` | https://github.com/boom5426/nature-paper-skills | MIT | 按章节撰写手稿的骨架与自查清单 |
| `manuscript-optimizer` | https://github.com/boom5426/nature-paper-skills | MIT | 手稿整体优化：逻辑链、贡献凸显、可读性 |
| `results-section-revision` | https://github.com/boom5426/nature-paper-skills | MIT | 结果部分改写：数据陈述与图表的对应关系 |
| `review-article-architecture` | https://github.com/boom5426/nature-paper-skills | MIT | 综述文章架构：分类框架、对比矩阵、研究缺口 |
| `anti-defensive-writing` | https://github.com/boom5426/nature-paper-skills | MIT | 反防御性写作：删掉过度限定与自我削弱表述 |
| `draft-marker-discipline` | https://github.com/boom5426/nature-paper-skills | MIT | 草稿标记纪律：TODO/待核实/待补数据的显式标记与清理 |
| `paper-bootstrap` | https://github.com/boom5426/nature-paper-skills | MIT | 从零起稿：确定卖点、贡献列表与章节骨架 |
| `submission-audit` | https://github.com/boom5426/nature-paper-skills | MIT | 投稿前审计：清单化检查格式、声明、附件与元数据 |
| `rebuttal-response` | https://github.com/boom5426/nature-paper-skills | MIT | 审稿意见回复信：逐条回应、措辞与证据组织 |
| `stats-reporting-audit` | https://github.com/boom5426/nature-paper-skills | MIT | 统计报告审计：效应量、置信区间、多重比较与报告规范 |
| `figure-planner` | https://github.com/boom5426/nature-paper-skills | MIT | 图表规划：每张图承担的论证任务与面板编排 |
| `nature-figure` | https://github.com/boom5426/nature-paper-skills | MIT | Nature 级配图规范：尺寸、字号、配色、矢量导出 |
| `figure-style` | https://github.com/boom5426/nature-paper-skills | MIT | 期刊图表风格统一：线宽、刻度、图例、色盲友好 |
| `nature-portfolio-playbook` | https://github.com/boom5426/nature-paper-skills | MIT | Nature 系期刊投稿策略：选刊、scope 匹配、常见 desk-reject 原因 |
| `conference-paper-writing` | https://github.com/boom5426/nature-paper-skills | MIT | 会议论文写作：篇幅约束下的贡献表达与排版 |
| `academic-presentations` | https://github.com/boom5426/nature-paper-skills | MIT | 学术汇报/答辩 PPT：叙事线、图表复用与讲述节奏 |
| `citation-verifier` | https://github.com/boom5426/nature-paper-skills | MIT | 引用核验：DOI/PMID 完整性、BibTeX 一致性、占位引用与重复条目 |
| `claim-source-verification` | https://github.com/boom5426/nature-paper-skills | MIT | 主张—证据对照：每条断言都能落到具体文献与页码 |
| `data-availability` | https://github.com/boom5426/nature-paper-skills | MIT | 数据可用性声明与仓库/附录准备 |
| `academic-researcher` | https://github.com/boom5426/nature-paper-skills | MIT | 研究者视角的研究设计：问题、假设、可行性与贡献 |
| `paper-analyzer-nature` | https://github.com/boom5426/nature-paper-skills | MIT | 论文结构化拆解：问题/方法/证据/局限 |
| `results-analysis` | https://github.com/boom5426/nature-paper-skills | MIT | 结果分析：从数据到可写进论文的结论链 |
| `paper-reviewer-nature` | https://github.com/boom5426/nature-paper-skills | MIT | Nature 风格审稿意见撰写 |
| `scholar-kit` | https://github.com/lottshin/scholar-kit | MIT | 中文优先的多源文献检索与引用导出：CNKI/OpenAlex/Semantic Scholar/arXiv/NSSD/DBLP/BASE，Crossref 补全、Unpaywall 找 OA 全文，导出 GB/T 7714 / APA / MLA / Chicago / BibTeX / RIS |
| `multi-source-paper-search` | https://github.com/PlutoLei/multi-source-paper-search | MIT | 四源并行检索 + 并查集去重 + 共识排序，降低单一数据库漏检 |
| `paper-search-pro` | https://github.com/O0000-code/paper-search-pro | Apache-2.0 | OpenAlex 五源检索与饱和曲线策略，附带检索报告生成 |
| `literature-harvest` | https://github.com/zhongzhx/literature-harvest | MIT | 批量抓取文献元数据与 PDF 全文，落盘成可复用文献库 |
| `arxiv-lookup` | https://github.com/ultimatile/arxiv-skills | MIT | arXiv 精确检索与条目解析 |
| `lit-search-strategy-zh` | https://github.com/YANZHANLIN/literature-review-skill | MIT | 中文文献检索策略构建：PICO/SPIDER 框架、数据库选择、可复现检索日志（PRISMA-S） |
| `lit-fulltext-fetch-zh` | https://github.com/YANZHANLIN/literature-review-skill | MIT | 中文文献全文获取：合法渠道、馆际互借、OA 与预印本 |
| `paper-lookup` | https://github.com/K-Dense-AI/claude-scientific-skills | MIT | 按 DOI/PMID/标题精确查论文并核对元数据 |
| `research-lookup` | https://github.com/K-Dense-AI/claude-scientific-skills | MIT | 面向研究问题的多源资料检索与证据汇总 |
| `paper-analyst` | https://github.com/flyer-Li/paper-analyst | MIT | 论文五档深度解读，所有结论标注来源段落，反幻觉 |
| `paper-reading-skill` | https://github.com/Kingslayer-bot/paper-reading-skill | MIT | 段级精读 + 20 维分析框架（问题、方法、实验、局限、可复用点） |
| `deeppapernote` | https://github.com/917Dhj/DeepPaperNote | MIT | 论文精读结构化笔记：方法拆解、公式推导、可复现清单 |
| `lit-close-reading-zh` | https://github.com/YANZHANLIN/literature-review-skill | MIT | 中文文献精读法：三遍阅读、批判性提问、笔记模板 |
| `mineru-pdf` | https://github.com/Nebutra/MinerU-Skill | MIT | PDF/扫描件转 Markdown（公式、表格、版面保留），供后续精读与检索 |
| `arxiv-paper-zh` | https://github.com/zeya-labs/arxiv-paper-zh | MIT | arXiv 论文中文翻译，保留公式与图表编号 |
| `paper-reader` | https://github.com/huangkiki/dailypaper-skills | Apache-2.0 | 单篇论文快速通读与要点卡片 |
| `lit-review-writing-zh` | https://github.com/YANZHANLIN/literature-review-skill | MIT | 中文文献综述写作：主题聚类、脉络梳理、批判性综合与引用规范 |
| `lit-review-section-zh` | https://github.com/YANZHANLIN/literature-review-skill | MIT | 把综述写进学位论文的「文献综述」章节（含过渡与评述） |
| `literature-review-synthesis` | https://github.com/K-Dense-AI/claude-scientific-skills | MIT | 英文文献综述综合：检索→筛选→证据表→叙事综合 |
| `chinese-thesis-workbench` | https://github.com/ZyhSechub/chinese-thesis-workbench-skill | MIT | 中文本科毕业论文/毕业设计全流程工作台：学校模板、任务书、开题、正文、图表登记、AIGC 降重、Word 交付 |
| `humanities-thesis` | https://github.com/ganzhi-black/humanities-thesis-skill | MIT | 中文人文社科论文写作：论证结构、材料使用、注释体例，强调不编造文献 |
| `thesis-writer-zh` | https://github.com/yanlin-cheng/skill-thesis-writer | MulanPSL-2.0 | 中文本硕学位论文写作（工科/心理/教育/管理），强制 GB/T 7714-2015 参考文献 |
| `dissertation-polisher-zh` | https://github.com/ChipsAhoyM/dissertation-polisher-zh | MIT | 中文博士论文润色：学术语体、逻辑衔接、章节一致性 |
| `deai-academic-zh` | https://github.com/houlaisan/deai-academic-zh | MIT | 中文学术文本去 AIGC 痕迹：三遍改写法，保持原意与事实零编造 |
| `chinese-reference-formatter` | https://github.com/Zechang-Xiong/chinese-reference-formatter-skill | MIT | 中文参考文献格式化：GB/T 7714-2015 全类型 + BibTeX 互转 |
| `apa-referencing` | https://github.com/keemanxp/apa-referencing-skill | 上游未声明许可证，不随仓库分发（install-extra.ps1 拉取） | APA 第 7 版参考文献与文内引用（28 种文献类型） |
| `fetch-bib` | https://github.com/MilkClouds/fetch-bib | MIT | 反幻觉 BibTeX：逐条人工确认后才写入 .bib |
| `wenxian` | https://github.com/njzjz/wenxian | LGPL-3.0 | DOI/PMID/arXiv 号一键转 BibTeX（CLI） |
| `citation-management` | https://github.com/K-Dense-AI/claude-scientific-skills | MIT | OpenAlex/PubMed/Crossref 元数据抓取、引用校验与 BibTeX 生成 |
| `reference-audit-guide` | https://github.com/boom5426/nature-paper-skills | MIT | 参考文献审计指南：逐条核验路径与常见错误 |
| `venue-templates` | https://github.com/K-Dense-AI/claude-scientific-skills | MIT | 主流期刊/会议模板与格式要求速查（LaTeX/Word） |
| `journal-paper-review` | https://github.com/WenyuChiou/academic-writing-skills | MIT | 英文期刊审稿：评审维度、意见措辞、给作者的修改建议 |
| `journal-paper-review-zh` | https://github.com/WenyuChiou/academic-writing-skills | MIT | 同上审稿技能的中文版 |
| `manuscript-review` | https://github.com/shaowen-ye/manuscript-review-skill | MIT | 六角色审稿（主编/方法/统计/领域/伦理/读者）+ 双语 docx 报告 |
| `ai-peer-review` | https://github.com/alexwortega/ai-peer-review-skill | MIT | AI 辅助同行评审：结构化评审表单与置信度标注 |
| `review-paper` | https://github.com/claesbackman/AI-research-feedback | MIT | 学术评审意见生成（MIT，侧重可操作修改建议） |
| `peer-review-kdense` | https://github.com/K-Dense-AI/claude-scientific-skills | MIT | 同行评审流程与评审意见模板 |
| `scholar-evaluation` | https://github.com/K-Dense-AI/claude-scientific-skills | MIT | 学者/论文影响力评估：指标含义与误用警告 |
| `hypothesis-generation` | https://github.com/K-Dense-AI/claude-scientific-skills | MIT | 从文献缺口生成可检验假设与研究设计 |
| `scientific-critical-thinking` | https://github.com/K-Dense-AI/claude-scientific-skills | MIT | 科研批判性思维：证据等级、偏倚识别、因果 vs 相关 |
| `scientific-writing-kdense` | https://github.com/K-Dense-AI/claude-scientific-skills | MIT | 科学写作通用规范（IMRaD、清晰度、术语一致性） |
| `humanizer` | https://github.com/blader/humanizer | MIT | 英文去 AI 写作痕迹：句式节奏、具体化、删套话 |
| `humanize-academic-writing` | https://github.com/momo2young/humanize-academic-writing | MIT | 学术文本去 AI 味（英文为主，含改写示例） |

> 统计：82 个技能；入库 75 个（MIT 66 / Apache-2.0 4 / MulanPSL-2.0 1 / LGPL-3.0 1 / 原创 1，含重复计数以 LICENSES 为准），不入库 7 个。
