"""合并已核验的调研资料并生成阅读入口；不联网、不运行第三方源码。"""
from pathlib import Path
from collections import Counter, defaultdict
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit
import csv
import hashlib
import io
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parent.parent
INDEX = Path(__file__).resolve().parent
if (INDEX / "github_ssp_supplement_records.json").exists():
    raise SystemExit("GitHub SSP专项已整合；请运行整合GitHub_SSP专项.py，避免将主索引恢复为上轮快照。")
DATE = "2026-10-23"
DIRS = {
    "01_Report": "01_调研报告",
    "02_JD_Cards": "02_招聘岗位资料",
    "03_Resume_Case_Cards": "03_简历与候选人案例",
    "04_Interview_and_Expert_Cards": "04_面经与专业观点",
    "05_Project_Source_Archives": "05_项目源码归档",
    "06_Project_Recommendations": "06_项目分析与推荐",
    "07_Your_Project_Blueprints": "07_个人项目设计_暂缓",
    "08_Evidence_Index": "08_证据索引与统计",
}


def folder(old):
    return ROOT / (DIRS[old] if (ROOT / DIRS[old]).exists() else old)


REPORT = folder("01_Report")
ARCHIVES = folder("05_Project_Source_Archives")
INTERVIEW_DIR = folder("04_Interview_and_Expert_Cards")
CV_DIR = folder("03_Resume_Case_Cards")


def read(path):
    return path.read_text(encoding="utf-8-sig")


def write(path, text):
    # 保留已存在文本的换行符；新生成的中文材料使用CRLF。
    newline = "\r\n" if not path.exists() or b"\r\n" in path.read_bytes() else "\n"
    with path.open("w", encoding="utf-8", newline="") as stream:
        stream.write(text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", newline))


def load(name):
    return json.loads(read(INDEX / name))


def dump(name, obj):
    write(INDEX / name, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def unique(records):
    result = {}
    for record in records:
        if record["id"] in result and result[record["id"]] != record:
            raise ValueError("重复ID且内容不同：" + record["id"])
        result[record["id"]] = record
    return list(result.values())


old_all = load("all_evidence_records.json")
backend = load("backend_interview_supplement.json")
agent = load("agent_interview_supplement.json")
added_interviews = backend + agent
interviews = unique([r for r in load("interview_records.json") if int(r["id"][3:]) < 20] + added_interviews)
interviews.sort(key=lambda r: int(r["id"][3:]))
project_data = load("project_recommendations.json")
project_added = load("project_supplement.json")["projects"]
projects = unique([r for r in project_data["projects"] if int(r["id"][3:]) < 8] + project_added)
project_data["projects"] = projects
project_data["supplement_date"] = DATE
project_data["supplement_scope"] = "重点补充面经、候选人关联项目与源码证据；个人项目设计暂缓。"
opinions = load("bilibili_zhihu_records.json")
for r in opinions:
    if r["id"] == "OP05":
        r["access_level"] = "知乎访问范围不变；本轮作者官网正文可读并核对项目经历、技能、STAR/FAB及建议部分"
        r["content_validation"] = "作者官网正文已核验；不是知乎本体全文核验"
        r["root_recheck"] = "2026-10-23重读官网正文；仅采纳真实职责与问题/效果表达，不采纳把非本人工作写成个人贡献的建议。"

candidate_data = load("candidate_cases.json")
candidate_additions = {
    "CV02": "本轮已补齐学成在线固定源码（PRO08）；RPC和点评仍仅有链接。",
    "CV05": "本轮已补齐Apache ShenYu当前固定源码（PRO09）；Helm Chart未归档。当前功能不等于2023年个人贡献。",
    "CV06": "本轮已补齐Casdoor当前固定源码（PRO10）；当前新增能力不等于2021年被打码的个人贡献。",
    "CV07": "本轮公开SSR入口一次读到正文，随后复核仍返回空壳，继续标记访问不稳定；没有新增完整CV或正式offer证明。",
}
for r in candidate_data["cases"]:
    if r["id"] in candidate_additions:
        r["supplement_update"] = candidate_additions[r["id"]]
        path = CV_DIR / (r["id"] + ".txt")
        text = read(path)
        if r["id"] == "CV02":
            text = text.replace("关联项目链接（不代表已打包源码）", "关联项目链接（学成在线已补归档；其他仅链接）")
        elif r["id"] == "CV05":
            text = text.replace("关联项目链接（不代表已打包源码）", "关联项目链接（ShenYu已补归档；Helm Chart仅链接）")
        elif r["id"] == "CV06":
            text = text.replace("关联项目链接（不代表已打包源码）", "关联项目链接（当前版本已补归档，非历史个人贡献快照）")
        text = re.sub(r"\n本轮信息搜集更新：\n[\s\S]*$", "", text)
        write(path, text.rstrip() + "\n\n本轮信息搜集更新：\n" + candidate_additions[r["id"]] + "\n")

observations = load("collection_observations.json")
rechecks = load("collection_recheck_log.json")
navigation = rechecks["navigation_sources"]
for r in observations:
    write(CV_DIR / (r["id"] + ".txt"), r["id"] + " | " + r["title"] + "\n\n" +
          "\n\n".join(k + "：\n" + ("\n".join(v) if isinstance(v, list) else str(v))
                       for k, v in r.items() if k not in {"id", "title"}) + "\n")

primary_by_id = {r["id"]: r for r in old_all}
for records, category in [(interviews, "面经复盘"), (projects, "项目参考"),
                          (opinions, "B站与知乎"), (candidate_data["cases"], "候选人资料"),
                          (observations, "候选人对照"), (navigation, "检索导航")]:
    for record in records:
        primary_by_id[record["id"]] = dict(record, category=category)
all_records = list(primary_by_id.values())
dump("interview_records.json", interviews)
dump("project_recommendations.json", project_data)
dump("bilibili_zhihu_records.json", opinions)
dump("candidate_cases.json", candidate_data)
dump("all_evidence_records.json", all_records)

manifests = load("SOURCE_MANIFEST.json") if (INDEX / "SOURCE_MANIFEST.json").exists() else json.loads(read(ARCHIVES / "SOURCE_MANIFEST.json"))
extra_manifests = json.loads(read(ARCHIVES / "SUPPLEMENT_MANIFEST.json"))
manifest_by_repo = {m["repo"]: m for m in manifests + extra_manifests if m.get("status") == "downloaded"}
manifests = list(manifest_by_repo.values())
write(ARCHIVES / "SOURCE_MANIFEST.json", json.dumps(manifests, ensure_ascii=False, indent=2) + "\n")

THEMES = {
    "项目职责、真实使用与架构取舍": r"个人贡献|项目深挖|负责|使用者|真实|选型|取舍|业务|必要性|架构",
    "Java/Go/Python与框架基础": r"Java|JVM|Spring|Python|Go\b|Golang|并发|线程|装饰器|GC|AOP",
    "数据库、缓存与检索存储": r"MySQL|SQL|Redis|数据库|缓存|索引|GEO|事务|ES|Elasticsearch",
    "消息、幂等与故障恢复": r"MQ|消息|幂等|重复|重试|恢复|宕机|超时|中断|失败|故障",
    "RAG、分块、召回与重排": r"RAG|召回|检索|分块|切分|重排|rerank|BM25|RRF|向量|Cross.Encoder",
    "Agent编排、工具与Skill/MCP": r"Agent|智能体|工具|Skill|MCP|Workflow|工作流|LangGraph|ReAct|Harness",
    "记忆、上下文与token成本": r"记忆|上下文|压缩|token|KV.?Cache|长短期|预算|成本",
    "评测、指标与上线效果": r"评测|指标|Recall|精确率|召回率|覆盖|质量|成功率|测试|量化|效果",
    "权限、审批与隔离": r"权限|审批|确认|安全|沙箱|租户|隔离|注入|授权|撤权",
    "网络、操作系统与编码": r"网络|HTTP|TCP|SSE|进程|端口|算法|编程|编码|手写|现场|矩阵|数组|链表|JSON|树",
}
topic_rows = []
for label, pattern in THEMES.items():
    matched = [r["id"] for r in interviews
               if re.search(pattern, " ".join(r.get("topics", []) + r.get("project_questions", [])), re.I)]
    topic_rows.append({"theme": label, "record_count": len(matched), "evidence_ids": matched, "rule": pattern})
dump("interview_topic_index.json", {"method": "只匹配topics和project_questions；每条资料每主题计一次。包含同作者与多场汇总，数字是本包检索索引，非独立场次或市场概率。", "themes": topic_rows})
buffer = io.StringIO(newline="")
writer = csv.writer(buffer)
writer.writerow(["主题", "资料条数_非独立场次", "资料ID", "复核规则"])
for row in topic_rows:
    writer.writerow([row["theme"], row["record_count"], ";".join(row["evidence_ids"]), row["rule"]])
write(INDEX / "面经主题索引.csv", buffer.getvalue())

groups = Counter(r.get("sample_group", "未分组") for r in interviews)
new_groups = Counter(r.get("sample_group", "未分组") for r in added_interviews)
statistics = {
    "date": DATE,
    "scope": "信息搜集增补；个人项目设计暂缓",
    "interviews_before": 19,
    "interviews_added": len(added_interviews),
    "backend_interviews_added": len(backend),
    "agent_interviews_added": len(agent),
    "interviews_total": len(interviews),
    "new_interview_groups": dict(new_groups),
    "all_interview_groups": dict(groups),
    "new_fulltext_records": sum(r.get("fulltext_verified") is True for r in added_interviews),
    "projects_before": 7,
    "projects_added": len(project_added),
    "projects_total": len(projects),
    "source_archives_total": len(manifests),
    "source_archives_added": len([m for m in extra_manifests if m.get("status") == "downloaded"]),
    "candidate_counterexamples_added": len(observations),
    "complete_successful_resumes": 0,
    "new_full_bilibili_videos": 0,
    "logical_evidence_total": len(all_records),
    "category_counts": dict(Counter(r["category"] for r in all_records)),
    "caution": "逻辑资料条目不等于独立候选人、面试场次、已获offer或当前在招数量；SSP仍仅为个别作者自述。",
}
dump("本轮增补统计.json", statistics)

LABELS = {
    "company": "公司", "team": "团队", "role": "岗位方向", "role_type": "岗位类型", "url": "原文链接",
    "canonical_url": "去参数原文", "supporting_urls": "补充来源", "supporting_url": "补充来源", "secondary_url": "同作者/补充原文",
    "date": "日期与确定性", "date_certainty": "日期核验", "round": "轮次", "rounds": "轮次", "outcome": "结果口径（自述）",
    "role_boundary": "岗位边界", "ssp_status": "SSP口径", "sample_group": "样本分组", "topics": "技术主题",
    "project_questions": "项目追问（归纳）", "summary": "摘要与评价", "borrowable_points": "值得借鉴", "weaknesses_and_limits": "不足与边界",
    "limitations": "限制", "limits": "限制", "confidence": "证据边界", "access_level": "实际访问范围", "fulltext_verified": "正文已读",
    "evidence_type": "证据类型", "source_project_links": "项目来源关系", "public_project_repositories": "候选人公开仓库",
    "repository_relationship": "仓库关系", "source_project_description": "项目描述", "candidate_group": "同作者分组", "author_group": "同作者分组",
    "reading_method": "读取方法", "recommended_use": "建议用途", "recommendation": "推荐理由", "commercial_bias": "商业利益与偏差",
    "independence_note": "独立性说明", "repo": "源码仓库", "stack": "技术栈", "strengths": "优点", "weaknesses": "不足与风险",
    "borrow": "建议阅读重点", "extend": "代码审查方向", "inspect_paths": "拆读源码路径", "source_findings": "固定版本源码证据",
    "tests_and_evaluation": "测试与评测材料", "runtime_dependencies": "运行依赖", "cost": "依赖与费用边界",
    "recommended_for": "适合参考", "not_recommended_for": "不适合直接采用", "candidate_links": "候选人关联",
    "interview_evidence_ids": "面经主题映射", "interview_linkage": "关联强度", "interview_questions": "源码深挖问题（整理者提出）",
    "license": "许可证", "license_scope": "许可范围", "commit": "固定commit", "commit_date": "commit日期", "source_archive": "已附源码包",
    "archive_file": "源码包文件", "archive_sha256": "SHA-256", "run_status": "运行验证状态", "inspection_boundary": "核验范围",
    "source_urls": "一手来源", "source_type": "来源类型", "source_summary": "可见材料摘要", "original_analysis": "整理者分析",
    "outcome_evidence": "录用证据", "document_type": "材料形式", "anonymous_background": "匿名背景", "projects": "项目与经历",
    "project_urls": "关联项目", "license_notes": "原材料许可", "original_file_status": "原件状态", "supplement_update": "本轮更新",
    "platform": "平台", "author": "公开作者", "identity_evidence": "身份依据", "opinion": "可见观点", "content_validation": "内容核验",
    "verified_video_viewing": "已观看完整视频", "root_recheck": "再次核查", "material_type": "材料类型", "archive_status": "归档状态",
    "use_rule": "使用边界", "degree_constraint": "学历届别", "availability_constraint": "到岗约束", "recruiting_status": "招聘状态",
    "required_stack": "明确要求", "preferred_stack": "偏好与加分", "own_summary": "摘要", "evidence_excerpt": "短摘录",
    "duties": "职责", "matrix_include": "纳入工程JD样本", "publish_date": "发布时间", "tags": "标签",
    "read_method": "正文读取方法", "verification_notes": "读取范围与限制", "archive_omission_reason": "未归档原因",
    "path": "源码路径", "line_start": "起始行", "line_end": "结束行", "finding": "观察结果", "kind": "证据类型",
}
SKIP = {"id", "title", "category", "retrieved_at", "retrieved_date", "retrieved_date", "source_line_range", "outcome_status"}


def value_html(value):
    if isinstance(value, list):
        return "<ul>" + "".join("<li>" + value_html(item) + "</li>" for item in value) + "</ul>"
    if isinstance(value, dict):
        return "<br>".join(escape(LABELS.get(k, k)) + "：" + value_html(v) for k, v in value.items())
    if isinstance(value, bool):
        return "是" if value else "否"
    if value is None:
        return "未提供"
    text = str(value)
    if re.fullmatch(r"https?://[^\s]+", text):
        return '<a href="' + escape(text, quote=True) + '">' + escape(text) + "</a>"
    if text.endswith(".zip") and (ARCHIVES / text).is_file() and Path(text).name == text:
        return '<a href="../05_项目源码归档/' + escape(text, quote=True) + '">' + escape(text) + '</a>'
    return escape(text).replace("\n", "<br>")


def card(record, fields=None, open_default=False):
    fields = fields or [k for k in record if k not in SKIP]
    body = "".join('<div class="field"><b>' + escape(LABELS.get(k, k)) + '</b><div>' + value_html(record[k]) + '</div></div>'
                   for k in fields if k in record and record[k] not in (None, [], ""))
    return '<details class="card" id="' + record["id"] + '" data-category="' + escape(record.get("category", "")) + '"' + (" open" if open_default else "") + '><summary><span class="tag">' + record["id"] + '</span> ' + escape(record["title"]) + "</summary>" + body + "</details>"


def table(headers, rows):
    return '<div class="tablewrap"><table><thead><tr>' + "".join("<th>" + h + "</th>" for h in headers) + "</tr></thead><tbody>" + "".join("<tr>" + "".join("<td>" + str(cell) + "</td>" for cell in row) + "</tr>" for row in rows) + "</tbody></table></div>"


def refs(ids, target="index.html"):
    return " ".join('<a href="' + target + "#" + key + '">' + key + "</a>" for key in ids)


css = """
*{box-sizing:border-box}body{margin:0;background:#f4f7fa;color:#243547;font:15px/1.8 'Microsoft YaHei',sans-serif}header{background:#132d46;color:white;padding:42px max(5vw,24px)}h1{font-size:30px;line-height:1.4}main{max-width:1240px;margin:auto;padding:25px}section{background:white;border:1px solid #dce4ec;border-radius:10px;margin-bottom:22px;padding:26px}h2{font-size:23px;color:#163650;border-bottom:3px solid #2b918a;padding-bottom:10px}h3{color:#176c70}a{color:#176c70;overflow-wrap:anywhere}header a{color:#a6f0df}aside{background:#eaf6f3;border-left:4px solid #2b918a;padding:15px 20px;margin:18px 0}table{width:100%;border-collapse:collapse;font-size:13px}th,td{border:1px solid #dce4ec;padding:10px;vertical-align:top}th{background:#eaf0f5}.tablewrap{overflow-x:auto}details.card{border:1px solid #dce4ec;border-radius:8px;margin:15px 0}summary{padding:14px;cursor:pointer;font-weight:bold}.tag{color:#176c70;display:inline-block;min-width:50px}.field{display:grid;grid-template-columns:150px 1fr;gap:12px;padding:9px 16px;border-top:1px solid #e8edf2;font-size:13px;overflow-wrap:anywhere}.field b{color:#516779}ul{padding-left:20px;margin:5px 0}.muted{font-size:13px;color:#62798d}.stats{display:flex;gap:12px;flex-wrap:wrap}.stats span{background:#234159;padding:12px 18px;border-radius:7px}.stats strong{display:block;color:#a6f0df;font-size:25px}.historic{margin-top:25px}footer{padding:20px;text-align:center;color:#62798d}@media(max-width:750px){.field{grid-template-columns:1fr}main{padding:10px}section{padding:18px}}@media print{@page{size:A4;margin:16mm}body{background:white;font-size:10pt}header{background:white;color:#163650;padding:0 0 10px}header a{color:#176c70}main{padding:0;max-width:none}section{padding:8px 0;border:0;border-radius:0}h1{font-size:24pt}h2{font-size:17pt;break-after:avoid}h3,summary{break-after:avoid}.stats span{background:#edf5f3;color:#163650}.stats strong{color:#176c70}.field{display:block;font-size:9pt;padding:6px 8px}.field b{display:block}details.card{break-inside:auto}table{font-size:8pt}.tablewrap{overflow:visible}tr{break-inside:avoid}a{word-break:break-all}footer{font-size:8pt}}
"""

scope_note = (f"本轮新增{len(added_interviews)}条面经资料（后端{len(backend)}条、Agent/混合方向{len(agent)}条），"
              f"新增{len(project_added)}份项目分析及5个固定源码包。现有{len(interviews)}条面经、{len(projects)}份项目分析、{len(manifests)}个源码包。")
overview_rows = [["面经资料", "19", str(len(interviews)), "原文阅读、结果口径、具体项目追问；同作者、多轮和汇总均标注"],
                 ["项目分析", "7", str(len(projects)), "新增候选人项目关系、具体源码证据、测试与运行边界"],
                 ["固定源码包", "7", str(len(manifests)), "新增学成在线、ShenYu、Casdoor、AgentScope、OpenManus"],
                 ["候选人对照", "0", "2", "不是成功者简历；用于降低只看上岸帖的选择偏差"],
                 ["完整成功者CV", "0", "0", "本轮未获取，不用卡片或求助帖冒充原件"]]
company_rows = [[r["id"], escape(r["company"]), escape(r["role"]), escape(r["date"]), escape(r["outcome"]), '<a href="' + escape(r["url"], quote=True) + '">原文</a>'] for r in added_interviews]
project_rows = [[r["id"], escape(r["repo"]), escape(r["license"]), "已归档" if r.get("source_archive") else "仅分析，未整库归档", escape(r["recommendation"])] for r in project_added]
theme_table = table(["主题", "本包可检索条数", "证据ID"], [[escape(r["theme"]), r["record_count"], refs(r["evidence_ids"])] for r in topic_rows])

mapping_rows = [
    ["线程池与异步超时", refs(["INT20", "INT22", "INT25"]), refs(["PRO08"]), "学成在线消息执行器的线程池生命周期与await边界；是主题映射，不声称面经考过该仓库。"],
    ["消息重复与业务一致性", refs(["INT22", "INT27", "INT40", "INT41"]), refs(["PRO01", "PRO02", "PRO08"]), "数据库提交、消息确认与恢复查询的故障窗口；框架幂等不自动覆盖所有业务副作用。"],
    ["网关、限流与多租户", refs(["INT23", "INT25"]), refs(["PRO09", "PRO10"]), "ShenYu插件与限流单测、Casdoor鉴权策略；部署与本人贡献分开。"],
    ["工具/Skill与人机审批", refs(["INT44", "INT45", "INT47", "INT53"]), refs(["PRO04", "PRO11", "PRO12"]), "AgentScope权限模式、OpenManus工具执行边界；框架确认不等于业务服务授权。"],
    ["评测质量与实际任务成功", refs(["INT01", "INT46", "INT51", "INT55"]), refs(["PRO06", "PRO11", "PRO12", "PRO13"]), "区分Mock机制测试、沙箱测试、5条示例与完整任务基准；不使用预期输出当实测。"],
    ["性能、记忆与token取舍", refs(["INT45", "INT46", "INT52", "INT54"]), refs(["PRO05", "PRO11", "PRO12"]), "源码帮助定位机制；压缩、恢复和执行循环的效果仍须另做实验。"],
]
interview_fields = ["company", "team", "role", "date", "date_certainty", "round", "rounds", "sample_group", "role_boundary", "outcome", "ssp_status", "url", "supporting_urls", "supporting_url", "secondary_url", "topics", "project_questions", "summary", "recommended_use", "borrowable_points", "weaknesses_and_limits", "limitations", "source_project_description", "source_project_links", "public_project_repositories", "repository_relationship", "candidate_group", "author_group", "independence_note", "commercial_bias", "access_level", "reading_method", "verification_notes", "confidence"]
project_fields = ["repo", "url", "role", "recommendation", "candidate_links", "stack", "strengths", "weaknesses", "borrow", "extend", "inspect_paths", "source_findings", "tests_and_evaluation", "runtime_dependencies", "cost", "recommended_for", "not_recommended_for", "interview_evidence_ids", "interview_linkage", "interview_questions", "commercial_bias", "license", "license_scope", "commit", "commit_date", "source_archive", "archive_file", "archive_omission_reason", "archive_sha256", "run_status"]
supplement = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>面经与项目信息搜集增补报告</title><style>' + css + '</style></head><body><header><p>2026-10-23 · 本地资料增补</p><h1>面经与项目信息搜集增补报告</h1><p>' + scope_note + '</p><p><a href="index.html">完整可搜索资料目录</a> · <a href="面经追问与源码对照.md">追问与源码对照表</a></p></header><main>'
supplement += '<section id="scope"><h2>本轮交付与使用范围</h2><aside>按最新要求，本轮先做信息搜集与项目阅读，不继续设计个人项目。既有设计仅作历史草案保留。</aside>' + table(["材料", "原有", "现有", "说明"], overview_rows) + '<p>新增面经均读取具体问题正文；全文可读仅表示获取范围，不代表面试、身份或录用结果获得企业认证。B站仍未获取完整视频或字幕。公开网页可能在下次访问时返回空壳。</p><p>项目优缺点分开记录源码可见行为、静态风险与未执行项；没有运行第三方系统、模型或付费服务。案例之间的关联不构成“某项目导致SSP”的因果证明。</p></section>'
supplement += '<section id="interviews"><h2>新增面经总览</h2><p>一条记录可能包含多轮或多公司；不能将29条资料理解成29个独立成功候选人。校招、历史SSP对照、批次不明和多场汇总单列。</p>' + table(["编号", "公司", "方向", "日期", "结果自述", "来源"], company_rows) + table(["新增分组", "条数"], [[escape(k), v] for k, v in new_groups.items()]) + '</section>'
supplement += '<section id="themes"><h2>按追问检索资料</h2><p>以下计数只用于在本包内找材料：按topics与project_questions匹配，每条资料每主题计一次。包含同作者与汇总记录，不是行业频率、独立场次或招聘概率。</p>' + theme_table + '</section>'
supplement += '<section id="mapping"><h2>面经追问与项目源码怎样对照阅读</h2><p>这是整理者按主题建立的阅读关系，除候选人卡明确说明的关系外，不表示面试官或候选人使用了相应开源仓库。</p>' + table(["追问主题", "面经", "源码", "阅读重点与关系边界"], mapping_rows) + '</section>'
supplement += '<section id="projects"><h2>新增项目总览</h2>' + table(["编号", "仓库", "许可", "打包", "推荐理由"], project_rows) + '<p>Hello-Agents是教材与子项目集合，顶层与子目录许可不同，本轮不整库归档；相应固定源码与评测材料已阅读。候选人关联的RPC、点评、Helm Chart仍未全部归档。</p></section>'
supplement += '<section id="new-cards"><h2>新增面经阅读卡</h2>' + "".join(card(dict(r, category="面经复盘"), interview_fields, True) for r in added_interviews) + '</section>'
supplement += '<section id="project-cards"><h2>新增项目拆读卡</h2>' + "".join(card(dict(r, category="项目参考"), project_fields, True) for r in project_added) + '</section>'
supplement += '<section id="counterexamples"><h2>候选人项目对照与来源复核</h2>' + "".join(card(r, open_default=True) for r in observations) + '<h3>仍然存在的缺口</h3><ul><li>没有新增完整成功者简历，Agent实习与SSP结果仍缺可完整对照的履历链。</li><li>没有企业侧独立核验offer，也没有同公司同批次的SSP与普通档对照。</li><li>B站视频/字幕未取得；作者官网可读不等于知乎本体已读。</li><li>源码存在性与静态阅读不代表部署、性能或业务效果已验证。</li></ul><p>访问变化和失败尝试见<a href="../08_证据索引与统计/collection_recheck_log.json">来源复核日志</a>；固定源码校验见<a href="../05_项目源码归档/SOURCE_MANIFEST.json">源码清单</a>。</p></section>'
supplement += '</main><footer>原创归纳与来源链接 · 第三方源码保留原许可 · 逻辑条目含同源交叉引用</footer></body></html>'
write(REPORT / "信息搜集增补报告.html", supplement)

markdown = "# 面经追问与源码对照\n\n" + scope_note + "\n\n这些对应仅是主题阅读关系；不等于面试官使用该仓库，也不证明该项目导致录用。个人项目设计暂缓。\n\n"
markdown += "| 主题 | 面经 | 项目 | 阅读重点 |\n|---|---|---|---|\n"
for theme, ids, pro_ids, note in mapping_rows:
    md_refs = lambda s: re.sub(r'<a href="([^"]+)">([^<]+)</a>', r'[\2](\1)', s)
    markdown += "| " + " | ".join([theme, md_refs(ids), md_refs(pro_ids), note]) + " |\n"
markdown += "\n## 新增项目阅读顺序\n\n"
for r in project_added:
    markdown += f"- {r['id']} {r['repo']}：{r['recommendation']} [原仓库]({r['url']})\n"
markdown += "\n具体追问、优缺点和固定源码行号，见[增补报告](信息搜集增补报告.html)及[完整目录](index.html)。\n"
write(REPORT / "面经追问与源码对照.md", markdown)

main_path = REPORT / "index.html"
original_path = REPORT / "历史报告_初版.html"
if not original_path.exists():
    original_path.write_bytes(main_path.read_bytes())
original_pdf = REPORT / "research_report.pdf"
historical_pdf = REPORT / "历史报告_含初版项目设计.pdf"
if original_pdf.exists() and not historical_pdf.exists():
    assert original_pdf.resolve().parent == REPORT.resolve()
    original_pdf.rename(historical_pdf)
markup = read(original_path)
for old, new in DIRS.items():
    markup = markup.replace(old, new)
markup = markup.replace("大厂后端与Agent实习调研 | 2026-10-23", "大厂后端与Agent信息搜集 | 2026-10-23增补")
markup = markup.replace("要求调研与双项目设计", "面经与项目资料库 · 增补版")
markup = markup.replace("CAREER RESEARCH / EVIDENCE & PROJECT DESIGN", "CAREER RESEARCH / INTERVIEWS & SOURCE MATERIALS")
markup = markup.replace('href="#s0">01 结论与阅读方式', 'href="#s0">01 本轮阅读入口')
markup = re.sub(r'<a href="#s8">[\s\S]*?<a href="#s12">[^<]+</a>', '<a href="#historical">初版项目草案（暂缓）</a>', markup, count=1)
markup = markup.replace("<strong>19</strong>面经与复盘", f"<strong>{len(interviews)}</strong>面经与复盘")
markup = markup.replace("<strong>7</strong>固定版本源码", f"<strong>{len(manifests)}</strong>固定版本源码")
banner = '<aside><strong>本轮信息搜集增补：</strong>' + scope_note + ' <a href="信息搜集增补报告.html">打开新增资料与分析</a> · <a href="信息搜集增补报告.pdf">增补PDF</a>。个人项目设计暂缓，初版草案折叠保留。</aside>'
markup = markup.replace('<article>', '<article>' + banner, 1)
markup = re.sub(r'<section id="s0">[\s\S]*?</section>', '<section id="s0"><h2>01 本轮阅读入口</h2><p>' + scope_note + '</p><p>先读<a href="信息搜集增补报告.html">信息搜集增补报告</a>，按公司、技术主题或源码证据定位材料；所有资料可在页末目录检索。既有JD和候选人材料继续保留。新增两个候选人对照案例，不计成功者简历。</p><p>完整成功者CV仍为0，B站仍未观看完整内容。所有录用结果维持作者自述口径。个人项目设计留待下一步讨论。</p></section>', markup, count=1)
markup = markup.replace("06 面经：项目最容易暴露的问题", "06 面经：原有分析与增补入口")
markup = markup.replace("面经目录包含19篇候选人公开记录：14篇明确实习面经、4篇校招或招聘批次未明的邻近岗位参考、1篇多场总结；后端、Agent、混合和AI全栈均在卡片标注。不同记录可能来自同一候选人，不能把题目出现次数当行业概率。", f"原有19条记录继续保留，本轮新增{len(added_interviews)}条，现共{len(interviews)}条面经资料。新增分组、结果及具体追问详见增补报告；不同记录可能来自同一候选人，多场汇总也不代表独立样本，不能把题目出现次数当行业概率。")
markup = markup.replace("七个项目怎样博采众长", "项目资料怎样对照阅读")
markup = markup.replace("七个推荐参考项目已附固定commit源码归档与原许可证", f"现有{len(projects)}份项目分析，其中{len(manifests)}个已附固定commit源码归档与原许可证")
markup = markup.replace("不是七个需要你全部重做的简历项目", "无需将这些参考项目全部重做")
markup = markup.replace("完整版额外含七个源码归档", f"本地完整版现含{len(manifests)}个源码归档")
markup = markup.replace("另列在履历卡的项目链接中。这些是背景线索，不全属于本次推荐源码包", "另列在履历卡的项目链接中。本轮已新增学成在线、ShenYu与Casdoor源码；RPC、点评和Helm Chart仍为链接，并不全属于本次源码包")
markup = markup.replace("OP05 JavaGuide：简历指南", "OP05 JavaGuide：官网正文已重读")
markup = markup.replace("知乎部分只有索引", "知乎本体部分只有索引（OP05作者官网本轮已读正文）")
start = markup.index('<section id="s8">')
end = markup.index('<section id="s13">')
markup = markup[:start] + '<details class="historic" id="historical"><summary>初版个人项目草案（暂缓讨论；本轮未继续设计）</summary>' + markup[start:end] + '</details>' + markup[end:]
markup = markup.replace("if(el&&el.classList.contains('card'))", "if(el){for(let p=el;p;p=p.parentElement){if(p.tagName==='DETAILS')p.open=true}}if(el&&el.classList.contains('card'))")
markup = markup.replace("19份面经复盘与7份B站/知乎资料卡", f"{len(interviews)}份面经资料与7份B站/知乎资料卡")
markup = markup.replace("7个固定commit的公开源码ZIP", f"{len(manifests)}个固定commit的公开源码ZIP")
markup = markup.replace("逐项目优缺点、借鉴模块、源码路径和改造方向", f"{len(projects)}份项目优缺点、模块、源码路径和运行边界")
markup = markup.replace("本报告PDF、完整离线HTML与可搜索资料目录", "增补HTML/PDF、完整搜索目录与初版历史报告")
categories = list(dict.fromkeys(r["category"] for r in all_records))
catalog = '<section id="evidence"><h2>15 可搜索资料目录</h2><p>按公司、技术点、编号、岗位批次或证据状态搜索。逻辑记录含同源交叉引用；成功者自述与对照样本分列。</p><div class="tools"><input id="q" type="search" placeholder="例如：Redis、评测、SSP、INT55、PRO08"><select id="category"><option>全部类别</option>' + "".join("<option>" + escape(c) + "</option>" for c in categories) + '</select><button id="expand">展开匹配</button><button id="collapse">全部收起</button></div><p class="muted" id="count"></p>' + "".join(card(r) for r in all_records) + '</section>'
markup = re.sub(r'<section id="evidence">[\s\S]*?</section>', lambda _: catalog, markup, count=1)
write(main_path, markup)

op_path = INTERVIEW_DIR / "OP05.txt"
op_text = read(op_path)
op_text = op_text.replace("知乎索引可见、403；作者官网搜索收录较长正文", "知乎索引可见、403；本轮已实际读取作者官网正文，不代表知乎本体全文已读")
op_text = op_text.replace("作者官网搜索收录正文部分核验", "作者官网正文已核验；不是知乎本体全文核验")
write(op_path, op_text)

write(ROOT / "00_START_HERE.txt", "大厂后端与Agent实习信息搜集包 | 2026-10-23增补\n\n" + scope_note +
      "\n\n先打开 01_调研报告/信息搜集增补报告.html 或同名PDF；完整离线检索入口为 01_调研报告/index.html。\n" +
      "面经包含明确实习、校招、历史SSP、批次不明与多场汇总，均在卡片分组。个别同作者多篇不算独立候选人。\n" +
      "7条B站/知乎材料继续保留，OP05作者官网正文已重读；B站视频与字幕仍未取得。\n" +
      "简历目录仍为9份候选人分析材料，没有完整成功者CV。另有2份候选人项目对照，不能算已获大厂offer案例。\n" +
      "全部源码包固定commit，保留许可；已核对CRC、SHA-256、推荐阅读路径。未部署、压测或运行模型。\n" +
      "Hello-Agents因体量及分目录许可仅做分析、不整库归档。RPC、点评、Helm Chart及无明确许可的候选人仓库仍仅链接。\n" +
      "个人项目设计暂缓。本轮没有扩展双项目方案；旧草案保留在07_个人项目设计_暂缓以及历史报告中。\n\n目录：\n" +
      "\n".join(DIRS.values()) + "\n")
write(INDEX / "source_methodology.txt", f"本包共{len(all_records)}条逻辑资料；同原文可在不同类别交叉引用，不代表独立样本。\n" +
      "招聘JD19；候选人资料9；面经资料" + str(len(interviews)) + "；B站/知乎7；项目分析" + str(len(projects)) + "；官方技术参考10；候选人对照2；检索导航1。\n" +
      "本轮新增29条面经均读取具体正文；其余旧条目按原访问说明。新增分组见本轮增补统计.json，主题频次只作资料检索。\n" +
      "结果均为作者自述；同作者、多场及历史材料分别标注。不用项目存在性推断录用因果。\n" +
      "JD工程分母仍14，其中部分员工招募帖身份未独立核验；要求、偏好和职责的提及不等于统一硬门槛。\n" +
      "视频仍仅标题/简介；OP05作者官网正文可读不等于知乎本体已读。\n个人项目设计暂缓。\n")
write(INDEX / "verification_scope.txt", f"源码归档共{len(manifests)}个：固定commit、ZIP CRC、SHA-256及推荐路径存在性校验。\n" +
      "本轮新增5包；新增项目抽读实现、测试及依赖，并记录固定源码行号。静态疑点不宣称已经运行复现。\n" +
      "未执行第三方完整部署、构建、模型调用、压测或任务评测；所有性能数字/预期输出不作为本次实测。\n" +
      "Ragent所选拒绝middleware不证明业务授权；DeerFlow契约文档仍为DRAFT；RAGFlow HTTP benchmark不等于检索质量。\n" +
      "学成在线await超时不自动取消工作线程；AgentScope权限模式不替代业务授权；OpenManus沙箱测试不等于任务成功评测；Hello-Agents示例5/5是预期输出。\n")

write(ROOT / "00_本轮更新说明.md", "# 信息搜集增补完成\n\n" + scope_note +
      "\n\n- [增补报告](01_调研报告/信息搜集增补报告.html)\n- [增补PDF](01_调研报告/信息搜集增补报告.pdf)\n- [完整可搜索目录](01_调研报告/index.html)\n- [面经追问与源码对照](01_调研报告/面经追问与源码对照.md)\n- [本轮统计](08_证据索引与统计/本轮增补统计.json)\n- [源码归档与校验](05_项目源码归档/SOURCE_MANIFEST.json)\n\n" +
      "八个子文件夹已统一中文命名，原个人项目草案暂缓讨论。完整成功者简历与B站视频正文仍未补齐；第三方项目未运行。\n")

# 验证合并后的ID、URL及源码包，结果写回索引。
urls = defaultdict(list)
for r in interviews:
    u = urlsplit(r["url"])
    key = (u.path.replace("/feed/main/detail/", "/feed/"), u.netloc.replace("api-cdn.nowcoder.com", "www.nowcoder.com"))
    urls[key].append(r["id"])
duplicates = [ids for ids in urls.values() if len(ids) > 1]
archive_checks = []
for m in manifests:
    p = ARCHIVES / m["archive_file"]
    assert p.resolve().parent == ARCHIVES.resolve()
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    assert actual == m["archive_sha256"], (m["repo"], "SHA-256不一致")
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None, (m["repo"], "CRC失败")
        names = z.namelist()
        for project in projects:
            if project.get("repo") == m["repo"]:
                for path in project.get("inspect_paths", []):
                    assert any(n.endswith("/" + path) or n == path for n in names), (project["id"], path)
    archive_checks.append({"repo": m["repo"], "sha256": actual, "crc": "通过", "member_count": len(names)})
dump("整合校验结果.json", {"json_records": len(all_records), "unique_ids": len({r["id"] for r in all_records}), "interview_duplicate_primary_urls": duplicates, "archives": archive_checks, "scope": "本地结构/链接/源码完整性验证；不等于第三方运行成功"})
assert not duplicates, duplicates
print(json.dumps(statistics, ensure_ascii=False, indent=2))
