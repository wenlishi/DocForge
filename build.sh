#!/bin/bash
# 一键构建：语法高亮 + PDF 生成
# 用法: ./build.sh <输入HTML文件> [输出PDF文件] [目录页数]

set -eu

INPUT="$1"
if [ -z "$INPUT" ] || [ ! -f "$INPUT" ]; then
    echo "用法: $0 <输入HTML文件> [输出PDF文件]"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INPUT_FILE="$(cd "$(dirname "$INPUT")" && pwd)/$(basename "$INPUT")"

# 临时高亮文件
HIGHLIGHTED="${INPUT_FILE%.html}-highlighted.html"

echo "=== 步骤1: 添加目录锚点 ==="
PYTHONIOENCODING=utf-8 python "$SCRIPT_DIR/add_toc_links.py" "$INPUT_FILE"

echo ""
echo "=== 步骤2: 语法高亮 ==="
PYTHONIOENCODING=utf-8 python "$SCRIPT_DIR/highlight.py" "$INPUT_FILE" "$HIGHLIGHTED"

echo ""
echo "=== 步骤3: 生成 PDF ==="
bash "$SCRIPT_DIR/html2pdf.sh" "$HIGHLIGHTED" "${2:-}"

echo ""
echo "=== 步骤4: 添加页码 ==="
PYTHONIOENCODING=utf-8 python "$SCRIPT_DIR/add_page_numbers.py" "${2:-${HIGHLIGHTED%.html}.pdf}" "" "${3:-2}"

echo ""
echo "=== 步骤5: 添加书签 ==="
PYTHONIOENCODING=utf-8 python "$SCRIPT_DIR/add_outline.py" "$HIGHLIGHTED" "${2:-${HIGHLIGHTED%.html}.pdf}" "${3:-2}"

# 清理中间文件
rm -f "$HIGHLIGHTED"
echo ""
echo "=== 完成 ==="
echo "PDF: ${2:-${HIGHLIGHTED%.html}.pdf}"
