"""整合公开GitHub SSP证据；只处理本地资料，不运行第三方源码。"""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import quote
from collections import Counter
import ast
import csv
import hashlib
import io
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "08_证据索引与统计"
REPORT = ROOT / "01_调研报告"
ARCHIVES = ROOT / "05_项目源码归档"
if (INDEX / "github_ssp_round2_records.json").exists():
    raise SystemExit("已增加第二轮资料；请运行整合GitHub_SSP第二轮.py，避免恢复旧的候选人分类与阅读入口。")
DATE = "2026-10-23"


def read(path):
    return path.read_text(encoding="utf-8-sig")


def write(path, value):
    newline = "\r\n" if not path.exists() or b"\r\n" in path.read_bytes() else "\n"
    with path.open("w", encoding="utf-8", newline="") as stream:
        stream.write(value.replace("\r\n", "\n").replace("\r", "\n").replace("\n", newline))


def load(name):
    return json.loads(read(INDEX / name))


def dump(name, value):
    write(INDEX / name, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def merge(old, added):
    records = {r["id"]: r for r in old}
    records.update({r["id"]: r for r in added})
    return list(records.values())


def source(repo, sha, path, start=None, end=None):
    fragment = "" if start is None else f"#L{start}" + (f"-L{end}" if end else "")
    return "https://github.com/" + repo + "/blob/" + sha + "/" + quote(path, safe="/") + fragment


backend = load("github_ssp_backend_discovery.json")
systems = load("github_ssp_systems_discovery.json")
agent = load("github_ssp_agent_discovery.json")
java = backend["accepted_candidates"][0]
muluo, lin = systems["cases"]
weak, dong = agent["candidates"]
new_manifest = json.loads(read(ARCHIVES / "GITHUB_SSP_SOURCE_MANIFEST.json"))
by_project = {m["id"]: m for m in new_manifest}
CALVIN_URL = "https://www.nowcoder.com/discuss/353154880351182848"
LIN_URL = lin["ssp_evidence"]["source_url"]
JAVA_SHA = java["fixed_commit"]
JAVA_REPO = java["repo"]
DONG_SHA = dong["ssp_source"]["commit"]

candidate_new = [
    {
        "id": "CV10", "title": "CalvinNeo：腾讯SSP实习转正与三个本人C++项目",
        "url": CALVIN_URL, "author": "CalvinNeo", "date": "2019届硕士；题名2018与正文去年相互对应，合理记为2018年求职结果；页面2019-03-15编辑，非已确认首发时间",
        "role": "C++后台/系统工程；历史实习转正及校招", "outcome": "腾讯SSP（实习转正）与阿里云A等offer，均为本人自述",
        "outcome_evidence": "同一篇原文开头明确SSP，在GitHub段逐一介绍并直接链接三个本人项目；无企业独立核验。",
        "evidence_excerpt": "我是2019届的硕士，在去年拿到了腾讯SSP（实习转正）和阿里云A等Offer。",
        "document_type": "本人求职复盘与阿里云面试主题；非完整简历",
        "anonymous_background": "原文自述C9硕士、本科跨专业、腾讯实习；不保存联系方式。",
        "stack": ["C++14/17", "词法/语法分析", "UDP可靠传输", "Raft", "Linux", "gRPC", "测试与调试"],
        "projects": ["CFortranTranslator：Fortran77/90到C++14翻译器", "ATP：参考libutp思想实现的可靠传输库", "Nuft：参考Raft论文实现的共识库"],
        "project_urls": ["https://github.com/CalvinNeo/CFortranTranslator", "https://github.com/CalvinNeo/ATP", "https://github.com/CalvinNeo/Nuft"],
        "source_summary": "作者明确说面试官对翻译器感兴趣；ATP源于课程作业，Nuft源于Raft论文。阿里云段讨论Linux、项目深挖、C++与系统设计。",
        "original_analysis": "本轮最完整的本人SSP自述→本人项目→求职/面试主题关联之一。价值在于不同项目各有机制深度；不证明三个项目单独导致SSP。",
        "strengths": ["本人正文直接建立项目关系，优于同名账号猜测", "三个项目均有固定源码及许可证", "项目设计与实现、失败处理和测试可具体定位"],
        "weaknesses": ["历史2018年结果，不能代表2026实习门槛", "腾讯SSP是实习转正，不是阿里云SSP，也不是三项目的效果证明", "没有腾讯逐轮逐题记录或完整成功者CV", "附的是当前可取得固定版本，非2018求职快照"],
        "recommended_use": "优先对照PRO14–16的源码优缺点与INT57；学习解释动机、个人工作、边界与实验，不复刻一串项目名称。",
        "access_level": "牛客正文实际已读；原链接163036重定向，动态页复查可能返回空壳",
        "confidence": "B：第一人称自述与项目关系可核；录用与项目贡献未经企业独立验证", "category": "候选人资料", "retrieved_at": DATE,
    },
    {
        "id": "CV11", "title": "linyacool／林亚：历史SSP学习复盘与本人WebServer",
        "url": LIN_URL, "author": "linyacool", "date": lin["source_date_note"], "role": "C++后台/基础架构；历史秋招与实习项目",
        "outcome": "标题自述offer大多是SSP；列字节、网易游戏、阿里云、华为、腾讯，未逐家公司定档",
        "outcome_evidence": lin["ssp_evidence"]["verification"], "evidence_excerpt": lin["ssp_evidence"]["excerpt"],
        "document_type": "本人学习与求职复盘；非逐轮面经、非完整简历",
        "stack": ["C++11", "Linux", "Reactor", "epoll ET", "线程池", "HTTP", "异步日志", "定时器"],
        "projects": ["本人静态WebServer，学习并借鉴muduo"], "project_urls": ["https://github.com/linyacool/WebServer"],
        "source_summary": lin["author_project_link_evidence"]["excerpt"],
        "original_analysis": "原文直接链接本人项目；设计、测试条件、困难及改进材料齐全，适合比较项目表达和基础深度。",
        "strengths": lin["project_sources"][0]["strengths"], "weaknesses": lin["limits"] + ["README面试问题.md为死链，不算已读面经"],
        "recommended_use": "优先读PRO17的并发模型、测试及改进、遇到的困难；重点看作者如何披露复用和不足。",
        "access_level": "本人牛客正文与固定源码、文档已读；README所指面试问题文档不存在",
        "confidence": "B：本人SSP自述与项目关系强；逐轮面经、具体公司SSP档位未确认", "category": "候选人资料", "retrieved_at": DATE,
    },
    {
        "id": "CV12", "title": "muluoleiguo：2021秋招SSP自述与Muluo系统库项目材料",
        "url": muluo["ssp_evidence"]["source_url"], "author": "muluoleiguo", "date": "2021年秋招（原文明确）", "role": "Linux C++服务器/游戏研发；历史校招",
        "outcome": "百度、阿里、字节、网易等offer中有SP及SSP，未指明哪家；最终选网易互娱不等于网易SSP",
        "outcome_evidence": muluo["ssp_evidence"]["verification"], "evidence_excerpt": muluo["ssp_evidence"]["excerpt"],
        "document_type": "本人结果自述＋项目材料与面经汇总，非完整简历",
        "stack": ["C++11", "Linux网络IO", "日志", "JSON", "线程池", "RPC", "协程"],
        "projects": ["Muluo：同仓展示的日志/JSON/网络/RPC/协程材料，未找到独立完整可构建源码"],
        "project_urls": [muluo["project_sources"][0]["source"]["url"]],
        "source_summary": "可读项目模块说明、连接生命周期片段和日志性能讨论；同仓网易面经含外部链接，不能全算仓主亲历。",
        "original_analysis": muluo["project_sources"][0]["recommended_use"],
        "strengths": muluo["project_sources"][0]["strengths"], "weaknesses": muluo["project_sources"][0]["weaknesses"] + muluo["limits"],
        "recommended_use": "作为项目拆分与追问导航；不将文档清单当已实现全量能力。本仓只给链接与短摘录，不整库归档。",
        "source_findings": muluo["project_sources"][0]["inspect_paths"], "interview_sources": muluo["interview_sources"],
        "license_notes": "未见根总许可证，子目录许可证不授权整个资料仓库；未归档。",
        "access_level": "固定commit README、项目材料与所选题目已读", "confidence": "B：本人SSP自述；项目实现完整度与面经作者关系未闭环", "category": "候选人资料", "retrieved_at": DATE,
    },
    {
        "id": "CV13", "title": "dong03：历史CV/多模态SSP自述、协作面经与同账号研究项目",
        "url": dong["ssp_source"]["url"], "author": "dong03", "date": "面经明确2022年；仓库固定commit为2023年；SSP具体发放年未写明",
        "role": "CV/多模态算法邻近参考；非Agent工程岗",
        "outcome": dong["ssp_status"], "outcome_evidence": "README第一人称明确SSP，未提供具体公司定档或企业证明。", "evidence_excerpt": dong["ssp_excerpt"],
        "document_type": "本人SSP自述、知识总结与多人协作面经；非完整简历",
        "stack": ["PyTorch", "CV/多模态", "模型训练", "跨数据集评测", "算法与数学"],
        "projects": ["同账号MVSS-Net图像篡改检测研究项目；面经没有点名该项目"],
        "project_urls": ["https://github.com/dong03/MVSS-Net"],
        "source_summary": dong["interview_materials"]["author_scope"], "original_analysis": dong["same_account_project_relation"]["relation_strength"],
        "strengths": dong["same_account_project_relation"]["recommended_lessons"], "weaknesses": dong["limitations"] + ["同账号关系不等于本人贡献、简历使用或获SSP的因果关系"],
        "recommended_use": "补充算法项目的数学、实现、数据划分与跨域指标追问；不纳入近期Agent要求。",
        "source_findings": [dong["same_account_project_relation"]], "access_level": "固定README、TIPS、5份短面经及MVSS-Net README已读，未读全部源码",
        "confidence": dong["confidence"], "category": "候选人资料", "retrieved_at": DATE,
    },
]

project_new = []


def finding(ident, path, start, end, text, kind="固定源码静态观察"):
    m = by_project[ident]
    return {"path": path, "line_start": start, "line_end": end, "finding": text, "kind": kind, "url": source(m["repo"], m["commit"], path, start, end)}


project_specs = [
    {
        "id": "PRO14", "title": "CalvinNeo CFortranTranslator：本人SSP关联的语言工具项目",
        "stack": ["C++14/17", "Fortran77/90", "词法/语法分析", "Bison", "AST", "代码生成", "GoogleTest"],
        "recommendation": "推荐研究领域约束如何推动工程深度；适合编译器/语言工具兴趣，不应为凑技术栈照搬整个翻译器。",
        "strengths": ["SSP自述原文直接介绍此项目，并称多数面试官感兴趣；关联明确", "项目具备词法、语法、符号信息、代码生成及Fortran库适配，超出单函数演示", "可把语义兼容和可读输出作为清晰取舍讨论"],
        "weaknesses": ["历史工具链与构建说明较旧，现代环境兼容性未验证", "README明确不支持Unicode输入、只报告阻碍解析的致命错误", "regen_do_range生成循环条件固定为<=，负步长DO的语义值得专项复核；本次未运行反例", "现存测试断言多关注解析节点；不能据此宣称翻译后的全部程序语义等价"],
        "inspect_paths": ["docs/Develop.md", "src/grammar/for90.y", "src/target/gen_do.cpp", "demos/test/parser_test.cpp", "README.md"],
        "source_findings": [finding("PRO14", "docs/Develop.md", 10, 29, "开发文档解释simple_lexer与Bison解析器，包含Fortran跨行token的特殊情况。", "设计文档"), finding("PRO14", "src/target/gen_do.cpp", 29, 43, "范围DO生成C++ for，条件固定<=且步长作为增量；递减范围的语义需独立测试。"), finding("PRO14", "demos/test/parser_test.cpp", 18, 47, "GoogleTest对DO节点、COMMON块等有断言；解析结构通过不自动证明端到端语义等价。", "测试材料"), finding("PRO14", "README.md", 111, 140, "明确Unicode不支持与错误诊断范围；提供demo和GoogleTest依赖。", "公开边界")],
        "tests_and_evaluation": ["已抽读GoogleTest与demo，不曾执行。", "宜区分解析正确、生成代码可编译和与原程序结果一致三个层次；不宣称本次已完成。"],
        "runtime_dependencies": ["C++14/17编译器、Boost、Bison/Flex相关工具，具体构建见原README。", "测试部分需要GoogleTest；Windows和Ubuntu说明均较旧。"],
        "interview_questions": ["为何需要可读的逐语句翻译，而不是换语言重写？", "Fortran负步长、COMMON块、数组下界怎样保持语义？", "怎样证明输出结果正确，如何归因解析错误和代码生成错误？"],
    },
    {
        "id": "PRO15", "title": "CalvinNeo ATP：本人SSP关联的UDP可靠传输库",
        "stack": ["C++17", "UDP", "可靠传输", "协议状态", "计时器", "非阻塞IO", "poll/AIO", "故障模拟"],
        "recommendation": "推荐拆读协议状态、计时器与故障测试，学习网络基础如何变成可追问实现；不把自制协议当生产TCP替代。",
        "strengths": ["本人求职原文说明项目来源：读libutp后写的大作业，并进一步修改", "API明确交代UDP接收事件与外部计时器职责，可讨论框架边界", "测试脚本包含延迟、丢包、重复、乱序及损坏网络条件的入口"],
        "weaknesses": ["README明确框架模式非线程安全；调用方需维护计时器与事件", "test/run_test.py仍用Python2语法，含sudo tc操作；本次不执行，也不能直接当现代环境可运行", "check_log只打印文件大小，未比较文件内容；测试跑完不等于可靠交付得到证明", "README指向atp_callback.cpp中的simulate_packet_loss_sendto，但该固定文件未见该函数名，文档与当前实现需核对"],
        "inspect_paths": ["README.md", "src/atp.h", "src/atp_impl.cpp", "src/atp_callback.cpp", "test/run_test.py"],
        "source_findings": [finding("PRO15", "README.md", 32, 39, "要求外部向框架转交UDP包并触发计时事件，明确非线程安全。", "接口约束"), finding("PRO15", "src/atp_callback.cpp", 24, 43, "实际发送回调调用sendto并按发送长度处理错误；不是完整网络可靠性保证。"), finding("PRO15", "test/run_test.py", 81, 95, "check_log只打印输入/输出字节数后返回，无内容比对。", "测试局限"), finding("PRO15", "test/run_test.py", 191, 196, "存在1000ms延迟与50%丢包测试入口；仅核到脚本，未运行。", "故障测试入口")],
        "tests_and_evaluation": ["静态读取丢包、延迟、重复和乱序测试组织方式。", "未构建、未sudo tc、未改网络配置、未跑数据传输；没有吞吐或正确率实测。"],
        "runtime_dependencies": ["C++17、Make、POSIX/Linux网络环境。", "原测试脚本依赖旧Python2语法、网络工具与部分特权操作；应先读脚本再准备隔离测试环境。"],
        "interview_questions": ["数据按序、不丢失、不重复分别由哪些机制保证？", "计时器或收包事件没有按时执行会怎样？", "为什么文件大小相同仍不能证明内容一致，校验与错误注入怎样设计？"],
    },
    {
        "id": "PRO16", "title": "CalvinNeo Nuft：本人SSP关联的Raft实现与失败测试材料",
        "stack": ["C++17", "Raft", "gRPC", "Protocol Buffers", "持久化", "选主/日志/快照", "GoogleTest"],
        "recommendation": "推荐对照论文、状态转换与失败测试，适合分布式系统进阶；不能当已验证一致性的可直接上线组件。",
        "strengths": ["本人原文直接说明该项目依据Raft论文实现，求职关系明确", "代码有选主、日志复制、快照与配置变更接口，以及持久化和测试", "持久化代码保留了崩溃/延迟RPC序号问题的反思，适合学习失败分析"],
        "weaknesses": ["README明确部分测试可能失败；本次不隐去此限制", "jepsen目录README仍是FIXME模板，不能把目录存在当Jepsen验证通过", "Persister直接向目标文件序列化，所读函数未见原子替换/fsync和完整错误处理；需验证掉电与半写场景，未运行复现", "测试辅助脚本为旧Python2写法；当前工具链和所有不变量未验证"],
        "inspect_paths": ["README.md", "src/node_persister.cpp", "src/node_rpc_a.cpp", "src/test/test.cpp", "src/test/test_until_fail.py", "jepsen/README.md"],
        "source_findings": [finding("PRO16", "README.md", 11, 25, "给测试命令与循环直至失败脚本，并明确某些测试可能失败。", "作者已披露限制"), finding("PRO16", "src/node_persister.cpp", 24, 41, "持久化term、vote与日志，并记录宕机后延迟RPC/序号问题。"), finding("PRO16", "src/node_persister.cpp", 60, 74, "序列化到fstream后关闭；加载直接解析并取字段。函数局部未见原子替换和结果校验，属于未复现静态风险。"), finding("PRO16", "jepsen/README.md", 1, 14, "仍为模板与FIXME；不是已实施的一致性测试。", "验证边界")],
        "tests_and_evaluation": ["源码包含GoogleTest和持续运行到失败的脚本。", "本次未构建、未运行集群、未做故障注入或Jepsen；不宣称满足全部Raft安全性/活性。"],
        "runtime_dependencies": ["C++17、gRPC/Protobuf、gtest，原仓Nuke辅助代码已内嵌。", "Python2风格辅助脚本需适配；Jepsen目录本身不提供已完成的使用方案。"],
        "interview_questions": ["term、投票和日志什么时候必须持久化？", "半写文件、延迟RPC、旧leader恢复时怎样保持不变量？", "单测、随机故障测试和线性一致性历史验证分别证明什么？"],
    },
    {
        "id": "PRO17", "title": "linyacool WebServer：本人SSP关联的网络工程与开发复盘",
        "stack": candidate_new[1]["stack"], "recommendation": lin["project_sources"][0]["recommended_use"],
        "strengths": lin["project_sources"][0]["strengths"], "weaknesses": lin["project_sources"][0]["weaknesses"],
        "inspect_paths": ["README.md", "并发模型.md", "WebServer/HttpData.cpp", "测试及改进.md", "遇到的困难.md", "项目目的.md"],
        "source_findings": [finding("PRO17", x["path"], x["line_start"], x["line_end"], x["summary"], "源码/项目文档") for x in lin["project_sources"][0]["inspect_paths"]],
        "tests_and_evaluation": ["原文给本地1000客户端、60s、4线程，关闭日志、内存Hello World等条件。", "本次未读性能截图、未编译/压测；不将作者QPS当复现结果。", "README面试问题.md链接404，不计为已读面经。"],
        "runtime_dependencies": ["Linux、C++11、CMake/Make；原README写Ubuntu14.04/g++4.8。", "内嵌WebBench保留其独立许可证；现代编译器/内核兼容性待实测。"],
        "interview_questions": ["ET模式怎样把accept/read读到合适边界？", "跨线程事件怎样唤醒，连接销毁与超时如何避免竞态？", "关闭日志与内存响应对QPS意味着什么，怎样测尾延迟和异常连接？"],
    },
]

for record in project_specs:
    m = by_project[record["id"]]
    record.update({k: m[k] for k in ["repo", "commit", "commit_date", "license", "license_scope", "archive_file", "archive_sha256", "source_archive"]})
    record.update({"url": m["source_url"], "candidate_links": ["CV11" if record["id"] == "PRO17" else "CV10"], "cost": "源码阅读与本地构建不需要模型API；本轮仅静态阅读和归档，没有运行费用。", "run_status": "固定源码和部分文档/测试静态阅读；未构建、运行、压测或修改系统配置。", "interview_linkage": "本人文章直接建立项目关系；固定版本晚于求职经历，不等于当时提交版本，也不证明该项目单独导致SSP。", "category": "项目参考", "retrieved_at": DATE})
    project_new.append(record)

java_rounds = [r for r in java["interview_paths"] if r.get("company")]
interview_new = [
    {"id": "INT56", "title": "JavaWxy本人面试记录：携程、菜鸟、美团项目追问对照", "url": source(JAVA_REPO, JAVA_SHA, "面试记录.md"), "company": "携程／菜鸟／美团等（同一候选人）", "role": "Java后端；历史实习与秋招混合", "date": java["batch"]["literal"] + "；" + java["batch"]["certainty"], "outcome": "作者整体自述腾讯SSP；这些轮次不等于腾讯SSP面经，也未逐轮提供档位证明", "sample_group": "历史同作者多轮汇总（不作独立成功者）", "candidate_group": "CV02_JavaWxy", "role_boundary": "原文件同时含同学记录；本卡仅选无此标记的携程0315、菜鸟0421、美团0831，排除0317美团同学一轮", "ssp_status": "候选人整体SSP自述明确；腾讯具体面经未公开", "topics": ["RPC", "Netty", "注册发现", "消息队列", "本地消息表", "幂等", "退款竞态", "事务", "压测", "本人贡献"], "project_questions": [q for r in java_rounds for q in r.get("project_questions", [])], "rounds": java_rounds, "summary": "本轮Java材料最值得读的增补：能把同一人的业务项目、RPC项目、具体问题与踩坑笔记对应起来。", "recommended_use": "先读菜鸟L632–692，再读携程L7–37和美团L1138–1170；结合PRO08，不将括号里的答案当标准答案。", "source_project_links": java["projects"], "limitations": java["limits"] + [java["ssp_specific_interview_limit"]], "access_level": "固定面试记录1186行原文已读；选择范围给出行号", "fulltext_verified": True, "confidence": "B：第一人称面试回忆；结果未经独立核验", "category": "面经复盘", "retrieved_at": DATE},
    {"id": "INT57", "title": "CalvinNeo：2018求职复盘中的阿里云后台面试主题", "url": CALVIN_URL, "company": "阿里云（腾讯SSP为同作者另外的实习转正结果）", "role": "C++后台；历史校招", "date": "2018年求职、2019届；页面2019-03-15编辑，非已确认首发时间", "outcome": "作者自述阿里云A和腾讯SSP（转正）；不混淆公司和路径", "sample_group": "历史求职复盘与面试主题（非逐轮记录）", "candidate_group": "CV10_CalvinNeo", "role_boundary": "非2026实习面经；原文阿里云补充段为主题总结，无完整题目逐字稿", "ssp_status": "腾讯实习转正SSP自述明确；阿里云不是SSP声明", "topics": ["C++", "Linux", "内存管理", "文件系统", "系统设计", "Redis", "MySQL", "RocksDB", "算法", "项目深挖"], "project_questions": ["为何选择并实现编译器、可靠传输或Raft，个人做了什么？（据项目段归纳）", "阿里云项目追得深，需要解释Linux实现与常见系统设计（原文主题，非整理者虚构逐字问句）"], "summary": "原文将项目动机、工程深度、实习表现与求职经验连起来，适合研究项目怎样支撑讨论。", "recommended_use": "与CV10、PRO14–16一起读；区分原文面试主题和项目卡中整理者提出的源码深挖题。", "source_project_links": candidate_new[0]["project_urls"], "limitations": candidate_new[0]["weaknesses"], "access_level": "原文正文及末尾阿里云补充段实际已读；页面可能复查空壳", "fulltext_verified": True, "confidence": "B：本人公开复盘；不是完整逐轮SSP面经", "category": "面经复盘", "retrieved_at": DATE},
    {"id": "INT58", "title": "dong03 CV_Interview：历史CV/多模态题目与协作面经范围", "url": source("dong03/CV_Interview", DONG_SHA, "TIPS.md", 24, 39), "company": "腾讯／蚂蚁／字节等（含实验室协作来源）", "role": "CV/多模态算法邻近参考", "date": "腾讯与蚂蚁正文为2022年；其他若未给年份则保留未知", "outcome": "仓主整体自述若干SSP；不能将各公司轮次或同学面经归为其SSP结果", "sample_group": "历史算法协作面经（作者关系未逐条确认）", "candidate_group": "CV13_dong03_协作", "role_boundary": "非近期Agent工程实习，不参与近期工程面经分母", "ssp_status": "整体自述明确，具体公司/轮次不明确", "topics": ["PyTorch", "损失函数", "FLOPs", "BatchNorm", "梯度", "论文与实习项目", "业务场景", "算法"], "project_questions": [x["questions"] for x in dong["interview_materials"]["read_examples"]], "rounds": dong["interview_materials"]["read_examples"], "summary": dong["interview_materials"]["author_scope"], "recommended_use": dong["interview_materials"]["recommendation"], "limitations": dong["limitations"] + ["同账号MVSS-Net未在这些面经中被点名，不能补写项目对应或获SSP因果"], "access_level": "固定README、TIPS、所选5篇短面经已读；未读全库全部知识点", "fulltext_verified": True, "confidence": "B-：公开文本可核；多人来源，不能全算仓主亲历", "category": "面经复盘", "retrieved_at": DATE},
]

observation_new = [{"id": "OBS03", "title": "大模型SSP自述但项目仍为hello world：避免按录用标签盲荐", "url": weak["ssp_source"]["url"], "author": weak["public_author"], "date": weak["year_and_role"], "role": "LLM算法弱线索；非已确认Agent岗位", "outcome": weak["ssp_status"], "evidence_excerpt": weak["ssp_excerpt"], "source_summary": weak["same_account_project_relation"]["relation"], "source_findings": weak["same_account_project_relation"]["actual_code"], "recommendation": weak["same_account_project_relation"]["project_recommendation"], "limitations": weak["limitations"], "access_level": "固定README和两个源码文件已读；未运行/下载模型，不归档无明确许可仓库", "confidence": weak["confidence"], "category": "候选人对照", "retrieved_at": DATE}]

candidate_data = load("candidate_cases.json")
if "pre_github_ssp_counts" not in candidate_data:
    candidate_data["pre_github_ssp_counts"] = dict(candidate_data["counts"])
candidate_data["cases"] = merge(candidate_data["cases"], candidate_new)
candidate_data["counts"]["curated_cases"] = len(candidate_data["cases"])
candidate_data["counts"]["successful_self_report_without_resume"] = candidate_data["pre_github_ssp_counts"]["successful_self_report_without_resume"] + len(candidate_new)
candidate_data["counts"]["github_ssp_new_public_profile_cases"] = 4
candidate_data["counts"]["github_ssp_existing_candidate_strengthened"] = 1
candidate_data["scope"] += "；GitHub SSP专项增加历史工程与算法邻近案例，完整CV数量仍为0。" if "GitHub SSP专项" not in candidate_data["scope"] else ""
for r in candidate_data["cases"]:
    if r["id"] == "CV02":
        r["github_ssp_update"] = {"source": java["ssp_claim"], "interview_source": source(JAVA_REPO, JAVA_SHA, "面试记录.md"), "interview_id": "INT56", "attribution_boundary": java["interview_paths"][0]["attribution_limit"], "ssp_interview_boundary": java["ssp_specific_interview_limit"]}
interviews = merge(load("interview_records.json"), interview_new)
project_data = load("project_recommendations.json")
project_data["projects"] = merge(project_data["projects"], project_new)
project_data["github_ssp_scope"] = "新增4个本人明确关联的历史工程项目；不声称项目导致SSP。"
all_records = merge(load("all_evidence_records.json"), candidate_data["cases"] + interview_new + project_new + observation_new)
for r in all_records:
    if r["id"].startswith("CV"):
        r["category"] = "候选人资料"
manifest = json.loads(read(ARCHIVES / "SOURCE_MANIFEST.json"))
manifest_by_repo = {m["repo"]: m for m in manifest + new_manifest}
manifest = list(manifest_by_repo.values())
dump("candidate_cases.json", candidate_data)
dump("interview_records.json", interviews)
dump("project_recommendations.json", project_data)
dump("all_evidence_records.json", all_records)
write(ARCHIVES / "SOURCE_MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
new_records = candidate_new + interview_new + project_new + observation_new
dump("github_ssp_supplement_records.json", {"date": DATE, "cases_new": candidate_new, "interviews_new": interview_new, "projects_new": project_new, "observations_new": observation_new})

# 复用已有字段译名；仅解析常量，不执行旧整合脚本。
labels = {}
for node in ast.parse(read(INDEX / "整合增补资料.py")).body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "LABELS" for t in node.targets):
        labels = ast.literal_eval(node.value)
labels.update({"github_ssp_update": "GitHub SSP专项更新", "ssp_claim": "SSP自述", "ssp_interview_boundary": "SSP面经边界", "interview_source": "面经入口", "interview_id": "面经编号", "attribution_boundary": "作者范围", "source": "来源", "interview_sources": "面经材料与作者边界", "query": "检索词", "reason": "排除理由", "classification": "分类", "disposition": "处理口径", "read_range": "已读范围", "questions": "题目归纳", "outcome_boundary": "结果边界", "permalink": "固定链接", "material_type": "材料类型", "relationship": "作者关系", "relationship_evidence": "关系来源", "relationship_lines": "关系原文行号", "limits": "限制", "line_start": "起始行", "line_end": "结束行"})


def value_html(v):
    if isinstance(v, list):
        return "<ul>" + "".join("<li>" + value_html(x) + "</li>" for x in v) + "</ul>"
    if isinstance(v, dict):
        return "<br>".join(escape(labels.get(k, k)) + "：" + value_html(x) for k, x in v.items())
    if isinstance(v, bool):
        return "是" if v else "否"
    if v is None:
        return "未提供"
    text = str(v)
    if re.fullmatch(r"https?://[^\s]+", text):
        return '<a href="' + escape(text, quote=True) + '">' + escape(text) + '</a>'
    if text.endswith('.zip') and Path(text).name == text and (ARCHIVES / text).is_file():
        return '<a href="../05_项目源码归档/' + escape(text, quote=True) + '">' + escape(text) + '</a>'
    return escape(text).replace("\n", "<br>")


def card(r, opened=False):
    body = "".join('<div class="field"><b>' + escape(labels.get(k, k)) + '</b><div>' + value_html(v) + '</div></div>' for k, v in r.items() if k not in {"id", "title", "category", "retrieved_at", "retrieved_date", "read_method", "source_line_range"} and v not in (None, [], ""))
    return '<details class="card" id="' + r["id"] + '" data-category="' + escape(r.get("category", "")) + '"' + (' open' if opened else '') + '><summary><span class="tag">' + r["id"] + '</span> ' + escape(r["title"]) + '</summary>' + body + '</details>'


def table(headers, rows):
    return '<div class="tablewrap"><table><thead><tr>' + ''.join('<th>' + escape(h) + '</th>' for h in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + str(c) + '</td>' for c in row) + '</tr>' for row in rows) + '</tbody></table></div>'


def plain_card(r):
    return r["id"] + " | " + r["title"] + "\n\n" + "\n\n".join(labels.get(k, k) + "：\n" + (json.dumps(v, ensure_ascii=False, indent=2) if isinstance(v, (list, dict)) else str(v)) for k, v in r.items() if k not in {"id", "title"}) + "\n"


for record in new_records:
    folder = "03_简历与候选人案例" if record["id"].startswith(("CV", "OBS")) else "04_面经与专业观点" if record["id"].startswith("INT") else "06_项目分析与推荐"
    write(ROOT / folder / (record["id"] + ".txt"), plain_card(record))
cv02 = next(r for r in candidate_data["cases"] if r["id"] == "CV02")
write(ROOT / "03_简历与候选人案例/CV02.txt", plain_card(cv02))

stats = {"date": DATE, "scope": "GitHub SSP作者、项目与面经专项；个人项目设计暂缓", "core_profiles_reviewed": 5, "new_candidate_profiles": 4, "existing_candidate_strengthened": 1, "new_project_analysis": 4, "new_source_archives": 4, "new_interview_material_records": 3, "new_weak_counterexample": 1, "engineering_priority_profiles": ["CV02", "CV10", "CV11"], "partial_engineering_profile": ["CV12"], "historical_algorithm_adjacent_profile": ["CV13"], "weak_algorithm_self_report": ["OBS03"], "recent_agent_ssp_with_mature_project_and_personal_interview_chain": 0, "totals": {"candidate_cases": len(candidate_data["cases"]), "interview_material_records": len(interviews), "project_analysis": len(project_data["projects"]), "source_archives": len(manifest), "logical_evidence_records": len(all_records)}, "category_counts": dict(Counter(r["category"] for r in all_records)), "caution": "同作者同原文跨类别交叉引用不等于独立样本；SSP均为作者自述，完整成功者CV和企业独立核验数量仍为0。"}
dump("GitHub_SSP专项统计.json", stats)

# 同步主题索引；旧报告的主题表保留上轮快照口径。
def topic_values(value):
    if isinstance(value, (list, tuple)):
        return " ".join(topic_values(item) for item in value)
    if isinstance(value, dict):
        return " ".join(topic_values(item) for item in value.values())
    return str(value)


topic_data = load("interview_topic_index.json")
for row in topic_data["themes"]:
    row["evidence_ids"] = [r["id"] for r in interviews if re.search(row["rule"], topic_values([r.get(k, []) for k in ("topics", "project_questions")]), re.I)]
    row["record_count"] = len(row["evidence_ids"])
topic_data["updated_at"] = DATE
topic_data["scope_records"] = len(interviews)
topic_data["scope_note"] = "涵盖GitHub SSP专项的历史和协作材料；旧HTML报告主题表为上轮48份资料的快照。"
dump("interview_topic_index.json", topic_data)
topic_csv = io.StringIO(newline="")
topic_writer = csv.writer(topic_csv)
topic_writer.writerow(["主题", "资料条数_非独立场次", "资料ID", "复核规则"])
for row in topic_data["themes"]:
    topic_writer.writerow([row["theme"], row["record_count"], ";".join(row["evidence_ids"]), row["rule"]])
write(INDEX / "面经主题索引.csv", topic_csv.getvalue())

rows = [
    ["CV02 JavaWxy（既有补强）", "腾讯SSP自述，批次见原文", "学成在线＋RPC＋点评，作者介绍和职责可读", "同仓1186行；定位3轮，排除同学记录；无腾讯专门轮次", '<a href="index.html#CV02">卡片</a> · <a href="index.html#INT56">面经</a>', "优先：Java业务＋基础组件"],
    ["CV10 CalvinNeo（新增）", "2018腾讯实习转正SSP", "本人文章直接链接翻译器、可靠传输、Raft；已附源码", "本人复盘及阿里云主题；非腾讯逐轮SSP面经", '<a href="#CV10">卡片</a> · <a href="#PRO14">源码</a>', "优先：三个项目各有机制重点"],
    ["CV11 linyacool（新增）", "历史offer大多SSP，未逐家定档", "本人文章直接链接WebServer；设计/测试/困难完整", "本人求职复盘；README面试问题链接404", '<a href="#CV11">卡片</a> · <a href="#PRO17">源码</a>', "优先：系统基础与诚实复盘"],
    ["CV12 muluoleiguo（新增）", "2021秋招有SP/SSP，未逐家定档", "同仓项目说明和片段；完整Muluo源码未定位", "仓库面经汇总，未证每条本人亲历", '<a href="#CV12">卡片</a>', "辅助：模块与追问导航"],
    ["CV13 dong03（新增）", "历史CV/多模态若干SSP，未逐家定档", "MVSS-Net仅同账号关系，未证用于获SSP", "部分面经为2022年，固定版本2023年；实验室协作需区分", '<a href="#CV13">卡片</a> · <a href="#INT58">面经</a>', "邻近：算法评测方法"],
]
css = """*{box-sizing:border-box}body{margin:0;color:#243547;background:#f4f7fa;font:15px/1.8 'Microsoft YaHei',sans-serif}header{background:#132d46;color:white;padding:38px max(5vw,24px)}header p{max-width:1100px}h1{font-size:30px;line-height:1.5}a{color:#176c70;overflow-wrap:anywhere}header a{color:#a6f0df}main{max-width:1240px;margin:auto;padding:24px}section{background:white;padding:25px;border:1px solid #dce4ec;border-radius:10px;margin-bottom:22px}h2{color:#163650;font-size:23px;border-bottom:3px solid #2b918a;padding-bottom:10px}h3{color:#176c70}aside{background:#eaf6f3;border-left:4px solid #2b918a;padding:15px 20px}table{border-collapse:collapse;width:100%;font-size:13px}th,td{border:1px solid #dce4ec;padding:10px;vertical-align:top}th{background:#eaf0f5}.tablewrap{overflow:auto}details.card{border:1px solid #dce4ec;border-radius:8px;margin:15px 0}summary{font-weight:bold;padding:14px;cursor:pointer}.tag{color:#176c70;min-width:50px;display:inline-block}.field{display:grid;grid-template-columns:155px 1fr;gap:12px;padding:9px 16px;border-top:1px solid #e8edf2;font-size:13px;overflow-wrap:anywhere}.field b{color:#516779}ul{padding-left:20px}footer{padding:20px;text-align:center;color:#62798d;font-size:13px}@media(max-width:750px){main{padding:10px}section{padding:16px}.field{grid-template-columns:1fr}}@media print{@page{size:A4;margin:16mm}body{background:white;font-size:10pt}header{background:white;color:#163650;padding:0 0 8px}header a{color:#176c70}main{padding:0}section{border:0;padding:8px 0}h1{font-size:24pt}h2{font-size:17pt;break-after:avoid}h3,summary{break-after:avoid}.field{display:block;font-size:9pt;padding:6px 8px}.field b{display:block}table{font-size:8pt}.tablewrap{overflow:visible}tr{break-inside:avoid}a{word-break:break-all}footer{font-size:8pt}}"""
report = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GitHub SSP作者项目与面经专项</title><style>' + css + '</style></head><body><header><p>2026-10-23 · GitHub定向信息搜集</p><h1>GitHub SSP作者：项目与面经专项</h1><p>新增4份候选人分析，补强既有JavaWxy；新增4份项目分析及源码包、3份面经资料索引。另保留1份代码未成形的对照案例。</p><p><a href="index.html">完整可搜索目录</a> · <a href="GitHub_SSP项目与面经专项.pdf">PDF</a> · <a href="../08_证据索引与统计/GitHub_SSP专项统计.json">统计与口径</a></p></header><main>'
report += '<section><h2>先读这五位，区分关联强弱</h2><aside>“拿到SSP”均为作者公开自述，没有企业侧独立核验。本人项目、同账号项目、教程项目、题库与他人面经分别标注。历史校招或转正结果不直接代表2026实习要求。</aside>' + table(["案例", "SSP口径", "项目关系", "面经范围", "入口", "推荐理由"], rows) + '</section>'
report += '<section><h2>按你关心的项目和面经来读</h2><ol><li><b>Java业务与基础组件：</b>先看<a href="index.html#CV02">CV02</a>，再看<a href="#INT56">同仓项目追问</a>。菜鸟轮次把RPC宕机、压测、消息表和退款竞态串起来；学成在线已有<a href="index.html#PRO08">PRO08源码</a>。RPC和点评仍仅链接。</li><li><b>项目各有侧重：</b>看<a href="#CV10">CalvinNeo本人介绍</a>与PRO14–16，分别对照语言语义、可靠传输和共识；这是已有项目对照，本轮不设计你的个人项目。</li><li><b>基础深度与复盘：</b>看<a href="#PRO17">WebServer</a>的并发模型、测试条件和开发困难。旧QPS不能直接搬进简历。</li><li><b>Agent缺口：</b>本轮没有找到“近期Agent SSP＋成熟本人项目＋本人面经”同时闭合的强案例。<a href="#OBS03">OBS03</a>虽自述若干SSP，代码却仅hello world及下载封装；不推荐为非toy Agent。</li></ol></section>'
report += '<section><h2>新增本人／协作面经的具体内容</h2>' + ''.join(card(r, True) for r in interview_new) + '</section>'
report += '<section><h2>新增候选人分析</h2>' + ''.join(card(r, True) for r in candidate_new) + '</section>'
report += '<section><h2>新增项目：值得借鉴什么、哪些地方需警惕</h2><p>四包均固定commit并保留根与内嵌组件许可。当前版本晚于求职时期，不当作当年简历代码快照。没有构建、运行、压测、模型调用或系统配置修改。</p>' + ''.join(card(r, True) for r in project_new) + '</section>'
report += '<section><h2>反例：SSP标签不替代代码核验</h2>' + ''.join(card(r, True) for r in observation_new) + '</section>'
excluded = backend['excluded_leads'] + agent['excluded_or_unresolved']
report += '<section><h2>哪些命中没有算作成功者</h2><ul><li>zslomo：本人总结是5个SP；SSP文字涉及周边或薪酬说明，不能升级为本人SSP。</li><li>Brave-peng：README明确由其他SP/SSP大佬提供原稿，不等于仓主本人获SSP。</li><li>AgentGuide等“SSP级题库”或课程宣传：没有对应作者第一人称录用与本人项目链，不能据标题收录。</li><li>CyC2018的SSP历史线索：本轮原站“作者介绍”复核仅得空壳，未新增为已读本人成功案例。</li><li>Azurer0121笔记线索：原路径raw 404，未按搜索摘要收为本人成功经历。</li></ul><p>更细的排除理由、固定链接与已读范围见<a href="../08_证据索引与统计/github_ssp_backend_discovery.json">后端检索记录</a>、<a href="../08_证据索引与统计/github_ssp_systems_discovery.json">系统方向记录</a>和<a href="../08_证据索引与统计/github_ssp_agent_discovery.json">Agent/算法记录</a>。</p></section>'
report += '<section><h2>检索方法与仍有的缺口</h2><p>GitHub公开仓库检索用于发现线索，读取固定commit下README、项目介绍、面经与代码来核对。搜索网页触发429后停止重复请求，转直接仓库、raw与作者正文；Yahoo/搜狗只作发现，不以搜索摘要代替原文。Bing对中文限定返回无关内容、Google跳转、Brave验证码均未作为证据。AI辅助做检索、静态阅读与原创归纳，短摘录保留原出处。</p><p>完整成功者CV仍为0，所有SSP与性能结果维持作者自述口径。没有建立项目导致录用的因果证明；B站完整视频也未补齐。个人项目设计暂缓。</p><p>归档清单：<a href="../05_项目源码归档/GITHUB_SSP_SOURCE_MANIFEST.json">本轮4包</a>；<a href="../05_项目源码归档/SOURCE_MANIFEST.json">全部源码包</a>。</p></section></main><footer>公开来源与原创归纳 · 第三方项目保留原许可 · 同作者与同原文交叉引用不作独立样本</footer></body></html>'
write(REPORT / "GitHub_SSP项目与面经专项.html", report)

md = "# GitHub SSP作者项目与面经专项\n\n本轮新增4份候选人分析，补强已有CV02；优先阅读JavaWxy、CalvinNeo和linyacool。SSP均为作者自述，个人项目设计暂缓。\n\n| 案例 | 结果与阅读重点 |\n|---|---|\n"
for r in rows:
    md += "| " + r[0] + " | " + r[1] + "；" + r[2] + "；" + r[3] + " |\n"
md += "\n[完整专项报告](GitHub_SSP项目与面经专项.html) · [PDF](GitHub_SSP项目与面经专项.pdf) · [可搜索目录](index.html)\n\n新增项目：\n\n"
for r in project_new:
    md += f"- {r['id']} [{r['repo']}]({r['url']})：{r['recommendation']}\n"
md += "\n完整成功者CV与近期Agent SSP强关联仍未补齐；项目未运行。\n"
write(REPORT / "GitHub_SSP阅读导航.md", md)

# 主入口保留上一轮分析及历史草案，新增专项入口并更新全包目录。
main_path = REPORT / "index.html"
markup = read(main_path)
markup = re.sub(r'<div class="stats">[\s\S]*?</div>', '<div class="stats"><span><strong>19</strong>JD线索 / 14全文工程实习</span><span><strong>' + str(len(candidate_data['cases'])) + '</strong>候选人材料 / 非完整CV</span><span><strong>' + str(len(interviews)) + '</strong>面经与复盘</span><span><strong>7</strong>B站/知乎资料</span><span><strong>' + str(len(manifest)) + '</strong>固定版本源码</span></div>', markup, count=1)
banner = '<aside id="github-ssp-update"><strong>新增GitHub SSP专项：</strong>新增4份候选人分析、补强已有JavaWxy，附4个本人关联项目源码包。<a href="GitHub_SSP项目与面经专项.html">打开专项报告</a> · <a href="GitHub_SSP项目与面经专项.pdf">专项PDF</a>。当前共' + str(len(interviews)) + '份面经资料、' + str(len(project_data['projects'])) + '份项目分析、' + str(len(manifest)) + '个源码包。历史/协作资料分别标注；个人项目设计暂缓。</aside>'
markup = re.sub(r'<aside id="github-ssp-update">[\s\S]*?</aside>', '', markup)
markup = markup.replace('<article>', '<article>' + banner, 1)
markup = markup.replace('本轮信息搜集增补：</strong>', '上轮信息搜集增补：</strong>')
new_intro = '<section id="s0"><h2>01 本轮阅读入口</h2><p>先读<a href="GitHub_SSP项目与面经专项.html">GitHub SSP作者项目与面经专项</a>：从本人结果自述追到项目、面经和具体源码；重点看CV02、CV10、CV11，另外两个部分关联/算法邻近案例分列。</p><p>上一轮新增29条面经与6份项目分析，见<a href="信息搜集增补报告.html">信息搜集增补报告</a>。全包资料在页末可搜索；历史批次、同作者与协作来源均有说明。</p><p>当前共' + str(len(candidate_data['cases'])) + '份候选人分析、' + str(len(interviews)) + '份面经资料、' + str(len(project_data['projects'])) + '份项目分析、' + str(len(manifest)) + '个源码包。完整成功者CV仍为0，SSP仅作者自述，近期Agent强关联仍有缺口。个人项目设计暂缓。</p></section>'
markup = re.sub(r'<section id="s0">[\s\S]*?</section>', lambda _: new_intro, markup, count=1)
markup = markup.replace('候选人目录共9个案例：', '初轮候选人目录9个案例的构成为：')
markup = markup.replace('原有19条记录继续保留，本轮新增29条，现共48条面经资料。', '原有19条及上轮新增29条继续保留；本次SSP专项再补3份资料，现共' + str(len(interviews)) + '份面经资料（含历史/协作参考）。')
markup = markup.replace('现有13份项目分析，其中12个已附固定commit源码归档与原许可证', '现有' + str(len(project_data['projects'])) + '份项目分析，其中' + str(len(manifest)) + '个已附固定commit源码归档与原许可证')
markup = markup.replace('9份匿名简历片段/履历分析，原文与推荐理由', str(len(candidate_data['cases'])) + '份简历片段/履历分析，另有对照样本；非完整CV')
markup = markup.replace('48份面经资料与7份B站/知乎资料卡', str(len(interviews)) + '份面经资料与7份B站/知乎资料卡')
markup = markup.replace('12个固定commit的公开源码ZIP', str(len(manifest)) + '个固定commit的公开源码ZIP')
markup = markup.replace('13份项目优缺点、模块、源码路径和运行边界', str(len(project_data['projects'])) + '份项目优缺点、模块、源码路径和运行边界')
markup = markup.replace('本地完整版现含12个源码归档', '本地完整版现含' + str(len(manifest)) + '个源码归档')
categories = list(dict.fromkeys(r['category'] for r in all_records))
catalog = '<section id="evidence"><h2>15 可搜索资料目录</h2><p>按作者、公司、技术点、编号、岗位批次或证据状态搜索。GitHub SSP专项案例见CV02、CV10–13，反例OBS03；同作者和同源交叉引用不作独立成功者。</p><div class="tools"><input id="q" type="search" placeholder="例如：CalvinNeo、SSP、INT56、PRO17"><select id="category"><option>全部类别</option>' + ''.join('<option>' + escape(c) + '</option>' for c in categories) + '</select><button id="expand">展开匹配</button><button id="collapse">全部收起</button></div><p class="muted" id="count"></p>' + ''.join(card(r) for r in all_records) + '</section>'
markup = re.sub(r'<section id="evidence">[\s\S]*?</section>', lambda _: catalog, markup, count=1)
write(main_path, markup)

write(ROOT / "00_START_HERE.txt", "大厂后端与Agent实习信息搜集包 | GitHub SSP专项更新 | 2026-10-23\n\n先看01_调研报告/GitHub_SSP项目与面经专项.html或同名PDF。完整可搜索入口：01_调研报告/index.html。\n\n本轮新增4份候选人分析，补强已有JavaWxy；新增4份项目分析及固定源码包、3份面经资料索引、1份项目未成形的对照。\n当前全包：" + str(len(candidate_data['cases'])) + "份候选人分析、" + str(len(interviews)) + "份面经资料、" + str(len(project_data['projects'])) + "份项目分析、" + str(len(manifest)) + "个源码包。\n\n优先读CV02 JavaWxy（Java/RPC/业务）、CV10 CalvinNeo（翻译器/可靠传输/Raft）、CV11 linyacool（WebServer）。CV12项目/面经归属不完整，CV13为历史CV算法邻近参考，OBS03不推荐为成熟Agent。\nSSP与性能均为作者自述；完整成功者CV、企业独立核验、近期Agent SSP成熟项目和面经的强关联仍为0。B站完整内容仍未取得。\n所有源码包固定commit并保留许可证；本轮未构建、运行、压测或调用模型。当前版本不等于求职时期快照。\n个人项目设计暂缓，原草案保留于07_个人项目设计_暂缓。\n\n上一轮29面经/6项目增补报告继续保留；最新全部数量以GitHub_SSP专项统计.json及主搜索目录为准。\n")
write(ROOT / "00_GitHub_SSP更新说明.md", "# GitHub SSP专项更新\n\n新增4份候选人分析，补强CV02；新增4份项目分析及源码包、3份面经资料、1份对照案例。\n\n- [专项报告](01_调研报告/GitHub_SSP项目与面经专项.html)\n- [专项PDF](01_调研报告/GitHub_SSP项目与面经专项.pdf)\n- [阅读导航](01_调研报告/GitHub_SSP阅读导航.md)\n- [完整搜索目录](01_调研报告/index.html)\n- [统计与分组](08_证据索引与统计/GitHub_SSP专项统计.json)\n- [本轮源码归档清单](05_项目源码归档/GITHUB_SSP_SOURCE_MANIFEST.json)\n\n近期Agent SSP成熟项目强关联仍未找到；完整CV仍为0；所有录用均作者自述；项目未运行。个人项目设计暂缓。\n")
method_path = INDEX / "source_methodology.txt"
method = read(method_path).split("\nGitHub SSP后续更新：")[0]
method = method.removeprefix("以下为上轮信息搜集快照；最新数量见文末GitHub SSP更新。\n")
write(method_path, "以下为上轮信息搜集快照；最新数量见文末GitHub SSP更新。\n" + method.rstrip() + "\n\nGitHub SSP后续更新：\n" + json.dumps(stats, ensure_ascii=False, indent=2) + "\n")

# 检查本轮新增源码的完整性、许可证、推荐路径与引用行号。
checks = []
for project in project_new:
    m = by_project[project['id']]
    p = ARCHIVES / m['archive_file']
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    assert actual == m['archive_sha256']
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        names = z.namelist()
        for path in project['inspect_paths']:
            assert any(n.endswith('/' + path) for n in names), (project['id'], path)
        for f in project['source_findings']:
            name = next(n for n in names if n.endswith('/' + f['path']))
            lines = z.read(name).decode('utf-8-sig', errors='replace').splitlines()
            assert 1 <= f['line_start'] <= f['line_end'] <= len(lines), (project['id'], f)
        for name in m['license_files']:
            assert name in names
    checks.append({'id':project['id'], 'sha256':actual, 'crc':'通过', 'paths_and_line_ranges':'通过', 'license_members_retained':m['license_files']})
assert len(all_records) == len({r['id'] for r in all_records})
dump("GitHub_SSP整合校验结果.json", {"unique_ids": len(all_records), "archives": checks, "scope":"本地来源结构、源码归档和行号校验；不是项目运行或录用真实性验证"})
print(json.dumps(stats, ensure_ascii=False, indent=2))
