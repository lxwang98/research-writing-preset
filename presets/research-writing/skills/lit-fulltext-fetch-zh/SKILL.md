---
name: lit-fulltext-fetch-zh
description: 当用户无法下载已检索到的论文 PDF 时触发。按合规优先级提供六级获取策略：机构订阅 → OA 版本 → 预印本与作者版 → 作者直接请求 → 馆际互借 → 最后讨论灰色渠道。基于 Suber 2012 Open Access 理论、Piwowar 2018 OA 状况实证、Dhakal 2019 Unpaywall 评测、Himmelstein 2018 Sci-Hub eLife 学术讨论。产出获取路径决策 + 可执行工具清单 + 作者索文邮件模板。
---

# 文献获取

检索到的论文下载不到？这个 skill 给你一条合规获取路径。

## 触发

激活：
- "这篇 PDF 下载不到"
- "这本书 / 这个报告怎么拿到"
- "我没订阅这个数据库但需要这几篇"

不激活：
- 还没搜到候选论文 → `文献检索`
- 下到后不知怎么读 → `文献精读`

## 六级获取策略（按合规优先）

### Level 1｜机构订阅

通过本校 / 实验室 / 图书馆正式订阅访问。

- 校内 IP / 校园网
- VPN 进校
- 图书馆账号登录
- SSO 单点登录

**90% 的情况这一步就够。** 先试这个再走下面。

### Level 2｜开放获取（OA）版本

同一篇论文可能有多个版本：

- **Gold OA**：期刊开放版（DOAJ 收录）
- **Green OA**：作者自存档版（机构库 / 个人主页）
- **预印本**：正式发表前版本（arXiv / bioRxiv / SSRN）

**工具：**

- **Unpaywall** 浏览器插件 — 自动找 OA 版（覆盖 50%+ 文章）
- **Open Access Button** — 同上，部分覆盖互补
- **Google Scholar** — 查该文章是否有 PDF 链接
- **ResearchGate** — 搜作者是否上传

详见 `references/oa-landscape.md`。

### Level 3｜预印本与作者版本

如果期刊版不行：

- **arXiv / bioRxiv / medRxiv / SSRN / PsyArXiv** — 按学科搜
- **作者个人主页 / 实验室主页** — 常有 preprint PDF
- **Google Scholar 作者档案** — 显示作者上传的版本

**注意：** 预印本 vs 期刊版可能有差异，引用时注明版本。

### Level 4｜作者直接请求

给论文作者发邮件索要。

- 通讯作者的邮箱在论文首页
- 用 `assets/author-request-email.md` 的中英模板
- 通常 1-3 天回复，回复率 50%+

**这是完全合规的**。作者也希望自己的论文被读到。

### Level 5｜馆际互借 / 本地资源

- **本校图书馆 ILL**（Inter-Library Loan）— 免费，通常 3-7 天
- **CALIS**（中国高等教育文献保障系统）— 高校联合
- **NSTL**（国家科技图书文献中心）— 非校际补充

详见 `references/china-access.md`。

### Level 6｜灰色渠道（仅作为学术讨论）

**Sci-Hub / Library Genesis 等。** 本 skill **不推荐使用**。

- 法律状态：各国不同，多数国家不合规
- 学术伦理：广泛争议
- Himmelstein et al. (2018, eLife) 的**学术研究**分析了 Sci-Hub 覆盖率与伦理，仅作为背景讨论参考

详见 `references/ethics-discussion.md`。

## 不同来源类型的特殊策略

### 期刊论文

- 优先 Level 1-2
- Level 4 作者请求回复率最高（作者愿意分享）

### 书籍 / 教材

- Level 1 图书馆借阅（实体 / 电子）
- **超星 / 读秀** — 中文书最全
- 单章节：WorldCat 找图书馆，ILL 申请复印
- 整本书：购买（Amazon / JD / 出版社官网）

### 会议论文

- IEEE / ACM 订阅或个人购买
- 作者个人主页（CS 领域常上传）
- arXiv（作者版）

### 学位论文

- 本校：从本校图书馆
- 国内其他校：CNKI / 万方 / 读秀
- 海外：ProQuest / 作者请求

### 政府 / 行业报告

- 官方网站免费公开（一般）
- 行业报告有时需付费（Deloitte / McKinsey / PwC 部分付费）
- 政策文件：中国政府网 / 各部委官网

### 标准（国标 / ISO / IEEE）

- 国标：**全国标准信息公共服务平台**（免费看部分）
- ISO：付费（昂贵）— 通过校图书馆或 ILL
- IEEE：订阅或个人购买

## 中国本地化重点

### CALIS

中国高等教育文献保障系统。免费：

- 本校不订阅但 CALIS 成员校订阅的期刊 / 书
- 通过本校图书馆提交申请
- 通常 1-3 天送文献电子版

### NSTL

国家科技图书文献中心。免费：

- 文献传递服务
- 网址：www.nstl.gov.cn
- 注册 → 申请 → 收到 PDF

### 个别学校的限制

- 部分高校订阅率低 → ILL 请求量大
- 读秀 / 超星对一些学校是主要补充

详见 `references/china-access.md`。

## 雷区

1. **直接放弃**：第一级失败就认为"这篇搞不到"——你还有 4-5 层没试
2. **用工具但忘记记录版本** — 预印本 vs 期刊版混用会引用错
3. **伦理误区** — 研究机构对 Sci-Hub 使用有明确规定，忽略会惹麻烦
4. **作者邮件群发** — 不要无脑群发；每封邮件应有针对性

## AI 边界

- **能做：** 列出获取策略、生成索文邮件模板、解析 DOI 找 OA 版本
- **不能做：** 代替你访问订阅库（账号限制）、判断某源是否合规（因国家/机构而异）

## 何时读 references/

| 需求 | 读哪个 |
|------|-------|
| Open Access 体系与工具 | `references/oa-landscape.md` |
| 中国本地化获取渠道 | `references/china-access.md` |
| Sci-Hub 等灰色渠道的学术讨论 | `references/ethics-discussion.md` |

## 何时用 assets/

| 需求 | 用哪个 |
|------|-------|
| 给作者发索文邮件 | `assets/email-templates.md` |

## 下游

论文拿到 → `文献精读`（开始读）
