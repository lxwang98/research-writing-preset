<div align="center">

# 中文参考文献.skill

### Chinese Reference Formatter Skill

把“只有题名”的文献，整理成可核验的中文论文参考文献和 BibTeX。

<p>
  <img alt="Codex Skill" src="https://img.shields.io/badge/Codex-Skill-111827">
  <img alt="GB/T 7714 style" src="https://img.shields.io/badge/GB%2FT%207714-style-2f6f4e">
  <img alt="BibTeX output" src="https://img.shields.io/badge/output-BibTeX-8b5e34">
  <img alt="Python stdlib" src="https://img.shields.io/badge/Python-stdlib-3776ab">
</p>

<p>
  <a href="#效果示例">效果示例</a>
  ·
  <a href="#安装">安装</a>
  ·
  <a href="#它解决什么">它解决什么</a>
  ·
  <a href="#工作原理">工作原理</a>
  ·
  <a href="#开发">开发</a>
</p>

</div>

快速安装：

```bash
npx skills add Zechang-Xiong/chinese-reference-formatter-skill
```

需要能联网检索、访问文件并执行 Python 的 Agent；formatter 本身只依赖 Python 3.9+ 标准库。版本更新见 [CHANGELOG.md](CHANGELOG.md)。

---

## 一句话

人工整理参考文献时，最烦的是格式；让 AI 代劳时，最怕的是信息不可靠。

这个 skill 同时解决这两个问题：先核验公开元数据，再输出通用中文论文参考文献条目和 BibTeX。找不到明确文献时，它会直接说找不到；来源冲突时，它会给出歧义说明。

> 少调格式，不编参考文献。

## 格式与国标版本

当前 1.1.1 提供通用顺序编码参考文献格式，具体模板见 [格式规则](references/chinese-reference-rules.md)。**尚未声明完整符合 GB/T 7714—2015 或 GB/T 7714—2025**；输出中的“标准参考文献”是结果标签，不是合规认证。

GB/T 7714—2025 已于 2026 年 7 月 1 日实施，日期见[国家标准官方记录](https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=C6CE52E55AC09B9C79A20AEA77CEDD14)。学校或期刊指定版本时，以其要求为准，需要 Agent 对照相应规则调整输出。当前不包含著者—出版年制、正文引文管理或 2025 版全部文献类型的完整实现。

---

## 效果示例

### 你输入

```text
帮我把下面这些文献补全成中文论文参考文献格式，并输出 BibTeX：

1. Semi-supervised classification with graph convolutional networks
2. Focal loss for dense object detection
3. 理想的图书馆员和信息专家的素质与形象
```

### 它输出

以下内容由 `examples/metadata.json` 直接生成，并由测试检查与脚本保持一致。GCN 示例引用 ICLR 会议版本，使用会议页面 URL；arXiv DOI 属于预印本记录，不作为会议版本的 DOI。

````text
标准参考文献：[1] Kipf T N, Welling M. Semi-Supervised Classification with Graph Convolutional Networks[C]. International Conference on Learning Representations, 2017.
BibTeX：
```bibtex
@inproceedings{kipf-2017-semi-supervised-classification-graph-29814ac722ca,
  author = {Kipf, Thomas N and Welling, Max},
  title = {{Semi-Supervised Classification with Graph Convolutional Networks}},
  booktitle = {International Conference on Learning Representations},
  year = {2017},
  url = {https://openreview.net/forum?id=SJU4ayYgl}
}
```
核验来源：https://openreview.net/forum?id=SJU4ayYgl

标准参考文献：[2] Lin T Y, Goyal P, Girshick R, et al. Focal Loss for Dense Object Detection[C]. Proceedings of the IEEE International Conference on Computer Vision, 2017:2980-2988.
BibTeX：
```bibtex
@inproceedings{lin-2017-focal-loss-dense-f15af3b59451,
  author = {Lin, Tsung-Yi and Goyal, Priya and Girshick, Ross and He, Kaiming and Dollár, Piotr},
  title = {{Focal Loss for Dense Object Detection}},
  booktitle = {Proceedings of the IEEE International Conference on Computer Vision},
  year = {2017},
  pages = {2980--2988}
}
```
核验来源：https://openaccess.thecvf.com/content_ICCV_2017/html/Lin_Focal_Loss_for_ICCV_2017_paper.html

标准参考文献：[3] 李炳穆. 理想的图书馆员和信息专家的素质与形象[J]. 图书情报工作, 2000, 44(2):5-8,95.
BibTeX：
```bibtex
@article{ref-2000-638bf7ae27af,
  author = {李炳穆},
  title = {{理想的图书馆员和信息专家的素质与形象}},
  journal = {图书情报工作},
  year = {2000},
  volume = {44},
  number = {2},
  pages = {5--8,95}
}
```
核验来源：https://www.lis.ac.cn/CN/Y2000/V44/I2
````

如果没有可靠匹配：

```text
未找到与“definitely not a real paper title”明确对应的公开文献。
```

如果多个来源冲突：

```text
无法确定“...”的唯一对应文献：多个来源信息冲突，无法确定唯一对应文献。
```

---

## 安装

### Codex skills 目录

```bash
git clone https://github.com/Zechang-Xiong/chinese-reference-formatter-skill.git ~/.codex/skills/chinese-reference-formatter-skill
```

如果你设置了 `CODEX_HOME`：

```bash
git clone https://github.com/Zechang-Xiong/chinese-reference-formatter-skill.git "$CODEX_HOME/skills/chinese-reference-formatter-skill"
```

### skills CLI

如果你使用 open agent skills 生态的 CLI：

```bash
npx skills add Zechang-Xiong/chinese-reference-formatter-skill
```

通过 CLI 的交互选择目标 Agent。已通过此 CLI 安装的技能，可用以下命令检查并更新：

```bash
npx skills update
```

### ZIP 安装

从 [GitHub Releases](https://github.com/Zechang-Xiong/chinese-reference-formatter-skill/releases) 下载已发布版本的 ZIP，解压后把 `chinese-reference-formatter-skill` 整个目录放入目标 Agent 的 skills 目录。也可以从源码运行 `python3 scripts/package_skill.py` 生成同样的安装包。需要同时保留 `scripts/` 与 `references/`，不能只复制 `SKILL.md`。

### 调用

```text
Use $chinese-reference-formatter-skill to format these literature titles as Chinese academic references with BibTeX.
```

中文也可以：

```text
帮我把这些文献题名补全为中文参考文献格式，并给 BibTeX。
```

---

## 它解决什么

| 痛点 | 处理方式 |
| --- | --- |
| 只有论文题名，没有完整引用 | 搜索并比对公开元数据 |
| 中英文文献格式混在一起 | 统一输出中文论文参考文献格式 |
| BibTeX 和中文参考文献不一致 | 同一份标准化 JSON 同时渲染两种结果 |
| 聚合站、预印本、正式发表版本冲突 | 权威来源优先，无法判断就标记歧义 |
| 文献根本不存在或无法确认 | 明确返回未找到，不猜测 |

---

## 支持类型

| 类型 | 标识 | 典型字段 |
| --- | --- | --- |
| 期刊论文 | `J` | 作者、题名、期刊、年、卷、期、页码、DOI |
| 会议论文 | `C` | 作者、题名、会议/论文集、年、页码 |
| 图书/专著 | `M` | 作者、书名、版次、出版地、出版社、年份 |
| 析出章节 | `M` | 章节作者、章节题名、图书题名、出版社、页码 |
| 学位论文 | `D` | 作者、题名、保存地、保存单位、年份 |
| 报告 | `R` | 作者、题名、机构、年份 |
| 标准 | `S` | 标准编号、标准名称、发布机构、年份 |
| 专利 | `P` | 申请者、专利名、国别、专利号、发布日期 |
| 报纸 | `N` | 作者、题名、报纸名、日期、版次 |
| 在线资源 | `EB/OL` | 作者、题名、发布日期、引用日期、URL |

作者和语言规则：

- 3 名及以内作者全部列出。
- 超过 3 名作者，中文文献使用 `等`，英文文献使用 `et al`。
- 中文作者名按来源保留。
- 西文作者使用姓在前、名缩写在后，例如 `Einstein A`。
- 题名和作者名默认不翻译。
- 保留来源题名中的大小写，例如 `DeepSeek`、`eBPF` 和 `arXiv`。
- 可用 `language: "zh"` 或 `"en"` 指定文献语言，决定使用 `等` 还是 `et al`。
- 学位信息已核实时使用 `degree: "master"` / `"phd"`；未知学位保留 `[D]`，BibTeX 使用 `@misc`，不默认推断为博士论文。

---

## 工作原理

输入题名后，skill 做四步：

| 步骤 | 做什么 | 目的 |
| --- | --- | --- |
| 1. 读取规则 | 读取 `references/chinese-reference-rules.md` | 确认通用中文参考文献格式 |
| 2. 核验来源 | 比对题名、作者、年份、载体、DOI/ISBN/URL | 避免把错文献格式化得很漂亮 |
| 3. 解决冲突 | DOI、出版社、官方页面、标准/专利机构优先 | 在正式版、预印本、聚合信息之间做取舍 |
| 4. 渲染输出 | 调用 `scripts/format_reference.py` | 同时生成中文参考文献和 BibTeX |

核心设计是把“核验”和“排版”拆开：

- 核验阶段负责判断文献是否可信。
- formatter 阶段只负责把可信元数据稳定渲染。

---

## 直接运行 formatter

`scripts/format_reference.py` 不联网检索，只格式化已经核验过的元数据。

```bash
python3 scripts/format_reference.py --start 1 < examples/metadata.json
```

输入可以是单个对象、对象数组，或 `{ "items": [...] }`：

```json
{
  "type": "inproceedings",
  "title": "Semi-Supervised Classification with Graph Convolutional Networks",
  "authors": ["Kipf, Thomas N", "Welling, Max"],
  "booktitle": "International Conference on Learning Representations",
  "year": 2017,
  "url": "https://openreview.net/forum?id=SJU4ayYgl",
  "sources": ["https://openreview.net/forum?id=SJU4ayYgl"]
}
```

常用字段：

| 字段 | 说明 |
| --- | --- |
| `type` | 文献类型，如 `article`、`inproceedings`、`book`、`thesis`、`standard`、`online` |
| `title` | 文献题名 |
| `authors` | 作者列表，支持字符串或 `{ "family": "...", "given": "...", "suffix": "Jr." }`；机构使用 `{ "literal": "..." }`，空姓名自动忽略 |
| `journal` / `booktitle` | 期刊名或会议/论文集名 |
| `year` | 出版年份 |
| `volume` / `issue` / `pages` | 卷、期、页码 |
| `doi` / `url` | DOI 或 URL |
| `access_date` | 在线资源引用日期 |
| `mark` | 明确指定在线载体，如 `J/OL`、`C/OL`；同时提供引用日期与 URL 或 DOI |
| `language` | 文献语言，通常为 `zh` 或 `en` |
| `degree` | 已核实的 `master` / `phd`，用于 `thesis` 类型 |
| `sources` | 核验来源 URL 列表 |
| `status` | `not_found` 或 `ambiguous` 时输出对应提示 |

输入字段使用普通文本，不需要预先转义为 LaTeX。BibTeX 输出保护题名大小写、转义文本特殊字符并将页码范围写成 `--`，URL 和 DOI 保留机器可读的形式。

一次传入完整数组可以保证批次内引用键唯一。1.1.x 的引用键包含完整题名、作者、年份与 DOI 的摘要，重复键追加数字后缀。更新已有 `.bib` 时，保留原有引用键或同步修改正文，避免引用失效。

---

## 诚实边界

这个 skill 明确不做这些事：

- 不凭题名猜测文献信息。
- 不把聚合站结果自动当成权威来源。
- 不默认翻译题名或作者名。
- 不把学校、期刊或会议的特殊细则强加到所有用户身上。
- 不自动追加到项目 `.bib` 文件，除非你明确要求。

一个参考文献工具最重要的能力不是“看起来格式对”，而是知道什么时候不能确定。

---

## 仓库结构

```text
chinese-reference-formatter-skill/
├── README.md
├── SKILL.md                              # skill 入口
├── CHANGELOG.md                          # 版本变更及升级说明
├── requirements-dev.txt                  # 测试依赖
├── .github/workflows/                    # CI 与 Release 草稿
├── examples/metadata.json                # README 的可运行示例
├── agents/
│   └── openai.yaml                       # Codex 展示信息
├── references/
│   └── chinese-reference-rules.md        # 中文参考文献规则
└── scripts/
    ├── format_reference.py               # JSON -> 参考文献 + BibTeX
    ├── package_skill.py                  # 生成可分发 ZIP
    ├── test_package_skill.py             # 安装包可移植性测试
    ├── test_format_reference.py          # formatter 行为测试
    └── test_skill_content.py             # skill 内容回归测试
```

---

## 开发

formatter 仅依赖 Python 3.9+ 标准库。开发测试使用 `pytest`、YAML 校验和 BibTeX 解析器：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest scripts -q
python scripts/package_skill.py
```

GitHub Actions 配置了 Python 3.9、3.11、3.13、3.14 的测试矩阵，并保存安装包。测试覆盖：

- 各文献类型、三名以上作者及文献语言。
- 在线载体、访问日期、DOI、出版信息和歧义来源。
- 大小写、BibTeX 转义、学位类型与引用键冲突。
- 无效输入、批次顺序、README 示例一致性。
- Skill 元数据、安装包完整性和解压后从其他目录运行。

## 发布与平台发现

GitHub 是源码与版本来源。先更新 `SKILL.md` 的版本和 `CHANGELOG.md`，完成检查后，将同名版本标签（例如 `v1.1.1`）推送至 GitHub。Release 工作流会重新测试、核对版本并创建带 ZIP 的 **Release 草稿**；检查后在 GitHub 发布。

| 平台 | 分发方式 |
| --- | --- |
| [skills.sh](https://skills.sh/docs/faq) | 用户通过 `npx skills add` 安装后，平台根据安装统计自动收录和排名。 |
| [SkillsMP](https://skillsmp.com/docs/faq) | 官方说明从 GitHub 自动索引，要求有效的 `SKILL.md` 与 `claude-skills` 或 `claude-code-skill` topic；标签配置在 GitHub 仓库设置中。 |

安装与检索能力依赖客户端提供的工具。发行包使用标准 Skill 目录结构；尚未对所有 Agent 客户端做端到端验证。

---

## English

Chinese Reference Formatter Skill turns verified bibliographic metadata into Chinese academic references and BibTeX.

It provides common GB/T 7714-style numeric bibliography templates, without claiming full conformance to the 2015 or 2025 edition. It verifies public metadata first, formats confirmed records, and reports uncertainty instead of inventing missing references. The host agent needs web search, file access, and Python 3.9+ execution.

```bash
git clone https://github.com/Zechang-Xiong/chinese-reference-formatter-skill.git ~/.codex/skills/chinese-reference-formatter-skill
```

```text
Use $chinese-reference-formatter-skill to format these literature titles as Chinese academic references with BibTeX.
```

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Zechang-Xiong/chinese-reference-formatter-skill&type=Date)](https://www.star-history.com/#Zechang-Xiong/chinese-reference-formatter-skill&Date)
