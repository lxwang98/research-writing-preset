# 4 种综述组织方式详解

> **核心 Source:**
> - Ridley, D. (2012). *The Literature Review: A Step-by-Step Guide for Students* (2nd ed.). SAGE.
> - Machi, L. A., & McEvoy, B. T. (2022). *The Literature Review: Six Steps to Success* (4th ed.). Corwin.
> - Galvan & Galvan (2017). *Writing Literature Reviews* (7th ed.). Routledge.

---

## 选择决策树

```
你的 research question 涉及...
  ├── 明确的议题 / 概念 → 主题式
  ├── 理论演进 / 历史 → 时间线式
  ├── 方法论对比 → 方法式
  └── 学科争议 / 多视角 → 视角式
```

多数实证研究用**主题式**。学位论文常**混合**。

---

## 方式 A: 主题式（Thematic / Conceptual）

**核心：** 按议题 / 子主题分节。

### 结构示例

**研究问题：** AI 对教育的影响

```
2.1 AI 提升学习效率的证据
    2.1.1 认知层面（元认知、记忆）
    2.1.2 动机层面（参与度、自主性）
2.2 AI 加剧教育不平等的证据
    2.2.1 访问鸿沟
    2.2.2 使用鸿沟
2.3 AI 改变师生关系
    2.3.1 教师角色
    2.3.2 学习评估
2.4 研究 gap
```

**优点：** 清晰、易读、易 synthesis
**缺点：** 议题交叉时需要处理

---

## 方式 B: 时间线式（Chronological）

**核心：** 按历史演进。

### 结构示例

**研究问题：** 大语言模型的发展

```
2.1 早期统计语言模型（1990s-2005）
2.2 神经网络语言模型（2005-2017）
2.3 Transformer 时代（2017-2019）
2.4 大规模预训练（2019-2022）
2.5 RLHF + Instruction Tuning（2022-至今）
2.6 研究 gap
```

**优点：** 历史脉络清晰
**缺点：** 易变成流水账，需在每期总结**变化的原因**

---

## 方式 C: 方法式（Methodological）

**核心：** 按研究方法分类。

### 结构示例

**研究问题：** 师生互动对学习效果的影响

```
2.1 实验研究（含 RCT）
2.2 准实验 / 纵向调查
2.3 质性研究（访谈 / 观察）
2.4 大数据 / 计算方法
2.5 元分析
2.6 方法 gap：混合方法的缺失
```

**优点：** 展示方法多样性 + 可发现方法 gap
**缺点：** 弱化议题本身的 synthesis

---

## 方式 D: 视角式（Perspective / Disciplinary）

**核心：** 按学科 / 理论流派分类。

### 结构示例

**研究问题：** 社交媒体与心理健康

```
2.1 心理学视角（认知、情绪调节）
2.2 社会学视角（身份建构、社会资本）
2.3 传播学视角（媒介效应理论）
2.4 公共卫生视角（流行病学数据）
2.5 跨视角 synthesis 与 gap
```

**优点：** 适合跨学科研究
**缺点：** 需要在结尾做跨视角综合

---

## 混合式（推荐给学位论文）

### 示例：博士论文 Ch2

```
2.1 概念界定与理论基础（概念式）
2.2 [主题 A] 研究（主题式）
  2.2.1 早期研究（1990-2010）
  2.2.2 近期研究（2010-至今）
2.3 [主题 B] 研究（主题式）
  2.3.1 实验方法
  2.3.2 质性方法
2.4 跨主题 synthesis
2.5 研究 gap 与本研究定位
```

---

## 组织方式的视觉化

### 矩阵图（适合综述章开头）

```
                时期 1    时期 2    时期 3
主题 A           [研究]    [研究]    [研究]
主题 B           [研究]    -         [研究]
主题 C           -         [研究]    [研究]
```

### 概念图（主题间关系）

```
     [主题 A] ←相关→ [主题 B]
         ↓                ↓
     [主题 C] ←对立→ [主题 D]
         ↘            ↙
          [本研究 RQ]
```

用 Mermaid / Excalidraw / 手画，放在综述章开头给读者路线图。

---

## 段落 → 小节 → 章的层级设计

```
Chapter: 综述全貌（1-2 段引 + 全章 synthesis 段）
  Section: 某主题（1 段引 + N 段展开 + 小节结论）
    Subsection: 子议题（3-5 段）
      Paragraph: 单一 synthesis 点（3-7 引用）
```

**每段只讲一个 synthesis 点。** 多于一个 → 拆段。

---

## 从矩阵到段落的转换

填完综述矩阵后，按**横向**读：

**矩阵（假设）：**

| 议题 "X 对 Y 的效应" | Smith (2015) | Jones (2018) | Chen (2022) |
|----------------------|-------------|-------------|-------------|
| 效应方向 | 正向 | 正向 | 无显著 |
| 样本 | N=120 | N=500 | N=2000 |
| 方法 | 实验 | 横断调查 | 纵向 |
| 理论 | A 理论 | A 理论 | B 理论 |

**段落 synthesis：**

> "Early research suggested a positive effect of X on Y (Smith 2015;
> Jones 2018), anchored in A-theory. However, Chen's (2022) longitudinal
> study with a larger sample (N=2000) found no significant effect, and
> introduced B-theory as an alternative framework. The inconsistency
> points to **methodological heterogeneity**: smaller, cross-sectional
> designs may overestimate the effect. Our study addresses this by
> using [本研究方法] to re-examine the question with [改进]."

---

## 审校时问的 5 个问题

1. 每节有明确主题句？
2. 每段有 synthesis（非堆砌）？
3. 组织方式一致（不中途换）？
4. 有批判立场（指出局限）？
5. 章末有 gap + 过渡到下章？
