#!/bin/bash
# 知识分享 PDF 生成工具 (Git Bash / WSL / Linux / macOS)
# 用法: ./html2pdf.sh <输入HTML文件> [输出PDF文件]

set -u

INPUT="$1"
if [ -z "$INPUT" ]; then
    echo "用法: $0 <输入HTML文件> [输出PDF文件]"
    echo "示例: $0 output.html output.pdf"
    exit 1
fi

# 转换绝对路径
INPUT=$(cd "$(dirname "$INPUT")" 2>/dev/null && pwd)/$(basename "$INPUT")
if [ ! -f "$INPUT" ]; then
    echo "错误: 找不到输入文件 $INPUT"
    exit 1
fi

if [ -n "${2:-}" ]; then
    OUTPUT=$(cd "$(dirname "$2")" 2>/dev/null && pwd)/$(basename "$2")
else
    OUTPUT="${INPUT%.html}.pdf"
fi

# 查找浏览器 (Windows Git Bash / WSL / Linux / macOS)
BROWSER=""
if [ -f "/c/Program Files/Google/Chrome/Application/chrome.exe" ]; then
    BROWSER="/c/Program Files/Google/Chrome/Application/chrome.exe"
elif [ -f "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" ]; then
    BROWSER="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
elif [ -f "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" ]; then
    BROWSER="/c/Program Files (x86)/Google/Chrome/Application/chrome.exe"
elif [ -f "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" ]; then
    BROWSER="/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
else
    for cmd in google-chrome chromium chromium-browser msedge; do
        if command -v "$cmd" &>/dev/null; then
            BROWSER="$cmd"
            break
        fi
    done
fi

if [ -z "$BROWSER" ]; then
    echo "错误: 未找到 Chrome 或 Edge 浏览器"
    echo "请安装 Google Chrome 或 Microsoft Edge"
    exit 1
fi

echo "使用浏览器: $BROWSER"
echo "输入: $INPUT"
echo "输出: $OUTPUT"
echo ""

"$BROWSER" --headless --disable-gpu --no-header-footer --print-to-pdf="$OUTPUT" "$INPUT"

if [ $? -eq 0 ]; then
    echo ""
    echo "成功: PDF 已生成 -> $OUTPUT"
else
    echo "失败: PDF 生成出错"
    exit 1
fi
