# import weibo_spider
# import json
# import re
# import jieba


# cities = ["上海"]

# def extract_repost_content(text: str) -> str | None:
#     """
#     从微博文本中提取 '转发内容:' 后面的文字
#     """
#     match = re.search(r"转发内容:\s*(.*)", text, re.S)
#     if match:
#         return match.group(1).strip()
#     return None

# filename = "python/config/weibo/7716940453/7716940453.json"
# with open(filename, "r", encoding="utf-8") as f:
#     data = json.load(f)
    
# for day_data in data["weibo"]:
#     content = day_data["content"]
#     lenth, start = 9, 5
#     if content[start: start + lenth] == "#live演出情报":
#         main_text = extract_repost_content(content)
#         found_cities = [city for city in cities if city in main_text]
#         if found_cities:
#             print(main_text)
            
import weibo_spider
import json
import re
import jieba
import os

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

# 输出文件
os.makedirs("../database", exist_ok=True)  # 确保 database 目录存在
output_file = "../database/result.jsonl"   # JSON Lines 文件

for day_data in data["weibo"]:
    content = day_data["content"]
    lenth, start = 9, 5
    if content[start: start + lenth] == "#live演出情报":
        main_text = extract_repost_content(content)
        found_cities = [city for city in cities if city in main_text]
        if found_cities:
            print(main_text)
            record = {
                "weibo_id": day_data.get("id", ""),       # 微博 ID
                "url": "https://weibo.cn/comment/" + day_data.get("id", ""),             # 微博 URL
                "date": day_data.get("created_at", ""),   # 微博创建日期
                "content": main_text                       # 转发内容
            }
            # 追加写入 JSON Lines 文件
            with open(output_file, "a", encoding="utf-8") as f_out:
                f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
