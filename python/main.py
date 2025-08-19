import json
import re
import jieba
import os
from datetime import datetime

# 地点列表, 用来判断是否位于上海
cities = [
    "上海",
    "育音堂",
    "新歌空间",
    "世界树", "第一百货"
    "聚一场", "上海广场",
    "瓦肆",
    "MAO", "mao", "Mao"
    "cave", "Cave", "CAVE",
    "星偶界",
    "theboxx", "the boxx", "城市乐园",
    "九六广场", "九六",
    "环球港",
    "万代南梦宫", "未来剧场", "梦想剧场", "浅水湾",
    "rojo", "ROJO", "Rojo",
    "安可空间", "意空间见",
    "次乐园", "小南门",
    "长宁", "虹口", "杨浦", "黄浦", "徐汇", "浦东", "静安", 
    "可游米",
    "上滨",

    ]

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
