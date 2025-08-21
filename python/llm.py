import json
import requests
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
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

# -------- 工具函数 --------
def parse_date(date_str: str):
    """尝试解析 live_date，成功返回 datetime，失败返回 None"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        return None

def insert_by_date(record: dict):
    """根据 live_date 建立/写入对应数据库"""
    live_date = record.get("live_date", "")
    dt = parse_date(live_date)

    if dt is None:
        db_path = os.path.join(OUTPUT_DIR, "special.json")
    else:
        db_path = os.path.join(OUTPUT_DIR, f"{dt.strftime('%Y-%m-%d')}.json")

    # 打开对应日期的数据库
    db = TinyDB(db_path, storage=CachingMiddleware(JSONStorage))
    Weibo = Query()

    # 去重：检查是否已存在
    if db.search(Weibo.weibo_id == record.get("weibo_id", "")):
        print(f"微博 {record['weibo_id']} 已存在 {db_path}，跳过")
    else:
        db.insert(record)
        print(f"✅ 插入微博 {record['weibo_id']} 到 {db_path}")
    db.close()

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
    publish_time = record.get("date", "")

    prompt = f"""
提取微博内容中的以下字段:
1. live日期 (输出的json中对应的key用 live_date 替换) 请注意日期请按照%Y-%m-%d格式输出, 如xxxx-xx-xx
2. live地点 (输出的json中对应的key用 live_location 替换)
3. 团体全员 (输出的json中对应的key用 groups 替换)
4. 正文(输出的json中对应的key用 main_text 替换) (保持换行美观)
**请给我jsonl格式, 不要有任何不能被json.loads加载的字段**!!!
请不要在开头和结尾生成形如```,json 的字符, 以正常的大括号作为开头结尾
请一定注意年份不要错了, 时间准确是最重要的内容,
如果原文没有写年份, 请自行根据原文的publish_time={publish_time}推断
我希望你对content进行排版, 让它尽可能美观, 保持段落和格式的清晰

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

        # 写入按 live_date 分库
        insert_by_date(final_record)

    except Exception as e:
        print(f"处理微博 {weibo_id} 出错:", e)

print(f"处理完成，新记录 {len(new_records)} 条")
print(f"数据库存放目录: {OUTPUT_DIR}")
