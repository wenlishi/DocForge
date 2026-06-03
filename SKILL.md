---
name: DocForge
description: |
  把你的文档、Markdown、笔记、经验总结，输出为排版精美的 PDF。支持多主题、封面、目录、书签树、页码。
  
  触发场景：
  - 用户想要生成 PDF 文档、资料、手册、总结、报告
  - 用户说「生成PDF」「做一份文档」「整理成资料」「知识分享」「创建文档」「导出PDF」
  - 用户想要把笔记/总结/经验分享输出为正式排版的可打印/可分享 PDF
  - 用户提到「模板」「主题」「封面」「目录」「书签」「页码」等文档排版相关词
  
  请积极触发此技能，只要用户提到生成正式文档相关需求就应该使用。
---

## 技能概述

将用户提供的内容（Markdown 笔记、技术总结、经验分享等）生成一份排版精美的 PDF 文档，包含：

1. **封面** — 专业的封面页，含标题、副标题、作者、日期
2. **目录** — 带页码的结构化目录，**可点击跳转**
3. **正文** — 带章节层级（h1/h2/h3）、代码块、表格、引用、列表
4. **页码** — 目录用罗马数字（i, ii…），正文用阿拉伯数字
5. **书签树** — PDF 左侧导航栏，h1/h2 自动分层，点击跳转章节

## 项目结构

```
DocForge/
├── build.sh                # 一键构建（核心入口）
│   ├── add_toc_links.py    # 步骤1: 添加锚点（可点击目录）
│   ├── highlight.py        # 步骤2(可选): 代码语法高亮
│   ├── html2pdf.sh         # 步骤3: Chrome headless → PDF
│   ├── add_page_numbers.py # 步骤4: 注入页码（PyMuPDF）
│   └── add_outline.py      # 步骤5: 书签树（PyMuPDF）
├── themes/
│   ├── minimalist.css      # 简约清新
│   ├── notebook.css        # 暖色笔记
│   └── professional.css    # 商务正式
├── templates/template.html
└── samples/                # 示例文件
```

## 可用主题

| 主题 | 文件名 | 风格 | 适用场景 |
|------|--------|------|----------|
| **简约清新** | `minimalist.css` | 白底绿调，大量留白 | 知识笔记、阅读摘要、教程 |
| **暖色笔记** | `notebook.css` | 白底棕色字，暖金装饰 | 个人随笔、读书笔记、经验分享 |
| **商务正式** | `professional.css` | 深蓝+金色，稳重 | 技术文档、工作总结、正式报告 |

三个主题均 15 页（示例内容），页码逻辑一致。

## 工作流程

### Step 1：了解需求

确认以下信息：

**封面必填 4 字段：**
- **主标题**（必填）
- **副标题**（必填）
- **作者**（必填，默认：泡泡吐puber）
- **日期**（必填，如 "2026 年 6 月"）

**其他：**
- **内容** — 粘贴文字、上传 .md 文件、或口述由你整理
- **主题** — 用户没指定时展示三个主题让其选择

### Step 2：编写 HTML

根据用户主题，生成完整的 HTML 文件。

**HTML 三段式结构：**
```html
<!-- 封面 -->
<section class="cover-page">
  <h1 class="cover-title">标题</h1>
  <div class="cover-divider"></div>
  <p class="cover-subtitle">副标题</p>
  <div class="cover-meta">
    <p>作者</p>
    <p class="date">2026 年 6 月</p>
  </div>
</section>

<!-- 目录（页码硬编码，需与正文对齐） -->
<section class="toc-page">
  <h2 class="toc-title">目&emsp;录</h2>
  <ul class="toc-list">
    <li class="toc-item toc-item-h1">
      <span>前言</span>
      <span class="toc-dots"></span>
      <span class="toc-page-num">1</span>
    </li>
    <!-- h2 条目: toc-item-h2 -->
  </ul>
</section>

<!-- 正文 -->
<section class="body-content">
  <h1>一、章节</h1>
  <p>...</p>
  <h2>1.1 小节</h2>
</section>
```

**关键规则：**
- `h1` = 章标题，每个 `h1` 自动分页（`page-break-before: always`）
- `h2` = 节标题，与 `h1` 同页
- 目录页页码：封面后第 1 页=TOC 第 1 页=i，第 2 页=ii
- 正文页码：TOC 后第 1 页=1，第 2 页=2…（由脚本自动生成，HTML 中不用写）
- **TOC 中的页码是硬编码的**，需人工与正文对齐。写法为 `1`、`2`… 阿拉伯数字（不含罗马数字）

**目录页码估算方法：**
每个 h1 分页，看内容长度估算每个章节占几页。三个主题排版密度不同（商务正式最松，简约最紧），以预览效果为准，必要时调整。

### Step 3：一键构建

```bash
bash build.sh <HTML路径> [输出PDF路径] [目录页数]
```

参数：
- 第 1 参：HTML 文件路径
- 第 2 参（可选）：输出 PDF 路径，默认同 HTML 文件名
- 第 3 参（可选）：目录占几页，默认 2

示例：
```bash
# 最简单用法
bash build.sh 我的文档.html

# 指定输出路径和目录页数
bash build.sh 我的文档.html 输出.pdf 2
```

build.sh 自动执行全部 5 步：
1. `add_toc_links.py` — 给 h1/h2 加 id 锚点，TOC 条目变链接
2. `highlight.py` — 代码语法高亮（按需使用，可跳过）
3. `html2pdf.sh` — Chrome headless 打印 PDF
4. `add_page_numbers.py` — 注入页码（罗马+阿拉伯）
5. `add_outline.py` — 生成书签树

### Step 4：告知用户

生成完成后告知文件路径。PDF 包含：
- 可点击的目录（点条目跳转章节）
- 左侧导航书签树（h1/h2 层级）
- 页码（目录罗马数字，正文阿拉伯数字）

## 页码机制

页码通过 `add_page_numbers.py` 后处理注入（非 CSS），因为 `--no-header-footer` 会抑制 CSS @page。

**逻辑：**
- 封面（PDF 第 1 页）→ 无页码
- 目录页（第 2~N 页）→ 小写罗马数字 i, ii, iii...
- 正文（第 N+1 页起）→ 阿拉伯数字 1, 2, 3...

**颜色自动匹配：** 根据文件名关键词匹配页码颜色：
- 含 "暖色"/"notebook" → 暖金色
- 含 "简约"/"minimalist" → 绿色
- 含 "商务"/"professional" → 灰蓝色

## 内容编写指南

### Markdown → HTML 映射

| Markdown | HTML | 说明 |
|----------|------|------|
| `# 标题` | `<h1>` | 大章节，自动分页 |
| `## 标题` | `<h2>` | 小节 |
| `### 标题` | `<h3>` | 子节 |
| `> 引用` | `<blockquote>` | 引用块 |
| `` `代码` `` | `<code>` | 行内代码 |
| ```` ``` ```` | `<pre><code>` | 代码块 |
| `- 列表` | `<ul><li>` | 无序列表 |
| `1. 列表` | `<ol><li>` | 有序列表 |
| `\| 表格 \|` | `<table>` | 表格 |
| `![图](url)` | `<img>` | 图片 |
| `---` | `<hr>` | 分隔线 |
| `**粗**` | `<strong>` | 加粗 |
| `*斜*` | `<em>` | 斜体 |

### 中文排版注意
- `&emsp;` = 中文空格（如 `目&emsp;录`）
- 正文段落默认首行缩进 2 字符（CSS 控制）
- 商务+暖色主题有首字下沉效果
- CSS 已包含中文字体回退链

## 主题 CSS 文件

```
themes/
├── professional.css
├── minimalist.css
└── notebook.css
```

引用时使用相对路径，建议把 HTML 放在项目内，引用如 `themes/minimalist.css`。

## 踩坑备忘录（重要！）

1. **CSS 页码不显示** — `--no-header-footer` 会抑制所有 @page margin boxes，必须用 PyMuPDF 后处理
2. **@page margin: 0 导致页码超出** — PyMuPDF 用 `page.rect.height - 35` 定位
3. **中文文件名匹配** — 颜色字典同时配英文和中文关键词
4. **TOC 页码是硬编码的** — 内容变化后需要手动更新
5. **不同主题页数可能不同** — 商务正式字体间距大，可能多 1 页，需调目录间距或页码对齐
