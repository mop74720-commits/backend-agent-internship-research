import concurrent.futures
import importlib.util
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("public_search", BASE / "第四轮Agent公开检索.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
queries = [
    ("yahoo", 'github SSP 后端 我的项目 秋招'),
    ("yahoo", 'github 拿到 SSP C++ 项目 面经'),
    ("yahoo", 'github 腾讯 SSP 简历 Java'),
    ("yahoo", 'github 字节 SSP Go 面经'),
    ("yahoo", '"SSP" "zhayujie"'),
    ("yahoo", '"SSP" "chenshuaihao"'),
    ("yahoo", '"SSP" "JasonkayZK"'),
    ("yahoo", '"SSP" "Agent" "实习" "拿到"'),
]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(module.fetch, queries))
(BASE / "github_ssp_round4_extended_search.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for r in results:
    print(r["query"], r.get("status"), len(r.get("items", [])))
    for x in r.get("items", []): print(json.dumps(x, ensure_ascii=False)[:950])
