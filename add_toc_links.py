"""为 HTML 添加可点击目录跳转（锚点链接）
用法: python add_toc_links.py <输入HTML>
  会在原文件上直接修改
"""
import re, sys, os

path = sys.argv[1]
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# ---- 1. 给正文中的 h1/h2 添加 id ----
# 收集所有标题文本用于生成 id
headings = []

def add_id_to_heading(m):
    tag = m.group(1)  # h1 or h2
    text = m.group(2)
    # 生成 id: 去除特殊字符
    id_ = re.sub(r'[^\w一-鿿]', '', text)
    headings.append((tag, text, id_))
    return f'<{tag} id="{id_}">{text}</{tag}>'

body_content_start = html.find('<section class="body-content">')
body_content_end = html.find('</section>', body_content_start)
body = html[body_content_start:body_content_end]

body = re.sub(
    r'<(h[12])>(.+?)</\1>',
    add_id_to_heading,
    body
)

html = html[:body_content_start] + body + html[body_content_end:]

# ---- 2. 替换目录中的条目为可点击链接 ----
# 对每个 TOC 条目，找到标题文本并包裹为 <a>
def make_toc_link(m):
    prefix = m.group(1)  # whitespace before <span>
    text = m.group(2)
    suffix = m.group(3)  # rest after </span>

    # 找到匹配的 heading id
    id_ = re.sub(r'[^\w一-鿿]', '', text)

    return f'{prefix}<a href="#{id_}" style="color:inherit;text-decoration:none;">{text}</a>{suffix}'

# 匹配 toc-item 中的第一个 <span>内容</span>
html = re.sub(
    r'(<li[^>]*class="toc-item[^"]*">\s*)<span>([^<]+)</span>(\s*<span class="toc-(?:dots|page-num))',
    make_toc_link,
    html
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"已添加目录链接: {path}")
