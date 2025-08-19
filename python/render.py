from tinydb import TinyDB
from datetime import datetime, timedelta

# TinyDB 路径
db_path = 'database/tinydb/weibo_db.json'
db = TinyDB(db_path)

# 时间范围：最近10天
today = datetime.today()
ten_days_ago = today - timedelta(days=10)
output_html = 'database/html/' + f"recent_lives_{today.strftime('%Y-%m-%d')}.html"
today_html = 'database/today.html'

recent_entries = []

# 遍历所有条目
for entry in db.all():
    live_date_str = entry["live_date"]
    print(live_date_str)
    if not live_date_str:
        continue

    try:
        live_datetime = datetime.strptime(live_date_str, "%Y-%m-%d")
    except ValueError:
        continue

    if ten_days_ago <= live_datetime <= today:
        entry["_date_obj"] = live_datetime
        recent_entries.append(entry)

# 按日期倒序排序
recent_entries.sort(key=lambda x: x["_date_obj"], reverse=True)

# 生成 HTML 内容
html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>最近10天的Live活动</title>
<style>
body {{ font-family: "微软雅黑", sans-serif; background-color: #f7f7f7; padding: 20px; }}
.card {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
.card h2 {{ margin: 0 0 10px 0; font-size: 1.2em; color: #333; }}
.card p {{ margin: 5px 0; line-height: 1.5; }}
.card .groups {{ color: #555; font-size: 0.95em; }}
</style>
</head>
<body>
<h1>最近10天的Live活动</h1>
"""

# 添加每条条目
for entry in recent_entries:
    groups = ', '.join(entry.get('groups', [])) if entry.get('groups') else ''
    main_text = entry.get('main_text', '').replace('\n', '<br>')
    html_content += f"""
<div class="card">
  <h2>{entry.get('live_date', '')} - {entry.get('live_location', '')}</h2>
  <p class="groups">团体: {groups}</p>
  <p>{main_text}</p>
</div>
"""

html_content += """
</body>
</html>
"""

# 写入文件
with open(output_html, "w", encoding="utf-8") as f:
    f.write(html_content)

with open(today_html, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"生成完成: {output_html}")
print(f"生成完成: {today_html}")
