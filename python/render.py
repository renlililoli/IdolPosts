#!/usr/bin/env python3
# scripts/render_jsonl_to_html.py
import json
import html
import re
from pathlib import Path
from datetime import date

# 自动根据当前日期选择文件
TODAY = date.today().strftime("%Y-%m-%d")
INPUT = Path(f"database/json/result_{TODAY}.jsonl")   # 输入 JSONL（按日期命名）
OUTPUT = Path(f"database/html/{TODAY}.html")   # 输出 HTML（同样按日期）
OUTPUT1 = Path(f"database/today/result.html")

URL_RE = re.compile(r'https?://[^\s\)\]\}，,。；;\'"<>]+')

def linkify_text(text: str) -> str:
    if not text:
        return ""
    escaped = html.escape(text)
    def repl(m):
        url = m.group(0)
        return f'<a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">{html.escape(url)}</a>'
    return URL_RE.sub(repl, escaped)

def render_html(records):
    head = f"""<!doctype html>
<html>
<meta charset="utf-8">
<head>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial; line-height:1.5; padding:18px;}}
    .record {{ border-bottom:1px solid #eee; padding:12px 0;}}
    .meta {{ color:#666; font-size:0.9em; margin-bottom:6px; }}
    .content {{ white-space:pre-wrap; }}
    a {{ color: #1a73e8; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
  <title>Weibo Results {TODAY}</title>
</head>
<body>
  <h1>Weibo Results {TODAY}</h1>
  <div class="records">
"""
    tail = """
  </div>
</body>
</html>
"""
    body_parts = []
    for r in reversed(records):
        weibo_id = html.escape(str(r.get("weibo_id", "")))
        url = r.get("url", "") or ""
        date_str = html.escape(str(r.get("date", "")))
        content_raw = r.get("content", "")
        content_html = linkify_text(content_raw).replace("\n", "<br>")
        if url:
            title_html = f'<a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">{weibo_id}</a>'
        else:
            title_html = weibo_id or "—"
        meta = f'<div class="meta"><strong>{title_html}</strong> &nbsp; <span>{date_str}</span></div>'
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
        print(f"[INFO] no records found in {INPUT.name}; writing empty html.")
    html_text = render_html(records)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html_text, encoding="utf-8")
    OUTPUT1.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT1.write_text(html_text, encoding="utf-8")
    print(f"Wrote HTML to: {OUTPUT1.resolve()}")
    print(f"Wrote HTML to: {OUTPUT.resolve()}")

if __name__ == "__main__":
    main()
