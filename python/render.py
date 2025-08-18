#!/usr/bin/env python3
# scripts/render_jsonl_to_html.py
import json
import html
import re
from pathlib import Path

INPUT = Path("database/result.jsonl")   # 输入 JSONL（每行一个 JSON 对象）
OUTPUT = Path("database/result.html")   # 输出 HTML

URL_RE = re.compile(r'https?://[^\s\)\]\}，,。；;\'"<>]+')  # 简单 URL 匹配（排除常见结束符）

def linkify_text(text: str) -> str:
    """
    将文本中的 http/https 链接替换成可点的 <a> 标签，同时进行 HTML 转义。
    """
    if not text:
        return ""
    # 先 escape 整体文本，避免注入
    escaped = html.escape(text)
    # 再把 URL 部分替换为 <a>（使用原始 URL 的 html.escape 作为 href 和文本）
    def repl(m):
        url = m.group(0)
        return f'<a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">{html.escape(url)}</a>'
    return URL_RE.sub(repl, escaped)

def render_html(records):
    head = """<!doctype html>
<html>
<meta charset="utf-8">
<head>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial; line-height:1.5; padding:18px;}
    .record { border-bottom:1px solid #eee; padding:12px 0;}
    .meta { color:#666; font-size:0.9em; margin-bottom:6px; }
    .content { white-space:pre-wrap; }
    a { color: #1a73e8; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
  <title>Weibo Results</title>
</head>
<body>
  <h1>Weibo Results</h1>
  <div class="records">
"""
    tail = """
  </div>
</body>
</html>
"""
    body_parts = []
    for r in records:
        weibo_id = html.escape(str(r.get("weibo_id", "")))
        url = r.get("url", "") or ""
        date = html.escape(str(r.get("date", "")))
        content_raw = r.get("content", "")
        content_html = linkify_text(content_raw).replace("\n", "<br>")
        # 标题：如果有 url 就把 weibo_id 包成链接
        if url:
            title_html = f'<a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">{weibo_id}</a>'
        else:
            title_html = weibo_id or "—"
        meta = f'<div class="meta"><strong>{title_html}</strong> &nbsp; <span>{date}</span></div>'
        rec_html = f'<div class="record">{meta}<div class="content">{content_html}</div></div>'
        body_parts.append(rec_html)
    return head + "\n".join(body_parts) + tail

def load_jsonl(path: Path):
    if not path.exists():
        print(f"[WARN] {path} not found, returning empty list.")
        return []
    records = []
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                records.append(obj)
            except json.JSONDecodeError:
                print(f"[WARN] line {i} is not valid JSON, skipping.")
    return records

def main():
    records = load_jsonl(INPUT)
    if not records:
        print("[INFO] no records found; writing empty html.")
    html_text = render_html(records)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html_text, encoding="utf-8")
    print(f"Wrote HTML to: {OUTPUT.resolve()}")

if __name__ == "__main__":
    main()
