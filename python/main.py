import json
import re
import jieba
import os
from datetime import datetime

# 城市列表
cities = ["上海"]

def extract_repost_content(text: str) -> str | None:
    """
    从微博文本中提取 '转发内容:' 后面的文字
    """
    match = re.search(r"转发内容:\s*(.*)", text, re.S)
    if match:
        return match.group(1).strip()
    return None

# 文件路径
filename = "./config/weibo/7716940453/7716940453.json"
with open(filename, "r", encoding="utf-8") as f:
    data = json.load(f)

# 输出文件目录
os.makedirs("../database/json", exist_ok=True)

# 根据脚本运行日期生成文件名，例如 result_2025-08-19.jsonl
today = datetime.now().strftime("%Y-%m-%d")
output_file = f"../database/json/result_{today}.jsonl"

for day_data in data["weibo"]:
    content = day_data["content"]
    lenth, start = 9, 5
    if content[start: start + lenth] == "#live演出情报":
        main_text = extract_repost_content(content)
        if not main_text:
            continue
        found_cities = [city for city in cities if city in main_text]
        if found_cities:
            print(main_text)
            record = {
                "weibo_id": day_data.get("id", ""),       # 微博 ID
                "url": "https://weibo.cn/comment/" + day_data.get("id", ""),  # 微博 URL
                "date": day_data.get("created_at", ""),   # 微博创建日期
                "content": main_text                      # 转发内容
            }
            # 追加写入 JSON Lines 文件
            with open(output_file, "a", encoding="utf-8") as f_out:
                f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
