#!/usr/bin/env python3
"""
知识分享 PDF - 代码语法高亮工具
基于 Pygments 对 HTML 中的 <pre><code> 块添加 One Dark Pro 配色。
用法: python highlight.py <输入HTML文件> [输出HTML文件]
"""

import sys
import re
import html as html_mod
from pygments import highlight
from pygments.lexers import guess_lexer, PythonLexer, JavascriptLexer, BashLexer
from pygments.lexers.special import TextLexer
from pygments.formatter import Formatter
from xml.sax.saxutils import escape as xml_escape


class OneDarkFormatter(Formatter):
    """One Dark Pro 配色的 Pygments Formatter"""

    def __init__(self, **options):
        super().__init__(**options)
        # One Dark Pro 配色映射
        self.colors = {
            # Token type (Pygments 完整名) -> CSS class name
            'Token.Keyword':         'odp-kw',      # #c678dd 紫色
            'Token.Keyword.Type':    'odp-kw',
            'Token.Keyword.Namespace':'odp-kw',
            'Token.Name.Function':   'odp-func',    # #61afef 蓝色
            'Token.Name.Class':      'odp-class',   # #e5c07b 黄色
            'Token.Name.Decorator':  'odp-dec',     # #61afef 蓝色
            'Token.Name.Builtin':    'odp-builtin', # #e06c75 红色
            'Token.Name.Attribute':  'odp-attr',    # #d19a66 橙色
            'Token.Name.Constant':   'odp-const',   # #d19a66 橙色
            'Token.Name.Namespace':  'odp-class',   # #e5c07b
            'Token.Name.Variable':   'odp-var',     # #e06c75
            'Token.Literal.String':          'odp-str',     # #98c379 绿色
            'Token.Literal.String.Doc':      'odp-comment', # #5c6370 灰色
            'Token.Literal.String.Interpol': 'odp-str',
            'Token.Literal.String.Double':   'odp-str',
            'Token.Literal.String.Single':   'odp-str',
            'Token.Literal.Number':    'odp-num',     # #d19a66 橙色
            'Token.Comment':           'odp-comment', # #5c6370 灰色
            'Token.Comment.Single':    'odp-comment',
            'Token.Comment.Multiline': 'odp-comment',
            'Token.Comment.Special':   'odp-comment',
            'Token.Operator':          'odp-op',      # #abb2bf 白色
            'Token.Operator.Word':     'odp-kw',
            'Token.Punctuation':       'odp-op',
            'Token.Generic.Heading':   'odp-class',
            'Token.Generic.Subheading':'odp-class',
        }

    def format(self, tokensource, outfile):
        for ttype, value in tokensource:
            css_class = ''
            # 从最具体到最通用匹配
            for cls in [str(ttype)] + [str(ttype.parent)] * 3:
                if cls in self.colors:
                    css_class = self.colors[cls]
                    break
            if css_class:
                outfile.write(f'<span class="{css_class}">{xml_escape(value)}</span>')
            else:
                outfile.write(xml_escape(value))


def highlight_html(html_content):
    """对HTML中的<pre><code>块添加语法高亮"""

    # 匹配 <pre><code> ... </code></pre>
    pattern = re.compile(
        r'<pre><code>(.*?)</code></pre>',
        re.DOTALL
    )

    def replace_code(match):
        code_text = match.group(1)
        # HTML 反转义
        code_text = html_mod.unescape(code_text)

        # 智能检测语言：去掉注释和字符串后再猜，避免中文干扰
        lexer = detect_lexer(code_text)

        formatter = OneDarkFormatter()
        highlighted = highlight(code_text, lexer, formatter)

        return f'<pre><code>{highlighted}</code></pre>'

    return pattern.sub(replace_code, html_content)


def detect_lexer(code_text):
    """智能检测代码语言，避免中文注释干扰"""
    # 去掉注释和字符串，提高检测准确率
    clean = code_text
    clean = re.sub(r'#.*$', '', clean, flags=re.MULTILINE)
    clean = re.sub(r'//.*$', '', clean, flags=re.MULTILINE)
    clean = re.sub(r'""".*?"""', '', clean, flags=re.DOTALL)
    clean = re.sub(r"'''.*?'''", '', clean, flags=re.DOTALL)
    clean = re.sub(r'/\*.*?\*/', '', clean, flags=re.DOTALL)
    clean = clean.strip()

    # 如果去掉注释后没内容，用完整文本
    if len(clean) < 10:
        clean = code_text

    # 按优先级尝试常见语言
    for lexer_cls in [PythonLexer, JavascriptLexer, BashLexer]:
        try:
            lexer = lexer_cls()
            tokens = list(lexer.get_tokens(clean[:200]))
            # 如果有超过2种不同token类型（排除Text），认为匹配
            types = set(str(t) for t, v in tokens if str(t) != 'Token.Text')
            if len(types) > 2:
                return lexer
        except Exception:
            continue

    # 最后用通用猜测
    try:
        return guess_lexer(clean[:500])
    except Exception:
        return PythonLexer()

    return pattern.sub(replace_code, html_content)


def main():
    if len(sys.argv) < 2:
        print("用法: python highlight.py <输入HTML文件> [输出HTML文件]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    highlighted = highlight_html(content)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(highlighted)

    lines_changed = content.count('<pre><code>')
    print(f"完成: {lines_changed} 个代码块已高亮 -> {output_file}")


if __name__ == '__main__':
    main()
