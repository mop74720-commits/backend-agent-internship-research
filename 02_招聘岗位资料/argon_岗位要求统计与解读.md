# 招聘岗位要求统计与解读（24 份可比工程 JD）

> **样本概览**：共采集 **33 条** JD 线索，其中 **24 份**为可比工程岗位全文（**后端 10 份**、**Agent 工程 11 份**、**混合 3 份**）。其余 9 份（算法研究对照 5、研究工程混合 1、摘要受限 3）已单列排除，不混入工程分母。

## 一、六大核心发现

### 1. 先准备共同底座，再按岗位方向读技术
- **结论解读**：主语言/编程能力在后端 10/10、Agent 11/11、混合 3/3 中明确要求。具体语言大多按选项或示例列出，不能把Java、Go、Python、C++都列成必会。
- **代表性依据**：[JD03](https://mnowpick.nowcoder.com/m/detail/index?jobId=379097)、[JD20](https://www.nowcoder.com/jobs/detail/447232)、[JD22](https://www.nowcoder.com/jobs/detail/447247)、[JD25](https://www.nowcoder.com/jobs/detail/454300)、[JD33](https://talent.baidu.com/jobs/detail/INTERN/15f123ac-2755-4324-b5ba-25682d0f9b40)。

### 2. 后端样本重存储与工程基础，Redis/MQ不是所有岗位统一前提
- **结论解读**：后端数据库/存储要求 7/10；精确Redis 3/10、MQ 3/10。MySQL另有单列了解 2/10。JD05只写分布式缓存、JD07只写存储/缓存，不能替换成Redis/MySQL。
- **代表性依据**：[JD01](https://www.nowcoder.com/jobs/detail/437499)、[JD02](https://www.nowcoder.com/jobs/detail/437835)、[JD05](https://talent.baidu.com/jobs/detail/INTERN/ef58d698-b944-4c05-86fe-e76daffecc8b)、[JD06](https://www.shixiseng.com/intern/inn_5lxff4vehchx?pcm=pc_SearchList)、[JD07](https://www.nowcoder.com/jobs/detail/463791)、[JD20](https://www.nowcoder.com/jobs/detail/447232)、[JD21](https://www.nowcoder.com/jobs/detail/381180)。

### 3. Agent的RAG与工具要求存在强弱，评测和状态更多写在职责
- **结论解读**：Agent组RAG要求中提及 6/11（含择一 1）；工具调用 6/11（含择一 1）。评测明确要求 1/11、优先 2/11、职责 5/11；状态/记忆/恢复职责 5/11。适合据此选读真实链路，但不能把全部职责改为入职硬门槛。
- **代表性依据**：[JD08](https://www.nowcoder.com/jobs/detail/432128?urlSource=sitemap)、[JD09](https://www.nowcoder.com/jobs/detail/432353)、[JD12](https://www.nowcoder.com/feed/main/detail/22154e3d68ed481588263f61f5f616b4)、[JD14](https://www.shixiseng.com/intern/inn_py1hkw0wds9o?pcm=pc_SearchList)、[JD24](https://www.nowcoder.com/jobs/detail/441472)、[JD26](https://www.nowcoder.com/discuss/932616763089383424)、[JD27](https://www.nowcoder.com/jobs/detail/445785)。

### 4. Agent框架应用、Infra和算法研究应分别看
- **结论解读**：JD26关注Runtime、容器、隔离、状态恢复与排障；JD23/JD27偏应用系统；JD15/16/28/29/32的训练算法岗位已排除。不能用研究岗的训练/论文要求覆盖全部Agent工程实习。
- **代表性依据**：[JD23](https://www.nowcoder.com/jobs/detail/436118)、[JD26](https://www.nowcoder.com/discuss/932616763089383424)、[JD27](https://www.nowcoder.com/jobs/detail/445785)、[JD28](https://www.nowcoder.com/jobs/detail/435213)、[JD29](https://www.nowcoder.com/jobs/detail/446094)。

### 5. 混合组不是第三条普遍赛道，而是3个百度样本
- **结论解读**：混合组JD11/JD22/JD33分别偏Java开放平台、Go/Python应用后端、核心产品后端；三者都来自百度。单列用于看桥接要求，不与另外两组相加比较概率，也不能跨公司外推。
- **代表性依据**：[JD11](https://talent.baidu.com/jobs/detail/INTERN/ef30e579-2d3d-4539-ad90-884521b815c9)、[JD22](https://www.nowcoder.com/jobs/detail/447247)、[JD33](https://talent.baidu.com/jobs/detail/INTERN/15f123ac-2755-4324-b5ba-25682d0f9b40)。

### 6. 公司模板重复会影响排序，保留原数并做等权敏感性
- **结论解读**：百度7条、字节6条、阿里品牌家族4条合计17/24。腾讯云智研发JD02/JD21为不同年度的近似模板。下面同时显示JD提及率和公司等权结果；结论只解释本样本。
- **代表性依据**：[JD02](https://www.nowcoder.com/jobs/detail/437835)、[JD21](https://www.nowcoder.com/jobs/detail/381180)。

---

## 二、24 个技术主题五层统计表

> **读表指南**：每个单元格优先展示 **明确要求数/总样本数**（若含多项择一则括注 `择一N`），其后展示非零的 **单列了解 / 优先加分 / 工作职责** 频次。后三层并非入职硬门槛，同一 JD 可在不同层级同时提及同一技术。

| 技术主题 | 后端开发 (n=10) | Agent 工程 (n=11) | 混合方向 (n=3) |
| :--- | :--- | :--- | :--- |
| **编程/主语言** | **要求 10/10** · 了解 2 / 优先 3 | **要求 11/11** · 优先 1 | **要求 3/3** |
| **计算机基础** | **要求 8/10** | **要求 8/11** | **要求 3/3** |
| **网络/通信协议** | **要求 5/10** | **要求 5/11** | **要求 1/3** |
| **数据库/存储** | **要求 7/10** · 了解 2 / 职责 1 | **要求 2/11** · 优先 1 / 职责 3 | **要求 2/3** |
| **MySQL（精确）** | **要求 4/10** · 了解 2 | **要求 0/11** | **要求 1/3** |
| **缓存（含Redis）** | **要求 5/10** | **要求 1/11** | **要求 2/3** |
| **Redis（精确）** | **要求 3/10** | **要求 0/11** | **要求 1/3** |
| **消息队列** | **要求 3/10** | **要求 0/11** · 职责 1 | **要求 1/3** · 优先 1 |
| **后端框架/接口** | **要求 3/10** | **要求 0/11** · 职责 1 | **要求 1/3** · 职责 1 |
| **系统设计/架构** | **要求 3/10** · 职责 5 | **要求 5/11** · 优先 1 / 职责 2 | **要求 1/3** · 职责 2 |
| **分布式/并发/高可用** | **要求 2/10** · 优先 3 / 职责 3 | **要求 3/11** (择一1) · 优先 1 / 职责 2 | **要求 0/3** · 优先 2 |
| **测试/代码与交付质量** | **要求 4/10** | **要求 3/11** · 职责 2 | **要求 1/3** |
| **日志/观测/排障** | **要求 1/10** · 职责 1 | **要求 2/11** · 职责 5 | **要求 0/3** · 优先 1 / 职责 1 |
| **容器/云原生/沙箱** | **要求 0/10** | **要求 2/11** (择一2) · 优先 1 / 职责 2 | **要求 1/3** |
| **Agent认知/框架/实践** | **要求 0/10** · 职责 1 | **要求 8/11** (择一1) · 优先 4 / 职责 5 | **要求 0/3** · 优先 1 / 职责 2 |
| **LLM原理/应用认知** | **要求 0/10** | **要求 4/11** · 优先 1 | **要求 0/3** · 优先 1 |
| **RAG/检索** | **要求 0/10** | **要求 6/11** (择一1) · 优先 2 / 职责 3 | **要求 0/3** · 优先 1 / 职责 1 |
| **工具调用/工具协议** | **要求 0/10** | **要求 6/11** (择一1) · 优先 1 / 职责 4 | **要求 0/3** · 优先 1 / 职责 1 |
| **Prompt/上下文工程** | **要求 0/10** | **要求 4/11** · 职责 3 | **要求 0/3** · 职责 1 |
| **状态/记忆/恢复** | **要求 0/10** | **要求 0/11** · 职责 5 | **要求 0/3** |
| **评测/效果指标** | **要求 0/10** | **要求 1/11** · 优先 2 / 职责 5 | **要求 0/3** |
| **训练/微调认知或经历** | **要求 0/10** | **要求 2/11** · 优先 4 / 职责 2 | **要求 0/3** |
| **鉴权/安全隔离** | **要求 2/10** | **要求 1/11** (择一1) · 职责 3 | **要求 0/3** · 优先 1 / 职责 1 |
| **项目/开源/贡献经历** | **要求 0/10** · 优先 2 | **要求 0/11** · 优先 5 | **要求 0/3** · 优先 2 |

---

## 三、代表性 JD 精读推荐路线

### 后端方向

- **[JD20 · 字节跳动 后端工程师开发 实习](https://www.nowcoder.com/jobs/detail/447232)**：Java基础与缓存/MQ/幂等的明确要求最具体；先看原文哪些是资格、哪些是优先。
- **[JD05 · 后端实习工程师（J93985）](https://talent.baidu.com/jobs/detail/INTERN/ef58d698-b944-4c05-86fe-e76daffecc8b)**：看Go/Java、RPC、缓存、MySQL优化怎样连接智能体业务；不要凭业务名推全部Agent门槛。
- **[JD02 · 后台开发-2027届暑期实习生](https://www.nowcoder.com/jobs/detail/437835)**：看语言择一、CS/网络必备、数据库了解和分布式加分四者的层级。
- **[JD30 · 快手 留用实习 C++开发工程师 深圳](https://www.nowcoder.com/jobs/detail/442097)**：C/C++/Rust系统后端对照；分布式海量查询是工作内容，不是统一前置组件清单。

### Agent工程方向

- **[JD08 · AI Agent开发实习生-计算](https://www.nowcoder.com/jobs/detail/432128?urlSource=sitemap)**：先看基础语言/算法与Agent经验优先的低门槛表达，再看职责范围。
- **[JD09 · 后端开发实习生-飞书（Agent/RAG）](https://www.nowcoder.com/jobs/detail/432353)**：看后端基础、LLM/RAG认知与检索/对话/评测职责的连接。
- **[JD23 · 淘天集团 AI Agent应用开发工程师 2026暑期实习](https://www.nowcoder.com/jobs/detail/436118)**：看Agent系统、上下文和工具协议的明确要求，以及训练/评测优先项。
- **[JD14 · Agent研发工程师（实习生）](https://www.shixiseng.com/intern/inn_py1hkw0wds9o?pcm=pc_SearchList)**：看规划、异常恢复与成功率职责；实习时长冲突需投递前核对。
- **[JD26 · 腾讯云 Agent Runtime 校招与日常实习](https://www.nowcoder.com/discuss/932616763089383424)**：单列Agent Infra；看Runtime/隔离/持久状态与实验定位，不强套给应用岗。

### 混合方向

- **[JD11 · AI开放平台研发工程师实习生（J103363）](https://talent.baidu.com/jobs/detail/INTERN/ef30e579-2d3d-4539-ad90-884521b815c9)**：后端基础硬要求，Agent/MQ/网关等优先，适合逐层读。
- **[JD22 · 百度 大模型应用开发 后端开发工程师 实习生](https://www.nowcoder.com/jobs/detail/447247)**：Go与Python并列要求；测试/容器是要求，Agent/RAG是职责。
- **[JD33 · 百度 大模型应用后端研发实习生 GO/Python方向 J101073](https://talent.baidu.com/jobs/detail/INTERN/15f123ac-2755-4324-b5ba-25682d0f9b40)**：检查标题与正文语言不一致；正文不支持Python明确必会。

---

## 四、编码方法与阅读边界

- **五层独立编码**：每份 JD 均由人工核对正文语义，划分为 `R`（明确要求）、`O`（明确择一选项）、`F`（原文单列了解项）、`P`（优先/加分项）、`D`（工作职责），绝不按关键词出现自动升级为硬门槛。
- **编程语言口径**：区分“单独或并列指定”、“明确择一”与“连接词未明”；如 JD22 并列要求 Golang 与 Python，JD33 正文不计入仅在标题出现的 Python。
- **公司去重敏感性**：百度（7份）、字节（6份）、阿里家族（4份）合计占 17/24；完整 HTML 页面同时提供“按 JD 等权”与“按公司等权平均”的双重对比图。

配套文件：[岗位要求统计与解读.html](argon_岗位要求统计与解读.html) · [技术项逐JD编码.csv](argon_技术项逐JD编码.csv) · [岗位统计_可读版.json](../08_证据索引与统计/argon_岗位统计_可读版.json)
