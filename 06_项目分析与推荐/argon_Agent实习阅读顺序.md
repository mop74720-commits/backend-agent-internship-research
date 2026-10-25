# Agent 工程实习：分级阅读与源码精读清单

> **核心原则**：先看字节/中科曙光等真实 Agent 实习履历（CV30、CV31）与近期 Agent 面经，重点掌握“状态图编排、RAG 召回重排、工具约束与回归评测”，再对照精读 Spring AI Alibaba、open_deep_research、Sprout 与 NoWorries。
> - **配套可视化页面**：[项目比较与精读指南.html](argon_项目比较与精读指南.html) · [面经重点与项目追问.html](../04_面经与专业观点/argon_面经重点与项目追问.html) · [候选人与简历图册.html](../03_简历与候选人案例/argon_候选人与简历图册.html)

---

## 一、项目源码分级精读清单（先读机制与缺陷，切勿整仓照搬）

### 精读 · 执行与权限

#### [PRO12 · OpenManus：紧凑 Agent循环、工具调用与沙箱边界对照](argon_项目比较与精读指南.html#PRO12)（精读｜[原仓库](https://github.com/FoundationAgents/OpenManus)）
- **为什么读**：范围较紧凑，先读完整工具循环，再对照AgentScope的权限/中断与评测缺口。
- **避坑提示**：is_stuck 依据相同 assistant 文本计数，处理方式是追加改变策略的提示；它不证明任务取得进展，也不保证成本收敛或业务正确。
- **推荐精读模块**：
  - `app/agent/base.py`
  - `app/agent/toolcall.py`
  - `app/sandbox/core/sandbox.py`
  - `tests/sandbox/test_sandbox.py`

#### [PRO11 · AgentScope：工具权限、状态与中断测试的工程参考](argon_项目比较与精读指南.html#PRO11)（精读｜[原仓库](https://github.com/agentscope-ai/agentscope)）
- **为什么读**：优先读权限引擎和中断测试，学会把机制保证与业务授权/任务成功分开。
- **避坑提示**：当前主线规模较大，SOP、语音、团队、服务、渠道和多种 workspace 会提高学习成本；README 部分功能明确标为 Experimental。
- **推荐精读模块**：
  - `src/agentscope/permission/_engine.py`
  - `src/agentscope/agent/_agent.py`
  - `src/agentscope/state/_state.py`
  - `tests/permission_engine_test.py`

### 精读 · 评测与证据

#### [PRO06 · Open Deep Research：研究编排与评测参考](argon_项目比较与精读指南.html#PRO06)（精读｜[原仓库](https://github.com/langchain-ai/open_deep_research)）
- **为什么读**：优先看评测器与基线配置，再沿研究循环回看质量来源；适合补评测短板。
- **避坑提示**：仅生成漂亮报告难以验证任务成功。
- **推荐精读模块**：
  - `src/open_deep_research/deep_researcher.py`
  - `tests/evaluators.py`
  - `tests/run_evaluate.py`
  - `tests/pairwise_evaluation.py`

### 精读 · 按语言与领域

- **Java方向**：
  - **[PRO04 · Ragent：Java Agent与RAG全链路参考](argon_项目比较与精读指南.html#PRO04)**（[原仓库](https://github.com/nageoffer/ragent)）：Java方向重点比较Workflow/Agent、状态与拒绝处理，先确认边界再看功能。精读入口：`agent/src/main/java/com/nageoffer/ai/ragent/agent/confirm/AgentConfirmDenialMiddleware.java`；`agent/src/main/java/com/nageoffer/ai/ragent/agent/dao/mapper/AgentStateMapper.java`；`agent/src/main/java/com/nageoffer/ai/ragent/agent/config/AgentEngineConfiguration.java`
- **RAG方向**：
  - **[PRO07 · RAGFlow：文档解析与检索工程参考](argon_项目比较与精读指南.html#PRO07)**（[原仓库](https://github.com/infiniflow/ragflow)）：RAG方向先读召回诊断与SDK，分清检索质量、生成质量、HTTP性能三者。精读入口：`docs/guides/dataset/retrieval_testing.md`；`example/sdk/retrieval_example.py`；`test/benchmark/README.md`

### 选读 · 进阶

#### [PRO05 · DeerFlow：长任务运行与隔离参考](argon_项目比较与精读指南.html#PRO05)（选读｜[原仓库](https://github.com/bytedance/deer-flow)）
- **为什么读**：先读检查点恢复契约和鉴权，再按需要读运行系统；平台范围较大。
- **避坑提示**：系统庞大，读完或部署成功不等于个人实现。
- **推荐精读模块**：
  - `backend/app/gateway/auth_middleware.py`
  - `backend/app/gateway/checkpoint_retention.py`
  - `backend/docs/checkpoint-retention-contract.md`
  - `backend/tests/test_checkpoint_retention_contract.py`

### 选读 · 补基础

#### [PRO13 · Hello-Agents：评测方法与教材代码参考，整库不归档](argon_项目比较与精读指南.html#PRO13)（选读｜[原仓库](https://github.com/datawhalechina/hello-agents)）
- **为什么读**：先补第十二章评价方法，分清示例、预期输出和实际基准；按缺口读章节。
- **避坑提示**：这是课程与共创仓库，不是一个统一部署／统一测试的成品系统；不能把不同作者项目的功能合并声称成一个已经验证的平台。
- **推荐精读模块**：
  - `LICENSE.txt`
  - `code/chapter12/README.md`
  - `code/chapter12/03_bfcl_custom_evaluation.py`
  - `code/chapter12/04_run_bfcl_evaluation.py`

#### [PRO10 · Casdoor：从候选人开源条目拆读身份与权限工程](argon_项目比较与精读指南.html#PRO10)（选读｜[原仓库](https://github.com/casdoor/casdoor)）
- **为什么读**：仅作工具背后业务授权的配套材料，不列为已核Agent求职项目。
- **避坑提示**：认证平台的协议和身份提供商范围很大；全面重做会分散时间，接入 SDK 本身也不能证明理解认证与授权。
- **推荐精读模块**：
  - `object/permission_enforcer.go`
  - `object/permission_enforcer_test.go`
  - `object/token_jwt_key.go`
  - `object/token_jwt_key_test.go`

#### [PRO18 · Crony：Go分布式定时任务工程参考，未证作者SSP](argon_项目比较与精读指南.html#PRO18)（选读｜[原仓库](https://github.com/tmnhs/Crony/tree/00df3df90306811332d0aff66a259cf90ad6954f)）
- **为什么读**：仅作为Agent长任务调度/重试的后端参照；本身不是Agent或SSP成功者项目。
- **避坑提示**：不是 SSP 成功案例、正式完整简历或 Agent 工程；不能用于补齐这些证据缺口。
- **推荐精读模块**：
  - `README.md`
  - `go.mod`
  - `common/pkg/etcdclient/registry.go`
  - `admin/internal/service/node.go`

### 待核

- 目前没有已核近期Agent正式SSP+本人项目+本人面经的完整关系。优先补这些关系，不用教材/平台填补成功者证据。

### 待核 · 状态与隔离风险对照

#### [PRO23 · QuantHarbor：多Agent状态与执行隔离风险对照](argon_项目比较与精读指南.html#PRO23)（待核｜[原仓库](https://github.com/shufengc/QuantHarbor/tree/f0d6380e9846f84f10be5f284fec40d42cfb34f9)）
- **为什么读**：适合研究状态/工具与权限边界的反例；不作为成熟成品推荐。
- **避坑提示**：所谓sandbox没有在核读文件中建立进程/文件系统/网络权限隔离；不能据此称安全执行沙箱。
- **推荐精读模块**：
  - `src/agents/base_agent.py`
  - `src/utils/code_executor_async.py`
  - `src_rag/core/report_pipeline.py`

### 选读 · 本人Agent实现与风险

#### [PRO24 · Sprout：任务树编排、预算与文本打分边界](argon_项目比较与精读指南.html#PRO24)（选读｜[原仓库](https://github.com/hlbbbbbbb/sprout/tree/3ecd36e5a4eac42ae90be854e415857fd0f3cf7c)）
- **为什么读**：研究机制与失败路径；未验证为成熟可直接复用的成品。
- **避坑提示**：benchmark文本特征分不代表功能正确；未复现任何模型效果。
- **推荐精读模块**：
  - `sprout/task_tree.py`
  - `sprout/worker.py`
  - `sprout/llm.py`
  - `examples/benchmark.py`
  - `tests/test_task_tree.py`

#### [PRO25 · NoWorries：桌面记忆与跨平台隔离风险选读](argon_项目比较与精读指南.html#PRO25)（选读｜[原仓库](https://github.com/hlbbbbbbb/No-worries/tree/c811e697bb48a979ee14bd932de80057b98b464f)）
- **为什么读**：研究机制与失败路径；未验证为成熟可直接复用的成品。
- **避坑提示**：Windows/Linux环境重定向不是系统级隔离；macOS回退可能重复执行并降低隔离。
- **推荐精读模块**：
  - `noworries_app/apps/desktop/src/main/sandbox/macos-sandbox.ts`
  - `noworries_app/apps/desktop/src/main/sandbox/windows-sandbox.ts`
  - `noworries_app/apps/desktop/src/main/sandbox/workspace-manager.ts`
  - `noworries_app/apps/desktop/src/main/clawdbot/memory/episode-memory.ts`
  - `noworries_app/apps/desktop/src/main/clawdbot/memory/memory-consolidation.ts`

---

## 二、对标候选人案例（共 9 位，按证据形态分级）

> **阅读提示**：CV31近期中科曙光Agent实习有完整CV和本人源码直链；框架继承、模块风险、本人面经及SSP缺口另列。CV30为互联网大厂内部Agent履历，无公开内部源码。

### 1. 含公开脱敏简历 / 网页履历的标杆案例（优先对标，共 3 位）

- **[CV31 · 黄一航：中科曙光Agent实习完整履历与本人项目](../03_简历与候选人案例/argon_候选人与简历图册.html#CV31)**（[原始来源](https://imyihang.com/)）：结果：本人CV明确Agent开发实习经历；SSP/SP未披露 ｜ 看点：精读CV职责与本人代码关系；按项目机制及静态风险选读，独立核评测与贡献
- **[CV30 · Andrew Wang：字节后端与Agent实习完整专业履历](../03_简历与候选人案例/argon_候选人与简历图册.html#CV30)**（[原始来源](https://andrewtheterp.com/)）：结果：两段大厂实习经历自述；SSP/SP档位未披露 ｜ 看点：精读实习职责及工程机制；公开源码、课程框架、内部项目分别核对，不推导录用因果
- **[CV24 · 林祥庆 / Huoma LXQ：近期实习完整公开履历脱敏副本](../03_简历与候选人案例/argon_候选人与简历图册.html#CV24)**（[原始来源](https://huomalxq.github.io/resume/)）：结果：本人完整履历明确实习公司、岗位和起止时间；档位未披露 ｜ 看点：硕士公开完整单页CV，近期Philips Agent应用工程实习对应LangGraph问数链路，职责具体到表结构检索、SQL校验与重试、耗时测试；履历指标为自述。Philips为跨国企业，不将其写成中国互联网大…

### 2. 求职经历与面经复盘案例（补充对标，共 6 位）

- **[CV07 · 等闲king：2025后端实习offer与本人Agent项目深挖](../03_简历与候选人案例/argon_候选人与简历图册.html#CV07)**（[原始来源](https://www.nowcoder.com/feed/main/detail/a3e209dc72154cb586a65a2d60fc5c3d)）：结果：本人年终总结明确2025小红书、快手后端实习offer；无SSP，Agent具体经历时间另核 ｜ 看点：辅助观察，不作为核心录用证据
- **[CV25 · 2026暑期：蚂蚁AlipayPlus智能体应用offer、TikTok后端OC及本人面经](../03_简历与候选人案例/argon_候选人与简历图册.html#CV25)**（[原始来源](https://ac.nowcoder.com/discuss/1610772)）：结果：蚂蚁集团 已收到offer自述；字节跳动 OC，称offer报审批；字节跳动 已在实习3个多月自述 ｜ 看点：Agent/后端实习的近期成功自述可选读；它补的是公司、岗位、事件年与结果，项目实现证据仍弱
- **[CV26 · 金蝶/讯飞Agent实习经历、360实习offer与多家公司项目深挖](../03_简历与候选人案例/argon_候选人与简历图册.html#CV26)**（[原始来源](https://www.nowcoder.com/feed/main/detail/202664206f23428ebea5d513ea261c9d?sourceSSR=subject)）：结果：360 收到offer自述；名创优品 后续汇总列为手上实习机会；九号公司 单篇OC；后续汇总称已拒绝；深信服 两轮后收到感谢信自述；小红书/百度 一面失败自述 ｜ 看点：Agent项目追问优先精读，特别是宕机恢复重复提单、工具检索、错误经验污染、权限与效果证明；成功录用和具体问题的公司仍逐条区别
- **[CV08 · 商汤大模型算法应用实习面经（已offer）](../03_简历与候选人案例/argon_候选人与简历图册.html#CV08)**（[原始来源](https://www.nowcoder.com/feed/main/detail/2762070c2c52472da06bf9ee59518d79)）：结果：标题自述已offer，未提SSP ｜ 看点：推荐作为Agent工程验收反推题库；勿当完整成功简历复制
- **[CV09 · 27双非本：腾讯IEG游戏安全后台实习面经](../03_简历与候选人案例/argon_候选人与简历图册.html#CV09)**（[原始来源](https://www.nowcoder.com/feed/main/detail/9ecd5997a7d74f3fa885695032f32065?sourceSSR=dynamic&weFlow=true)）：结果：本人时间线记载Offer；没有SSP信息 ｜ 看点：优先用来验证广度与深度的组合；与纯Agent岗位分列
- **[CV33 · 非科班转码：211化学本→985材料硕→字节后端开发](../03_简历与候选人案例/argon_候选人与简历图册.html#CV33)**（[原始来源](https://ac.nowcoder.com/discuss/1626909?channel=-1&source_id=discuss_terminal_discuss_hot_nctrack&type=0)）：结果：明确2026实习；字节财经未披露档位offer自述，TT失败分开 ｜ 看点：最贴近“后端＋AI”组合的近期样本：传统一致性和Agent问题出现在同一后端面试中

---

## 三、精选面经阅读顺序（共 20 份，按时效与代表性分级）

### 1. 严格近期（2025–2026）工程实习面经（必读，共 0 份）


### 2. 高价值专项追问与经典实习面经（选读，共 20 份）

- **[INT42 · 26.4百度大模型生态集成实习，新鲜面经~](https://www.nowcoder.com/feed/main/detail/62d4ca9866d84d63bf6eafbb0a947bb8?sourceSSR=search)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT42) · 实习/年份已核）：考察主题：编程语言/并发、Agent循环/工具、AI编码、RAG/检索、系统设计/取舍。
- **[INT47 · 小红书大模型平台 Agentic 全栈研发练习生 一面凉经](https://www.nowcoder.com/feed/main/detail/e5e9311a623940eead6ec98c65e7f9e8?sourceSSR=search)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT47) · 实习/年份已核）：考察主题：项目深挖/个人贡献、Agent循环/工具、安全/权限、记忆/上下文、系统设计/取舍。
- **[INT74 · MINISO名创优品Agent开发实习一面](https://www.nowcoder.com/feed/main/detail/f844a4ac20be44bc9b3f756bd0ebb84c?sourceSSR=subject)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT74) · 实习/年份未标）：考察主题：checkpoint与幂等、技能版本与回归、上下文压缩、权限边界。
- **[INT72 · 深信服Agent开发实习生一面二面](https://www.nowcoder.com/feed/main/detail/14b2c379ae434062a009aefea9fc5df9?sourceSSR=subject)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT72) · 实习/年份未标）：考察主题：工具注册/发现、业务闭环、评测、个人贡献。
- **[INT73 · 九号公司Agent开发实习一面，1h30m](https://www.nowcoder.com/feed/main/detail/c0b53fdd38e041d2bc779753d04ee2ce?sourceSSR=subject)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT73) · 实习/年份未标）：考察主题：状态数据流、OCR错误恢复、指标与badcase、工具分层。
- **[INT75 · 小红书Agent开发实习生一面凉经，附百度Agent凉经](https://www.nowcoder.com/feed/main/detail/e319aadc79a9479397a6661a7f5ca088?sourceSSR=subject)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT75) · 实习/年份未标）：考察主题：业务定义、分图设计、恢复与人工控制、后端基础。
- **[INT76 · 科大讯飞（AI相关岗）一面](https://www.nowcoder.com/feed/main/detail/1c425483516d4af1813d2dcdf98f4781?sourceSSR=users)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT76) · 实习/年份未标）：考察主题：规划选型、工具边界、异常兜底、评测。
- **[INT01 · 字节跳动-Agent开发实习生 一面（45分钟）](https://www.nowcoder.com/feed/main/detail/931a8a935a5e4b4f8d0b71cd4e818604)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT01) · 实习/年份未标）：考察主题：项目深挖/个人贡献、Agent循环/工具、RAG/检索、评测/指标、记忆/上下文。
- **[INT02 · 4.21 字节agent开发实习一面分享](https://www.nowcoder.com/feed/main/detail/e0d5745e28b64db79ba1832f958b758c)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT02) · 实习/年份未标）：考察主题：项目深挖/个人贡献、系统设计/取舍、Agent循环/工具、记忆/上下文、算法/编程。
- **[INT40 · 智能体与大模型应用工程实习 一面](https://www.nowcoder.com/discuss/894720138258173952?sourceSSR=post)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT40) · 实习/年份未标）：考察主题：项目深挖/个人贡献、数据库/缓存、消息队列/一致性、RAG/检索、Agent循环/工具。
- **[INT41 · 腾讯实习 ai应用开发后端面经分享](https://www.nowcoder.com/feed/main/detail/144c6ae334b24c0aa643ed43ccfebaac?sourceSSR=dynamic)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT41) · 实习/年份未标）：考察主题：项目深挖/个人贡献、Agent循环/工具、RAG/检索、系统设计/取舍、消息队列/一致性。
- **[INT54 · 字节数据中台Agent全栈面经](https://www.nowcoder.com/feed/main/detail/fe77496948f74b4091ab4bb6e8156c8b?sourceSSR=dynamic)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT54) · 实习/年份未标）：考察主题：项目深挖/个人贡献、Agent循环/工具、网络/操作系统、系统设计/取舍、算法/编程。
- **[INT55 · 字节Agent开发后端 日常实习一面凉面](https://www.nowcoder.com/discuss/932295617999622144)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT55) · 实习/年份未标）：考察主题：RAG/检索、评测/指标、项目深挖/个人贡献、系统设计/取舍、算法/编程。
- **[INT84 · 9.7百度agent开发日常实习面经](https://www.nowcoder.com/feed/main/detail/bb8c28105f364770b57ff5eb5649cc60)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT84) · 实习/年份未标）：考察主题：混合检索、RAG切片、开源改造、工具执行器、失败兜底。
- **[INT102 · 字节AI Agent实习面经](https://www.nowcoder.com/feed/main/detail/8a553bb6ea8445d0b0abe11e87614cea?sourceSSR=%E5%85%B6%E4%BB%96)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT102) · 实习/年份未标）：考察主题：算法/编程、并发/线程、项目深挖/个人贡献、记忆/检索、Agent循环/工具。
- **[INT103 · 实习面经分享 阿里云AI应用开发一面](https://www.nowcoder.com/feed/main/detail/775b45a6884f4688bc1e24ad8023183b)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT103) · 实习/年份未标）：考察主题：算法/编程、项目深挖/个人贡献、Agent循环/工具、评测/指标。
- **[INT104 · 美团Agent开发一面 日常](https://api-cdn.nowcoder.com/feed/main/detail/58159306df52463ab75d72daa80d66df?sourceSSR=subject)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT104) · 实习/年份未标）：考察主题：算法/编程、并发/线程、操作系统、项目深挖/个人贡献、RAG/检索。
- **[INT67 · 阿里云Agent一面：项目取舍、RPC与AI Coding热更新](https://www.nowcoder.com/discuss/872120976190816256)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT67) · 未知/年份未标）：考察主题：工作流与Agent、实习项目、IPC、RPC/HTTP、AI Coding。
- **[INT82 · 字节- AML大模型后端开发-一二面](https://www.nowcoder.com/feed/main/detail/25df6c4042a742dbbe420db58c3abf0c)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT82) · 未知/年份未标）：考察主题：MCP网关、多租户、记忆、KV Cache、Agentic RAG。
- **[INT83 · 百度一面面经](https://www.nowcoder.com/feed/main/detail/fa3706d7d465417f83d550b7f471941b)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT83) · 未知/年份未标）：考察主题：SQL、ES、锁、线程池、检索融合。

