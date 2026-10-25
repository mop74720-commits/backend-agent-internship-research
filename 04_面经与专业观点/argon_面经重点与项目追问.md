# 面经重点与项目追问指南

> **核心阅读提示**：
> - **样本范围**：共核读 **99 份**面经材料（全文 92、部分 7），含 **14 份**严格近期（2025–2026）工程实习面经、1 份 AI Infra 对照及 48 份未标事件年的明确实习面经。
> - **口径说明**：面经提问为作者回忆要点转述（非逐字录音）；“建议准备深度”为本报告归纳的自查标准，不代表原作者现场答出；项目与面经按技术主题对照，仅标有候选人编号的项目为候选人本人项目。

---

## 一、后端实习面试：五大核心追问簇

### B1 · 先讲业务约束和本人职责，再讲技术栈
- **核心结论**：能解释为什么需要这些模块、自己负责哪段链路，比把组件名写满更能承接后续追问。
- **高频追问切入点**：需求、使用者、数据与请求链路；自己负责和复用的范围；业务字段、数据访问方式与选型之间的关系；替代方案的代价。
- **建议准备深度**：
  - 画出一条真实请求或数据流，明确入口、状态、依赖和自己的改动。
  - 挑一个具体业务约束，说明选择、备选方案与未解决的问题。
  - 对个人实现、团队部分、框架代码分别给出证据。
- **代表性原题与来源**：
  - [INT12 27双非本—腾讯IEG游戏安全后台实习面经](https://www.nowcoder.com/feed/main/detail/9ecd5997a7d74f3fa885695032f32065?sourceSSR=dynamic&weFlow=true)（近期工程实习 · 2025-09-26 offer；2025-10-04复盘）：K8S与Casbin RBAC实习做了什么？。
  - [INT24 26届快手暑期实习（已OC）](https://www.nowcoder.com/feed/main/detail/8c1a63e46e4e462892474e405d611028)（近期工程实习 · 2025-03-24/03-31技术面；04-15 HR；4月下旬offer）：实习中POI表保存了哪些字段，如何限定中心点附近的结果？。
  - [INT28 26届后端实习-蚂蚁集团后端开发一面面经](https://www.nowcoder.com/feed/main/detail/bb4c92b4084f44e69388ac342c1ca809?sourceSSR=users)（近期工程实习 · 2025-03-17面试）：研究生阶段在实验室实际做了什么、如何说明自己的贡献？；为什么目前项目方向没有选择AI？。
- **对照精读项目**：[PRO19](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO19)、[PRO09](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO09)、[PRO20](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO20)

### B2 · 数据库与缓存准备到访问路径和并发边界
- **核心结论**：SQL、索引、Redis结构和缓存策略会接着项目中的实际查询继续问，单独背定义覆盖不了这些问题。
- **高频追问切入点**：SQL实际读取了什么、为什么命中或失去索引、容量与B+树层级估算；GEO、ZSet等结构适配什么查询；缓存击穿、更新和多实例边界。
- **建议准备深度**：
  - 针对一条具体查询说明索引、回表、排序和数据规模，能做数量级估算。
  - 解释一个缓存更新与失效流程，指出并发回源、过期和失败时的结果。
  - 用可审查测试或复现实验区别“本机合并回源”和“跨实例互斥”。
- **代表性原题与来源**：
  - [INT20 阿里云Java研发实习 - 一面](https://www.nowcoder.com/discuss/743798386737897472?sourceSSR=dynamic)（近期工程实习 · 2025-04-21一面）：项目数据库访问做过哪些优化，去掉SELECT *为何能改善查询？。
  - [INT24 26届快手暑期实习（已OC）](https://www.nowcoder.com/feed/main/detail/8c1a63e46e4e462892474e405d611028)（近期工程实习 · 2025-03-24/03-31技术面；04-15 HR；4月下旬offer）：实习中POI表保存了哪些字段，如何限定中心点附近的结果？；使用GEO查询时，其底层如何组织和查找坐标？；Hash与跳表为何适合相应数据，为什么没有选择其他树结构？。
  - [INT101 快手商业化垂直业务 Java日常实习](https://www.nowcoder.com/discuss/726371483039133696)（近期工程实习 · 2025-02-25投递、2025-02-26一面）：订单水平分片不按商家路由查询时怎么办？；千万行数据的B+树高度怎样估计，何时不适合建索引？；Redis结构、缓存击穿怎样处理？。
- **对照精读项目**：[PRO21](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO21)、[PRO20](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO20)

### B3 · 消息和事务的重点是失败窗口
- **核心结论**：顺序消息、异步编排与幂等要结合业务约束解释；引入MQ后，仍需交代重复投递、事务提交和补偿失败。
- **高频追问切入点**：为什么要MQ、是否要求顺序、吞吐与并行度会损失什么；数据库提交、投递与确认之间宕机；重复消费与转账事务边界。
- **建议准备深度**：
  - 按时间线推演提交前、提交后未投递、已投递未确认三个失败位置。
  - 说明业务幂等键、状态转换、重试/补偿与对账各自处理什么问题。
  - 能在代码中指出事务边界与条件更新，不凭框架注解宣称端到端exactly-once。
- **代表性原题与来源**：
  - [INT22 四非本 滴滴-后端实习面经(已OC)](https://www.nowcoder.com/feed/main/detail/c822bd1fffa64addb718e806090a20ee?toCommentId=21427551)（近期工程实习 · 2025-03-21/03-25面试；03-28正式offer）：采用RocketMQ顺序消息解决了什么需求，同时损失什么能力？；如何把服务同步编排改成CompletableFuture，怎样设计充值和转账的事务边界？。
  - [INT85 爱橙科技Java暑期实习一面：MQ、测试幂等及高可用追问](https://www.nowcoder.com/discuss/730542760465276928)（近期工程实习 · 2025-03-14一面约50分钟，2025-03-15作者看到未通过）：MQbus向RPC等组件推广时，环境隔离可能遇到什么问题；测试框架如何设计，非幂等的数据新增操作如何清理，测试覆盖标准如何确定。
  - [INT40 智能体与大模型应用工程实习 一面](https://www.nowcoder.com/discuss/894720138258173952?sourceSSR=post)（明确实习；事件年未知 · 06-09面试，年未显示）：异步订单怎样在个人环境验证；重复投递、删集合时宕机如何收尾？。
- **对照精读项目**：[PRO20](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO20)、[PRO19](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO19)

### B4 · 语言、系统基础与现场编码仍要独立准备
- **核心结论**：有项目或Agent经历的实习者仍遇到JVM、锁、网络、Redis底层和手写算法；基础与项目需要连着解释。
- **高频追问切入点**：实际使用的JDK/GC、同步方式、网络与多实例会话；跳表操作、事务原子性、统计结构误差；现场题及边界用例。
- **建议准备深度**：
  - 用项目中的一个并发点解释锁保护什么、生命周期和争用代价。
  - 沿网络请求或登录流程说清状态保存与故障位置。
  - 现场完成典型数组、链表、树或DP题，说明复杂度和边界用例。
- **代表性原题与来源**：
  - [INT91 快手商业化 Java日常实习](https://www.nowcoder.com/discuss/719242991700889600)（近期工程实习 · 2024-11-05面试，11-06时间线标挂）：JVM结构、HashMap旧版本扩容和AQS怎样说明？；项目中何时使用synchronized和ReentrantLock？；为什么要Redis缓存、网关和分布式Session？；手写两数之和。
  - [INT93 字节生活服务后端开发日常实习一二三面经](https://www.nowcoder.com/feed/main/detail/f38ea39b741e44be8730c1e7f7d88439?sourceSSR=dynamic)（近期工程实习 · 多轮技术面与HR后，2025-03-05收到正式offer；各技术面具体日期未给）：为什么选择JDK17，了解其GC和ZooKeeper分布式协议吗？；ZSet跳表如何插入、删除和排序？；扫码登录完整链路怎样实现？；网站UV/DAU如何统计，选用结构有什么误差？；现场解树子结构、三数之和及变式、LCS、接雨水等。
  - [INT10 腾讯日常实习一面面经（2027暑期向）](https://www.nowcoder.com/feed/main/detail/37c64318e134459bbd9a5c7953e99aea?sourceSSR=post)（近期工程实习 · 2026-03-10面试）：Redis主从、哨兵、集群在项目中怎样选？；大数字符串转换的现场编码。
- **对照精读项目**：[PRO21](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO21)、[PRO09](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO09)

### B5 · 排障与测试要能验证自己声称的能力
- **核心结论**：追问不仅是“怎么设计”，还包括OOM、消息积压、测试清理和覆盖标准。准备时应把验证方法和结果边界一起讲。
- **高频追问切入点**：OOM/高CPU、消息堆积、分片查询的定位顺序；非幂等测试数据如何清理，异常、超时和竞争条件如何覆盖。
- **建议准备深度**：
  - 区分现象、假设、采集证据与验证步骤，避免看到慢就直接加缓存或扩容。
  - 为关键机制提出正常、重复、异常和中断用例，并解释断言。
  - 明确哪些测试已运行、哪些只是源码存在；作者模板不能替代自己的排障经历。
- **代表性原题与来源**：
  - [INT85 爱橙科技Java暑期实习一面：MQ、测试幂等及高可用追问](https://www.nowcoder.com/discuss/730542760465276928)（近期工程实习 · 2025-03-14一面约50分钟，2025-03-15作者看到未通过）：如何排查OOM，以及如何判断消费者积压或处理缓慢的程度；测试框架如何设计，非幂等的数据新增操作如何清理，测试覆盖标准如何确定；为字符串形式的整数求和函数设计测试用例；另一个算法服务项目如何保证高可用，熔断和限流如何实现。
  - [INT101 快手商业化垂直业务 Java日常实习](https://www.nowcoder.com/discuss/726371483039133696)（近期工程实习 · 2025-02-25投递、2025-02-26一面）：OOM怎样定位处理，消息分区术语是否准确？；订单水平分片不按商家路由查询时怎么办？。
  - [INT81 从一面到二面：Java后端实习面试复盘（原版两轮，含事后模板）](https://raw.githubusercontent.com/DavidHLP/DavidHLP.github.io/6f3d114a6ef9eb08b730f5f4740afe5b7d22d426/src/content/note/zh-cn/java-internship-interview-blog-polished.md)（明确实习；事件年未知 · 事件年月日未知）：高CPU如何定位进程、线程和调用链。
- **对照精读项目**：[PRO20](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO20)、[PRO21](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO21)、[PRO09](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO09)

---

## 二、Agent 工程实习面试：五大核心追问簇

### A1 · 先证明任务和编排的必要性
- **核心结论**：Agent项目要回答服务谁、完成什么任务、为什么采用这套编排，以及本人贡献；多Agent数量本身无法说明收益。
- **高频追问切入点**：真实用户与工作流；实习或项目的具体产出；单Agent、多Agent、固定Workflow和自研框架的取舍。
- **建议准备深度**：
  - 给出任务输入、预期输出、成功与失败条件，画出状态和工具流。
  - 解释拆分角色/步骤的理由，并列出更简单基线供比较。
  - 定位自己的改动，说明沿用框架与未落地功能。
- **代表性原题与来源**：
  - [INT47 小红书大模型平台 Agentic 全栈研发练习生 一面凉经](https://www.nowcoder.com/feed/main/detail/e5e9311a623940eead6ec98c65e7f9e8?sourceSSR=search)（近期工程实习 · 2026-08-06面试）：项目解决谁的研发问题，写操作边界与Harness职责如何划分？；如何从SQLite原型扩到数千用户；自研编排与LangGraph图结构怎样解释？。
  - [INT68 华为AI应用实习：专业面、主管面与offer时间线](https://www.nowcoder.com/discuss/884479038142586880)（近期工程实习 · 2026-05-14专业面及主管面，05-15沟通杭州，05-25收到offer自述；原面经另记03-31注册，关联总表华为行记2026-04-01投递。）：实习负责哪些模块、产出是什么，项目各阶段做了什么？；科研/项目困难如何分析和解决，在团队中是主导还是配合？。
  - [INT17 8.25 小红书实习 AI全栈开发实习一面挂凉经](https://www.nowcoder.com/feed/main/detail/c712eda7fbf44ba69835b6dd2ff7fc4c?sourceSSR=dynamic)（明确实习；事件年未知 · 08-25面试；年未显示）：为什么必须多Agent，如何编排？；系统如何评测，同事有没有准确率反馈？。
- **对照精读项目**：[PRO04](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO04)、[PRO24](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO24)

### A2 · RAG与效果指标要能回到数据和对照
- **核心结论**：切块、检索、幻觉和任务评测要能说明测什么、如何比较。当前深入提问的部分来源事件年未知，作为高相关选读保留。
- **高频追问切入点**：RAG与直接文件检索、关键词与向量召回、query和chunk粒度的取舍；Recall@k与端到端成功率分别测什么，如何找到剩余错误并避免过拟合。
- **建议准备深度**：
  - 说明语料、测试集构成和标注/判定依据，把检索质量与答案质量分开。
  - 固定一套基线和对照条件，检查失败样本，而非只展示几条成功回答。
  - 若用模型裁判，说明人工抽查、裁判偏差及成本；不把文本特征分当任务正确率。
- **代表性原题与来源**：
  - [INT42 26.4百度大模型生态集成实习，新鲜面经~](https://www.nowcoder.com/feed/main/detail/62d4ca9866d84d63bf6eafbb0a947bb8?sourceSSR=search)（近期工程实习 · 2026-04实习面试）：怎样组织工具调用、检索策略、向量相似度与设计模式？。
  - [INT01 字节跳动-Agent开发实习生 一面（45分钟）](https://www.nowcoder.com/feed/main/detail/931a8a935a5e4b4f8d0b71cd4e818604)（明确实习；事件年未知 · 面试日期未标明（页面06-04））：检索为何选择ES，替换为向量检索损益是什么？；Recall@5怎样测出，如何避免评测过拟合？。
  - [INT104 美团Agent开发一面 日常](https://api-cdn.nowcoder.com/feed/main/detail/58159306df52463ab75d72daa80d66df?sourceSSR=subject)（明确实习；事件年未知 · 一面约75分钟，年月日未知）：为什么用RAG而不让Agent直接grep原文/代码，忽略token时各有什么损益？；无标题Markdown怎样切块，短query与长chunk如何比较并做对照？；关键词与向量召回如何互补，长query如何处理？；怎样判断幻觉，如何识别剩余1%到2%的错误？。
  - [INT103 实习面经分享 阿里云AI应用开发一面](https://www.nowcoder.com/feed/main/detail/775b45a6884f4688bc1e24ad8023183b)（明确实习；事件年未知 · 一面年月日未知；astra卡片页面05-05无年份）：Agent系统如何评价，实习遇到的问题如何解决？；幻觉如何处理？。
- **对照精读项目**：[PRO06](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO06)、[PRO24](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO24)

### A3 · 工具调用准备到可观察状态与中断续跑
- **核心结论**：需要说明工具如何接入、执行过程是否可见，以及超时、中断、重试和知识更新怎样影响状态；会调用API只是链路的一环。
- **高频追问切入点**：Skill/Tool/MCP如何接入现有项目；工具执行器及日志怎样定位卡点；任务中断后的恢复点、重试时机、知识库持续更新与副作用。
- **建议准备深度**：
  - 沿一次工具调用解释参数、执行结果、错误与下一状态，能查看执行日志。
  - 列出进程中断、工具超时和外部操作已成功但响应丢失的恢复策略。
  - 区别内存重试、持久化恢复和业务幂等，指出项目实际实现到哪一层。
- **代表性原题与来源**：
  - [INT42 26.4百度大模型生态集成实习，新鲜面经~](https://www.nowcoder.com/feed/main/detail/62d4ca9866d84d63bf6eafbb0a947bb8?sourceSSR=search)（近期工程实习 · 2026-04实习面试）：接到已有大项目的新功能需求，如何规划并开发Agent Skill？；怎样组织工具调用、检索策略、向量相似度与设计模式？。
  - [INT84 9.7百度agent开发日常实习面经](https://www.nowcoder.com/feed/main/detail/bb8c28105f364770b57ff5eb5649cc60)（明确实习；事件年未知 · 标题为9.7；正文称15点刚面完，面试约45分钟；未直接写事件年）：工具层兜底具体覆盖什么失败；工具执行器的具体实现；任务中断后，下次如何继续执行；如何感知Agent当前执行动作，是否呈黑盒；如何通过日志定位Agent卡点。
  - [INT41 腾讯实习 ai应用开发后端面经分享](https://www.nowcoder.com/feed/main/detail/144c6ae334b24c0aa643ed43ccfebaac?sourceSSR=dynamic)（明确实习；事件年未知 · 面试年月日未确认（页面04-23））：中断后怎么安全重试；跨境汇款任务超时怎样保护资金状态？；知识库在持续提供服务时如何更新？。
- **对照精读项目**：[PRO04](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO04)、[PRO20](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO20)、[PRO25](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO25)

### A4 · 写操作、隔离与协作冲突必须有明确边界
- **核心结论**：能执行文件或业务操作之后，权限、回滚与并发冲突就成为工程问题。用户确认、工作目录设置和安全隔离需要分别说明。
- **高频追问切入点**：写操作边界，沙箱/快照/回滚时机；多Agent同时改文件、超时后重复执行、资金等有副作用任务的保护。
- **建议准备深度**：
  - 对读、写、网络及敏感工具说明服务端检查位置，不能只依赖模型提示或UI确认。
  - 区分进程环境设置、文件路径校验和系统级隔离，明确平台差异。
  - 解释冲突检测、审批、幂等与补偿的责任；从失败路径验证，不只跑成功演示。
- **代表性原题与来源**：
  - [INT47 小红书大模型平台 Agentic 全栈研发练习生 一面凉经](https://www.nowcoder.com/feed/main/detail/e5e9311a623940eead6ec98c65e7f9e8?sourceSSR=search)（近期工程实习 · 2026-08-06面试）：项目解决谁的研发问题，写操作边界与Harness职责如何划分？。
  - [INT03 字节agent开发实习生一面面经 29届](https://www.nowcoder.com/feed/main/detail/617d30ab75dc40db81b291b8b98dfb13)（明确实习；事件年未知 · 面试日期未标明（页面08-05））：为何使用沙箱，快照及回滚时机怎样选择？。
  - [INT102 字节AI Agent实习面经](https://www.nowcoder.com/feed/main/detail/8a553bb6ea8445d0b0abe11e87614cea?sourceSSR=%E5%85%B6%E4%BB%96)（明确实习；事件年未知 · 08-13一面、08-16二面，年份未知）：多个Agent同时修改同一文件怎样避免冲突？。
  - [INT41 腾讯实习 ai应用开发后端面经分享](https://www.nowcoder.com/feed/main/detail/144c6ae334b24c0aa643ed43ccfebaac?sourceSSR=dynamic)（明确实习；事件年未知 · 面试年月日未确认（页面04-23））：中断后怎么安全重试；跨境汇款任务超时怎样保护资金状态？。
- **对照精读项目**：[PRO25](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO25)、[PRO04](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO04)、[PRO20](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO20)

### A5 · 上下文与成本优化要连着服务基础解释
- **核心结论**：上下文压缩、Memory、缓存和模型分工需要交代保留什么、牺牲什么；Agent岗位也会继续考调度、网络与现场编码。
- **高频追问切入点**：压缩后保留用户约束、长期记忆提取、工具返回过长与Prompt Cache；并发任务资源上限、线程/协程区别、基础协议与算法。
- **建议准备深度**：
  - 说明上下文保留与丢弃规则，用失败样本检查关键约束是否丢失。
  - 拆开输入/输出token、重试、并发和时延；区分事后计费统计与调用前硬限额。
  - 能解释自己使用的语言和并发模型，并现场实现基础题；不能以Agent术语代替这些能力。
- **代表性原题与来源**：
  - [INT102 字节AI Agent实习面经](https://www.nowcoder.com/feed/main/detail/8a553bb6ea8445d0b0abe11e87614cea?sourceSSR=%E5%85%B6%E4%BB%96)（明确实习；事件年未知 · 08-13一面、08-16二面，年份未知）：上下文压缩保留什么，如何防止丢失用户关键约束？；路径震荡怎样定位，长期Memory如何提取存储检索？；工具过多或返回过长时如何控制上下文？；Prompt Cache怎样提升命中，小模型如何分工？；现场判断平衡二叉树。
  - [INT104 美团Agent开发一面 日常](https://api-cdn.nowcoder.com/feed/main/detail/58159306df52463ab75d72daa80d66df?sourceSSR=subject)（明确实习；事件年未知 · 一面约75分钟，年月日未知）：三万个协程和三万个线程在8核16线程机器上调度有何不同？；现场实现链表合并与最长有效括号。
  - [INT12 27双非本—腾讯IEG游戏安全后台实习面经](https://www.nowcoder.com/feed/main/detail/9ecd5997a7d74f3fa885695032f32065?sourceSSR=dynamic&weFlow=true)（近期工程实习 · 2025-09-26 offer；2025-10-04复盘）：Go调度、网络IO、Raft、LSM分别是什么？；Agent与模型、LangChain与LangGraph、Function Call与MCP怎样区分？。
- **对照精读项目**：[PRO24](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO24)、[PRO25](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO25)、[PRO06](../06_项目分析与推荐/argon_项目比较与精读指南.html#PRO06)

---

## 三、八个重点项目：精读模块与避坑清单

### PRO09 · Apache ShenYu：插件链、响应式网关与可测试开源贡献（后端／开源贡献）
- **核心学习目标**：学插件链、响应式生命周期和一项可核查贡献怎样配测试；优先看本人两项测试PR，再读平台实现。
- **候选人归属与结果边界**：CV05：仅确认PR3848(OAuth2集成测试)、3672(logging-rocketmq集成测试)由erdengk提交并于2022合并；未审其余PR。
- **推荐精读源码模块**：
  - [2022本人OAuth2测试](https://github.com/apache/shenyu/blob/e63d4b366d0d0eb2c7cea87e4b4cf0c711645bcd/shenyu-integrated-test/shenyu-integrated-test-https/src/test/java/org/apache/shenyu/integrated/test/https/Oauth2PluginTest.java#L38) (`shenyu-integrated-test/shenyu-integrated-test-https/src/test/java/org/apache/shenyu/integrated/test/https/Oauth2PluginTest.java`)：只核该测试文件及作者/合并关系。
  - [2022本人RocketMQ日志测试](https://github.com/apache/shenyu/blob/55f3147ea54e0963cfed14b1edcb7c8545520ad0/shenyu-integrated-test/shenyu-integrated-test-http/src/test/java/org/apache/shenyu/integrated/test/http/combination/RocketMqPluginTest.java#L54) (`shenyu-integrated-test/shenyu-integrated-test-http/src/test/java/org/apache/shenyu/integrated/test/http/combination/RocketMqPluginTest.java`)：只核该测试文件及作者/合并关系。
  - [限流插件及单测](https://github.com/apache/shenyu/blob/34f2ed036747936a5e28aea2c94cd9b3cddcce47/shenyu-plugin/shenyu-plugin-fault-tolerance/shenyu-plugin-ratelimiter/src/main/java/org/apache/shenyu/plugin/ratelimiter/RateLimiterPlugin.java) (`shenyu-plugin/shenyu-plugin-fault-tolerance/shenyu-plugin-ratelimiter/src/main/java/org/apache/shenyu/plugin/ratelimiter/RateLimiterPlugin.java`)：读插件链如何返回放行/限流与测试覆盖。
- **静态核查短板与勿照搬项**：
  - Redis限流单测使用mock，不能证明集群故障或吞吐。
  - 2026平台版本与2022本人PR、2023录用自述分开。
  - **切勿照搬**：不把运行整个平台或当前Agent Gateway功能写成本人当年贡献。

### PRO19 · SchoolBus：本人面经直接关联的预约项目，附v1代码局限（后端／本人面经直连项目）
- **核心学习目标**：学同一业务如何被字节、京东追问，并把预约、支付、取消与补偿落实到源码失败窗口。
- **候选人归属与结果边界**：CV21：本人字节和京东面经直接提班车项目，根README标明作者与项目；京东offer、字节意向书分开。
- **推荐精读源码模块**：
  - [下单与补偿](https://github.com/DreamCats/school-bus/blob/fc50ea8b19f99b4b15b2012048ea4651d896dd94/school-bus/guns-order/src/main/java/com/stylefeng/guns/rest/modular/order/OrderServiceImpl.java) (`school-bus/guns-order/src/main/java/com/stylefeng/guns/rest/modular/order/OrderServiceImpl.java`)：按下单、支付竞争及补偿失败逐段读。
  - [取消消息消费](https://github.com/DreamCats/school-bus/blob/fc50ea8b19f99b4b15b2012048ea4651d896dd94/school-bus/guns-bus/src/main/java/com/stylefeng/guns/rest/modular/bus/mq/OrderSeatsCancleListener.java) (`school-bus/guns-bus/src/main/java/com/stylefeng/guns/rest/modular/bus/mq/OrderSeatsCancleListener.java`)：读标记检查和业务操作之间的竞争窗口。
- **静态核查短板与勿照搬项**：
  - 所读v1补偿消息失败仅打印；单例可变tag存在并发覆盖静态风险。
  - 取消消费查标记→业务→写标记，不能据此认定并发幂等；其他版本未泛化。
  - **切勿照搬**：不照搬高性能/高可用口号，不把Guns框架和团队全部工作算个人原创。

### PRO20 · UltiCode：完整履历直接点名的本人判题平台（后端／本人履历直连项目）
- **核心学习目标**：学提交、Outbox、Redis投递、租约与结果竞争的组合机制；适合练消息可靠性和业务状态转换。
- **候选人归属与结果边界**：CV28：完整履历直接链接本人UltiCode，指定实现与测试可读；本人面经仅主题对应。
- **推荐精读源码模块**：
  - [提交事务入口](https://github.com/DavidHLP/UltiCode/blob/d53b582e2fae32ef644642651086df0e5ed3163d/services/submission/src/main/java/com/ulticode/modules/submission/port/DefaultSubmissionWritePort.java) (`services/submission/src/main/java/com/ulticode/modules/submission/port/DefaultSubmissionWritePort.java`)：读提交与Outbox在何条件下同事务。
  - [Outbox投递](https://github.com/DavidHLP/UltiCode/blob/d53b582e2fae32ef644642651086df0e5ed3163d/services/submission/src/main/java/com/ulticode/modules/queue/outbox/dispatcher/JudgeOutboxDispatcher.java) (`services/submission/src/main/java/com/ulticode/modules/queue/outbox/dispatcher/JudgeOutboxDispatcher.java`)：读投递、退避与崩溃重复窗口。
  - [结果条件更新](https://github.com/DavidHLP/UltiCode/blob/d53b582e2fae32ef644642651086df0e5ed3163d/services/submission/src/main/java/com/ulticode/modules/submission/mapper/SubmissionMapper.java) (`services/submission/src/main/java/com/ulticode/modules/submission/mapper/SubmissionMapper.java`)：读generation/attempt约束与租约恢复。
  - [Streams集成测试](https://github.com/DavidHLP/UltiCode/blob/d53b582e2fae32ef644642651086df0e5ed3163d/services/judge-runtime/src/test/java/com/ulticode/modules/queue/port/adapter/JudgeStreamRedisIntegrationTest.java) (`services/judge-runtime/src/test/java/com/ulticode/modules/queue/port/adapter/JudgeStreamRedisIntegrationTest.java`)：读断言，注意测试未执行。
- **静态核查短板与勿照搬项**：
  - Outbox依特性开关及mapper，数据库事务不跨Redis投递；重复、死信与幂等全链路仍需核。
  - 当前源码晚于实习，集成测试未运行；不能证明投递版本或录用因果。
  - **切勿照搬**：不把Outbox模式名当端到端exactly-once；旧面经Kafka答案也不能贴给现版Redis Streams。

### PRO21 · ResiCache：完整履历直接点名的本人缓存扩展（后端／本人履历直连项目）
- **核心学习目标**：学single-flight、Future共享、重入/异常/超时清理和按版本CAS更新TTL，适合把缓存问到具体并发代码。
- **候选人归属与结果边界**：CV28：完整履历直接链接本人ResiCache，指定实现与测试可读；本人面经仅主题对应。
- **推荐精读源码模块**：
  - [并发角色](https://github.com/DavidHLP/ResiCache/blob/1ed3be36af0795a363d624d38de676c0d00b4cf7/src/main/java/io/github/davidhlp/spring/cache/redis/cache/SyncRole.java) (`src/main/java/io/github/davidhlp/spring/cache/redis/cache/SyncRole.java`)：读leader选择、共享Future与身份匹配清理。
  - [提前刷新](https://github.com/DavidHLP/ResiCache/blob/1ed3be36af0795a363d624d38de676c0d00b4cf7/src/main/java/io/github/davidhlp/spring/cache/redis/cache/EarlyRefresh.java) (`src/main/java/io/github/davidhlp/spring/cache/redis/cache/EarlyRefresh.java`)：读缓存值版本CAS与TTL变化。
  - [并发测试](https://github.com/DavidHLP/ResiCache/blob/1ed3be36af0795a363d624d38de676c0d00b4cf7/src/test/java/io/github/davidhlp/spring/cache/redis/cache/SyncSupportSingleFlightTest.java) (`src/test/java/io/github/davidhlp/spring/cache/redis/cache/SyncSupportSingleFlightTest.java`)：读异常、重入和follower超时测试。
- **静态核查短板与勿照搬项**：
  - 本地Map选leader不是分布式唯一回源。
  - 竞态测试代码可读但未执行；逐提交个人和AI辅助比例未核。
  - **切勿照搬**：不因使用Redis就宣称跨节点一致；不能复制作者效果数字或把后期代码当投递版本。

### PRO04 · Ragent：Java Agent与RAG全链路参考（Agent／Java工程参考）
- **核心学习目标**：学Workflow/Agent、状态存储与工具确认的分层；作为Java实现参照，不作为已获岗者项目证据。
- **候选人归属与结果边界**：工程参照：仅用于面经/JD能力主题对照，未核成功候选人本人求职项目或具体贡献；不凭同账号或star建立关系。
- **推荐精读源码模块**：
  - [引擎配置](https://github.com/nageoffer/ragent/blob/ff93871ab88fff24a5dac7feee7ea342359a3439/agent/src/main/java/com/nageoffer/ai/ragent/agent/config/AgentEngineConfiguration.java) (`agent/src/main/java/com/nageoffer/ai/ragent/agent/config/AgentEngineConfiguration.java`)：沿配置看状态、工具与执行机制接线。
  - [状态存储](https://github.com/nageoffer/ragent/blob/ff93871ab88fff24a5dac7feee7ea342359a3439/agent/src/main/java/com/nageoffer/ai/ragent/agent/dao/mapper/AgentStateMapper.java) (`agent/src/main/java/com/nageoffer/ai/ragent/agent/dao/mapper/AgentStateMapper.java`)：读状态写入与外部操作的不同边界。
  - [拒绝处理](https://github.com/nageoffer/ragent/blob/ff93871ab88fff24a5dac7feee7ea342359a3439/agent/src/main/java/com/nageoffer/ai/ragent/agent/confirm/AgentConfirmDenialMiddleware.java) (`agent/src/main/java/com/nageoffer/ai/ragent/agent/confirm/AgentConfirmDenialMiddleware.java`)：区分文案处理、用户确认与业务授权。
- **静态核查短板与勿照搬项**：
  - 持久化存在不等于断进程恢复或外部工具副作用原子。
  - 拒绝middleware主要修正文案；确认/拒绝不能替代服务端授权，业务评测未核。
  - **切勿照搬**：不把整个平台冒充个人原创，也不直接采用“企业级”宣传作为质量结论。

### PRO06 · Open Deep Research：研究编排与评测参考（Agent／研究与评测参考）
- **核心学习目标**：优先学评测器、基线与成对比较，再沿研究协调、工具、压缩和报告流程反查效果来源。
- **候选人归属与结果边界**：工程参照：仅用于面经/JD能力主题对照，未核成功候选人本人求职项目或具体贡献；不凭同账号或star建立关系。
- **推荐精读源码模块**：
  - [研究流程](https://github.com/langchain-ai/open_deep_research/blob/1b7d2e80db9faa586165c60e09096dbbfd483a64/src/open_deep_research/deep_researcher.py) (`src/open_deep_research/deep_researcher.py`)：读Supervisor、并行研究、压缩及重试。
  - [多维评测器](https://github.com/langchain-ai/open_deep_research/blob/1b7d2e80db9faa586165c60e09096dbbfd483a64/tests/evaluators.py) (`tests/evaluators.py`)：看相关性、正确性、依据与完整性怎样判。
  - [成对比较](https://github.com/langchain-ai/open_deep_research/blob/1b7d2e80db9faa586165c60e09096dbbfd483a64/tests/pairwise_evaluation.py) (`tests/pairwise_evaluation.py`)：看对照单位和裁判机制，准备人工抽核。
- **静态核查短板与勿照搬项**：
  - 模型裁判存在偏差，生成漂亮报告不足以证明结论正确。
  - 未做等预算成本/尾延迟实验，也未验证完整业务权限和外部写操作恢复。
  - **切勿照搬**：不把同一模型自评或默认模型/搜索配置当可信效果；不复制未复现分数。

### PRO24 · Sprout：任务树编排、预算与文本打分边界（Agent／本人主页直连机制库）
- **核心学习目标**：学树形拆分、并发Worker、拖慢检测与重拆；特别适合对照“代码有机制”和“任务真成功”的差别。
- **候选人归属与结果边界**：CV31：本人主页直接链接；当前源码晚于实习结束，不证明投递时使用或促成录用。
- **推荐精读源码模块**：
  - [任务树](https://github.com/hlbbbbbbb/sprout/blob/3ecd36e5a4eac42ae90be854e415857fd0f3cf7c/sprout/task_tree.py) (`sprout/task_tree.py`)：读并发、取消、重拆、合成与预算统计时机。
  - [Worker](https://github.com/hlbbbbbbb/sprout/blob/3ecd36e5a4eac42ae90be854e415857fd0f3cf7c/sprout/worker.py) (`sprout/worker.py`)：看实际可用工具是报告/放弃还是外部执行。
  - [benchmark](https://github.com/hlbbbbbbb/sprout/blob/3ecd36e5a4eac42ae90be854e415857fd0f3cf7c/examples/benchmark.py) (`examples/benchmark.py`)：核评分对象，区分文本形式与功能正确。
  - [mock测试](https://github.com/hlbbbbbbb/sprout/blob/3ecd36e5a4eac42ae90be854e415857fd0f3cf7c/tests/test_task_tree.py) (`tests/test_task_tree.py`)：明确控制流测试与真实任务评测的区别。
- **静态核查短板与勿照搬项**：
  - benchmark用正则/关键词给输出文本打分，未执行生成代码，分数不等于正确率。
  - 调用后累计token，非并发硬预算；未见持久化检查点，所读Worker未形成完整外部动作闭环。
  - **切勿照搬**：不复制25→100分为任务成功率，不把内存回退当重启恢复，也不回填为实习投递项目。

### PRO25 · NoWorries：桌面记忆与跨平台隔离风险选读（Agent／本人CV直连桌面项目）
- **核心学习目标**：学情景记忆、执行器和跨平台权限差异；用具体失败路径练安全边界审查。
- **候选人归属与结果边界**：CV31：本人CV直接列仓库；基于OpenWork/OpenClaw/Pi Agent，未逐diff核全库原创比例；PR3064只核端点修复。
- **推荐精读源码模块**：
  - [情景记忆](https://github.com/hlbbbbbbb/No-worries/blob/c811e697bb48a979ee14bd932de80057b98b464f/noworries_app/apps/desktop/src/main/clawdbot/memory/episode-memory.ts) (`noworries_app/apps/desktop/src/main/clawdbot/memory/episode-memory.ts`)：读按月JSON存储与关键词检索，核崩溃/并发边界。
  - [macOS执行与回退](https://github.com/hlbbbbbbb/No-worries/blob/c811e697bb48a979ee14bd932de80057b98b464f/noworries_app/apps/desktop/src/main/sandbox/macos-sandbox.ts) (`noworries_app/apps/desktop/src/main/sandbox/macos-sandbox.ts`)：读无输出时的再次执行和降级。
  - [Windows执行](https://github.com/hlbbbbbbb/No-worries/blob/c811e697bb48a979ee14bd932de80057b98b464f/noworries_app/apps/desktop/src/main/sandbox/windows-sandbox.ts) (`noworries_app/apps/desktop/src/main/sandbox/windows-sandbox.ts`)：区分环境设置与系统隔离。
  - [工作区校验](https://github.com/hlbbbbbbb/No-worries/blob/c811e697bb48a979ee14bd932de80057b98b464f/noworries_app/apps/desktop/src/main/sandbox/workspace-manager.ts) (`noworries_app/apps/desktop/src/main/sandbox/workspace-manager.ts`)：读路径校验，审子目录与符号链接边界。
- **静态核查短板与勿照搬项**：
  - Windows/Linux环境重定向不构成系统级隔离；macOS回退可能重复执行并降低隔离。
  - 路径字符串前缀校验有组件边界/符号链接待核；只归档14文件，整体运行与任务评测未核。
  - **切勿照搬**：不把框架继承算全库原创，不把端点修复PR3064扩大为整个产品的贡献证明。

---

## 四、面试高频主题覆盖统计（99 份面经）

| 考察主题 | 全部面经提及 (n=99) | 严格近期工程实习 (n=14) | 明确实习但年份未知 (n=48) |
| :--- | :---: | :---: | :---: |
| 项目职责、真实使用与架构取舍 | 83 | 12 | 42 |
| Java/Go/Python与框架基础 | 58 | 10 | 27 |
| 数据库、缓存与检索存储 | 61 | 12 | 24 |
| 消息、幂等与故障恢复 | 38 | 4 | 20 |
| RAG、分块、召回与重排 | 26 | 2 | 16 |
| Agent编排、工具与Skill/MCP | 47 | 4 | 29 |
| 记忆、上下文与token成本 | 19 | 1 | 12 |
| 评测、指标与上线效果 | 36 | 2 | 22 |
| 权限、审批与隔离 | 25 | 2 | 13 |
| 网络、操作系统与编码 | 81 | 13 | 36 |

## 五、分方向精读路线建议

### 1. 后端方向三步精读
- 先读B1–B3并选PRO19/20中的一个业务链，沿问题读源码。
- 再读PRO21的并发与测试，补B4/B5基础、排障和验证。
- 需要开源贡献表达时读PRO09两项真实PR；C++网络方向另选PRO17，不要求整库复刻。

### 2. Agent 工程方向三步精读
- 先读A1/A2，以PRO06观察怎样评测，以PRO04观察怎样接线。
- 再读PRO24的机制、评分与预算缺口；读PRO25的记忆、隔离和重复执行风险。
- 按A3–A5核对恢复、授权、成本和后端基础；不把四个仓库拼装成个人项目方案。

