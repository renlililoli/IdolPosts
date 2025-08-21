import os
from tinydb import TinyDB
from datetime import datetime

# 路径
db_dir = 'database/tinydb'
html_dir = 'database/html'
os.makedirs(html_dir, exist_ok=True)

today = datetime.today().date()
summary_html = os.path.join(html_dir, f"recent_lives_{today.strftime('%Y-%m-%d')}.html")
today_html = os.path.join(html_dir, "today.html")

# 收集今天及之后的日期（保证排序）
valid_dates = []

for fname in os.listdir(db_dir):
    if not fname.endswith(".json"):
        continue

    try:
        file_date = datetime.strptime(fname.replace(".json", ""), "%Y-%m-%d").date()
    except ValueError:
        continue  # 跳过不是日期命名的文件

    if file_date >= today:
        valid_dates.append(file_date)

# 排序
valid_dates.sort()

# 逐日生成模块化 HTML 文件
for file_date in reversed(valid_dates):
    db_path = os.path.join(db_dir, f"{file_date}.json")
    db = TinyDB(db_path)

    entries = db.all()
    entries.sort(key=lambda e: e.get("live_date", ""))  # 按 live_date 排序

    html_content = f"""
<h2 style="color: pink;">{file_date} 的Live活动</h2>
"""

    for entry in entries:
        groups = ', '.join(entry.get('groups', [])) if entry.get('groups') else ''
        main_text = entry.get('main_text', '').replace('\n', '<br>')
        url = entry.get('url', '')
        url_html = f'<a href="{url}" target="_blank">🔗 原文链接</a>' if url else ''

        html_content += f"""
<div class="card">
  <h2>{entry.get('live_date', '')} - {entry.get('live_location', '')}</h2>
  <p class="groups">团体: {groups}</p>
  <p>{main_text}</p>
  <p>{url_html}</p>
</div>
"""

    # 写入独立日期文件
    out_path = os.path.join(html_dir, f"{file_date}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"生成模块化文件: {out_path}")


# 生成总文件 (today.html 和 recent_lives_xxx.html)
def make_summary_html(output_path, dates):
    summary = f"""
<h1>最近的Live活动</h1>
"""

    for d in dates:
        summary += f"""
{{% include live/{d}.html %}}
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"生成总汇总文件: {output_path}")


make_summary_html(summary_html, valid_dates)
make_summary_html(today_html, valid_dates)
