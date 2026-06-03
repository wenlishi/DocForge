"""为 PDF 添加页码（后处理）
用法: python add_page_numbers.py <输入PDF> [输出PDF] [目录页数]
  目录页数: 封面后有多少页目录（默认 1，0 表示无目录）
"""
import sys, os, shutil
import tempfile

try:
    import fitz
except ImportError:
    print("请安装 PyMuPDF: pip install PyMuPDF")
    sys.exit(1)

input_pdf = sys.argv[1]
output_pdf = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else input_pdf
toc_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 1

# 配色调色板（按文件名关键词匹配）
THEME_COLORS = {
    'notebook': (0.79, 0.73, 0.60),    # #c9b99a 暖金
    '暖色':    (0.79, 0.73, 0.60),
    'minimalist': (0.28, 0.73, 0.47),  # #48bb78 绿色
    '简约':    (0.28, 0.73, 0.47),
    'professional': (0.54, 0.60, 0.67),# #8899aa 灰蓝
    '商务':    (0.54, 0.60, 0.67),
}

# 根据文件名猜测主题
fname = os.path.basename(input_pdf).lower()
color = (0.5, 0.5, 0.5)  # 默认灰色
for theme, rgb in THEME_COLORS.items():
    if theme in fname:
        color = rgb
        break

doc = fitz.open(input_pdf)

def to_roman(n):
    """整数转小写罗马数字（1~10）"""
    return ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x'][n - 1]

body_page = 1
for i, page in enumerate(doc):
    if i == 0:
        continue  # 封面无页码
    r = page.rect
    x = r.width / 2
    y = r.height - 35

    if i <= toc_pages:
        num = to_roman(i)  # 目录用罗马数字 i, ii, iii...
    else:
        num = str(body_page)
        body_page += 1

    page.insert_text(
        (x, y), num,
        fontsize=10,
        color=color,
        overlay=True,
    )

# 保存到临时文件再替换，避免增量保存问题
tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
tmp_path = tmp.name
tmp.close()
doc.save(tmp_path, deflate=True)
doc.close()
shutil.move(tmp_path, output_pdf)
print(f"页码已添加到: {output_pdf}")
