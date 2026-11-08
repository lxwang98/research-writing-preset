---
name: lit-review-section-zh
description: 写论文 / 学位论文中的"文献综述章节"（区别于独立的综述型论文）。重点：synthesis 而非堆砌，承上启下建立 gap，主题组织而非作者组织。
---

# 文献综述章节（Literature Review Chapter）

> 📚 基于 Ridley (2012) *The Literature Review*、Machi & McEvoy (2022) *Six Steps to Success*、Hart (2018) *Doing a Literature Review*、Webster & Watson (2002) MIS Quarterly、Torraco (2016) *Human Resource Development Review*
> ⚠️ 与「文献综述写作」skill（写综述型论文）不同，本 skill 专指论文中的 Lit Review **章节**。

---

## 何时使用

- 学位论文的 Chapter 2 文献综述
- 期刊论文的 Related Work / Literature Review 章
- 论文引言太长需要拆出独立综述章
- 综述章被批「堆砌无综合」要重写

---

## 核心原则

1. **Lit Review 章 ≠ 综述型论文**。章节服务于本研究的 argument；综述型论文本身即 argument。
2. **Synthesis 而非堆砌**：不是 "A 说 X，B 说 Y，C 说 Z"，而是 "关于问题 P，已有研究可分为 X 派（A,B）和 Y 派（C），二者在 Z 上分歧..."
3. **主题组织 > 作者组织**：按议题分节，而非按作者。
4. **批判性阅读**：指出已有研究的局限，为本研究 gap 铺路。
5. **闭环**：章结尾必须明确 gap + 本研究如何填。

---

## Lit Review 章与其他相关章节的区别

| 章 | 作用 | 位置 | 长度 |
|---|------|------|------|
| **Introduction** | 建立领域 + 引出 gap（CARS） | 首章 | 10-15% |
| **Related Work / Lit Review** | 系统梳理已有研究，细化 gap | 紧邻 Intro | 10-20% |
| **Theoretical Framework** | 选定理论 / 视角 | Lit Review 后或嵌入 | 5-10% |
| **Discussion** | 把本研究发现放回文献 | 结尾 | 18-22% |

**注：** 短期刊论文常无独立 Lit Review 章（融入 Intro）。长期刊 / 综述刊 / 学位论文必有。

---

## 写综述章的 6 步法

### Step 1: 定综述范围

- **时间范围**：近 5 年 / 10 年 / 经典至今？
- **语言范围**：英文 / 中文 / 双语？
- **学科范围**：单学科 / 跨学科？
- **质量范围**：顶刊 / SCI/SSCI / 全部？

### Step 2: 定组织方式（关键）

**推荐 4 种：**

| 组织方式 | 适用 | 示例 |
|---------|------|------|
| **主题式** | 议题明确 | 主题 1 / 主题 2 / 主题 3 |
| **时间线式** | 历史演进 | 1990s / 2000s / 2010s / 2020s |
| **方法式** | 方法多样 | 实验 / 调查 / 质性 / 建模 |
| **视角式** | 学科争议 | 心理学视角 / 社会学视角 / 经济视角 |

**混合式：** 顶层按主题，主题内按时间或方法。

❌ **禁用：** 按作者一篇篇综述（"Smith 2020 说...; Jones 2021 说..."）

### Step 3: 建综述矩阵（synthesis matrix）

用 `assets/synthesis-matrix.md`：

| 主题 → | 研究 1 | 研究 2 | 研究 3 | ... |
|-------|-------|--------|--------|-----|
| 方法 | | | | |
| 样本 | | | | |
| 发现 | | | | |
| 理论 | | | | |
| 局限 | | | | |

横向看行 = 某主题下各研究对比 → 写 synthesis 段落。
纵向看列 = 单个研究全貌 → 写单篇总结句。

### Step 4: 写段落（每段一 synthesis）

**综述段标准结构：**

1. **主题句**：段落 synthesis 要点
2. **证据**：引 3-5 篇支持
3. **对比 / 冲突**：指出研究间分歧
4. **批判**：指出局限
5. **过渡**：引下段或 gap

**示例：**

> "Research on X's effect on Y has produced mixed findings. Early
> studies (Smith 2015; Jones 2016) reported a positive effect, arguing
> that [机制]. More recent work, however, has questioned this
> conclusion: both Chen (2020) and Wu (2022), using larger samples and
> longitudinal designs, found no significant effect or even a reverse
> pattern. The inconsistency may stem from [解释]—an issue we return
> to in our analysis (§4)."

### Step 5: 建立 gap

**章节结尾必须有 gap 段，内容包括：**
- 前文综述的核心主题回顾（2-3 句）
- 具体 gap（经验 / 方法 / 理论 / 应用 / 争议）
- 本研究如何填 gap（1-2 句，过渡到下章）

### Step 6: 控字数与引用

| 元素 | 典型值 |
|------|--------|
| 章节字数（期刊） | 800-1500 |
| 章节字数（学位） | 8000-15000 |
| 引用数（期刊） | 20-40 |
| 引用数（学位） | 80-150 |
| 单段字数 | 150-250 |
| 单段引用 | 3-7 |

---

## 综述章 vs Related Work（计算机）

计算机顶会的 Related Work 比 Lit Review 更紧凑：

**典型计算机 RW 结构：**

```
2. Related Work
2.1 [类别 1: 前辈方法]
   - 2-3 段，每段一族方法，引 3-5 篇
   - 指出局限
2.2 [类别 2: 相邻问题]
   - 与本研究问题的区别
2.3 [类别 3: 本研究最接近的工作]
   - 1-2 段，精确对比
```

关键：**"We differ from X by... We are the first to..."**。

---

## 常见错误

| 错误 | 症状 | 修复 |
|------|------|------|
| **作者接龙** | "X 做了... Y 做了... Z 做了..." | 改主题组织 |
| **无批判** | 只总结不评价 | 每段加局限 |
| **无 gap** | 综述完就停 | 加 gap 段 |
| **引用过时** | 近 3 年文献 < 20% | 补近期研究 |
| **引用碎片** | 一个 paragraph 30+ 引用 | 合并同类，减到 5-7 |
| **Quote 堆砌** | 直接引原文占 40%+ | 改 paraphrase + synthesis |
| **与 Intro 重复** | Lit Review 重讲 Intro 内容 | 拆分：Intro 概述 / LR 深入 |

---

## 批判性阅读维度

每篇文献至少问 5 个问题：

1. **方法局限：** 样本、测量、设计有何问题？
2. **理论局限：** 理论框架是否适用？
3. **样本局限：** 泛化到本研究对象吗？
4. **时代局限：** 过时了吗？
5. **一致性：** 与其他研究一致吗？

---

## 综述的"声音"（voice）

要让读者听见**你**的判断，不只是他人：

❌ "Smith (2020) argued that... Jones (2021) argued that..."

✅ "While both Smith (2020) and Jones (2021) argue that X, they differ in **how they operationalize** Y. **This distinction matters** because..."

**关键词：** however, whereas, in contrast, building on, in line with, challenge, extend, complicate

---

## 资源

- **references/organization-modes.md** — 4 种综述组织方式详解
- **references/synthesis-vs-summary.md** — synthesis vs summary 识别与改写
- **assets/synthesis-matrix.md** — 综述矩阵填空
- **assets/review-paragraph-template.md** — 综述段落模板

---

## Anti-pattern

❌ "Chronological dump"（按时间堆砌）
❌ "Author-by-author sweep"（一个一个作者讲）
❌ "No gap"（综述完不说干什么）
❌ "He said she said"（只报告不综合）

✅ **主题组织 + synthesis 写法 + 批判立场 + 明确 gap**
