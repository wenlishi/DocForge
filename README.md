# DocForge

把你的文档、Markdown、笔记、经验总结，输出为排版精美的 PDF。支持多主题、封面、目录、书签树、页码，中文优化开箱即用。

同时也是一个 **Claude Code skill**，聊天中触发"生成 PDF""做文档""导出资料"等场景时自动调用。Skill 文件在：

```
C:\Users\Administrator\.claude\skills\DocForge\SKILL.md
```

---

## 整体架构

```
DocForge/
├── build.sh              # 一键构建脚本（核心入口）
├── html2pdf.sh / .bat    # Chrome headless 打印到 PDF
├── highlight.py          # 代码语法高亮
├── add_toc_links.py      # 添加锚点（可点击目录跳转）
├── add_page_numbers.py   # 后处理添加页码
├── add_outline.py        # 后处理添加 PDF 书签树
├── themes/
│   ├── minimalist.css    # 简约清新主题
│   ├── notebook.css      # 暖色笔记主题
│   └── professional.css  # 商务正式主题
├── templates/
│   └── template.html     # 内容模板
└── samples/
    ├── 如何高效学习新技术.html                  # 简约清新版
    ├── 如何高效学习新技术-暖色笔记.html         # 暖色笔记版
    ├── 如何高效学习新技术-商务正式.html         # 商务正式版
    └── *.pdf              # 生成的 PDF 文件
```

### 构建流程（4 步，不含可选高亮）

```
原始 HTML
    │
    ▼
[步骤1] add_toc_links.py ── 给正文 h1/h2 加 id 锚点，TOC 条目改为 <a> 链接
    │
    ▼
[步骤2 可选] highlight.py ── 代码块语法高亮（本例未使用，可跳过）
    │
    ▼
[步骤3] html2pdf.sh ──────── Chrome headless 打印到 PDF
    │
    ▼
[步骤4] add_page_numbers.py ── PyMuPDF 后处理，在底部注入页码
    │
    ▼
[步骤5] add_outline.py ─────── PyMuPDF 后处理，根据标题匹配生成书签树
    │
    ▼
   完成：PDF（含可点击目录、页码、书签树）
```

---

## 各组件详解

### 1. HTML 源文件结构

每个 HTML 文件包含三个 `<section>`：

```html
<!-- 封面 -->
<section class="cover-page">
  <h1 class="cover-title">标题</h1>
  <p class="cover-subtitle">副标题</p>
  <div class="cover-meta">
    <p>作者</p>
    <p class="date">日期</p>
  </div>
</section>

<!-- 目录 -->                                  ← page-break-after: always
<section class="toc-page">
  <h2 class="toc-title">目&emsp;录</h2>
  <ul class="toc-list">
    <li class="toc-item toc-item-h1">
      <span>章节名</span>
      <span class="toc-dots"></span>
      <span class="toc-page-num">1</span>
    </li>
  </ul>
</section>

<!-- 正文 -->                                  ← page-break-after 在每个 h1 上
<section class="body-content">
  <h1>一、章节</h1>
  <h2>1.1 小节</h2>
  ...
</section>
```

**关键规则：**
- `h1` = 章标题，每个 `h1` 自动分页（`page-break-before: always`）
- `h2` = 节标题，与 `h1` 同页
- TOC 页码需手工与正文对齐（或通过脚本批量更新）

### 2. CSS 主题系统

三个主题共用同一套 HTML 结构，仅通过 CSS 改变视觉效果。

| 主题 | 风格 | 配色 | 字体 | 装饰 |
|------|------|------|------|------|
| **简约清新** (minimalist) | 轻量、干净 | 绿色 `#48bb78` | Inter + Noto Sans SC | 圆形装饰、渐变条 |
| **暖色笔记** (notebook) | 纸质书感 | 暖金 `#c9b99a` + 棕色 | Noto Serif SC + ZCOOL XiaoWei | 双边框、首字下沉、❧ 装饰 |
| **商务正式** (professional) | 正式、沉稳 | 深蓝 `#1a365d` + 金色 | Noto Serif SC + Noto Sans SC | 深蓝顶部区块、首字下沉 |

**CSS 关键知识点：**
- `@page` 规则控制打印页边距、页眉页脚
- `page-break-before: always` / `page-break-after: avoid` 控制分页
- `string-set: chapter content()` + `@top-right { content: string(chapter) }` 实现动态页眉
- `@page:first` 单独设置封面页（无边距、无页眉）
- `@media print` 确保打印时保留颜色和背景

### 3. 构建脚本 (build.sh)

```bash
./build.sh <输入HTML> [输出PDF] [目录页数]
```

参数：
- 输入HTML：源文件路径
- 输出PDF：可选，默认同输入文件名
- 目录页数：可选，默认 2（目录在 PDF 中占多少页）

### 4. 页码系统 (add_page_numbers.py)

**实现方式：** 不用 CSS `@page` 的 margin boxes（因为 `--no-header-footer` 会抑制它们），而是用 PyMuPDF 在 PDF 生成后注入文字。

**逻辑：**
- 封面 → 无页码
- 目录页 → 小写罗马数字 i, ii, iii...
- 正文页 → 阿拉伯数字 1, 2, 3...

**主题色自动匹配：** 根据文件名关键词匹配页码颜色
- `暖色` / `notebook` → 暖金色 (0.79, 0.73, 0.60)
- `简约` / `minimalist` → 绿色 (0.28, 0.73, 0.47)
- `商务` / `professional` → 灰蓝色 (0.54, 0.60, 0.67)

### 5. 可点击目录 (add_toc_links.py)

**原理：** Chrome print-to-pdf 会保留 HTML 锚点链接作为 PDF 内部跳转。

实现两步：
1. 给正文中每个 `<h1>` 和 `<h2>` 添加 `id` 属性
2. 将 TOC 中的 `<span>` 替换为 `<a href="#id">`

```html
<!-- 修改前 -->
<li><span>前言</span><span class="toc-page-num">1</span></li>

<!-- 修改后 -->
<li><a href="#前言">前言</a><span class="toc-page-num">1</span></li>
```

### 6. 书签树 (add_outline.py)

**原理：** 使用 PyMuPDF 的 `doc.set_toc()` 方法，为 PDF 添加大纲/书签。

实现三步：
1. 从 HTML 正文提取所有 h1/h2/h3 标题及层级
2. 扫描 PDF 每页文字，匹配标题找到对应页码
3. 调用 `doc.set_toc()` 写入书签树

**效果：** 在 PDF 阅读器左侧导航栏显示可折叠的层级树，点击跳转章节。

### 7. 语法高亮 (highlight.py) — 可选，按需使用

`build.sh` 默认会运行语法高亮步骤。如果你的内容不含代码块，或不需要高亮，可以跳过此步骤：

```bash
# 方法1：手动分步执行
# 跳过 highlight，直接：
bash html2pdf.sh 你的文件.html 输出.pdf
python add_page_numbers.py 输出.pdf "" 2
python add_outline.py 你的文件.html 输出.pdf 2

# 方法2：或删除 build.sh 中的步骤2
```

highlight.py 的原理是用正则匹配 `<pre><code>` 块，识别关键词并替换为带 CSS class 的 `<span>`。

---

## 踩坑记录

### 1. CSS @page margin boxes 不显示
- **问题：** `@page { @bottom-center { content: counter(page) } }` 在生成的 PDF 中不显示
- **原因：** Chrome headless 的 `--no-header-footer` 参数会抑制所有 CSS @page margin boxes
- **解决：** 放弃 CSS 页码，改用 PyMuPDF 后处理注入

### 2. 页面边距与页码位置冲突
- **问题：** `@page { margin: 0 }` 时 PyMuPDF 插入的页码超出页面范围
- **解决：** `@page` 保持 `margin: 0`（Chrome 渲染用 padding），页码坐标用 `page.rect.height - 35`

### 3. 主题色匹配中文文件名
- **问题：** `add_page_numbers.py` 用英文关键词（如 'notebook'）匹配文件名，但中文文件名不包含英文
- **解决：** 在颜色字典中添加中文别名（如 `'暖色': (0.79, 0.73, 0.60)`）

### 4. TOC 页码写死问题
- **问题：** TOC 中的页码是 HTML 中硬编码的，内容变化后需要手动更新
- **解决：** 目前仍为手动/脚本更新。理想方案是自动计算，但因不同主题排版差异大，自动化复杂

### 5. 不同主题页数不一致
- **问题：** 商务正式主题比另外两个多 1 页，导致 TOC 页码偏移
- **原因：** 商务主题字体和间距较大，内容溢出到下一页
- **解决：** 调小商务主题的目录间距和字号，使页数统一为 15 页

### 6. --no-header-footer 副作用
- **问题：** `--no-header-footer` 会抑制所有 CSS @page 页眉页脚，包括自定义 header
- **解决：** 所有页眉、页码、页脚功能都移到后处理或正文区域实现

---

## 使用指南

### 快速开始

```bash
# 生成一个 PDF
bash build.sh samples/如何高效学习新技术.html 输出.pdf 2

# 三种主题已预置在 samples/ 中
```

### 创建新内容

1. 复制 `templates/template.html` 为新文件
2. 修改封面信息（标题、作者、日期）
3. 更新目录条目（标题 + 页码）
4. 填写正文内容（h1 分章，h2 分节）
5. 引用对应主题的 CSS（`themes/*.css`）
6. 运行 `bash build.sh <你的文件.html> <输出.pdf> 2`

### 创建新主题

1. 在 `themes/` 下新建 CSS 文件
2. 参考现有主题，覆盖封面、目录、正文、代码等样式
3. 在 `add_page_numbers.py` 的颜色字典中添加主题色
4. 在 `add_outline.py` 和 `add_toc_links.py` 无需修改（纯 HTML 结构驱动）

### 页码颜色配置

编辑 `add_page_numbers.py` 的 `THEME_COLORS` 字典：

```python
THEME_COLORS = {
    '关键词1': (R, G, B),  # RGB 值 0.0~1.0
    '关键词2': (R, G, B),
}
```

文件名字段包含任一关键词即匹配该颜色。

---

## 依赖

- **Python 3.8+**
  - PyMuPDF（fitz）：PDF 后处理
  - （语法高亮用标准库 re 实现，无额外依赖）
- **Chrome / Chromium**：HTML → PDF 渲染

```bash
pip install PyMuPDF
```
