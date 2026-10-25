"""固定公开证据，仅静态读取；联系字段不落盘，不执行外部源码。"""
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
S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0"
SITE = "f49953fb0d4bd52a39bf81167b0c4b7dd7d78a64"
ULTI = "d53b582e2fae32ef644642651086df0e5ed3163d"
RESI = "1ed3be36af0795a363d624d38de676c0d00b4cf7"


def read(repo, sha, path):
    url = f"https://raw.githubusercontent.com/{repo}/{sha}/{path}"
    r = S.get(url, timeout=45)
    r.raise_for_status()
    return r, {"url": url, "http_status": r.status_code, "sha256": hashlib.sha256(r.content).hexdigest(), "lines": len(r.text.splitlines())}


def code(repo, sha, path, scope, finding):
    _, meta = read(repo, sha, path)
    return {"path": path, **meta, "reading_scope": scope, "finding": finding, "verification": "静态源码可见/测试代码可见，未运行"}


def main():
    existing = ROOT / "08_证据索引与统计/持续补证_实习履历与本人源码.json"
    if existing.exists() and json.loads(existing.read_text("utf-8")).get("source_archives"):
        raise SystemExit("已有后续归档及比较依据，停止覆盖发现记录。")
    r, resume_meta = read("DavidHLP/DavidHLP.github.io", SITE, "src/content/information/zh-cn/introduction.md")
    raw = r.text
    # 剔除前置元数据，联系行及非专业人口信息；不记录剔除内容。
    body = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", raw, flags=re.S)
    contact = re.compile(r"微信|邮箱|电话|mailto:|tel:|城市:|城市：|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?<!\d)1[3-9]\d{9}(?!\d)", re.I)
    removed = sum(bool(contact.search(line)) for line in body.splitlines())
    clean = "\n".join(line for line in body.splitlines() if not contact.search(line))
    soup = BeautifulSoup(markdown.markdown(clean, extensions=["extra"]), "html.parser")
    for node in soup.select("script,style,img,iframe,form,input,button"):
        node.decompose()
    for node in soup.find_all(True):
        for key in list(node.attrs):
            if key.lower().startswith("on") or key in ["style", "src", "srcset"]:
                del node.attrs[key]
        if node.has_attr("href") and not node["href"].startswith(("https://", "http://", "#")):
            del node["href"]
    text = soup.get_text(" ", strip=True)
    assert not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?<!\d)1[3-9]\d{9}(?!\d)", text)
    expected = ["实习经历", "项目经历", "专业技能", "教育背景", "开源贡献与技术沉淀"]
    assert all(x in text for x in expected)
    folder = ROOT / "03_简历与候选人案例/核心后端履历_脱敏副本"
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / "DavidHLP_公开完整履历_脱敏转录.html"
    note = (
        "作者公开完整职业履历的整理者脱敏转录：删除联系区与人口信息，保留全部专业模块。"
        "任职与职责为本人自述；雇主为博彦科技，服务项目属于阿里云，不能写成阿里巴巴直接录用。"
        "项目为当前个人开源版本，未证实这些版本曾用于2026年初求职，也不证明项目导致录用。"
    )
    page = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>DavidHLP公开完整职业履历：脱敏转录</title><style>body{{margin:0;background:#f4f6f8;color:#18283b;font:17px/1.8 system-ui,"Microsoft YaHei",sans-serif}}main{{max-width:920px;margin:26px auto;padding:30px;background:white;border-radius:12px}}h2{{margin-top:32px;border-bottom:1px solid #cad5df;padding-bottom:10px}}h2 span{{font-size:13px;color:#567}}a{{overflow-wrap:anywhere;color:#175a9d}}aside{{background:#edf4ff;border-left:4px solid #4c779a;padding:16px}}li,p,div{{overflow-wrap:anywhere}}@media(max-width:600px){{main{{padding:20px;margin:0}}}}@media print{{body{{background:white}}main{{padding:0;margin:0;max-width:none}}}}</style><main><aside><strong>公开完整专业履历：脱敏转录</strong><p>{html.escape(note)}</p><p><a href="https://davidhlp.github.io/about/">作者原页</a> · <a href="{resume_meta['url']}">固定来源</a> · 采集日期：2026-10-23</p></aside><article>{soup}</article></main></html>'''
    target.write_text(page, encoding="utf-8")
    resume = {
        "discovery_key": "DavidHLP", "author": "贺恋棚 / DavidHLP", "title": "近期后端交付实习完整公开履历直接点名两个本人开源项目",
        "url": "https://davidhlp.github.io/about/", "fixed_source": resume_meta,
        "source_repo": "DavidHLP/DavidHLP.github.io", "source_sha": SITE, "source_commit_time": "2026-10-05T05:34:00Z",
        "profile_type": "完整公开HTML职业履历的脱敏专业模块转录", "professional_modules": expected,
        "reading_scope": "公开HTML正文及固定来源全部专业模块已读", "local_path": target.relative_to(ROOT).as_posix(),
        "redacted_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "track": "后端", "recruitment": "实习", "event_time": "2026.01–2026.06", "recent_status": "近期确认（作者自述明确起止月）",
        "outcome": {"employer": "博彦科技", "role": "后端开发实习生", "client_project": "阿里云专有云·安骑士主机安全", "employer_is_client": False, "employer_verified": False, "grade": "未披露", "ssp": False},
        "internship_responsibilities": ["集群GPU资源接入聚合", "AI资产识别相关后端逻辑", "SQL查询优化", "Arthas线上问题定位与回归", "containerd/Harbor TLS链排查"],
        "education": "洛阳师范学院，数据科学与大数据技术本科；原稿2021.09–2026.07",
        "direct_project_links": [
            {"name": "UltiCode", "url": "https://github.com/DavidHLP/UltiCode", "basis": "固定履历L44–45点名并直接链接；正文称个人开源平台", "relation": "直接点名本人项目"},
            {"name": "ResiCache", "url": "https://github.com/DavidHLP/ResiCache", "basis": "固定履历L63–64点名并直接链接；正文称个人开源扩展", "relation": "直接点名本人项目"},
        ],
        "privacy": {"original_saved": False, "removed_contact_or_demographic_lines": removed, "contact_pattern_after": False, "external_images": 0, "professional_module_presence_checked": True, "visual_review": "待浏览器检查"},
        "limits": ["雇主为博彦科技，不能冒称阿里直签大厂实习", "任职与个人职责未企业独立核验", "未披露SSP", "现版项目含实习之后的实现，不证明求职当时水平", "履历没有提供企业内部源码"],
    }
    ulti_modules = [
        code("DavidHLP/UltiCode", ULTI, "services/submission/src/main/java/com/ulticode/modules/queue/outbox/dispatcher/JudgeOutboxDispatcher.java", "L47–206类与dispatch/回退重试路径", "dispatch存在事务边界、队列不可用时保留可重试outbox、投递与退避路径；不是仅README架构词"),
        code("DavidHLP/UltiCode", ULTI, "services/submission/src/main/java/com/ulticode/modules/submission/mapper/SubmissionMapper.java", "L44–143租约、generation和attempt条件写入", "结果写回SQL同时限制generation与current_attempt_id；租约恢复与新attempt领取也有条件更新。只证明该机制代码存在，不证明全部竞态正确"),
        code("DavidHLP/UltiCode", ULTI, "services/auth/src/main/java/com/ulticode/auth/refreshtoken/service/RefreshTokenService.java", "L55–156刷新令牌创建、轮换与拒绝分支", "刷新令牌哈希、用途/有效期/旧令牌消费及轮换事务有源码；不据此宣称安全认证已通过"),
        code("DavidHLP/UltiCode", ULTI, "services/judge-runtime/src/test/java/com/ulticode/modules/queue/port/adapter/JudgeStreamRedisIntegrationTest.java", "测试类及命名、主要断言/测试容器路径", "有面向Redis Streams的集成测试代码；未运行，不能将测试存在写为已通过"),
    ]
    resi_modules = [
        code("DavidHLP/ResiCache", RESI, "src/main/java/io/github/davidhlp/spring/cache/redis/cache/SyncSupport.java", "L137–186同步与独占写的角色选择", "重入、leader/follower及独占写路径明确分开，避免把写操作作为读请求合并"),
        code("DavidHLP/ResiCache", RESI, "src/main/java/io/github/davidhlp/spring/cache/redis/cache/SyncRole.java", "L158–190 follower超时；L286–327注册/完成/清理", "ConcurrentHashMap存in-flight Future，以putIfAbsent选leader；成功或异常完成，按key和future身份删除，存在具体并发机制"),
        code("DavidHLP/ResiCache", RESI, "src/main/java/io/github/davidhlp/spring/cache/redis/cache/EarlyRefresh.java", "L51–94脚本与L238–287执行参数", "Lua检查payload.version后缩短TTL；原值版本是CAS依据，区别于封装格式版本"),
        code("DavidHLP/ResiCache", RESI, "src/test/java/io/github/davidhlp/spring/cache/redis/cache/SyncSupportSingleFlightTest.java", "定点核读L88起并发共享、L375起异常传播、L427起重入、L448起超时测试", "覆盖单次回源/共享结果、leader异常、重入不自等待、follower超时等场景的测试代码；未运行"),
        code("DavidHLP/ResiCache", RESI, "src/test/java/io/github/davidhlp/spring/cache/redis/cache/EarlyExpirationHandlerRaceConditionIntegrationTest.java", "测试方法、并发场景和断言定点核读", "有提前过期与并发写入的竞态集成测试代码；尚未本地运行或复现"),
    ]
    projects = []
    for name, sha, date, modules in [("UltiCode", ULTI, "2026-10-23T15:12:39Z", ulti_modules), ("ResiCache", RESI, "2026-10-09T15:30:33Z", resi_modules)]:
        license_response, license_meta = read("DavidHLP/" + name, sha, "LICENSE")
        projects.append({
            "name": name, "repo": "DavidHLP/" + name, "sha": sha, "source_commit_time": date,
            "fixed_repo": f"https://github.com/DavidHLP/{name}/tree/{sha}", "fork": False,
            "ownership_evidence": "作者完整专业履历直接点名、链接并称个人开源；不把所有依赖/第三方代码算本人独立完成",
            "license": {"label": "MIT", "actual_text_read": True, **license_meta, "note": "UltiCode为完整标准MIT正文；ResiCache有MIT标题/许可与免责声明，但缺常见标准MIT尾部责任段，应保留其实际文本而不只依API标签"},
            "implementation_and_tests": modules, "run_status": "未运行", "archive_status": "未制作源码ZIP；固定源码与具体阅读路径已核，主代理可据需归档",
            "reading_scope": "仅所列文件与方法的定点静态核读，不称整仓审计",
            "recommendation": "UltiCode适合研究业务闭环、消息故障与结果竞争；ResiCache适合研究缓存并发、状态清理与真实集成测试。按实际模块读，不能由文件规模推项目质量。",
            "limitations": ["无本地构建/测试证据", "未核每次提交的个人工作占比或AI辅助比例", "当前源码晚于实习开始时间，不能证明求职因果", "源码存在不等于生产性能或成熟度通过"],
        })
    interview_response, interview_meta = read("DavidHLP/DavidHLP.github.io", "6f3d114a6ef9eb08b730f5f4740afe5b7d22d426", "src/content/note/zh-cn/java-internship-interview-blog-polished.md")
    synthesis_response, synthesis_meta = read("DavidHLP/DavidHLP.github.io", SITE, "src/content/note/zh-cn/java-internship-interview-blog-polished.md")
    interview = {
        "title": "从一面到二面：Java后端实习面试复盘", "source": interview_meta, "author_relation": "本人站公开文章，自称基于两轮真实Java后端实习面试整理；未给企业名或逐轮原始录音",
        "publication_time": "2026-02-25 00:00:00+08:00（原稿timestamp）", "interview_event_time": "未知", "strict_recent_interview": False,
        "recruitment": "实习", "company": "未知", "outcome": "未知", "ssp": False,
        "reading_scope": "713行原文已取得；定点核读来源说明、3.1/3.2项目追问、4.1–4.5二面追问、5排障、7项目表达和结尾边界；非逐字逐行技术审定",
        "material_type": "自述面试问题与推荐回答模板/事后工程化补充混合",
        "question_answer_boundary": "文中的推荐回答模板、能力雷达主观分数和后续补齐建议，不等于候选人在面试当场实际答出；文章声明两轮约30/45分钟，不拆成两位候选人",
        "project_relationship": "原文追问Spring Cache二开和OJ沙箱；与履历ResiCache/UltiCode领域对应，但原文未点名仓库名，所以只能标主题/实现领域关联，不能保证同一版本或当年面试项目",
        "version_difference": "原文OJ用Kafka作回答，当前UltiCode所核版本用Redis Streams；必须保留差异，不能把旧面经答案贴为现版实现",
        "questions": [
            {"section": "3.1", "question": "Spring Cache二开怎样防穿透/击穿/雪崩", "source_lines": "L78–112", "code_module": "ResiCache SyncSupport/SyncRole、EarlyRefresh", "relation": "主题对应，不证明原面试仓库版本"},
            {"section": "3.2", "question": "OJ怎样用Docker运行不可信用户代码", "source_lines": "L114–163", "code_module": "UltiCode judge-runtime，沙箱细节本轮未审", "relation": "主题对应，Docker限制不能凭模板宣称全部源码已核"},
            {"section": "4.2", "question": "为什么OJ引入Kafka", "source_lines": "L279–316", "code_module": "现版JudgeOutboxDispatcher/Redis Streams", "relation": "历史回答与当前实现不同；可比较异步投递需求，不混写具体中间件"},
            {"section": "4.4", "question": "缓存责任链如何避免过度设计", "source_lines": "L358–387", "code_module": "ResiCache职责拆分", "relation": "主题对应，需结合实际文件考察取舍"},
            {"section": "5", "question": "高CPU如何定位进程、线程和调用链", "source_lines": "L429–513", "code_module": "履历Arthas排障职责", "relation": "知识/专业经历交叉，不是已复现线上事故"},
        ],
        "current_synthesis": {**synthesis_meta, "kind": "synthesis", "status": "provisional", "boundary": "当前101行文章自称综合能力模型，不另计为第二份真实面经"},
        "cannot_link_to_specific_employer_offer": True,
    }
    data = {
        "research_date": "2026-10-23", "scope": "近期实习完整专业履历→作者直接点名本人项目→可审源码/测试；不扩博士对照",
        "existing_candidate_checks": [
            {"id": "CV23", "author": "zhh2001", "source": "https://raw.githubusercontent.com/zhh2001/zhh2001.github.io/bdd665acc8d73c80aefc7260fdeeef598fabf48f/docs/resume.md", "result": "内部项目只列名称/角色，无公开源码直接链接；主页只有账号链接，不能拿pinned个人仓库填成内部项目源码", "stop": "保留原缺口，不继续追内部未公开代码"},
            {"id": "CV24", "author": "huomalxq", "source": "https://raw.githubusercontent.com/huomalxq/huomalxq.github.io/6b8add7398dcbf1f79fd4c850b0c0b047344bc4d/docs/study/teco-rag-project-summary.md", "result": "问数Agent复盘与Teco-RAG复盘没有直接开源代码链接；同账号spec-decode-learning不冒充企业问数实现", "stop": "补读Teco复盘后确认本轮不新增源码关系，不否认以后可公开"},
        ],
        "candidate": resume, "projects": projects, "interview": interview,
        "chain_audit": {
            "internship_to_profile": "直接：完整本人职业履历列雇主、客户项目、岗位与年月；仍属自述",
            "profile_to_named_personal_repos": "直接：同页点名且直接链接UltiCode和ResiCache，不是同账号猜测",
            "repos_to_implementation_tests": "直接：所列固定源码/测试文件可读，未执行",
            "profile_to_interview": "本人站原文；具体面试公司/事件日期/录用结果缺失",
            "named_repos_to_interview": "主题对应，原文未直接点名这两个仓库名，且Kafka/Streams版本有区别",
            "interview_to_internship_offer": "未建立，不能把两轮复盘等同博彦录用流程",
            "ssp": "未披露，无新增SSP证据",
        },
        "remaining_gap": "闭合了一个近期后端实习完整履历→本人直接点名源码的样本，但雇主是交付企业，非互联网大厂直签；没有近期Agent正式SSP或同一录用流程完整四段链。",
        "search_paths": ["中英文近期实习/完整CV/项目链接检索", "作者公开about页→固定GitHub履历源→点名仓库", "固定源码定点实现/测试→站内原版面经与当前综合版比较"],
        "no_execution_or_outreach": True,
    }
    out = ROOT / "08_证据索引与统计/持续补证_实习履历与本人源码.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": out.as_posix(), "candidate": resume["author"], "resume": resume["local_path"], "read_code_files": sum(len(p["implementation_and_tests"]) for p in projects), "ssp": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
