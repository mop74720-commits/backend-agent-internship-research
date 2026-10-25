"""本轮本人履历、指定源码与面经增量；只读公开来源，不执行被研究项目。"""
from copy import deepcopy
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent


def load(name):
    return json.loads((BASE / name).read_text(encoding='utf-8-sig'))


def taxonomy(track, recruitment, event, source, known=False):
    return {'track': track, 'recruitment': recruitment, 'experience_date_text': event,
            'date_precision': '范围' if known else '未知', 'year_confirmed': known,
            'recent_status': '近期确认' if known else '年份未知', 'source_date_text': source,
            'date_basis': '本人CV直接写实习起止年月' if known else '未取得明确事件年；届别、发表时间、仓库时间不替代事件年'}


def reading(scope, note):
    return {'scope': scope, 'fulltext': scope == '全文', 'scope_note': note, 'video_watched': False}


def node(url, basis, gap='', relation='直接点名'):
    return {'url': url, 'direct_basis': basis, 'gap': gap, 'relation': relation}


def merge(old, new):
    by = {r['id']: r for r in old}
    for r in new:
        if r['id'] in by:
            assert by[r['id']].get('source_key') == r.get('source_key'), r['id']
        by[r['id']] = r
    return list(by.values())


def apply(rows, comparison):
    if not (BASE / '近期Agent补链_脱敏简历.json').exists():
        return rows, comparison, {}
    snapshot = BASE / '近期Agent补链前主数据快照.json'
    if not snapshot.exists():
        snapshot.write_text(json.dumps({'records': rows, 'comparison': comparison}, ensure_ascii=False, indent=2), encoding='utf-8')
    cv_file = load('近期Agent补链_脱敏简历.json')
    sprout = load('近期Agent补链_Sprout源码归档.json')
    noworries = load('近期Agent补链_NoWorries选读归档.json')
    pr = load('近期Agent补链_个人PR核对.json')
    home = 'https://imyihang.com/'
    cv_url = cv_file['url']
    records = []
    c = {'id': 'CV31', 'source_key': 'YIHANG_AGENT_INTERNSHIP', 'category': '候选人资料',
         'title': '黄一航：中科曙光Agent实习完整履历与本人项目', 'url': home,
         'role': 'Agent应用工程实习；另有AI产品实习', 'date': '中科曙光2025.12–2026.02；饭团外卖2024.11–2025.02',
         'source_date': '2026-10-23读取公开CV及主页；非投递时间',
         'profile_type': '完整公开PDF履历的脱敏专业模块副本', 'document_type': '完整专业履历脱敏副本',
         'taxonomy': taxonomy('Agent工程', '实习', '中科曙光Agent开发实习2025.12–2026.02；AI产品实习另列', '公开版本读取2026-10-23', True),
         'reading': reading('全文', '公开PDF全部专业模块已读；主页按履历、项目及直接链接核读；未调用网页AI分身'),
         'outcome': '本人CV明确Agent开发实习经历；SSP/SP未披露',
         'outcomes': [{'company': '中科曙光', 'role': 'Agent开发实习生（RAG/多智能体方向）', 'grade': '未披露',
                       'status': 'internship_experience_self_report', 'date': '2025.12–2026.02', 'evidence_url': cv_url,
                       'basis': 'CV实习经历第一段：Dify HR Agent、企业RAG、SFT题目交叉验证及飞书质检',
                       'boundary': '产业企业应用工程经历；不改称互联网大厂SSP；指标为作者自述', 'independent_employer_verified': False},
                      {'company': '饭团外卖', 'role': 'AI应用产品实习生', 'grade': '未披露', 'status': 'internship_experience_self_report',
                       'date': '2024.11–2025.02', 'evidence_url': cv_url, 'basis': 'CV第二段；产品评测和迭代职责',
                       'boundary': '产品经历单列，不当Agent研发录用或研发技术门槛', 'independent_employer_verified': False}],
         'stack': ['Python', 'TypeScript', 'Electron', 'Dify', 'RAG', 'Tool Calling', '多智能体', 'Flask', 'PostgreSQL'],
         'projects': [{'name': 'NoWorries', 'url': noworries['source_url'], 'relation': 'CV直接列仓库URL；OpenWork二次开发边界明确'},
                      {'name': 'Sprout', 'url': sprout['source_url'].replace('https://codeload.github.com/', 'https://github.com/').replace('/zip/', '/tree/'),
                       'relation': '本人主页Sprout段直接链接；未在本次PDF中列出，不冒称投递项目'},
                      {'name': 'OpenClaw PR3064', 'url': pr['html_url'], 'relation': '主页直接链接，API核作者hlbbbbbbb及合并；仅核具体端点修复'}],
         'source_summary': '完整CV有明确Agent实习时间和职责，且直接链接NoWorries；主页另链Sprout与合并PR。可研究调度、记忆及权限的真实实现差距；内部实习源码、本人面经和SSP仍缺。',
         'complete_redacted_cv_file_received': True, 'complete_cv_file_received': False, 'cv_file_licensed_for_redistribution': False,
         'redacted_cv_local_file': cv_file['local_path'], 'ssp_claim_present': False, 'ssp_grade_company_explicit': False,
         'has_confirmed_personal_interview_source': False, 'has_direct_named_project_or_contribution': True, 'personal_source_code_verified': True,
         'chain': {'outcome': [node(cv_url, 'Agent实习的主体、职责及起止年月直接列于CV', '仅本人履历自述；无SSP')],
                   'profile': [node(cv_url, '教育、两段实习、项目与专业技能完整保留', '公开现版，非求职当时投递版')],
                   'project': [node(noworries['source_url'], 'CV直接列NoWorries仓库；本包固定14文件选读', '继承框架和独立贡献比例未审全；未运行'),
                               node(home, '主页Sprout段直接链接本人仓库', '2026.07源码晚于2026.02实习结束，不倒推录用因果'),
                               node(pr['html_url'], 'PR作者hlbbbbbbb、2026-01-28合并已由API核对', '端点修复事实不证明整库均本人原创')],
                   'interview': [node(None, '未定位本人公开求职面经', '网页AI分身的FAQ不当真实面试', '未建立')]},
         'weaknesses': ['实习为产业Agent应用工程，互联网大厂目标仍需对照；未披露SSP。', 'NoWorries基于OpenWork/OpenClaw等；只核指定路径及一项PR，不全归原创。',
                        '问答准确率、用时、订单与商业指标均为本人自述，测试及运行效果未复现。', '主页演示窗口自称动画；AI分身FAQ不代表实际面经。',
                        'Sprout为编排机制参考，当前未见持久化恢复或真实外部工具执行；NoWorries存在所读权限组件风险。'],
         'recommendation': '精读CV职责与本人代码关系；按项目机制及静态风险选读，独立核评测与贡献。',
         'source_record': {'author': '黄一航', 'source_url': cv_url, 'home': home, 'attachment': cv_file,
                           'professional_modules': cv_file['professional_modules'], 'direct_source_relationship': 'CV→NoWorries；主页→Sprout及PR3064',
                           'commercial_background': '主页推广本人产品；PowerMyWeb开放Free/Pro订阅、ContractLens商业应用，具体收入未核'}}
    c['chain_gaps'] = list(dict.fromkeys(n['gap'] for v in c['chain'].values() for n in v if n.get('gap')))
    records.append(c)
    for ident, archive, is_sprout in [('PRO24', sprout, True), ('PRO25', noworries, False)]:
        repo, sha = archive['repo'], archive['sha']
        url = f'https://github.com/{repo}/tree/{sha}'
        prefix = '' if is_sprout else 'noworries_app/apps/desktop/src/main/'

        def cell(status, finding, path, scope='指定段落静态核读；未运行'):
            return {'status': status, 'finding': finding, 'source_URL': f'https://github.com/{repo}/blob/{sha}/{path}',
                    'read_paths': [path], 'read_scope': scope}

        tree = 'sprout/task_tree.py' if is_sprout else prefix + 'clawdbot/memory/episode-memory.ts'
        worker = 'sprout/worker.py' if is_sprout else prefix + 'sandbox/index.ts'
        tests = 'tests/test_task_tree.py' if is_sprout else 'noworries_app/apps/desktop/__tests__/integration/main/permission-api.integration.test.ts'
        own = '本人主页直接链接；当前源码晚于实习结束，不证明投递时使用或促成录用。' if is_sprout else '本人CV直接列仓库；基于OpenWork/OpenClaw/Pi Agent，未逐diff核全库原创比例；PR3064只核端点修复。'
        backend = {
            '业务闭环': cell('未核' if is_sprout else '文档宣称', '任务树编排库，不是完整业务应用。' if is_sprout else '桌面文件/办公Agent为作者定位；本次只核指定组件，未完成端到端任务。', 'README.md'),
            '一致性': cell('未核', '核读路径为内存节点状态，未见持久化重启恢复。' if is_sprout else '月度JSON读写可见；跨进程及崩溃一致性未验证。', tree),
            '并发': cell('源码可见' if is_sprout else '未核', 'asyncio并行子任务及LLM信号量可定位；资源预算仍需独立核对。' if is_sprout else '记忆与执行组件可读，整体并发、重入及取消传播未审全。', tree),
            '缓存MQ': cell('不适用', '本次未核业务缓存/MQ能力，不把记忆或任务树当消息队列。', 'README.md'),
            '测试': cell('源码可见', '有mock Worker/LLM的拆分、重拆与预算测试；不证明真实任务质量。' if is_sprout else '权限测试核到ID前缀、函数和服务创建，未覆盖全部沙箱隔离与降级路径。', tests),
            '可运行材料': cell('未核', '原仓有pyproject与示例；本轮未安装依赖或调用模型。' if is_sprout else '归档仅14指定文本；未下载bundled Python、全部源码或运行依赖，不能直接当完整可运行包。', 'pyproject.toml' if is_sprout else 'README.md'),
            '个人贡献': cell('文档宣称', own, 'README.md')}
        if is_sprout:
            agent = {
                '真实任务': cell('文档宣称', '示例是代码文本生成任务；未验证真实外部业务执行。', 'examples/benchmark.py'),
                '状态工具': cell('源码可见', 'analyze拆分/execute报告或放弃/synthesize，节点状态、上下文及事件可定位；所读Worker未执行真实外部工具。', 'sprout/worker.py'),
                '恢复': cell('源码可见', '有拖慢子任务取消/重拆和失败回退；不等于进程重启恢复或副作用幂等。', tree),
                '权限': cell('未核', '树形和token限制属于资源约束；未核文件、网络或业务动作授权隔离。', 'sprout/config.py'),
                '评测基线': cell('静态风险', 'benchmark L91–164用正则/关键字为输出文本打分，不执行生成代码；25→100分不等于任务正确率或成功率。', 'examples/benchmark.py'),
                '成本延迟': cell('静态风险', '节点开始前查已用token，调用结束后累计；并发调用及合成阶段未见逐次预留/硬限，存在超支风险，未运行复现。', tree),
                '超API封装证据': cell('源码可见', '多节点拆分、并行、拖慢检测及合成有代码；作为机制参考，不冒充成熟业务Agent。', tree),
                '个人贡献': cell('文档宣称', own, 'README.md')}
            strengths = ['两阶段Worker、树形调度和拖慢检测均有具体代码。', 'mock测试覆盖部分控制流，便于学习测试边界。']
            limits = ['benchmark文本特征分不代表功能正确；未复现任何模型效果。', '预算检查不构成硬费用上限；配置max_retries与LLM内硬编码重试也未贯通。', '执行路径未见持久化检查点，Worker工具主要为报告结果/放弃；不是完整外部动作闭环。', own]
            modules = ['sprout/task_tree.py', 'sprout/worker.py', 'sprout/llm.py', 'examples/benchmark.py', 'tests/test_task_tree.py']
        else:
            agent = {
                '真实任务': cell('文档宣称', '本人CV与主页定位桌面办公助手，未运行真实文件/表格任务。', 'README.md'),
                '状态工具': cell('源码可见', '情景记忆按月JSON保存；有关键词检索及记忆衰减/提升逻辑，整体接线未审全。', tree),
                '恢复': cell('静态风险', 'macOS执行器L164–175将零退出且无输出的结果转入环境变量隔离并再次执行，存在重复副作用和隔离降级风险；未运行复现。', prefix + 'sandbox/macos-sandbox.ts'),
                '权限': cell('静态风险', 'Windows以cwd/HOME等环境变量和PowerShell Bypass执行；Linux也为环境变量模式。所读组件不构成系统级文件隔离，整体授权入口未审全。', prefix + 'sandbox/windows-sandbox.ts'),
                '评测基线': cell('未核', '未核桌面任务黄金集、成功率及长期记忆效果；所读权限测试不等于端到端任务评测。', tests),
                '成本延迟': cell('未核', '未核整体任务的token、费用和时延；不从UI动画或模块存在推定生产效果。', 'README.md'),
                '超API封装证据': cell('源码可见', '记忆、执行器和权限组件有实现；安全与恢复仍有静态缺口。', worker),
                '个人贡献': cell('文档宣称', own, 'README.md')}
            strengths = ['本人CV直接链接实现；记忆存储、检索及执行组件可静态审查。', '一个本人端点修复PR已核合并；继承框架与该具体增量分别呈现。']
            limits = ['Windows/Linux环境重定向不是系统级隔离；macOS回退可能重复执行并降低隔离。', 'workspace-manager L65–73仅用字符串前缀判子目录，未核路径组件边界/符号链接；属于静态风险。', '仅归档14文件选读，未核整体运行、任务评测、回滚和各平台完整授权接线。', own]
            modules = [prefix + 'sandbox/macos-sandbox.ts', prefix + 'sandbox/windows-sandbox.ts', prefix + 'sandbox/workspace-manager.ts', tree, prefix + 'clawdbot/memory/memory-consolidation.ts']
        title = 'Sprout：任务树编排、预算与文本打分边界' if is_sprout else 'NoWorries：桌面记忆与跨平台隔离风险选读'
        archive_file = str(Path(archive['local_path']).relative_to('05_项目源码归档')).replace('\\', '/')
        cp = {'id': ident, 'title': title, 'repo': repo, 'source_URL': url, 'commit': sha,
              'source_nature': ['本人主页直接链接' if is_sprout else '本人CV直接链接', '编排机制参考' if is_sprout else '继承框架上的桌面应用'],
              'candidate_relationships': [{'candidate_id': 'CV31', 'relationship_type': '直接点名', 'direct_evidence_URLs': [home if is_sprout else cv_url],
                                          'finding': own, 'event_time_boundary': '实习2025.12–2026.02，固定源码2026.07', 'snapshot_boundary': '当前固定版本不是投递版本', 'offer_causality': '不证明项目促成录用'}],
              'backend_dimensions': backend, 'agent_dimensions': agent,
              'backend_priority': {'level': '选读', 'reason': '用于并发/状态及故障边界阅读；非完整后端业务样板。', 'read_modules': modules[:2]},
              'agent_priority': {'level': '选读', 'reason': '研究机制与失败路径；未验证为成熟可直接复用的成品。', 'read_modules': modules},
              'evidence_completeness': '近期Agent实习完整CV→本人主页/项目直接链接已建立；本人面经、SSP及运行验证仍缺。',
              'target_applicability': '编排机制与评测反例' if is_sprout else '记忆组件与权限/重复副作用反例',
              'attachment': {'status': '固定源码文本派生包' if is_sprout else '固定14文件文本选读派生包，非完整源码', 'archive_file': archive_file,
                             'exists': True, 'reason': archive['execution'], 'source_manifest': '08_证据索引与统计/' + ('近期Agent补链_Sprout源码归档.json' if is_sprout else '近期Agent补链_NoWorries选读归档.json'), 'runtime_verified': False},
              'read_paths': modules, 'strengths': strengths, 'limitations': limits, 'commercial_background': '作者主页推广本人产品与订阅；本仓MIT，不据此保证部署/服务无成本。',
              'run_status': '未运行、未构建、未调用模型或执行模型代码。', 'source_nature_boundary': own,
              'priority_interpretation': '本人归属和录用经历不自动证明项目成熟度；逐项读代码、文档和风险。'}
        comparison['projects'] = merge(comparison['projects'], [cp])
        records.append({'id': ident, 'source_key': 'YIHANG_' + ('SPROUT' if is_sprout else 'NOWORRIES'), 'category': '项目参考',
                        'title': title, 'url': url, 'author': 'hlbbbbbbb', 'commit': sha,
                        'taxonomy': {**taxonomy('Agent工程', '不适用', '源码版本2026.07，非招聘事件', '固定提交'), 'recent_status': '不适用'},
                        'reading': reading('部分', '指定代码段、许可及测试断言核读；未逐行审定整仓'), 'outcomes': [],
                        'source_findings': strengths + limits, 'strengths': strengths, 'limitations': limits,
                        'recommended_use': cp['target_applicability'], 'archive_file': archive_file, 'archive_status': cp['attachment']['status'],
                        'license_notes': archive['license'], 'project_relationship': own, 'candidate_links': ['CV31'],
                        'source_record': archive, 'comparison': cp})
    transcript = 'https://github.com/petergyang/behind-the-craft-transcripts/blob/fee802bad021ed071dc55b1a6e45c5ac1b5c114c/transcripts/2026/159-5-rules-for-building-ai-agents-that-work-in-production-nan-yu-jacob-shumway.md'
    records.append({'id': 'OP15', 'source_key': 'LINEAR_PRODUCTION_AGENT_PRIMARY_TRANSCRIPT', 'category': 'B站与知乎',
                    'title': 'Linear生产Agent：B站导读与发布者公开转写稿选读', 'url': 'https://www.bilibili.com/video/BV1P6tN6bEps/',
                    'platform': 'B站视频公开导读；原始播客逐字稿为平台外来源', 'author': 'B站Easonlee；原访谈Nan Yu/Jacob Shumway，主持Peter Yang',
                    'taxonomy': {**taxonomy('Agent工程', '不适用', '专业观点，非招聘事件', 'B站2026-08-28；原访谈2026-08-09'), 'recent_status': '不适用'},
                    'reading': reading('部分', 'B站公开导读选读，视频未观看；原始公开逐字稿选读开场及L69/71/79/83/87，未读整篇'),
                    'platform_native_fulltext_verified': False, 'verified_video_viewing': False, 'primary_external_transcript_selected': True,
                    'opinion': '按真实工作流定义完成与人工检查点；按需加载技能/上下文；用户反馈转为回归样本，LLM评分器需人工校准。',
                    'identity_evidence': '原始访谈页明示两位嘉宾参与构建Linear Agent；B站为转述/导读，不升格原团队署名。',
                    'commercial_bias': '原发布页有付费订阅及Oceans Talent合作；Linear为自身产品案例，效果不视为独立测评。B站作者商业关系未核。',
                    'limits': ['未观看视频、未取得B站字幕；原始逐字稿不算B站字幕。', '不将针对特定字段/意图的评测取舍泛化成所有Agent不需要评测。', '逐字稿有转写拼写错误，属于公开文本选读而非音视频逐句校对。'],
                    'recommendation': '与项目状态、权限及评测维度对读；只支持具体工程观点，不充作招聘门槛。',
                    'source_record': {'primary_url': transcript, 'primary_article': 'https://creatoreconomy.so/p/5-rules-for-building-ai-agents-in-production-linear-nan-jacob',
                                      'transcript_sha256': '797758b28016f6378e21aea99a0202799ed42505119448e858a262a09e5394a7', 'fixed_commit': 'fee802bad021ed071dc55b1a6e45c5ac1b5c114c',
                                      'reading_ranges': ['开场/循环与工作流', 'L69/71/79/83/87评测/用户反馈/按需技能'], 'bilibili_access': '网页工具可读公开导读；普通GET412',
                                      'publisher_relationship': 'GitHub公开账号petergyang的blog字段直接指向creatoreconomy.so；固定版本README明确称本人Behind the Craft频道的转写档案，自动从已发布视频更新。账号自述与来源链接对应，不等于逐句人工校对。',
                                      'publisher_readme_url': 'https://github.com/petergyang/behind-the-craft-transcripts/blob/fee802bad021ed071dc55b1a6e45c5ac1b5c114c/README.md',
                                      'media_downloaded': False, 'full_transcript_archived': False}})
    records.append({'id': 'OBS10', 'source_key': 'ZTE_LLM_SSP_NOT_AGENT_CONFIRMED', 'category': '候选人对照',
                    'title': '指数函数：中兴大模型开发SSP自述，Agent职责未披露',
                    'url': 'https://www.nowcoder.com/feed/main/detail/33e2209965c44c6e86a27ecb9e01f9b1',
                    'taxonomy': {**taxonomy('混合', '校招', '原文2025年回顾去年秋招；具体日期未核', '2025-08-08已编辑'), 'recent_status': '时间边界待核'},
                    'reading': reading('全文', '原帖公开文字正文已读，未读offer截图、评论和图片；普通GET空壳但网页工具可读'),
                    'outcomes': [{'company': '中兴', 'role': '大模型开发', 'grade': 'SSP', 'status': 'offer_self_report', 'date': '原文称去年秋招，具体事件年未直接核定',
                                  'evidence_url': 'https://www.nowcoder.com/feed/main/detail/33e2209965c44c6e86a27ecb9e01f9b1',
                                  'basis': '本人明确表示选择中兴大模型开发SSP offer', 'boundary': '不等于Agent工程/后端实习SSP；具体部门职责、源码和简历缺', 'independent_employer_verified': False}],
                    'summary': '公司、宽泛岗位与SSP自述明确；描述三轮流程与项目表达，但没有具体Agent职责或项目实现。作为大模型邻近对照，不扩大核心Agent SSP样本。',
                    'limits': ['不按话题标签或25届补写事件年。', '薪资选择与工作体验为个人自述，不推为统一招聘要求。', '未证明赞助/推广关系；正向体验不自动判广告，也不作独立测评。']})
    result = {'date': '2026-10-23', 'added_ids': [r['id'] for r in records],
              'summary': '新增一份近期Agent实习完整脱敏CV及两个本人直链项目；选读Linear公开原始逐字稿，另核中兴大模型SSP与Agent职责的边界。托马斯两篇已在OBS08收录，复核不重复增加候选人或面经数。',
              'manual': [{'title': '托马斯杨儿本人博客', 'url': 'https://blog.openingclouds.xyz/', 'status': 'TLS证书已过期，未读取博客正文',
                          'to_verify': '本人具体逐轮面经及项目源码；已有牛客选读范围保留', 'priority': '补充：本人原站', 'priority_reason': '可能补全原始轮次；访问失败不抹去牛客已读文字'},
                         {'title': 'Linear团队：构建生产级别Agent的5条规则', 'url': 'https://www.bilibili.com/video/BV1P6tN6bEps/',
                          'status': '网页工具可读公开导读，普通GET412；未观看视频、未取B站字幕。已选读发布者公开原始逐字稿，来源另列',
                          'to_verify': '视频实际内容及与原始访谈对应；不能将原稿选读记为已观看B站视频', 'priority': '优先：生产工程视频原文',
                          'priority_reason': '可与公开原始逐字稿对照，重点核评测、工作流和技能加载'}],
              'remaining': ['已补近期Agent实习者完整CV→本人开源实现；项目仍有评测/权限/恢复缺口，尚未定位同人的真实求职面经或SSP。',
                            '中兴样本只明确大模型开发SSP，未披露Agent职责；近期大厂Agent具体岗位、批次与最终档位关系仍需补强。',
                            '已选读一份生产Agent访谈的原始公开逐字稿，但B站视频/字幕仍未实际观看或读取；平台正文与原稿来源分开。']}
    (BASE / '近期Agent补链_来源核读.json').write_text(json.dumps({'date': '2026-10-23', 'scope': result, 'records': records}, ensure_ascii=False, indent=2), encoding='utf-8')
    return merge(rows, records), comparison, result
