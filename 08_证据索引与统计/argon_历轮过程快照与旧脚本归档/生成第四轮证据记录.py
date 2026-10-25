"""用本轮实际已读正文形成原创资料卡，不把搜索命中算成录用成功。"""
from pathlib import Path
from urllib.parse import quote
import json

BASE = Path(__file__).resolve().parent


def load(name):
    return json.loads((BASE / name).read_text(encoding="utf-8-sig"))


def source(repo, sha, path, line=None):
    return f"https://github.com/{repo}/blob/{sha}/{quote(path)}" + (f"#L{line}" if line else "")


guest = load("github_ssp_round4_guest_ssp_read.json")
original = load("github_ssp_round4_guest_original_access.json")
guest_url = source(guest["repo"], guest["sha"], guest["path"])
dream_sha = "c4cf3bbbb6bc95daaf6deff734642ea51c7cec9c"
go_sha = "5a48dfc6003468aa6c152da05e79beafdee1bcd7"
school_sha = "fc50ea8b19f99b4b15b2012048ea4651d896dd94"
dream = lambda path, line=None: source("DreamCats/java-notes", dream_sha, path, line)
school = lambda path, line=None: source("DreamCats/school-bus", school_sha, path, line)
gofile = lambda path, line=None: source("CocaineCong/Golang-Interview", go_sha, path, line)

candidates = [
    {"id": "CV20", "title": "鬼卞：2019字节SSP来稿，GSoC与数据库比赛项目经历", "url": guest_url + "#L30", "author": "鬼卞（文末署名）；不是收录仓主puge-up", "date": "文章署2019-10-24；收录仓当前固定提交2025-02-18，不能混作面试年份", "role": "历史Linux C/C++后端方向；腾讯实习转正与秋招结果分别记录", "outcome": "来稿第一人称自述字节SSP、腾讯实习转正SP、网易游戏SP；不能互换档位", "document_type": "GitHub收录的署名读者来稿，含原始公众号链接；非作者本人仓库或完整简历", "evidence_excerpt": "字节跳动直通终面 ssp", "stack": ["Linux", "C/C++", "网络编程", "数据库", "Redis/libco源码阅读"], "projects": ["自述大二参与并完成GSoC，未写具体组织、任务和本人仓库", "自述阿里云天池数据库性能赛作为求职压轴项目，未给赛题年份、代码与可核排名"], "source_findings": [{"url": guest_url + "#L34", "finding": "结果列表分别给出三家档位"}, {"url": guest_url + "#L52", "finding": "GSoC经历与开源参与的本人回顾；不把文中申请人数统计当当前事实"}, {"url": guest_url + "#L67", "finding": "数据库比赛与求职项目关系为本人明示；源码未定位"}, {"url": guest_url + "#L156", "finding": "文末有2019日期、鬼卞署名和原始文章链接"}], "recommended_use": "比较开源协作、专项比赛与实习转正如何形成履历；可提炼项目来源和个人贡献的表达，暂不足以做源码复刻案例。", "strengths": ["年份、署名、公司档位与求职项目来源都比只有标题的线索清楚"], "limitations": ["原公众号本轮遇环境验证，未核原始正文；GitHub版本属于第三方收录，证据强度低于本人仓直接发布", "没有核到本人GitHub、具体GSoC任务或数据库赛源码，不打包猜测项目", "没有逐轮题目，不能算新增具体逐轮面经；录用未获企业核验"], "confidence": "C+：署名第一人称来稿可读；原始发布页和本人代码尚未核实"},
    {"id": "CV21", "title": "DreamCats：本人项目与三家面经可直接对应，SSP未证", "url": dream("Java/mianjing/my字节.md", 12), "author": "DreamCats", "date": "面经只标7—8月；年份未确认。资料仓固定提交2024-12-02，不当面试年份", "role": "历史Java后端求职资料；不是新确认SSP成功者", "outcome": "本人京东offer、字节意向书；腾讯自评不理想，未核最终结果。未写SSP档位", "document_type": "本人面经目录、项目文档与源码仓；非完整CV原件", "stack": ["Java", "Spring Boot", "MySQL", "Redis", "Dubbo", "RocketMQ", "JWT/SSO", "Sentinel"], "projects": ["微服务班车在线预约系统SchoolBus：用户、班车、订单、支付四服务；Guns框架二次开发，前端另有作者"], "source_findings": [{"url": dream("Java/mianjing/README.md", 24), "finding": "目录单列“自己”，区别前面的他人面经汇总"}, {"url": dream("README.md", 27), "finding": "根目录把班车项目文档和仓库明确署为DreamCats"}, {"url": dream("Java/mianjing/my字节.md", 12), "finding": "字节本人问题明确追问微服务班车、拆分、自动取消和MQ；文件首尾写意向书"}, {"url": dream("Java/mianjing/my京东.md", 2), "finding": "京东文件明确offer，二面又问班车状态业务"}], "recommended_use": "优先看同一项目在字节、京东的不同深挖路径，再对照PRO19的源码局限。项目归属清楚，但不能由此推导SSP。", "strengths": ["求职项目、本人多轮问题与可读代码形成直接关系，适合研究技术栈为什么会被追问"], "limitations": ["年份、完整履历和档位未核；意向书与正式offer分开", "源码有两个版本及第三方框架，不能把全部代码算作者独立原创", "未构建或运行项目，不验证性能和高可用宣传"], "confidence": "B：本人项目和面经关联清楚；SSP结果未证"},
]
for r in candidates:
    r.update({"category": "候选人资料", "retrieved_at": "2026-10-23"})


def interview(ident, title, url, company, role, date, outcome, topics, questions, use, limits, **extra):
    record = {"id": ident, "title": title, "url": url, "company": company, "role": role, "date": date, "outcome": outcome, "topics": topics, "project_questions": questions, "recommended_use": use, "limitations": limits, "access_level": "原始正文实际取得并核读；只保存专业归纳和必要短摘录", "fulltext_verified": True, "confidence": "B：公开面试自述可读，录用和技术答案未获独立认证", "category": "面经复盘", "retrieved_at": "2026-10-23"}
    record.update(extra)
    return record


interviews = [
    interview("INT64", "CocaineCong：字节Go三轮技术面，项目深挖原文已省略", gofile("a. 字节跳动.md"), "字节跳动", "历史Go开发", "固定文档提交2022-10-07；具体面试年月未逐条核实", "没有在所读文件明确最终offer或SSP", ["Go/GMP", "I/O复用", "TCP", "数据库索引", "死锁", "Kafka", "TLS", "算法"], ["项目深挖被作者主动省略，不能从题单恢复个人项目", "三轮分别覆盖网络与Go、索引与锁、消息可靠性与安全"], "用分轮结构查基础知识盲区；随附答案是历史笔记，应另核原理与版本。", ["不是SSP结果证据，也没有完整项目问题", "答案未逐条校对，不当标准答案背诵"], author="CocaineCong", sample_group="同作者历史Go面试；三轮仍算一份逻辑资料"),
    interview("INT65", "CocaineCong：B站Go两轮失败复盘与流量突增追问", gofile("b. B站.md"), "哔哩哔哩", "历史Go开发", "固定文档提交2022-10-07；具体面试年月未逐条核实", "作者自述二面后淘汰，不是offer或SSP案例", ["Go map/channel", "GMP", "Linux", "MySQL", "分布式锁", "TCP", "流量突增", "算法"], ["只给出项目流量突然增长的问题，没有本人业务项目细节"], "与成功叙述对照，避免把答出题目直接等同录用；按问题查漏，答案另核。", ["文件里的hmap代码属于历史语境；Go官方说明1.24改用Swiss Table实现，不直接套作当前版本答案", "技术回答混有简化表述，不逐条背诵"], author="CocaineCong", version_check_url="https://go.dev/blog/swisstable", sample_group="同作者另一公司失败自述"),
    interview("INT66", "DreamCats：同一班车项目在字节、京东、腾讯的本人多轮对照", dream("Java/mianjing/README.md", 24), "字节／京东／腾讯", "历史Java后端", "面经标7—8月，年份未知；资料仓固定提交2024-12-02", "京东offer、字节意向书；腾讯自评不理想；均未写SSP", ["项目拆分", "Dubbo", "JWT/SSO", "Redis锁", "订单超时", "RocketMQ", "消息幂等", "JVM", "MySQL", "算法"], ["为什么将班车系统拆成四服务、为什么选择Dubbo？", "订单自动取消、事务消息、幂等与登录Token如何实现？", "京东继续追问班车到点更新状态；腾讯更偏锁、JVM、数据库恢复和一致性算法"], "这是本轮项目与面经对应最直接的一组；按原文公司和日期段阅读，不将多轮计作多位成功者。", ["字节文件拼有多次流程，未逐次核明岗位，不能归成一条固定三轮", "腾讯只写自评，不能当HR确认淘汰；档位未知"], author="DreamCats", candidate_group="CV21_DreamCats", source_findings=[{"url": dream("Java/mianjing/my字节.md", 12), "finding": "项目相关问题及后续多轮记录"}, {"url": dream("Java/mianjing/my京东.md", 9), "finding": "一面基础/幂等与二面业务，末尾明确offer"}, {"url": dream("Java/mianjing/my腾讯.md", 8), "finding": "130分钟一面问题与作者自评"}]),
    interview("INT67", "阿里云Agent一面：项目取舍、RPC与AI Coding热更新", "https://www.nowcoder.com/discuss/872120976190816256", "阿里云", "Agent面试，招聘类型原帖未明确", "原帖标题4.10、页面只见月日；导航索引标2026，年份未由正文确认", "未核到录用或SSP", ["工作流与Agent", "实习项目", "IPC", "RPC/HTTP", "AI Coding", "配置热更新"], ["项目开发难点与后续改进，工作流和Agent如何选？", "区分进程间与跨主机通信，解释RPC选择", "使用AI实现本地YAML/INI配置监听热更新，并继续审查修改方案"], "体现Agent岗位仍会追基础通信、项目贡献和代码审查；不只考框架名。", ["单篇自述不代表阿里云统一门槛", "作者关于RPC快慢的回答和面试官说法不直接当技术结论", "未给本人项目仓库"]),
    interview("INT68", "华为AI应用实习：专业面、主管面与offer时间线", "https://www.nowcoder.com/discuss/884479038142586880", "华为云软件研发部／杭州研究所（作者自述）", "AI应用工程师-AI技术应用；原帖带27届实习标签", "原帖列3.31至5.25过程；只标月日，年份未由正文确认", "作者自述5.25收到offer邮件；未写SSP", ["个人贡献", "项目架构", "团队协作", "科研/竞赛", "Agent架构", "三数之和"], ["实习负责哪些模块、产出是什么，项目各阶段做了什么？", "科研/项目困难如何分析和解决，在团队中是主导还是配合？", "Agent概念、宏观架构与系统准备方式"], "重点对照技术面与主管面对个人贡献的不同问法，补足项目真实性、时间线和协作表达。", ["仅该作者流程，不能把跳过机考条件推广到所有申请者", "项目及竞赛效果仍是自述，没有对应代码仓库或完整CV"]),
    interview("INT69", "百度27届Agent一面：上下文压缩、内部RAG与数据库建模", "https://www.nowcoder.com/discuss/921590204903723008", "百度MEG广告投放部门（作者自述）", "27届秋招大模型研发Agent方向", "原帖标8.18，27届秋招；具体年份未由正文日期确认", "原帖提后续二面，未核最终结果或SSP", ["Context/Harness", "上下文压缩", "RAG", "数据库索引", "前端", "算法"], ["上下文接近窗口上限如何处理，如何设计压缩？", "团队内部知识问答RAG从零如何搭建？", "K线表如何建模，项目如何使用索引？"], "可研究AI工程与传统后端、前端基础交叉的提问范围；专有产品内部实现需回官方来源核实。", ["文中Claude Code“三层压缩”只是作者转述的问题，未验证产品实际实现", "不能与INT70自动视作同一个候选人的连续两轮", "没有本人项目源码、指标或SSP证据"]),
    interview("INT70", "百度Agent二面自述：C端架构、数据流与工具循环边界", "https://www.nowcoder.com/discuss/920461634072477696", "百度（作者自述）", "大模型研发Agent二面", "导航索引标2026-08-21，正文未给完整年月日，作为待核日期", "未核最终结果或SSP", ["C端Agent架构", "工具调用", "重复动作检测", "超时降级", "Coding Agent数据流", "API编排"], ["C端Agent有哪些模块，各类Agent产品如何比较？", "一次用户输入到工具执行的流程如何说明？", "如何避免失败工具无限重复，只给LLM API如何搭建Agent？"], "提取六道设计题的思考范围；把面试题与作者事后补写答案分开。", ["可读正文为2588字的题目与部分解答，部分图表/后续内容未取得；不标整篇所有材料完整核读", "延迟数字、产品分类和确认写文件行为是作者说法，未验证，不当事实引用", "原文标题二面不能证明与INT69同一人"], fulltext_verified=False, access_level="已读公开可见2588字；题目及部分事后解答，未读图片或缺失后续"),
]

project = {"id": "PRO19", "title": "SchoolBus：本人面经直接关联的预约项目，附v1代码局限", "url": "https://github.com/DreamCats/school-bus/tree/" + school_sha, "author": "DreamCats；团队与第三方框架边界见README", "commit": school_sha, "category": "项目参考", "retrieved_at": "2026-10-23", "stack": ["Java", "Spring Boot", "MyBatis", "Dubbo", "MySQL", "Redis", "RocketMQ", "JWT/SSO", "Sentinel"], "project_relationship": "CV21/INT66本人字节和京东面经直接提微服务班车，根目录直接署项目来源；不是只凭同账号配项目", "outcome": "作者京东offer、字节意向书；SSP未证，不以项目质量推导档位", "source_findings": [{"url": school("README.md", 214), "finding": "README给出求职简历写法与四服务范围；同文说明在Guns4.2基础开发，前端另链他人仓库"}, {"url": school("school-bus/guns-order/src/main/java/com/stylefeng/guns/rest/modular/order/OrderServiceImpl.java", 203), "finding": "v1实际存在下单、过期键设置和异常补偿消息发送，能和面经问题对照"}], "strengths": ["业务主线和文档较具体，同一项目在不同公司面经中反复被深挖", "源码含多版本，可比较描述、实现与贡献边界；不把框架及团队全部算个人原创"], "static_risks": [{"url": school("school-bus/guns-order/src/main/java/com/stylefeng/guns/rest/modular/order/OrderServiceImpl.java", 273), "finding": "v1补偿消息发送失败后只打印异常；所读路径未见持久化待补偿记录或恢复流程。进程崩溃和失败重发需另验证。"}, {"url": school("school-bus/guns-bus/src/main/java/com/stylefeng/guns/rest/modular/bus/mq/OrderSeatsCancleListener.java", 52), "finding": "去重判断、业务执行、写入Redis标记为三个步骤，不能只凭缓存判断就证明并发消费幂等。"}, {"url": school("school-bus/guns-order/src/main/java/com/stylefeng/guns/rest/modular/order/OrderServiceImpl.java", 52), "finding": "单例服务中tag是可变成员，下单中反复赋值；并发请求存在覆盖补偿标签的静态风险，未做并发复现。"}, {"url": school("school-bus/guns-order/src/main/java/com/stylefeng/guns/rest/modular/order/rd/RedisKeyExpirationListener.java", 39), "finding": "v1监听过期键并发起关闭订单；只读这个入口不能证明断线恢复、通知遗漏补偿或与支付竞态已处理。"}], "recommended_use": "把本人被问过的业务点对应到实现，再检查失败处理和一致性声明；适合信息调研中的项目取舍分析，个人项目设计继续暂缓。", "limitations": ["以上仅固定提交school-bus/下v1路径的静态观察；同仓另有school-bus-cloud版本，不把局部风险泛化为全版本结论", "只读README、相关文档和三个Java文件关键段；未构建、压测或运行第三方代码", "高性能、高可用是作者描述，未验证指标；不是SSP案例背书"], "license_notes": "固定源码树未发现名为LICENSE/COPYING的文件，尚未确认整库再分发授权；Guns等第三方组件须分别遵循许可，不据公开可读推定整仓授权。", "archive_status": "未新增源码ZIP；保留固定源码入口与原创分析", "confidence": "B：归属与具体代码可核；运行效果、许可和SSP未闭环"}

blocked = []
for name in ["github_ssp_round4_fulltext_access.json", "github_ssp_round4_follow_article_reads.json"]:
    for r in load(name):
        if "nowcoder.com" in r["url"] and r.get("status") == 200 and r.get("body_length", 0) == 0:
            blocked.append({"title": r.get("title", "牛客待核原帖").removesuffix("_牛客网"), "url": r["url"], "status": "HTTP200但本轮未取得正文，只有标题或页面外壳；不等同明确限流", "to_verify": ["本人身份、岗位、年月与实际面试问题", "录用及SSP是否是本人正式结果", "本人项目和GitHub；若为转载/教程请注明"]})
blocked.append({"title": "小米AI Agent一面（暑期）：付费问答的公开部分", "url": "https://www.nowcoder.com/discuss/891698510574153728", "status": "公开部分可读，页尾提示剩余60%需购买或订阅；未付费、未读完整内容", "to_verify": ["这是否本人逐轮记录，还是事后教学问答", "实际项目仓库、指标和录用结果；目前不当SSP成功证据"]})
blocked.append({"title": "鬼卞2019字节SSP来稿的原始公众号页面", "url": original["url"], "status": "HTTP200显示环境异常验证页，未取得原始正文；GitHub收录版本已读", "to_verify": ["原文署名和结果是否与GitHub来稿一致", "是否有本人GitHub、GSoC具体任务或数据库赛源码"]})

value = {"date": "2026-10-23", "candidates": candidates, "interviews": interviews, "projects": [project], "blocked_new": blocked, "method": "第四轮转向GitHub署名来稿、个人面经目录、固定源码与Agent原帖追源；实际并行代理执行服务失败后由根代理接手。联网搜索连接器一次返回空错误，随后使用公开requests GET。未付费、未联系作者、未运行第三方项目。", "limits": "本轮仅新增1位历史署名来稿中的SSP自述；不是新核实的近期Agent SSP完整链。失败面经、意向书、普通offer和SSP分别标注，未保证检索穷尽。"}
(BASE / "github_ssp_round4_records.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"candidates": len(candidates), "interviews": len(interviews), "projects": 1, "new_manual_links": len(blocked)}, ensure_ascii=False))
