<#
.SYNOPSIS
    补齐因许可原因未随仓库分发的 7 个技能。

.DESCRIPTION
    本仓库只直接分发可以再分发的技能（MIT / Apache-2.0 / MulanPSL-2.0 / LGPL-3.0）。
    下面 7 个技能的上游许可为「CC BY-NC 4.0」或「未声明许可证」，直接入库有法律风险，
    因此改由本脚本在你自己机器上从上游仓库拉取。许可原文见 presets/research-writing/LICENSES/。

        Imbad0202/academic-research-skills  → 学术论文 / 流水线 / 深度调研 / 审稿 / 系统综述筛查（CC BY-NC 4.0）
        keemanxp/apa-referencing-skill      → APA 第 7 版引用（上游未声明许可证）
        yzy1996/english-writing             → 英文分节句式库（上游未声明许可证）

    需要：git 可用、能访问 github.com。

.PARAMETER SkillsDir
    技能目录。默认是本脚本所在仓库的 presets/research-writing/skills。

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\install-extra.ps1
#>
[CmdletBinding()]
param(
    [string]$SkillsDir
)

$ErrorActionPreference = 'Stop'
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $SkillsDir) {
    $SkillsDir = Join-Path $repoRoot 'presets\research-writing\skills'
}
$SkillsDir = [System.IO.Path]::GetFullPath($SkillsDir)

if (-not (Test-Path $SkillsDir)) {
    if ($PSBoundParameters.ContainsKey('SkillsDir')) {
        # 显式指定了目录，允许直接创建（方便装到自建技能目录）
        New-Item -ItemType Directory -Force -Path $SkillsDir | Out-Null
    }
    else {
        throw "技能目录不存在：$SkillsDir（先 clone 本仓库，或显式传 -SkillsDir）"
    }
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw '找不到 git，请先安装 Git for Windows：https://git-scm.com/download/win'
}

$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ('rw-extra-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

function Get-Upstream {
    param([string]$Slug)
    $dir = Join-Path $tmp ($Slug -replace '/', '__')
    Write-Host "  拉取 $Slug ..." -ForegroundColor DarkGray
    & git clone --depth 1 --quiet "https://github.com/$Slug.git" $dir 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "git clone 失败：$Slug（检查网络 / VPN）" }
    return $dir
}

function Set-SkillName {
    param([string]$Dir, [string]$Name)
    $file = Join-Path $Dir 'SKILL.md'
    if (-not (Test-Path $file)) { throw "$Dir 下没有 SKILL.md" }
    $text = [System.IO.File]::ReadAllText($file)
    $rx = New-Object System.Text.RegularExpressions.Regex '(?m)^name:\s*.*$'
    if ($rx.IsMatch($text)) {
        $text = $rx.Replace($text, "name: $Name", 1)
    } else {
        $text = "---`nname: $Name`n---`n" + $text
    }
    [System.IO.File]::WriteAllText($file, $text, $Utf8NoBom)
}

function Copy-Skill {
    param([string]$Source, [string]$Name)
    $dest = Join-Path $SkillsDir $Name
    if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
    Copy-Item -LiteralPath $Source -Destination $dest -Recurse -Force
    Get-ChildItem $dest -Recurse -Force -Directory |
        Where-Object { $_.Name -in @('.git', 'node_modules', '__pycache__', '.github') } |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Set-SkillName -Dir $dest -Name $Name
}

$results = New-Object System.Collections.Generic.List[object]

# 1) Imbad0202：5 个技能，上游是仓库顶层目录
try {
    $src = Get-Upstream 'Imbad0202/academic-research-skills'
    $map = [ordered]@{
        'academic-paper'          = 'academic-paper'
        'academic-pipeline'       = 'academic-pipeline'
        'deep-research'           = 'deep-research'
        'academic-paper-reviewer' = 'paper-review-pipeline'
        'sr-screener'             = 'systematic-review-screener'
    }
    foreach ($key in $map.Keys) {
        $to = $map[$key]
        try {
            $from = Join-Path $src $key
            if (-not (Test-Path $from)) { throw "上游缺少目录 $key" }
            Copy-Skill -Source $from -Name $to
            $results.Add([pscustomobject]@{ Skill = $to; Source = 'Imbad0202/academic-research-skills'; Status = 'ok' })
        } catch {
            $results.Add([pscustomobject]@{ Skill = $to; Source = 'Imbad0202/academic-research-skills'; Status = $_.Exception.Message })
        }
    }
} catch {
    $results.Add([pscustomobject]@{ Skill = '5 skills (Imbad0202)'; Source = 'Imbad0202/academic-research-skills'; Status = $_.Exception.Message })
}

# 2) keemanxp：APA-7，仓库根目录就是技能
try {
    $src = Get-Upstream 'keemanxp/apa-referencing-skill'
    Copy-Skill -Source $src -Name 'apa-referencing'
    $results.Add([pscustomobject]@{ Skill = 'apa-referencing'; Source = 'keemanxp/apa-referencing-skill'; Status = 'ok' })
} catch {
    $results.Add([pscustomobject]@{ Skill = 'apa-referencing'; Source = 'keemanxp/apa-referencing-skill'; Status = $_.Exception.Message })
}

# 3) yzy1996：只有分节词句表、没有 SKILL.md，这里补一个最小 frontmatter
try {
    $src = Get-Upstream 'yzy1996/english-writing'
    $dest = Join-Path $SkillsDir 'paper-polish-sentence-bank'
    if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
    New-Item -ItemType Directory -Force -Path (Join-Path $dest 'references') | Out-Null
    Get-ChildItem $src -File -Filter '*.md' | Copy-Item -Destination (Join-Path $dest 'references') -Force
    $skillMd = @'
---
name: paper-polish-sentence-bank
description: Polish and improve English writing for academic/research papers, especially in CS and ML fields. Use when the user asks to improve, revise, or polish academic English; wants sentence templates for paper sections (abstract, introduction, related work, method, experiment, conclusion, rebuttal); needs better academic vocabulary or phrasing for results and methods.
---

# Academic Paper Polish（分节句式库）

先判断用户要润色的段落属于论文哪一节（摘要 / 引言 / 相关工作 / 方法 / 实验 / 结论 / 回复审稿人），
再从 `references/` 下对应的词句表里挑改写方案，给 2–3 个可选版本并说明语气差别。

## 使用纪律

1. **只借句式，不借事实**：模板里的占位内容必须换成用户自己的数据与主张。
2. **不改原意**：润色不新增结论、不夸大结果、不删掉限定条件。
3. **给选择**：每个改写点给 2–3 个版本，标注语气差别（更克制 / 更强调贡献 / 更简洁）。
4. **术语一致**：沿用用户全文已有的术语与缩写，不擅自换词。
'@
    [System.IO.File]::WriteAllText((Join-Path $dest 'SKILL.md'), $skillMd, $Utf8NoBom)
    $results.Add([pscustomobject]@{ Skill = 'paper-polish-sentence-bank'; Source = 'yzy1996/english-writing'; Status = 'ok' })
} catch {
    $results.Add([pscustomobject]@{ Skill = 'paper-polish-sentence-bank'; Source = 'yzy1996/english-writing'; Status = $_.Exception.Message })
}

Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue

$ok = @($results | Where-Object { $_.Status -eq 'ok' }).Count
$fail = @($results | Where-Object { $_.Status -ne 'ok' }).Count

Write-Host ''
$results | Format-Table -AutoSize | Out-String -Width 200 | Write-Host
Write-Host ("技能目录：{0}" -f $SkillsDir) -ForegroundColor Cyan

if ($fail -eq 0) {
    Write-Host ("全部 {0} 个技能已就位。重启 DSH（或重新加载预设）后生效。" -f $ok) -ForegroundColor Green
} else {
    Write-Host ("成功 {0} 个，失败 {1} 个。失败多为网络问题，可重跑本脚本。" -f $ok, $fail) -ForegroundColor Yellow
    exit 1
}
