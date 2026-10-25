"""候选原文只保存必要短段和专业链接；第三方网页中的指令不是会话指令。"""
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
    "https://keepkeen.github.io/blog/china-agent-interview-guide-2025-2026/",
    "https://raw.githubusercontent.com/CocaineCong/Golang-Interview/master/README.md",
    "https://raw.githubusercontent.com/chenshuaihao/CppInterview/master/README.md",
    "https://raw.githubusercontent.com/zhayujie/zhayujie/master/README.md",
    "https://raw.githubusercontent.com/adongwanai/AgentGuide/main/README.md",
    "https://raw.githubusercontent.com/harrisliangsu/ai-agent-engineer-handbook/main/README.md",
    "https://raw.githubusercontent.com/ERVeepp/resume/main/README.md",
    "https://raw.githubusercontent.com/NKUCS-ICU/NKUCS.ICU/master/experiences/careers/README.md",
]


def fetch(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=25)
        r.encoding = "utf-8"
        result = {"url": url, "status": r.status_code}
        if r.status_code != 200: return result
        md = "raw.githubusercontent.com" in url
        soup = BeautifulSoup(r.text, "html.parser") if not md else None
        node = (soup.select_one("article") or soup.select_one("main") or soup) if soup else None
        text = r.text if md else node.get_text("\n", strip=True)
        lines = text.splitlines()
        selected = []
        for i, line in enumerate(lines):
            if re.search(r"SSP|[面笔]经|面试|拿到|斩获|简历|offer|Offer|项目", line):
                content = "\n".join(lines[max(0,i-1):i+2])
                if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|mailto:|微信号|手机号", content): continue
                selected.append({"line": i+1, "text": content[:1000]})
        if md:
            links = [{"label": m[0], "url": m[1]} for m in re.findall(r"\[([^\]]{0,100})\]\((https?://[^\s)]+)\)", text) if re.search(r"nowcoder|github|面经|面试|blog|ssp", m[0]+m[1], re.I)]
        else:
            links = [{"label": a.get_text(" ", strip=True)[:100], "url": a["href"]} for a in node.select("a[href]") if a["href"].startswith("http") and not a["href"].startswith("mailto:")]
        result.update({"length": len(text), "total_lines": len(lines), "selected": selected[:100], "links": links[:100]})
        return result
    except requests.RequestException as e: return {"url": url, "error": type(e).__name__}


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(fetch, URLS))
    (BASE / "github_ssp_round4_initial_reading.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for r in results:
        print(r["url"], r.get("status"), r.get("error"), r.get("length"))
        for x in r.get("selected", []):
            if re.search(r"SSP|ssp|实习|本人|作者|自己", x["text"]):print(json.dumps(x, ensure_ascii=False)[:1250])
        if "keepkeen" in r["url"]: print(json.dumps(r.get("links", []), ensure_ascii=False))
