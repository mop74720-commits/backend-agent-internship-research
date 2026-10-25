"""按近期实习目标整理证据；不执行第三方项目，不把补搜数量当质量。"""
from collections import Counter
from copy import deepcopy
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl, urlencode, urlunsplit
import csv
import io
import json
import re

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "08_证据索引与统计"
TODAY = "2026-10-23"


def read(path):
    return path.read_text(encoding="utf-8-sig")


def write(path, text):
    newline = "\r\n" if not path.exists() or b"\r\n" in path.read_bytes() else "\n"
    with path.open("w", encoding="utf-8", newline="") as stream:
        stream.write(text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", newline))


def load(name):
    return json.loads(read(INDEX / name))


def dump(name, value):
    write(INDEX / name, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def flatten(value):
    if isinstance(value, dict): return " ".join(flatten(v) for v in value.values())
    if isinstance(value, list): return " ".join(flatten(v) for v in value)
    return str(value)


def merge(old, added):
    records = {x["id"]: x for x in old}
    records.update({x["id"]: x for x in added})
    return list(records.values())


def csv_write(path, headers, rows):
    buf = io.StringIO(newline="")
    writer = csv.writer(buf)
    writer.writerow(headers)
    for row in rows:
        # 外部标题不得在电子表格里成为公式。
        writer.writerow(["'" + str(v) if str(v).startswith(("=", "+", "-", "@")) else v for v in row])
    write(path, "\ufeff" + buf.getvalue())


def generic_taxonomy(record):
    title = record.get("title", "")
    agent = bool(re.search(r"Agent|RAG|LLM|LangGraph|MCP|工具|智能体|上下文", title, re.I))
    return {"track": "Agent工程" if agent else "后端" if record["id"].startswith("PRO") else "未知", "recruitment": "不适用", "experience_date_text": "非招聘事件；源码或原文版本日期另列", "date_precision": "不适用", "year_confirmed": False, "recent_status": "不适用", "date_basis": "不以技术文档/仓库日期替代个人求职时间", "source_date_text": record.get("commit_date", record.get("date", "未核"))}


def canonical(url):
    p = urlsplit(url)
    tracking = {"sourceSSR", "source_id", "toCommentId", "weFlow", "urlSource", "token", "lang", "chksm"}
    pairs = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if k not in tracking]
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), urlencode(sorted(pairs)), ""))


def integrate():
    if (INDEX / "目标执行统计.json").exists():
        raise SystemExit("目标执行补证版已存在，请使用整合目标执行.py；禁止用前轮数据覆盖新证据。")
    norm = load("统一样本分类与候选人关联.json")
    comparisons = load("项目统一比较与阅读优先级.json")
    professional = load("专业观点补核与缺口检索.json")
    coverage_gap = load("近期实习缺口核查结论.json")
    capabilities = load("能力要求四类证据对照.json")
    all_records = load("all_evidence_records.json")
    cases = load("candidate_cases.json")
    interviews = load("interview_records.json")
    projects = load("project_recommendations.json")
    backup = INDEX / "纠偏前主数据快照.json"
    if not backup.exists():
        write(backup, json.dumps({"date": TODAY, "candidate_cases": cases, "interview_records": interviews, "project_recommendations": projects, "all_evidence_records": all_records}, ensure_ascii=False, indent=2) + "\n")
    normalized = {r["id"]: r for rows in norm["records"].values() for r in rows}
    p_by_id = {r["id"]: r for r in comparisons["projects"]}
    for r in all_records:
        n = normalized.get(r["id"])
        if n:
            r["taxonomy"] = n["taxonomy"]
            r["reading"] = n["reading"]
            r["outcomes"] = n["outcomes"]
            if r["id"].startswith(("CV", "INT")):
                r["date"] = n["taxonomy"]["experience_date_text"]
                r["source_date"] = n["taxonomy"]["source_date_text"]
            if r["id"].startswith("CV"):
                for key in ["profile_type", "chain", "chain_gaps", "has_confirmed_personal_interview_source", "has_direct_named_project_or_contribution", "ssp_grade_company_explicit", "ssp_claim_present"]:
                    r[key] = n[key]
            if r["id"].startswith("INT"):
                for key in ["material_type", "candidate_link_ids", "strict_recent_internship", "publication_recent_event_year_unknown", "result_status", "related_record_ids"]:
                    r[key] = n[key]
                group = n["taxonomy"]["recruitment"]
                r["sample_group"] = {"实习": "明确实习面经", "校招": "校招资料（单列）", "混合": "混合批次或多公司汇总（单列）", "未知": "招聘类型未确认（单列）"}.get(group, group)
                r["fulltext_verified"] = n["reading"]["fulltext"]
        else:
            r["taxonomy"] = generic_taxonomy(r)
            r["reading"] = {"scope": "部分" if r["id"].startswith("PRO") else "资料索引", "fulltext": False, "scope_note": "按原卡具体核读范围；不视为项目已运行或全部源码逐行核读", "video_watched": False}
            r["outcomes"] = []
        if r["id"] in p_by_id:
            r["comparison"] = p_by_id[r["id"]]
            r["backend_priority"] = p_by_id[r["id"]]["backend_priority"]
            r["agent_priority"] = p_by_id[r["id"]]["agent_priority"]
            r["attachment_status"] = p_by_id[r["id"]]["attachment"]
    by_id = {r["id"]: r for r in all_records}
    cv05 = by_id["CV05"]
    cv05["weaknesses"] = ["已核2022年两项测试PR，其余贡献未逐条审计" if "没有本轮逐条核验PR归属" in x else x for x in cv05.get("weaknesses", [])]
    cv05["weaknesses"] = [x.replace("历史校招与当前Agent工作必须分开", "历史录用与当前Agent方向更新必须分开") for x in cv05.get("weaknesses", [])]
    for ident in ["INT21", "INT23", "INT30"]:
        by_id[ident]["date_certainty"] = "正文仅月日或年份未明确；不依据届别、页面当前展示或抓取日期推定事件年份。"
    pro09 = by_id["PRO09"]
    for link in pro09.get("candidate_links", []):
        if isinstance(link, dict) and link.get("id", link.get("candidate_id")) == "CV05":
            link["relation"] = "已核erdengk的PR3848、3672在2022年合并并静态读两测试文件；其余PR和模块归属未审。"
    for key in ["weaknesses", "limitations"]:
        if key in pro09:
            pro09[key] = [x.replace("未逐条审计其 PR 和模块归属", "已核两项2022年测试PR，未逐条审计其余PR和模块归属") for x in pro09[key]]
    comp09 = p_by_id["PRO09"]
    comp09["limitations"] = [x.replace("未逐条审计其 PR 和模块归属", "已核两项2022年测试PR，未逐条审计其余PR和模块归属") for x in comp09["limitations"]]
    pro09["comparison"] = comp09
    pro09["extend"] = "先读已核PR3848、3672及历史测试断言局限，其余贡献待核；当前网关整体不算个人实现。"
    historical_modules = [v for pr in pro09.get("verified_contributions", []) for v in [pr["url"], pr["code_url"]]]
    comp09["backend_priority"]["read_modules"] = list(dict.fromkeys(historical_modules + comp09["backend_priority"]["read_modules"]))
    pro09["backend_priority"] = comp09["backend_priority"]
    p_by_id["PRO10"]["source_nature"] = ["本人开源贡献自述（具体PR待核）" if x == "本人开源贡献" else x for x in p_by_id["PRO10"]["source_nature"]]

    # 原平台缺口与作者官网替代阅读分别保存。
    for update in professional["existing_record_updates"]:
        r = by_id[update["id"]]
        r["latest_access_review"] = update
        r["content_validation"] = update["content_validation"]
        r["verified_video_viewing"] = False
        if update.get("discrepancy"):
            r["source_discrepancy"] = update["discrepancy"]
    new_primary = []
    for offset, original in enumerate(professional["proposed_native_opinion_sources"], 8):
        r = deepcopy(original)
        r.pop("proposed_key", None)
        r.update({"id": f"OP{offset:02}", "category": "专业原文补充", "taxonomy": {"track": "Agent工程", "recruitment": "不适用", "experience_date_text": "专业原文发表/更新日期，非招聘事件", "date_precision": "不适用", "year_confirmed": False, "recent_status": "不适用", "date_basis": "不把作者工程观点当招聘结果", "source_date_text": original.get("date", "未核")}, "reading": {"scope": "全文", "fulltext": True, "scope_note": "作者官方原站实际正文；平台外原文，不是B站观看或知乎本体阅读", "video_watched": False}, "outcomes": []})
        new_primary.append(r)
    all_records = merge(all_records, new_primary)
    by_id = {r["id"]: r for r in all_records}
    cases["cases"] = [by_id[x["id"]] for x in cases["cases"]]
    cases.setdefault("pre_requirement_audit_counts", deepcopy(cases["counts"]))
    cases["counts"] = {"curated_cases": len(cases["cases"]), **norm["statistics"]["candidates"]}
    cases["scope"] = "近期后端与Agent工程实习优先；历史SSP、实习转正、邻近算法与未知批次单列，分析卡不冒充简历原件。"
    cases["requirements_audit_date"] = TODAY
    interviews = [by_id[x["id"]] for x in interviews]
    projects["projects"] = [by_id[x["id"]] for x in projects["projects"]]
    projects["requirements_audit_scope"] = "19项目全部统一比较；16份源码ZIP、3份固定链接，阅读优先级与证据完整度分开；未运行。"
    dump("all_evidence_records.json", all_records)
    dump("candidate_cases.json", cases)
    dump("interview_records.json", interviews)
    dump("project_recommendations.json", projects)
    dump("项目统一比较与阅读优先级.json", comparisons)

    # 频数只作为本资料包索引，分组计算，不是市场概率。
    topics = load("interview_topic_index.json")
    for row in topics["themes"]:
        matching = [r for r in interviews if re.search(row["rule"], flatten([r.get("topics", []), r.get("project_questions", [])]), re.I)]
        row["evidence_ids"] = [r["id"] for r in matching]
        row["record_count"] = len(matching)
        row["explicit_internship_ids"] = [r["id"] for r in matching if r["taxonomy"]["recruitment"] == "实习"]
        row["strict_recent_internship_ids"] = [r["id"] for r in matching if r.get("strict_recent_internship")]
        row["year_unknown_internship_ids"] = [r["id"] for r in matching if r["taxonomy"]["recruitment"] == "实习" and not r["taxonomy"]["year_confirmed"]]
    topics.update({"updated_at": TODAY, "scope_records": len(interviews), "scope_note": "全包、明确实习、严格近期、年份未知分别列。每资料每主题一次，不等于独立候选人数或行业概率。"})
    dump("interview_topic_index.json", topics)
    csv_write(INDEX / "面经主题索引.csv", ["主题", "全包资料数", "明确实习资料数", "严格近期实习资料数", "实习事件年未知资料数", "全包资料ID", "严格近期ID"], [[x["theme"], x["record_count"], len(x["explicit_internship_ids"]), len(x["strict_recent_internship_ids"]), len(x["year_unknown_internship_ids"]), ";".join(x["evidence_ids"]), ";".join(x["strict_recent_internship_ids"])] for x in topics["themes"]])
    for row in capabilities["rows"]:
        row["support"] = {}
        for group in ["jd", "interview", "candidate", "opinion", "project"]:
            row["support"][group] = [{"id": key, "title": by_id[key]["title"], "url": by_id[key].get("url", ""), "taxonomy": by_id[key]["taxonomy"], "reading_scope": by_id[key]["reading"]["scope"]} for key in row.get(group + "_ids", [])]
    dump("能力要求四类证据对照.json", capabilities)

    # 待核链接保留实际状态；只去除跟踪参数，不丢失公众号文章标识。
    blocked = load("待手动访问链接.json")
    extra = []
    for x in professional["manual_access_links"]:
        title = by_id[x["related_id"]]["title"]
        extra.append({"title": x["related_id"] + " " + title, "url": x["url"], "status": x["status"], "to_verify": [x["check"]]})
    for ident in ["OP02", "OP05"]:
        r = by_id[ident]
        extra.append({"title": ident + " " + r["title"], "url": r["url"], "status": r["latest_access_review"]["access_status"], "to_verify": ["原平台实际内容与作者身份；作者官网替代不计原平台阅读"]})
    extra += [
        {"title": "后端开发实习简历五次迭代（原帖待核）", "url": "https://blog.csdn.net/m0_45362454/article/details/144808692", "status": "本轮HTTP521，未得正文", "to_verify": ["是否本人成功实习简历、具体事件时间、原始履历与项目；不按搜索摘要还原"]},
        {"title": "CV07 等闲king履历：当前原帖不稳定", "url": by_id["CV07"]["url"], "status": "先前读过正文；本轮目标文章未得，主容器仅外围热榜，不计新的正文核验", "to_verify": ["原始正文、本人项目及社区贡献、正式录用与实习时间"]},
        {"title": "CV09 腾讯后台实习本人面经：当前访问空壳", "url": "https://www.nowcoder.com/feed/main/detail/9ecd5997a7d74f3fa885695032f32065", "status": "先前已读；本轮HTTP200标题空壳，不取消先前阅读事实，也不补写本人源码", "to_verify": ["本人履历与项目仓库是否有公开后续补充"]},
    ]
    pending = {canonical(x["url"]): x for x in blocked}
    pending.update({canonical(x["url"]): x for x in extra})
    blocked = list(pending.values())
    dump("待手动访问链接.json", blocked)

    # 推荐的是阅读目标与模块，不给个人项目定题或设计。
    backend_interviews = ["INT10", "INT12", "INT20", "INT22", "INT24", "INT28", "INT07", "INT09", "INT11", "INT66"]
    agent_interviews = ["INT42", "INT47", "INT01", "INT02", "INT40", "INT41", "INT54", "INT55", "INT67"]
    reading_order = {"principle": "严格近期先看；缺年份但明确实习者保留高相关选读并提示时间。历史SSP用于具体模块与贡献表达，不能当当前门槛。", "backend": {"interview_ids": backend_interviews, "candidate_ids": ["CV09", "CV04", "CV21", "CV02", "CV18"], "candidate_boundary": "CV09近期明确实习；CV04为转正自述、事件年份未独立确认；其他为历史或时间未知专项对照。", "project_routes": comparisons["reading_routes"]["backend"]}, "agent": {"interview_ids": agent_interviews, "candidate_ids": ["CV08", "CV07", "CV09"], "candidate_boundary": "CV08混合应用/算法且年份未知；CV07不稳定且正式offer未证；CV09是后台与Agent交叉，不能填成纯Agent SSP成功者。", "project_routes": comparisons["reading_routes"]["agent"]}, "pending_professional_ids": ["OP01", "OP02", "OP03", "OP06", "OP07"], "read_professional_ids": ["OP04", "OP05", "OP08", "OP09"], "total_quality_score": None}
    dump("两方向阅读顺序.json", reading_order)

    coverage = {"schema_version": "1.0", "research_date": TODAY, "priority": "近期实习优先", "recent_window": norm["recent_window"], "totals": {"logical_evidence_records": len(all_records), "candidate_cases": len(cases["cases"]), "interview_materials": len(interviews), "projects": len(projects["projects"]), "source_archives": comparisons["counts"]["source_archives"], "fixed_link_only": comparisons["counts"]["fixed_link_only"], "jd_leads": len(norm["records"]["jobs"]), "engineering_jd_fulltext": norm["statistics"]["jobs"]["first_party_engineering_matrix_fulltext_count"], "platform_opinion_records": 7, "additional_primary_texts": len(new_primary), "manual_links": len(blocked)}, "candidate_coverage": norm["statistics"]["candidates"], "interview_coverage": norm["statistics"]["interviews"], "job_coverage": norm["statistics"]["jobs"], "opinion_coverage": {**norm["statistics"]["opinions"], "new_external_official_fulltexts": len(new_primary)}, "project_coverage": comparisons["counts"], "new_qualifying_internship_chains_this_pass": 0, "recent_agent_ssp_complete_chain_confirmed": 0, "new_complete_cv_files_this_pass": 0, "search_rounds_completed_per_gap": 2, "remaining_gaps": [coverage_gap["gap"], "B站实际观看/字幕0；知乎本体正文0，平台外原文不能抵扣此缺口", "19项目均未运行；源码/测试可见不等于效果复现"], "source_boundaries": norm["methodology"], "category_counts": dict(Counter(r["category"] for r in all_records))}
    coverage["source_boundaries"] = {**norm["methodology"], "scope": "统一分类子任务依据原有110条记录；本轮另有两路径补搜与主表整合，见检索日志及整合校验。分类子任务不执行源码，整合阶段更新主表。"}
    dump("需求覆盖统计.json", coverage)

    # 可直接在Excel/文本中查看的统一表格，不依赖网页脚本。
    csv_write(ROOT / "03_简历与候选人案例/候选人证据链对照.csv", ["ID", "标题", "方向", "招聘路径", "事件时间", "近期状态", "结果自述", "资料类型", "录用证据", "履历证据", "项目贡献证据", "本人面经", "缺口"], [[r["id"], r["title"], r["taxonomy"]["track"], r["taxonomy"]["recruitment"], r["taxonomy"]["experience_date_text"], r["taxonomy"]["recent_status"], r.get("outcome", ""), r["profile_type"], *[" | ".join((n.get("url") or "未建立") + "：" + n["direct_basis"] for n in r["chain"][k]) for k in ["outcome", "profile", "project", "interview"]], "；".join(r["chain_gaps"])] for r in cases["cases"]])
    csv_write(ROOT / "04_面经与专业观点/面经统一分类.csv", ["ID", "标题", "方向", "招聘路径", "实际时间", "发表日期另列", "事件年已证", "近期状态", "阅读范围", "资料类型", "结果", "来源"], [[r["id"], r["title"], r["taxonomy"]["track"], r["taxonomy"]["recruitment"], r["date"], r["source_date"], r["taxonomy"]["year_confirmed"], r["taxonomy"]["recent_status"], r["reading"]["scope"], r["material_type"], r.get("outcome", ""), r["url"]] for r in interviews])
    dim_rows = []
    for p in comparisons["projects"]:
        for group in ["backend", "agent"]:
            for dimension, value in p[group + "_dimensions"].items():
                dim_rows.append([p["id"], p["title"], "后端" if group == "backend" else "Agent", dimension, value["status"], value["finding"], value["source_URL"], ";".join(value["read_paths"]), p[group + "_priority"]["level"], p[group + "_priority"]["reason"], p["attachment"]["status"], p["run_status"]])
    csv_write(ROOT / "06_项目分析与推荐/19项目统一比较.csv", ["ID", "项目", "方向", "维度", "证据状态", "具体发现", "来源", "阅读路径", "阅读级别", "理由", "附件", "运行范围"], dim_rows)
    cap_rows = [[x["ability"], x["backend_relevance"], x["agent_relevance"], ";".join(x["jd_ids"]), ";".join(x["interview_ids"]), ";".join(x["candidate_ids"]), ";".join(x["opinion_ids"]), x["question"], x["competency"], x["module"], x["common_pitfall"], x["gap"]] for x in capabilities["rows"]]
    csv_write(INDEX / "能力要求四类证据对照.csv", ["能力", "后端相关性", "Agent相关性", "JD", "面经", "履历", "专业原文", "提问", "考察能力", "项目模块主题映射", "研究归纳薄弱点", "缺口"], cap_rows)
    csv_write(INDEX / "全部资料统一分类.csv", ["ID", "类别", "标题", "方向", "招聘路径", "实际事件时间", "来源时间", "事件年已证", "近期状态", "阅读范围", "来源"], [[r["id"], r["category"], r["title"], r["taxonomy"]["track"], r["taxonomy"]["recruitment"], r["taxonomy"]["experience_date_text"], r["taxonomy"]["source_date_text"], r["taxonomy"]["year_confirmed"], r["taxonomy"]["recent_status"], r["reading"]["scope"], r.get("url", "")] for r in all_records])
    for direction, title in [("backend", "后端实习阅读顺序"), ("agent", "Agent实习阅读顺序")]:
        lines = ["# " + title, "", reading_order["principle"], "", "## 面经与履历", ""]
        for ident in reading_order[direction]["interview_ids"] + reading_order[direction]["candidate_ids"]:
            r = by_id[ident]
            lines += [f'- [{ident} {r["title"]}]({r["url"]})：{r["taxonomy"]["recruitment"]}／{r["taxonomy"]["recent_status"]}，{r["reading"]["scope"]}。', ""]
        lines += ["## 项目模块", ""]
        for p in comparisons["projects"]:
            q = p[direction + "_priority"]
            if q["level"] == "非本方向": continue
            lines += [f'- [{p["id"]} {p["title"]}]({p["source_URL"]})｜{q["level"]}：{q["reason"]}', "  阅读模块：" + "；".join(q["read_modules"]), "  边界：" + p["evidence_completeness"], ""]
        lines += ["个人项目设计暂缓。精读是模块阅读建议，不要求整仓复刻；所有项目未运行。", ""]
        write(ROOT / "06_项目分析与推荐" / (title + ".md"), "\n".join(lines))
    dump("需求纠偏整合校验.json", {"all_records": len(all_records), "unique_ids": len({r["id"] for r in all_records}), "classified_all": all("taxonomy" in r and "reading" in r for r in all_records), "candidates_with_all_chain_nodes": sum(all(k in r["chain"] for k in ["outcome", "profile", "project", "interview"]) for r in cases["cases"]), "projects_compared": len(p_by_id), "dimensions": len(dim_rows), "source_archives_checked": comparisons["validation"], "personal_project_design_modified": False})
    print(json.dumps({"totals": coverage["totals"], "strict_recent_internship": coverage["interview_coverage"]["strict_recent_explicit_internship_count"], "publication_recent_year_unknown": coverage["interview_coverage"]["publication_recent_event_year_unknown_count"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    integrate()
