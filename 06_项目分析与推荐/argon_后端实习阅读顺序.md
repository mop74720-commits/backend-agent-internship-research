# 后端开发实习：分级阅读与源码精读清单

> **核心原则**：先看 2025–2026 严格近期工程实习面经与含完整履历的候选人案例，明确“数据库/缓存/MQ/并发排障”的追问深度，再对照精读 SchoolBus、UltiCode、ResiCache 与 ShenYu 的核心模块。
> - **配套可视化页面**：[项目比较与精读指南.html](argon_项目比较与精读指南.html) · [面经重点与项目追问.html](../04_面经与专业观点/argon_面经重点与项目追问.html) · [候选人与简历图册.html](../03_简历与候选人案例/argon_候选人与简历图册.html)

---

## 一、项目源码分级精读清单（先读机制与缺陷，切勿整仓照搬）

### 精读 · 业务与故障分析

#### [PRO01 · 12306：交易与并发模块参考](argon_项目比较与精读指南.html#PRO01)（精读｜[原仓库](https://github.com/nageoffer/12306)）
- **为什么读**：交易一致性与并发题的基础样本；优先看MQ幂等与购票令牌，再读失败窗口。
- **避坑提示**：面向求职教学，直接复刻辨识度低。
- **推荐精读模块**：
  - `frameworks/idempotent/src/main/java/org/opengoofy/index12306/framework/starter/idempotent/core/spel/IdempotentSpELByMQExecuteHandler.java`
  - `services/ticket-service/src/main/java/org/opengoofy/index12306/biz/ticketservice/service/impl/TicketServiceImpl.java`
  - `services/ticket-service/src/main/resources/lua/ticket_availability_token_bucket.lua`

#### [PRO02 · SaaS短链接：读多写少与统计链路参考](argon_项目比较与精读指南.html#PRO02)（精读｜[原仓库](https://github.com/nageoffer/shortlink)）
- **为什么读**：比大平台范围集中，适合读热点缓存、访问链与异步统计的取舍。
- **避坑提示**：教学项目同质化。
- **推荐精读模块**：
  - `project/src/main/java/com/nageoffer/shortlink/project/service/impl/ShortLinkServiceImpl.java`
  - `project/src/main/java/com/nageoffer/shortlink/project/mq/consumer/ShortLinkStatsSaveConsumer.java`

#### [PRO08 · 学成在线：成功候选人关联业务仓库与消息可靠性反例](argon_项目比较与精读指南.html#PRO08)（精读｜[原仓库](https://github.com/viego1999/xuecheng-plus-project)）
- **为什么读**：优先做成功者项目描述→课程发布事务→消息线程池→测试断言的对照阅读。
- **避坑提示**：仓库固定版本最后提交于 2023 年，父 POM 为 Java 8／Spring Boot 2.3.7；这是历史技术组合，不能称作 2026 年招聘统一推荐版本。
- **推荐精读模块**：
  - `xuecheng-plus-content/xuecheng-plus-content-service/src/main/java/com/xuecheng/content/service/impl/CoursePublishServiceImpl.java`
  - `xuecheng-plus-message-sdk/src/main/java/com/xuecheng/messagesdk/service/MessageProcessAbstract.java`
  - `xuecheng-plus-learning/xuecheng-plus-learning-service/src/main/java/com/xuecheng/learning/service/impl/ReceivePayNotifyServiceImpl.java`
  - `xuecheng-plus-learning/xuecheng-plus-learning-service/src/test/java/com/xuecheng/learning/PayNotifyServiceTest.java`

#### [PRO19 · SchoolBus：本人面经直接关联的预约项目，附v1代码局限](argon_项目比较与精读指南.html#PRO19)（精读｜[原仓库](https://github.com/DreamCats/school-bus/tree/fc50ea8b19f99b4b15b2012048ea4651d896dd94)）
- **为什么读**：最适合面经→实现→局限的对照；先看本人字节/京东追问，再读v1补偿和取消。
- **避坑提示**：以上仅固定提交school-bus/下v1路径的静态观察；同仓另有school-bus-cloud版本，不把局部风险泛化为全版本结论。
- **推荐精读模块**：
  - `README.md`
  - `school-bus/guns-order/src/main/java/com/stylefeng/guns/rest/modular/order/OrderServiceImpl.java`

### 精读 · 方向选择

- **Go方向**：
  - **[PRO18 · Crony：Go分布式定时任务工程参考，未证作者SSP](argon_项目比较与精读指南.html#PRO18)**（[原仓库](https://github.com/tmnhs/Crony/tree/00df3df90306811332d0aff66a259cf90ad6954f)）：Go方向精读注册、任务分配与失败迁移，特别对照公司描述与个人重写的边界。精读入口：`README.md`；`go.mod`；`common/pkg/etcdclient/registry.go`
- **C++网络方向**：
  - **[PRO17 · linyacool WebServer：本人SSP关联的网络工程与开发复盘](argon_项目比较与精读指南.html#PRO17)**（[原仓库](https://github.com/linyacool/WebServer)）：C++/网络方向精读并发模型、测试条件和遇到的困难；Java方向按兴趣选读。精读入口：`README.md`；`并发模型.md`；`WebServer/HttpData.cpp`
- **开源协作方向**：
  - **[PRO09 · Apache ShenYu：插件链、响应式网关与可测试开源贡献](argon_项目比较与精读指南.html#PRO09)**（[原仓库](https://github.com/apache/shenyu)）：开源贡献目标先精读两个本人PR的改动与断言，再选读插件链；勿把整库算个人。精读入口：`https://github.com/apache/shenyu/pull/3848`；`https://github.com/apache/shenyu/blob/e63d4b366d0d0eb2c7cea87e4b4cf0c711645bcd/shenyu-integrated-test/shenyu-integrated-test-https/src/test/java/org/apache/shenyu/integrated/test/https/Oauth2PluginTest.java#L38`；`https://github.com/apache/shenyu/pull/3672`

### 选读 · 补专项

#### [PRO03 · mall：业务建模与常用技术栈参考](argon_项目比较与精读指南.html#PRO03)（选读｜[原仓库](https://github.com/macrozheng/mall)）
- **为什么读**：读订单生成与超时取消即可，避免为覆盖功能把时间耗在全站CRUD。
- **避坑提示**：全部照做耗时，容易停留在CRUD。
- **推荐精读模块**：
  - `mall-portal/src/main/java/com/macro/mall/portal/service/impl/OmsPortalOrderServiceImpl.java`
  - `mall-portal/src/main/java/com/macro/mall/portal/component/CancelOrderReceiver.java`
  - `mall-portal/src/main/java/com/macro/mall/portal/config/RabbitMqConfig.java`

#### [PRO10 · Casdoor：从候选人开源条目拆读身份与权限工程](argon_项目比较与精读指南.html#PRO10)（选读｜[原仓库](https://github.com/casdoor/casdoor)）
- **为什么读**：按权限策略和测试模块精确选读；候选人具体贡献保留待核。
- **避坑提示**：认证平台的协议和身份提供商范围很大；全面重做会分散时间，接入 SDK 本身也不能证明理解认证与授权。
- **推荐精读模块**：
  - `object/permission_enforcer.go`
  - `object/permission_enforcer_test.go`
  - `object/token_jwt_key.go`
  - `object/token_jwt_key_test.go`

#### [PRO14 · CalvinNeo CFortranTranslator：本人SSP关联的语言工具项目](argon_项目比较与精读指南.html#PRO14)（选读｜[原仓库](https://github.com/CalvinNeo/CFortranTranslator)）
- **为什么读**：系统/C++方向读编译原理、语义边界与测试表达；Java业务方向优先级较低。
- **避坑提示**：历史工具链与构建说明较旧，现代环境兼容性未验证。
- **推荐精读模块**：
  - `docs/Develop.md`
  - `src/grammar/for90.y`
  - `src/target/gen_do.cpp`
  - `demos/test/parser_test.cpp`

#### [PRO15 · CalvinNeo ATP：本人SSP关联的UDP可靠传输库](argon_项目比较与精读指南.html#PRO15)（选读｜[原仓库](https://github.com/CalvinNeo/ATP)）
- **为什么读**：网络/C++方向读事件边界与故障测试局限；不把QPS/可靠性口号写成果。
- **避坑提示**：README明确框架模式非线程安全；调用方需维护计时器与事件。
- **推荐精读模块**：
  - `README.md`
  - `src/atp.h`
  - `src/atp_impl.cpp`
  - `src/atp_callback.cpp`

#### [PRO16 · CalvinNeo Nuft：本人SSP关联的Raft实现与失败测试材料](argon_项目比较与精读指南.html#PRO16)（选读｜[原仓库](https://github.com/CalvinNeo/Nuft)）
- **为什么读**：分布式系统进阶读不变量、持久化和失败材料；先理解为何测试不能证明一致性。
- **避坑提示**：README明确部分测试可能失败；本次不隐去此限制。
- **推荐精读模块**：
  - `README.md`
  - `src/node_persister.cpp`
  - `src/node_rpc_a.cpp`
  - `src/test/test.cpp`

### 选读 · Agent服务实现

#### [PRO04 · Ragent：Java Agent与RAG全链路参考](argon_项目比较与精读指南.html#PRO04)（选读｜[原仓库](https://github.com/nageoffer/ragent)）
- **为什么读**：已有Java基础后读状态存储和服务边界；不适合替代传统后端基本功。
- **避坑提示**：已经是一套较大的平台，不宜整体冒充个人原创。
- **推荐精读模块**：
  - `agent/src/main/java/com/nageoffer/ai/ragent/agent/confirm/AgentConfirmDenialMiddleware.java`
  - `agent/src/main/java/com/nageoffer/ai/ragent/agent/dao/mapper/AgentStateMapper.java`
  - `agent/src/main/java/com/nageoffer/ai/ragent/agent/config/AgentEngineConfiguration.java`

#### [PRO05 · DeerFlow：长任务运行与隔离参考](argon_项目比较与精读指南.html#PRO05)（选读｜[原仓库](https://github.com/bytedance/deer-flow)）
- **为什么读**：针对异步任务/持久化服务进阶阅读，常规实习先读范围更集中的项目。
- **避坑提示**：系统庞大，读完或部署成功不等于个人实现。
- **推荐精读模块**：
  - `backend/app/gateway/auth_middleware.py`
  - `backend/app/gateway/checkpoint_retention.py`
  - `backend/docs/checkpoint-retention-contract.md`
  - `backend/tests/test_checkpoint_retention_contract.py`

#### [PRO06 · Open Deep Research：研究编排与评测参考](argon_项目比较与精读指南.html#PRO06)（选读｜[原仓库](https://github.com/langchain-ai/open_deep_research)）
- **为什么读**：研究异步任务与可测量服务时选读；不是常用Java业务技术栈样本。
- **避坑提示**：仅生成漂亮报告难以验证任务成功。
- **推荐精读模块**：
  - `src/open_deep_research/deep_researcher.py`
  - `tests/evaluators.py`
  - `tests/run_evaluate.py`
  - `tests/pairwise_evaluation.py`

#### [PRO07 · RAGFlow：文档解析与检索工程参考](argon_项目比较与精读指南.html#PRO07)（选读｜[原仓库](https://github.com/infiniflow/ragflow)）
- **为什么读**：只取检索服务和测试工程片段，不为大平台体量整库复刻。
- **避坑提示**：大平台搭建成本高，容易遮蔽自己的核心贡献。
- **推荐精读模块**：
  - `docs/guides/dataset/retrieval_testing.md`
  - `example/sdk/retrieval_example.py`
  - `test/benchmark/README.md`
  - `test/README.md`

#### [PRO11 · AgentScope：工具权限、状态与中断测试的工程参考](argon_项目比较与精读指南.html#PRO11)（选读｜[原仓库](https://github.com/agentscope-ai/agentscope)）
- **为什么读**：需要研究异步执行与取消语义时选读；常规业务后端先看领域服务。
- **避坑提示**：当前主线规模较大，SOP、语音、团队、服务、渠道和多种 workspace 会提高学习成本；README 部分功能明确标为 Experimental。
- **推荐精读模块**：
  - `src/agentscope/permission/_engine.py`
  - `src/agentscope/agent/_agent.py`
  - `src/agentscope/state/_state.py`
  - `tests/permission_engine_test.py`

#### [PRO12 · OpenManus：紧凑 Agent循环、工具调用与沙箱边界对照](argon_项目比较与精读指南.html#PRO12)（选读｜[原仓库](https://github.com/FoundationAgents/OpenManus)）
- **为什么读**：异步循环与资源清理参考；非传统后端主技术栈。
- **避坑提示**：is_stuck 依据相同 assistant 文本计数，处理方式是追加改变策略的提示；它不证明任务取得进展，也不保证成本收敛或业务正确。
- **推荐精读模块**：
  - `app/agent/base.py`
  - `app/agent/toolcall.py`
  - `app/sandbox/core/sandbox.py`
  - `tests/sandbox/test_sandbox.py`

### 暂缓 · 整库复刻

- 先读模块和失败材料，不把通用平台照搬成个人项目。

### 精读 · 本人履历直接点名

#### [PRO20 · UltiCode：完整履历直接点名的本人判题平台](argon_项目比较与精读指南.html#PRO20)（精读｜[原仓库](https://github.com/DavidHLP/UltiCode/tree/d53b582e2fae32ef644642651086df0e5ed3163d)）
- **为什么读**：适合按消息故障/结果竞争读具体业务实现。
- **避坑提示**：无本地构建/测试证据。
- **推荐精读模块**：
  - `services/submission/src/main/java/com/ulticode/modules/queue/outbox/dispatcher/JudgeOutboxDispatcher.java`
  - `services/submission/src/main/java/com/ulticode/modules/submission/mapper/SubmissionMapper.java`
  - `services/auth/src/main/java/com/ulticode/auth/refreshtoken/service/RefreshTokenService.java`
  - `services/judge-runtime/src/test/java/com/ulticode/modules/queue/port/adapter/JudgeStreamRedisIntegrationTest.java`
  - `services/submission/src/main/java/com/ulticode/modules/submission/port/DefaultSubmissionWritePort.java`

#### [PRO21 · ResiCache：完整履历直接点名的本人缓存扩展](argon_项目比较与精读指南.html#PRO21)（精读｜[原仓库](https://github.com/DavidHLP/ResiCache/tree/1ed3be36af0795a363d624d38de676c0d00b4cf7)）
- **为什么读**：适合深入缓存并发、清理和测试边界。
- **避坑提示**：无本地构建/测试证据。
- **推荐精读模块**：
  - `src/main/java/io/github/davidhlp/spring/cache/redis/cache/SyncSupport.java`
  - `src/main/java/io/github/davidhlp/spring/cache/redis/cache/SyncRole.java`
  - `src/main/java/io/github/davidhlp/spring/cache/redis/cache/EarlyRefresh.java`
  - `src/test/java/io/github/davidhlp/spring/cache/redis/cache/SyncSupportSingleFlightTest.java`
  - `src/test/java/io/github/davidhlp/spring/cache/redis/cache/EarlyExpirationHandlerRaceConditionIntegrationTest.java`

### 选读 · 大厂实习者本人项目

#### [PRO22 · Distributed Key-Value Store：课程框架上的Raft/MVCC实现](argon_项目比较与精读指南.html#PRO22)（选读｜[原仓库](https://github.com/shufengc/distributed-kv-store/tree/d7132bba33fb2aec2ccd802c357dc1cd1f74fb5e)）
- **为什么读**：分布式存储进阶，先分清课程框架和个人实现。
- **避坑提示**：未运行课程测试；未证明所有partition场景linearizability或独立实现比例；当前固定版本不自动代表2025腾讯投递时项目。
- **推荐精读模块**：
  - `raft/raft.go`
  - `kv/server/server.go`

---

## 二、对标候选人案例（共 15 位，按证据形态分级）

> **阅读提示**：CV29有2025腾讯/2026 Stripe实习和主页直接项目链接，履历不完整且课程框架边界明确；CV30为字节2025后端/2026 Agent完整CV，无公开内部源码。CV28为交付企业，非阿里直签。 本轮CV33为明确2026后端实习offer的经历选读；CV32为校招、CV34事件年未知，均无新增完整CV或本人源码。

### 1. 含公开脱敏简历 / 网页履历的标杆案例（优先对标，共 3 位）

- **[CV30 · Andrew Wang：字节后端与Agent实习完整专业履历](../03_简历与候选人案例/argon_候选人与简历图册.html#CV30)**（[原始来源](https://andrewtheterp.com/)）：结果：两段大厂实习经历自述；SSP/SP档位未披露 ｜ 看点：精读实习职责及工程机制；公开源码、课程框架、内部项目分别核对，不推导录用因果
- **[CV28 · DavidHLP：近期后端实习完整履历与本人开源项目直接关联](../03_简历与候选人案例/argon_候选人与简历图册.html#CV28)**（[原始来源](https://davidhlp.github.io/about/)）：结果：博彦科技后端实习，服务阿里云客户项目；非阿里直签，未分档 ｜ 看点：精读本人职责与两仓指定模块；实习与开源作品、面经时点分别核对
- **[CV23 · 张恒华 / Henghua Zhang：近期实习完整公开履历脱敏副本](../03_简历与候选人案例/argon_候选人与简历图册.html#CV23)**（[原始来源](https://zhh2001.github.io/resume)）：结果：本人完整履历明确实习公司、岗位和起止时间；档位未披露 ｜ 看点：可精读时间线与项目主体/角色的对应；无法从本材料分析项目实现深度。作为Go后端成功实习真实履历样本，比模板或仅offer自述更直接，但不能当作项目技术栈充分样本

### 2. 求职经历与面经复盘案例（补充对标，共 12 位）

- **[CV29 · Shufeng (Alex) Chen：腾讯/Stripe实习履历与本人直链项目](../03_简历与候选人案例/argon_候选人与简历图册.html#CV29)**（[原始来源](https://shufengc.dev/)）：结果：两段大厂实习经历自述；SSP/SP档位未披露 ｜ 看点：精读实习职责及工程机制；公开源码、课程框架、内部项目分别核对，不推导录用因果
- **[CV22 · Stochastic / Asthenia0412：2025—2026后端与Agent工程实习履历片段](../03_简历与候选人案例/argon_候选人与简历图册.html#CV22)**（[原始来源](https://github.com/Asthenia0412/Asthenia0412/blob/61058d605bbf82efeb0ef451d77d1b049c71a20e/README.md)）：结果：本人列出2025—2026多段后端实习；未披露SSP ｜ 看点：选读岗位时间线；不以同账号仓库填成个人求职项目
- **[CV27 · 2025暑期19场复盘：阿里云基架存储offer及WebServer经验反思](../03_简历与候选人案例/argon_候选人与简历图册.html#CV27)**（[原始来源](https://ac.nowcoder.com/discuss/737813386313940992)）：结果：阿里云 正式offer自述 ｜ 看点：近期C++实习的成功与不足对照选读。缺分布式实战等失败原因是作者自评，不升级为企业反馈；对整个C++岗位前景的个人劝退不当作市场结论
- **[CV25 · 2026暑期：蚂蚁AlipayPlus智能体应用offer、TikTok后端OC及本人面经](../03_简历与候选人案例/argon_候选人与简历图册.html#CV25)**（[原始来源](https://ac.nowcoder.com/discuss/1610772)）：结果：蚂蚁集团 已收到offer自述；字节跳动 OC，称offer报审批；字节跳动 已在实习3个多月自述 ｜ 看点：Agent/后端实习的近期成功自述可选读；它补的是公司、岗位、事件年与结果，项目实现证据仍弱
- **[CV09 · 27双非本：腾讯IEG游戏安全后台实习面经](../03_简历与候选人案例/argon_候选人与简历图册.html#CV09)**（[原始来源](https://www.nowcoder.com/feed/main/detail/9ecd5997a7d74f3fa885695032f32065?sourceSSR=dynamic&weFlow=true)）：结果：本人时间线记载Offer；没有SSP信息 ｜ 看点：优先用来验证广度与深度的组合；与纯Agent岗位分列
- **[CV04 · 双非本上岸字节后端：接单、开发、测开转后端的大学四年](../03_简历与候选人案例/argon_候选人与简历图册.html#CV04)**（[原始来源](https://www.nowcoder.com/discuss/753246853839269888)）：结果：本人自述字节后端转正，另有其他大厂offer；未说明SSP ｜ 看点：中优先级；借鉴真实交付和基础补强，不依赖接单或转岗作为唯一计划
- **[CV21 · DreamCats：本人项目与三家面经可直接对应，SSP未证](../03_简历与候选人案例/argon_候选人与简历图册.html#CV21)**（[原始来源](https://github.com/DreamCats/java-notes/blob/c4cf3bbbb6bc95daaf6deff734642ea51c7cec9c/Java/mianjing/my%E5%AD%97%E8%8A%82.md#L12)）：结果：本人京东offer、字节意向书；腾讯自评不理想，未核最终结果。未写SSP档位 ｜ 看点：['求职项目、本人多轮问题与可读代码形成直接关系，适合研究技术栈为什么会被追问']
- **[CV02 · JavaWxy：作者学习路线、求职项目与面试自我介绍](../03_简历与候选人案例/argon_候选人与简历图册.html#CV02)**（[原始来源](https://github.com/viego1999/JavaWxy)）：结果：本人自述腾讯SSP，另有拼多多/快手/阿里等offer；暑期选择拼多多 ｜ 看点：优先阅读；用于学习项目组合与深挖准备，不能直接把课程项目包装成个人生产经历
- **[CV18 · IcyCC：2019后端SP/SSP自述、历史履历与本人项目组合](../03_简历与候选人案例/argon_候选人与简历图册.html#CV18)**（[原始来源](https://github.com/IcyCC/effective_note/blob/d55074032217c48e3d872d4524ba6cea94613b86/%E7%A7%8B%E6%8B%9B/%E7%A7%8B%E6%8B%9B%E6%80%BB%E7%BB%93.md#L16)）：结果：本人自述多家结果中大多为SP和SSP，未逐公司定档 ｜ 看点：['成功自述文章→“我的简历”直接链接→2019历史简历→本人命名仓库，归属链清楚。', '业务交付、网络机制、语言互操作和开发效率工具各有侧重，适合分析项目组合。', '实际公开简历有安全可抽取的技能/项目内…
- **[CV32 · 无实习人士如何上岸秋招（总结+面经+路线）](../03_简历与候选人案例/argon_候选人与简历图册.html#CV32)**（[原始来源](https://www.nowcoder.com/discuss/545916636923006976)）：结果：本人校招经历及项目追问；录用档位未披露 ｜ 看点：适合选后端主项目：消息系统同时承载幂等、顺序、重试、削峰和可观测性，技术点有共同业务理由
- **[CV33 · 非科班转码：211化学本→985材料硕→字节后端开发](../03_简历与候选人案例/argon_候选人与简历图册.html#CV33)**（[原始来源](https://ac.nowcoder.com/discuss/1626909?channel=-1&source_id=discuss_terminal_discuss_hot_nctrack&type=0)）：结果：明确2026实习；字节财经未披露档位offer自述，TT失败分开 ｜ 看点：最贴近“后端＋AI”组合的近期样本：传统一致性和Agent问题出现在同一后端面试中
- **[CV34 · 择难路 未有疑 四非学院本春招拿下大厂后端](../03_简历与候选人案例/argon_候选人与简历图册.html#CV34)**（[原始来源](https://ac.nowcoder.com/discuss/1518502?channel=-1&source_id=0&type=0)）：结果：春招后端未披露档位offer；本次未独立确认事件年 ｜ 看点：适合研究真实问题与实习产出的价值，以及业务项目和基础设施项目如何互补

---

## 三、精选面经阅读顺序（共 27 份，按时效与代表性分级）

### 1. 严格近期（2025–2026）工程实习面经（必读，共 0 份）


### 2. 高价值专项追问与经典实习面经（选读，共 27 份）

- **[INT77 · 暑期实习面试结束啦，写个总结吧](https://ac.nowcoder.com/discuss/737813386313940992)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT77) · 实习/年份已核）：考察主题：C++网络、数据库/缓存实战、场景题。
- **[INT10 · 腾讯日常实习一面面经（2027暑期向）](https://www.nowcoder.com/feed/main/detail/37c64318e134459bbd9a5c7953e99aea?sourceSSR=post)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT10) · 实习/年份已核）：考察主题：项目深挖/个人贡献、网络/操作系统、数据库/缓存、RAG/检索、算法/编程。
- **[INT12 · 27双非本—腾讯IEG游戏安全后台实习面经](https://www.nowcoder.com/feed/main/detail/9ecd5997a7d74f3fa885695032f32065?sourceSSR=dynamic&weFlow=true)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT12) · 实习/年份已核）：考察主题：项目深挖/个人贡献、编程语言/并发、网络/操作系统、数据库/缓存、系统设计/取舍。
- **[INT20 · 阿里云Java研发实习 - 一面](https://www.nowcoder.com/discuss/743798386737897472?sourceSSR=dynamic)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT20) · 实习/年份已核）：考察主题：项目深挖/个人贡献、Java并发/JVM、SQL优化/事务、Spring/AOP、网络协议。
- **[INT22 · 四非本 滴滴-后端实习面经(已OC)](https://www.nowcoder.com/feed/main/detail/c822bd1fffa64addb718e806090a20ee?toCommentId=21427551)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT22) · 实习/年份已核）：考察主题：项目深挖/个人贡献、Java并发/JVM、消息顺序/一致性、RPC协议、事务。
- **[INT24 · 26届快手暑期实习（已OC）](https://www.nowcoder.com/feed/main/detail/8c1a63e46e4e462892474e405d611028)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT24) · 实习/年份已核）：考察主题：项目深挖/个人贡献、Redis数据结构/GEO、空间查询、算法/编程、业务理解。
- **[INT28 · 26届后端实习-蚂蚁集团后端开发一面面经](https://www.nowcoder.com/feed/main/detail/bb4c92b4084f44e69388ac342c1ca809?sourceSSR=users)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT28) · 实习/年份已核）：考察主题：实验室/项目经历、Java泛型/集合、设计模式、线程池、Redis高可用。
- **[INT85 · 爱橙科技Java暑期实习一面：MQ、测试幂等及高可用追问](https://www.nowcoder.com/discuss/730542760465276928)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT85) · 实习/年份已核）：考察主题：MQ、环境隔离、RPC、OOM、消费者积压。
- **[INT91 · 快手商业化 Java日常实习](https://www.nowcoder.com/discuss/719242991700889600)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT91) · 实习/年份已核）：考察主题：算法/编程、JVM/语言运行时、并发/线程、数据库/SQL、缓存/Redis。
- **[INT93 · 字节生活服务后端开发日常实习一二三面经](https://www.nowcoder.com/feed/main/detail/f38ea39b741e44be8730c1e7f7d88439?sourceSSR=dynamic)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT93) · 实习/年份已核）：考察主题：算法/编程、JVM/语言运行时、数据库/SQL、缓存/Redis、网络/协议。
- **[INT101 · 快手商业化垂直业务 Java日常实习](https://www.nowcoder.com/discuss/726371483039133696)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT101) · 实习/年份已核）：考察主题：算法/编程、JVM/语言运行时、数据库/SQL、缓存/Redis、消息/异步。
- **[INT81 · 从一面到二面：Java后端实习面试复盘（原版两轮，含事后模板）](https://raw.githubusercontent.com/DavidHLP/DavidHLP.github.io/6f3d114a6ef9eb08b730f5f4740afe5b7d22d426/src/content/note/zh-cn/java-internship-interview-blog-polished.md)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT81) · 实习/年份未标）：考察主题：Spring Cache、缓存并发、OJ、MQ选型、容器隔离。
- **[INT71 · 字节-TikTok-后端一面](https://www.nowcoder.com/discuss/876046266558398464?sourceSSR=users)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT71) · 实习/年份未标）：考察主题：RAG检索与评测、JVM/并发、AI Coding验收。
- **[INT07 · 美团后端暑期实习面经](https://www.nowcoder.com/feed/main/detail/3187ad5588394e108f96db0eb9e82bcf)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT07) · 实习/年份未标）：考察主题：项目深挖/个人贡献、系统设计/取舍、消息队列/一致性、编程语言/并发、算法/编程。
- **[INT09 · 暑期实习第二个offer-淘天oc](https://www.nowcoder.com/feed/main/detail/32f9c690698f4462b8f6b75ba721d168)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT09) · 实习/年份未标）：考察主题：项目深挖/个人贡献、编程语言/并发、数据库/缓存、消息队列/一致性、系统设计/取舍。
- **[INT11 · 腾讯后端实习一面90min](https://www.nowcoder.com/feed/main/detail/9e1c51d930b247aab6e1973ba920d271)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT11) · 实习/年份未标）：考察主题：项目深挖/个人贡献、编程语言/并发、数据库/缓存、消息队列/一致性、系统设计/取舍。
- **[INT86 · 美团后端暑期实习二面已offer：项目调研、容量与运维追问](https://www.nowcoder.com/discuss/736940763258400768)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT86) · 实习/年份未标）：考察主题：个人贡献、方案调研、项目优化、容量、分片。
- **[INT87 · 美团后端日常实习（已offer）](https://api-cdn.nowcoder.com/discuss/741030289186525184?sourceSSR=subject)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT87) · 实习/年份未标）：考察主题：算法/编程、JVM/语言运行时、数据库/SQL、缓存/Redis、分布式/一致性。
- **[INT88 · 字节后端实习面经](https://www.nowcoder.com/discuss/723622216419586048?sourceSSR=users)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT88) · 实习/年份未标）：考察主题：算法/编程、并发/线程、网络/协议、操作系统。
- **[INT89 · 美团 Java 二面 强度这么高吗](https://ac.nowcoder.com/discuss/1674038?channel=-1&source_id=discuss_tag_discuss_hot_nctrack&type=0)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT89) · 实习/年份未标）：考察主题：算法/编程、并发/线程、数据库/SQL、缓存/Redis、网络/协议。
- **[INT94 · 暑期实习记录 附C++面经](https://ac.nowcoder.com/discuss/1500141?type=0)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT94) · 实习/年份未标）：考察主题：算法/编程、并发/线程、网络/协议、操作系统、项目深挖/个人贡献。
- **[INT99 · 26快手商业化 日常实习一二面 已OC](https://www.nowcoder.com/discuss/718514450587746304?sourceSSR=users)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT99) · 实习/年份未标）：考察主题：算法/编程、并发/线程、数据库/SQL、缓存/Redis、项目深挖/个人贡献。
- **[INT100 · 京东后端实习一二面面经 Offer](https://api-cdn.nowcoder.com/discuss/933060569995759616?sourceSSR=dynamic)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT100) · 实习/年份未标）：考察主题：缓存/Redis、项目深挖/个人贡献、Agent循环/工具。
- **[INT66 · DreamCats：同一班车项目在字节、京东、腾讯的本人多轮对照](https://github.com/DreamCats/java-notes/blob/c4cf3bbbb6bc95daaf6deff734642ea51c7cec9c/Java/mianjing/README.md#L24)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT66) · 未知/年份未标）：考察主题：项目拆分、Dubbo、JWT/SSO、Redis锁、订单超时。
- **[INT78 · 快手秋招正式批 Golang后端 一二三四面面经（已Offer）](https://www.nowcoder.com/discuss/792809776626356224)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT78) · 校招/年份已核）：考察主题：IM、心跳与连接、时间轮、消息可靠性、Kafka。
- **[INT79 · 字节后端 秋招一二三四面面经（已接Offer）](https://www.nowcoder.com/discuss/793068978837921792)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT79) · 校招/年份已核）：考察主题：项目瓶颈、IM、消息队列选型、性能瓶颈与排障、全链路。
- **[INT80 · 小鹏秋招正式批 Golang后端 一二面面经（待HR面）](https://www.nowcoder.com/discuss/788000430256037888)**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#INT80) · 校招/年份已核）：考察主题：Golang并发、IPC/Protobuf、TCP容量、SQL、项目选型。

