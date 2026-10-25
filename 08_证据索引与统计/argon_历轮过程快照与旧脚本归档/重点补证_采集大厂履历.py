"""只读公开资料；原PDF仅内存读取，输出专业模块完整的脱敏副本与独立发现JSON。"""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import re
import warnings

import fitz
import requests

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "08_证据索引与统计/重点补证_大厂实习履历.json"
DEST = ROOT / "03_简历与候选人案例/核心后端履历_脱敏副本"
QA = Path("C:/Users/GW/.codex/visualizations/2026/10/23/01a16839-9742-7672-812b-1576a3dd064f")
S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0"
KV_SHA = "d7132bba33fb2aec2ccd802c357dc1cd1f74fb5e"
Q_SHA = "f0d6380e9846f84f10be5f284fec40d42cfb34f9"


def fetch_file(repo, sha, path):
    url = f"https://raw.githubusercontent.com/{repo}/{sha}/{path}"
    r = S.get(url, timeout=40)
    r.raise_for_status()
    return {"repo": repo, "sha": sha, "path": path, "url": url, "status": r.status_code,
            "line_count": len(r.text.splitlines()), "sha256": hashlib.sha256(r.content).hexdigest()}


def andrew_copy():
    url = "https://andrewtheterp.com/assets/download/resume.pdf"
    r = S.get(url, timeout=40)
    r.raise_for_status()
    raw = r.content
    d = fitz.open(stream=raw, filetype="pdf")
    before = "\n".join(p.get_text() for p in d)
    marker = "EDUCATION"
    professional_before = before[before.index(marker):]
    boundary = min(x.y0 for x in d[0].search_for(marker)) - 3
    d[0].add_redact_annot(fitz.Rect(0, 0, d[0].rect.width, boundary), fill=(1, 1, 1))
    removed_links = 0
    for p in d:
        for link in p.get_links():
            p.delete_link(link)
            removed_links += 1
        p.apply_redactions()
    d.set_metadata({})
    d.del_xml_metadata()
    d.xref_set_key(-1, "Info", "null")
    assert sum(len(p.get_images()) for p in d) == 0
    data = d.tobytes(garbage=4, deflate=True, clean=True)
    d.close()
    c = fitz.open(stream=data, filetype="pdf")
    after = "\n".join(p.get_text() for p in c)
    normalize = lambda v: re.sub(r"\s+", "", v)
    assert normalize(professional_before) == normalize(after)
    assert not re.search(r"[\w.+-]+\s*@\s*[\w.-]+\.[A-Za-z]{2,}", after)
    assert not re.search(r"(?:mailto:|tel:|微信|WeChat|phone:|E-?mail:)", after, re.I)
    assert not re.search(r"\+?\d[\d ()-]{8,}\d", after)
    modules = ["EDUCATION", "EXPERIENCE", "PROJECTS", "TECHNICAL SKILLS"]
    assert all(m in after for m in modules)
    assert all(not c.metadata.get(k) for k in ["title", "author", "subject", "keywords", "creator", "producer", "creationDate", "modDate"])
    assert sum(len(p.get_links()) + len(list(p.annots() or [])) for p in c) == 0
    DEST.mkdir(parents=True, exist_ok=True)
    output = DEST / "AndrewWang_字节后端与Agent实习_公开完整简历_脱敏副本.pdf"
    if output.exists():
        raise RuntimeError("副本已存在，停止覆盖")
    output.write_bytes(data)
    QA.mkdir(parents=True, exist_ok=True)
    renders = []
    for i, p in enumerate(c):
        png = QA / f"重点补证_AndrewWang_脱敏简历_第{i+1}页.png"
        p.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save(png)
        renders.append(str(png))
    result = {
        "url": url, "source_status": r.status_code, "retrieved_on": "2026-10-23",
        "fixed_git_sha": None, "fixed_git_sha_note": "作者站点实时PDF；未取得网站源仓固定提交，以此次原文件内容hash标识版本",
        "source_sha256": hashlib.sha256(raw).hexdigest(), "original_saved": False,
        "local_path": output.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data), "pages": len(c), "professional_modules": modules,
        "professional_modules_complete": True, "professional_text_unchanged_after_education": True,
        "packaging_type": "整理者制作的公开完整专业履历脱敏PDF副本；不是未经修改的作者原件",
        "redaction": {"header_contact_region_removed": True, "all_link_annotations_removed": removed_links,
                      "contact_regex_hits": 0, "image_or_qr_count": 0, "metadata_nonempty_private_fields": 0,
                      "annotation_count": 0, "visible_url_types": "正文保留Research Report/Technical Report/Live Demo文字，无联系URL；实际专业链接列在JSON",
                      "visual_review": "待目视渲染图"},
        "qa_images": renders,
    }
    c.close()
    return result


def main():
    if OUT.exists():
        raise RuntimeError("独立发现JSON已存在，停止覆盖")
    jobs = [
        ("shufengc/distributed-kv-store", KV_SHA, p) for p in ["README.md", "raft/raft.go", "kv/server/server.go", "LICENSE"]
    ] + [("shufengc/QuantHarbor", Q_SHA, p) for p in ["README.md", "src/agents/base_agent.py", "src/utils/code_executor_async.py", "src_rag/core/report_pipeline.py", "src_rag/core/llm_client.py", "demo/backend/app.py", "docs/migration_notes.md", "LICENSE"]]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        files = list(pool.map(lambda j: fetch_file(*j), jobs))
    pdf = andrew_copy()
    data = {
        "date": "2026-10-23", "scope": "近期互联网大厂普通后端/Agent应用工程实习者，公开履历与直接项目链；独立发现，不改主表/不占ID",
        "recent_window": ["2024-10-23", "2026-10-23"],
        "counts": {"new_core_complete_redacted_resume": 1, "new_core_profile_fragment": 1, "new_verified_ssp": 0, "new_original_source_archives": 0},
        "new_core_complete_profiles": [{
            "key": "AndrewWang_wandrew0", "author": "Andrew Wang", "home": "https://andrewtheterp.com/",
            "track": "后端与Agent应用工程", "recruitment": "实习", "profile_type": "本人站公开完整PDF专业模块脱敏副本",
            "education": ["University of Maryland，CS本科，2026.05", "Carnegie Mellon University，CS硕士，2026.08–2028.01预计"],
            "outcomes": [
                {"company": "ByteDance (TikTok Shop)", "role": "Backend Software Engineer Intern — Creator Assistant", "time": "2026.05–2026.08", "basis": "公开PDF EXPERIENCE第一段", "content": "Go后端集成内部ReAct Agent平台；配置skills/MCP tools/knowledge；实现live-data MCP、tool-schema token优化；RPC自动执行、工具技能trace、盲评的Agent评测harness；模型上下文与工具调用trace viewer；作者称面向全部Affiliate creators上线"},
                {"company": "ByteDance (TikTok Shop)", "role": "Backend Software Engineer Intern — Journey Builder", "time": "2025.05–2025.08", "basis": "公开PDF EXPERIENCE第三段", "content": "React onboarding UI；Go/Kitex服务；GORM/MySQL指标接口；内部CI/CD与生产问题处理"},
            ],
            "event_region": "履历为美国高校背景，PDF没有明确写出两段字节实习工作地；不推定中国校招档位",
            "grade": "未披露", "enterprise_verified": False, "ssp_relation": "没有SSP/SP/意向书的直接证据",
            "attachment": pdf,
            "projects": [
                {"name": "UMIACS Wiki Chatbot", "period": "2024.08–2024.12", "relation": "PDF PROJECTS直接点名六人团队与本人Developer身份，并直接链接Technical Report", "document": "https://andrewtheterp.com/assets/download/Chatbot.pdf", "source_repo": None, "boundary": "本人贡献为LangChain/Qdrant RAG与LLaMA3 LoRA；项目开始在近期窗口之前、结束在窗口内；报告和PDF未给直接GitHub源码链接"},
                {"name": "Doodles and Character Classifier", "period": "2024.07–2024.08", "relation": "PDF直接点名并链接Live Demo", "demo": "https://imageclassifier.andrewtheterp.com", "source_repo": None, "boundary": "早于近期窗口；demo页面未给GitHub源码；同账号ImageClassifier仓README对应相似用途，但没有直接履历到源码链接，不补成已确认求职项目"},
                {"name": "Creator Assistant Agent / Journey Builder", "relation": "实习职责直接点名", "source_repo": None, "boundary": "企业内部系统；未发现对外源码，不能以同账号仓库代替"},
            ],
            "interview": None,
            "reading_reason": "当前最贴近Agent应用后端实习的完整专业CV之一：职责明确到MCP工具、真实对话评测、trace可观测、上线使用；适合看简历怎样写工程闭环",
            "limits": ["职责、使用规模和上线结果均为作者自述，未企业独立核验", "不是SSP证明", "未取得本人面经", "未闭合完整履历→本人公开源码", "没有将内部项目称为可复用开源项目"],
        }],
        "new_core_partial_profiles": [{
            "key": "shufengc", "author": "Shufeng (Alex) Chen", "home": "https://shufengc.dev/", "source_status": 200,
            "profile_type": "本人专业主页履历片段，缺完整教育模块且未发现CV/PDF直链", "is_full_resume": False,
            "track": "后端应用工程；主页同时列研究经历，不因此归为博士算法对照", "recruitment": "实习",
            "outcomes": [
                {"company": "Tencent · Cloud Computing Group", "role": "Software Engineer Intern", "time": "2025.07–2025.08", "basis": "本人站Experience第二段", "content": "Kubernetes分布式推理微服务；Spring Boot/Security、Redis/MySQL集群管理和调度API；云metadata同步与telemetry；规模及性能为作者自述"},
                {"company": "Stripe · Cash & Banking Infrastructure", "role": "Software Engineer Intern", "time": "2026.05–2026.08", "basis": "本人站Experience第一段", "content": "Java/gRPC的SFTP配置与onboarding接口、validation/feature flags与SSH host-key服务"},
            ],
            "grade": "未披露", "enterprise_verified": False, "interview": None,
            "direct_project_relation": "同一主页Projects中的GitHub按钮逐项直接链接以下具体仓库；关系强于仅同账号，但不能据此证明求职时使用或项目促成录用",
            "projects": [
                {"name": "Distributed Key-Value Store", "repo": "shufengc/distributed-kv-store", "sha": KV_SHA,
                 "url": f"https://github.com/shufengc/distributed-kv-store/tree/{KV_SHA}", "category": "TinyKV课程框架上的分布式系统实现",
                 "ownership": "README Acknowledgements明确基于PingCAP Talent Plan/TinyKV；网络模拟/测试框架/协议定义来自课程，作者自述实现Raft、raftstore、scheduler、事务；本轮仅核2核心文件存在实质实现，未逐diff审定全部独立贡献",
                 "license": "LICENSE原文Apache-2.0已读取，不能把继承框架所有源码算个人原创",
                 "findings": [
                     {"status": "已见实现", "claim": "raft.go包含候选/Leader切换、投票、AppendEntries和多数派提交索引逻辑", "file": "raft/raft.go", "ranges": ["L253–333", "L488–532", "L722–952"]},
                     {"status": "已见实现", "claim": "事务handler包含local latches、write conflict/lock检查、Prewrite的value/lock写入、Commit的write record与释放锁", "file": "kv/server/server.go", "ranges": ["L87–209"]},
                     {"status": "未核", "claim": "未运行课程测试；未证明所有partition场景linearizability或独立实现比例；当前固定版本不自动代表2025腾讯投递时项目"},
                 ], "reading": "后端进阶选读：先看课程任务边界，再看Raft quorum提交与MVCC prewrite/commit；不作为普通业务闭环/大厂SSP充分条件"},
                {"name": "QuantHarbor", "repo": "shufengc/QuantHarbor", "sha": Q_SHA,
                 "url": f"https://github.com/shufengc/QuantHarbor/tree/{Q_SHA}", "category": "多Agent金融研究与RAG应用；当前静态风险需先核",
                 "ownership": "主页直接列为本人项目；迁移文档明确移除lecture目录运行依赖、从course-style文档转product-style文档；课程/外部框架原始来源与具体独立贡献尚未完整核清",
                 "license": "LICENSE原文GNU GPL v3已读取；未归档运行环境或API密钥",
                 "findings": [
                     {"status": "已见实现", "claim": "BaseAgent保存/恢复conversation、round、tool dependencies和executor state；迭代上限与每轮checkpoint", "file": "src/agents/base_agent.py", "ranges": ["L95–224", "L302–344", "L447–510"]},
                     {"status": "已见实现", "claim": "异步代码executor执行模型代码并捕获stdout/stderr；提供完整Python builtins与os/sys，代码在线程池exec", "file": "src/utils/code_executor_async.py", "ranges": ["L25–73", "L253–307"]},
                     {"status": "静态风险", "claim": "所谓sandbox没有在核读文件中建立进程/文件系统/网络权限隔离；不能据此称安全执行沙箱", "file": "src/utils/code_executor_async.py", "ranges": ["L25–73", "L266–279"]},
                     {"status": "静态风险", "claim": "RAG pipeline导入src.agents.analyst_agent/retriever_agent/writer_agent，固定树实际在src_rag/agents；Web backend导入src.memory，固定树没有该模块。属于可直接核对的入口路径不一致，未执行验证", "file": "src_rag/core/report_pipeline.py + demo/backend/app.py", "ranges": ["report_pipeline.py L6–8", "app.py L20–23"], "tree_evidence": "重点补证_quant_tree.json，recursive树truncated=false"},
                     {"status": "已见实现", "claim": "LLMRouter捕获primary异常后尝试fallback；没有据此证明断点任务幂等/重试不重复外部副作用", "file": "src_rag/core/llm_client.py", "ranges": ["L60–66"]},
                     {"status": "文档宣称/未核", "claim": "README宣称138PDF/4577页/8309chunks、长报告、citation tracing等；未复现，无独立任务成功率/成本/延迟benchmark；固定树未见单元/集成测试文件，smoke_test_providers.py仅可算provider脚本"},
                 ], "reading": "待核/反例选读：状态持久化与真实权限隔离要分开；先排入口导入风险，再判断完整工程可复现性。不能当已验证成熟Agent项目推荐"},
                {"name": "Patton Food / OnlineOrder", "url": "https://github.com/shufengc/OnlineOrder", "boundary": "README明确each team member deployment for grading与coursework用途；团队课程业务项目，未核具体个人贡献，不扩为独立推荐"},
                {"name": "PDF-AI", "url": "https://github.com/shufengc/pdfai", "boundary": "README Reference明确来源Laioffer Full Stack课程Next AI并扩展PDF对话；基础RAG课程扩展，不满足成熟非toy Agent依据，不扩推荐"},
            ],
            "limits": ["履历片段不计完整CV", "无SSP档位/本人面经", "未企业独立核验", "4仓为主页直接点名，仍不能将当前项目倒推录用因果", "没有把课程和团队框架全部认定个人原创"],
        }],
        "read_source_files": files,
        "archives": [],
        "archive_status": "本轮先交履历副本、固定SHA与静态风险；源码ZIP未生成，不计入已打包数量",
        "search_paths": [
            {"path": "中文近期后端/Agent履历与CV搜索→原作者个人站/GitHub", "queries": ['"2025" "后端" "实习经历" "项目经历" "github.com" -模板 -范文 -招聘', '"2026" "Agent" "实习" "CV" "GitHub" -模板 -招聘 -research', '"腾讯" "2025" "后端" "resume.pdf"'], "result": "找到shufengc主页直链项目；课程/团队边界均回原README核查，未找到完整教育CV"},
            {"path": "英文大厂backend intern resume→本人官网PDF→PDF实际链接与技术报告", "queries": ['"2025" "resume" "ByteDance" "Projects" "github.com" -research -PhD -hiring', '"ByteDance" "Backend Software Engineer Intern" "resume.pdf" -job -hiring'], "result": "找到Andrew完整CV，直接核2025后端与2026Agent实习；PDF项目技术报告/LiveDemo未给特定GitHub源码，缺口保留"},
        ],
        "excluded_or_unclosed": [
            {"source": "https://geoffreywtech.me/resume", "reason": "腾讯实习2019，非本轮近期"},
            {"source": "https://hills-code.github.io/CV.pdf", "reason": "TikTok后台实习2022；近期腾讯为研究，未作核心近期应用工程新样本"},
            {"source": "GitHub模板/无实习个人页/招聘工具", "reason": "不计成功实习者CV"},
        ],
        "unresolved_gap": "尚未闭合近期大厂Agent应用实习完整CV→本人可审成熟源码→本人具体面经→SSP录用。已有两个不同检索路径的实读进展，不能宣称全网没有。",
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(OUT), "counts": data["counts"], "pdf": pdf["local_path"], "qa_images": pdf["qa_images"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
