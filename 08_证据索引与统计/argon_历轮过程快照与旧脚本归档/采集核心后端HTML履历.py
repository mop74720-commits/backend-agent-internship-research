"""保留公开作者履历全部专业模块；删除联系区、站点前置元数据。"""
from pathlib import Path
import hashlib
import html
import json
import re
import warnings

import markdown
import requests
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
SHA = "bdd665acc8d73c80aefc7260fdeeef598fabf48f"
SOURCE = f"https://raw.githubusercontent.com/zhh2001/zhh2001.github.io/{SHA}/docs/resume.md"
S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0"


def main():
    response = S.get(SOURCE, timeout=45)
    response.raise_for_status()
    raw = response.text
    professional_body = raw[raw.index("# 张恒华"):]
    lines = professional_body.splitlines()
    remove = re.compile(r"邮箱|电话|微信|mailto:|tel:|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", re.I)
    removed_lines = sum(bool(remove.search(x)) for x in lines)
    clean = "\n".join(x for x in lines if not remove.search(x))
    # VitePress静态标签转为纯文字，保留原有专业内容。
    clean = re.sub(r'<Badge\b[^>]*\btext="([^"]*)"[^>]*/>', r"（\1）", clean)
    assert not remove.search(clean)
    assert not re.search(r"(?<!\d)1[3-9]\d{9}(?!\d)|\+\d[\d ()*-]{8,}\d", clean)
    folder = ROOT / "03_简历与候选人案例/核心后端履历_脱敏副本"
    folder.mkdir(parents=True, exist_ok=True)
    mdpath = folder / "zhh2001_公开HTML履历_脱敏转录.md"
    htmlpath = folder / "zhh2001_公开HTML履历_脱敏副本.html"
    note = (
        "这是作者完整公开HTML履历的整理者脱敏转录，保留原文件已有的全部专业模块；"
        "删除邮箱、电话、站点前置结构化联系元数据。不是企业核验结果，也不是求职时投递版本证明。"
        "莉莉丝Golang后端和简文投资全栈经历属于近期实习；网易2026年岗位是游戏客户端。"
        "原稿仅列项目名称、角色、主体与时间，缺少具体职责、技术难点及开源源码，不能补写。"
    )
    source_note = f"整理日期：2026-10-23\n\n{note}\n\n原页：https://zhh2001.github.io/resume\n\n固定版本：{SOURCE}\n\n---\n\n"
    mdpath.write_text(source_note + clean, encoding="utf-8")
    body = markdown.markdown(clean, extensions=["extra"])
    page = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>zhh2001公开HTML履历：脱敏副本</title><style>body{{font:17px/1.8 system-ui,"Microsoft YaHei",sans-serif;color:#172536;background:#f4f6f8;margin:0}}main{{max-width:940px;margin:30px auto;padding:30px;background:white;border-radius:12px}}h1,h2{{line-height:1.4}}h2{{border-bottom:1px solid #ccd5e0;padding-bottom:8px;margin-top:32px}}a{{color:#165cb5;overflow-wrap:anywhere}}aside{{background:#edf4ff;padding:18px;border-left:4px solid #547ca9}}p,li{{overflow-wrap:anywhere}}@media(max-width:600px){{main{{margin:0;padding:20px}}}}@media print{{body{{background:white}}main{{margin:0;max-width:none;padding:0}}a{{text-decoration:none;color:inherit}}}}</style><main><aside><strong>公开履历脱敏副本</strong><p>{html.escape(note)}</p><p><a href="https://zhh2001.github.io/resume">作者原页</a> · <a href="{SOURCE}">固定版本源文件</a> · 整理日期：2026-10-23</p></aside><article>{body}</article></main></html>'''
    htmlpath.write_text(page, encoding="utf-8")
    headings = re.findall(r"^## (.+)$", clean, re.M)
    expected = ["教育背景", "科研成果", "学术服务", "实习经历", "获奖情况", "技能证书", "项目经历"]
    assert headings == expected
    display_text = BeautifulSoup(page, "html.parser").get_text(" ", strip=True)
    # 提示语可含“邮箱、电话”字样；真实地址/号码不应残留。
    assert not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?<!\d)1[3-9]\d{9}(?!\d)|\+\d[\d ()*-]{8,}\d", display_text)
    row = {
        "key": "zhh2001", "author": "张恒华 / Henghua Zhang", "track": "后端", "recruitment": "实习",
        "recent_status": "近期确认（作者明确起止时间，自述未企业核验）",
        "url": "https://zhh2001.github.io/resume", "source_url": SOURCE,
        "repo": "zhh2001/zhh2001.github.io", "sha": SHA,
        "commit_date": "2026-10-22T09:31:51Z", "source_status": 200,
        "original_sha256": hashlib.sha256(response.content).hexdigest(), "original_saved": False,
        "profile_type": "完整公开HTML履历的脱敏专业模块副本", "is_full_public_profile": True,
        "complete_as_published": True, "all_original_professional_modules_preserved": headings,
        "local_html": htmlpath.relative_to(ROOT).as_posix(), "local_markdown": mdpath.relative_to(ROOT).as_posix(),
        "redacted_html_sha256": hashlib.sha256(htmlpath.read_bytes()).hexdigest(),
        "redacted_markdown_sha256": hashlib.sha256(mdpath.read_bytes()).hexdigest(),
        "redaction": {"removed_contact_lines": removed_lines, "removed_frontmatter": True, "email_phone_pattern_after": False, "external_images": 0, "visual_review": "待浏览器核对"},
        "outcomes": [
            {"company": "莉莉丝游戏", "role": "Golang后端实习", "time": "2026.03–2026.06", "grade": "未披露", "basis": "原稿实习经历与项目经历共同直接列出", "project": "LiLAC本地化平台", "evidence_url": SOURCE},
            {"company": "上海简文私募基金", "role": "Golang全栈实习", "time": "2025.09–2026.03", "grade": "未披露", "basis": "原稿实习经历直接列出；项目列LC-Event、LC-SBL及分析工具", "evidence_url": SOURCE},
            {"company": "网易游戏", "role": "游戏客户端实习", "time": "2026.09–至今", "grade": "未披露", "basis": "原稿直接列出，非后端/Agent，不计对应成功样本", "evidence_url": SOURCE},
        ],
        "projects": [
            {"name": "LiLAC本地化平台", "time": "2026.03–2026.06", "role": "Golang后端工程师", "owner": "莉莉丝游戏", "relation": "履历直接点名实习公司与本人角色", "source_code": None, "read_scope": "项目名称/时间/角色，不含实现细节", "contribution_verified": False},
            {"name": "LC-Event交易平台", "time": "2025.09–2026.03", "role": "Golang全栈工程师", "owner": "简文投资", "relation": "履历直接点名公司和本人角色", "source_code": None, "read_scope": "项目名称/时间/角色，不含实现细节", "contribution_verified": False},
            {"name": "LC-SBL海外借券", "time": "2025.09–2026.03", "role": "Python后端工程师", "owner": "简文投资", "relation": "履历直接点名公司和本人角色", "source_code": None, "read_scope": "项目名称/时间/角色，不含实现细节", "contribution_verified": False},
        ],
        "enterprise_verified": False, "ssp_confirmed": False, "interview_material": None,
        "reading": "固定源文件全部专业模块与公开HTML正文核读",
        "recommendation": "可精读时间线与项目主体/角色的对应；无法从本材料分析项目实现深度。作为Go后端成功实习真实履历样本，比模板或仅offer自述更直接，但不能当作项目技术栈充分样本。",
        "limitations": ["原稿技术技能主要列证书，没有详细技术栈能力分级", "项目仅名称、角色和时间，没有职责与结果", "企业项目未公开源码", "无本人面经", "无SSP档位", "不是求职投递当时版本证明"],
    }
    p = ROOT / "08_证据索引与统计/目标执行_近期履历发现.json"
    data = json.loads(p.read_text("utf-8"))
    data["new_core_complete_profiles"] = [row]
    data["counts"]["new_core_complete_public_html_profiles"] = 1
    data["counts"]["new_core_complete_resume_files"] = 1
    data["remaining_gap"] = "已取得1份近期Go后端成功实习者完整公开HTML履历脱敏副本，但缺详细项目职责、源码和本人面经；核心Agent应用工程完整成功履历及SSP链仍待补。研究/Infra 3份PDF单列。"
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"new_profile": row["key"], "professional_modules": headings, "removed_contact_lines": removed_lines, "html": str(htmlpath), "counts": data["counts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
