# 岗位技术要求分层与四类证据对照表

> **统计范围**：基于 **24 份**可比工程实习 JD 全文（后端 10、Agent 工程 11、混合 3），严格区分 **明确要求（硬门槛）**、**优先/加分项** 与 **工作职责**，并与候选人履历、99 份面经及 25 个项目源码交叉印证。
> - 更详细的图表与公司去重敏感性分析见：[岗位要求统计与解读.html](../02_招聘岗位资料/argon_岗位要求统计与解读.html)

---

## 一、核心结论：硬门槛 vs 加分项 vs 面试追问

### 1. 后端开发方向
- **一门主力服务端语言与计算机基础**：岗位允许 Java / Go / C++ 择一，重点考察并发模型、内存机制、网络协议与数据结构算法，不要求多语言全会。
- **数据库、缓存与消息队列**：MySQL、Redis 与 MQ 在多数岗位明确点名（部分岗位将数据库/KV 列为“有一定了解”或将 MQ 列为“优先项”）；面试必追问事务隔离、缓存并发回源（Single-Flight/锁）与消息幂等补偿（参考 [PRO19](argon_项目比较与精读指南.html#PRO19)、[PRO20](argon_项目比较与精读指南.html#PRO20)、[PRO21](argon_项目比较与精读指南.html#PRO21)）。
- **分布式架构与开源贡献**：高并发容灾、微服务治理与开源 PR 多为优先加分项或入职职责；可通过 [PRO09 ShenYu](argon_项目比较与精读指南.html#PRO09) 学习如何用高价值测试 PR 证明工程能力。

### 2. Agent 工程方向
- **服务端基础 + Agent/LLM 基本认知**：从基础语言与算法，到 RAG 检索、Prompt 与 Agent 框架原理；不同团队门槛跨度较大，需区分应用开发岗与底层 Runtime 岗（如 JD26）。
- **工具协议、异常恢复与自动化评测**：多出现在工作职责与高频面试追问中（参考 [CV30](../03_简历与候选人案例/argon_候选人与简历图册.html#CV30)、[CV31](../03_简历与候选人案例/argon_候选人与简历图册.html#CV31)、[INT84](../01_调研报告/argon_资料检索与证据详表.html#INT84)）；准备项目时重点打磨状态持久化、工具失败兜底与留出集回归评测（对照 [PRO04](argon_项目比较与精读指南.html#PRO04)、[PRO06](argon_项目比较与精读指南.html#PRO06)、[PRO24](argon_项目比较与精读指南.html#PRO24)、[PRO25](argon_项目比较与精读指南.html#PRO25)）。
- **训练微调与论文要求边界**：仅策略算法对照岗（JD15/16/28/29）将深度学习训练列为核心门槛；应用工程岗中 SFT/RL 多为了解或加分项。

---

## 二、11 项核心能力 × 四类证据对照表

| 能力编号与名称 | 核心考察问题 | 需证明的工程深度 | 常见准备误区（避坑） | 推荐精读项目 |
| :--- | :--- | :--- | :--- | :--- |
| **CAP01 · 语言、并发、操作系统与网络基础**<br><small>方向：通用</small> | Agent或业务项目之外，仍会问Go运行时、Java并发、网络IO和算法；如何解释具体实现和竞争条件？。 | 能从代码说明运行机制、资源与故障边界，而非只列组件。 | 把多种语言名当广度，或认为AI项目能替代基础。此项为研究归纳，不是拒绝原因统计。 | [PRO09](argon_项目比较与精读指南.html#PRO09)、[PRO10](argon_项目比较与精读指南.html#PRO10)、[PRO19](argon_项目比较与精读指南.html#PRO19) |
| **CAP02 · 数据库、业务状态与一致性**<br><small>方向：通用</small> | 积分兑换状态如何保持一致、库存约束如何保证，消息或请求失败后业务终态是什么？。 | 明确数据权威、事务边界、状态转移和重复操作的处理。 | 把一个Redis锁或MQ名称当作一致性证明；只测正常路径。 | [PRO01](argon_项目比较与精读指南.html#PRO01)、[PRO03](argon_项目比较与精读指南.html#PRO03)、[PRO08](argon_项目比较与精读指南.html#PRO08)、[PRO19](argon_项目比较与精读指南.html#PRO19) |
| **CAP03 · 缓存、索引与热点处理**<br><small>方向：通用</small> | 为什么采用某种Redis结构或两级缓存，失效与更新怎样处理，收益如何测量？。 | 按访问模式解释数据结构、索引、缓存收益和失效边界。 | 先堆缓存再找理由，或只报告吞吐量而没有基线、负载和一致性代价。 | [PRO02](argon_项目比较与精读指南.html#PRO02)、[PRO03](argon_项目比较与精读指南.html#PRO03)、[PRO19](argon_项目比较与精读指南.html#PRO19)、[PRO21](argon_项目比较与精读指南.html#PRO21) |
| **CAP04 · 消息可靠性、重试与幂等**<br><small>方向：通用</small> | MQ不可用如何兜底，中断后怎样重试，如何知道一次动作是否已经完成？。 | 区分消息传递、业务执行和真实终态；说明恢复与重复副作用的边界。 | 把先检查再执行当原子幂等，把模型输出完成当业务完成。 | [PRO01](argon_项目比较与精读指南.html#PRO01)、[PRO08](argon_项目比较与精读指南.html#PRO08)、[PRO11](argon_项目比较与精读指南.html#PRO11)、[PRO19](argon_项目比较与精读指南.html#PRO19) |
| **CAP05 · RPC、服务拆分与选型依据**<br><small>方向：通用</small> | 为什么用MQ而非HTTP、为什么拆成多个服务、选择RPC解决什么问题？。 | 从业务约束比较同步/异步调用和服务边界，说明收益与复杂度。 | 为了技术栈广度拆服务，或把RPC必然更快当作无条件结论。 | [PRO09](argon_项目比较与精读指南.html#PRO09)、[PRO19](argon_项目比较与精读指南.html#PRO19) |
| **CAP06 · 项目真实性、个人贡献与工程验证**<br><small>方向：通用</small> | 本人负责什么、难点怎样解决、是否真正测过、项目是否有实际使用者？。 | 把职责、变更、验证方法与局限讲清楚，区分框架、团队与本人工作。 | 把整个开源平台当个人作品，或复制他人的指标和实习经历。 | [PRO09](argon_项目比较与精读指南.html#PRO09)、[PRO11](argon_项目比较与精读指南.html#PRO11)、[PRO19](argon_项目比较与精读指南.html#PRO19)、[PRO24](argon_项目比较与精读指南.html#PRO24) |
| **CAP07 · Agent规划、工具调用与动态决策**<br><small>方向：通用</small> | Tool、Skill、MCP如何组织，为什么需要Agent，工具调用如何受约束？。 | 能解释决策循环、工具契约与编排取舍，展示超出一次API调用的实现。 | 把框架接通等同成熟Agent，或为名词增加多Agent。 | [PRO04](argon_项目比较与精读指南.html#PRO04)、[PRO11](argon_项目比较与精读指南.html#PRO11)、[PRO12](argon_项目比较与精读指南.html#PRO12)、[PRO24](argon_项目比较与精读指南.html#PRO24) |
| **CAP08 · RAG检索、数据处理与引用**<br><small>方向：通用</small> | 文档如何切分，混合检索/重排的增量是什么，Recall如何取得且避免过拟合？。 | 把语料、检索、引用与任务效果联系起来，比较简单基线和复杂组件。 | 把检索命中率当任务成功率，或将随手生成的问题同时用于调参与评测。 | [PRO04](argon_项目比较与精读指南.html#PRO04)、[PRO06](argon_项目比较与精读指南.html#PRO06)、[PRO07](argon_项目比较与精读指南.html#PRO07) |
| **CAP09 · 状态、上下文、记忆与异常恢复**<br><small>方向：通用</small> | 上下文过长如何处理，工具超时、进程重启或回滚后如何继续？。 | 区分对话记忆、任务状态与业务事实；说明恢复时的动作与权限检查。 | 内存状态当持久化，恢复后盲目重放写动作，或只保留聊天记录。 | [PRO05](argon_项目比较与精读指南.html#PRO05)、[PRO11](argon_项目比较与精读指南.html#PRO11)、[PRO12](argon_项目比较与精读指南.html#PRO12)、[PRO23](argon_项目比较与精读指南.html#PRO23) |
| **CAP10 · 权限、多租户与工具边界**<br><small>方向：通用</small> | 多租户和工具权限放在哪里校验，沙箱及写操作确认解决什么问题？。 | 把用户身份、对象权限、工具能力与执行环境分别说明。 | 仅靠提示词限制权限，或把接入MCP当成已有完整授权。 | [PRO10](argon_项目比较与精读指南.html#PRO10)、[PRO11](argon_项目比较与精读指南.html#PRO11)、[PRO23](argon_项目比较与精读指南.html#PRO23)、[PRO25](argon_项目比较与精读指南.html#PRO25) |
| **CAP11 · 评测、观测、成本与失败归因**<br><small>方向：通用</small> | 指标如何定义、实验是否真实执行，坏例和额外成本在哪里，为什么要增加某个组件？。 | 有基线、任务集、可追踪执行过程与明确评分依据，区分作者宣称和实际验证。 | 把模型自评当独立结果，忽略失败成本，用一次演示代替效果证据。 | [PRO04](argon_项目比较与精读指南.html#PRO04)、[PRO05](argon_项目比较与精读指南.html#PRO05)、[PRO06](argon_项目比较与精读指南.html#PRO06)、[PRO07](argon_项目比较与精读指南.html#PRO07) |

---

## 三、24 份可比工程 JD 逐条分层速查表

| JD 编号与岗位 | 公司与方向 | 明确要求（硬门槛） | 优先/加分项 | 工作职责要点 |
| :--- | :--- | :--- | :--- | :--- |
| **[JD01](https://www.nowcoder.com/jobs/detail/437499)**<br>抖音-27届-后端开发实习生 | 字节跳动/抖音平台产品<br>（后端） | 扎实编程；计算机原理；数据结构与算法；MySQL；Redis；消息队列 | 未单列 | 系统架构与性能优化 |
| **[JD02](https://www.nowcoder.com/jobs/detail/437835)**<br>后台开发-2027届暑期实习生 | 腾讯云智研发<br>（后端） | C/C++/Java/Go择一；TCP/UDP及网络编程；进程通信；数据结构与算法；操作系统；设计模式；数据库系统；网络安全 | Python/Shell/Perl了解；MySQL/SQL了解；NoSQL/KV原理了解；分布式系统；负载均衡；容灾与高可用 | 后台设计、开发、优化与运营 |
| **[JD03](https://mnowpick.nowcoder.com/m/detail/index?jobId=379097)**<br>暑期实习-Java研发工程师（供应链&IDC-天基） | 阿里云<br>（后端） | 熟练编程；数据结构与算法；数理基础 | 未单列 | 数据中心监控、能耗、智能运维 |
| **[JD04](https://www.nowcoder.com/jobs/detail/433220?urlSource=sitemap)**<br>软件研发工程师（实习） | 小米集团<br>（后端） | Go/C/C++/Java择一；Linux/Unix；设计开发测试发布流程 | Ruby/Python/Bash | DevOps、SRE、AIOps与站点稳定性 |
| **[JD05](https://talent.baidu.com/jobs/detail/INTERN/ef58d698-b944-4c05-86fe-e76daffecc8b)**<br>后端实习工程师（J93985） | 百度MEG<br>（后端） | Go或Java及相应框架；RPC；分布式缓存；MySQL及调优；SOA；数据结构；架构设计；面向对象 | AI技术与项目经验 | 妙笔与智能体业务可靠性、性能与扩展性 |
| **[JD06](https://www.shixiseng.com/intern/inn_5lxff4vehchx?pcm=pc_SearchList)**<br>服务端研发工程师（Golang） | 百度网盘/文库内容安全<br>（后端） | 至少一门后端语言；MySQL；Redis；MQ原理；数据结构；操作系统；网络 | Golang | 分布式性能与线上稳定性维护 |
| **[JD07](https://www.nowcoder.com/jobs/detail/463791)**<br>后端开发实习生-飞书项目 | 字节跳动/飞书项目<br>（后端） | 后端开发经验；Go/Java/Python择一；后端框架；协议；存储；缓存；系统设计；测试日志规范 | Golang | 高并发、系统解耦、技术调研 |
| **[JD08](https://www.nowcoder.com/jobs/detail/432128?urlSource=sitemap)**<br>AI Agent开发实习生-计算 | 字节跳动/基础设施计算<br>（Agent工程） | 数据结构与算法；C/C++/Python/Go/Java择一 | Agent开发；Agent框架；Agent Skills | 多Agent、记忆知识、鉴权观测、开发框架 |
| **[JD09](https://www.nowcoder.com/jobs/detail/432353)**<br>后端开发实习生-飞书（Agent/RAG） | 字节跳动/飞书<br>（Agent工程） | 后端开发经验；Go/Java/Python择一；系统设计；存储缓存协议；LLM应用架构；Agent/RAG/SFT基本认知；测试日志规范 | Golang；LLM应用工程；AI研发工具；校园/竞赛/开源实践 | 规划、工具、对话管理；RAG召回重排；Prompt版本、评测与监控 |
| **[JD10](https://talent.baidu.com/jobs/detail/INTERN/e3cec5b8-b7a3-4946-99fc-b292b749cd53)**<br>智能体应用开发实习生（J99649） | 百度ACG<br>（Agent工程） | 数据结构与算法；操作系统；网络；Python/Java/Go择一；RAG；Prompt工程；知识图谱概念；LangChain/LlamaIndex；Coze/Dify/AppBuilder/百炼任选 | PyTorch/TensorFlow/Paddle/DeepSpeed；AST/代码调用链/依赖分析；CodeAgent/AI Coding实践 | 代码结构知识、问题溯源、生成测试部署 |
| **[JD11](https://talent.baidu.com/jobs/detail/INTERN/ef30e579-2d3d-4539-ad90-884521b815c9)**<br>AI开放平台研发工程师实习生（J103363） | 百度安全与企业效率平台<br>（混合） | 数据结构与算法；操作系统；网络；数据库；Java/JVM/并发/集合；Spring/Spring Boot；RESTful；MySQL；Redis | 消息队列；Agent/RAG/Function Calling/MCP实践；LLM API/流式/Token计费；API网关/OAuth2/JWT/限流熔断/可观测；微服务/高并发/开源贡献 | 能力注册治理、模型路由、上下文、流式响应、鉴权配额 |
| **[JD12](https://www.nowcoder.com/feed/main/detail/22154e3d68ed481588263f61f5f616b4)**<br>阿里国际实习招聘（AI应用研发） | 阿里国际<br>（Agent工程） | Java/Python/JS等一种深入实践；数据结构算法；网络操作系统；LLM应用范式；Context/Prompt工程；工具调用；Agent框架；AI Coding经验 | RAG/多Agent/MCP/Skills落地；高质量开源/博客；vLLM/Ollama/延迟/KV cache理解；CV/NLP/SFT/RL经验 | 业务归因、反思纠错、自动评测回测、链路归因、异步与降级 |
| **[JD13](https://www.nowcoder.com/feed/main/detail/a6d09e3d6f1845ba990a59acc366aca2)**<br>Dev Agent后端开发实习（北京/27届） | 字节跳动/开发者服务<br>（Agent工程） | Go/Java/Python/C++择一；工程兴趣与逻辑能力 | 未单列 | 研发全链路；Prompt、知识工程、评测 |
| **[JD14](https://www.shixiseng.com/intern/inn_py1hkw0wds9o?pcm=pc_SearchList)**<br>Agent研发工程师（实习生） | 百度<br>（Agent工程） | Python/Go等一种语言；数据结构与算法；LLM/RAG/Function Call/任务规划认知；系统设计与抽象 | 框架/中间件设计落地 | 多Agent、任务调度、异常恢复；测试集与任务成功率 |
| **[JD20](https://www.nowcoder.com/jobs/detail/447232)**<br>字节跳动 后端工程师开发 实习 | 字节跳动<br>（后端） | Java/集合/IO/反射/泛型/JVM/类加载；线程池/锁/CAS/AQS/ThreadLocal/ConcurrentHashMap；Spring Boot/Cloud/MyBatis及微服务项目；MySQL/索引/事务/锁/执行计划/慢SQL/分库分表；Redis/缓存/分布式锁/限流；至少一种Kafka/RocketMQ/RabbitMQ，可靠性/幂等/重复消费；RESTful/接口设计/代码规范 | 高并发/高可用/分布式系统；跨境电商/支付/订单/库存/履约/营销经验 | 该页“岗位职责”部分实际也列学历与Java基础资格；按原文性质记录，不据栏目标题改写为工作经历 |
| **[JD21](https://www.nowcoder.com/jobs/detail/381180)**<br>腾讯云智研发 后台开发 2026届暑期实习生 | 腾讯云智研发<br>（后端） | 编程能力；C/C++/Java/Go；TCP/UDP/IPC编程；算法/OS/数据结构/数据库/软件工程/设计模式/网络安全 | 分布式/负载均衡/容灾/高可用；腾讯云资格或同等认证 | 服务后台架构设计、开发、优化与运营；网络接入、业务逻辑、存储和数据挖掘 |
| **[JD22](https://www.nowcoder.com/jobs/detail/447247)**<br>百度 大模型应用开发 后端开发工程师 实习生 | 百度<br>（混合） | Golang/Python（正文并列熟练掌握）；数据结构算法/计算机原理；数据库/缓存/消息中间件；Docker/Kubernetes及云原生高性能服务平台经验；单元测试/集成测试 | 未单列 | AI平台后端与系统架构、Agent/RAG/Workflow功能、性能调优、稳定性和版本维护 |
| **[JD23](https://www.nowcoder.com/jobs/detail/436118)**<br>淘天集团 AI Agent应用开发工程师 2026暑期实习 | 淘天集团<br>（Agent工程） | Python/Java/Go/C++等主语言；算法/数据结构；Agent系统实践与LangChain/LlamaIndex/AutoGen原理；高可用/可扩展Agent工程架构；Prompt/RAG/Tool Calling/Context Engineering；OpenAPI/RPC/MCP工具集成；了解PyTorch/TensorFlow | Transformer实战；数据工程；模型微调/后训练；模型评测 | 电商消费决策、商家运营多智能体、代码生成、运营及办公提效平台 |
| **[JD24](https://www.nowcoder.com/jobs/detail/441472)**<br>阿里云 AI Agent研发 基础平台研发工程师 暑期实习 | 阿里云<br>（Agent工程） | 计算机基础/主语言；数据库原理；Kubernetes/Serverless或Docker/gVisor安全隔离；LLM原理；至少一种Agent框架或RAG/工具/规划组件；Agent训练/评测/部署生命周期经验 | 数据库/分布式/云/AI应用项目；模型数据预处理/LoRA/Prefix Tuning等适配实践 | 多模态数据通道，获取解析结构化至上下文；意图规划工具调用；知识切片索引检索；文档模型后训练；分布式高可用。原文明确“一项或多项” |
| **[JD25](https://www.nowcoder.com/jobs/detail/454300)**<br>腾讯 微信 微信实习生招聘 Agent框架方向 | 腾讯<br>（Agent工程） | C++/Python至少一种；主流Agent开发框架实际经验与核心组件；Multi-Agent；MCP/A2A/FunctionCall；系统设计/模块化/高性能工程 | 未单列 | 分布式Agent框架、沙箱/云/消息/存储/账号基础设施，性能与一致性，算法落地与训练架构 |
| **[JD26](https://www.nowcoder.com/discuss/932616763089383424)**<br>腾讯云 Agent Runtime 校招与日常实习 | 腾讯云<br>（Agent工程） | Go/Rust/C/C++至少一种；数据结构/算法/OS；Linux/网络/进程/文件系统；Kubernetes/容器/分布式基础认知；Agent实践兴趣；使用Coding Agent并独立验证代码方案；日志/Trace/实验定位，问题定义至实现验证 | Kubernetes/Docker/containerd/Firecracker/Kata项目；Agent/Sandbox/Serverless；RL/Rollout/Harness/评测；开源/高质量本人项目；后端/中间件/Infra实习；ACM/ICPC/CTF获奖 | Agent生命周期、状态持久化、暂停恢复、弹性、工具网络；Sandbox快启/快照/隔离；跨应用、容器、MicroVM、网络存储调度定位生产问题 |
| **[JD27](https://www.nowcoder.com/jobs/detail/445785)**<br>美图 暑期实习 AI Agent研发实习生 | 美图<br>（Agent工程） | 主流语言至少一种/算法/数据结构；Agent系统与LangGraph/ADK/AgentScope原理；了解Claude Code机制/可扩展架构；Prompt/RAG/Tool Calling/Harness/Skills；能解释架构权衡和技术决策 | Agent生态实际PR；了解ML/DL框架与Transformer实战 | 记忆管理、复杂状态机、知识库检索；前后端接口；自动评测；监控与全链路可观测 |
| **[JD30](https://www.nowcoder.com/jobs/detail/442097)**<br>快手 留用实习 C++开发工程师 深圳 | 快手<br>（后端） | C/C++或Rust；数据结构/算法/计算机基础；面向对象/开发流程 | 实际项目/互联网实习；OI/ICPC | 后端平台研发、性能瓶颈、海量分布式处理/查询/数据一致性 |
| **[JD33](https://talent.baidu.com/jobs/detail/INTERN/15f123ac-2755-4324-b5ba-25682d0f9b40)**<br>百度 大模型应用后端研发实习生 GO/Python方向 J101073 | 百度<br>（混合） | 数据结构/算法；C/C++或PHP/Go（原文）；Windows/Unix/Linux原理及系统支持开发；问题分析/学习/协作 | 编程竞赛/论文/专利；项目/软件开发流程；搜索/ML/多媒体/GIS/云/分布式知识技能 | 核心产品功能架构，算法研究实现优化，前瞻跟踪与AI平台开发 |

---

## 四、代表性候选人案例的竞争力亮点与边界

> **SSP 归因准则**：可核的个人实现、问题取舍、测试与业务验证能够形成面试深挖材料；具体收益只在个案中观察；尚无相同招聘批次、岗位和背景下普通offer与SSP的可比较样本，不能把特定技术、论文、star或项目名称当SSP必要/充分条件。

- **[CV01](../03_简历与候选人案例/argon_候选人与简历图册.html#CV01)**（[原文链接](https://www.nowcoder.com/discuss/825498059369955328?toCommentId=22311081) · 2025秋招；另有2023.12—2024.07实习经历）：Go业务经历把投递、重试去重、索引和性能串起来；代码与性能条件未公开，不能复制自报数字。
- **[CV02](../03_简历与候选人案例/argon_候选人与简历图册.html#CV02)**（[原文链接](https://github.com/viego1999/JavaWxy) · 实习与秋招具体发生年份未确认）：本人项目、职责与同仓面经可对应；教学来源要说明，历史腾讯SSP不证明当前复刻相同项目的收益。
- **[CV05](../03_简历与候选人案例/argon_候选人与简历图册.html#CV05)**（[原文链接](https://github.com/erdengk) · 2023-12：快手、小红书商业化录用自述）：2022年两项合并测试PR有可核增量；2023录用与2026 Agent方向更新分开，其他贡献未审。
- **[CV10](../03_简历与候选人案例/argon_候选人与简历图册.html#CV10)**（[原文链接](https://www.nowcoder.com/discuss/353154880351182848) · 2018年求职；腾讯实习转正和阿里云校招分开）：2018求职文章直接链接三项本人系统项目；能研究领域问题深度，不能变成当前实习必做清单。
- **[CV17](../03_简历与候选人案例/argon_候选人与简历图册.html#CV17)**（[原文链接](https://juejin.cn/post/7461269186713321491) · 2024日常/暑期实习与秋招；具体轮次月日未核）：有多段实习和SSP结果自述，项目优化追问可参考；未定位本人仓库，2024秋招日期边界仍待核。
- **[CV09](../03_简历与候选人案例/argon_候选人与简历图册.html#CV09)**（[原文链接](https://www.nowcoder.com/feed/main/detail/9ecd5997a7d74f3fa885695032f32065?sourceSSR=dynamic&weFlow=true) · 2025-09-26：自述收到腾讯实习offer）：近期后台实习offer与具体面经可对应；个人项目只有描述，不能自动补成纯Agent SSP案例。
- **[CV23](../03_简历与候选人案例/argon_候选人与简历图册.html#CV23)**（[原文链接](https://zhh2001.github.io/resume) · 莉莉丝游戏 2026.03–2026.06；上海简文私募基金 2025.09–2026.03；网易游戏 2026.09–至今）：完整公开专业履历可对应实习主体、角色和时间，但项目实现与效果细节缺失；有完整履历不代表已能审查技术深度。
- **[CV24](../03_简历与候选人案例/argon_候选人与简历图册.html#CV24)**（[原文链接](https://huomalxq.github.io/resume/) · Philips 2026.03–2026.05；上海诺基亚贝尔 2023.09–2024.01）：Agent实习职责、问数链路和作者自列未完成项具体；源码、指标复现及与企业项目的精确对应仍未核，不称SSP。
- **[CV25](../03_简历与候选人案例/argon_候选人与简历图册.html#CV25)**（[原文链接](https://ac.nowcoder.com/discuss/1610772) · 2026-02-25立贴；2026年3月至4月暑期流程；蚂蚁4月13日offer）：2026蚂蚁智能体应用实习offer有明确时间线；RAG技术问题来自本人TikTok面经，不把两家公司的结果与问题串成同一场。
- **[CV28](../03_简历与候选人案例/argon_候选人与简历图册.html#CV28)**（[原文链接](https://davidhlp.github.io/about/) · 2026.01–2026.06）：完整履历直接链接本人OJ和缓存扩展，指定消息投递、条件写回、single-flight与测试可审；雇主博彦、客户阿里云分开，面经仅主题对应，不证明现版代码导致录用。
- **[CV03](../03_简历与候选人案例/argon_候选人与简历图册.html#CV03)**（[原文链接](https://www.nowcoder.com/discuss/832657601983688704) · 2025年3—4月暑期招聘；5—8月美团实习；8月下旬意向，10月底美团SSP；9—11月其他秋招结果）：原文直接明确2025美团暑期后同公司SSP；外部校招另列，京东SSP/网易SP为作者推定，华为15a不换算。具体项目源码和岗位职称仍缺。
- **[CV30](../03_简历与候选人案例/argon_候选人与简历图册.html#CV30)**（[原文链接](https://andrewtheterp.com/) · ByteDance (TikTok Shop) 2026.05–2026.08；ByteDance (TikTok Shop) 2025.05–2025.08）：完整公开CV明确2026字节Creator Assistant后端实习，写到MCP工具、真实对话评测和trace；仍为本人职责自述，企业内部源码、本人面经与SSP未披露。
- **[CV29](../03_简历与候选人案例/argon_候选人与简历图册.html#CV29)**（[原文链接](https://shufengc.dev/) · Tencent · Cloud Computing Group 2025.07–2025.08；Stripe · Cash & Banking Infrastructure 2026.05–2026.08）：腾讯2025/Stripe2026实习主页直接链接两项源码；TinyKV继承课程框架，QuantHarbor入口和执行隔离有静态风险，不能用大厂经历替项目成熟度背书。
- **[CV31](../03_简历与候选人案例/argon_候选人与简历图册.html#CV31)**（[原文链接](https://imyihang.com/) · 中科曙光Agent开发实习2025.12–2026.02；AI产品实习另列）：近期中科曙光Agent实习完整CV直接链接NoWorries；本人主页另链Sprout及合并PR。可研究编排、记忆与权限，但文本打分、预算和沙箱降级存在静态风险；非互联网大厂SSP，未运行。

