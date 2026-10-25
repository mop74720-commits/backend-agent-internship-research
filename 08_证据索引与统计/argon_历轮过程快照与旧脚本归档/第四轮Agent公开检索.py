"""检索公开索引；结果仅用于发现，不代替原文核验。"""
import concurrent.futures
import json
from pathlib import Path
import re
from urllib.parse import unquote
import warnings

warnings.filterwarnings("ignore")
import requests
from bs4 import BeautifulSoup

BASE = Path(__file__).resolve().parent
QUERIES = [
    ("github_repositories", 'SSP 智能体 in:readme fork:false'),
    ("github_repositories", 'SSP RAG in:readme fork:false'),
    ("github_issues", 'SSP "Agent" "offer"'),
    ("github_issues", 'SSP "大模型" "面经"'),
    ("yahoo", '"Agent开发" "SSP" 面经 github'),
    ("yahoo", '"拿到" "SSP" "RAG"'),
    ("yahoo", '"SSP" "智能体" "面经"'),
    ("yahoo", '大模型应用 开发 SSP 面经 GitHub 本人'),
]


def clean(text):
    return re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[联系方式略]", text or "")


def fetch(item):
    provider, query = item
    url = {"github_repositories": "https://api.github.com/search/repositories", "github_issues": "https://api.github.com/search/issues", "yahoo": "https://search.yahoo.com/search"}[provider]
    params = {"p": query} if provider == "yahoo" else {"q": query, "per_page": 100}
    result = {"provider": provider, "query": query}
    try:
        r = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=28)
        r.encoding = "utf-8"
        result.update({"status": r.status_code, "url": r.url})
        if r.status_code != 200:
            return result
        if provider.startswith("github"):
            data = r.json()
            result["total_count"] = data.get("total_count")
            result["items"] = [{k: clean(x.get(k)) for k in (["full_name", "html_url", "description", "default_branch"] if provider == "github_repositories" else ["title", "html_url", "body", "repository_url"])} for x in data.get("items", [])]
            for x in result["items"]:
                if "body" in x: x["body"] = x["body"][:2500]
        else:
            soup = BeautifulSoup(r.text, "html.parser")
            items = []
            for el in soup.select(".algo"):
                a = el.select_one("h3 a") or el.select_one("a[href]")
                if not a: continue
                href = a["href"]
                match = re.search(r"/RU=([^/]+)/RK=", href)
                if match: href = unquote(match.group(1))
                items.append({"url": href, "text": clean(el.get_text(" ", strip=True))[:1300]})
            result["items"] = items
        return result
    except requests.RequestException as e:
        result["error"] = type(e).__name__
        return result


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(fetch, QUERIES))
    (BASE / "github_ssp_agent_round4_search.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for r in results:
        print(json.dumps(r, ensure_ascii=False))
