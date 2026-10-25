# 外部调研文档（DOC01–DOC10）价值判断与对应精读模块

> **使用说明**：本表对外部调研合入的 10 份综述文档（`DOC01`–`DOC10`）进行证据去重与工程价值评估，并将其中有价值的结论直接映射到本包已核实的 **JD、候选人履历、面经与源码模块**，避免重复阅读二手综述。

---

## 一、10 份外部调研文档（DOC01–DOC10）逐份评估表

| 编号 | 文档主题与摘要 | 推荐动作 | 可采信的工程分析 | 需剔除的夸大或未核推断 |
| :---: | :--- | :---: | :--- | :--- |
| **DOC01** | **Building effective agents**<br><small></small> | `核验后吸收` | 提供方向性综述视角 | 二手汇总不直接计入原始样本分母 |
| **DOC02** | **Demystifying evals for AI agents**<br><small></small> | `核验后吸收` | 提供方向性综述视角 | 二手汇总不直接计入原始样本分母 |
| **DOC03** | **Agent评测白皮书01：Agent评测全览**<br><small></small> | `核验后吸收` | 提供方向性综述视角 | 二手汇总不直接计入原始样本分母 |
| **DOC04** | **LangGraph Persistence**<br><small></small> | `核验后吸收` | 提供方向性综述视角 | 二手汇总不直接计入原始样本分母 |
| **DOC05** | **LangGraph Interrupts**<br><small></small> | `核验后吸收` | 提供方向性综述视角 | 二手汇总不直接计入原始样本分母 |
| **DOC06** | **MCP Tools specification（固定2025-06-18版）**<br><small></small> | `核验后吸收` | 提供方向性综述视角 | 二手汇总不直接计入原始样本分母 |
| **DOC07** | **Debezium Outbox Event Router**<br><small></small> | `核验后吸收` | 提供方向性综述视角 | 二手汇总不直接计入原始样本分母 |
| **DOC08** | **MySQL InnoDB Locking Reads**<br><small></small> | `核验后吸收` | 提供方向性综述视角 | 二手汇总不直接计入原始样本分母 |
| **DOC09** | **Redis Distributed Locks**<br><small></small> | `核验后吸收` | 提供方向性综述视角 | 二手汇总不直接计入原始样本分母 |
| **DOC10** | **RocketMQ Consumption Retry**<br><small></small> | `核验后吸收` | 提供方向性综述视角 | 二手汇总不直接计入原始样本分母 |

---

## 二、外部调研提及项目（PRO01–PRO25）精读模块速查表

> 完整优缺点对比与交互筛选请打开：[项目比较与精读指南.html](argon_项目比较与精读指南.html)

| 项目编号与名称 | 后端优先级 | Agent 优先级 | 核心精读模块路径 | 主要静态核查短板 |
| :--- | :---: | :---: | :--- | :--- |
| **[PRO01](argon_项目比较与精读指南.html#PRO01)**<br>12306：交易与并发模块参考 | 精读 | 非本方向 | `frameworks/idempotent/src/main/java/org/opengoofy/index12306/framework/starter/idempotent/core/spel/IdempotentSpELByMQExecuteHandler.java`<br>`services/ticket-service/src/main/java/org/opengoofy/index12306/biz/ticketservice/service/impl/TicketServiceImpl.java`<br>`services/ticket-service/src/main/resources/lua/ticket_availability_token_bucket.lua` | 面向求职教学，直接复刻辨识度低 |
| **[PRO02](argon_项目比较与精读指南.html#PRO02)**<br>SaaS短链接：读多写少与统计链路参考 | 精读 | 非本方向 | `project/src/main/java/com/nageoffer/shortlink/project/service/impl/ShortLinkServiceImpl.java`<br>`project/src/main/java/com/nageoffer/shortlink/project/mq/consumer/ShortLinkStatsSaveConsumer.java` | 教学项目同质化 |
| **[PRO03](argon_项目比较与精读指南.html#PRO03)**<br>mall：业务建模与常用技术栈参考 | 选读 | 非本方向 | `mall-portal/src/main/java/com/macro/mall/portal/service/impl/OmsPortalOrderServiceImpl.java`<br>`mall-portal/src/main/java/com/macro/mall/portal/component/CancelOrderReceiver.java`<br>`mall-portal/src/main/java/com/macro/mall/portal/config/RabbitMqConfig.java` | 全部照做耗时，容易停留在CRUD |
| **[PRO04](argon_项目比较与精读指南.html#PRO04)**<br>Ragent：Java Agent与RAG全链路参考 | 选读 | 精读 | `agent/src/main/java/com/nageoffer/ai/ragent/agent/confirm/AgentConfirmDenialMiddleware.java`<br>`agent/src/main/java/com/nageoffer/ai/ragent/agent/dao/mapper/AgentStateMapper.java`<br>`agent/src/main/java/com/nageoffer/ai/ragent/agent/config/AgentEngineConfiguration.java` | 已经是一套较大的平台，不宜整体冒充个人原创 |
| **[PRO05](argon_项目比较与精读指南.html#PRO05)**<br>DeerFlow：长任务运行与隔离参考 | 选读 | 选读 | `backend/app/gateway/auth_middleware.py`<br>`backend/app/gateway/checkpoint_retention.py`<br>`backend/docs/checkpoint-retention-contract.md` | 系统庞大，读完或部署成功不等于个人实现 |
| **[PRO06](argon_项目比较与精读指南.html#PRO06)**<br>Open Deep Research：研究编排与评测参考 | 选读 | 精读 | `src/open_deep_research/deep_researcher.py`<br>`tests/evaluators.py`<br>`tests/run_evaluate.py` | 仅生成漂亮报告难以验证任务成功 |
| **[PRO07](argon_项目比较与精读指南.html#PRO07)**<br>RAGFlow：文档解析与检索工程参考 | 选读 | 精读 | `docs/guides/dataset/retrieval_testing.md`<br>`example/sdk/retrieval_example.py`<br>`test/benchmark/README.md` | 大平台搭建成本高，容易遮蔽自己的核心贡献 |
| **[PRO08](argon_项目比较与精读指南.html#PRO08)**<br>学成在线：成功候选人关联业务仓库与消息可靠性反例 | 精读 | 非本方向 | `xuecheng-plus-content/xuecheng-plus-content-service/src/main/java/com/xuecheng/content/service/impl/CoursePublishServiceImpl.java`<br>`xuecheng-plus-message-sdk/src/main/java/com/xuecheng/messagesdk/service/MessageProcessAbstract.java`<br>`xuecheng-plus-learning/xuecheng-plus-learning-service/src/main/java/com/xuecheng/learning/service/impl/ReceivePayNotifyServiceImpl.java` | 仓库固定版本最后提交于 2023 年，父 POM 为 Java 8／Spring Boot 2.3.7；这是历史技术组合，不能称作 2026 年招聘统一推荐版本 |
| **[PRO09](argon_项目比较与精读指南.html#PRO09)**<br>Apache ShenYu：插件链、响应式网关与可测试开源贡献 | 精读 | 非本方向 | `https://github.com/apache/shenyu/pull/3848`<br>`https://github.com/apache/shenyu/blob/e63d4b366d0d0eb2c7cea87e4b4cf0c711645bcd/shenyu-integrated-test/shenyu-integrated-test-https/src/test/java/org/apache/shenyu/integrated/test/https/Oauth2PluginTest.java#L38`<br>`https://github.com/apache/shenyu/pull/3672` | 平台模块多，运行所有协议、注册中心和集成测试的成本高；把部署成功称作本人实现网关会夸大贡献 |
| **[PRO10](argon_项目比较与精读指南.html#PRO10)**<br>Casdoor：从候选人开源条目拆读身份与权限工程 | 选读 | 选读 | `object/permission_enforcer.go`<br>`object/permission_enforcer_test.go`<br>`object/token_jwt_key.go` | 认证平台的协议和身份提供商范围很大；全面重做会分散时间，接入 SDK 本身也不能证明理解认证与授权 |
| **[PRO11](argon_项目比较与精读指南.html#PRO11)**<br>AgentScope：工具权限、状态与中断测试的工程参考 | 选读 | 精读 | `src/agentscope/permission/_engine.py`<br>`src/agentscope/agent/_agent.py`<br>`src/agentscope/state/_state.py` | 当前主线规模较大，SOP、语音、团队、服务、渠道和多种 workspace 会提高学习成本；README 部分功能明确标为 Experimental |
| **[PRO12](argon_项目比较与精读指南.html#PRO12)**<br>OpenManus：紧凑 Agent循环、工具调用与沙箱边界对照 | 选读 | 精读 | `app/agent/base.py`<br>`app/agent/toolcall.py`<br>`app/sandbox/core/sandbox.py` | is_stuck 依据相同 assistant 文本计数，处理方式是追加改变策略的提示；它不证明任务取得进展，也不保证成本收敛或业务正确 |
| **[PRO13](argon_项目比较与精读指南.html#PRO13)**<br>Hello-Agents：评测方法与教材代码参考，整库不归档 | 非本方向 | 选读 | `LICENSE.txt`<br>`code/chapter12/README.md`<br>`code/chapter12/03_bfcl_custom_evaluation.py` | 这是课程与共创仓库，不是一个统一部署／统一测试的成品系统；不能把不同作者项目的功能合并声称成一个已经验证的平台 |
| **[PRO14](argon_项目比较与精读指南.html#PRO14)**<br>CalvinNeo CFortranTranslator：本人SSP关联的语言工具项目 | 选读 | 非本方向 | `docs/Develop.md`<br>`src/grammar/for90.y`<br>`src/target/gen_do.cpp` | 历史工具链与构建说明较旧，现代环境兼容性未验证 |
| **[PRO15](argon_项目比较与精读指南.html#PRO15)**<br>CalvinNeo ATP：本人SSP关联的UDP可靠传输库 | 选读 | 非本方向 | `README.md`<br>`src/atp.h`<br>`src/atp_impl.cpp` | README明确框架模式非线程安全；调用方需维护计时器与事件 |
| **[PRO16](argon_项目比较与精读指南.html#PRO16)**<br>CalvinNeo Nuft：本人SSP关联的Raft实现与失败测试材料 | 选读 | 非本方向 | `README.md`<br>`src/node_persister.cpp`<br>`src/node_rpc_a.cpp` | README明确部分测试可能失败；本次不隐去此限制 |
| **[PRO17](argon_项目比较与精读指南.html#PRO17)**<br>linyacool WebServer：本人SSP关联的网络工程与开发复盘 | 精读 | 非本方向 | `README.md`<br>`并发模型.md`<br>`WebServer/HttpData.cpp` | 主要是静态 HTTP 基础库练习，不能替代含数据库、缓存、一致性、业务约束的现代业务后端项目 |
| **[PRO18](argon_项目比较与精读指南.html#PRO18)**<br>Crony：Go分布式定时任务工程参考，未证作者SSP | 精读 | 选读 | `README.md`<br>`go.mod`<br>`common/pkg/etcdclient/registry.go` | 不是 SSP 成功案例、正式完整简历或 Agent 工程；不能用于补齐这些证据缺口 |
| **[PRO19](argon_项目比较与精读指南.html#PRO19)**<br>SchoolBus：本人面经直接关联的预约项目，附v1代码局限 | 精读 | 非本方向 | `README.md`<br>`school-bus/guns-order/src/main/java/com/stylefeng/guns/rest/modular/order/OrderServiceImpl.java` | 以上仅固定提交school-bus/下v1路径的静态观察；同仓另有school-bus-cloud版本，不把局部风险泛化为全版本结论 |
| **[PRO20](argon_项目比较与精读指南.html#PRO20)**<br>UltiCode：完整履历直接点名的本人判题平台 | 精读 | 选读 | `services/submission/src/main/java/com/ulticode/modules/queue/outbox/dispatcher/JudgeOutboxDispatcher.java`<br>`services/submission/src/main/java/com/ulticode/modules/submission/mapper/SubmissionMapper.java`<br>`services/auth/src/main/java/com/ulticode/auth/refreshtoken/service/RefreshTokenService.java` | 无本地构建/测试证据 |
| **[PRO21](argon_项目比较与精读指南.html#PRO21)**<br>ResiCache：完整履历直接点名的本人缓存扩展 | 精读 | 选读 | `src/main/java/io/github/davidhlp/spring/cache/redis/cache/SyncSupport.java`<br>`src/main/java/io/github/davidhlp/spring/cache/redis/cache/SyncRole.java`<br>`src/main/java/io/github/davidhlp/spring/cache/redis/cache/EarlyRefresh.java` | 无本地构建/测试证据 |
| **[PRO24](argon_项目比较与精读指南.html#PRO24)**<br>Sprout：任务树编排、预算与文本打分边界 | 选读 | 选读 | `sprout/task_tree.py`<br>`sprout/worker.py`<br>`sprout/llm.py` | benchmark文本特征分不代表功能正确；未复现任何模型效果 |
| **[PRO25](argon_项目比较与精读指南.html#PRO25)**<br>NoWorries：桌面记忆与跨平台隔离风险选读 | 选读 | 选读 | `noworries_app/apps/desktop/src/main/sandbox/macos-sandbox.ts`<br>`noworries_app/apps/desktop/src/main/sandbox/windows-sandbox.ts`<br>`noworries_app/apps/desktop/src/main/sandbox/workspace-manager.ts` | Windows/Linux环境重定向不是系统级隔离；macOS回退可能重复执行并降低隔离 |
| **[PRO22](argon_项目比较与精读指南.html#PRO22)**<br>Distributed Key-Value Store：课程框架上的Raft/MVCC实现 | 选读 | 非本方向 | `raft/raft.go`<br>`kv/server/server.go` | 未运行课程测试；未证明所有partition场景linearizability或独立实现比例；当前固定版本不自动代表2025腾讯投递时项目 |
| **[PRO23](argon_项目比较与精读指南.html#PRO23)**<br>QuantHarbor：多Agent状态与执行隔离风险对照 | 选读 | 待核 | `src/agents/base_agent.py`<br>`src/utils/code_executor_async.py`<br>`src_rag/core/report_pipeline.py` | 所谓sandbox没有在核读文件中建立进程/文件系统/网络权限隔离；不能据此称安全执行沙箱 |

