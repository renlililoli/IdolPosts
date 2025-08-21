import sys
import json
from pathlib import Path

def main(cookie: str):
    config = {
        "user_id_list": "user_id_list.txt",
        "filter": 0,
        "since_date": 1,
        "end_date": "now",
        "random_wait_pages": [1, 3],
        "random_wait_seconds": [6, 10],
        "global_wait": [[1000, 3600], [500, 2000]],
        "write_mode": ["json", "txt"],
        "pic_download": 0,
        "video_download": 0,
        "file_download_timeout": [5, 5, 10],
        "result_dir_name": 1,
        "cookie": cookie
    }

    # 写入 config.json
    path = Path("config/config.json")
    path.write_text(json.dumps(config, indent=4, ensure_ascii=False), encoding="utf-8")
    print(f"✅ Config written to {path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("Cookie not provided")
    main(sys.argv[1])
