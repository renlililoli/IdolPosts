import json
import requests
from tinydb import TinyDB, Query
from datetime import datetime
import argparse
import os

# -------- 参数设置 --------
parser = argparse.ArgumentParser()
parser.add_argument("--apikey", required=True, help="百度 LLM API Key")
parser.add_argument("--input", required=True, help="输入 JSONL 文件路径")
parser.add_argument("--output_dir", default="database/tinydb", help="生成 JSONL 文件目录")
args = parser.parse_args()

API_KEY = args.apikey
INPUT_FILE = args.input
OUTPUT_DIR = args.output_dir

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 输出文件名带日期
today_str = datetime.now().strftime("%Y-%m-%d")
output_file = os.path.join(OUTPUT_DIR, f"result_{today_str}.jsonl")

# TinyDB 数据库
db_path = os.path.join(OUTPUT_DIR, "weibo_db.json")
db = TinyDB(db_path)
Weibo = Query()

# -------- 百度 LLM 调用函数 --------
def call_baidu_llm(prompt: str) -> dict:
    url = "https://qianfan.baidubce.com/v2/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "model": "ernie-4.0-8k",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    resp = requests.post(url, headers=headers, json=data)
    resp.raise_for_status()
    return resp.json()

# -------- 读取 JSONL 输入 --------
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    input_records = [json.loads(line) for line in f]

# -------- 处理每条记录 --------
new_records = []

for record in input_records:
    print(record)
    content = record.get("content", "")
    weibo_id = record.get("weibo_id", "")

    # 检查数据库中是否已存在
    if db.search(Weibo.weibo_id == weibo_id):
        print(f"微博 {weibo_id} 已存在，跳过")
        continue

    prompt = f"""
提取微博内容中的以下字段:
1. live日期 (输出的json中对应的key用 live_date 替换) 请注意日期请按照%Y-%m-%d格式输出, 如2023-08-22
2. live地点 (输出的json中对应的key用 live_location 替换)
3. 团体全员 (输出的json中对应的key用 groups 替换)
4. 正文(输出的json中对应的key用 main_text 替换) (保持换行美观)
**请给我jsonl格式, 不要有任何不能被json.loads加载的字段**!!!
请不要在开头和结尾生成形如```,json 的字符, 以正常的大括号作为开头结尾

如果没有某个字段，请留空。内容如下：
{content}
"""
    try:
        llm_result = call_baidu_llm(prompt)
        # 百度 LLM 输出文本通常在 choices[0].message.content
        llm_text = llm_result.get("choices", [{}])[0].get("message", {}).get("content", "")
        llm_text = llm_text.replace("```json", "").replace("```", "").strip()
        print(llm_text)
        # 尝试解析为 JSON
        try:
            extracted = json.loads(llm_text)
        except json.JSONDecodeError:
            extracted = {
                "live_date": "",
                "live_location": "",
                "groups": "",
                "main_text": llm_text.strip()
            }
        # 合并原始信息
        final_record = {
            "weibo_id": weibo_id,
            "url": record.get("url", ""),
            "date": record.get("date", ""),
            **extracted
        }
        new_records.append(final_record)

        # 写入每日 JSONL 文件
        # with open(output_file, "a", encoding="utf-8") as f_out:
        #     f_out.write(json.dumps(final_record, ensure_ascii=False) + "\n")

        # 写入 TinyDB
        db.insert(final_record)

    except Exception as e:
        print(f"处理微博 {weibo_id} 出错:", e)

print(f"处理完成，新记录 {len(new_records)} 条")
# print(f"JSONL 文件: {output_file}")
print(f"TinyDB 数据库: {db_path}")
