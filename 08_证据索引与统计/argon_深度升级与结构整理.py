"""执行四维深度整理升级：
1. 目录结构整理：收敛 08_证据索引与统计 零散快照、创建 03 精选简历可读命名直达目录、生成 4 本单文件 Markdown 合集；
2. 内容转化升级：提炼【6组简历写法正反例模板】与【10大追问三层应答骨架】，生成 argon_实战备考手册_简历模板与答题骨架.html/.md 并嵌入图册与面经页；
3. 项目免解压源码精读：从 05_项目源码归档 本地 ZIP 提取 8 个核心项目的真实代码片段 + 架构状态流转图，嵌入项目指南与面经页；
4. 全站交互升级：生成 argon_evidence_drawer.js 右侧滑出式证据抽屉组件，并在 argon_00_开始阅读.html 增加一站式备考专题工作台。
"""
from __future__ import annotations

from html import escape, unescape
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import os
import re
import shutil
import zipfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def E(val):
    return escape(str(val or ''), quote=True)


def clean_item(text):
    return str(text or '').strip().rstrip('。；; ')


# ==============================================================================
# 1. 提取 8 个重点项目的本地真实源码片段与可视化流程链
# ==============================================================================
PROJECT_FLOWS_AND_SPECS = {
    'PRO19': {
        'flow': [
            '用户发起预约下单 (addOrder)',
            '检查班次余票与状态',
            'RocketMQ 投递延迟/事务消息',
            '支付超时或取消触发 OrderSeatsCancleListener',
            '⚠️ 风险窗口：先查幂等标记 → 执行退票 → 再写标记（非原子）'
        ],
        'zip': 'SchoolBus_固定源码选读.zip',
        'files': [
            ('school-bus/guns-order/src/main/java/com/stylefeng/guns/rest/modular/order/OrderServiceImpl.java', 1, 75, '下单主流程与补偿消息发送（注意异常分支仅打印日志）'),
            ('school-bus/guns-bus/src/main/java/com/stylefeng/guns/rest/modular/bus/mq/OrderSeatsCancleListener.java', 1, 70, '取消订单消费监听器（面试高频追问：查改写分离的并发幂等窗口）'),
        ],
        'fix_tip': '面试改进方案：① 将“查幂等标记 + 退还座位 + 写消费状态”放入同一数据库本地事务，或基于唯一业务键（order_id）做 INSERT IGNORE / 唯一索引防重；② 补偿发送失败必须写入本地异常重试表而非仅 log.error。'
    },
    'PRO20': {
        'flow': [
            '提交评测代码 (DefaultSubmissionWritePort)',
            '本地事务内写 Submission + JudgeOutbox 表',
            'JudgeOutboxDispatcher 轮询拉取待投递记录',
            '投递至 Redis Stream 并更新 Outbox 状态',
            'Judge Worker 租约抢占 + CAS 条件写回评测结果'
        ],
        'zip': 'UltiCode_固定源码文本_去联系字段_d53b582e2f.zip',
        'files': [
            ('services/submission/src/main/java/com/ulticode/modules/submission/port/DefaultSubmissionWritePort.java', 1, 80, '提交写入口：本地事务同时落库提交单与 Outbox 消息'),
            ('services/submission/src/main/java/com/ulticode/modules/queue/outbox/dispatcher/JudgeOutboxDispatcher.java', 1, 85, 'Outbox 异步分发器：拉取未投递记录推送至 Redis Stream'),
        ],
        'fix_tip': '面试改进方案：当 Redis Stream 投递成功但更新 DB Outbox 状态前进程崩溃，会导致重复投递；因此消费端（Judge Worker）必须结合 SubmissionMapper 的状态条件更新（WHERE status = RUNNING）实现幂等闭环。'
    },
    'PRO21': {
        'flow': [
            '并发请求查询同一 Key',
            'SyncSupport 借助 ConcurrentHashMap.compute 选举单机 Leader',
            'Leader 发起真实 DB/下游回源，Follower 共享 CompletableFuture 等待',
            'EarlyRefresh 在过期窗口内异步触发后台 CAS 刷新 TTL',
            '⚠️ 边界：单机 Map 仅防进程内击穿，跨实例仍会各自回源一次'
        ],
        'zip': 'ResiCache_固定源码文本_去联系字段_1ed3be36af.zip',
        'files': [
            ('src/main/java/io/github/davidhlp/spring/cache/redis/cache/SyncRole.java', 1, 70, 'Single-Flight 并发角色定义（Leader 回源 vs Follower 等待共享 Future）'),
            ('src/main/java/io/github/davidhlp/spring/cache/redis/cache/EarlyRefresh.java', 1, 80, '逻辑过期与提前异步刷新控制（CAS 防并发重复刷新）'),
        ],
        'fix_tip': '面试改进方案：讲清楚“进程内 Single-Flight（零额外网络开销，集群最多 N 个节点回源 N 次）”与“分布式互斥锁（全局 1 次回源，但增加 Redis 锁 RTT 与死锁超时风险）”的折中取舍。'
    },
    'PRO09': {
        'flow': [
            'HTTP 请求进入 ShenYu 响应式网关 WebFlux 管道',
            '經過 Plugin 责任链（OAuth2 鉴权 → RateLimiter 限流 → 路由转发）',
            'Redis Lua 脚本执行令牌桶/滑动窗口原子扣减',
            '异步投递访问日志至 RocketMQ (RocketMqLogCollectClient)',
            '集成测试验证网关鉴权与日志链路完整性'
        ],
        'zip': 'apache__shenyu__34f2ed036747.zip',
        'files': [
            ('shenyu-plugin/shenyu-plugin-fault-tolerance/shenyu-plugin-ratelimiter/src/main/java/org/apache/shenyu/plugin/ratelimiter/RateLimiterPlugin.java', 1, 75, '网关限流插件核心执行链（WebFlux 响应式放行与拒绝）'),
            ('shenyu-integrated-test/shenyu-integrated-test-http/src/test/java/org/apache/shenyu/integrated/test/http/combination/RocketMqPluginTest.java', 1, 75, 'CV05 本人合并 PR：RocketMQ 日志插件端到端集成测试'),
        ],
        'fix_tip': '面试改进方案：展示开源贡献时，重点说明你如何阅读网关插件生命周期源码、如何构造可复现的集成测试上下文，切忌把整个 ShenYu 网关架构吹嘘为个人独立开发。'
    },
    'PRO04': {
        'flow': [
            '初始化 AgentEngineConfiguration 与状态图节点',
            '请求进入图执行器，每步状态通过 AgentStateMapper 持久化',
            '命中敏感工具调用时触发 AgentConfirmDenialMiddleware 拦截',
            '等待人工审批确认（Approve 继续执行 / Deny 注入拒绝反馈）',
            '⚠️ 边界：中间件拦截不替代底层微服务 API 的服务端 RBAC 鉴权'
        ],
        'zip': 'nageoffer__ragent__ff93871ab88f.zip',
        'files': [
            ('agent/src/main/java/com/nageoffer/ai/ragent/agent/config/AgentEngineConfiguration.java', 1, 75, 'Java Agent 引擎配置与组件装配入口'),
            ('agent/src/main/java/com/nageoffer/ai/ragent/agent/confirm/AgentConfirmDenialMiddleware.java', 1, 75, '工具调用人工确认与拒绝处理中间件（Human-in-the-loop）'),
        ],
        'fix_tip': '面试改进方案：除保存对话/节点状态到数据库外，还需为外部写操作工具设计唯一幂等 RequestID，防止进程从 Checkpoint 恢复重跑时造成外部业务重复扣款或重复发文。'
    },
    'PRO06': {
        'flow': [
            '用户输入复杂研究课题 → Supervisor 拆解子问题',
            '并行派发多个 Researcher 子图执行检索与工具调用',
            '子图局部压缩上下文后汇总至最终报告生成节点',
            '运行 tests/evaluators.py 对相关性、结构、事实性逐维打分',
            '运行 tests/pairwise_evaluation.py 与基线版本做 A/B 成对比较'
        ],
        'zip': 'langchain-ai__open_deep_research__1b7d2e80db9f.zip',
        'files': [
            ('tests/evaluators.py', 1, 80, '多维自动化评测器实现（面试高频追问：如何定量评估 Agent 输出质量）'),
            ('tests/pairwise_evaluation.py', 1, 75, 'A/B 成对比较评测脚本（对比改造前后策略优劣）'),
        ],
        'fix_tip': '面试改进方案：LLM-as-a-Judge 存在位置偏见（倾向选第一个）和长度偏见（倾向选长文）；面试时应提出“交换 A/B 顺序双向盲测 + 统计固定 Token 预算下的任务成功率与 P95 延迟”。'
    },
    'PRO24': {
        'flow': [
            '根节点接收复杂任务 → 判断是否需要拆解 (TaskTree)',
            '递归生成子任务节点并交由并发 Worker 线程池执行',
            '监控 Straggler（慢节点）触发动态重拆与上下文汇总',
            'examples/benchmark.py 运行评测并统计累计 Token',
            '⚠️ 缺陷：benchmark 用正则匹配代替代码真实编译运行；Token 为事后统计非硬熔断'
        ],
        'zip': 'Sprout_固定源码文本_去联系字段_3ecd36e5a4.zip',
        'files': [
            ('sprout/task_tree.py', 1, 80, '树形任务拆解与节点状态流转核心实现'),
            ('examples/benchmark.py', 1, 80, '基准测试与评分实现（注意其正则评分与事后 Token 统计的局限）'),
        ],
        'fix_tip': '面试改进方案：① 代码生成类任务必须在受限容器中执行真实单测（Pass@1）而非正则匹配；② 在 LLM 调用入口前置 Token 预算守卫（BudgetGuard），超限立即降级或终止递归。'
    },
    'PRO25': {
        'flow': [
            '用户输入指令 → 检索 EpisodeMemory 历史情景记忆',
            '组装上下文与桌面动作工具集（文件/终端/系统操作）',
            'WorkspaceManager 校验路径是否在允许工作区内',
            '调用平台沙箱执行器 (macos-sandbox.ts / windows-sandbox.ts)',
            '⚠️ 风险：macOS 沙箱失败回退分支可能重复执行；Windows 改环境变量不等于内核隔离'
        ],
        'zip': 'NoWorries_固定文本选读_去联系字段_c811e697bb.zip',
        'files': [
            ('noworries_app/apps/desktop/src/main/sandbox/macos-sandbox.ts', 1, 80, 'macOS 沙箱执行器与异常降级分支（注意回退重复执行风险）'),
            ('noworries_app/apps/desktop/src/main/clawdbot/memory/episode-memory.ts', 1, 75, '桌面 Agent 情景记忆存储与检索模块'),
        ],
        'fix_tip': '面试改进方案：区分“应用层路径白名单校验”、“环境变量重定向”与“OS 级沙箱（如 macOS sandbox-exec / Linux bubblewrap / Docker）”的安全边界；当沙箱启动失败时应直接拒绝执行敏感写命令，绝不可静默降级为无沙箱裸跑。'
    }
}


def extract_zip_snippets():
    """从 05_项目源码归档 的本地 ZIP 中提取真实源码片段。"""
    archive_root = ROOT / '05_项目源码归档'
    extracted = {}
    for pid, spec in PROJECT_FLOWS_AND_SPECS.items():
        zips = list(archive_root.rglob(spec['zip']))
        snippets = []
        if zips:
            with zipfile.ZipFile(zips[0]) as zf:
                names = zf.namelist()
                for rel_path, start_line, end_line, desc in spec['files']:
                    match = next((n for n in names if n.endswith(rel_path) or Path(rel_path).name in n), None)
                    if match:
                        raw_text = zf.read(match).decode('utf-8', errors='replace')
                        lines = raw_text.splitlines()
                        selected = lines[max(0, start_line - 1):min(len(lines), end_line)]
                        numbered = '\n'.join(f'{i:3d} | {line}' for i, line in enumerate(selected, start=max(1, start_line)))
                        snippets.append({
                            'path': rel_path,
                            'desc': desc,
                            'code': numbered
                        })
        extracted[pid] = {
            'flow': spec['flow'],
            'snippets': snippets,
            'fix_tip': spec['fix_tip']
        }
    return extracted


# ==============================================================================
# 2. 六组简历写法 Before / After 正反例模板 & 十大追问三层应答骨架
# ==============================================================================
RESUME_TEMPLATES = [
    {
        'category': '后端 · 缓存并发与一致性',
        'ref_ids': ['CV28', 'PRO21', 'CV01', 'INT101'],
        'bad': '使用 Redis 缓存热点数据，解决了缓存击穿和雪崩问题，大幅提升了系统查询性能。',
        'good': '针对高频查询接口，基于 CompletableFuture 实现进程内 Single-Flight（单飞）回源合并，将同 Key 并发回源请求收敛为单次 DB 查询；结合逻辑过期 + CAS 异步提前刷新机制消除热 Key 失效毛刺，并在回源异常分支显式清理占位 Future 防止线程死等。在 5000 QPS 压测下回源率下降 92%，P99 延迟从 180ms 降至 14ms。',
        'why': '面试官看到“解决了击穿”必问怎么实现的。好写法直接交代了并发原语（CompletableFuture + CAS）、异常兜底（清理失败占位）和量化边界（进程内单飞 vs 跨实例锁）。'
    },
    {
        'category': '后端 · 异步消息、幂等与事务外盒 (Outbox)',
        'ref_ids': ['CV28', 'PRO20', 'CV21', 'PRO19', 'INT85'],
        'bad': '引入 RocketMQ / Redis Stream 实现订单与评测任务异步解耦，保证消息不丢失和消费幂等。',
        'good': '为消除 DB 本地事务与外部 MQ 投递的跨组件不一致窗口，采用本地事务外盒（Transactional Outbox）模式将业务单据与待投递事件同库原子写入，由独立 Dispatcher 轮询推送至 Redis Stream；消费端基于业务唯一键 + 状态机条件更新（WHERE status = PENDING）实现并发幂等，并配套超时租约回收与死信重投机制。',
        'why': '直接点明“为什么不能在 @Transactional 里直接发 MQ”，并给出生产端（Outbox 表）和消费端（条件更新防并发窗口）的完整闭环。'
    },
    {
        'category': '后端 · 数据库索引优化与容量设计',
        'ref_ids': ['CV01', 'INT20', 'INT24', 'INT101'],
        'bad': '负责数据库慢 SQL 优化，通过建立联合索引和分库分表提升了查询效率。',
        'good': '排查百万级通知/订单表慢查询（单表 800 万行，B+ 树约 3 层），通过构建 (merchant_id, status, create_time) 联合覆盖索引并移除 SELECT * 大字段回表，以及将深分页 OFFSET 改造为基于游标（Cursor）的连续翻页，使核心列表接口扫描行数从 12 万降至 50 行以内，慢查询告警归零。',
        'why': '把数据规模、B+ 树层级估算、索引字段顺序、回表消除与深分页改造串成完整证据链，直接封堵面试官的基础追问。'
    },
    {
        'category': 'Agent · 多步状态图编排与中断恢复',
        'ref_ids': ['CV30', 'PRO04', 'PRO24', 'INT41', 'INT84'],
        'bad': '基于 LangGraph / Spring AI Alibaba 搭建多 Agent 智能体工作流，支持复杂任务规划与记忆管理。',
        'good': '针对单次 Prompt 在长链路任务中易丢失约束的问题，设计 Supervisor-Worker 状态图编排引擎：显式定义节点输入输出 Schema 与路由转移条件，基于持久化 Saver 在关键节点落盘 Checkpoint 状态快照；引入单任务 Token 硬预算守卫与循环震荡检测，支持任务中断后从最近检查点幂等恢复执行。',
        'why': '回答了“为什么不用单次调用”、“状态存在哪”、“死循环或超预算怎么办”三个 Agent 面试核心必考题。'
    },
    {
        'category': 'Agent · 工具调用 (MCP/Function Call) 与安全沙箱',
        'ref_ids': ['CV30', 'CV31', 'PRO25', 'OP09', 'INT47'],
        'bad': '接入 MCP 协议与多种外部工具，实现文件读写、代码执行与外部接口自动化调用。',
        'good': '围绕高频业务场景将原子接口收敛为粗粒度语义工具（MCP 协议），在执行器入口实施 JSON Schema 强校验与工作区路径白名单拦截；针对高危写操作引入 Human-in-the-loop 审批中间件与幂等请求号，并在沙箱启动异常时严格熔断阻断（禁止静默回退裸跑），将工具参数幻觉报错率降低 65%。',
        'why': '结合 Anthropic 工具工程原则（OP09）与桌面 Agent 沙箱边界（PRO25），体现出对“模型不可信、写操作有副作用”的成熟工程敬畏。'
    },
    {
        'category': 'Agent · RAG 检索链路与留出集回归评测',
        'ref_ids': ['CV30', 'CV33', 'PRO06', 'OP16', 'INT42'],
        'bad': '使用向量数据库实现 RAG 知识库问答，优化了分块和 Prompt，问答准确率达到 90%。',
        'good': '构建“结构化语义分块 + 向量与 BM25 双路混合召回 + Cross-Encoder 重排（Rerank）”检索流水线；沉淀 120 条真实复杂问答留出评测集（Hold-out Set），自动化追踪召回命中率（Recall@K）、工具调用错误率、单题退化（Regression）及 P95 尾延迟，通过 Bad Case 归因迭代将端到端任务成功率从 62% 提升至 84%。',
        'why': '面试官极度反感拍脑袋的“准确率 90%”。写出混合召回重排 + 固定留出集 + 逐题回归与延迟/成本联合指标，立刻拉开与普通玩具项目的差距。'
    },
]

ANSWER_FRAMEWORKS = {
    'B1': {
        'step1': '先用 30 秒画清请求入口、核心状态流转和上下游依赖，明确指出哪几个类/接口是你本人从零写的，哪部分复用了团队脚手架。',
        'step2': '主动挑出业务中最痛的 1 个约束（如高并发争抢、跨服务状态同步），对比当时考虑过的备选方案及放弃原因（如开发成本 vs 一致性代价）。',
        'step3': '给出可核查的交付物证据（如单测覆盖、上线后修复过的 1 个真实 Bug 或压测对比数据）。'
    },
    'B2': {
        'step1': '报出核心表的数据量级（如千万行）、主键与联合索引结构，说明高频 SQL 是如何命中覆盖索引或避免回表与文件排序（Using filesort）的。',
        'step2': '讲清 Redis 与 MySQL 的读写配合模式（如 Cache-Aside + 延迟双删或 Binlog 异步淘汰），重点剖析并发回源（Single-Flight vs 分布式锁）和缓存失效瞬间的边界。',
        'step3': '用 EXPLAIN 执行计划指标（rows、key、Extra）或压测 QPS/P99 曲线证明优化实效，并坦诚指出单机合并与跨节点互斥的适用边界。'
    },
    'B3': {
        'step1': '画出异步链路的完整状态机（如：已创建 → 待投递 → 处理中 → 成功/失败补偿），说明为什么该场景必须异步化（削峰、解耦或长耗时任务）。',
        'step2': '拆解三大故障窗口：① 生产端 DB 事务成功但 MQ 投递失败（用本地 Outbox 表解决）；② Broker 重复投递（消费端用业务唯一键 + 状态条件更新解决，绝不能先查后写分离）；③ 消费持续失败（重试退避 + 死信队列告警）。',
        'step3': '说明积压监控指标（Consumer Lag）以及当下游服务不可用时的降级与重放恢复演练结果。'
    },
    'B4': {
        'step1': '从你项目实际使用的组件切入（如线程池参数、Go GMP 协程调度、Netty 连接管理或 JVM 内存分配），把底层原理锚定在具体业务配置上。',
        'step2': '分析极端负载下的资源耗尽表现（如线程池队列打满触发拒绝策略、连接池泄漏、FullGC 停顿或 TIME_WAIT 堆积）。',
        'step3': '结合手撕算法/并发编程题（如手写阻塞队列、LRU 或交替打印），展现扎实的代码基本功与边界检查习惯。'
    },
    'B5': {
        'step1': '按“现象告警 → 指标定位（Metrics）→ 链路追踪（Trace）→ 日志与堆栈（Logs/Arthas/pprof）”的标准化排障路径复盘一次真实故障。',
        'step2': '说明当时的止血措施（限流、降级、回滚或熔断）与根因修复方案（如修复锁粒度、补齐超时设置或消除 N+1 查询）。',
        'step3': '交代故障后的工程复盘闭环：新增了什么监控阈值、补充了哪类混沌/并发集成测试防止问题复发。'
    },
    'A1': {
        'step1': '先回答“为什么不用单次 Prompt 或简单 Workflow”：指出任务存在动态分支、多轮外部信息依赖或长上下文污染，必须引入状态图编排。',
        'step2': '讲清架构控制权：由确定性代码控制状态机流转、重试上限与停止条件，大模型仅负责节点内的局部推理或结构化路由决策。',
        'step3': '给出与单 Agent / 单次调用基线（Baseline）在相同测试集上的成功率、Token 消耗与耗时对比。'
    },
    'A2': {
        'step1': '拆解文档预处理与分块策略（按标题层级/代码块语义切分 + Overlap 保留上下文），说明为何纯向量检索在专有名词/精确代码号场景会失效。',
        'step2': '详述“向量检索 + BM25 关键词检索”双路召回与 Cross-Encoder 重排（Rerank）管线，以及当检索结果置信度过低时的拒答或改写查询（Query Rewrite）机制。',
        'step3': '展示工具 Schema 的精简设计、必填参数校验以及模型产生幻觉参数时的结构化错误回传（让模型自我修正而非直接崩溃）。'
    },
    'A3': {
        'step1': '区分“对话历史（Memory）”与“执行状态机快照（Checkpoint）”：说明每个节点执行完毕后如何将状态序列化落盘（如 PostgreSQL/Redis）。',
        'step2': '重点解答“工具执行一半超时或进程重启怎么办”：只读查询工具可直接指数退避重试；外部写操作工具必须携带幂等键或先查询远端状态再决定重放/补偿。',
        'step3': '说明全链路 Trace_ID 与节点级结构化日志设计，确保任意一次卡死都能在 1 分钟内定位到具体 Prompt、工具入参与原始响应。'
    },
    'A4': {
        'step1': '明确划分工具安全等级：只读工具自动放行；涉及文件修改、命令执行、数据库写入或外部资金/消息发送的工具必须经过安全拦截层。',
        'step2': '讲清三道防线：① 服务端路径白名单与命令语法树校验；② Human-in-the-loop 人工审批挂起与恢复中间件；③ OS/容器级沙箱隔离（区分修改环境变量与真正系统隔离的差异）。',
        'step3': '针对多 Agent 并发修改同一资源场景，说明乐观锁版本号、工作区隔离或任务锁机制，且沙箱异常时严禁静默降级裸跑。'
    },
    'A5': {
        'step1': '说明上下文窗口的分层管理策略：系统核心约束与用户红线置顶常驻（Pinned），历史工具长输出做摘要压缩或按需分页读取，配合 Prompt Cache 降低首字延迟（TTFT）。',
        'step2': '拆解评测与成本账本：区分“事后计费统计”与“调用前硬预算熔断（Budget Guard）”，说明如何用固定留出集监控每次改版后的单题退化（Regression）。',
        'step3': '回到服务端工程底座：说明并发流式响应（SSE/WebSocket）、协程/线程池调度与背压控制，证明自己不仅懂 Prompt，更具备扎实的后端系统功底。'
    }
}


def render_code_panel_html(pid, snippets_by_pid):
    data = snippets_by_pid.get(pid)
    if not data:
        return ''
    flow_steps = ''.join(
        f'<span class="flow-step"><b>{idx}</b> {E(step)}</span>'
        + ('<span class="flow-arrow">→</span>' if idx < len(data['flow']) else '')
        for idx, step in enumerate(data['flow'], 1)
    )
    code_blocks = []
    for s in data['snippets']:
        code_blocks.append(
            f'<div class="code-card"><div class="code-head"><b>{E(s["desc"])}</b> '
            f'<code>{E(s["path"])}</code></div>'
            f'<pre class="code-pre"><code>{escape(s["code"])}</code></pre></div>'
        )
    return (
        f'<details class="code-walkthrough"><summary>展开免解压源码精读：调用链流程图 + 核心源码片段 + 面试改进方案 ({E(pid)})</summary>'
        f'<div class="flow-bar">{flow_steps}</div>'
        f'<div class="code-grid">{"".join(code_blocks)}</div>'
        f'<p class="note"><b>面试追问应对与代码改进方案：</b>{E(data["fix_tip"])}</p></details>'
    )


def build_handbook_pages(snippets_by_pid, synthesis, comp):
    """生成根目录 argon_实战备考手册_简历模板与答题骨架.html 与 .md。"""
    from argon_生成可读调研总报告 import shell, link, bullet_html

    html_parts = [
        '<section class="report-page" id="handbook-top">',
        '<div class="kicker">ACTIONABLE PLAYBOOK · 简历改写模板 × 面试三层答题骨架 × 核心源码走读</div>',
        '<h1>后端与 Agent 实习：实战备考手册</h1>',
        '<p class="lead">本手册将 239 条公开证据直接转化为<b>可复制的简历写法模板</b>、<b>10 大高频追问的三步应答公式</b>以及<b>8 个核心项目的免解压源码走读</b>，解决“看懂了报告但不知道怎么写简历、怎么答面试”的最后一公里问题。</p>',
        '<div class="bottom-links">',
        '<a href="#resume-templates">01 六大场景简历 Before/After 模板</a>',
        '<a href="#backend-answers">02 后端五大追问三层答题骨架</a>',
        '<a href="#agent-answers">03 Agent五大追问三层答题骨架</a>',
        '<a href="#code-walkthroughs">04 八大核心项目免解压源码走读</a>',
        '</div></section>'
    ]

    # Section 1: 简历模板
    res_sec = [
        '<section class="report-page" id="resume-templates">',
        '<div class="kicker">01 · 简历专业模块改写指南</div>',
        '<h2>六大高频场景：平庸简历写法 vs 大厂高分写法</h2>',
        '<p class="lead">提炼自 CV01（字节后端SSP）、CV28（后端完整履历）、CV30（字节Agent实习）、CV31（Agent实习+开源直连）等真实样本。写简历的核心原则是：<b>业务场景/约束 + 核心机制原语 + 异常/并发兜底边界 + 可验证指标</b>。</p>'
    ]
    for idx, item in enumerate(RESUME_TEMPLATES, 1):
        refs = ' '.join(f'<a href="01_调研报告/argon_资料检索与证据详表.html#{rid}">{rid}</a>' for rid in item['ref_ids'])
        res_sec.append(
            f'<div class="qa-block"><h3><span class="number">0{idx}</span>{E(item["category"])}</h3>'
            f'<div class="two">'
            f'<div class="box warn-box"><h3>❌ 平庸写法（容易被面试官一问就穿）</h3><p>“{E(item["bad"])}”</p></div>'
            f'<div class="box"><h3>✅ 高分写法（自带追问锚点与工程深度）</h3><p>“{E(item["good"])}”</p></div>'
            f'</div>'
            f'<p class="small" style="margin-top:8px"><b>为什么这样改：</b>{E(item["why"])} · <b>对标证据：</b>{refs}</p></div>'
        )
    res_sec.append('</section>')
    html_parts.append(''.join(res_sec))

    # Section 2 & 3: 后端 & Agent 答题骨架
    for key, sec_id, kicker, title in [
        ('backend_findings', 'backend-answers', '02 · 后端面试三层应答骨架', '后端五大高频追问簇：三步递进答题公式'),
        ('agent_findings', 'agent-answers', '03 · AGENT面试三层应答骨架', 'Agent 工程五大高频追问簇：三步递进答题公式'),
    ]:
        sec = [f'<section class="report-page" id="{sec_id}"><div class="kicker">{E(kicker)}</div><h2>{E(title)}</h2>']
        for f in synthesis[key]:
            fid = f['id']
            fw = ANSWER_FRAMEWORKS.get(fid, {})
            qs = '；'.join(clean_item(q) for s in f.get('sources', [])[:2] for q in s.get('source_questions', [])[:1]) + '。'
            sec.append(
                f'<div class="qa-block" id="fw-{E(fid)}">'
                f'<h3><span class="number">{E(fid)}</span>{E(f["title"])}</h3>'
                f'<p class="question">典型真题切入：{E(qs)}</p>'
                f'<div class="three">'
                f'<div class="box"><h3>第一步：讲清约束与职责</h3><p>{E(fw.get("step1",""))}</p></div>'
                f'<div class="box"><h3>第二步：拆解并发/失败边界</h3><p>{E(fw.get("step2",""))}</p></div>'
                f'<div class="box"><h3>第三步：给出量化验证证据</h3><p>{E(fw.get("step3",""))}</p></div>'
                f'</div></div>'
            )
        sec.append('</section>')
        html_parts.append(''.join(sec))

    # Section 4: 8个核心项目免解压源码走读
    code_sec = [
        '<section class="report-page" id="code-walkthroughs">',
        '<div class="kicker">04 · 八个重点项目免解压源码走读</div>',
        '<h2>核心调用链流程图 + 真实源码片段 + 漏洞修复方案</h2>',
        '<p class="lead">直接从本地归档源码包（05_项目源码归档）提取最关键的 2 个代码文件片段，配合调用链流程图与面试改进方案，无需解压 ZIP 即可完成代码级精读。</p>'
    ]
    for p in synthesis['projects']:
        pid = p['id']
        code_sec.append(
            f'<div class="qa-block" id="code-{E(pid)}">'
            f'<h3>{E(pid)} · {E(p["title"])} <span class="pill core">{E(p["kind"])}</span></h3>'
            f'<p>{E(p["learn"])}</p>'
            + render_code_panel_html(pid, snippets_by_pid).replace('<details class="code-walkthrough">', '<details class="code-walkthrough" open>')
            + '</div>'
        )
    code_sec.append('</section>')
    html_parts.append(''.join(code_sec))

    extra_css = (
        '<style>'
        '.flow-bar{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:12px 0;padding:12px;background:#f2f6f4;border:1px solid #c9dad4;border-radius:4px}'
        '.flow-step{background:#fff;border:1px solid #9ab7af;padding:5px 10px;border-radius:4px;font-size:13px;line-height:1.4}'
        '.flow-step b{color:#a3482d;margin-right:4px}'
        '.flow-arrow{color:#1d5c59;font-weight:700}'
        '.code-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:12px 0}'
        '.code-card{border:1px solid #cbd6d1;border-radius:4px;overflow:hidden;background:#1e2629;color:#e6edf0;min-width:0}'
        '.code-head{background:#2b383c;padding:8px 12px;font-size:12.5px;border-bottom:1px solid #3c4d52;display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap}'
        '.code-head b{color:#fff}.code-head code{color:#9ad1c6;font-size:11.5px}'
        '.code-pre{margin:0;padding:10px 12px;font:11.5px/1.55 Consolas,"Courier New",monospace;overflow-x:auto;max-height:340px;white-space:pre}'
        'details.code-walkthrough{margin:12px 0;padding:12px 14px;background:#f8faf8;border:1px solid #ccd8d2;border-radius:4px}'
        'details.code-walkthrough>summary{cursor:pointer;font-weight:700;color:#1d5c59;font-size:14.5px}'
        '@media(max-width:900px){.code-grid{grid-template-columns:1fr}}'
        '</style>'
    )
    page_html = shell('实战备考手册：简历模板与答题骨架', ''.join(html_parts), False, ROOT, 'handbook')
    page_html = page_html.replace('</head>', extra_css + '</head>', 1)
    (ROOT / 'argon_实战备考手册_简历模板与答题骨架.html').write_text(page_html, encoding='utf-8')

    # Markdown 版实战备考手册
    md = [
        '# 后端与 Agent 工程实习：实战备考手册（简历模板 × 答题骨架 × 源码走读）',
        '',
        '> **手册定位**：将 239 条证据提炼为可直接套用的 **6 组简历 Bullet 改写模板**、**10 大高频追问的三步递进应答骨架** 与 **8 个代表性项目的核心源码片段**。',
        '> - 配套网页版：[argon_实战备考手册_简历模板与答题骨架.html](argon_实战备考手册_简历模板与答题骨架.html)',
        '',
        '---',
        '',
        '## 一、六大高频场景：简历 Bullet 正反例改写模板',
        ''
    ]
    for idx, item in enumerate(RESUME_TEMPLATES, 1):
        md += [
            f'### {idx}. {item["category"]}',
            f'- ❌ **平庸写法**：“{item["bad"]}”',
            f'- ✅ **大厂高分写法**：“{item["good"]}”',
            f'- 💡 **改写要点**：{item["why"]}',
            ''
        ]
    md += ['---', '', '## 二、十大面试高频追问簇：三步递进应答骨架', '']
    for key, sub_title in [('backend_findings', '（一）后端开发五大追问簇'), ('agent_findings', '（二）Agent 工程五大追问簇')]:
        md += [f'### {sub_title}', '']
        for f in synthesis[key]:
            fw = ANSWER_FRAMEWORKS.get(f['id'], {})
            md += [
                f'#### {f["id"]} · {f["title"]}',
                f'1. **第一步（讲清业务约束与本人职责）**：{fw.get("step1","")}',
                f'2. **第二步（拆解并发/失败边界与兜底机制）**：{fw.get("step2","")}',
                f'3. **第三步（给出压测或留出集验证证据）**：{fw.get("step3","")}',
                ''
            ]
    md += ['---', '', '## 三、八个重点项目：核心调用链与面试避坑方案', '']
    for p in synthesis['projects']:
        pid = p['id']
        spec = snippets_by_pid.get(pid, {})
        md += [
            f'### {pid} · {p["title"]}',
            f'- **核心调用链**：`{" → ".join(spec.get("flow", []))}`',
            f'- **面试追问应对与代码改进方案**：{spec.get("fix_tip","")}',
            ''
        ]
    (ROOT / 'argon_实战备考手册_简历模板与答题骨架.md').write_text('\n'.join(md) + '\n', encoding='utf-8')


# ==============================================================================
# 3. 生成全站右侧滑出式证据抽屉组件 (argon_evidence_drawer.js)
# ==============================================================================
def build_evidence_drawer_js(rows, comp, visuals, synthesis):
    """构建轻量级全站证据速查抽屉脚本，点击任何 #JDxx/#CVxx/#INTxx/#PROxx/#OPxx/#CAPxx/#DOCxx 即刻右侧预览。"""
    assets_by_cid = {}
    for a in visuals.get('assets', []):
        if a.get('candidate_id'):
            assets_by_cid.setdefault(a['candidate_id'], []).append(a)

    cap_rows = load_json(BASE / '能力要求四类证据对照.json')['rows']
    db = {}
    for r in rows:
        rid = r['id']
        tax = r.get('taxonomy', {})
        item = {
            'id': rid,
            'cat': r.get('category', ''),
            'title': r.get('title', ''),
            'url': r.get('url', ''),
            'track': tax.get('track', ''),
            'rec': tax.get('recruitment', ''),
            'date': tax.get('experience_date_text') or tax.get('source_date_text') or r.get('date') or '',
            'summary': clean_item(r.get('source_summary') or r.get('summary') or r.get('opinion') or ''),
        }
        if rid.startswith('JD'):
            item['company'] = r.get('company', '')
            item['req'] = r.get('required_stack', [])[:6]
            item['pref'] = r.get('preferred_stack', [])[:5]
            item['duties'] = clean_item(r.get('duties', ''))[:240]
        elif rid.startswith('CV') or rid.startswith('OBS'):
            out = r.get('outcome', '')
            if not out and r.get('outcomes'):
                out = '；'.join(f'{x.get("company","")}:{x.get("grade","")}/{x.get("status","")}' for x in r['outcomes'][:4])
            item['outcome'] = out
            item['strength'] = clean_item(r.get('strengths') or r.get('recommendation') or '')[:260]
            item['weakness'] = clean_item(r.get('weaknesses') or r.get('chain_gaps') or '')[:220]
            if rid in assets_by_cid:
                a0 = assets_by_cid[rid][0]
                item['thumb'] = a0.get('thumbnail_file') or (a0.get('preview_files') or [''])[0]
                item['file'] = a0.get('local_file', '')
        elif rid.startswith('INT'):
            qs = r.get('questions') or r.get('project_questions') or r.get('key_questions') or []
            if isinstance(qs, list):
                item['questions'] = [clean_item(x) for x in qs[:8] if clean_item(x)]
            item['topics'] = (r.get('topics') or [])[:6]
        elif rid.startswith('PRO') and rid in comp:
            p = comp[rid]
            item['b_lvl'] = p['backend_priority']['level']
            item['a_lvl'] = p['agent_priority']['level']
            item['strengths'] = [clean_item(x) for x in p.get('strengths', [])[:4]]
            item['limits'] = [clean_item(x) for x in p.get('limitations', [])[:4]]
            item['mods'] = (p['backend_priority'].get('read_modules', []) + p['agent_priority'].get('read_modules', []))[:4]
        db[rid] = item

    for c in cap_rows:
        cid = c['id']
        db[cid] = {
            'id': cid,
            'cat': '核心能力维度',
            'title': c.get('ability', ''),
            'track': c.get('track', '通用'),
            'summary': clean_item(c.get('competency', '')),
            'questions': [clean_item(c.get('question', '')), '常见误区：' + clean_item(c.get('common_pitfall', ''))],
            'mods': c.get('project_ids', [])
        }

    js_code = f"""(() => {{
  const DB = {json.dumps(db, ensure_ascii=False)};
  const style = document.createElement('style');
  style.textContent = `
    .ag-drawer-backdrop {{ position:fixed; inset:0; background:rgba(18,32,35,.35); z-index:9998; opacity:0; pointer-events:none; transition:opacity .2s; }}
    .ag-drawer-backdrop.open {{ opacity:1; pointer-events:auto; }}
    .ag-drawer {{ position:fixed; top:0; right:0; bottom:0; width:min(520px, 92vw); background:#fffefb; border-left:3px solid #1d5c59; box-shadow:-8px 0 28px rgba(0,0,0,.18); z-index:9999; transform:translateX(102%); transition:transform .22s ease; display:flex; flex-direction:column; font:14.5px/1.65 "Microsoft YaHei",sans-serif; color:#1e292d; }}
    .ag-drawer.open {{ transform:translateX(0); }}
    .ag-drawer-head {{ padding:16px 20px; background:#173e42; color:#fff; display:flex; justify-content:space-between; align-items:flex-start; gap:12px; }}
    .ag-drawer-head h3 {{ margin:4px 0 0; font-size:18px; line-height:1.35; color:#fff; font-family:"Microsoft YaHei",sans-serif; }}
    .ag-drawer-badge {{ display:inline-block; font-size:11px; background:#2c5855; color:#d7f2ec; padding:2px 8px; border-radius:3px; font-weight:600; }}
    .ag-drawer-close {{ background:transparent; border:1px solid #6b9692; color:#fff; border-radius:4px; padding:4px 10px; cursor:pointer; font-size:13px; }}
    .ag-drawer-body {{ padding:18px 20px; overflow-y:auto; flex:1; }}
    .ag-drawer-body h4 {{ margin:14px 0 6px; font-size:14px; color:#1d5c59; border-bottom:1px solid #dce4df; padding-bottom:4px; }}
    .ag-drawer-body ul {{ margin:6px 0; padding-left:18px; }}
    .ag-drawer-body li {{ margin:4px 0; }}
    .ag-drawer-thumb {{ display:block; width:100%; max-height:290px; object-fit:contain; background:#f2f4f0; border:1px solid #d5ddd8; margin:10px 0; border-radius:4px; }}
    .ag-drawer-foot {{ padding:12px 20px; border-top:1px solid #d8e0db; background:#f4f6f2; display:flex; gap:10px; flex-wrap:wrap; justify-content:space-between; align-items:center; font-size:13px; }}
    .ag-drawer-btn {{ background:#1d5c59; color:#fff !important; text-decoration:none; padding:6px 12px; border-radius:4px; font-weight:600; display:inline-block; }}
    .ag-drawer-btn.secondary {{ background:#a3482d; }}
    @media print {{ .ag-drawer, .ag-drawer-backdrop {{ display:none !important; }} }}
  `;
  document.head.appendChild(style);

  const backdrop = document.createElement('div');
  backdrop.className = 'ag-drawer-backdrop';
  const drawer = document.createElement('aside');
  drawer.className = 'ag-drawer';
  drawer.setAttribute('aria-label', '证据速查抽屉');
  drawer.innerHTML = `
    <div class="ag-drawer-head">
      <div><span class="ag-drawer-badge" id="ag-d-cat">证据卡片</span><h3 id="ag-d-title"></h3></div>
      <button class="ag-drawer-close" id="ag-d-close" type="button">关闭 ✕</button>
    </div>
    <div class="ag-drawer-body" id="ag-d-body"></div>
    <div class="ag-drawer-foot" id="ag-d-foot"></div>
  `;
  document.body.appendChild(backdrop);
  document.body.appendChild(drawer);

  function closeDrawer() {{
    drawer.classList.remove('open');
    backdrop.classList.remove('open');
  }}
  backdrop.addEventListener('click', closeDrawer);
  drawer.querySelector('#ag-d-close').addEventListener('click', closeDrawer);
  document.addEventListener('keydown', e => {{ if (e.key === 'Escape') closeDrawer(); }});

  function rootPrefix() {{
    const p = location.pathname.replace(/\\\\/g, '/');
    if (/\\/(01_调研报告|02_招聘岗位资料|03_简历与候选人案例|04_面经与专业观点|06_项目分析与推荐)\\//.test(p)) {{
      return '../';
    }}
    return '';
  }}

  function esc(s) {{
    const d = document.createElement('div');
    d.textContent = s || '';
    return d.innerHTML;
  }}

  function openRecord(id, originalHref) {{
    const r = DB[id];
    if (!r) return false;
    const prefix = rootPrefix();
    drawer.querySelector('#ag-d-cat').textContent = `${{r.id}} · ${{r.cat || '证据'}} · ${{r.track || '通用'}}`;
    drawer.querySelector('#ag-d-title').textContent = r.title || r.id;

    let html = '';
    if (r.date || r.rec || r.company) {{
      html += `<p style="margin:0 0 10px;color:#5c6b68;font-size:13px">`;
      if (r.company) html += `<b>公司：</b>${{esc(r.company)}} · `;
      if (r.rec) html += `<b>类型：</b>${{esc(r.rec)}} · `;
      if (r.date) html += `<b>时间：</b>${{esc(r.date)}}`;
      html += `</p>`;
    }}
    if (r.outcome) {{
      html += `<p style="background:#fbf5e8;border-left:3px solid #a3482d;padding:7px 10px;margin:8px 0"><b>结果/档位：</b>${{esc(r.outcome)}}</p>`;
    }}
    if (r.thumb) {{
      const fileHref = prefix + r.file;
      html += `<a href="${{esc(fileHref)}}" target="_blank"><img class="ag-drawer-thumb" src="${{esc(prefix + r.thumb)}}" alt="${{esc(r.id)}}预览"></a>`;
    }}
    if (r.summary) {{
      html += `<h4>核心摘要</h4><p>${{esc(r.summary)}}</p>`;
    }}
    if (r.req && r.req.length) {{
      html += `<h4>明确要求（硬门槛）</h4><ul>` + r.req.map(x => `<li>${{esc(x)}}</li>`).join('') + `</ul>`;
    }}
    if (r.pref && r.pref.length) {{
      html += `<h4>优先/加分项</h4><ul>` + r.pref.map(x => `<li>${{esc(x)}}</li>`).join('') + `</ul>`;
    }}
    if (r.duties) {{
      html += `<h4>工作职责</h4><p>${{esc(r.duties)}}</p>`;
    }}
    if (r.questions && r.questions.length) {{
      html += `<h4>代表性追问 / 考察要点</h4><ul>` + r.questions.map(x => `<li>${{esc(x)}}</li>`).join('') + `</ul>`;
    }}
    if (r.strength) {{
      html += `<h4>可借鉴亮点</h4><p>${{esc(r.strength)}}</p>`;
    }}
    if (r.weakness) {{
      html += `<h4>样本边界与局限</h4><p>${{esc(r.weakness)}}</p>`;
    }}
    if (r.strengths && r.strengths.length) {{
      html += `<h4>值得学习的机制（后端:${{esc(r.b_lvl)}} / Agent:${{esc(r.a_lvl)}}）</h4><ul>` + r.strengths.map(x => `<li>${{esc(x)}}</li>`).join('') + `</ul>`;
    }}
    if (r.limits && r.limits.length) {{
      html += `<h4>静态核查短板（切勿照搬）</h4><ul>` + r.limits.map(x => `<li>${{esc(x)}}</li>`).join('') + `</ul>`;
    }}
    if (r.mods && r.mods.length) {{
      html += `<h4>关联模块 / 项目编号</h4><ul>` + r.mods.map(x => `<li><code>${{esc(x)}}</code></li>`).join('') + `</ul>`;
    }}
    drawer.querySelector('#ag-d-body').innerHTML = html;

    let foot = '';
    if (r.file) {{
      foot += `<a class="ag-drawer-btn secondary" href="${{esc(prefix + r.file)}}" target="_blank">打开脱敏简历附件 ↗</a>`;
    }}
    if (originalHref) {{
      foot += `<a class="ag-drawer-btn" href="${{esc(originalHref)}}">跳转至完整页面锚点 →</a>`;
    }}
    if (r.url && r.url.startsWith('http')) {{
      foot += `<a href="${{esc(r.url)}}" target="_blank" rel="noreferrer">原始外链 ↗</a>`;
    }}
    drawer.querySelector('#ag-d-foot').innerHTML = foot;

    backdrop.classList.add('open');
    drawer.classList.add('open');
    return true;
  }}

  document.addEventListener('click', e => {{
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const a = e.target.closest('a[href]');
    if (!a || a.closest('.ag-drawer')) return;
    const href = a.getAttribute('href') || '';
    const m = href.match(/#(JD\\d+|CV\\d+|OBS\\d+|INT\\d+|OP\\d+|PRO\\d+|CAP\\d+|DOC\\d+)$/);
    if (m && DB[m[1]]) {{
      // 如果目标锚点就在当前页面且不是证据详表跳转，也允许抽屉预览或滚屏
      const samePage = href.startsWith('#');
      if (!samePage) {{
        e.preventDefault();
        openRecord(m[1], href);
      }}
    }}
  }});
}})();
"""
    (BASE / 'argon_evidence_drawer.js').write_text(js_code, encoding='utf-8')


# ==============================================================================
# 4. 生成 4 本单文件可读 Markdown 合集 & 03 精选简历可读命名直达目录
# ==============================================================================
def build_compendiums_and_resume_shortcuts(rows, comp, visuals):
    by = {r['id']: r for r in rows}

    # (A) 03_简历与候选人案例/argon_精选简历直达/
    shortcut_dir = ROOT / '03_简历与候选人案例/argon_精选简历直达'
    shortcut_dir.mkdir(exist_ok=True)
    for old_f in shortcut_dir.iterdir():
        if old_f.is_file():
            old_f.unlink()
    readable_names = [
        ('CV30', 'argon_01_CV30_Agent与后端_字节CreatorAssistant实习简历.pdf'),
        ('CV31', 'argon_02_CV31_Agent工程_中科曙光实习与开源项目简历.pdf'),
        ('CV28', 'argon_03_CV28_后端开发_DavidHLP完整网页履历.html'),
        ('CV23', 'argon_04_CV23_后端开发_zhh2001完整网页履历.html'),
        ('CV24', 'argon_05_CV24_Agent工程_huomalxq双段实习完整简历.pdf'),
        ('CV01', 'argon_06_CV01_后端SSP_字节实习通知服务简历片段.png'),
        ('CV06', 'argon_07_CV06_后端开发_实习与开源经历简历片段.png'),
        ('OBS11', 'argon_08_OBS11_后端对照_一页式网盘与RPC简历图.png'),
        ('OBS05', 'argon_09_OBS05_算法对照_大模型训练研究简历.pdf'),
        ('OBS06', 'argon_10_OBS06_算法对照_强化学习与多模态简历.pdf'),
        ('OBS07', 'argon_11_OBS07_AI_Infra对照_推理加速与系统简历.pdf'),
    ]
    assets_by = {a['candidate_id']: a for a in visuals.get('assets', []) if a.get('candidate_id')}
    guide_lines = [
        '# 简历与候选人案例：目录导览与直达索引',
        '',
        '> **快速看真实简历**：为方便在资源管理器中直接打开脱敏 PDF、PNG 与网页版简历，已将 11 份视觉简历按 **`序号_编号_方向_标签`** 统一汇总至 [`argon_精选简历直达/`](argon_精选简历直达) 文件夹，同时你也可以打开可视化网页 [`argon_候选人与简历图册.html`](argon_候选人与简历图册.html) 按赛道筛选与对比。',
        '',
        '## 一、11 份含真实视觉附件的简历直达表',
        '',
        '| 编号 | 候选人方向与背景 | 可读直达文件（点击直接打开） | 图册锚点 |',
        '| :---: | :--- | :--- | :---: |'
    ]
    for cid, target_name in readable_names:
        asset = assets_by.get(cid)
        if not asset:
            continue
        src = ROOT / asset['local_file']
        dst = shortcut_dir / target_name
        if src.exists():
            if src.suffix.lower() == '.html':
                # 修正 HTML 履历被复制到子目录后的相对链接
                txt = src.read_text('utf-8-sig')
                dst.write_text(txt, encoding='utf-8')
            else:
                shutil.copy2(src, dst)
        r = by.get(cid, {})
        guide_lines.append(
            f'| **{cid}** | {r.get("title", cid)} | [`{target_name}`](argon_精选简历直达/{target_name}) | [图册卡片](argon_候选人与简历图册.html#{cid}) |'
        )
    guide_lines += [
        '',
        '## 二、本目录文件结构说明',
        '',
        '- [`argon_候选人与简历图册.html`](argon_候选人与简历图册.html)：**【首选入口】** 含 6 大简历改写模板 + 34 位核心候选人 + 4 份视觉对照交互图册。',
        '- [`argon_34位候选人案例合集.md`](argon_34位候选人案例合集.md)：将 `逐条分析底稿/` 下的 34 份零散 TXT 整合为单文件可读合集。',
        '- `argon_精选简历直达/`：按中文可读文件名整理好的 11 份 PDF / PNG / HTML 简历副本。',
        '- `核心Agent履历_脱敏副本/`、`核心后端履历_脱敏副本/`、`履历对照_脱敏副本/`、`简历视觉材料/`、`简历预览/`：底层原始归档路径（供图册与校验脚本引用）。',
        ''
    ]
    (ROOT / '03_简历与候选人案例/argon_README_简历目录导览.md').write_text('\n'.join(guide_lines), encoding='utf-8')

    # (B) 生成 4 本单文件 Markdown 合集，消除翻找 200 个小 TXT 的痛苦
    # 1. 02_招聘岗位资料/argon_33条JD全文与编码合集.md
    jds = sorted([r for r in rows if r['id'].startswith('JD')], key=lambda x: int(x['id'][2:]))
    jd_md = [
        '# 33 条招聘 JD 全文与要求分层合集',
        '',
        '> 本合集将 `逐条岗位资料/` 下的 33 个零散 TXT 卡片整合为单文件，按编号排序。可视化统计图表见 [`argon_岗位要求统计与解读.html`](argon_岗位要求统计与解读.html)。',
        '',
        '---',
        ''
    ]
    for j in jds:
        tax = j.get('taxonomy', {})
        jd_md += [
            f'## {j["id"]} · {j["title"]}（{j.get("company","")}｜{tax.get("track","")}）',
            f'- **原始链接**：[{j["url"]}]({j["url"]})（发布/窗口：{j.get("publish_date","未标")} · 纳入24份工程对比：`{"是" if j.get("matrix_include") else "否"}`）',
            f'- **明确要求**：{"；".join(clean_item(x) for x in j.get("required_stack", [])) or "未单列"}。',
            f'- **优先/加分**：{"；".join(clean_item(x) for x in j.get("preferred_stack", [])) or "未单列"}。',
            f'- **工作职责**：{clean_item(j.get("duties", "未单列"))}。',
            ''
        ]
    (ROOT / '02_招聘岗位资料/argon_33条JD全文与编码合集.md').write_text('\n'.join(jd_md), encoding='utf-8')

    # 2. 03_简历与候选人案例/argon_34位候选人案例合集.md
    cvs = sorted([r for r in rows if r['category'] == '候选人资料'], key=lambda x: int(x['id'][2:]))
    cv_md = [
        '# 34 位核心候选人案例全量合集',
        '',
        '> 本合集将 `逐条分析底稿/` 下的 34 个零散 TXT 卡片整合为单文件。带真实 PDF/PNG 简历预览与改写模板请打开 [`argon_候选人与简历图册.html`](argon_候选人与简历图册.html)。',
        '',
        '---',
        ''
    ]
    for c in cvs:
        tax = c.get('taxonomy', {})
        out = c.get('outcome', '') or '；'.join(f'{x.get("company","")}:{x.get("grade","")}/{x.get("status","")}' for x in c.get('outcomes', []))
        projs = '；'.join(p.get('name', '') if isinstance(p, dict) else str(p) for p in (c.get('projects') or []))
        cv_md += [
            f'## {c["id"]} · {c["title"]}（{tax.get("track","")}｜{tax.get("recruitment","")}）',
            f'- **来源链接**：[{c["url"]}]({c["url"]})（时间：{tax.get("experience_date_text","未知")}）',
            f'- **录用结果与档位**：{clean_item(out) or "未核"}。',
            f'- **本人项目**：{clean_item(projs or c.get("source_summary","")) or "见原文"}。',
            f'- **可借鉴亮点**：{clean_item(c.get("strengths") or c.get("recommendation") or "")}。',
            f'- **局限与边界**：{clean_item(c.get("weaknesses") or c.get("chain_gaps") or "")}。',
            ''
        ]
    (ROOT / '03_简历与候选人案例/argon_34位候选人案例合集.md').write_text('\n'.join(cv_md), encoding='utf-8')

    # 3. 04_面经与专业观点/argon_99份面经与18份观点合集.md
    ints = sorted([r for r in rows if r['id'].startswith('INT')], key=lambda x: int(x['id'][3:]))
    ops = sorted([r for r in rows if r['id'].startswith('OP')], key=lambda x: int(x['id'][2:]))
    int_md = [
        '# 99 份真实面经与 18 份专业技术观点全量合集',
        '',
        '> 本合集将 `逐条面经与观点/` 下的零散 TXT 卡片整合为单文件。按 10 大高频问题簇归类的精炼版与三步答题骨架见 [`argon_面经重点与项目追问.html`](argon_面经重点与项目追问.html)。',
        '',
        '---',
        '',
        '## 第一部分：99 份面经材料逐条汇总',
        ''
    ]
    for i in ints:
        tax = i.get('taxonomy', {})
        qs = i.get('questions') or i.get('project_questions') or i.get('key_questions') or []
        q_str = '；'.join(clean_item(x) for x in qs[:6] if clean_item(x)) if isinstance(qs, list) else clean_item(qs)
        int_md += [
            f'### {i["id"]} · {i["title"]}（{tax.get("track","")}｜{tax.get("experience_date_text","时间未标")}）',
            f'- **原文链接**：[{i["url"]}]({i["url"]})',
            f'- **核心提问与考察点**：{q_str or clean_item(i.get("source_summary",""))}。',
            ''
        ]
    int_md += ['---', '', '## 第二部分：18 份工业界专业观点汇总', '']
    for o in ops:
        int_md += [
            f'### {o["id"]} · {o["title"]}',
            f'- **原文链接**：[{o["url"]}]({o["url"]})',
            f'- **核心工程判断**：{clean_item(o.get("opinion") or o.get("source_summary") or "")}。',
            ''
        ]
    (ROOT / '04_面经与专业观点/argon_99份面经与18份观点合集.md').write_text('\n'.join(int_md), encoding='utf-8')

    # 4. 06_项目分析与推荐/argon_25个项目深度分析合集.md
    pro_md = [
        '# 25 个代码项目深度分析合集（长处 × 短板 × 精读路径）',
        '',
        '> 本合集将 `逐项分析底稿/` 下的 `PRO01.txt`–`PRO25.txt` 整合为单文件。交互筛选与免解压源码精读请打开 [`argon_项目比较与精读指南.html`](argon_项目比较与精读指南.html)。',
        '',
        '---',
        ''
    ]
    for pid in sorted(comp.keys(), key=lambda x: int(x[3:])):
        p = comp[pid]
        pro_md += [
            f'## {pid} · {p["title"]}',
            f'- **仓库链接**：[{p["source_URL"]}]({p["source_URL"]})',
            f'- **方向优先级**：后端 `{p["backend_priority"]["level"]}`（{clean_item(p["backend_priority"]["reason"])}）｜ Agent `{p["agent_priority"]["level"]}`（{clean_item(p["agent_priority"]["reason"])}）',
            '- **核心长处（值得学）**：',
            *[f'  - {clean_item(s)}。' for s in p.get('strengths', [])],
            '- **静态核查短板（切勿照搬）**：',
            *[f'  - {clean_item(l)}。' for l in p.get('limitations', [])],
            '- **推荐精读代码路径**：',
            *[f'  - `{m}`' for m in (p['backend_priority'].get('read_modules', []) + p['agent_priority'].get('read_modules', []))[:4]],
            ''
        ]
    (ROOT / '06_项目分析与推荐/argon_25个项目深度分析合集.md').write_text('\n'.join(pro_md), encoding='utf-8')


# ==============================================================================
# 5. 将新组件、源码精读面板、简历模板与答题骨架注入全站核心页面
# ==============================================================================
def upgrade_all_core_html_pages(snippets_by_pid, synthesis):
    # (A) 在 argon_项目比较与精读指南.html 的 8 个核心项目中嵌入免解压源码精读面板
    proj_html_path = ROOT / '06_项目分析与推荐/argon_项目比较与精读指南.html'
    if proj_html_path.exists():
        txt = proj_html_path.read_text('utf-8')
        extra_css = (
            '.flow-bar{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:10px 0;padding:10px 12px;background:#f2f6f4;border:1px solid #c9dad4;border-radius:4px}'
            '.flow-step{background:#fff;border:1px solid #9ab7af;padding:4px 9px;border-radius:4px;font-size:12.5px;line-height:1.4}'
            '.flow-step b{color:#a3482d;margin-right:4px}'
            '.flow-arrow{color:#1d5c59;font-weight:700}'
            '.code-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:10px 0}'
            '.code-card{border:1px solid #cbd6d1;border-radius:4px;overflow:hidden;background:#1e2629;color:#e6edf0;min-width:0}'
            '.code-head{background:#2b383c;padding:7px 11px;font-size:12px;border-bottom:1px solid #3c4d52;display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap}'
            '.code-head b{color:#fff}.code-head code{color:#9ad1c6;font-size:11px}'
            '.code-pre{margin:0;padding:10px 12px;font:11.5px/1.55 Consolas,"Courier New",monospace;overflow-x:auto;max-height:320px;white-space:pre}'
            'details.code-walkthrough{margin:12px 0;padding:12px 14px;background:#f8faf8;border:1px solid #ccd8d2;border-radius:4px}'
            'details.code-walkthrough>summary{cursor:pointer;font-weight:700;color:#1d5c59;font-size:14px}'
            '@media(max-width:900px){.code-grid{grid-template-columns:1fr}}'
        )
        if '.flow-bar{' not in txt:
            txt = txt.replace('</style>', extra_css + '</style>', 1)
        # 先移除已有重复面板以保证幂等
        txt = re.sub(r'<details class="code-walkthrough">.*?</details>', '', txt, flags=re.S)
        for pid in PROJECT_FLOWS_AND_SPECS:
            panel = render_code_panel_html(pid, snippets_by_pid)
            pattern = rf'(<article[^>]*\bid="{pid}"[^>]*>.*?)(<p class="note"><strong>归属与证据边界：)'
            txt = re.sub(pattern, lambda m: m.group(1) + panel + m.group(2), txt, count=1, flags=re.S)
        proj_html_path.write_text(txt, encoding='utf-8')

    # (B) 在 argon_面经重点与项目追问.html 中嵌入 10 大追问三步应答骨架 + 8 项目源码面板
    int_html_path = ROOT / '04_面经与专业观点/argon_面经重点与项目追问.html'
    if int_html_path.exists():
        txt = int_html_path.read_text('utf-8')
        extra_css = (
            '.ans-framework{margin:10px 0 4px;padding:12px 14px;background:#f4f8f6;border-left:4px solid #1d5c59;border-radius:3px}'
            '.ans-framework h4{margin:0 0 6px;font-size:14px;color:#1d5c59;font-family:"Microsoft YaHei",sans-serif}'
            '.ans-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;font-size:13px}'
            '.ans-step{background:#fff;border:1px solid #d4e0dc;padding:8px 10px;border-radius:3px}'
            '.ans-step b{display:block;color:#a3482d;margin-bottom:3px}'
            '@media(max-width:850px){.ans-steps{grid-template-columns:1fr}}'
        )
        if '.ans-framework{' not in txt:
            txt = txt.replace('</style>', extra_css + '</style>', 1)
        txt = re.sub(r'<div class="ans-framework">.*?</div></div></div>', '', txt, flags=re.S)
        for fid, fw in ANSWER_FRAMEWORKS.items():
            fw_html = (
                f'<div class="ans-framework"><h4>💡 面试官追问时的三步递进答题骨架（{E(fid)}）</h4>'
                f'<div class="ans-steps">'
                f'<div class="ans-step"><b>第一步：讲清约束与职责</b>{E(fw["step1"])}</div>'
                f'<div class="ans-step"><b>第二步：拆解并发/失败边界</b>{E(fw["step2"])}</div>'
                f'<div class="ans-step"><b>第三步：给出量化验证证据</b>{E(fw["step3"])}</div>'
                f'</div></div>'
            )
            pattern = rf'(<div class="qa-block" id="{fid}">.*?</div></div>)(</div>)'
            txt = re.sub(pattern, lambda m: m.group(1) + fw_html + m.group(2), txt, count=1, flags=re.S)
        int_html_path.write_text(txt, encoding='utf-8')

    # (C) 在 argon_候选人与简历图册.html 顶部增加【6大高频场景简历写法 Before/After 对照面板】与精选简历直达提示
    atlas_path = ROOT / '03_简历与候选人案例/argon_候选人与简历图册.html'
    if atlas_path.exists():
        txt = atlas_path.read_text('utf-8')
        tpl_cards = []
        for idx, item in enumerate(RESUME_TEMPLATES, 1):
            tpl_cards.append(
                f'<div class="entry" style="padding:14px 16px">'
                f'<div style="font-weight:700;color:#1d5c59;margin-bottom:6px">0{idx} · {E(item["category"])}</div>'
                f'<p style="margin:4px 0;font-size:12.5px;color:#8a3b24;background:#fbf2ee;padding:6px 8px;border-radius:3px"><b>❌ 平庸写法：</b>{E(item["bad"])}</p>'
                f'<p style="margin:6px 0;font-size:12.5px;color:#184a3b;background:#eef6f2;padding:6px 8px;border-radius:3px"><b>✅ 高分写法：</b>{E(item["good"])}</p>'
                f'<p style="margin:4px 0 0;font-size:11.5px;color:#5b6974"><b>要点：</b>{E(item["why"])}</p></div>'
            )
        tpl_sec = (
            '<details class="article-collection" id="resume-writing-guide" open>'
            '<summary>💡 抄作业专区：6 大高频场景【简历 Bullet 平庸写法 vs 大厂高分写法】对照表 <span>提炼自 CV01 / CV28 / CV30 / CV31</span></summary>'
            '<p class="intro">写简历切忌只罗列“用过 Redis / MQ / LangGraph”。请对照下方正反例，把你的项目改写为“业务约束 + 机制原语 + 异常兜底 + 验证指标”结构（资源管理器可直接打开 <a href="argon_README_简历目录导览.md"><b>argon_精选简历直达/</b></a> 下的中文命名简历）：</p>'
            f'<div class="grid" style="grid-template-columns:repeat(2,minmax(0,1fr))">{"".join(tpl_cards)}</div>'
            '</details>'
        )
        txt = re.sub(r'<details class="article-collection" id="resume-writing-guide".*?</details>', '', txt, flags=re.S)
        txt = txt.replace('<section class="toolbar"', tpl_sec + '<section class="toolbar"', 1)
        atlas_path.write_text(txt, encoding='utf-8')

    # (D) 在首站 argon_00_开始阅读.html 增加【6大备考专题一站式联动工作台】
    start_path = ROOT / 'argon_00_开始阅读.html'
    if start_path.exists():
        txt = start_path.read_text('utf-8')
        workbench_html = '''
<h2 id="workbench">二、六大备考专题一站式联动工作台（点击任意编号可在右侧直接滑出详情预览）</h2>
<p class="small">将分散在各目录的【JD要求 + 面经真题 + 标杆简历 + 精读项目 + 答题手册】按 6 个核心备考模块同屏聚合；点击任意蓝绿编号即可同页唤出右侧证据抽屉：</p>
<div class="two" style="margin-bottom:22px">
  <div class="box">
    <span class="pill core">后端专题 01</span>
    <h3>高并发缓存一致性与 Single-Flight</h3>
    <p class="small"><b>JD 门槛：</b><a href="01_调研报告/argon_资料检索与证据详表.html#JD01">JD01</a> <a href="01_调研报告/argon_资料检索与证据详表.html#JD20">JD20</a>（要求 Redis/分布式锁/限流）<br>
    <b>面经真题：</b><a href="01_调研报告/argon_资料检索与证据详表.html#INT24">INT24</a> <a href="01_调研报告/argon_资料检索与证据详表.html#INT101">INT101</a>（GEO/ZSet结构、缓存击穿与多实例边界）<br>
    <b>标杆简历与源码：</b><a href="03_简历与候选人案例/argon_候选人与简历图册.html#CV28">CV28</a> → <a href="06_项目分析与推荐/argon_项目比较与精读指南.html#PRO21">PRO21 ResiCache</a>（CompletableFuture单飞 + CAS刷新）<br>
    <b>直接抄模板：</b><a href="argon_实战备考手册_简历模板与答题骨架.html#resume-templates">简历模板01</a> · <a href="argon_实战备考手册_简历模板与答题骨架.html#fw-B2">B2三步答题骨架</a></p>
  </div>
  <div class="box">
    <span class="pill core">后端专题 02</span>
    <h3>异步消息可靠性、幂等与事务外盒 (Outbox)</h3>
    <p class="small"><b>JD 门槛：</b><a href="01_调研报告/argon_资料检索与证据详表.html#JD06">JD06</a> <a href="01_调研报告/argon_资料检索与证据详表.html#JD20">JD20</a>（MQ可靠投递、削峰与幂等）<br>
    <b>面经真题：</b><a href="01_调研报告/argon_资料检索与证据详表.html#INT66">INT66</a> <a href="01_调研报告/argon_资料检索与证据详表.html#INT85">INT85</a>（重复消费、超时取消补偿与死信隔离）<br>
    <b>标杆简历与源码：</b><a href="03_简历与候选人案例/argon_候选人与简历图册.html#CV21">CV21</a> → <a href="06_项目分析与推荐/argon_项目比较与精读指南.html#PRO19">PRO19 SchoolBus</a> · <a href="06_项目分析与推荐/argon_项目比较与精读指南.html#PRO20">PRO20 UltiCode</a><br>
    <b>直接抄模板：</b><a href="argon_实战备考手册_简历模板与答题骨架.html#resume-templates">简历模板02</a> · <a href="argon_实战备考手册_简历模板与答题骨架.html#fw-B3">B3三步答题骨架</a></p>
  </div>
  <div class="box">
    <span class="pill core">后端专题 03</span>
    <h3>数据库索引、慢查询优化与网关开源协作</h3>
    <p class="small"><b>JD 门槛：</b><a href="01_调研报告/argon_资料检索与证据详表.html#JD02">JD02</a> <a href="01_调研报告/argon_资料检索与证据详表.html#JD05">JD05</a>（MySQL优化、RPC与高可用架构）<br>
    <b>面经真题：</b><a href="01_调研报告/argon_资料检索与证据详表.html#INT20">INT20</a> <a href="01_调研报告/argon_资料检索与证据详表.html#INT86">INT86</a>（SELECT *回表、B+树高度估算、线上排障）<br>
    <b>标杆简历与源码：</b><a href="03_简历与候选人案例/argon_候选人与简历图册.html#CV01">CV01</a> <a href="03_简历与候选人案例/argon_候选人与简历图册.html#CV05">CV05</a> → <a href="06_项目分析与推荐/argon_项目比较与精读指南.html#PRO09">PRO09 ShenYu</a><br>
    <b>直接抄模板：</b><a href="argon_实战备考手册_简历模板与答题骨架.html#resume-templates">简历模板03</a> · <a href="argon_实战备考手册_简历模板与答题骨架.html#fw-B5">B5排障答题骨架</a></p>
  </div>
  <div class="box">
    <span class="pill core">Agent 专题 04</span>
    <h3>多步状态图编排、Checkpoint 恢复与预算控制</h3>
    <p class="small"><b>JD 门槛：</b><a href="01_调研报告/argon_资料检索与证据详表.html#JD14">JD14</a> <a href="01_调研报告/argon_资料检索与证据详表.html#JD23">JD23</a> <a href="01_调研报告/argon_资料检索与证据详表.html#JD27">JD27</a>（多步规划、状态机与异常恢复）<br>
    <b>面经真题：</b><a href="01_调研报告/argon_资料检索与证据详表.html#INT41">INT41</a> <a href="01_调研报告/argon_资料检索与证据详表.html#INT84">INT84</a>（任务中断续跑、路径震荡与Token硬预算）<br>
    <b>标杆简历与源码：</b><a href="03_简历与候选人案例/argon_候选人与简历图册.html#CV31">CV31</a> → <a href="06_项目分析与推荐/argon_项目比较与精读指南.html#PRO04">PRO04 Ragent</a> · <a href="06_项目分析与推荐/argon_项目比较与精读指南.html#PRO24">PRO24 Sprout</a><br>
    <b>直接抄模板：</b><a href="argon_实战备考手册_简历模板与答题骨架.html#resume-templates">简历模板04</a> · <a href="argon_实战备考手册_简历模板与答题骨架.html#fw-A1">A1/A3答题骨架</a></p>
  </div>
  <div class="box">
    <span class="pill core">Agent 专题 05</span>
    <h3>工具协议 (MCP/Function Call)、权限审批与沙箱隔离</h3>
    <p class="small"><b>JD 门槛：</b><a href="01_调研报告/argon_资料检索与证据详表.html#JD11">JD11</a> <a href="01_调研报告/argon_资料检索与证据详表.html#JD24">JD24</a> <a href="01_调研报告/argon_资料检索与证据详表.html#JD26">JD26</a>（Tool/MCP接入、容器与安全隔离）<br>
    <b>面经真题：</b><a href="01_调研报告/argon_资料检索与证据详表.html#INT03">INT03</a> <a href="01_调研报告/argon_资料检索与证据详表.html#INT47">INT47</a> <a href="01_调研报告/argon_资料检索与证据详表.html#INT102">INT102</a>（写操作边界、沙箱快照回滚、多Agent写冲突）<br>
    <b>标杆简历与源码：</b><a href="03_简历与候选人案例/argon_候选人与简历图册.html#CV30">CV30</a> <a href="03_简历与候选人案例/argon_候选人与简历图册.html#CV31">CV31</a> → <a href="06_项目分析与推荐/argon_项目比较与精读指南.html#PRO25">PRO25 NoWorries</a><br>
    <b>直接抄模板：</b><a href="argon_实战备考手册_简历模板与答题骨架.html#resume-templates">简历模板05</a> · <a href="argon_实战备考手册_简历模板与答题骨架.html#fw-A4">A4三步答题骨架</a></p>
  </div>
  <div class="box">
    <span class="pill core">Agent 专题 06</span>
    <h3>RAG 混合召回重排与留出集回归评测闭环</h3>
    <p class="small"><b>JD 门槛：</b><a href="01_调研报告/argon_资料检索与证据详表.html#JD09">JD09</a> <a href="01_调研报告/argon_资料检索与证据详表.html#JD12">JD12</a> <a href="01_调研报告/argon_资料检索与证据详表.html#JD24">JD24</a>（RAG召回重排、评测集与成功率指标）<br>
    <b>面经真题：</b><a href="01_调研报告/argon_资料检索与证据详表.html#INT42">INT42</a> <a href="01_调研报告/argon_资料检索与证据详表.html#OP09">OP09</a> <a href="01_调研报告/argon_资料检索与证据详表.html#OP16">OP16</a>（分块粒度、Rerank、单题退化与LLM裁判偏见）<br>
    <b>标杆简历与源码：</b><a href="03_简历与候选人案例/argon_候选人与简历图册.html#CV30">CV30</a> <a href="03_简历与候选人案例/argon_候选人与简历图册.html#CV33">CV33</a> → <a href="06_项目分析与推荐/argon_项目比较与精读指南.html#PRO06">PRO06 open_deep_research</a><br>
    <b>直接抄模板：</b><a href="argon_实战备考手册_简历模板与答题骨架.html#resume-templates">简历模板06</a> · <a href="argon_实战备考手册_简历模板与答题骨架.html#fw-A2">A2/A5答题骨架</a></p>
  </div>
</div>
'''
        txt = re.sub(r'<h2 id="workbench">.*?</div>\s*</div>', '', txt, flags=re.S)
        txt = txt.replace('<h2>二、六大专题阅读入口（按需点击进入）</h2>', workbench_html + '<h2>三、七大专题阅读入口（按需点击进入）</h2>', 1)
        if 'argon_实战备考手册_简历模板与答题骨架.html' not in txt:
            txt = txt.replace(
                '<div class="two"><div class="box">',
                '<div class="two"><div class="box" style="border-top-color:#a3482d;background:#fff8f4"><span class="pill warn">新增实战手册 · 强烈推荐</span><h3><a href="argon_实战备考手册_简历模板与答题骨架.html">00 · 实战备考手册：简历模板 × 答题骨架 × 源码走读</a></h3><p>直接提供 6 组简历 Bullet 正反例改写模板、10 大高频追问三步答题公式与 8 个核心项目免解压源码走读。</p></div><div class="box">',
                1
            )
        start_path.write_text(txt, encoding='utf-8')

    # (E) 为所有核心 HTML 页面注入顶栏的【实战备考手册】入口与底部 argon_evidence_drawer.js 脚本
    core_htmls = [
        ROOT / 'argon_00_开始阅读.html',
        ROOT / 'argon_实战备考手册_简历模板与答题骨架.html',
        ROOT / '01_调研报告/argon_实习求职调研总报告.html',
        ROOT / '01_调研报告/argon_index.html',
        ROOT / '01_调研报告/argon_资料检索与证据详表.html',
        ROOT / '01_调研报告/argon_待手动访问链接.html',
        ROOT / '02_招聘岗位资料/argon_岗位要求统计与解读.html',
        ROOT / '03_简历与候选人案例/argon_候选人与简历图册.html',
        ROOT / '04_面经与专业观点/argon_面经重点与项目追问.html',
        ROOT / '06_项目分析与推荐/argon_项目比较与精读指南.html',
    ]
    for hp in core_htmls:
        if not hp.exists():
            continue
        txt = hp.read_text('utf-8')
        rel_js = Path(os.path.relpath(BASE / 'argon_evidence_drawer.js', hp.parent)).as_posix()
        rel_hb = Path(os.path.relpath(ROOT / 'argon_实战备考手册_简历模板与答题骨架.html', hp.parent)).as_posix()
        # 顶栏补充“实战备考手册”链接
        if '实战备考手册</a>' not in txt and '<nav class="top-links"' in txt:
            active_cls = ' class="active"' if hp.name == 'argon_实战备考手册_简历模板与答题骨架.html' else ''
            txt = re.sub(
                r'(<nav class="top-links"[^>]*>.*?开始阅读</a>)',
                lambda m: m.group(1) + f'<a{active_cls} href="{E(rel_hb)}">实战备考手册</a>',
                txt,
                count=1
            )
        # 注入抽屉脚本
        script_tag = f'<script src="{E(rel_js)}"></script>'
        txt = re.sub(r'<script src="[^"]*argon_evidence_drawer\.js"></script>', '', txt)
        txt = txt.replace('</body>', script_tag + '</body>', 1)
        hp.write_text(txt, encoding='utf-8')


# ==============================================================================
# 6. 收敛 08_证据索引与统计 下的 200+ 个未被引用的历史过程快照与旧脚本
# ==============================================================================
def tidy_08_directory():
    archive_sub = BASE / 'argon_历轮过程快照与旧脚本归档'
    archive_sub.mkdir(exist_ok=True)

    # 收集全站所有 HTML / MD / 活跃脚本中引用到的 08_证据索引与统计 文件名
    referenced = {
        'all_evidence_records.json',
        '需求覆盖统计.json',
        'argon_岗位统计_可读版.json',
        '技术要求_明确要求与加分项.json',
        '面经项目_阅读结论.json',
        '简历视觉材料_整理清单.json',
        '项目统一比较与阅读优先级.json',
        '两方向阅读顺序.json',
        '能力要求四类证据对照.json',
        '能力要求四类证据对照.csv',
        '专业观点交叉核对_来源与比较.json',
        '待手动访问链接.json',
        '已解决访问线索.json',
        '全部资料统一分类.csv',
        '面经主题索引.csv',
        '履历脱敏副本目录.json',
        '可读性整理_路径映射.json',
        '可读性整理_链接修复.json',
        'astra来源_合并前文件指纹.json',
        'astra合并_JD核对.json',
        '简历视觉材料_OCR.ps1',
        'argon_evidence_drawer.js',
    }
    for p in ROOT.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in ['.html', '.md', '.py', '.cjs', '.json']:
            continue
        if archive_sub in p.parents:
            continue
        # 只扫描 HTML/MD 以及活跃的 argon_ 脚本和 05 清单
        if p.suffix.lower() in ['.html', '.md'] or p.name.startswith('argon_') or p.parent.name == '05_项目源码归档':
            content = p.read_text('utf-8-sig', errors='ignore')
            for f in BASE.iterdir():
                if f.is_file() and f.name in content:
                    referenced.add(f.name)

    moved_count = 0
    for f in list(BASE.iterdir()):
        if not f.is_file():
            continue
        if f.name.startswith('argon_') or f.name in referenced:
            continue
        target = archive_sub / f.name
        if target.exists():
            target.unlink()
        f.rename(target)
        moved_count += 1

    # 在 08_证据索引与统计 下生成一份清晰的 README 导览
    readme_08 = [
        '# 08_证据索引与统计：权威主数据与构建脚本说明',
        '',
        '> **目录整理说明**：为消除原先 280+ 个多轮采集临时快照平铺造成的视觉干扰，所有未被引用的单轮过程快照、临时校验回执与旧轮次脚本已统一归档至 [`argon_历轮过程快照与旧脚本归档/`](argon_历轮过程快照与旧脚本归档)，本顶层目录仅保留**权威主数据库、汇总 CSV 与当前活跃的 `argon_` 生成/校验脚本**。',
        '',
        '## 一、核心权威数据文件',
        '- [`all_evidence_records.json`](all_evidence_records.json)：全库 **239 条**逻辑证据主数据库（唯一事实源）。',
        '- [`全部资料统一分类.csv`](全部资料统一分类.csv)：239 条证据的表格化全量索引（可用 Excel 直接打开）。',
        '- [`能力要求四类证据对照.csv`](能力要求四类证据对照.csv) / [`.json`](能力要求四类证据对照.json)：11 项核心能力在 JD、履历、面经、项目四类证据上的映射表。',
        '- [`argon_岗位统计_可读版.json`](argon_岗位统计_可读版.json)：24 份可比工程 JD 的五层语义编码与公司等权敏感性统计。',
        '- [`面经项目_阅读结论.json`](面经项目_阅读结论.json)：99 份面经提炼的 10 大追问簇与 8 个重点项目核查结论。',
        '- [`项目统一比较与阅读优先级.json`](项目统一比较与阅读优先级.json)：25 个代码项目的 375 维对比矩阵。',
        '- [`简历视觉材料_整理清单.json`](简历视觉材料_整理清单.json)：脱敏 PDF / PNG / 网页履历的 SHA256 与预览图清单。',
        '',
        '## 二、活跃生成与校验脚本（均带 `argon_` 前缀）',
        '- [`argon_生成可读调研总报告.py`](argon_生成可读调研总报告.py)：生成核心总报告、面经页、项目比较页与 5 份配套 Markdown。',
        '- [`argon_生成岗位统计_可读版.py`](argon_生成岗位统计_可读版.py)：生成 JD 五层统计 HTML、SVG 图表、Markdown 与 CSV。',
        '- [`argon_整理简历视觉材料.py`](argon_整理简历视觉材料.py)：构建候选人与简历视觉图册 HTML。',
        '- [`argon_深度升级与结构整理.py`](argon_深度升级与结构整理.py)：提取 8 大项目源码片段、生成实战备考手册、构建全站右侧证据抽屉 `argon_evidence_drawer.js` 并收敛目录结构。',
        '- [`argon_导出重点报告.cjs`](argon_导出重点报告.cjs)：调用本机 Edge 无头浏览器导出 8 页 A4 PDF 并校验移动端/桌面端渲染。',
        '- [`argon_校验可读性整理.py`](argon_校验可读性整理.py)：校验全站所有 HTML/Markdown 本地链接、锚点、PDF 页数与主数据完整性。',
        ''
    ]
    (BASE / 'argon_README_数据与脚本索引.md').write_text('\n'.join(readme_08), encoding='utf-8')
    return moved_count


def main():
    rows = load_json(BASE / 'all_evidence_records.json')
    comp = load_json(BASE / '项目统一比较与阅读优先级.json')['projects']
    comp_by = {p['id']: p for p in comp}
    visuals = load_json(BASE / '简历视觉材料_整理清单.json')
    synthesis = load_json(BASE / '面经项目_阅读结论.json')

    snippets_by_pid = extract_zip_snippets()
    build_handbook_pages(snippets_by_pid, synthesis, comp_by)
    build_evidence_drawer_js(rows, comp_by, visuals, synthesis)
    build_compendiums_and_resume_shortcuts(rows, comp_by, visuals)
    upgrade_all_core_html_pages(snippets_by_pid, synthesis)
    moved = tidy_08_directory()
    print(json.dumps({
        'extracted_code_projects': len(snippets_by_pid),
        'resume_templates': len(RESUME_TEMPLATES),
        'answer_frameworks': len(ANSWER_FRAMEWORKS),
        'archived_08_scratch_files': moved
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
