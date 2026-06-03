# DocForge

把你的文档、Markdown、笔记、经验总结，输出为排版精美的 PDF。三套主题、可点击目录、书签树、自动页码，中文排版开箱即用。

## 快速预览

三套内置主题，同一份内容，不同风格：

| 简约清新 | 暖色笔记 | 商务正式 |
|:---:|:---:|:---:|
| 白底绿调，轻量干净 | 白底棕字，纸质书感 | 深蓝金色，稳重专业 |

运行示例直接体验：

```bash
bash build.sh "samples/如何高效学习新技术.html" 输出.pdf
```

## 功能特性

- **三套主题** — 同一套 HTML 结构切换主题 CSS，无需改内容
- **可点击目录** — PDF 中点击目录条目跳转到对应章节
- **书签树** — 阅读器左侧导航栏，h1/h2 自动分层折叠
- **自动页码** — 目录用罗马数字（i, ii…），正文用阿拉伯数字（1, 2…），颜色随主题变化
- **封面页** — 标题、副标题、作者、日期
- **代码高亮** — 支持代码块语法着色（可选）
- **中文排版** — 首行缩进、首字下沉、中文字体栈

## 快速开始

### 安装依赖

```bash
pip install PyMuPDF
```

需要 Chrome 或 Edge（用于 HTML → PDF 渲染）。

### 编写文档

复制模板，按结构填写内容：

```bash
cp templates/template.html 我的文档.html
```

HTML 分三个区域：

```
┌─ 封面 ─────────────────────┐
│ 标题、副标题、作者、日期      │
├─ 目录 ─────────────────────┤
│ 章节目录（页码需手动填写）    │
├─ 正文 ─────────────────────┤
│ h1 = 章（自动分页）          │
│ h2 = 节                     │
│ p / ul / table / pre…       │
└─────────────────────────────┘
```

### 生成 PDF

```bash
bash build.sh 我的文档.html 我的文档.pdf
```

输出文件包含：封面 → 目录（罗马页码 i, ii） → 正文（阿拉伯页码 1, 2…），附带可点击目录和书签树。

## 使用指南

### build.sh 参数

```bash
bash build.sh <HTML文件> [输出PDF] [目录页数]
```

- `HTML文件` — 必填，源文件路径
- `输出PDF` — 可选，默认与 HTML 同名
- `目录页数` — 可选，默认 2（目录在 PDF 中占几页）

### 构建流程

```
你的文档 → [写 HTML] → [build.sh] → PDF
                                    
  build.sh 自动完成：
    1. 添加锚点链接（目录可点击）
    2. 代码语法高亮（可选）
    3. Chrome 渲染为 PDF
    4. 注入页码
    5. 生成书签树
```

### 切换主题

修改 HTML 中引用的 CSS 文件：

```html
<link rel="stylesheet" href="themes/minimalist.css">   <!-- 简约清新 -->
<link rel="stylesheet" href="themes/notebook.css">      <!-- 暖色笔记 -->
<link rel="stylesheet" href="themes/professional.css">   <!-- 商务正式 -->
```

### 手动分步执行

```bash
# 1. 添加目录锚点
python add_toc_links.py 我的文档.html

# 2. 生成 PDF
bash html2pdf.sh 我的文档.html 我的文档.pdf

# 3. 添加页码
python add_page_numbers.py 我的文档.pdf "" 2

# 4. 添加书签树
python add_outline.py 我的文档.html 我的文档.pdf 2
```

## 项目结构

```
DocForge/
├── build.sh               # 一键构建
├── html2pdf.sh / .bat     # Chrome → PDF
├── add_toc_links.py       # 可点击目录
├── add_page_numbers.py    # 页码注入
├── add_outline.py         # 书签树
├── highlight.py           # 代码高亮（可选）
├── themes/                # CSS 主题
├── templates/             # 内容模板
└── samples/               # 示例
```

## 依赖

- **Python 3.8+** + PyMuPDF
- **Chrome / Edge**（HTML 渲染为 PDF）

```bash
pip install PyMuPDF
```
