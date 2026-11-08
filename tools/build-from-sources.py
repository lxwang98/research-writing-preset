#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""构建 DSH「科研写作模式」preset bundle。

源：<SRC>/<owner>__<repo>/...（git clone 的第三方学术技能库）
    默认取环境变量 RESEARCH_SKILLS_SRC，否则 ../_sources（相对本 bundle），
    再否则 D:\\dsh-bundles\\_research\\src。
产物：本 bundle 根目录（脚本所在的上一级）下的 presets/research-writing/skills/
反复运行是幂等的：每次都重建 skills/ 与 SOURCES.md。
"""
from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

import yaml

OUT = Path(__file__).resolve().parent.parent
_CANDIDATES = [
    Path(os.environ["RESEARCH_SKILLS_SRC"]) if os.environ.get("RESEARCH_SKILLS_SRC") else None,
    OUT.parent / "_sources",
    Path(r"D:\dsh-bundles\_research\src"),
]
SRC = next((p for p in _CANDIDATES if p and p.is_dir()), _CANDIDATES[1])
PRESET_ID = "research-writing"
SKILLS_DIR = OUT / "presets" / PRESET_ID / "skills"

# (源目录相对 SRC, 目标 skill 名, 中文一句话, 上游 repo)
# repo 用于 SOURCES.md 与 LICENSE 收集
M = [
    # ── 英文期刊写作：全流程 ────────────────────────────────────────────────
    (r"Imbad0202__academic-research-skills\academic-paper", "academic-paper",
     "12-agent 学术论文写作流水线：11 种模式（全文/大纲/修订/摘要/文献综述/引用核查/回复审稿人）、6 类论文、5 种引用格式、双语摘要、LaTeX/DOCX/PDF 输出", "Imbad0202/academic-research-skills"),
    (r"Imbad0202__academic-research-skills\academic-pipeline", "academic-pipeline",
     "从选题到定稿的端到端论文流水线编排（研究→写作→审稿→修订→定稿）", "Imbad0202/academic-research-skills"),
    (r"Imbad0202__academic-research-skills\deep-research", "deep-research",
     "深度调研：把研究问题拆成可检索的子问题，多轮检索并综合成带出处的调研报告", "Imbad0202/academic-research-skills"),
    (r"Imbad0202__academic-research-skills\academic-paper-reviewer", "paper-review-pipeline",
     "模拟期刊审稿：多角色评审意见、评分表与修改清单", "Imbad0202/academic-research-skills"),
    (r"Imbad0202__academic-research-skills\sr-screener", "systematic-review-screener",
     "系统综述筛查：PRISMA 流程下的标题/摘要与全文纳排筛选", "Imbad0202/academic-research-skills"),
    (r"WenyuChiou__academic-writing-skills\skills\academic-writing-skills", "academic-writing",
     "英文期刊写作分节训练（摘要/引言/方法/结果/讨论）＋语言润色＋期刊适配，带 evals", "WenyuChiou/academic-writing-skills"),
    (r"WenyuChiou__academic-writing-skills\skills\academic-writing-skills-zh-cn", "academic-writing-zh",
     "同上技能的中文版（中文讲解英文写作规范，适合中文母语作者）", "WenyuChiou/academic-writing-skills"),
    (r"wubing2023__paperspine\dist\claude\skills\paper-spine", "paper-spine",
     "PaperSpine 双语 10-skill 套件：论文骨架搭建、章节扩写、图表与叙事线", "wubing2023/paperspine"),
    (r"Master-cai__Research-Paper-Writing-Skills\research-paper-writing", "research-paper-writing",
     "科研论文写作方法论笔记（选题、贡献陈述、写作顺序、常见退稿原因）", "Master-cai/Research-Paper-Writing-Skills"),
    (r"yzy1996__english-writing\skills\academic-paper-polish", "paper-polish-sentence-bank",
     "英文学术写作分节句式库与润色替换表", "yzy1996/english-writing"),
    (r"wantongc__journal-adapt-writing-skill\skill", "journal-adapt-writing",
     "按目标期刊的已发表语料适配行文风格、篇幅与结构", "wantongc/journal-adapt-writing-skill"),
    (r"yunshenwuchuxun__latex-paper-skills\skills\latex-paper-skills", "latex-paper-skills",
     "LaTeX 论文从零到编译：选题、模板、图表、参考文献编译验证", "yunshenwuchuxun/latex-paper-skills"),
    # ── nature-paper-skills：细粒度期刊写作/审稿技能 ─────────────────────────
    (r"boom5426__nature-paper-skills\skills\core\paper-workflow", "nature-paper-workflow",
     "Nature 系论文工作流总调度：从故事线到投稿的阶段划分与检查点", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\core\scientific-writing", "nature-scientific-writing",
     "顶刊科学写作规范：叙事结构、段落功能、时态与措辞", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\core\scientific-prose-style", "nature-prose-style",
     "科学文风打磨：去冗余、去防御性写作、提高信息密度", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\core\write-scientific-manuscript", "write-scientific-manuscript",
     "按章节撰写手稿的骨架与自查清单", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\core\manuscript-optimizer", "manuscript-optimizer",
     "手稿整体优化：逻辑链、贡献凸显、可读性", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\core\results-section-revision", "results-section-revision",
     "结果部分改写：数据陈述与图表的对应关系", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\core\review-article-architecture", "review-article-architecture",
     "综述文章架构：分类框架、对比矩阵、研究缺口", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\core\anti-defensive-writing", "anti-defensive-writing",
     "反防御性写作：删掉过度限定与自我削弱表述", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\core\draft-marker-discipline", "draft-marker-discipline",
     "草稿标记纪律：TODO/待核实/待补数据的显式标记与清理", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\core\paper-bootstrap", "paper-bootstrap",
     "从零起稿：确定卖点、贡献列表与章节骨架", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\core\submission-audit", "submission-audit",
     "投稿前审计：清单化检查格式、声明、附件与元数据", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\core\rebuttal-response", "rebuttal-response",
     "审稿意见回复信：逐条回应、措辞与证据组织", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\core\stats-reporting-audit", "stats-reporting-audit",
     "统计报告审计：效应量、置信区间、多重比较与报告规范", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\core\figure-planner", "figure-planner",
     "图表规划：每张图承担的论证任务与面板编排", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\figure\nature-figure", "nature-figure",
     "Nature 级配图规范：尺寸、字号、配色、矢量导出", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\figure\figure-style", "figure-style",
     "期刊图表风格统一：线宽、刻度、图例、色盲友好", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\venue\nature-portfolio-playbook", "nature-portfolio-playbook",
     "Nature 系期刊投稿策略：选刊、scope 匹配、常见 desk-reject 原因", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\optional\conference-paper-writing", "conference-paper-writing",
     "会议论文写作：篇幅约束下的贡献表达与排版", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\optional\academic-presentations", "academic-presentations",
     "学术汇报/答辩 PPT：叙事线、图表复用与讲述节奏", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\core\citation-verifier", "citation-verifier",
     "引用核验：DOI/PMID 完整性、BibTeX 一致性、占位引用与重复条目", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\core\claim-source-verification", "claim-source-verification",
     "主张—证据对照：每条断言都能落到具体文献与页码", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\core\data-availability", "data-availability",
     "数据可用性声明与仓库/附录准备", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\research\academic-researcher", "academic-researcher",
     "研究者视角的研究设计：问题、假设、可行性与贡献", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\research\paper-analyzer", "paper-analyzer-nature", "论文结构化拆解：问题/方法/证据/局限", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\research\results-analysis", "results-analysis",
     "结果分析：从数据到可写进论文的结论链", "boom5426/nature-paper-skills"),
    (r"boom5426__nature-paper-skills\skills\review\paper-reviewer", "paper-reviewer-nature",
     "Nature 风格审稿意见撰写", "boom5426/nature-paper-skills"),
    # ── 文献检索 ────────────────────────────────────────────────────────────
    (r"lottshin__scholar-kit", "scholar-kit",
     "中文优先的多源文献检索与引用导出：CNKI/OpenAlex/Semantic Scholar/arXiv/NSSD/DBLP/BASE，Crossref 补全、Unpaywall 找 OA 全文，导出 GB/T 7714 / APA / MLA / Chicago / BibTeX / RIS", "lottshin/scholar-kit"),
    (r"PlutoLei__multi-source-paper-search", "multi-source-paper-search",
     "四源并行检索 + 并查集去重 + 共识排序，降低单一数据库漏检", "PlutoLei/multi-source-paper-search"),
    (r"O0000-code__paper-search-pro", "paper-search-pro",
     "OpenAlex 五源检索与饱和曲线策略，附带检索报告生成", "O0000-code/paper-search-pro"),
    (r"zhongzhx__literature-harvest", "literature-harvest",
     "批量抓取文献元数据与 PDF 全文，落盘成可复用文献库", "zhongzhx/literature-harvest"),
    (r"ultimatile__arxiv-skills\skills\arxiv-lookup", "arxiv-lookup",
     "arXiv 精确检索与条目解析", "ultimatile/arxiv-skills"),
    (r"YANZHANLIN__literature-review-skill\skills\文献检索", "lit-search-strategy-zh",
     "中文文献检索策略构建：PICO/SPIDER 框架、数据库选择、可复现检索日志（PRISMA-S）", "YANZHANLIN/literature-review-skill"),
    (r"YANZHANLIN__literature-review-skill\skills\文献获取", "lit-fulltext-fetch-zh",
     "中文文献全文获取：合法渠道、馆际互借、OA 与预印本", "YANZHANLIN/literature-review-skill"),
    (r"K-Dense-AI__claude-scientific-skills\skills\paper-lookup", "paper-lookup",
     "按 DOI/PMID/标题精确查论文并核对元数据", "K-Dense-AI/claude-scientific-skills"),
    (r"K-Dense-AI__claude-scientific-skills\skills\research-lookup", "research-lookup",
     "面向研究问题的多源资料检索与证据汇总", "K-Dense-AI/claude-scientific-skills"),
    # ── 文献阅读与笔记 ───────────────────────────────────────────────────────
    (r"flyer-Li__paper-analyst", "paper-analyst",
     "论文五档深度解读，所有结论标注来源段落，反幻觉", "flyer-Li/paper-analyst"),
    (r"Kingslayer-bot__paper-reading-skill", "paper-reading-skill",
     "段级精读 + 20 维分析框架（问题、方法、实验、局限、可复用点）", "Kingslayer-bot/paper-reading-skill"),
    (r"917Dhj__DeepPaperNote\skills\deeppapernote", "deeppapernote",
     "论文精读结构化笔记：方法拆解、公式推导、可复现清单", "917Dhj/DeepPaperNote"),
    (r"YANZHANLIN__literature-review-skill\skills\文献精读", "lit-close-reading-zh",
     "中文文献精读法：三遍阅读、批判性提问、笔记模板", "YANZHANLIN/literature-review-skill"),
    (r"Nebutra__MinerU-Skill\skills\mineru", "mineru-pdf",
     "PDF/扫描件转 Markdown（公式、表格、版面保留），供后续精读与检索", "Nebutra/MinerU-Skill"),
    (r"zeya-labs__arxiv-paper-zh\arxiv-paper-zh", "arxiv-paper-zh",
     "arXiv 论文中文翻译，保留公式与图表编号", "zeya-labs/arxiv-paper-zh"),
    (r"huangkiki__dailypaper-skills\skills\paper-reader", "paper-reader",
     "单篇论文快速通读与要点卡片", "huangkiki/dailypaper-skills"),
    # ── 文献综述 ────────────────────────────────────────────────────────────
    (r"YANZHANLIN__literature-review-skill\skills\文献综述写作", "lit-review-writing-zh",
     "中文文献综述写作：主题聚类、脉络梳理、批判性综合与引用规范", "YANZHANLIN/literature-review-skill"),
    (r"YANZHANLIN__literature-review-skill\skills\文献综述章节", "lit-review-section-zh",
     "把综述写进学位论文的「文献综述」章节（含过渡与评述）", "YANZHANLIN/literature-review-skill"),
    (r"K-Dense-AI__claude-scientific-skills\skills\literature-review", "literature-review-synthesis",
     "英文文献综述综合：检索→筛选→证据表→叙事综合", "K-Dense-AI/claude-scientific-skills"),
    # ── 中文毕业论文 ────────────────────────────────────────────────────────
    (r"ZyhSechub__chinese-thesis-workbench-skill", "chinese-thesis-workbench",
     "中文本科毕业论文/毕业设计全流程工作台：学校模板、任务书、开题、正文、图表登记、AIGC 降重、Word 交付", "ZyhSechub/chinese-thesis-workbench-skill"),
    (r"ganzhi-black__humanities-thesis-skill", "humanities-thesis",
     "中文人文社科论文写作：论证结构、材料使用、注释体例，强调不编造文献", "ganzhi-black/humanities-thesis-skill"),
    (r"yanlin-cheng__skill-thesis-writer", "thesis-writer-zh",
     "中文本硕学位论文写作（工科/心理/教育/管理），强制 GB/T 7714-2015 参考文献", "yanlin-cheng/skill-thesis-writer"),
    (r"ChipsAhoyM__dissertation-polisher-zh", "dissertation-polisher-zh",
     "中文博士论文润色：学术语体、逻辑衔接、章节一致性", "ChipsAhoyM/dissertation-polisher-zh"),
    (r"houlaisan__deai-academic-zh", "deai-academic-zh",
     "中文学术文本去 AIGC 痕迹：三遍改写法，保持原意与事实零编造", "houlaisan/deai-academic-zh"),
    # ── 引用格式与文献真实性 ────────────────────────────────────────────────
    (r"Zechang-Xiong__chinese-reference-formatter-skill", "chinese-reference-formatter",
     "中文参考文献格式化：GB/T 7714-2015 全类型 + BibTeX 互转", "Zechang-Xiong/chinese-reference-formatter-skill"),
    (r"keemanxp__apa-referencing-skill", "apa-referencing",
     "APA 第 7 版参考文献与文内引用（28 种文献类型）", "keemanxp/apa-referencing-skill"),
    (r"MilkClouds__fetch-bib\skills\fetch-bib", "fetch-bib",
     "反幻觉 BibTeX：逐条人工确认后才写入 .bib", "MilkClouds/fetch-bib"),
    (r"njzjz__wenxian\skill", "wenxian",
     "DOI/PMID/arXiv 号一键转 BibTeX（CLI）", "njzjz/wenxian"),
    (r"K-Dense-AI__claude-scientific-skills\skills\citation-management", "citation-management",
     "OpenAlex/PubMed/Crossref 元数据抓取、引用校验与 BibTeX 生成", "K-Dense-AI/claude-scientific-skills"),
    (r"boom5426__nature-paper-skills\skills\optional\reference-audit-guide", "reference-audit-guide",
     "参考文献审计指南：逐条核验路径与常见错误", "boom5426/nature-paper-skills"),
    (r"K-Dense-AI__claude-scientific-skills\skills\venue-templates", "venue-templates",
     "主流期刊/会议模板与格式要求速查（LaTeX/Word）", "K-Dense-AI/claude-scientific-skills"),
    # ── 审稿、评估与投稿 ────────────────────────────────────────────────────
    (r"WenyuChiou__academic-writing-skills\skills\paper-review", "journal-paper-review",
     "英文期刊审稿：评审维度、意见措辞、给作者的修改建议", "WenyuChiou/academic-writing-skills"),
    (r"WenyuChiou__academic-writing-skills\skills\paper-review-zh-cn", "journal-paper-review-zh",
     "同上审稿技能的中文版", "WenyuChiou/academic-writing-skills"),
    (r"shaowen-ye__manuscript-review-skill", "manuscript-review",
     "六角色审稿（主编/方法/统计/领域/伦理/读者）+ 双语 docx 报告", "shaowen-ye/manuscript-review-skill"),
    (r"alexwortega__ai-peer-review-skill", "ai-peer-review",
     "AI 辅助同行评审：结构化评审表单与置信度标注", "alexwortega/ai-peer-review-skill"),
    (r"claesbackman__AI-research-feedback\Skills\review-paper", "review-paper",
     "学术评审意见生成（MIT，侧重可操作修改建议）", "claesbackman/AI-research-feedback"),
    (r"K-Dense-AI__claude-scientific-skills\skills\peer-review", "peer-review-kdense",
     "同行评审流程与评审意见模板", "K-Dense-AI/claude-scientific-skills"),
    (r"K-Dense-AI__claude-scientific-skills\skills\scholar-evaluation", "scholar-evaluation",
     "学者/论文影响力评估：指标含义与误用警告", "K-Dense-AI/claude-scientific-skills"),
    # ── 选题、假设与批判性思维 ──────────────────────────────────────────────
    (r"K-Dense-AI__claude-scientific-skills\skills\hypothesis-generation", "hypothesis-generation",
     "从文献缺口生成可检验假设与研究设计", "K-Dense-AI/claude-scientific-skills"),
    (r"K-Dense-AI__claude-scientific-skills\skills\scientific-critical-thinking", "scientific-critical-thinking",
     "科研批判性思维：证据等级、偏倚识别、因果 vs 相关", "K-Dense-AI/claude-scientific-skills"),
    (r"K-Dense-AI__claude-scientific-skills\skills\scientific-writing", "scientific-writing-kdense",
     "科学写作通用规范（IMRaD、清晰度、术语一致性）", "K-Dense-AI/claude-scientific-skills"),
    # ── 去 AI 味 ────────────────────────────────────────────────────────────
    (r"blader__humanizer", "humanizer",
     "英文去 AI 写作痕迹：句式节奏、具体化、删套话", "blader/humanizer"),
    (r"momo2young__humanize-academic-writing", "humanize-academic-writing",
     "学术文本去 AI 味（英文为主，含改写示例）", "momo2young/humanize-academic-writing"),
]

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".github", "dist", "build"}
KEEP_BIG_EXT = {".docx", ".doc", ".tex", ".cls", ".sty", ".bst", ".bib", ".csv", ".json", ".xlsx", ".xls", ".yaml", ".yml"}
MAX_BYTES = 2 * 1024 * 1024

BAD_NAME = re.compile(r"[^a-z0-9-]+")


def clean_name(n: str) -> str:
    n = n.strip().lower().replace("_", "-").replace(" ", "-")
    n = BAD_NAME.sub("-", n).strip("-")
    return n


def parse_front(text: str):
    if not text.startswith("---"):
        return {}, text
    m = re.match(r"^---\r?\n(.*?)\r?\n---[ \t]*\r?\n?", text, re.S)
    if not m:
        return {}, text
    raw = m.group(1)
    try:
        data = yaml.safe_load(raw) or {}
    except Exception:
        data = {}
        for line in raw.splitlines():
            if ":" in line and not line.startswith((" ", "\t")):
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()
    body = text[m.end():]
    return (data if isinstance(data, dict) else {}), body


def describe(data: dict, body: str, fallback: str) -> str:
    d = data.get("description")
    if isinstance(d, str) and d.strip():
        s = " ".join(d.split())
    else:
        s = ""
        for para in body.split("\n\n"):
            p = para.strip()
            if p and not p.startswith("#") and not p.startswith("---"):
                s = " ".join(p.split())
                break
        s = s or fallback
    if len(s) > 900:
        s = s[:897].rstrip() + "..."
    return s


def copy_tree(src: Path, dst: Path):
    skipped = []
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIRS]
        rel = Path(root).relative_to(src)
        (dst / rel).mkdir(parents=True, exist_ok=True)
        for f in files:
            sp = Path(root) / f
            if sp.name == "SKILL.md" and rel == Path("."):
                continue  # 由调用方写入规范化版本
            try:
                size = sp.stat().st_size
            except OSError:
                continue
            if size > MAX_BYTES and sp.suffix.lower() not in KEEP_BIG_EXT:
                skipped.append((str(sp), size))
                continue
            shutil.copy2(sp, dst / rel / f)
    return skipped


def main() -> int:
    if not SRC.is_dir():
        print(f"missing source root: {SRC}")
        return 2
    if SKILLS_DIR.exists():
        shutil.rmtree(SKILLS_DIR)
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    rows, problems, big_skips = [], [], []
    seen = {}
    for rel, dest, note, repo in M:
        src = SRC / rel
        name = clean_name(dest)
        if not (src / "SKILL.md").is_file():
            problems.append(f"MISSING SKILL.md: {rel}")
            continue
        if name in seen:
            problems.append(f"DUPLICATE name {name}: {rel} vs {seen[name]}")
            continue
        seen[name] = rel
        target = SKILLS_DIR / name
        target.mkdir(parents=True, exist_ok=True)
        text = (src / "SKILL.md").read_text(encoding="utf-8", errors="replace")
        data, body = parse_front(text)
        desc = describe(data, body, note)
        fm = {"name": name, "description": desc}
        lic = data.get("license")
        if isinstance(lic, str) and lic.strip():
            fm["license"] = lic.strip()
        head = "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000).strip() + "\n---\n\n"
        (target / "SKILL.md").write_text(head + body.lstrip("\n"), encoding="utf-8")
        big_skips += copy_tree(src, target)
        rows.append((name, repo, note, rel))

    # 本预设自带的入口技能（原创，放在 tools/skill-overview.md 下便于单独编辑）
    overview = Path(__file__).resolve().parent / "skill-overview.md"
    if overview.is_file():
        d = SKILLS_DIR / "research-writing-overview"
        d.mkdir(parents=True, exist_ok=True)
        shutil.copy2(overview, d / "SKILL.md")
        rows.insert(0, ("research-writing-overview", "(self)", "总览与路由：把科研全流程映射到本预设的具体技能，并给出反编造引用规则", "assets/skill-overview.md"))

    # 许可证与来源
    lic_dir = OUT / "presets" / PRESET_ID / "LICENSES"
    lic_dir.mkdir(parents=True, exist_ok=True)
    repos = sorted({r for _, r, _, _ in rows if r and not r.startswith("(")})
    lic_rows = []
    for repo in repos:
        d = SRC / repo.replace("/", "__")
        found = [p for p in d.glob("LICENSE*")] + [p for p in d.glob("LICENCE*")] + [p for p in d.glob("COPYING*")]
        if found:
            f = found[0]
            out = lic_dir / (repo.replace("/", "__") + f.suffix)
            shutil.copy2(f, out)
            first = " ".join(f.read_text(encoding="utf-8", errors="replace").split())[:120]
            lic_rows.append((repo, f.name, first))
        else:
            lic_rows.append((repo, "(no LICENSE file)", "上游未提供许可证文件，仅作本地个人研读使用"))

    src_md = ["# 技能来源与许可（SOURCES）", "",
              "本预设的技能全部来自 GitHub 开源仓库，原样收录（仅规范化 `SKILL.md` 的 YAML frontmatter、剔除超大示例资源）。",
              "许可原文见同目录 `LICENSES/`。使用前请遵守各仓库许可条款；`CC BY-NC 4.0` 等非商业许可仅限非商业用途。", "",
              "| 技能 | 上游仓库 | 许可 | 说明 |", "|---|---|---|---|"]
    lic_map = {r: (n, f) for r, n, f in lic_rows}
    for name, repo, note, _ in rows:
        if repo.startswith("("):
            src_md.append(f"| `{name}` | 本预设自带（原创） | — | {note} |")
        else:
            src_md.append(f"| `{name}` | https://github.com/{repo} | {lic_map[repo][1]} | {note} |")

    (OUT / "presets" / PRESET_ID / "SOURCES.md").write_text("\n".join(src_md) + "\n", encoding="utf-8")

    total = sum(f.stat().st_size for f in SKILLS_DIR.rglob("*") if f.is_file())
    print(f"skills: {len(rows)}  size: {total/1024/1024:.1f} MB")
    for p in problems:
        print("PROBLEM", p)
    if big_skips:
        print(f"skipped large files: {len(big_skips)}")
        for s, sz in big_skips[:10]:
            print(f"  {sz/1024:.0f}KB {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
