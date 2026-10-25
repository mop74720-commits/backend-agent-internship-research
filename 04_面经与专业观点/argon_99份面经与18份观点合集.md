# 99 份真实面经与 18 份专业技术观点全量合集

> 本合集将 `逐条面经与观点/` 下的零散 TXT 卡片整合为单文件。按 10 大高频问题簇归类的精炼版与三步答题骨架见 [`argon_面经重点与项目追问.html`](argon_面经重点与项目追问.html)。

---

## 第一部分：99 份面经材料逐条汇总

### INT01 · 字节跳动-Agent开发实习生 一面（45分钟）（Agent工程｜面试日期未标明（页面06-04））
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/931a8a935a5e4b4f8d0b71cd4e818604](https://www.nowcoder.com/feed/main/detail/931a8a935a5e4b4f8d0b71cd4e818604)
- **核心提问与考察点**：检索为何选择ES，替换为向量检索损益是什么？；工具调用怎样限制？压缩策略参数为什么这样选？；Recall@5怎样测出，如何避免评测过拟合？。

### INT02 · 4.21 字节agent开发实习一面分享（Agent工程｜04-21面试，年未明）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/e0d5745e28b64db79ba1832f958b758c](https://www.nowcoder.com/feed/main/detail/e0d5745e28b64db79ba1832f958b758c)
- **核心提问与考察点**：为何选择该Agent工作流程？借鉴了什么产品？；本地工具、MCP工具、Skill在架构中的关系是什么？；现场实现Skill注册、发现与调用。

### INT03 · 字节agent开发实习生一面面经 29届（Agent工程｜面试日期未标明（页面08-05））
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/617d30ab75dc40db81b291b8b98dfb13](https://www.nowcoder.com/feed/main/detail/617d30ab75dc40db81b291b8b98dfb13)
- **核心提问与考察点**：自进化数据怎样获得与判断质量？；为何使用沙箱，快照及回滚时机怎样选择？；为什么用Go重写Hello Agent，模块依赖如何组织？。

### INT04 · 美团agent一面（Agent工程｜面试日期未标明（页面09-24））
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/554bdcc695ae42f8b0d78e3c44dd17d5](https://www.nowcoder.com/feed/main/detail/554bdcc695ae42f8b0d78e3c44dd17d5)
- **核心提问与考察点**：单Agent与多Agent怎样选择？；微调和RAG各适合什么情况？。

### INT05 · 京东大模型应用开发 实习面经（Agent工程｜面试日期未标明（页面03-14））
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/904555611d13461da9288d4147b7550b](https://www.nowcoder.com/feed/main/detail/904555611d13461da9288d4147b7550b)
- **核心提问与考察点**：混合检索权重和非标准输入如何处理？；如何确保向量检索准召率，如何评估整个RAG？；IVF与HNSW为什么选其一？。

### INT06 · 字节-广告后开-日常实习(已offer)（后端｜面试/offer发生年未直接明示）
- **原文链接**：[https://www.nowcoder.com/discuss/798306098527715328?sourceSSR=subject](https://www.nowcoder.com/discuss/798306098527715328?sourceSSR=subject)
- **核心提问与考察点**：MQ积压时紧急消息如何处理？；扫码登录为何还需手机确认？；实习细节、联合索引命中与对象锁实现。

### INT07 · 美团后端暑期实习面经（后端｜05-14、05-16面试，年份未由当前原记录正文单独确认）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/3187ad5588394e108f96db0eb9e82bcf](https://www.nowcoder.com/feed/main/detail/3187ad5588394e108f96db0eb9e82bcf)
- **核心提问与考察点**：为什么用MQ而非同步HTTP或数据库传文件？；本人承担什么任务、提出过什么改进？；已有项目还能怎样利用AI，尝试落地过什么工具？。

### INT08 · 京东后端oc面经（含timeline）（后端｜08-15、08-19技术面，年份未由当前原记录正文单独确认）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/8e28ab8ad4b944bd82ae653a094b5aa7?sourceSSR=subject](https://www.nowcoder.com/feed/main/detail/8e28ab8ad4b944bd82ae653a094b5aa7?sourceSSR=subject)
- **核心提问与考察点**：低延迟下单怎样从GC角度优化？；如何设计不丢失、可幂等、可保序的MQ？；最近项目做得最差的地方是什么，重做会怎样改？。

### INT09 · 暑期实习第二个offer-淘天oc（后端｜6.11/6.16/6.18技术面、6.20 HR、6.24 OC；实际年未知）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/32f9c690698f4462b8f6b75ba721d168](https://www.nowcoder.com/feed/main/detail/32f9c690698f4462b8f6b75ba721d168)
- **核心提问与考察点**：点赞、收藏、排行为何使用相应Redis结构？；Kafka的顺序、幂等、可靠性与积压怎样处理？；积分兑换红包怎样确保两边状态和金额一致？。

### INT10 · 腾讯日常实习一面面经（2027暑期向）（后端｜2026-03-10面试）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/37c64318e134459bbd9a5c7953e99aea?sourceSSR=post](https://www.nowcoder.com/feed/main/detail/37c64318e134459bbd9a5c7953e99aea?sourceSSR=post)
- **核心提问与考察点**：Redis主从、哨兵、集群在项目中怎样选？；RAG切块、多路召回和幻觉如何优化？；大数字符串转换的现场编码。

### INT11 · 腾讯后端实习一面90min（后端｜面试日期及事件年未知；2025-12-07为原帖发表日期）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/9e1c51d930b247aab6e1973ba920d271](https://www.nowcoder.com/feed/main/detail/9e1c51d930b247aab6e1973ba920d271)
- **核心提问与考察点**：数GB文件的处理方案有没有真正测过？；MQ宕机后订单超时取消怎样兜底？；为何CAS不能自动实现一人一单，库存正确性怎样保障？。

### INT12 · 27双非本—腾讯IEG游戏安全后台实习面经（混合｜2025-09-26 offer；2025-10-04复盘）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/9ecd5997a7d74f3fa885695032f32065?sourceSSR=dynamic&weFlow=true](https://www.nowcoder.com/feed/main/detail/9ecd5997a7d74f3fa885695032f32065?sourceSSR=dynamic&weFlow=true)
- **核心提问与考察点**：K8S与Casbin RBAC实习做了什么？；Go调度、网络IO、Raft、LSM分别是什么？；Agent与模型、LangChain与LangGraph、Function Call与MCP怎样区分？。

### INT13 · 腾讯IEG后台开发日常实习二面/HR面（已过等offer中）（混合｜二面/HR完成等待offer；事件年月日未确认）
- **原文链接**：[https://www.nowcoder.com/discuss/935191455750946816](https://www.nowcoder.com/discuss/935191455750946816)
- **核心提问与考察点**：自建深度研究比通用模型产品好在哪里？；来源质量、覆盖与边际收益如何计算？；既然最后仍由大模型兜底，为何微调？现场演示。

### INT14 · 字节广告团队agent面经（一二面）（Agent工程｜一二面；事件年月日未确认）
- **原文链接**：[https://www.nowcoder.com/discuss/930870582843805696?sourceSSR=dynamic](https://www.nowcoder.com/discuss/930870582843805696?sourceSSR=dynamic)
- **核心提问与考察点**：内部Skill发布平台及本地Runtime怎样设计？；营销秒杀系统怎样设计？；现场运行Demo，解释Skill与Function Call的区别。

### INT15 · 小红书-引擎架构-timeline（后端｜03-19、03-26面试；03-27 OC；年未由当前正文单独确认）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/b955d160ffa54d98a2bbc5f089619a2b?sourceSSR=users](https://www.nowcoder.com/feed/main/detail/b955d160ffa54d98a2bbc5f089619a2b?sourceSSR=users)
- **核心提问与考察点**：并发安全与ThreadLocal怎样理解？；如何设计高并发系统？；两轮主要追问已做实习。

### INT16 · 小红书后端实习面经（已offer）（后端｜05-13、05-16面试；05-19 offer；年未由当前正文单独确认）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/25e8d4a18bbf4bcba4521c24fc9efd13](https://www.nowcoder.com/feed/main/detail/25e8d4a18bbf4bcba4521c24fc9efd13)
- **核心提问与考察点**：项目中延伸分布式场景题；GC选择、索引列选择、Redis数据结构与持久化。

### INT17 · 8.25 小红书实习 AI全栈开发实习一面挂凉经（Agent工程｜08-25面试；年未显示）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/c712eda7fbf44ba69835b6dd2ff7fc4c?sourceSSR=dynamic](https://www.nowcoder.com/feed/main/detail/c712eda7fbf44ba69835b6dd2ff7fc4c?sourceSSR=dynamic)
- **核心提问与考察点**：为什么必须多Agent，如何编排？；系统如何评测，同事有没有准确率反馈？；RAG和Harness具体如何落地？。

### INT18 · 小红书 Product Engineer（AI与全栈方向）-社区工程 一面面经（Agent工程｜面试年月日未确认）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/70ad5ead2f784676b0b399eab877d3d4?sourceSSR=dynamic](https://www.nowcoder.com/feed/main/detail/70ad5ead2f784676b0b399eab877d3d4?sourceSSR=dynamic)
- **核心提问与考察点**：为什么选关键词而不是向量检索，测过准确率吗？；调用LLM的功能与Agent到底有什么不同？；AI高并发下怎样设计用户级缓存、限流和异步队列？。

### INT19 · 26届后端暑期实习总结（后端｜多场暑期实习面试；具体年月日未单独确认）
- **原文链接**：[https://www.nowcoder.com/discuss/744612931374977024](https://www.nowcoder.com/discuss/744612931374977024)
- **核心提问与考察点**：监控与数据库设计、红包容灾、跨境物流同步；线程池问题定位与熔断降级。

### INT20 · 阿里云Java研发实习 - 一面（后端｜2025-04-21一面）
- **原文链接**：[https://www.nowcoder.com/discuss/743798386737897472?sourceSSR=dynamic](https://www.nowcoder.com/discuss/743798386737897472?sourceSSR=dynamic)
- **核心提问与考察点**：项目数据库访问做过哪些优化，去掉SELECT *为何能改善查询？；统一日志切面如何实现，怎样读取参数并控制多个切面的次序？；面对突发请求怎样选择限流方法，令牌桶与漏桶有何取舍？。

### INT21 · 百度-java后端实习-凉经（后端｜07-10面试；年未显示）
- **原文链接**：[https://www.nowcoder.com/discuss/905123127074582528?sourceSSR=post](https://www.nowcoder.com/discuss/905123127074582528?sourceSSR=post)
- **核心提问与考察点**：附近商户查询如何把Redis GEO与地图服务连接起来？；购物车计价为何采用策略、工厂和模板方法，各自如何实现？；MySQL到ES出现同步差异时怎样排查，添加索引会带来哪些运行风险？。

### INT22 · 四非本 滴滴-后端实习面经(已OC)（后端｜2025-03-21/03-25面试；03-28正式offer）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/c822bd1fffa64addb718e806090a20ee?toCommentId=21427551](https://www.nowcoder.com/feed/main/detail/c822bd1fffa64addb718e806090a20ee?toCommentId=21427551)
- **核心提问与考察点**：采用RocketMQ顺序消息解决了什么需求，同时损失什么能力？；自研RPC为什么值得做，协议包含哪些信息、如何保证可解析？；如何把服务同步编排改成CompletableFuture，怎样设计充值和转账的事务边界？。

### INT23 · 27实习面经-蚂蚁后端ai开发一面（混合｜面试年月日未确认）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/db9292f9a3dc4102bec84668a7f2df18?urlSource=home-api](https://www.nowcoder.com/feed/main/detail/db9292f9a3dc4102bec84668a7f2df18?urlSource=home-api)
- **核心提问与考察点**：自己实现的锁为何采用Lua，哪些操作需要保持原子性？；缓存更新方案怎样处理Redis与MySQL的时间差？；短链系统的读写瓶颈在哪里，如何按瓶颈调整架构？。

### INT24 · 26届快手暑期实习（已OC）（后端｜2025-03-24/03-31技术面；04-15 HR；4月下旬offer）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/8c1a63e46e4e462892474e405d611028](https://www.nowcoder.com/feed/main/detail/8c1a63e46e4e462892474e405d611028)
- **核心提问与考察点**：实习中POI表保存了哪些字段，如何限定中心点附近的结果？；使用GEO查询时，其底层如何组织和查找坐标？；Hash与跳表为何适合相应数据，为什么没有选择其他树结构？。

### INT25 · 京东-京东零售-jdy- java实习-一面凉经（后端｜面试日期未写；四天后自述失败，年未单独确认）
- **原文链接**：[https://ac.nowcoder.com/discuss/1535507?channel=-1&source_id=discuss_terminal_discuss_hot_nctrack&type=0](https://ac.nowcoder.com/discuss/1535507?channel=-1&source_id=discuss_terminal_discuss_hot_nctrack&type=0)
- **核心提问与考察点**：突发流量时，限流精度与系统开销怎样平衡？；线程池参数考虑了哪些资源约束，任务堆积导致内存问题时如何定位？；每段业务链路能否观测，锁注解有哪些参数、粒度和替代方案？。

### INT26 · 美团java后端日常实习一二面（后端｜各轮具体日期未写；编辑年不作面试年）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/d27704499b5c41e0bd0019a8d158a052](https://www.nowcoder.com/feed/main/detail/d27704499b5c41e0bd0019a8d158a052)
- **核心提问与考察点**：用户规模变大后，轮询对服务端造成什么压力，改用推送有何取舍？；项目怎样排查SQL，重复读的快照与当前读如何影响行为？；如何发现和管理依赖版本冲突？。

### INT27 · 快手Java日常实习一面（后端｜面试日期未写；发布年不作面试年）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/dd1f2a0a303644dab4b53c5be40caf9b?sourceSSR=users](https://www.nowcoder.com/feed/main/detail/dd1f2a0a303644dab4b53c5be40caf9b?sourceSSR=users)
- **核心提问与考察点**：为何选RabbitMQ，重复投递会在什么情况下发生，消费者如何去重？；项目自定义协议有哪些字段，怎样处理半包和粘包？；缺少日志与后台数据时，怎样逐步缩小线上故障范围？。

### INT28 · 26届后端实习-蚂蚁集团后端开发一面面经（后端｜2025-03-17面试）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/bb4c92b4084f44e69388ac342c1ca809?sourceSSR=users](https://www.nowcoder.com/feed/main/detail/bb4c92b4084f44e69388ac342c1ca809?sourceSSR=users)
- **核心提问与考察点**：研究生阶段在实验室实际做了什么、如何说明自己的贡献？；为什么目前项目方向没有选择AI？；高可用Redis集群怎样处理节点故障？。

### INT29 · 26届秋招字节后端二+三面速通面经详细版（附timeline）（后端｜2025-09-04/09-08技术面；09-28意向）
- **原文链接**：[https://www.nowcoder.com/discuss/796747192839991296](https://www.nowcoder.com/discuss/796747192839991296)
- **核心提问与考察点**：自己负责的服务在全系统上下游什么位置，为哪项业务服务？；系统选择何种一致性方案，为什么可以接受相应延迟？；最难挑战如何解决，竞赛经历能否转成清晰的算法解释与现场实现？。

### INT30 · 百度秋招后端一面面经（混合｜07-22面试，年未显示）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/4f3b80037f7e42778eabe9358b84deba](https://www.nowcoder.com/feed/main/detail/4f3b80037f7e42778eabe9358b84deba)
- **核心提问与考察点**：Skill上线效果怎样量化，流量放大后系统哪段先受限？；Prompt配置出错怎样止损，缓存的过期与更新依据是什么？；多次工具执行中间失败时，如何恢复且避免已完成动作重复发生？。

### INT31 · 京东科技后端秋招一面与二面（同候选人合并）（后端｜2025-09-04/09-09两轮；10-09意向）
- **原文链接**：[https://www.nowcoder.com/discuss/805923665652039680](https://www.nowcoder.com/discuss/805923665652039680)
- **核心提问与考察点**：实习系统的复杂度和稳定性改进体现在哪里，能否用几句话概括？；LiteFlow在需求里承担什么职责，和责任链思路如何对应？；服务CPU与内存同时升高怎样排查，手写Spring如何处理循环依赖？。

### INT32 · 滴滴秋储后端实习生面经+秋招正式批面经（历史SSP对照）（后端｜实习/校招具体年未确认；事件不晚于2022-06-17原文）
- **原文链接**：[https://www.nowcoder.com/discuss/366180144833200128](https://www.nowcoder.com/discuss/366180144833200128)
- **核心提问与考察点**：为何采用不同配置与注册组件，更新推拉方式各有什么代价？；自研RPC如何实现负载均衡，缓存线程安全怎样保证？；在订单、结算场景如何提高系统可靠性，多维约束下如何匹配人车资源？。

### INT40 · 智能体与大模型应用工程实习 一面（Agent工程｜06-09面试，年未显示）
- **原文链接**：[https://www.nowcoder.com/discuss/894720138258173952?sourceSSR=post](https://www.nowcoder.com/discuss/894720138258173952?sourceSSR=post)
- **核心提问与考察点**：哪些请求值得增加本地与Redis两级缓存，怎样确定失效和更新策略？；异步订单怎样在个人环境验证；重复投递、删集合时宕机如何收尾？；Java/Spring AI相对Python框架的选择依据，以及知识导入、BM25和对话循环如何衔接？。

### INT41 · 腾讯实习 ai应用开发后端面经分享（Agent工程｜面试年月日未确认（页面04-23））
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/144c6ae334b24c0aa643ed43ccfebaac?sourceSSR=dynamic](https://www.nowcoder.com/feed/main/detail/144c6ae334b24c0aa643ed43ccfebaac?sourceSSR=dynamic)
- **核心提问与考察点**：作品是否有正式使用者，尚未上线的原因是什么？；多Agent如何分工；数据来源与模型调优如何交代？；中断后怎么安全重试；跨境汇款任务超时怎样保护资金状态？；知识库在持续提供服务时如何更新？。

### INT42 · 26.4百度大模型生态集成实习，新鲜面经~（Agent工程｜2026-04实习面试）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/62d4ca9866d84d63bf6eafbb0a947bb8?sourceSSR=search](https://www.nowcoder.com/feed/main/detail/62d4ca9866d84d63bf6eafbb0a947bb8?sourceSSR=search)
- **核心提问与考察点**：Python列表/元组、函数对象、装饰器与实际实现怎样对应？；接到已有大项目的新功能需求，如何规划并开发Agent Skill？；怎样组织工具调用、检索策略、向量相似度与设计模式？。

### INT43 · 【面经】阿里淘宝闪购 · Agent 算法工程师 · 27届实习一面 时长约 60 分钟（混合｜面试年月日未确认（页面04-30，27届非事件年））
- **原文链接**：[https://www.nowcoder.com/discuss/879393838081597440?sourceSSR=post](https://www.nowcoder.com/discuss/879393838081597440?sourceSSR=post)
- **核心提问与考察点**：框架选型如何考虑私有部署；高风险工具怎样接人工中断、隔离和审计？；长期会话如何分层保留，工具schema与调用轮数的改进如何验证？；离线模型效果很好、上线下跌时，如何从数据、标签和serving逐层排查？。

### INT44 · 阿里淘天agent开发 日常实习 一面（Agent工程｜面试年月日未确认（页面04-16））
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/566fa6594dcc446a82bd203f139c45c2](https://www.nowcoder.com/feed/main/detail/566fa6594dcc446a82bd203f139c45c2)
- **核心提问与考察点**：既有状态机与Workflow各解决什么问题，如何降低延迟和token用量？；多Agent传递上下文的数据结构、组件可插拔以及Skill/MCP边界是什么？；现场借助AI交付并发优惠券分发程序，需展示入口、边界测试和README。

### INT45 · 字节agent开发一面 实习面经（Agent工程｜面试年月日未确认（页面03-19））
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/6506d4b4addf447c8e2c135b5088cdc8](https://www.nowcoder.com/feed/main/detail/6506d4b4addf447c8e2c135b5088cdc8)
- **核心提问与考察点**：上下文压缩怎样筛选有效信息，如何检查压缩后质量？；MCP与Skill的实现层次是什么，渐进式加载怎样落实？；框架有哪些组件，项目为何选这些组件；现场编码螺旋矩阵。

### INT46 · 字节Agent开发一面90min凉经（Agent工程｜面试年月日未确认（页面04-09））
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/91c5394e57c14927841d7a86bfe427c2?sourceSSR=search](https://www.nowcoder.com/feed/main/detail/91c5394e57c14927841d7a86bfe427c2?sourceSSR=search)
- **核心提问与考察点**：单测分支覆盖怎样测，插桩、mock、代码有效性分析各做了什么？；AST/LSP难覆盖的代码怎样筛除；怎样解释生成质量下降？；查询改写何时需用户补充，意图识别为何并行，上下文待办如何起作用？。

### INT47 · 小红书大模型平台 Agentic 全栈研发练习生 一面凉经（Agent工程｜2026-08-06面试）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/e5e9311a623940eead6ec98c65e7f9e8?sourceSSR=search](https://www.nowcoder.com/feed/main/detail/e5e9311a623940eead6ec98c65e7f9e8?sourceSSR=search)
- **核心提问与考察点**：项目解决谁的研发问题，写操作边界与Harness职责如何划分？；模糊query如何识别，Skill何时加载，不同模型的行为如何保持可接受？；如何从SQLite原型扩到数千用户；自研编排与LangGraph图结构怎样解释？。

### INT48 · 美团 软件开发（全栈）暑期实习 面经全记录（二面（Agent工程｜04-07面试；04-10邮件offer，年未明）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/6c36de1ad1354e17b3e6ab2d6b63167f?sourceSSR=search](https://www.nowcoder.com/feed/main/detail/6c36de1ad1354e17b3e6ab2d6b63167f?sourceSSR=search)
- **核心提问与考察点**：语音下单Agent怎样选语音转写与端到端方案，长等待时如何逐步反馈？；跨十几个业务仓库开发新功能，怎样用文档、代码阅读与阶段测试约束AI？；为什么AI时代仍需理解并发锁、消息幂等等基础；现场原地合并数组。

### INT49 · 小红书Agent开发实习生一面凉经，附百度Agent凉经（Agent工程｜08-24发帖前一周两场面试，年未明）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/e319aadc79a9479397a6661a7f5ca088?sourceSSR=search](https://www.nowcoder.com/feed/main/detail/e319aadc79a9479397a6661a7f5ca088?sourceSSR=search)
- **核心提问与考察点**：LangGraph为何拆成多个子图，节点输入输出和共享状态怎么传递？；Skill生成错误文件、子图偏航时怎样重跑或人工移出？；与纯脚本/单Agent相比的必要性，以及MySQL索引、事务锁和最长递增子序列。

### INT50 · 字节、蚂蚁、腾讯Agent实习面经（凉经） 看一看有什么问题呢（混合｜三家公司流程；各轮年月日未确认）
- **原文链接**：[https://www.nowcoder.com/discuss/904029765160497152](https://www.nowcoder.com/discuss/904029765160497152)
- **核心提问与考察点**：字节把进程线程、Transformer与训练泛化问题连到具体项目；腾讯云平台以多轮现场编码和变更约束为主，而不是Agent题；蚂蚁追问微调/RAG选择、LoRA、显存和batch size依据。

### INT51 · T厂 Agent开发日常实习一面挂凉经（Agent工程｜面试年月日未确认（页面04-09））
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/aef9769bc0604700bcc8ed4fa8db8377?sourceSSR=dynamic](https://www.nowcoder.com/feed/main/detail/aef9769bc0604700bcc8ed4fa8db8377?sourceSSR=dynamic)
- **核心提问与考察点**：多模态召回的跨场景误命中、精确率/召回率怎样具体计算？；Qwen思考模型的空调用与错调用如何适配，自己相对参考框架改了什么？；长短记忆如何触发迁移与淘汰；大代码库依赖怎样查找并提供给模型？；少量失败样本怎样扩成训练数据，如何说明后训练工作的贡献？。

### INT52 · 字节Agent开发日常实习一面（Agent工程｜面试年月日未确认（页面08-27））
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/d2cf5165d1184b59879eff5793b7b453?sourceSSR=subject](https://www.nowcoder.com/feed/main/detail/d2cf5165d1184b59879eff5793b7b453?sourceSSR=subject)
- **核心提问与考察点**：token如何计量，压缩提示如何生成，怎样确认压缩实际完成而非只有模型声明？；会话、Skill加载和子Agent分别如何组织，业务项目接了哪些外部能力？；现场递归合并嵌套JSON，区分数据类型并保持输入不变；另问SQL去重与进程/端口排查。

### INT53 · 美团一面全栈开发日常实习面经（Agent工程｜面试年月日未确认（页面10-12））
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/95e9fc44397d4118ba3946ef0d33b6da?sourceSSR=enterprise](https://www.nowcoder.com/feed/main/detail/95e9fc44397d4118ba3946ef0d33b6da?sourceSSR=enterprise)
- **核心提问与考察点**：为何自研与选择ReAct，哪些精确任务应绕开RAG？；子Agent的消息/工具权限、schema、注入防护与失败降级如何落实？；记忆、自进化、检索指标怎样衔接端到端测试；长任务、幂等、缓存一致性如何设计？。

### INT54 · 字节数据中台Agent全栈面经（Agent工程｜09-20一面、09-21二面，年未明）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/fe77496948f74b4091ab4bb6e8156c8b?sourceSSR=dynamic](https://www.nowcoder.com/feed/main/detail/fe77496948f74b4091ab4bb6e8156c8b?sourceSSR=dynamic)
- **核心提问与考察点**：通用Agent应包含哪些功能，既往两段实习各负责什么？；如何决定能力封成Skill还是Tool，LangChain与LangGraph的取舍是什么？；HTTPS与浏览器到机房链路、SSE底层，以及前缀树和树右视图编码。

### INT55 · 字节Agent开发后端 日常实习一面凉面（Agent工程｜09-23面试，年未明）
- **原文链接**：[https://www.nowcoder.com/discuss/932295617999622144](https://www.nowcoder.com/discuss/932295617999622144)
- **核心提问与考察点**：AI生成的评测题怎样保证覆盖与质量，哪个指标真正对应任务目标？；Markdown/TXT/PDF如何差别切分；BM25与向量为什么混合，RRF为什么不直接加原分数？；Cross-Encoder重排的额外价值与领域失配怎样验证；两个项目除了技术栈还有何区别？。

### INT56 · JavaWxy本人面试记录：携程、菜鸟、美团项目追问对照（后端｜各轮只保留文件月日；24暑期/24秋招为组名，具体事件年未明）
- **原文链接**：[https://github.com/viego1999/JavaWxy/blob/69c82b68d5d7b023adadc2421c2d0a1406641397/%E9%9D%A2%E8%AF%95%E8%AE%B0%E5%BD%95.md](https://github.com/viego1999/JavaWxy/blob/69c82b68d5d7b023adadc2421c2d0a1406641397/%E9%9D%A2%E8%AF%95%E8%AE%B0%E5%BD%95.md)
- **核心提问与考察点**：RPC注册发现与完整调用流程；远程调用是否每次访问注册中心；同步/异步返回；订单全流程、消息积压和Spring事务；RPC节点宕机与故障恢复；压测实施与本人贡献。

### INT57 · CalvinNeo：2018求职复盘中的阿里云后台面试主题（后端｜2018求职；阿里云面试主题）
- **原文链接**：[https://www.nowcoder.com/discuss/353154880351182848](https://www.nowcoder.com/discuss/353154880351182848)
- **核心提问与考察点**：为何选择并实现编译器、可靠传输或Raft，个人做了什么？（据项目段归纳）；阿里云项目追得深，需要解释Linux实现与常见系统设计（原文主题，非整理者虚构逐字问句）。

### INT58 · dong03 CV_Interview：历史CV/多模态题目与协作面经范围（算法对照｜部分面经正文明确2022年，其他轮次年未知）
- **原文链接**：[https://github.com/dong03/CV_Interview/blob/6ff6dde31ef16c9c691bce7b1caab0391f1b6c38/TIPS.md#L24-L39](https://github.com/dong03/CV_Interview/blob/6ff6dde31ef16c9c691bce7b1caab0391f1b6c38/TIPS.md#L24-L39)
- **核心提问与考察点**：论文与实习项目、focal loss参数、FLOPs、BatchNorm工程实现、受限空间排序；实习、论文、全连接层零初始化、softmax梯度、weight decay、PyTorch function/module和底层理解；数组组合约束、DeepLabV3+、视频tag/embedding冷启动业务；实习收获、业务场景理解、项目后续规划；矩阵转置与取球概率题；本轮仅记录题目存在，不将答案当技术核验。

### INT59 · mio4：四家公司本人实习面经与综合面试笔记（后端｜2019-01后端实习；2019求职总结）
- **原文链接**：[https://www.nowcoder.com/discuss/353154814064402432](https://www.nowcoder.com/discuss/353154814064402432)
- **核心提问与考察点**：微博点赞MySQL表设计；美团轮次项目细节与@Autowired底层实现。

### INT60 · CyC2018：从项目太浅的失败到头条SSP的本人多轮复盘（后端｜2018春招/实习/秋招）
- **原文链接**：[https://github.com/CyC2018/CS-Notes/blob/6ea58eff7e40a8b449a567af5ba7dcd20f7cd058/other/2018%20%E8%BF%99%E4%B8%80%E5%B9%B4.md#L11-L21](https://github.com/CyC2018/CS-Notes/blob/6ea58eff7e40a8b449a567af5ba7dcd20f7cd058/other/2018%20%E8%BF%99%E4%B8%80%E5%B9%B4.md#L11-L21)
- **核心提问与考察点**：项目为何太浅，如何从微博时间线继续追问？；实习项目和开源博客的个人贡献如何讲清？；头条加面项目问题与SQL执行/索引如何定位？。

### INT61 · LittleChild：地平线SSP与小马普通档的同作者面经对照（算法对照｜秋招接春招；事件年未明，22领航员不自动作2022年）
- **原文链接**：[https://github.com/LittleChild/Preparation-For-OFFER/blob/6bfb0a7dd6e11d04cdc9f7b832d79fc92427fb21/README.md#L243-L251](https://github.com/LittleChild/Preparation-For-OFFER/blob/6bfb0a7dd6e11d04cdc9f7b832d79fc92427fb21/README.md#L243-L251)
- **核心提问与考察点**：围绕简历项目及实习细节；背包类编码题；由不等概率生成器构造等概率生成器；一维max pooling及二维延伸；多个项目及实习逐项深挖；公司选择、职业规划与HR沟通。

### INT62 · 25届Java SSP作者：锁超时、异步补偿与项目指标的追问复盘（后端｜2024实习与秋招；各轮月日未核）
- **原文链接**：[https://www.nowcoder.com/discuss/712641117967093760](https://www.nowcoder.com/discuss/712641117967093760)
- **核心提问与考察点**：Redis分段锁为何采用、替代方案和差异；锁超时释放、极端场景和看门狗机制；Kafka异步解耦与库存扣减，MQ消费失败后的XXL-JOB补偿；项目不足和可优化之处，以及耗时/QPS等指标如何表达。

### INT63 · IcyCC：HTTPS、协程与Reactor的本人总体求职复盘（后端｜2019秋招）
- **原文链接**：[https://github.com/IcyCC/effective_note/blob/d55074032217c48e3d872d4524ba6cea94613b86/%E7%A7%8B%E6%8B%9B/%E7%A7%8B%E6%8B%9B%E6%80%BB%E7%BB%93.md#L94](https://github.com/IcyCC/effective_note/blob/d55074032217c48e3d872d4524ba6cea94613b86/%E7%A7%8B%E6%8B%9B/%E7%A7%8B%E6%8B%9B%E6%80%BB%E7%BB%93.md#L94)
- **核心提问与考察点**：HTTPS所处层次、加密方法、威胁与防御如何结合实现说明？；协程解决什么问题，与Reactor并发模型如何联系？；量化框架、网络库和商业项目的个人分工有什么可核材料？。

### INT64 · CocaineCong：字节Go三轮技术面，项目深挖原文已省略（后端｜三轮Go面试；年月日未逐条确认）
- **原文链接**：[https://github.com/CocaineCong/Golang-Interview/blob/5a48dfc6003468aa6c152da05e79beafdee1bcd7/a.%20%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8.md](https://github.com/CocaineCong/Golang-Interview/blob/5a48dfc6003468aa6c152da05e79beafdee1bcd7/a.%20%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8.md)
- **核心提问与考察点**：项目深挖被作者主动省略，不能从题单恢复个人项目；三轮分别覆盖网络与Go、索引与锁、消息可靠性与安全。

### INT65 · CocaineCong：B站Go两轮失败复盘与流量突增追问（后端｜两轮Go面试；年月日未逐条确认）
- **原文链接**：[https://github.com/CocaineCong/Golang-Interview/blob/5a48dfc6003468aa6c152da05e79beafdee1bcd7/b.%20B%E7%AB%99.md](https://github.com/CocaineCong/Golang-Interview/blob/5a48dfc6003468aa6c152da05e79beafdee1bcd7/b.%20B%E7%AB%99.md)
- **核心提问与考察点**：只给出项目流量突然增长的问题，没有本人业务项目细节。

### INT66 · DreamCats：同一班车项目在字节、京东、腾讯的本人多轮对照（后端｜7—8月本人面经；年未明）
- **原文链接**：[https://github.com/DreamCats/java-notes/blob/c4cf3bbbb6bc95daaf6deff734642ea51c7cec9c/Java/mianjing/README.md#L24](https://github.com/DreamCats/java-notes/blob/c4cf3bbbb6bc95daaf6deff734642ea51c7cec9c/Java/mianjing/README.md#L24)
- **核心提问与考察点**：为什么将班车系统拆成四服务、为什么选择Dubbo？；订单自动取消、事务消息、幂等与登录Token如何实现？；京东继续追问班车到点更新状态；腾讯更偏锁、JVM、数据库恢复和一致性算法。

### INT67 · 阿里云Agent一面：项目取舍、RPC与AI Coding热更新（Agent工程｜04-10一面，年未由正文确认）
- **原文链接**：[https://www.nowcoder.com/discuss/872120976190816256](https://www.nowcoder.com/discuss/872120976190816256)
- **核心提问与考察点**：项目开发难点与后续改进，工作流和Agent如何选？；区分进程间与跨主机通信，解释RPC选择；使用AI实现本地YAML/INI配置监听热更新，并继续审查修改方案。

### INT68 · 华为AI应用实习：专业面、主管面与offer时间线（Agent工程｜2026-05-14专业面及主管面，05-15沟通杭州，05-25收到offer自述；原面经另记03-31注册，关联总表华为行记2026-04-01投递。）
- **原文链接**：[https://www.nowcoder.com/discuss/884479038142586880](https://www.nowcoder.com/discuss/884479038142586880)
- **核心提问与考察点**：实习负责哪些模块、产出是什么，项目各阶段做了什么？；科研/项目困难如何分析和解决，在团队中是主导还是配合？；Agent概念、宏观架构与系统准备方式。

### INT69 · 百度27届Agent一面：上下文压缩、内部RAG与数据库建模（Agent工程｜08-18一面；27届秋招，具体年未确认）
- **原文链接**：[https://www.nowcoder.com/discuss/921590204903723008](https://www.nowcoder.com/discuss/921590204903723008)
- **核心提问与考察点**：上下文接近窗口上限如何处理，如何设计压缩？；团队内部知识问答RAG从零如何搭建？；K线表如何建模，项目如何使用索引？。

### INT70 · 百度Agent二面自述：C端架构、数据流与工具循环边界（Agent工程｜二面；正文未给完整日期，索引2026-08-21不采用）
- **原文链接**：[https://www.nowcoder.com/discuss/920461634072477696](https://www.nowcoder.com/discuss/920461634072477696)
- **核心提问与考察点**：C端Agent有哪些模块，各类Agent产品如何比较？；一次用户输入到工具执行的流程如何说明？；如何避免失败工具无限重复，只给LLM API如何搭建Agent？。

### INT71 · 字节-TikTok-后端一面（后端｜单篇未写；暑期导航列3月27日TikTok一面，但未用显式链接把具体场次一一绑定）
- **原文链接**：[https://www.nowcoder.com/discuss/876046266558398464?sourceSSR=users](https://www.nowcoder.com/discuss/876046266558398464?sourceSSR=users)
- **核心提问与考察点**：本人RAG项目的总体选择、检索与效果改进依据；Java对象锁、集合及GC的设计和性能；AI辅助开发经验、协作方式及约束流程；箭射靶计分的组合策略题。

### INT72 · 深信服Agent开发实习生一面二面（Agent工程｜一两周前；绝对年未知）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/14b2c379ae434062a009aefea9fc5df9?sourceSSR=subject](https://www.nowcoder.com/feed/main/detail/14b2c379ae434062a009aefea9fc5df9?sourceSSR=subject)
- **核心提问与考察点**：金蝶实习中接口协作、业务链路、个人最核心工作和效果证明；上百工具时如何分层注册、检索、注入，以及找不到适配工具时的退路；自研注册机制与MCP、LangChain Tools和多Agent框架的差别。

### INT73 · 九号公司Agent开发实习一面，1h30m（Agent工程｜未写绝对年月日）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/c0b53fdd38e041d2bc779753d04ee2ce?sourceSSR=subject](https://www.nowcoder.com/feed/main/detail/c0b53fdd38e041d2bc779753d04ee2ce?sourceSSR=subject)
- **核心提问与考察点**：讯飞流程各节点输入输出、OCR失败处理及人工效率增益的验证；金蝶建单中90%以上指标如何测、剩余失败类型和处理方式；接口/能力/实现三层抽象、工具注册发现，以及一个任务的完整交付闭环。

### INT74 · MINISO名创优品Agent开发实习一面（Agent工程｜未写绝对年月日）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/f844a4ac20be44bc9b3f756bd0ebb84c?sourceSSR=subject](https://www.nowcoder.com/feed/main/detail/f844a4ac20be44bc9b3f756bd0ebb84c?sourceSSR=subject)
- **核心提问与考察点**：为何拆子图，状态如何传递；外部操作完成但checkpoint前宕机如何避免重复提交；错误badcase如何避免污染Skills，自主规划和固定编排如何分工；上下文与循环token膨胀、工具结果压缩、权限与注入校验。

### INT75 · 小红书Agent开发实习生一面凉经，附百度Agent凉经（Agent工程｜原文上周，绝对年月日未明）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/e319aadc79a9479397a6661a7f5ca088?sourceSSR=subject](https://www.nowcoder.com/feed/main/detail/e319aadc79a9479397a6661a7f5ca088?sourceSSR=subject)
- **核心提问与考察点**：小红书：七步流水线为何拆三个LangGraph子图、Skills与Prompt的选型，再问索引与锁；百度：服务对象和业务痛点、子图节点I/O、幻觉与路径错误时的恢复、路由决策和人工干预。

### INT76 · 科大讯飞（AI相关岗）一面（Agent工程｜几天前，绝对年月日未明）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/1c425483516d4af1813d2dcdf98f4781?sourceSSR=users](https://www.nowcoder.com/feed/main/detail/1c425483516d4af1813d2dcdf98f4781?sourceSSR=users)
- **核心提问与考察点**：ReAct与计划/固定workflow的选择；OCR缺失的兜底和建单评测证据；工具分层、动态发现、ORM接口暴露为工具的偏移控制；提示词与Skills的评估，以及AI Coding实际故障与实践。

### INT77 · 暑期实习面试结束啦，写个总结吧（后端｜2025年1月至4月职业时间线）
- **原文链接**：[https://ac.nowcoder.com/discuss/737813386313940992](https://ac.nowcoder.com/discuss/737813386313940992)
- **核心提问与考察点**：从WebServer准备转向补数据库、缓存及分布式事务的学习不足；腾讯遍历/元编程、字节业务场景及京东分布式事务等自评薄弱点。

### INT78 · 快手秋招正式批 Golang后端 一二三四面面经（已Offer）（后端｜2025秋招；具体面试年月日单篇未写）
- **原文链接**：[https://www.nowcoder.com/discuss/792809776626356224](https://www.nowcoder.com/discuss/792809776626356224)
- **核心提问与考察点**：本人IM项目心跳、连接规模对系统指标的影响、时间轮和goroutine使用；消息重复与漏失的选择，项目亮点；Kafka取消息后磁盘读取/计算/落盘链路如何优化，数量级估算；IM性能如何测试，整数编码与海量热门查询设计。

### INT79 · 字节后端 秋招一二三四面面经（已接Offer）（后端｜2025秋招；具体面试日单篇未写）
- **原文链接**：[https://www.nowcoder.com/discuss/793068978837921792](https://www.nowcoder.com/discuss/793068978837921792)
- **核心提问与考察点**：项目选型、瓶颈和改进；RocketMQ与Kafka对比；IM性能瓶颈与AI技术了解；本人两模块架构，通知服务为何采用MQ，稳定性和上游超时排查；系统输出全链路、网站慢的优化、算法及需求工期沟通。

### INT80 · 小鹏秋招正式批 Golang后端 一二面面经（待HR面）（后端｜2025秋招；具体面试日单篇未写）
- **原文链接**：[https://www.nowcoder.com/discuss/788000430256037888](https://www.nowcoder.com/discuss/788000430256037888)
- **核心提问与考察点**：Protobuf选型、Unix Domain Socket、channel分离、生产消费和读多写少场景；服务器TCP容量需要哪些资源估算，连接各阶段内存差异；每用户最新记录SQL、Golang与Java原理差别、MySQL性能及协作。

### INT81 · 从一面到二面：Java后端实习面试复盘（原版两轮，含事后模板）（后端｜事件年月日未知）
- **原文链接**：[https://raw.githubusercontent.com/DavidHLP/DavidHLP.github.io/6f3d114a6ef9eb08b730f5f4740afe5b7d22d426/src/content/note/zh-cn/java-internship-interview-blog-polished.md](https://raw.githubusercontent.com/DavidHLP/DavidHLP.github.io/6f3d114a6ef9eb08b730f5f4740afe5b7d22d426/src/content/note/zh-cn/java-internship-interview-blog-polished.md)
- **核心提问与考察点**：Spring Cache二开怎样防穿透/击穿/雪崩；OJ怎样用Docker运行不可信用户代码；为什么OJ引入Kafka；缓存责任链如何避免过度设计；高CPU如何定位进程、线程和调用链。

### INT82 · 字节- AML大模型后端开发-一二面（混合｜未知；原帖明确为隔一段时间回忆，未写面试年月日）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/25df6c4042a742dbbe420db58c3abf0c](https://www.nowcoder.com/feed/main/detail/25df6c4042a742dbbe420db58c3abf0c)
- **核心提问与考察点**：MCP网关实现、限流、模型观测指标、DSL序列化、多租户隔离方式；长期和短期对话记忆及KV Cache；手写多租户限流器；JVM、GC、Spring AOP，Agentic RAG与工具调用，多轮缓存命中连续性、分层架构中的长链token溢出；二面手写LRU，并记录部分实习和开源追问已记不清。

### INT83 · 百度一面面经（混合｜面试事件年与具体日期未知）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/fa3706d7d465417f83d550b7f471941b](https://www.nowcoder.com/feed/main/detail/fa3706d7d465417f83d550b7f471941b)
- **核心提问与考察点**：本人慢SQL优化、读写分离、单列与联合索引的回表和索引下推；ES分片/资源与查询优化，字段选型与精准匹配；锁过期、误删、重入、秒杀，自旋策略，以及CompletableFuture线程池参数与CPU/I/O隔离；Agent模型切换后的输出方式、完整响应时间指标、责任链/观察者与模板方法取舍；HNSW、BM25、向量缺点与检索分数融合。

### INT84 · 9.7百度agent开发日常实习面经（Agent工程｜标题为9.7；正文称15点刚面完，面试约45分钟；未直接写事件年）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/bb8c28105f364770b57ff5eb5649cc60](https://www.nowcoder.com/feed/main/detail/bb8c28105f364770b57ff5eb5649cc60)
- **核心提问与考察点**：介绍本人经历及做过的工作；混合检索采用什么实现；RAG文档切片粒度如何选择，依据是什么；Coding Agent是否由开源项目改造，基于哪个项目；本人实现相对开源Agent的具体优势；工具层兜底具体覆盖什么失败。

### INT85 · 爱橙科技Java暑期实习一面：MQ、测试幂等及高可用追问（后端｜2025-03-14一面约50分钟，2025-03-15作者看到未通过）
- **原文链接**：[https://www.nowcoder.com/discuss/730542760465276928](https://www.nowcoder.com/discuss/730542760465276928)
- **核心提问与考察点**：MQbus向RPC等组件推广时，环境隔离可能遇到什么问题；如何排查OOM，以及如何判断消费者积压或处理缓慢的程度；测试框架如何设计，非幂等的数据新增操作如何清理，测试覆盖标准如何确定；为字符串形式的整数求和函数设计测试用例；另一个算法服务项目如何保证高可用，熔断和限流如何实现；Spring和Autowired注解的实现机制。

### INT86 · 美团后端暑期实习二面已offer：项目调研、容量与运维追问（后端｜正文称这周二面；未直接写面试事件年或绝对日期）
- **原文链接**：[https://www.nowcoder.com/discuss/736940763258400768](https://www.nowcoder.com/discuss/736940763258400768)
- **核心提问与考察点**：团队规模、本人角色、项目动机和实际解决的问题；是否调研同类平台或技术方案，目前最大挑战是什么；每项优化解决的问题、使用的组件及Java工具包；生产消费任务的吞吐上限、数据规模与分片方案；负载持续升高时如何定位，线程池如何配置，并发问题如何解决；上线或预测分析还缺什么，复杂模型怎样对外提供可靠服务。

### INT87 · 美团后端日常实习（已offer）（后端｜04-01一面；04-07 OC；04-09邮箱offer，年份未知）
- **原文链接**：[https://api-cdn.nowcoder.com/discuss/741030289186525184?sourceSSR=subject](https://api-cdn.nowcoder.com/discuss/741030289186525184?sourceSSR=subject)
- **核心提问与考察点**：布隆过滤器与分布式锁结合的流程是什么？；分库分表按什么字段分片？；Redis普通分布式锁与RedLock有什么区别？；Redis主从怎样同步，ZSet怎样实现？；JVM内存结构、垃圾回收、lambda与语法糖如何说明？；现场实现合并区间。

### INT88 · 字节后端实习面经（后端｜面试年月日未知；2025-02-24仅编辑日期）
- **原文链接**：[https://www.nowcoder.com/discuss/723622216419586048?sourceSSR=users](https://www.nowcoder.com/discuss/723622216419586048?sourceSSR=users)
- **核心提问与考察点**：同步/异步网络I/O与阻塞/非阻塞怎样区分？；进程线程通信、管道、虚拟内存映射怎样实现？；HTTP/HTTPS和网络分层如何说明？；shared_ptr引用计数有什么优缺点？；使用普通互斥锁实现读写锁RLock和WLock。

### INT89 · 美团 Java 二面 强度这么高吗（后端｜二面年月日未知；页面09-09编辑且无年份）
- **原文链接**：[https://ac.nowcoder.com/discuss/1674038?channel=-1&source_id=discuss_tag_discuss_hot_nctrack&type=0](https://ac.nowcoder.com/discuss/1674038?channel=-1&source_id=discuss_tag_discuss_hot_nctrack&type=0)
- **核心提问与考察点**：缓存与数据库一边成功一边失败时，除重试还有什么一致性方案？；EXPLAIN主要看哪些指标，何时索引失效？；ThreadLocal、volatile、锁升级和线程池如何说明？；实习中的具体项目和团队协作怎样开展？；手写三个线程按abc交替打印十组及线程安全单例。

### INT90 · 面经 腾讯篇（后端｜作者回顾去年暑期、秋招与本次春招；各轮年份未逐项明确）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/8b87d083399c4c41b0ec4d26d42f76ee?sourceSSR=users](https://www.nowcoder.com/feed/main/detail/8b87d083399c4c41b0ec4d26d42f76ee?sourceSSR=users)
- **核心提问与考察点**：秒杀后发送异步消息时RabbitMQ宕机怎样处理？；请求都打到Redis时怎样承载流量？；深分页、MyBatis缓存、令牌桶底层如何实现？；TCP第三次握手丢失、TIME_WAIT连接多怎样解释？；两个上亿URL文件如何找出重复内容？；线程/协程使用场景、Linux虚拟内存与I/O多路复用怎样说明？。

### INT91 · 快手商业化 Java日常实习（后端｜2024-11-05面试，11-06时间线标挂）
- **原文链接**：[https://www.nowcoder.com/discuss/719242991700889600](https://www.nowcoder.com/discuss/719242991700889600)
- **核心提问与考察点**：JVM结构、HashMap旧版本扩容和AQS怎样说明？；项目中何时使用synchronized和ReentrantLock？；为什么要Redis缓存、网关和分布式Session？；多实例和分布式怎样实现？；手写两数之和。

### INT92 · 阿里国际一面面经（后端｜面试年月日未知；2025-04-03为发布日）
- **原文链接**：[https://www.nowcoder.com/discuss/737334743661875200](https://www.nowcoder.com/discuss/737334743661875200)
- **核心提问与考察点**：独立索引和联合索引下多个SQL的命中和效率怎样比较？；IoC容器和简单Web容器怎样设计？；多级缓存为何必要、过期时间如何设置、如何保持一致？；40G内容放入单节点10G容量的集群怎样分片？；Hash取模四节点损坏一节点时怎样重新分配和保证高可用？；HTTP请求到Controller有哪些环节？。

### INT93 · 字节生活服务后端开发日常实习一二三面经（后端｜多轮技术面与HR后，2025-03-05收到正式offer；各技术面具体日期未给）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/f38ea39b741e44be8730c1e7f7d88439?sourceSSR=dynamic](https://www.nowcoder.com/feed/main/detail/f38ea39b741e44be8730c1e7f7d88439?sourceSSR=dynamic)
- **核心提问与考察点**：为什么选择JDK17，了解其GC和ZooKeeper分布式协议吗？；ZSet跳表如何插入、删除和排序？；MySQL事务原子性、容量估计和主从同步怎样说明？；扫码登录完整链路怎样实现？；网站UV/DAU如何统计，选用结构有什么误差？；现场解树子结构、三数之和及变式、LCS、接雨水等。

### INT94 · 暑期实习记录 附C++面经（后端｜04月多公司流程；事件年未知，2025-04-28为编辑日）
- **原文链接**：[https://ac.nowcoder.com/discuss/1500141?type=0](https://ac.nowcoder.com/discuss/1500141?type=0)
- **核心提问与考察点**：如何增加HTTP服务器连接数、如何跨进程传socket？；有限内存统计100GB文件不同记录数怎样设计？；数据库B+树、MVCC、日志和缓存一致性如何说明？；从HTTP服务器升级HTTPS需要哪些改动？；手写多生产者多消费者队列、shared_ptr、非阻塞ringbuffer及线程池；返回局部string的c_str代码有什么生命周期问题？。

### INT95 · 26届秋招字节后端一面面经详细版（后端｜09-01一面；通过直接链接可关联旧INT29后续2025秋招时间线，本条不单独从编辑年补年）
- **原文链接**：[https://www.nowcoder.com/discuss/795684745727250432](https://www.nowcoder.com/discuss/795684745727250432)
- **核心提问与考察点**：实习系统在上下游什么位置、负责哪些功能？；分布式系统如何保证一致性？；最大技术挑战是什么，如何解决？；Java和C++、GC机制以及Redis热Key怎样说明？；10GB文件只有1GB内存如何求IP频次Top10，分片后计数仍放不下怎么办？；现场实现树节点求和与接雨水。

### INT96 · 5月21日25届春招 字节后端一面面经（后端｜05-21一面，事件年未知；标题25届指届别，2025-05-21为发布日）
- **原文链接**：[https://ac.nowcoder.com/discuss/1509544?type=0](https://ac.nowcoder.com/discuss/1509544?type=0)
- **核心提问与考察点**：点评项目实际用哪些Redis结构、分别解决什么业务问题？；Canal监听binlog如何工作，延迟及版本冲突怎样处理？；兑换码如何保证安全、唯一、不可重复兑换？；除了雪花算法还有哪些唯一性方案，回拨怎么处理？；字符串能否由字典构成，若每项只能使用一次如何修改？。

### INT97 · 后端与全栈面经一次性放出（混合｜2026-07-16至09-07多公司已结束流程；仍在进行的公司不混入失败结果）
- **原文链接**：[https://ac.nowcoder.com/discuss/1678382?type=0](https://ac.nowcoder.com/discuss/1678382?type=0)
- **核心提问与考察点**：竞拍为什么用Redis Lua而不直接写MySQL，Lua失败能回滚吗？；Redis Stream异步落库、消费者重启、重复消费与最终结算如何保证一致？；幂等键谁生成、何时写入，Lua成功而幂等键未写入时如何处理？；Agent算法生成不合法、换弱模型或换策略后怎样评估有效性？；ReAct与Plan-and-Execute如何选择，如何定义复杂任务？；WebSocket房间和断线重连怎样实现？。

### INT98 · 百度海外业务 后端Go二面（混合｜二面年月日未知；页面09-04编辑且无年份）
- **原文链接**：[https://www.nowcoder.com/discuss/925099258619928576?urlSource=home-api](https://www.nowcoder.com/discuss/925099258619928576?urlSource=home-api)
- **核心提问与考察点**：幂等ID由谁生成，重复请求怎样得到同一ID？；为什么使用分布式事务，串行RPC不能满足什么要求？；DTM挂掉或回退库存失败怎样恢复？；k6是压单接口还是整链路，在哪里跑，Prometheus是否真实使用？；Agent任务目标谁指定，如何判断执行路径和最终结论正确？；Agent问题闭环与逐步工具调用轨迹如何记录？。

### INT99 · 26快手商业化 日常实习一二面 已OC（后端｜02-08一面、02-10二面与OC，事件年未知）
- **原文链接**：[https://www.nowcoder.com/discuss/718514450587746304?sourceSSR=users](https://www.nowcoder.com/discuss/718514450587746304?sourceSSR=users)
- **核心提问与考察点**：线程池参数、ForkJoinPool及拒绝策略如何说明？；MySQL索引、慢查询优化、MVCC和日志怎样解释？；Redis和数据库一致性如何保障？；仓管库存五个函数无bug，怎样优化代码并解释取舍？；与mentor沟通、任务完成和会议协作怎样展开？；现场实现双重检查单例与岛屿面积。

### INT100 · 京东后端实习一二面面经 Offer（后端｜09-15技术一面、09-22HR二面、09-23 OC、09-24 offer，年份未知）
- **原文链接**：[https://api-cdn.nowcoder.com/discuss/933060569995759616?sourceSSR=dynamic](https://api-cdn.nowcoder.com/discuss/933060569995759616?sourceSSR=dynamic)
- **核心提问与考察点**：订单对账怎样做，订单ID何时生成？；为什么使用Lua，原子性和具体特点是什么？；下单十分钟未支付自动关闭怎样实现？；Codex和Cursor有什么区别，怎样组织AI辅助开发流程？；Agent为什么按开发流程执行，流程如何定义与核验？；实习中最大挑战怎样解决，效果怎样验证？。

### INT101 · 快手商业化垂直业务 Java日常实习（后端｜2025-02-25投递、2025-02-26一面）
- **原文链接**：[https://www.nowcoder.com/discuss/726371483039133696](https://www.nowcoder.com/discuss/726371483039133696)
- **核心提问与考察点**：RocketMQ动态路由怎样打环境标识，MQ-bus覆盖部门还是平台，是否SDK化？；OOM怎样定位处理，消息分区术语是否准确？；订单水平分片不按商家路由查询时怎么办？；千万行数据的B+树高度怎样估计，何时不适合建索引？；Redis结构、缓存击穿怎样处理？；现场实现接雨水。

### INT102 · 字节AI Agent实习面经（Agent工程｜08-13一面、08-16二面，年份未知）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/8a553bb6ea8445d0b0abe11e87614cea?sourceSSR=%E5%85%B6%E4%BB%96](https://www.nowcoder.com/feed/main/detail/8a553bb6ea8445d0b0abe11e87614cea?sourceSSR=%E5%85%B6%E4%BB%96)
- **核心提问与考察点**：Coding Agent架构是什么，ReAct与Plan适用于什么场景？；上下文压缩保留什么，如何防止丢失用户关键约束？；路径震荡怎样定位，长期Memory如何提取存储检索？；工具过多或返回过长时如何控制上下文？；Prompt Cache怎样提升命中，小模型如何分工？；多个Agent同时修改同一文件怎样避免冲突？。

### INT103 · 实习面经分享 阿里云AI应用开发一面（Agent工程｜一面年月日未知；astra卡片页面05-05无年份）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/775b45a6884f4688bc1e24ad8023183b](https://www.nowcoder.com/feed/main/detail/775b45a6884f4688bc1e24ad8023183b)
- **核心提问与考察点**：Agent系统如何评价，实习遇到的问题如何解决？；幻觉如何处理？；重新做一次项目会改进什么？；资源调度场景如何设计分析调度Agent？；01背包若同时约束重量、体积或n种资源怎样扩展？。

### INT104 · 美团Agent开发一面 日常（Agent工程｜一面约75分钟，年月日未知）
- **原文链接**：[https://api-cdn.nowcoder.com/feed/main/detail/58159306df52463ab75d72daa80d66df?sourceSSR=subject](https://api-cdn.nowcoder.com/feed/main/detail/58159306df52463ab75d72daa80d66df?sourceSSR=subject)
- **核心提问与考察点**：为什么用RAG而不让Agent直接grep原文/代码，忽略token时各有什么损益？；无标题Markdown怎样切块，短query与长chunk如何比较并做对照？；关键词与向量召回如何互补，长query如何处理？；怎样判断幻觉，如何识别剩余1%到2%的错误？；为什么选Plan-and-Execute而非ReAct，Harness承担哪些上下文职责？；Milvus与手写余弦检索有何差别，存储检索机制是否读过？。

### INT105 · 字节Agent一面面经 挂了（Agent工程｜秋招一面约45分钟，年月日未知）
- **原文链接**：[https://www.nowcoder.com/feed/main/detail/9e1506be1bd54e8fb83c764cf724a20b?sourceSSR=dynamic](https://www.nowcoder.com/feed/main/detail/9e1506be1bd54e8fb83c764cf724a20b?sourceSSR=dynamic)
- **核心提问与考察点**：项目最大挑战是什么、怎样解决？；RAG的chunk具体流程和细节是什么？；Embedding模型怎样选择，依据是什么？；内存溢出和泄漏如何区分及解决？；TCP怎样保证可靠性？；实习经历中的具体实现是什么；算法题题面未公开。

### INT106 · 2025春招实习面经汇总 已接阿里offer（算法对照｜2025春招，02月至04月多公司流程）
- **原文链接**：[https://www.nowcoder.com/discuss/736868736837173248?sourceSSR=dynamic](https://www.nowcoder.com/discuss/736868736837173248?sourceSSR=dynamic)
- **核心提问与考察点**：算子优化如何检测提升，怎样排除GPU精度算力差异？；TRT-LLM、vLLM和SGLang的加速手段与PagedAttention怎样比较？；连续批处理和Prefix Cache按什么维度切分，依据是什么？；量化和算子优化最终数值是什么，有哪些测量条件？；GPU内存管理和流量调度怎样设计，指标冲突如何取舍？；CUDA手写Softmax2D、All-Reduce及伪代码MHA。

---

## 第二部分：18 份工业界专业观点汇总

### OP01 · 时隔六年，曝光一下我的最新简历！
- **原文链接**：[https://www.bilibili.com/video/BV1DCDjBRExV/](https://www.bilibili.com/video/BV1DCDjBRExV/)
- **核心工程判断**：仅标题/简介可见的定位或主张（并非已核验视频观点）：可见简介主张简历展示AI经验、架构能力和项目搭配，而不只列工具名。

### OP02 · 27届问：简历写了AI项目，但是只是名词，没有实际业务
- **原文链接**：[https://www.bilibili.com/video/BV1r2jc6mEWq/](https://www.bilibili.com/video/BV1r2jc6mEWq/)
- **核心工程判断**：仅标题/简介可见的定位或主张（并非已核验视频观点）：简介反对同质化AI模板及纯名词堆积，强调业务难点、岗位侧重点和项目与考点的区分。

### OP03 · 【终于把项目讲明白了】如何封装简历上的项目？
- **原文链接**：[https://www.bilibili.com/video/BV1EE411T7HF/](https://www.bilibili.com/video/BV1EE411T7HF/)
- **核心工程判断**：仅标题/简介可见的定位或主张（并非已核验视频观点）：视频简介聚焦项目亮点写法、流程表达与面试沟通；适用于整理讲述结构。

### OP04 · 《Agent 评测白皮书》系列01：Agent 评测全览
- **原文链接**：[https://zhuanlan.zhihu.com/p/2081333572456206815](https://zhuanlan.zhihu.com/p/2081333572456206815)
- **核心工程判断**：工程难点包括真实场景覆盖、问题定位与业务价值证明。建议评测和Agent迭代联动，先建最小观测、回归集与版本门禁，再按问题扩展。

### OP05 · 程序员简历编写指南（超详细）
- **原文链接**：[https://zhuanlan.zhihu.com/p/661113978](https://zhuanlan.zhihu.com/p/661113978)
- **核心工程判断**：项目精选而非堆数量，简要交代背景与技术，重点说明本人职责、解决问题和可量化改进。

### OP06 · 有没有大佬分享一下做agent时的一些经验？（小林coding回答）
- **原文链接**：[https://www.zhihu.com/question/1982512240482619481/answer/2000174392479606071](https://www.zhihu.com/question/1982512240482619481/answer/2000174392479606071)
- **核心工程判断**：可见摘要主张从工作痛点出发设计适合Agent应用岗位表达的项目。

### OP07 · Java程序员项目：智能协同云图库
- **原文链接**：[https://www.bilibili.com/video/BV1akwGeSERK/](https://www.bilibili.com/video/BV1akwGeSERK/)
- **核心工程判断**：仅标题/简介可见的定位或主张（并非已核验视频观点）：简介展示协同图库结合数据库、缓存、权限、实时通信与AI能力的项目组织方式。

### OP08 · The rise of context engineering
- **原文链接**：[https://www.langchain.com/blog/the-rise-of-context-engineering](https://www.langchain.com/blog/the-rise-of-context-engineering)
- **核心工程判断**：作者把Agent可靠性与动态上下文的构建联系起来：按任务提供必要信息、可用工具和合适格式，并区分信息缺失与模型自身错误。短期摘要、长期偏好、检索和工具输出都属于需要控制的上下文。

### OP09 · Writing effective tools for agents — with agents
- **原文链接**：[https://www.anthropic.com/research/writing-tools-for-agents](https://www.anthropic.com/research/writing-tools-for-agents)
- **核心工程判断**：工具应围绕真实任务选取，避免把大量底层接口机械包装给Agent。评测任务需要可核结果及留出集，同时记录耗时、调用次数、token与错误；依据轨迹改进工具说明、返回字段和分页截断。

### OP10 · Java程序员如何写简历？
- **原文链接**：[https://www.zhihu.com/tardis/bd/ans/2605287243](https://www.zhihu.com/tardis/bd/ans/2605287243)
- **核心工程判断**：作者主张按目标JD组织技能与经历，以个人角色、行动和可核成果突出重点，并保持简洁、诚实。可用于检查简历表达；不能替代技术深度或项目真实性验证。

### OP11 · 有了这个网站，找编程资源再也不求人了！
- **原文链接**：[https://www.zhihu.com/tardis/bd/art/363371891](https://www.zhihu.com/tardis/bd/art/363371891)
- **核心工程判断**：原文以编程导航为例，强调解决真实查找需求，以分类、收藏、推荐和用户反馈改善链接堆砌，避免仅靠站长维护。适合思考业务闭环和信息质量，不证明底层性能。

### OP12 · 程序员鱼皮的保姆级写简历指南第一弹，基础入手带你写好简历
- **原文链接**：[https://www.bilibili.com/opus/949414868828553234](https://www.bilibili.com/opus/949414868828553234)
- **核心工程判断**：把技术名词落到掌握细节和具体实践，说明自己能用它解决什么问题。；项目简介应简短，把篇幅留给本人职责、技术选择、解决的问题和效果；区分团队整体项目与个人工作。；量化效果应来自实际测量，写出背景、方法和变化；没有测量不要编造数据。；亮点可来自对既有实现的优化与扩展，并考虑可用性、稳定性、吞吐及延迟。；了解同类技术的优缺点与场景，才能解释选型而非只列使用过的框架。；可访问的项目和实际部署能补真实性；教程项目应增加自主工作，但改名换外观本身不足以证明技术深度。

### OP13 · 大模型-Agent LangGraph 面试八股文，简单背一背 (入门级)
- **原文链接**：[https://www.zhihu.com/tardis/bd/art/32373609214](https://www.zhihu.com/tardis/bd/art/32373609214)
- **核心工程判断**：材料把图控制流、状态快照、人工中断与工具节点列为Agent实现要素，适合建立阅读框架；不能据此认定项目可靠或非toy。

### OP14 · 26年最新AI编程学习路线一条龙，5分钟速通！
- **原文链接**：[https://www.bilibili.com/opus/1216966837161426944](https://www.bilibili.com/opus/1216966837161426944)
- **核心工程判断**：先拆任务，再逐步实现和审查；检查业务、异常及安全，并留可回退版本。；将上下文预算、失败模式和调用成本列为进阶能力；AI工具使用与AI应用开发分开。

### OP15 · Linear生产Agent：B站导读与发布者公开转写稿选读
- **原文链接**：[https://www.bilibili.com/video/BV1P6tN6bEps/](https://www.bilibili.com/video/BV1P6tN6bEps/)
- **核心工程判断**：按真实工作流定义完成与人工检查点；按需加载技能/上下文；用户反馈转为回归样本，LLM评分器需人工校准。

### OP16 · 百度Comate公开演讲：反馈、工具恢复与评测取舍
- **原文链接**：[https://www.infoq.cn/article/l7BXlstUWDOBwI30miJU](https://www.infoq.cn/article/l7BXlstUWDOBwI30miJU)
- **核心工程判断**：按模型分别观察工具失败、自愈和调用轮次，定位框架适配问题。；比较单题变化及结果/效率的异常组合，避免总分掩盖回退。；按需加载工具描述，并用失败后的工具衔接改善恢复。

### OP17 · 解密互联网大厂研发流程
- **原文链接**：[https://www.bilibili.com/opus/578080002218926853](https://www.bilibili.com/opus/578080002218926853)
- **核心工程判断**：补完整交付流程、容量与失败恢复的观点；可用作项目阅读时检查证据的维度。

### OP18 · 程序员鱼皮的保姆级写简历指南第三弹 简历常见问题和建议汇总
- **原文链接**：[https://www.bilibili.com/opus/950153255348862982](https://www.bilibili.com/opus/950153255348862982)
- **核心工程判断**：直接支持两项目各有侧重；补个人工作、业务约束与前后实测的说明方法。
