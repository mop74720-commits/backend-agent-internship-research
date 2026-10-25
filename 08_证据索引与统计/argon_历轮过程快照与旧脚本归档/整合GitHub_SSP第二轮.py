"""合并第二轮公开检索证据，保留历史报告；不运行第三方项目。"""
from pathlib import Path
from html import escape
from collections import Counter
import ast
import csv
import io
import json
import re

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "08_证据索引与统计"
REPORT = ROOT / "01_调研报告"
TITLE = "GitHub_SSP第二轮补充"

if (INDEX / "GitHub_SSP第三轮统计.json").exists():
    raise SystemExit("已有第三轮交付；停止旧整合脚本，避免覆盖最新目录与统计。")


def read(path):
    return path.read_text(encoding="utf-8-sig")


def write(path, text):
    newline = "\r\n" if not path.exists() or b"\r\n" in path.read_bytes() else "\n"
    with path.open("w", encoding="utf-8", newline="") as stream:
        stream.write(text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", newline))


def load(name):
    return json.loads(read(INDEX / name))


def dump(name, data):
    write(INDEX / name, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def merge(old, added):
    records = {r["id"]: r for r in old}
    records.update({r["id"]: r for r in added})
    return list(records.values())


backend = load("github_ssp_backend_round2_discovery.json")
systems = load("github_ssp_systems_round2_discovery.json")
agent = load("github_ssp_agent_round2_discovery.json")
root_source = load("github_ssp_round2_root_discovery.json")
mio, little = backend["candidate_records"]
cyc = systems["new_candidates"][0]
gui = agent["new_candidates"][0]
recent = root_source["recent_cross_platform_reference"]

candidate_new = [
    {"id": "CV14", "title": "mio4：历史Java后端SP/SSP自述、本人实习面经与综合笔记", "url": mio["ssp_evidence"]["url"],
     "author": "mio4", "date": mio["batch"]["literal"], "role": mio["scope"],
     "outcome": mio["status"], "evidence_excerpt": mio["ssp_evidence"]["quote"],
     "outcome_evidence": mio["ssp_evidence"]["company_boundary"],
     "document_type": "本人校招复盘与综合笔记；非完整简历或逐轮SSP原稿",
     "stack": ["Java", "JVM", "Spring", "MySQL", "Redis", "RabbitMQ", "操作系统", "网络"],
     "projects": ["作者选择课程项目复现，未确认个人求职业务成品仓库；不能将学习笔记算原创生产系统"],
     "project_relationship": mio["project_relationship"], "source_findings": mio["supporting_sources"], "supporting_url": mio["interview_relationship"]["specific_company_link"]["canonical_url"],
     "strengths": ["从原作者历史版本核到SSP声明，不把fork当新成功者", "本人明确链接面试笔记，可按基础和实习章节拆读"],
     "recommended_use": mio["recommended_reason"], "limitations": mio["limitations"],
     "confidence": "B：本人公开自述；公司与档位未逐家对应，未获企业核验"},
    {"id": "CV15", "title": cyc["title"], "url": cyc["ssp_source"]["url"], "author": "CyC2018", "date": cyc["year_and_role"],
     "role": "历史Java/后台研发；另有图形学科研与网易游戏实习", "outcome": "本人明确头条后台SSP、腾讯SP；不互换档位",
     "evidence_excerpt": cyc["ssp_source"]["short_excerpt"], "document_type": "本人年度复盘＋可读公开HTML履历页；未打包完整CV原件",
     "stack": ["Java", "Spring", "MySQL主从", "Redis", "Feed流", "并发与网络", "实习项目优化"],
     "projects": ["微博系统：本人记录PHP实现后改Java/Spring；履历说明主从读写分离、热点缓存和Feed流", "CS-Notes及Markdown转换工具", "网易游戏场景破坏重建实习：图形学邻近材料"],
     "public_html_profile": {k: cyc["public_html_profile"][k] for k in ["public_url", "source_url", "commit", "commit_date", "document_type", "read_scope", "education_boundary", "privacy_and_packaging"]},
     "project_relationship": [{"name": p["name"], "relationship": p["relationship"], "source_status": p.get("current_source_status", p.get("source_status", "见原始核验记录")), "recommended_use": p.get("recommended_lessons", []), "limitations": p.get("limits", [])} for p in cyc["project_associations"]],
     "source_findings": [cyc["ssp_source"], cyc["ssp_detail_source"], cyc["public_html_profile"]["author_link_evidence"]],
     "strengths": cyc["strengths"], "recommended_use": cyc["recommendation"], "limitations": cyc["limitations"],
     "confidence": "B：同作者SSP、面经、项目与履历页面关系清楚；仍是自述"},
    {"id": "CV16", "title": "LittleChild：地平线SSP与本人多轮面经，属自动驾驶算法邻近参考", "url": little["ssp_evidence"]["url"],
     "author": "LittleChild", "date": little["batch"], "role": "历史SLAM/自动驾驶/视觉算法；非Java后端或Agent工程",
     "outcome": "自述地平线SSP，拒绝后选小马智行；小马原文为算法普通档", "evidence_excerpt": little["ssp_evidence"]["quote"],
     "document_type": "本人秋招多公司多轮回忆；非完整简历", "stack": ["C++", "SLAM", "3D视觉", "自动驾驶感知", "算法"],
     "projects": little["project_relationship"]["article_project_mentions"], "project_relationship": little["project_relationship"],
     "source_findings": [little["ssp_evidence"], little["interview_relationship"]["role_evidence"]],
     "strengths": ["SSP公司与同段轮次结果可定位", "同文区分不同公司的档位，保留拒绝与接受选择"],
     "recommended_use": little["recommended_reason"], "limitations": little["limitations"], "confidence": "B：本人历史回忆；项目源码关系未闭环"},
    {"id": "CV17", "title": "码间烟火录：25届Java多家SSP复盘，尚未找到本人代码仓库", "url": recent["urls"][0],
     "supporting_urls": recent["urls"][1:], "author": recent["author"], "date": recent["date"], "role": recent["role"],
     "outcome": recent["outcome_boundary"], "evidence_excerpt": recent["ssp_excerpt"],
     "document_type": "跨站本人学习与求职复盘；不计新确认GitHub成功作者", "stack": recent["stack"],
     "projects": [recent["projects"]], "source_summary": recent["github_identity_or_project_repo"],
     "strengths": ["2024年两段实习到25届秋招的时间线较清楚", "具体讨论锁超时、补偿、指标及项目不足"],
     "recommended_use": recent["recommended_use"], "limitations": recent["limitations"], "access_level": recent["read_range"],
     "confidence": "B：正文已读，结果自述；本人仓库、完整CV和逐轮题目未确认"},
]
for r in candidate_new:
    r.update({"category": "候选人资料", "retrieved_at": "2026-10-23"})

interview_new = [
    {"id": "INT59", "title": "mio4：四家公司本人实习面经与综合面试笔记", "url": mio["interview_relationship"]["specific_company_link"]["canonical_url"],
     "supporting_url": mio["interview_relationship"]["same_account_notes"]["url"],
     "company": "头条测开／搜狐后端／美团后端／百度云；不是SSP公司专属轮次", "role": mio["scope"], "date": mio["batch"]["literal"],
     "outcome": "作者总体SP/SSP自述明确，未逐题对应公司或档位", "candidate_group": "CV14_mio4",
     "sample_group": "历史本人实习多公司复盘＋综合笔记", "role_boundary": "牛客原文四家公司分别记录；综合笔记含知识汇编；头条是测开，百度段不列具体题目；不将所有结果算SSP",
     "topics": ["Java", "JVM", "操作系统", "网络", "SQL", "Spring", "Redis", "RabbitMQ", "实习复盘"],
     "project_questions": ["微博点赞MySQL表设计", "美团轮次项目细节与@Autowired底层实现"], "rounds": mio["interview_relationship"]["specific_company_link"]["interview_summary"], "source_findings": mio["interview_relationship"]["same_account_notes"],
     "access_level": "牛客本人实习面经正文实际已读；7068行综合文件完整取得，核读目录与指定章节，未逐条审定全部技术答案。此组合记录不标全部材料逐行已读。", "fulltext_verified": False,
     "recommended_use": "先读牛客分公司问题与不同结果，再看笔记L6633起实习总结；百度只保留作者写出的主题，不移植别家具体题目。",
     "limitations": [mio["interview_relationship"]["counting_boundary"], mio["interview_relationship"]["specific_company_link"]["access"]]},
    {"id": "INT60", "title": "CyC2018：从项目太浅的失败到头条SSP的本人多轮复盘", "url": cyc["ssp_source"]["url"],
     "company": "阿里／腾讯／虎牙／头条等；SSP仅头条明确", "role": "历史后台研发", "date": "2018春招与秋招，固定正文2018-12-31",
     "outcome": "头条后台SSP、腾讯SP；不推定其他公司档位", "candidate_group": "CV15_CyC2018",
     "sample_group": "历史同作者春招与秋招多轮汇总", "role_boundary": cyc["interview_attribution"],
     "topics": ["项目深挖", "微博Feed流", "线程安全", "ThreadLocal", "ConcurrentHashMap", "限流边界", "SQL索引", "Paxos", "网络ET/LT", "算法", "实习优化"],
     "project_questions": ["项目为何太浅，如何从微博时间线继续追问？", "实习项目和开源博客的个人贡献如何讲清？", "头条加面项目问题与SQL执行/索引如何定位？"],
     "rounds": cyc["personal_interview_sources"], "access_level": "固定历史求职复盘原文已读；保留6段定位，不计6个独立成功者", "fulltext_verified": True,
     "recommended_use": "优先读L33–51的失败与项目问题、L73–79改进，再读L115–117头条结果，避免只看成功结论。", "limitations": cyc["limitations"]},
    {"id": "INT61", "title": "LittleChild：地平线SSP与小马普通档的同作者面经对照", "url": little["ssp_evidence"]["url"],
     "company": "地平线／小马智行等", "role": "SLAM/自动驾驶算法邻近参考", "date": little["batch"]["literal"],
     "outcome": "地平线SSP、小马普通档，均自述", "candidate_group": "CV16_LittleChild", "sample_group": "历史算法多公司本人汇总",
     "role_boundary": "不纳入后端或Agent工程成功者；同账号fork不等于求职原创项目",
     "topics": ["项目与实习深挖", "C++", "SLAM", "max pooling", "背包", "概率", "算法"],
     "project_questions": little["interview_relationship"]["horizon_rounds"]["questions_reported"] + little["interview_relationship"]["pony_rounds"]["questions_reported"],
     "rounds": [little["interview_relationship"]["horizon_rounds"], little["interview_relationship"]["pony_rounds"]],
     "access_level": "固定README262行完整取得并核读结果上下文", "fulltext_verified": True,
     "recommended_use": little["recommended_reason"], "limitations": little["limitations"]},
    {"id": "INT62", "title": "25届Java SSP作者：锁超时、异步补偿与项目指标的追问复盘", "url": recent["urls"][2],
     "supporting_url": recent["urls"][0], "company": "多家Java研发求职总结；不逐轮归公司", "role": recent["role"], "date": recent["date"],
     "outcome": recent["outcome_boundary"], "candidate_group": "CV17_码间烟火录", "sample_group": "近期跨站求职与项目主题复盘（非逐轮）",
     "role_boundary": recent["topic_boundary"], "topics": ["Redis锁", "锁超时", "看门狗", "Kafka", "库存", "MQ补偿", "XXL-JOB", "QPS", "项目取舍", "实习经历"],
     "project_questions": recent["project_interview_topics"], "access_level": recent["read_range"], "fulltext_verified": True,
     "recommended_use": "对照项目为什么这样做、故障后怎样恢复及指标从哪里来；不是现成逐公司考题清单。", "limitations": recent["limitations"]},
]
for r in interview_new:
    r.update({"category": "面经复盘", "retrieved_at": "2026-10-23", "confidence": "B：本人公开记录；未经企业独立核验，阅读范围单列"})

observations = [{"id": "OBS04", "title": "GUI-Agent：2026竞赛项目获SSP面试卡，不能当SSP offer", "url": gui["fixed_source"]["url"],
                 "author": gui["public_account"], "date": gui["year_and_role"], "role": "GUI Agent竞赛工程；校招面试资格线索",
                 "outcome": gui["ssp_status"], "evidence_excerpt": gui["ssp_excerpt"], "project_relationship": gui["project_and_author_relation"],
                 "source_findings": gui["static_project_reading"], "verification_notes": gui["independent_verification"], "license_notes": gui["license_check"],
                 "recommended_use": "可以研究带状态的GUI操作循环及失败处理；已有源码可读，正式SSP录用和本人求职面经仍未确认。",
                 "confidence": gui["confidence"], "category": "候选人对照", "retrieved_at": "2026-10-23"}]
new_records = candidate_new + interview_new + observations
dump("github_ssp_round2_records.json", {"date": "2026-10-23", "cases_new": candidate_new, "interviews_new": interview_new, "observations_new": observations})
cases = load("candidate_cases.json")
cases.setdefault("pre_round2_counts", dict(cases["counts"]))
cases["cases"] = merge(cases["cases"], candidate_new)
cases["counts"]["curated_cases"] = len(cases["cases"])
cases["counts"]["successful_self_report_without_resume"] = cases["pre_round2_counts"]["successful_self_report_without_resume"] + 3
cases["counts"]["successful_public_html_profile_without_complete_cv"] = 1
cases["round2_scope"] = "新增3位GitHub SSP自述作者（2后台、1算法邻近）和1位跨站25届Java参考；可读公开HTML履历页1，获授权完整CV原件仍0。"
interviews = merge(load("interview_records.json"), interview_new)
all_records = merge(load("all_evidence_records.json"), new_records)
assert len(all_records) == len({r["id"] for r in all_records})
dump("candidate_cases.json", cases)
dump("interview_records.json", interviews)
dump("all_evidence_records.json", all_records)
manifest = json.loads(read(ROOT / "05_项目源码归档/SOURCE_MANIFEST.json"))
projects = load("project_recommendations.json")["projects"]
stats = {"date": "2026-10-23", "scope": "第二轮扩搜；不保证穷尽", "new_confirmed_github_ssp_self_report_authors": 3,
         "new_backend_authors": ["CV14", "CV15"], "new_adjacent_algorithm_author": "CV16", "new_cross_platform_java_reference": "CV17",
         "new_interview_records": 4, "new_interview_channel_counterexample": "OBS04", "public_html_profiles_read": 1,
         "complete_cv_originals_authorized_for_packaging": 0, "new_source_archives": 0,
         "recent_agent_ssp_offer_mature_personal_project_and_interview_chain_confirmed": 0,
         "totals": {"candidate_cases": len(cases["cases"]), "interview_material_records": len(interviews), "project_analysis": len(projects), "source_archives": len(manifest), "logical_evidence_records": len(all_records)},
         "category_counts": dict(Counter(r["category"] for r in all_records)),
         "boundary": "未检得不等于不存在；面试通道不是offer；同源多轮不是独立成功者；录用与贡献均自述。"}
dump("GitHub_SSP第二轮统计.json", stats)

# 只提取旧脚本的静态译名，不执行历史整合流程。
labels = {}
for node in ast.parse(read(INDEX / "整合增补资料.py")).body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "LABELS" for t in node.targets):
        labels = ast.literal_eval(node.value)
labels.update({"public_html_profile": "本人公开HTML履历页", "public_url": "公开页面", "source_url": "固定来源", "read_scope": "已读范围", "document_type": "材料形式", "education_boundary": "教育模块边界", "privacy_and_packaging": "归档范围", "project_relationship": "项目与作者关系", "name": "项目", "relationship": "作者关系", "source_status": "源码取得情况", "reading_scope": "已读范围", "quote": "短摘录", "type": "材料类型", "note_kind": "笔记类型", "selected_topic_locations": "选读章节", "topic": "主题", "start": "起始行", "jvm_start": "JVM起始行", "questions_reported": "作者记录的问题", "result": "自述结果", "company_boundary": "公司档位边界", "short_excerpt": "短摘录", "public_account": "公开账号", "description": "项目说明", "strength": "关联强度", "contribution_boundary": "原创贡献边界", "contribution_source": "贡献说明来源", "same_author_interview_material": "本人求职面经状态", "visible_strengths": "源码可见优点", "critical_limits": "源码与评测局限", "sources": "来源", "scope": "范围", "readme_claim": "README许可声明", "tree_observation": "文件树观察", "license_body_verified": "许可证正文已读", "boundary": "边界", "award": "获奖核验", "offer": "录用核验", "code": "代码核验", "explicit_year": "原文明示年份", "direction": "方向", "recruitment_type": "招聘路径", "unknowns": "未知信息", "repo_created_at_from_search_api": "仓库创建时间", "historical_repo_url": "历史仓库", "current_source_status": "当前源码状态", "article_project_mentions": "正文项目描述", "direct_project_repository_links_in_article": "正文项目源码关系", "same_account_observations": "同账号观察", "language": "语言", "fork": "是否fork", "archive_status": "归档状态", "verification_boundary": "验证范围"})


def value_html(value):
    if isinstance(value, list):
        return "<ul>" + "".join("<li>" + value_html(v) + "</li>" for v in value) + "</ul>"
    if isinstance(value, dict):
        return "<br>".join(escape(labels.get(k, k)) + "：" + value_html(v) for k, v in value.items())
    if isinstance(value, bool):
        return "是" if value else "否"
    text = str(value)
    if re.fullmatch(r"https?://[^\s]+", text):
        return '<a href="' + escape(text, quote=True) + '">' + escape(text) + '</a>'
    if text.endswith(".zip") and Path(text).name == text and (ROOT / "05_项目源码归档" / text).is_file():
        return '<a href="../05_项目源码归档/' + escape(text, quote=True) + '">' + escape(text) + '</a>'
    return escape(text).replace("\n", "<br>")


def card(r, opened=False):
    fields = ''.join('<div class="field"><b>' + escape(labels.get(k, k)) + '</b><div>' + value_html(v) + '</div></div>' for k, v in r.items() if k not in {"id", "title", "category", "retrieved_at", "retrieved_date"} and v not in (None, [], ""))
    return '<details class="card" id="' + r["id"] + '" data-category="' + escape(r.get("category", "")) + '"' + (' open' if opened else '') + '><summary><span class="tag">' + r["id"] + '</span> ' + escape(r["title"]) + '</summary>' + fields + '</details>'


for r in new_records:
    folder = "04_面经与专业观点" if r["id"].startswith("INT") else "03_简历与候选人案例"
    write(ROOT / folder / (r["id"] + ".txt"), r["id"] + " | " + r["title"] + "\n\n" + "\n\n".join(labels.get(k, k) + "：" + (json.dumps(v, ensure_ascii=False, indent=2) if isinstance(v, (list, dict)) else str(v)) for k, v in r.items() if k not in {"id", "title"}) + "\n")

# 继续更新全包主题索引；按值匹配，避免把字段名误计入主题。
def flatten(value):
    if isinstance(value, list): return " ".join(flatten(v) for v in value)
    if isinstance(value, dict): return " ".join(flatten(v) for v in value.values())
    return str(value)


topics = load("interview_topic_index.json")
for row in topics["themes"]:
    row["evidence_ids"] = [r["id"] for r in interviews if re.search(row["rule"], flatten([r.get("topics", []), r.get("project_questions", [])]), re.I)]
    row["record_count"] = len(row["evidence_ids"])
topics.update({"updated_at": "2026-10-23", "scope_records": len(interviews), "scope_note": "包含第二轮历史、算法邻近和跨站资料；旧报告表格为各自生成时快照。"})
dump("interview_topic_index.json", topics)
buf = io.StringIO(newline="")
writer = csv.writer(buf)
writer.writerow(["主题", "资料条数_非独立场次", "资料ID", "复核规则"])
for row in topics["themes"]: writer.writerow([row["theme"], row["record_count"], ";".join(row["evidence_ids"]), row["rule"]])
write(INDEX / "面经主题索引.csv", buf.getvalue())

previous = read(REPORT / "GitHub_SSP项目与面经专项.html")
css = re.search(r"<style>([\s\S]*?)</style>", previous).group(1)
html = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GitHub SSP第二轮：新增作者与未完成线索</title><style>' + css + '</style></head><body><header><p>2026-10-23 · 第二轮扩搜</p><h1>还有新案例，上一轮没有搜尽</h1><p>新增3位GitHub SSP自述作者：2位后台、1位算法邻近；另补1位25届Java跨站参考及1项Agent竞赛面试通道。来源能证明到哪一步，逐项标明。</p><p><a href="index.html">完整搜索目录</a> · <a href="GitHub_SSP项目与面经专项.html">上一轮专项</a> · <a href="' + TITLE + '.pdf">本报告PDF</a></p></header><main>'
html += '<section><h2>本轮新增，优先看哪些</h2><aside>不能确认全网没有更多。上一轮的“未找到”仅指当时访问到的资料；本轮已经找出新作者，并通过历史固定版本和真实正文容器补回失效入口。</aside><div class="tablewrap"><table><thead><tr><th>案例</th><th>核实到的材料</th><th>保留的边界</th></tr></thead><tbody>'
rows = [
    ("CV14", "mio4／Java", "本人SP/SSP自述＋四家实习面经＋综合笔记", "SSP具体公司、个人成品项目源码未确认；头条轮次是测开"),
    ("CV15", "CyC2018／后台", "头条SSP＋本人多轮面经＋本人公开HTML履历页", "腾讯为SP；微博当前源码404；2018历史案例"),
    ("CV16", "LittleChild／算法邻近", "地平线SSP与同文多轮面经", "SLAM/自动驾驶方向；小马为普通档；不算Java或Agent工程"),
    ("CV17", "码间烟火录／25届Java", "字节、快手、淘天、京东SSP自述＋项目追问复盘", "跨站参考；本人代码仓库未找到；美团为SP"),
    ("OBS04", "GUI-Agent／2026", "竞赛项目、状态与动作实现、SSP面试直通卡自述", "面试资格不是offer；无本人求职逐轮面经"),
]
for ident, name, finding, boundary in rows:
    html += '<tr><td><a href="#' + ident + '">' + ident + ' ' + name + '</a></td><td>' + finding + '</td><td>' + boundary + '</td></tr>'
html += '</tbody></table></div><p>本轮没有新增源码包。新发现的后台作者未提供当前可取得、可明确对应的个人求职业务成品源码；学习笔记、fork、比赛框架各自标注。</p></section>'
html += '<section><h2>这轮纠正了哪些遗漏</h2><ul><li>CyC2018：以前只读首页会得空壳；其首页跳到page.html，专业履历内容实际可读。历史本人原文也能从固定commit恢复。</li><li>mio4：当前README删减过旧自述，应查历史版本；fork只是发现线索，成功者归属回原作者。</li><li>牛客与掘金：旧正文选择器未命中不等于空页。25届Java复盘从实际正文容器取得，两篇正文已读。</li><li>SSP面试直通卡、薪资科普、冲SSP目标、课程宣传与他人面经，均不能算本人SSP offer。</li></ul><p>公开HTML履历页新增1份（缺教育模块）；获授权打包的完整CV原件仍为0。只保存专业模块归纳、短摘录和来源链接。</p></section>'
html += '<section><h2>新增作者分析</h2>' + ''.join(card(r, True) for r in candidate_new) + '</section>'
html += '<section><h2>面经与综合笔记的具体入口</h2>' + ''.join(card(r, True) for r in interview_new) + '</section>'
html += '<section><h2>Agent新线索：工程项目与招聘结果分开</h2>' + card(observations[0], True) + '</section>'
html += '<section><h2>覆盖范围与未完成线索</h2><p>本轮通过GitHub仓库检索、历史版本、本人博客/牛客/掘金交叉追源。根代理另记录48结果的仓库查询及选定README扫描；它们不覆盖全站、全部文件、私有项目或未公开经历。其他方向独立检索日志也保留。</p><p>近期Agent方向尚未建立“正式SSP offer＋成熟本人项目＋本人求职面经”的完整关联；这只表示尚未核实，不能下结论说不存在。</p><p>Azurer0121相关标题仍被索引，但精确raw和repo API404，原因未知；另有仅标题可见或原帖受限线索。可继续追，但不以搜索摘要补写经历。</p><p>核验记录：<a href="../08_证据索引与统计/github_ssp_backend_round2_discovery.json">后端</a> · <a href="../08_证据索引与统计/github_ssp_systems_round2_discovery.json">系统与履历</a> · <a href="../08_证据索引与统计/github_ssp_agent_round2_discovery.json">Agent</a> · <a href="../08_证据索引与统计/github_ssp_round2_root_discovery.json">跨站与访问纠正</a> · <a href="../08_证据索引与统计/GitHub_SSP第二轮统计.json">最新统计</a></p><p>所有录用、竞赛结果和个人贡献仍是作者自述；未构建、运行项目、调用模型或执行ADB。个人项目设计继续暂缓。</p></section></main><footer>公开来源与原创归纳 · 检索没有穷尽性保证 · 同作者多轮不作独立成功者</footer></body></html>'
write(REPORT / (TITLE + ".html"), html)

main_path = REPORT / "index.html"
main = read(main_path)
main = re.sub(r'<aside id="github-ssp-round2">[\s\S]*?</aside>', '', main)
banner = '<aside id="github-ssp-round2"><strong>第二轮又找到新案例：</strong>新增mio4、CyC2018、LittleChild三位GitHub SSP自述作者，另补25届Java跨站复盘。<a href="' + TITLE + '.html">查看新增证据</a> · <a href="' + TITLE + '.pdf">PDF</a>。当前共' + str(len(cases["cases"])) + '份候选人分析、' + str(len(interviews)) + '份面经资料。公开HTML履历页新增1份；完整CV原件未取得。检索未穷尽。</aside>'
main = main.replace('<article>', '<article>' + banner, 1)
main = re.sub(r'<div class="stats">[\s\S]*?</div>', '<div class="stats"><span><strong>19</strong>JD线索 / 14全文工程实习</span><span><strong>' + str(len(cases["cases"])) + '</strong>候选人材料 / 非完整CV原件</span><span><strong>' + str(len(interviews)) + '</strong>面经与复盘</span><span><strong>7</strong>B站/知乎资料</span><span><strong>' + str(len(manifest)) + '</strong>固定版本源码</span></div>', main, count=1)
intro = '<section id="s0"><h2>01 本轮阅读入口</h2><p>最新：<a href="' + TITLE + '.html">GitHub SSP第二轮补充</a>，优先看CV14、CV15及INT60；CV16为算法邻近，CV17为近期Java跨站参考，OBS04只是SSP面试通道。</p><p>此前报告继续保留为各轮快照。当前全包' + str(len(cases["cases"])) + '份候选人分析、' + str(len(interviews)) + '份面经资料、' + str(len(projects)) + '份项目分析、' + str(len(manifest)) + '个源码包。另有可读公开HTML履历页1份，缺教育模块；未获得可打包的完整CV原件。SSP均自述，近期Agent完整关联尚未核实，检索没有穷尽性保证。个人项目设计暂缓。</p></section>'
main = re.sub(r'<section id="s0">[\s\S]*?</section>', lambda _: intro, main, count=1)
categories = list(dict.fromkeys(r["category"] for r in all_records))
catalog = '<section id="evidence"><h2>15 可搜索资料目录</h2><p>新增CV14–17、INT59–62、OBS04；可按作者、技术点或编号搜索。同作者多轮、历史与算法邻近资料分别标注。</p><div class="tools"><input id="q" type="search" placeholder="例如：CyC2018、mio4、INT60、OBS04"><select id="category"><option>全部类别</option>' + ''.join('<option>' + escape(c) + '</option>' for c in categories) + '</select><button id="expand">展开匹配</button><button id="collapse">全部收起</button></div><p class="muted" id="count"></p>' + ''.join(card(r) for r in all_records) + '</section>'
main = re.sub(r'<section id="evidence">[\s\S]*?</section>', lambda _: catalog, main, count=1)
main = main.replace('本次SSP专项再补3份资料，现共51份面经资料', '第一轮SSP专项补3份，第二轮再补4份，现共55份面经资料')
main = main.replace('13份简历片段/履历分析，另有对照样本；非完整CV', '17份候选人分析，含公开HTML履历页与跨站参考；非完整CV原件')
main = main.replace('51份面经资料与7份B站/知乎资料卡', '55份面经资料与7份B站/知乎资料卡')
write(main_path, main)

# 上轮HTML保留其统计快照，新增后续入口；其PDF也保持当轮版本。
previous = re.sub(r'<aside id="round2-followup">[\s\S]*?</aside>', '', previous)
previous = previous.replace('<main>', '<main><aside id="round2-followup"><b>已有第二轮新增：</b><a href="' + TITLE + '.html">新增3位GitHub作者、25届Java参考与Agent面试卡线索</a>。以下为上一轮快照，最新全包统计见主目录。</aside>', 1)
write(REPORT / "GitHub_SSP项目与面经专项.html", previous)
write(ROOT / "00_START_HERE.txt", "大厂后端与Agent信息搜集包 | SSP第二轮更新 | 2026-10-23\n\n先看01_调研报告/" + TITLE + ".html或同名PDF。完整可搜索入口：01_调研报告/index.html。\n\n本轮新增3位GitHub SSP自述作者（mio4、CyC2018、LittleChild；后者为自动驾驶算法邻近），另有25届Java跨站复盘及GUI-Agent SSP面试通道对照。新增4份面经/综合笔记资料，没有新增源码包。\n全包：17份候选人分析、55份面经资料、17份项目分析、16个固定源码包。公开HTML履历页1份（缺教育模块），获授权完整CV原件0。\n\n不能保证搜尽；近期Agent正式SSP录用＋成熟本人项目＋本人面经尚未核实，不等于不存在。所有录用均作者自述，项目未运行。\n个人项目设计继续暂缓。旧报告为各轮快照，最新统计见08_证据索引与统计/GitHub_SSP第二轮统计.json。\n")
write(ROOT / "00_GitHub_SSP第二轮更新说明.md", "# GitHub SSP第二轮补充\n\n上一轮没有穷尽，本轮已确认新线索。\n\n- [第二轮报告](01_调研报告/" + TITLE + ".html)\n- [PDF](01_调研报告/" + TITLE + ".pdf)\n- [完整搜索目录](01_调研报告/index.html)\n- [最新统计与边界](08_证据索引与统计/GitHub_SSP第二轮统计.json)\n\n新增3位GitHub SSP作者、1位跨站近期Java参考、4份面经/综合笔记、1项Agent面试通道对照。无新增源码包。个人项目设计暂缓。\n")
method_path = INDEX / "source_methodology.txt"
method = read(method_path).split("\nGitHub SSP第二轮最新更新：")[0]
write(method_path, method.rstrip() + "\n\nGitHub SSP第二轮最新更新：\n" + json.dumps(stats, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(stats, ensure_ascii=False, indent=2))
