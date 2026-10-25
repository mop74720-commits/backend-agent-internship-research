"""只读取公开页面与固定源码文本；不执行被调研仓库代码。"""
import concurrent.futures
import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = Path(__file__).resolve().parent
SHA = "b6157f3ca72a0c4dee0f873ad974cb61e4610c8f"
URLS = [
    f"https://raw.githubusercontent.com/liyupi/yupi-skill/{SHA}/README.md",
    f"https://raw.githubusercontent.com/liyupi/yupi-skill/{SHA}/references/identity.md",
    f"https://raw.githubusercontent.com/liyupi/yupi-skill/{SHA}/references/knowledge-sources.md",
    "https://www.codefather.cn/course/yupi",
    "https://erdengk.top/archives/wo-de-shuo-shi-qian-ban-sheng",
    "https://erdengk.top/archives/gsoc-cong-kai-shi-dao-zhong-xuan",
    "https://erdengk.github.io/gsoc-analyse/",
]


def fetch(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=28)
        r.encoding = "utf-8"
        is_md = "raw.githubusercontent.com" in url
        soup = BeautifulSoup(r.text, "html.parser") if not is_md else None
        text = r.text if is_md else soup.get_text("\n", strip=True)
        # 不保留联系方式；仅摘取检索主题附近的短段，避免转载整份履历。
        lines = text.splitlines()
        selected = []
        for i, line in enumerate(lines):
            if re.search(r"SSP|[面笔]试|简历|offer|Offer|项目|ShenYu|GSoC|腾讯|[成贡]献|201[89]|202[0-3]", line):
                block = "\n".join(lines[max(0, i - 1):i + 2])
                if re.search(r"mailto:|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|微信号|手机号", block):
                    continue
                selected.append({"line": i + 1, "text": block[:1200]})
        links = []
        if soup:
            for a in soup.select("a[href]"):
                label = a.get_text(" ", strip=True)
                href = a["href"]
                if re.search(r"github|面试|成长|硕士|gsoc|shenyu", href + label, re.I) and not href.startswith("mailto:"):
                    links.append({"label": label[:100], "url": href})
        return {"url": url, "final_url": r.url, "status": r.status_code, "length": len(text), "title": soup.title.get_text() if soup and soup.title else "", "selected": selected, "links": links[:50]}
    except requests.RequestException as e:
        return {"url": url, "error": type(e).__name__}


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(fetch, URLS))
    (BASE / "github_ssp_round3_root_further_reads.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for item in results:
        print(json.dumps(item, ensure_ascii=False))
