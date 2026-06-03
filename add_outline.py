"""为 PDF 添加书签树（Outline），自动匹配正文标题到页码
用法: python add_outline.py <输入HTML> <输入PDF> [目录页数]
"""
import sys, re, tempfile, shutil
import fitz

html_path = sys.argv[1]
pdf_path = sys.argv[2]
toc_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 2

# 1. 从 HTML 正文中提取标题层级
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

body_start = html.find('class="body-content"')
body = html[body_start:] if body_start >= 0 else html

headings = []  # [(level, title)]
for m in re.finditer(r'<(h[1-3])(?:\s[^>]*)?>(.+?)</\1>', body):
    level = int(m.group(1)[1])
    title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
    headings.append((level, title))

if not headings:
    print("未找到标题，跳过书签")
    sys.exit(0)

# 2. 扫描 PDF，匹配标题到页码
doc = fitz.open(pdf_path)

toc = []
hi = 0
total = doc.page_count
start_page = 1 + toc_pages  # 跳过封面和第 1 页目录（0-indexed）

for page_num in range(start_page, total):
    page = doc[page_num]
    text = page.get_text()

    while hi < len(headings) and headings[hi][1] in text:
        level, title = headings[hi]
        toc.append([level, title, page_num + 1])  # 1-based PDF 页码
        hi += 1

    if hi >= len(headings):
        break

doc.close()

# 3. 写入书签
doc = fitz.open(pdf_path)
doc.set_toc(toc)

tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
tmp_path = tmp.name
tmp.close()
doc.save(tmp_path, deflate=True)
doc.close()
shutil.move(tmp_path, pdf_path)

print(f"书签已添加: {len(toc)} 个条目（{len(headings)} 个标题）")
