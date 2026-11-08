# 科研写作模式 · DSH Agent 预设（research-writing）

一个把 **75 个学术技能**（另有 7 个按许可要求由脚本拉取）整合在一起的 DeepSeek Harness
Agent 预设。装上它，会话里的 Agent 就是一名科研写作助手：会检索真实文献、会精读与做结构化
笔记、会写英文期刊论文、会写中文毕业论文、会按目标期刊/学校要求排版与套引用格式，并且被写死
了「不许编造文献」的硬规则。

> **这是 Agent 预设，不是 Skill。**
> `cordis.patch.yml` 定义一个 Agent 的身份（persona）、工具面与技能目录；`presets/research-writing/skills/`
> 下的技能是这个 Agent 按需加载的能力包。

- 预设 id：`research-writing`
- 显示名：**科研写作模式**
- 技能：82 个（仓库直接分发 75 个，`install-extra.ps1` 拉取 7 个）
- 覆盖：选题 → 文献检索 → 精读 → 综述 → 英文期刊论文 / 中文毕业论文 → 引用格式 → 投稿 → 审稿回复

## 它和「普通对话」有什么不一样

| | 普通会话 | 装上这个预设之后 |
|---|---|---|
| 文献 | 模型凭记忆报文献，容易编 | 只允许来自 `scholar-kit` / `paper-search-pro` / `multi-source-paper-search` 的真实检索结果，引用必须带 DOI / PMID / arXiv ID |
| 写作 | 一次生成一大段 | 先确认选题与检索策略 → 证据表 `evidence.csv` → 分节写作 → 自查清单 |
| 格式 | 泛泛地「按 APA 格式」 | GB/T 7714-2015、APA-7、MLA、Chicago、BibTeX、RIS 都有对应技能与导出脚本 |
| 语种 | 中英混杂 | 英文期刊论文按目标期刊语料适配；中文毕业论文按学校模板与中文行文习惯 |
| 改稿 | 直接覆盖原稿 | 只增不删、改动留痕，不覆盖用户原稿 |

## 技能地图（按科研阶段）

| 阶段 | 代表技能 |
|---|---|
| 入口路由 | `research-writing-overview`（原创总览：把下面这些技能按阶段串起来） |
| 选题 | `academic-researcher`、`paper-bootstrap`、`hypothesis-generation`、`research-paper-writing` |
| 文献检索 | `scholar-kit`（CNKI + OpenAlex + Semantic Scholar + arXiv + NSSD + DBLP + BASE）、`paper-search-pro`、`multi-source-paper-search`、`literature-harvest`、`arxiv-lookup`、`paper-lookup`、`research-lookup` |
| 精读笔记 | `paper-analyzer`、`paper-reading-skill`、`deeppapernote`、`paper-analyzer-nature`、`scientific-critical-thinking` |
| 综述写作 | `literature-review`、`literature-review-zh`、`systematic-review-screener`、`review-article-architecture` |
| 中文毕业论文 | `chinese-thesis-workbench`、`thesis-writer-zh`、`humanities-thesis`、`dissertation-polisher-zh`、`chinese-reference-formatter`、`deai-academic-zh` |
| 英文期刊论文 | `academic-paper`、`academic-pipeline`、`nature-paper-workflow`、`paper-spine`、`write-scientific-manuscript`、`academic-writing`、`journal-adapt-writing`、`scientific-writing` |
| 引用与核对 | `citation-verifier`、`claim-source-verification`、`fetch-bib`、`wenxian`、`citation-management`、`apa-referencing` |
| 图表与投稿 | `figure-planner`、`nature-figure`、`venue-templates`、`submission-audit`、`latex-paper-skills` |
| 审稿与回复 | `paper-review-pipeline`、`manuscript-review-skill`、`AI-research-feedback`、`rebuttal-response`、`peer-review` |
| 去 AI 味 | `humanizer`、`humanize-academic-writing`、`deai-academic-zh`、`anti-defensive-writing` |

完整清单（82 个，含上游仓库与许可证）见 [`presets/research-writing/SOURCES.md`](presets/research-writing/SOURCES.md)。

## 安装

前置：一份能正常启动的 DeepSeek Harness（DSH 0.2.x）。本预设不引入新的第三方 npm 包，用的都是
DSH 自带插件（人设、文件读写、命令行、技能、计划模式、子代理、压缩等），只是按科研写作场景重新组合，
另加一套人设与技能库。

### 方式一：clone 到本地，用 link 安装（推荐，可改可更新）

```powershell
# 1. 克隆到任意目录（这里放 D:\dsh-bundles，你也可以放别处）
git clone https://github.com/lxwang98/research-writing-preset.git D:\dsh-bundles\research-writing-preset

# 2. 补齐 7 个因许可原因未入库的技能（需要 git + 能访问 github.com）
powershell -ExecutionPolicy Bypass -File D:\dsh-bundles\research-writing-preset\install-extra.ps1
```

然后在 DSH 会话里让 Agent 执行：

```
plugin_manager install_bundle target="link:D:\dsh-bundles\research-writing-preset"
```

或者直接用 CLI（路径换成你的克隆位置）：

```powershell
dsh plugin install "link:D:\dsh-bundles\research-writing-preset" --profile desktop
```

重启 DSH，新建会话时在预设选择器里选 **科研写作模式**。

### 方式二：直接从 GitHub 装（不含那 7 个技能）

如果你的 DSH 支持 `github:` 协议的 bundle：

```
plugin_manager install_bundle target="github:lxwang98/research-writing-preset"
```

装完只有 75 个技能。要补那 7 个，需要把 `install-extra.ps1` 指向已安装的包目录
（在 `%USERPROFILE%\.dsh\profiles\<profile>\node_modules\@local\dsh-preset-research-writing`），
且**每次重装都会被覆盖**，所以长期使用建议走方式一。

### 方式三：没有 git

仓库页面 → 绿色 **Code** → **Download ZIP** → 解压 → 把文件夹放到任意位置 →
把 `install-extra.ps1` 跑一遍（或跳过）→ 用上面的 `plugin_manager install_bundle` 指向该目录。

### 装完怎么用

1. 新建会话时选 **科研写作模式**（`research-writing`）。列表里没有就重启一次 DSH。
2. 开场先说清四件事：**论文类型**（英文期刊 / 中文毕业论文）、**学科**、**目标期刊或学校**、**已有材料**（数据、实验记录、初稿）。
3. 让 Agent 先加载 `research-writing-overview`（人设已把这一步写进工作方法），它是「阶段 → 技能」路由表。
4. 检索链默认 `scholar-kit`，交叉校验用 `paper-search-pro` / `multi-source-paper-search`；引用落地前用
   `citation-verifier` / `fetch-bib` / `wenxian` 核对 DOI、PMID、arXiv ID。
5. 中文毕业论文：`chinese-thesis-workbench` → `thesis-writer-zh` / `humanities-thesis` →
   `chinese-reference-formatter`（GB/T 7714-2015）→ `deai-academic-zh`。
6. 英文期刊：`academic-pipeline` → `academic-paper` / `nature-paper-workflow` → `venue-templates` →
   `submission-audit` → `rebuttal-response`。

## 仓库内容与许可边界

本仓库**只直接分发可以再分发的内容**：

| 内容 | 是否入库 | 说明 |
|---|---|---|
| `cordis.patch.yml`、`package.json`、`lib/`、`tools/`、`install-extra.ps1`、`README.md` | ✅ | 本项目的组合、脚本与文档，作者原创（MIT） |
| `presets/research-writing/skills/research-writing-overview/` | ✅ | 原创入口技能（阶段路由 + 反编造规则） |
| 74 个上游采用宽松许可的技能 | ✅ | MIT 70 / Apache-2.0 2 / MulanPSL-2.0 1 / LGPL-3.0 1，各带上游许可原文 |
| 7 个非宽松/无许可技能 | 由 `install-extra.ps1` 拉取 | CC BY-NC 4.0 ×5（Imbad0202 的论文流水线）、上游未声明许可证 ×2 |

入库技能的上游许可统计（以 `presets/research-writing/LICENSES/` 原文为准）：

| 许可 | 数量 | 代表 |
|---|---|---|
| MIT | 70 | `scholar-kit`、`nature-paper-*`、`paper-spine`、`chinese-thesis-*` |
| Apache-2.0 | 2 | `paper-search-pro`、`paper-reader` |
| MulanPSL-2.0 | 1 | `thesis-writer-zh` |
| LGPL-3.0 | 1 | `wenxian` |
| 原创 | 1 | `research-writing-overview` |

未入库、由 `install-extra.ps1` 拉取的 7 个：`academic-paper`、`academic-pipeline`、`deep-research`、
`paper-review-pipeline`、`systematic-review-screener`（CC BY-NC 4.0，仅限非商业用途）、
`apa-referencing`、`paper-polish-sentence-bank`（上游未声明许可证，仅供个人研读）。

## 目录结构

```
research-writing-preset/
├─ package.json                  # 包名 @local/dsh-preset-research-writing；dsh.bundle.patch 指向 patch
├─ cordis.patch.yml              # 预设声明：persona + 工具面 + 技能目录
├─ lib/index.js                  # 空 ESM 入口（保持模块解析路径正常）
├─ install-extra.ps1             # 拉取 7 个未入库技能
├─ tools/
│  ├─ build-from-sources.py       # 从上游 clone 重建 skills/ 的脚本（映射表在文件顶部）
│  └─ skill-overview.md           # 原创入口技能的正文
├─ LICENSE                        # MIT（只覆盖作者原创部分）
└─ presets/research-writing/
   ├─ skills/<kebab-name>/SKILL.md    # 一层目录一个技能
   ├─ SOURCES.md                      # 每个技能的上游仓库、许可证与用途
   └─ LICENSES/<owner>__<repo>.txt    # 上游许可原文
```

技能目录**只扫描一层**：`<root>/<name>/SKILL.md` 或 `<root>/<name>.md`。新增技能直接建目录、
写 `SKILL.md`（frontmatter 必须有 kebab-case `name` 与 `description`），重启 DSH 即生效，
不需要改 patch。

## 组合要点（给想改 preset 的人）

`cordis.patch.yml` 是 agent-plane 组合：

- `persona`：中文人设，写死三条铁律（文献只能来自真实检索 / 引用必须带 DOI·PMID·arXiv ID / 区分原文与转述）、
  工作方法、语言文风、工具纪律。
- `skill-filesystem` + `tool-skill`：`customSkillDirs` 用 `!!js` IIFE 解析
  `@local/dsh-preset-research-writing/package.json` 再拼 `presets/research-writing/skills`。
  **必须走 `createRequire(baseUrl).resolve(...)`**：`baseUrl` 是注册表的位置（profile 目录），
  不是 patch 文件所在目录。
- `tool-skill` 的 `catalogDescriptionMaxLength: 300`：82 个技能如果按默认 500 字符展示，
  每轮光技能目录就要吃掉一万多 token。
- `tool-pwsh` / `tool-bash` 按平台互斥启用；`tool-web` 开 search + fetch（抓期刊页与 PDF 必需）。
- 计划模式、压缩、委派各用 `cordis:group` + `isolate`，避免和宿主平面抢服务实例。
- 预设内所有行共享同一个作用域：**不要重复注册同名工具**（例如再写一行 `tool-pwsh`），否则整个预设挂载失败。

## 维护

- 更新预设：`git pull`，然后重启 DSH（link 安装，改动直接生效）。
- 重新生成技能：先把上游仓库 clone 回一个源目录（`<SRC>/<owner>__<repo>`，清单见 `SOURCES.md` 与脚本顶部映射表），
  再跑 `python tools\build-from-sources.py`。脚本按 `RESEARCH_SKILLS_SRC` 环境变量 → `..\_sources` →
  `D:\dsh-bundles\_research\src` 的顺序找源目录。
- 卸载：`plugin_manager remove_bundle @local/dsh-preset-research-writing`。
- 检索类技能依赖 Python 包：`httpx beautifulsoup4 selenium openpyxl python-docx pdfplumber pypdf PyMuPDF pyalex semanticscholar biopython arxiv requests Jinja2 PyYAML`
  （各技能目录下的 `requirements.txt` 有分项清单）。知网抓取首次运行会下载 msedgedriver，并需要你自己的知网登录态。

## 常见问题

**Q：为什么有 7 个技能要另外拉取？**
它们的上游许可是 CC BY-NC 4.0（禁止商业使用）或干脆没有许可证。把它们放进公开仓库再分发有法律风险，
所以改成脚本在你的机器上从上游拉——功能一样，只是不经过这个仓库。

**Q：Agent 还会编文献吗？**
人设里写了硬规则，检索与引用技能也会校验 DOI/PMID/arXiv ID；但最终判断仍在你自己——任何引用落地前，
让 Agent 用它检索到的条目原文对一遍。技能是减少幻觉，不是消除幻觉。

**Q：能只用中文毕业论文那一套吗？**
可以。装上后直接说「我要写中文毕业论文，学校模板是 XX」，Agent 会走 `chinese-thesis-workbench` 那条链，
不碰英文期刊技能。

**Q：技能目录会不会太占上下文？**
不会全量加载：人设要求先读 `research-writing-overview` 路由表，再按阶段只加载需要的 2–3 个技能，
目录描述也截断到 300 字符。

## 许可

本仓库作者原创部分（patch、脚本、文档、`research-writing-overview`）采用 MIT，见 [`LICENSE`](LICENSE)。
第三方技能保留各上游许可，见 [`presets/research-writing/SOURCES.md`](presets/research-writing/SOURCES.md) 与
[`presets/research-writing/LICENSES/`](presets/research-writing/LICENSES/)。
