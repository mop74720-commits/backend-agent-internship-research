import concurrent.futures
import json
from pathlib import Path
import re
import warnings
warnings.filterwarnings("ignore")
import requests
from bs4 import BeautifulSoup

BASE = Path(__file__).resolve().parent
URLS = [
 "https://www.nowcoder.com/discuss/746382064101908480",
 "https://www.nowcoder.com/feed/main/detail/8a553bb6ea8445d0b0abe11e87614cea",
 "https://www.nowcoder.com/discuss/872120976190816256",
 "https://www.nowcoder.com/feed/main/detail/28edcddf0c204c08b6562a3e6e6b73ae",
 "https://www.nowcoder.com/feed/main/detail/681c33aafac84af0a70b6fd5e663a04c",
 "https://www.nowcoder.com/discuss/904419777614049280",
 "https://www.nowcoder.com/feed/main/detail/25aec4b727ac4985a7b83fa1e05594e8",
 "https://www.nowcoder.com/feed/main/detail/63f974c8a2214503bdc0ad7505cdc15b",
 "https://raw.githubusercontent.com/CocaineCong/Golang-Interview/5a48dfc6003468aa6c152da05e79beafdee1bcd7/a.%20%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8.md",
 "https://raw.githubusercontent.com/CocaineCong/Golang-Interview/5a48dfc6003468aa6c152da05e79beafdee1bcd7/b.%20B%E7%AB%99.md",
]


def fetch(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=25)
        r.encoding = "utf-8"
        out = {"url": url, "status": r.status_code, "final_url": r.url}
        if r.status_code != 200: return out
        if "raw.githubusercontent.com" in url:
            text = r.text
            out["selector"] = "raw固定文件"
        else:
            s = BeautifulSoup(r.text, "html.parser")
            out["title"] = s.title.get_text() if s.title else ""
            out["canonical"] = s.select_one('link[rel="canonical"]')["href"] if s.select_one('link[rel="canonical"]') else None
            node = s.select_one(".nc-post-content") or s.select_one(".post-content-box") or s.select_one(".feed-detail-content") or s.select_one(".content-box")
            out["selector"] = node.get("class") if node else None
            text = node.get_text("\n", strip=True) if node else ""
            # 仅保留可见日期，不猜测帖子年份。
            out["visible_dates"] = list(dict.fromkeys(re.findall(r"20[12]\d[-年/.]\d{1,2}[-月/.]\d{1,2}|\d{2}-\d{2}\s*\d{2}:\d{2}", s.get_text(" ", strip=True))))[:5]
        text = "\n".join(line for line in text.splitlines() if not re.search(r"mailto:|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|微信号|手机号|加[我微]", line))
        out["body_length"] = len(text)
        out["short_excerpt"] = text[:160]
        print("BODY", url, json.dumps({**out, "read_text": text[:14500]}, ensure_ascii=False))
        return out
    except requests.RequestException as e: return {"url": url, "error": type(e).__name__}


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(fetch, URLS))
    (BASE / "github_ssp_round4_fulltext_access.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for r in results: print("RESULT", json.dumps(r, ensure_ascii=False))
