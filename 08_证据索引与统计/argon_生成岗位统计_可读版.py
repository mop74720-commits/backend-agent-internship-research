"""从已核 JD 生成可审查的描述统计；人工语义编码，不改权威主库。"""
from collections import Counter, defaultdict
from datetime import date
from html import escape
from pathlib import Path
import csv
import hashlib
import io
import json
import re

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
OUT = ROOT / '02_招聘岗位资料'
E = lambda value: escape(str(value), quote=True)
TRACKS = ('后端', 'Agent工程', '混合')
LEVELS = {'R': '明确要求', 'O': '明确择一选项', 'F': '单列了解项', 'P': '优先/加分', 'D': '工作职责'}
TOPICS = {
 'lang': ('编程/主语言', '明确编程或语言能力；具体语言品牌另表，不把列出的语言都当必会。'),
 'cs': ('计算机基础', '明确数据结构算法、操作系统、计算机原理等；不从岗位名称或语言名推断。'),
 'network': ('网络/通信协议', '网络、TCP/UDP、IPC、RPC等明确通信要求；不因使用Web框架自动补计。'),
 'db': ('数据库/存储', '数据库或持久存储基础；泛称存储不自动等同MySQL。'),
 'mysql': ('MySQL（精确）', '只有明确写MySQL才计数，SQL/数据库泛称不计。'),
 'cache': ('缓存（含Redis）', '缓存或分布式缓存；KV存储本身不自动视为缓存。'),
 'redis': ('Redis（精确）', '仅明确出现Redis，分布式缓存不自动视为Redis。'),
 'mq': ('消息队列', 'MQ或Kafka/RocketMQ/RabbitMQ等；任选一种仍是一个岗位。'),
 'web': ('后端框架/接口', '后端框架、Spring、RESTful服务接口等明确工程要求。'),
 'arch': ('系统设计/架构', '系统设计、抽象、架构设计或明确系统架构优化。'),
 'distributed': ('分布式/并发/高可用', '明确分布式、高并发、高可用、容灾等；泛称性能或稳定性不自动补计。'),
 'quality': ('测试/代码与交付质量', '单元/集成测试、代码规范、开发测试发布流程；Agent评测集另计。'),
 'observability': ('日志/观测/排障', '日志、Trace、监控、定位问题等；效果评测另计。'),
 'cloud': ('容器/云原生/沙箱', '明确容器、Kubernetes、Serverless、沙箱等；云公司名称本身不计。'),
 'agent': ('Agent认知/框架/实践', '保留兴趣、认知、框架或实践的原深度；计数不等于有成熟Agent经验。'),
 'llm': ('LLM原理/应用认知', '明确LLM原理、应用范式/架构、API等；不由岗位标题自动补计。'),
 'rag': ('RAG/检索', '明确RAG、检索、召回、重排或索引检索链路；泛称知识工程不自动补计。'),
 'tools': ('工具调用/工具协议', 'Tool/Function Calling、MCP/A2A、工具集成与执行等；不把所有RPC都当Agent工具。'),
 'context': ('Prompt/上下文工程', 'Prompt、上下文或版本管理；线程状态、记忆、恢复另计。'),
 'state': ('状态/记忆/恢复', '对话/任务状态、记忆、持久化、暂停恢复或异常恢复。'),
 'evaluation': ('评测/效果指标', 'Agent/模型评测、回测、测试集、成功率等；不替代单元测试。'),
 'training': ('训练/微调认知或经历', '明确SFT/RL/后训练、微调或训练生命周期；不由PyTorch/Transformer名称推断。'),
 'security': ('鉴权/安全隔离', '鉴权、权限、安全隔离或明确网络安全；仅提网关不自动计。'),
 'opensource': ('项目/开源/贡献经历', '明确项目、开源、PR或基础设施实习经历；品牌框架数量不计为个人贡献。'),
}

# 每个岗位逐条阅读后确定；下列标记从不由关键词自动推断。
# R=明确要求；O=确实为某个择一条件的选项；F=原文单列了解；P=优先；D=职责。
CODES = {
 'JD01': {'R':'lang cs db mysql cache redis mq', 'D':'arch'},
 'JD02': {'R':'lang cs network db security', 'F':'lang db mysql', 'P':'distributed', 'D':'arch'},
 'JD03': {'R':'lang cs', 'D':'observability'},
 'JD04': {'R':'lang cs quality', 'P':'lang'},
 'JD05': {'R':'lang cs network db mysql cache web arch distributed', 'P':'opensource', 'D':'agent arch'},
 'JD06': {'R':'lang cs network db mysql cache redis mq', 'P':'lang', 'D':'distributed'},
 'JD07': {'R':'lang network db cache web arch quality observability', 'P':'lang', 'D':'distributed'},
 'JD08': {'R':'lang cs', 'P':'agent', 'D':'agent state security observability'},
 'JD09': {'R':'lang network db cache arch quality observability llm agent rag training',
          'P':'lang llm opensource', 'D':'tools state rag context evaluation observability'},
 'JD10': {'R':'lang cs network rag context agent', 'D':'quality'},
 'JD11': {'R':'lang cs network db mysql cache redis web',
          'P':'mq agent llm rag tools security observability distributed opensource',
          'D':'agent tools context security observability'},
 'JD12': {'R':'lang cs network llm context tools agent', 'P':'rag agent tools training opensource',
          'D':'evaluation observability'},
 'JD13': {'R':'lang', 'D':'context evaluation'},
 'JD14': {'R':'lang cs llm rag tools arch', 'P':'arch', 'D':'agent tools context state evaluation'},
 'JD20': {'R':'lang web db mysql cache redis mq arch distributed quality', 'P':'distributed'},
 'JD21': {'R':'lang cs network db security', 'F':'lang db mysql', 'P':'distributed', 'D':'arch db'},
 'JD22': {'R':'lang cs db cache mq cloud quality arch', 'D':'agent rag web arch'},
 'JD23': {'R':'lang cs agent arch distributed rag tools context', 'P':'training evaluation', 'D':'agent'},
 'JD24': {'R':'lang cs network quality db llm evaluation training', 'O':'cloud security agent rag tools',
          'P':'db distributed agent rag training opensource', 'D':'db rag tools arch distributed training'},
 'JD25': {'R':'lang agent tools arch', 'D':'agent distributed cloud mq db security arch quality training'},
 'JD26': {'R':'lang cs network agent observability quality', 'O':'cloud distributed',
          'P':'cloud agent training evaluation opensource', 'D':'agent state tools cloud security db observability'},
 'JD27': {'R':'lang cs agent arch distributed rag tools context', 'P':'opensource',
          'D':'state rag evaluation observability web'},
 'JD30': {'R':'lang cs quality', 'P':'opensource', 'D':'distributed arch'},
 'JD33': {'R':'lang cs', 'P':'distributed opensource', 'D':'arch'},
}

NOTES = {
 'JD02':'原文“有一定了解”的脚本、MySQL/SQL、NoSQL/KV从旧preferred字段拆回F层；不是加分项。',
 'JD03':'标题Java不等于正文明确要求Java；不从标题补Spring/Redis。',
 'JD05':'AI技术项目经验是优先；智能体业务名称不等于要求Agent/RAG经验。分布式缓存不补Redis品牌。',
 'JD07':'泛称存储/缓存不补MySQL/Redis；高并发、解耦在职责。',
 'JD08':'Agent/框架/Skills为优先；多Agent、记忆、鉴权、观测为职责，非全套入职门槛。',
 'JD09':'Agent/RAG/SFT为基本认知，不等于已完成模型训练；评测、对话管理为职责。',
 'JD10':'框架/平台为原文示例或任选，不要求所有品牌；深度学习框架优先不自动计模型训练实践。',
 'JD11':'MQ和Agent/RAG/MCP、网关安全/观测为优先，职责不升级为硬门槛。',
 'JD14':'LLM/RAG/Function Call/规划为认知要求；恢复、上下文、成功率在职责。正文6月与页头4月冲突保留。',
 'JD20':'栏目“岗位职责”实为学历/Java资格列表，按语义编码为要求；MQ至少一种。明确微服务项目、缓存锁等属分布式场景。',
 'JD21':'与JD02同公司相近模板、不同投递期；原文“必须具备/有一定了解/可以加分”分开。语言连接词未明确择一。',
 'JD22':'原文并列熟练掌握Golang、Python，不擅改任选；Agent/RAG/Workflow在职责。',
 'JD23':'框架列表为“等框架”；明确要求高可用/高扩展工程架构，计入分布式/并发/高可用主题。PyTorch/TensorFlow仅了解，Transformer实战、后训练、模型评测为优先。',
 'JD24':'计算机网络与代码风格规范均为原文明确要求。云原生或安全隔离二选一；至少一种Agent框架或RAG/工具/规划组件。训练/评测/部署为生命周期经验，不等于全部SFT/RL均须做。职责明确“一项或多项”。',
 'JD25':'Agent框架、工具协议为要求；沙箱/存储/训练架构是职责，不能推为已完成全部系统。',
 'JD26':'单独的Agent Infra方向；明确要求Agent兴趣且自己用过/做过/研究过，计入认知/框架/实践主题，但不等于成熟系统经验。云原生或分布式为基础认知选项；RL/评测/开源为加分。2027校招与2028+实习资格分开。',
 'JD27':'语言至少一种，框架品牌为示例；明确要求高可用/高扩展工程架构，计入分布式/并发/高可用主题。记忆状态机、自动评测和观测是职责。',
 'JD30':'C/C++或Rust；页标签Java、0天0月不采纳。海量查询不自动补数据库品牌。',
 'JD33':'标题GO/Python与正文C/C++或PHP/Go不一致；正文不计Python。',
}

# 具体语言列保持连接词。fixed只用于正文确实指定，options/listed都不能写成每种必会。
LANGUAGES = {
 'JD01':{}, 'JD02':{'options':'C C++ Java Go','familiarity':'Python Shell Perl'},
 'JD03':{'title_only':'Java'}, 'JD04':{'options':'Go C C++ Java','preferred':'Ruby Python Bash'},
 'JD05':{'options':'Go Java'}, 'JD06':{'preferred':'Go'},
 'JD07':{'options':'Go Java Python','preferred':'Go'}, 'JD08':{'options':'C C++ Python Go Java'},
 'JD09':{'options':'Go Java Python','preferred':'Go'}, 'JD10':{'options':'Python Java Go'},
 'JD11':{'fixed':'Java'}, 'JD12':{'options':'Java Python JavaScript'},
 'JD13':{'options':'Go Java Python C++'}, 'JD14':{'options':'Python Go'},
 'JD20':{'fixed':'Java'}, 'JD21':{'listed':'C C++ Java Go','familiarity':'Python Shell Perl'},
 'JD22':{'fixed':'Go Python'}, 'JD23':{'listed':'Python Java Go C++'},
 'JD24':{'options':'Java Python Go C++'}, 'JD25':{'options':'C++ Python'},
 'JD26':{'options':'Go Rust C C++'}, 'JD27':{'options':'Python JavaScript TypeScript Java Go C++'},
 'JD30':{'options':'C C++ Rust'}, 'JD33':{'listed':'C C++ PHP Go'},
}

FAMILIAR = ['Python/Shell/Perl等脚本语言有一定了解', 'MySQL及SQL有一定了解', 'NoSQL/Key-value存储原理有一定了解']
OVERRIDES = {
 ('JD11','D'):'企业级AI开放平台；API网关、鉴权配额、能力注册、调用链路、日志监控；Agent Tool/Skill/MCP接入；模型路由、上下文、流式响应。',
 ('JD20','R'):'Java/JVM/并发；Spring Boot/Cloud/MyBatis及微服务项目；MySQL；Redis缓存/分布式锁/限流；至少一种MQ及可靠性/幂等；RESTful接口与代码规范。',
 ('JD24','R'):'数据结构、算法、操作系统、计算机网络等基础；至少一门编程语言，代码风格规范；了解关系型/非关系型数据库原理；深入理解LLM原理；具备Agent全生命周期管理（训练/评测/部署）经验。',
 ('JD24','O'):'熟悉Kubernetes/Serverless云原生或Docker/gVisor安全隔离；至少一种Agent框架或RAG/工具调用/多步规划核心组件。',
 ('JD26','R'):'Go/Rust/C/C++至少一门，算法/数据结构/OS；Linux、网络、进程、文件系统；对Agent有真实兴趣，自己用过、做过或研究过Agent；借助Coding Agent开发并独立判断代码方案；用代码、日志、Trace和实验定位，推进问题定义至验证。',
 ('JD26','O'):'对Kubernetes、容器或分布式系统有基本了解，愿意深入学习。',
 ('JD27','R'):'至少一种主语言、算法和数据结构；Agent开发经验及框架原理；了解Claude Code机制，能设计高可用、高扩展性的大模型工程架构；Prompt/RAG/Tool Calling/Harness/Skills；能阐述架构权衡与技术决策。',
}


def load(name):
    return json.loads((BASE / name).read_text(encoding='utf-8-sig'))


def company_family(company):
    if '腾讯云智' in company:
        return '腾讯云智研发（独立雇主）'
    for terms, label in [(('百度',),'百度'), (('字节','抖音'),'字节跳动'),
                         (('阿里','淘天'),'阿里品牌家族'), (('腾讯',),'腾讯品牌家族'),
                         (('小米',),'小米'), (('美图',),'美图'), (('快手',),'快手')]:
        if any(term in company for term in terms):
            return label
    return company


def evidence(jd, level):
    key = (jd['id'], level)
    if key in OVERRIDES:
        return OVERRIDES[key]
    if level == 'F':
        return '；'.join(FAMILIAR)
    if level in ('R','O'):
        return '；'.join(jd.get('required_stack', []))
    if level == 'P':
        source = jd.get('preferred_stack', [])
        if jd['id'] == 'JD02':
            source = [item for item in source if '了解' not in item]
        return '；'.join(source)
    return jd.get('duties', '')


def coding(jobs):
    rows = []
    for jd in jobs:
        included = jd['id'] in CODES
        for topic, (label, _) in TOPICS.items():
            row = {'jd_id':jd['id'], 'title':jd['title'], 'track':jd['taxonomy']['track'],
                   'company':jd['company'], 'company_family':company_family(jd['company']),
                   'included':included, 'topic_id':topic, 'topic':label,
                   'source_url':jd['url'], 'source_date':jd.get('publish_date','未展示'),
                   'semantic_note':NOTES.get(jd['id'], '未列不等于不要求；只按原文语义编码。')}
            for level in LEVELS:
                hit = topic in CODES.get(jd['id'], {}).get(level, '').split()
                row[level] = hit
                row[level+'_basis'] = evidence(jd, level) if hit else ''
                if hit:
                    assert row[level+'_basis'], (jd['id'], topic, level)
            row['absence_meaning'] = '未明示/未核，不能推断不要求' if included else '排除于24条工程比较，不参与比例'
            rows.append(row)
    return rows


def date_scope(jds):
    counts = Counter()
    for jd in jds:
        if not jd['taxonomy'].get('year_confirmed'):
            counts['年份未知'] += 1
        else:
            years = re.findall(r'20\d{2}', jd.get('publish_date',''))
            counts[min(years) if years else '年份已核但本字段未给年'] += 1
    return dict(counts)


def build_stats(jobs, rows):
    groups = {}
    included = [jd for jd in jobs if jd['id'] in CODES]
    for track in TRACKS:
        jds = [jd for jd in included if jd['taxonomy']['track'] == track]
        ids = {jd['id'] for jd in jds}
        features = {}
        for topic, (label, definition) in TOPICS.items():
            selected = [row for row in rows if row['jd_id'] in ids and row['topic_id'] == topic]
            item = {'label':label, 'definition':definition}
            for level, key in [('R','required_direct'),('O','required_option'),('F','familiarity'),('P','preferred'),('D','duties')]:
                item[key+'_ids'] = [row['jd_id'] for row in selected if row[level]]
                item[key+'_count'] = len(item[key+'_ids'])
            item['required_any_ids'] = [row['jd_id'] for row in selected if row['R'] or row['O']]
            item['required_any_count'] = len(item['required_any_ids'])
            features[topic] = item
        groups[track] = {'n':len(jds), 'jd_ids':[jd['id'] for jd in jds],
                         'company_n':len({company_family(jd['company']) for jd in jds}),
                         'source_types':dict(Counter(jd['source_type'] for jd in jds)),
                         'source_date_year_counts':date_scope(jds), 'features':features}
    lang_stats = {}
    for track in TRACKS:
        ids = groups[track]['jd_ids']
        languages = sorted({lang for jid in ids for values in LANGUAGES[jid].values() for lang in values.split()})
        lang_stats[track] = {}
        for lang in languages:
            item = {}
            for level in ('fixed','options','listed','familiarity','preferred','title_only'):
                matches = [jid for jid in ids if lang in LANGUAGES[jid].get(level,'').split()]
                item[level+'_ids'] = matches
                item[level+'_count'] = len(matches)
            lang_stats[track][lang] = item
    company_map = {jd['id']:company_family(jd['company']) for jd in included}
    sensitivity = []
    for track in TRACKS:
        ids = groups[track]['jd_ids']
        companies = sorted({company_map[jid] for jid in ids})
        for topic in TOPICS:
            hits = set(groups[track]['features'][topic]['required_any_ids'])
            company_rows = []
            for company in companies:
                company_ids = [jid for jid in ids if company_map[jid] == company]
                company_hits = [jid for jid in company_ids if jid in hits]
                company_rows.append({'company':company,'jd_ids':company_ids,'hit_ids':company_hits,
                                     'within_company_fraction':len(company_hits)/len(company_ids)})
            sensitivity.append({'track':track, 'topic_id':topic, 'label':TOPICS[topic][0],
                                'jd_count':len(ids), 'required_any_count':len(hits),
                                'raw_jd_fraction':len(hits)/len(ids),
                                'company_count':len(companies),
                                'company_equal_weight_fraction':sum(row['within_company_fraction'] for row in company_rows)/len(companies),
                                'companies_with_any_mention':sum(bool(row['hit_ids']) for row in company_rows),
                                'company_rows':company_rows})
    excluded = []
    for jd in jobs:
        if jd['id'] in CODES:
            continue
        reason = ('仅摘要/原页受限，不能进入全文分母' if not jd['reading']['fulltext'] else
                  '算法研究对照，不与工程门槛混计' if jd['taxonomy']['track']=='算法对照' else
                  '研究与工程混合对照，保持现行matrix_include=false，不擅改比较范围')
        excluded.append({'id':jd['id'],'title':jd['title'],'reason':reason,'url':jd['url']})
    input_names = ['all_evidence_records.json','技术要求_明确要求与加分项.json','astra合并_JD核对.json']
    return {'date':'2026-10-24', 'title':'岗位要求统计与解读',
            'source_files':[{'file':'08_证据索引与统计/'+name,'sha256':hashlib.sha256((BASE/name).read_bytes()).hexdigest()} for name in input_names],
            'denominators':{'all_jd':len(jobs),'engineering_fulltext':len(included),
                            'by_track':{key:value['n'] for key,value in groups.items()},'excluded':len(excluded)},
            'rules':['统计单位是独立JD，不是公司、录用者、面试轮次或SSP名额。',
                     '24条中明确要求/择一选项/单列了解/优先加分/职责五层独立编码，不把职责当门槛。',
                     '同一JD可以在要求、优先和职责同时出现同一技术，层级计数不能相加。',
                     '要求中提及=直接明确要求或明确择一选项；选项不能解释为该技术单独必需。',
                     '了解/兴趣/基本认知与熟练开发的强度不同；数量不认证技能深度。',
                     '“单列了解项”特指原文单设的了解栏目；其余要求也可能只要求认知，不能把“要求”全解读为熟练实践。',
                     '未提及不能解释为不考；便利样本比例不能估计就业市场概率。',
                     '年份来自页面日期/投递窗口/明确标题，不按届别或抓取时间补年；不是当前HC核验。'],
            'topics':[{'id':key,'label':label,'definition':definition} for key,(label,definition) in TOPICS.items()],
            'groups':groups, 'excluded':excluded, 'language_mentions_by_group':lang_stats,
            'company_mapping':company_map,
            'sensitivity':{'method':'先算各公司本样本中要求提及率，再对公司等权平均。降低重复采样权重；仍非市场概率或公司统一门槛。',
                           'company_boundary':'腾讯云智研发单列独立雇主；腾讯与腾讯云合为腾讯品牌家族。百度/字节/阿里内部团队按品牌家族分组。',
                           'company_counts':dict(Counter(company_map.values())),
                           'alternate_boundary':'若把腾讯云智研发也并入腾讯品牌家族，总公司组由8变7；各方向内后端6、Agent5、混合1不变。',
                           'rows':sensitivity},
            'coding':rows, 'manual_semantic_notes':NOTES}


def conclusions(stats):
    g = stats['groups']
    n = lambda track,topic,level='required_any':g[track]['features'][topic][level+'_count']
    ids = lambda track,topic,level='required_any':g[track]['features'][topic][level+'_ids']
    return [
      {'title':'先准备共同底座，再按岗位方向读技术',
       'body':f"主语言/编程能力在后端 {n('后端','lang')}/10、Agent {n('Agent工程','lang')}/11、混合 {n('混合','lang')}/3 中明确要求。具体语言大多按选项或示例列出，不能把Java、Go、Python、C++都列成必会。",
       'basis_ids':['JD03','JD20','JD22','JD25','JD33']},
      {'title':'后端样本重存储与工程基础，Redis/MQ不是所有岗位统一前提',
       'body':f"后端数据库/存储要求 {n('后端','db')}/10；精确Redis {n('后端','redis')}/10、MQ {n('后端','mq')}/10。MySQL另有单列了解 {n('后端','mysql','familiarity')}/10。JD05只写分布式缓存、JD07只写存储/缓存，不能替换成Redis/MySQL。",
       'basis_ids':list(dict.fromkeys(ids('后端','db')+['JD02','JD21']))},
      {'title':'Agent的RAG与工具要求存在强弱，评测和状态更多写在职责',
       'body':f"Agent组RAG要求中提及 {n('Agent工程','rag')}/11（含择一 {n('Agent工程','rag','required_option')}）；工具调用 {n('Agent工程','tools')}/11（含择一 {n('Agent工程','tools','required_option')}）。评测明确要求 {n('Agent工程','evaluation')}/11、优先 {n('Agent工程','evaluation','preferred')}/11、职责 {n('Agent工程','evaluation','duties')}/11；状态/记忆/恢复职责 {n('Agent工程','state','duties')}/11。适合据此选读真实链路，但不能把全部职责改为入职硬门槛。",
       'basis_ids':['JD08','JD09','JD12','JD14','JD24','JD26','JD27']},
      {'title':'Agent框架应用、Infra和算法研究应分别看',
       'body':'JD26关注Runtime、容器、隔离、状态恢复与排障；JD23/JD27偏应用系统；JD15/16/28/29/32的训练算法岗位已排除。不能用研究岗的训练/论文要求覆盖全部Agent工程实习。',
       'basis_ids':['JD23','JD26','JD27','JD28','JD29']},
      {'title':'混合组不是第三条普遍赛道，而是3个百度样本',
       'body':'混合组JD11/JD22/JD33分别偏Java开放平台、Go/Python应用后端、核心产品后端；三者都来自百度。单列用于看桥接要求，不与另外两组相加比较概率，也不能跨公司外推。',
       'basis_ids':['JD11','JD22','JD33']},
      {'title':'公司模板重复会影响排序，保留原数并做等权敏感性',
       'body':'百度7条、字节6条、阿里品牌家族4条合计17/24。腾讯云智研发JD02/JD21为不同年度的近似模板。下面同时显示JD提及率和公司等权结果；结论只解释本样本。',
       'basis_ids':['JD02','JD21']},
    ]


READING = {
 '后端':[('JD20','Java基础与缓存/MQ/幂等的明确要求最具体；先看原文哪些是资格、哪些是优先。'),
         ('JD05','看Go/Java、RPC、缓存、MySQL优化怎样连接智能体业务；不要凭业务名推全部Agent门槛。'),
         ('JD02','看语言择一、CS/网络必备、数据库了解和分布式加分四者的层级。'),
         ('JD30','C/C++/Rust系统后端对照；分布式海量查询是工作内容，不是统一前置组件清单。')],
 'Agent工程':[('JD08','先看基础语言/算法与Agent经验优先的低门槛表达，再看职责范围。'),
             ('JD09','看后端基础、LLM/RAG认知与检索/对话/评测职责的连接。'),
             ('JD23','看Agent系统、上下文和工具协议的明确要求，以及训练/评测优先项。'),
             ('JD14','看规划、异常恢复与成功率职责；实习时长冲突需投递前核对。'),
             ('JD26','单列Agent Infra；看Runtime/隔离/持久状态与实验定位，不强套给应用岗。')],
 '混合':[('JD11','后端基础硬要求，Agent/MQ/网关等优先，适合逐层读。'),
         ('JD22','Go与Python并列要求；测试/容器是要求，Agent/RAG是职责。'),
         ('JD33','检查标题与正文语言不一致；正文不支持Python明确必会。')],
}


def refs(jds, by):
    return '、'.join(f'<a href="{E(by[jid]["url"])}" target="_blank" rel="noopener">{E(jid)}</a>' for jid in jds)


def layered_chart(stats, track, topic_ids, filename):
    n = stats['groups'][track]['n']
    feature = stats['groups'][track]['features']
    width, step = 1060, 78
    height = 112 + len(topic_ids)*step
    x0, plot_width = 270, 610
    colors = [('required_any_count','#0b6f6b','要求中提及（含择一）'),('preferred_count','#cf8b37','优先/加分'),('duties_count','#667e99','工作职责')]
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{E(track)}岗位分层计数">',
           '<rect width="100%" height="100%" fill="#fff"/>',
           '<style>text{font-family:Microsoft YaHei,Arial,sans-serif;fill:#203b42;font-size:16px}.small{font-size:13px;fill:#556b72}</style>',
           f'<text x="24" y="31" font-size="22" font-weight="700">{E(track)} · {n} 份可比JD</text>']
    for index,(key,color,label) in enumerate(colors):
        x=24+index*310
        svg += [f'<rect x="{x}" y="49" width="13" height="13" rx="2" fill="{color}"/>',f'<text class="small" x="{x+21}" y="61">{E(label)}</text>']
    for k in range(n+1):
        x=x0+plot_width*k/n
        svg += [f'<line x1="{x}" y1="87" x2="{x}" y2="{height-25}" stroke="#e6eeec"/>',f'<text class="small" x="{x}" y="82" text-anchor="middle">{k}</text>']
    for i,topic in enumerate(topic_ids):
        y=104+i*step
        svg.append(f'<text x="24" y="{y+23}" font-weight="600">{E(TOPICS[topic][0])}</text>')
        for j,(key,color,_) in enumerate(colors):
            count=feature[topic][key]
            bar=plot_width*count/n
            yy=y+j*18
            svg += [f'<rect x="{x0}" y="{yy}" width="{bar:.2f}" height="12" rx="3" fill="{color}"/>',
                    f'<text class="small" x="{x0+bar+8:.2f}" y="{yy+11}">{count}/{n}</text>']
        fam=feature[topic]['familiarity_count'];opt=feature[topic]['required_option_count']
        note='；'.join(item for item in [f'择一 {opt}' if opt else '',f'另有了解 {fam}' if fam else ''] if item)
        if note:svg.append(f'<text class="small" x="905" y="{y+25}">{E(note)}</text>')
    svg.append('</svg>')
    (OUT/filename).write_text(''.join(svg),encoding='utf-8')
    return filename


def sensitivity_chart(stats, filename):
    selected=[('后端',topic) for topic in ['db','cache','redis','mq']]+[('Agent工程',topic) for topic in ['rag','tools','evaluation','cloud']]
    lookup={(row['track'],row['topic_id']):row for row in stats['sensitivity']['rows']}
    width,height,x0,pw=1060,720,325,560
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="公司等权敏感性">',
         '<rect width="100%" height="100%" fill="white"/><style>text{font-family:Microsoft YaHei,Arial,sans-serif;fill:#203b42;font-size:16px}.small{font-size:13px;fill:#556b72}</style>',
         '<text x="24" y="32" font-size="22" font-weight="700">要求中提及率：重复采样敏感性</text>',
         '<text x="24" y="62" class="small">绿色：按JD等权；蓝色：先算公司内比例，再对公司等权。不是市场概率。</text>']
    for k in range(6):
        x=x0+pw*k/5
        svg += [f'<line x1="{x}" y1="100" x2="{x}" y2="{height-25}" stroke="#e7eeec"/>',f'<text class="small" x="{x}" y="91" text-anchor="middle">{k*20}%</text>']
    for i,(track,topic) in enumerate(selected):
        row=lookup[(track,topic)];y=118+i*72
        svg.append(f'<text x="24" y="{y+18}">{E(track)} · {E(TOPICS[topic][0])}</text>')
        for j,(key,color) in enumerate([('raw_jd_fraction','#0b6f6b'),('company_equal_weight_fraction','#667e99')]):
            val=row[key];w=pw*val;yy=y+j*21
            svg += [f'<rect x="{x0}" y="{yy}" width="{w:.2f}" height="14" rx="3" fill="{color}"/>',f'<text class="small" x="{x0+w+8:.2f}" y="{yy+12}">{val*100:.1f}%</text>']
    svg.append('</svg>');(OUT/filename).write_text(''.join(svg),encoding='utf-8');return filename


def feature_cell(item,n):
    req=item['required_any_count']
    pct=int(round(req*100/n)) if n else 0
    option=f' <span class="tag">含择一 {item["required_option_count"]}</span>' if item['required_option_count'] else ''
    bar=f'<div class="mini-track"><div class="mini-fill" style="width:{pct}%"></div></div>'
    sub=[]
    if item['familiarity_count']:sub.append(f'了解 <b>{item["familiarity_count"]}</b>')
    if item['preferred_count']:sub.append(f'优先 <b>{item["preferred_count"]}</b>')
    if item['duties_count']:sub.append(f'职责 <b>{item["duties_count"]}</b>')
    sub_str=' · '.join(sub) if sub else '了解/优先/职责均为 0'
    return f'<b>要求 {req}/{n}</b>{option}{bar}<small>{sub_str}</small>'


def render_html(stats, jobs, charts):
    by={jd['id']:jd for jd in jobs};g=stats['groups']
    css='''*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:68px}body{margin:0;background:#ede9e0;color:#18373b;font:16px/1.72 "Microsoft YaHei","PingFang SC",sans-serif}
.top-bar{position:sticky;top:0;z-index:20;background:#1b363acc;backdrop-filter:blur(8px);border-bottom:1px solid #2d4f54;color:#fff}
.top-bar-inner{max-width:1180px;margin:auto;padding:10px 24px;display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}
.top-brand{font-weight:700;font-size:14px;letter-spacing:.8px;color:#e4f2ef;white-space:nowrap}
.top-links{display:flex;gap:6px 10px;flex-wrap:wrap;align-items:center}
.top-links a{color:#d3e6e3;text-decoration:none;font-size:13px;padding:4px 9px;border-radius:4px;transition:background .15s}
.top-links a:hover,.top-links a.active{background:#2c5855;color:#fff}
.top-links a.pdf-pill{background:#a3482d;color:#fff;font-weight:600}
main{max-width:1180px;margin:auto;padding:28px 24px 70px}h1{font-size:36px;line-height:1.3;margin:10px 0}h2{font-size:25px;line-height:1.4;margin:0 0 14px}h3{font-size:19px;margin:16px 0 8px}p{margin:9px 0 15px}a{color:#096c68;text-underline-offset:3px}header.hero{background:#173e42;color:#fff;padding:30px 34px;border-radius:10px}header.hero a{color:#c9ece4}header.hero nav{display:flex;gap:10px 18px;flex-wrap:wrap;margin-top:20px;padding-top:14px;border-top:1px solid #2b595e}.eyebrow{font-size:12px;letter-spacing:2px;color:#b8ded9;font-weight:700}.lead{font-size:18px;color:#e6f4f1}section{background:#fffefb;border:1px solid #d4e2dc;border-radius:8px;padding:28px 32px;margin:22px 0;box-shadow:0 4px 14px #18373b08}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:18px}.metric{background:#f3f8f5;border:1px solid #d5e2dc;padding:16px;border-radius:7px}.metric b{font-size:32px;display:block;line-height:1.2;color:#096e69}.metric small{display:block;color:#536d72;margin-top:4px}.note{padding:13px 16px;background:#fbf5e6;border-left:4px solid #cc9845;border-radius:4px;font-size:14px}.finding-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px}.finding{border:1px solid #dce6e1;background:#f9fbf9;padding:16px 18px;border-radius:6px;border-top:3px solid #096e69}.finding h3{margin:0 0 8px;font-size:17px}.finding p{margin:0 0 8px;font-size:14.5px}.muted,small{color:#587077}table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:11px;border:1px solid #d7e3de;text-align:left;vertical-align:top}th{background:#edf4f0;white-space:normal}.scroll{overflow:auto;max-width:100%}.scroll table{min-width:860px}.chart-scroll{overflow:auto;max-width:100%;margin:18px 0}.chart-scroll img{width:100%;min-width:780px;height:auto;display:block}.route{padding:14px 18px;background:#f5f8f5;border:1px solid #dce6e0;border-left:4px solid #096e69;margin:10px 0;border-radius:6px}.route p{margin:6px 0}details{margin:16px 0;border:1px solid #dce6e0;border-radius:6px;padding:12px 16px;background:#f8fbf9}summary{cursor:pointer;font-weight:700;color:#096c68}input,select{font:inherit;padding:9px 12px;border:1px solid #bdcec8;border-radius:6px;max-width:100%}.filters{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin:15px 0}tr[hidden]{display:none}.tag{display:inline-block;font-size:11px;padding:1px 6px;border-radius:4px;background:#e6f1ec;color:#166b62;font-weight:600}.mini-track{height:6px;background:#e4ece8;border-radius:3px;margin:5px 0;overflow:hidden}.mini-fill{height:100%;background:#0b6f6b;border-radius:3px}@media(max-width:760px){.finding-grid{grid-template-columns:1fr}}@media(max-width:600px){main{padding:14px 12px 40px}header.hero{padding:22px 18px}h1{font-size:28px}h2{font-size:22px}section{padding:18px 16px}.metrics{grid-template-columns:repeat(2,1fr)}.metric{padding:14px}.lead{font-size:16px}.filters input{width:100%}}@media print{@page{size:A4;margin:14mm}body{background:white;font-size:10pt;line-height:1.5}main{max-width:none;padding:0}.top-bar{display:none!important}header.hero{background:white;color:#18373b;padding:0 0 10px;border-bottom:2px solid #173e42;border-radius:0}header.hero a{color:#096c68}h1{font-size:24pt}h2{font-size:17pt}section{border:0;border-top:1px solid #cbd8d1;padding:14px 0;margin:16px 0;border-radius:0;box-shadow:none}header.hero nav,.filters{display:none}.metrics{grid-template-columns:repeat(4,1fr)}.metric{padding:8px}.metric b{font-size:20pt}.scroll,.chart-scroll{overflow:visible}.scroll table{min-width:0;font-size:8pt}td,th{padding:5px}.chart-scroll img{min-width:0;width:100%;max-height:235mm;object-fit:contain}h2,h3,summary{break-after:avoid}tr,.metric,.finding,.route,.chart-scroll{break-inside:avoid}a{color:inherit}details:not([open])>*:not(summary){display:none}}'''
    topbar = (
        '<header class="top-bar"><div class="top-bar-inner">'
        '<span class="top-brand">后端 &amp; Agent 实习调研</span>'
        '<nav class="top-links" aria-label="全站导航">'
        '<a href="../argon_00_开始阅读.html">开始阅读</a>'
        '<a href="../01_调研报告/argon_实习求职调研总报告.html">调研总报告</a>'
        '<a class="active" href="argon_岗位要求统计与解读.html">岗位要求统计</a>'
        '<a href="../03_简历与候选人案例/argon_候选人与简历图册.html">候选人简历图册</a>'
        '<a href="../04_面经与专业观点/argon_面经重点与项目追问.html">面经与项目追问</a>'
        '<a href="../06_项目分析与推荐/argon_项目比较与精读指南.html">25项目精读指南</a>'
        '<a href="../01_调研报告/argon_资料检索与证据详表.html">239条证据检索</a>'
        '<a class="pdf-pill" href="../01_调研报告/argon_实习求职调研总报告.pdf">重点版 PDF ↗</a>'
        '</nav></div></header>'
    )
    body=f'<header class="hero"><div class="eyebrow">招聘 JD 五层语义编码 · 描述统计 · 2026-10-24</div><h1>后端与 Agent 工程实习，到底要求什么？</h1><p class="lead">33 条 JD 线索中，24 份工程岗位全文可比（后端 10、Agent 工程 11、混合 3）。本页严格区分【明确要求】【择一选项】【单列了解】【优先加分】与【工作职责】，助你精准定位复习重心。</p><nav><a href="#takeaways">01 六大核心结论</a><a href="#backend">02 后端10份分层图</a><a href="#agent">03 Agent11份分层图</a><a href="#mixed">04 混合3份对照</a><a href="#sensitivity">05 公司去重敏感性</a><a href="#read">06 重点JD精读路线</a><a href="#methods">07 24项完整统计表</a></nav></header>'
    body+='<section id="takeaways"><h2>一、先看六个关键结论</h2><div class="metrics">'
    for n,label,sub in [(33,'全部 JD 线索','含 9 份算法/摘要对照（已单列排除）'),(10,'后端工程全文','覆盖 6 个公司组，重存储与高可用'),(11,'Agent 工程全文','覆盖 5 个公司组，含 Agent Infra'),(3,'混合方向全文','均来自百度，服务端底座+AI应用')]:
        body+=f'<div class="metric"><b>{n}</b>{E(label)}<small>{E(sub)}</small></div>'
    body+='</div><div class="finding-grid">'
    for idx, finding in enumerate(stats['findings'], 1):
        body+=f'<article class="finding"><h3><span class="tag">结论 0{idx}</span> {E(finding["title"])}</h3><p>{E(finding["body"])}</p><small>代表性依据：{refs(finding["basis_ids"],by)}</small></article>'
    body+='</div><p class="note" style="margin-top:16px"><b>统计口径提示：</b>本表基于公开便利样本做精细分层（非全市场随机抽样）；“未在 JD 明示”不代表面试不考察，建议结合【面经与项目追问】配套使用。</p></section>'
    for track,anchor,chart in [('后端','backend',charts[0]),('Agent工程','agent',charts[1])]:
        body+=f'<section id="{anchor}"><h2>{E(track)}方向：{g[track]["n"]} 份可比 JD 分层对比</h2>'
        body+='<p>图中每个技术主题包含三条横柱：<b>深绿＝明确要求（含择一选项）</b>、<b>橙色＝优先/加分项</b>、<b>灰蓝＝工作职责</b>。阅读时切勿将入职后的工作职责直接等同于投递硬门槛。</p>'
        body+=f'<div class="chart-scroll"><img src="{E(chart)}" alt="{E(track)}岗位技术要求分层计数，见后方完整统计表"></div>'
        body+='<p class="muted">样本时间分布：'+E('；'.join(f'{k} ({v}条)' for k,v in g[track]['source_date_year_counts'].items()))+' · 来源平台：'+E('；'.join(f'{k} ({v})' for k,v in g[track]['source_types'].items()))+'。</p>'
        if track=='Agent工程':body+='<p class="note"><b>方向细分提示：</b>JD26 属于 Agent Infra（容器、安全沙箱、Runtime 与故障恢复），本页纳入工程组统计，但其容器/内核要求并非普通 Agent 应用开发岗的统一门槛；JD24 则包含多方向择一条件。</p>'
        body+='</section>'
    body+='<section id="mixed"><h2>混合组：3 份百度桥接岗位对照</h2><p>单独列出这 3 份桥接岗位，避免把“Java AI 开放平台”、“Go/Python 智能体后端”与“C++/Go 核心搜索后端”混成同一张技能表。</p><div class="scroll"><table><thead><tr><th>岗位编号与名称</th><th>明确要求（硬门槛）</th><th>优先/加分项</th><th>工作职责与阅读注意</th></tr></thead><tbody>'
    for jid in g['混合']['jd_ids']:
        jd=by[jid];body+='<tr><td><b>'+refs([jid],by)+'</b><br>'+E(jd['title'])+'</td><td>'+E('；'.join(jd['required_stack']))+'</td><td>'+E('；'.join(jd['preferred_stack']) or '未单列')+'</td><td>'+E(jd['duties'])+'<br><small><b>编码注记：</b>'+E(NOTES[jid])+'</small></td></tr>'
    body+='</tbody></table></div></section>'
    body+='<section id="sensitivity"><h2>公司重复采样敏感性：如果按公司等权平均</h2><p>'+E(stats['sensitivity']['method'])+'</p><div class="chart-scroll"><img src="'+E(charts[2])+'" alt="按JD与公司等权的要求提及率对比"></div><p class="small">'+E(stats['sensitivity']['company_boundary'])+' '+E(stats['sensitivity']['alternate_boundary'])+'</p>'
    body+='<details><summary>展开查看各公司品牌家族的 JD 样本分布</summary><ul>'
    for company,n in stats['sensitivity']['company_counts'].items():body+='<li><b>'+E(company)+f'</b>：{n} 份可比工程 JD</li>'
    body+='</ul></details></section>'
    body+='<section id="read"><h2>下一步：精读这 12 份代表性 JD 即可建立标尺</h2><p>按岗位典型差异挑选，帮你快速看清不同梯队与细分方向的招聘原文写法：</p>'
    for track,items in READING.items():
        body+='<h3>'+E(track)+'代表样本</h3>'
        for jid,reason in items:body+='<div class="route"><b>'+refs([jid],by)+' · '+E(by[jid]['title'])+'</b><p>'+E(reason)+'</p><small>发布/窗口：'+E(by[jid].get('publish_date','未展示'))+' · 来源：'+E(by[jid]['source_type'])+'</small></div>'
    body+='</section>'
    body+='<section id="methods"><h2>24 个技术主题完整五层统计表与可审查编码</h2><p>每个单元格顶部展示<b>明确要求数 / 该方向总 JD 数</b>（配进度条与择一选项标签），下方列出<b>单列了解 · 优先加分 · 工作职责</b>频次。</p><p><a href="argon_技术项逐JD编码.csv">下载逐 JD 编码明细 (CSV)</a> · <a href="../08_证据索引与统计/argon_岗位统计_可读版.json">统计源数据 (JSON)</a> · <a href="argon_岗位要求统计与解读.md">阅读 Markdown 简版</a></p><div class="scroll"><table><thead><tr><th>技术主题与编码定义</th><th>后端开发 (n=10)</th><th>Agent 工程 (n=11)</th><th>混合方向 (n=3)</th></tr></thead><tbody>'
    for topic,(label,definition) in TOPICS.items():
        body+='<tr><td><b>'+E(label)+'</b><br><small>'+E(definition)+'</small></td>'
        for track in TRACKS:body+='<td>'+feature_cell(g[track]['features'][topic],g[track]['n'])+'</td>'
        body+='</tr>'
    body+='</tbody></table></div><details><summary>展开：编程语言要求细分（单独指定 vs 择一选项 vs 并列清单）</summary><p>“单独/并列指定”表示原文明确要求掌握该语言；“明确选项”表示多语言任选其一；“清单连接词未明”表示原文顿号/斜杠并列但未写明是否择一。</p><div class="scroll"><table><thead><tr><th>方向</th><th>编程语言</th><th>单独/并列指定</th><th>明确择一选项</th><th>连接词未明</th><th>了解 / 优先 / 仅标题出现</th></tr></thead><tbody>'
    for track,langs in stats['language_mentions_by_group'].items():
        for lang,item in langs.items():
            body+='<tr><td>'+E(track)+'</td><td><b>'+E(lang)+'</b></td><td>'+str(item['fixed_count'])+'</td><td>'+str(item['options_count'])+'</td><td>'+str(item['listed_count'])+'</td><td>'+str(item['familiarity_count'])+' / '+str(item['preferred_count'])+' / '+str(item['title_only_count'])+'</td></tr>'
    body+='</tbody></table></div></details><details><summary>展开：全部 33 条 JD 线索纳入状态与逐条编码边界（支持搜索）</summary><div class="filters"><input id="jd-search" type="search" placeholder="搜索 JD 编号、岗位名、公司或关键词..." aria-label="搜索JD"><span>当前显示 <b id="jd-shown">33</b> / 33</span></div><div class="scroll"><table><thead><tr><th>JD 编号与来源</th><th>赛道与纳入状态</th><th>发布日期/窗口</th><th>编码说明与阅读边界</th></tr></thead><tbody>'
    exclusion={x['id']:x['reason'] for x in stats['excluded']}
    for jd in jobs:
        jid=jd['id'];scope=jd['taxonomy']['track']+' · '+('纳入工程对比' if jid in CODES else '单列排除')
        note=NOTES.get(jid,exclusion.get(jid,'按原文要求、优先和职责分列；未列不等于不要求。'))
        search=' '.join([jid,jd['title'],scope,note]).lower()
        body+='<tr class="jd-row" data-search="'+E(search)+'"><td><b>'+refs([jid],by)+'</b><br>'+E(jd['title'])+'<br><small>'+E(jd['source_type'])+'</small></td><td>'+E(scope)+'</td><td>'+E(jd.get('publish_date','未展示'))+'</td><td>'+E(note)+'</td></tr>'
    body+='</tbody></table></div></details><details><summary>展开：统计方法论与八条编码准则</summary><ul>'
    for rule in stats['rules']:body+='<li>'+E(rule)+'</li>'
    body+='</ul></details></section>'
    js="""const q=document.getElementById('jd-search');q.addEventListener('input',()=>{let n=0;const s=q.value.trim().toLocaleLowerCase();document.querySelectorAll('.jd-row').forEach(row=>{row.hidden=!!s&&!row.dataset.search.includes(s);if(!row.hidden)n++});document.getElementById('jd-shown').textContent=n});"""
    return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>岗位要求统计与解读</title><style>'+css+'</style></head><body>'+topbar+'<main>'+body+'</main><script>'+js+'</script></body></html>'


def format_md_cell(x, n):
    req = x['required_any_count']
    opt = x['required_option_count']
    fam = x['familiarity_count']
    pref = x['preferred_count']
    duty = x['duties_count']
    head = f"**要求 {req}/{n}**" + (f" (择一{opt})" if opt else "")
    extras = []
    if fam:
        extras.append(f"了解 {fam}")
    if pref:
        extras.append(f"优先 {pref}")
    if duty:
        extras.append(f"职责 {duty}")
    return head + (" · " + " / ".join(extras) if extras else "")


def render_md(stats,jobs):
    by={jd['id']:jd for jd in jobs}
    lines=[
        '# 招聘岗位要求统计与解读（24 份可比工程 JD）',
        '',
        '> **样本概览**：共采集 **33 条** JD 线索，其中 **24 份**为可比工程岗位全文（**后端 10 份**、**Agent 工程 11 份**、**混合 3 份**）。其余 9 份（算法研究对照 5、研究工程混合 1、摘要受限 3）已单列排除，不混入工程分母。',
        '',
        '## 一、六大核心发现',
        ''
    ]
    for idx, finding in enumerate(stats['findings'], 1):
        lines += [
            f'### {idx}. {finding["title"]}',
            f'- **结论解读**：{finding["body"]}',
            f'- **代表性依据**：' + '、'.join(f'[{jid}]({by[jid]["url"]})' for jid in finding['basis_ids']) + '。',
            ''
        ]
    lines += [
        '---',
        '',
        '## 二、24 个技术主题五层统计表',
        '',
        '> **读表指南**：每个单元格优先展示 **明确要求数/总样本数**（若含多项择一则括注 `择一N`），其后展示非零的 **单列了解 / 优先加分 / 工作职责** 频次。后三层并非入职硬门槛，同一 JD 可在不同层级同时提及同一技术。',
        '',
        '| 技术主题 | 后端开发 (n=10) | Agent 工程 (n=11) | 混合方向 (n=3) |',
        '| :--- | :--- | :--- | :--- |'
    ]
    for topic,(label,_) in TOPICS.items():
        cells=[]
        for track in TRACKS:
            n = stats['groups'][track]['n']
            x = stats['groups'][track]['features'][topic]
            cells.append(format_md_cell(x, n))
        lines.append('| **'+label+'** | '+' | '.join(cells)+' |')
    lines += ['', '---', '', '## 三、代表性 JD 精读推荐路线', '']
    for track,items in READING.items():
        lines+=['### '+track+'方向','']
        for jid,reason in items:lines.append(f'- **[{jid} · {by[jid]["title"]}]({by[jid]["url"]})**：{reason}')
        lines.append('')
    lines += [
        '---',
        '',
        '## 四、编码方法与阅读边界',
        '',
        '- **五层独立编码**：每份 JD 均由人工核对正文语义，划分为 `R`（明确要求）、`O`（明确择一选项）、`F`（原文单列了解项）、`P`（优先/加分项）、`D`（工作职责），绝不按关键词出现自动升级为硬门槛。',
        '- **编程语言口径**：区分“单独或并列指定”、“明确择一”与“连接词未明”；如 JD22 并列要求 Golang 与 Python，JD33 正文不计入仅在标题出现的 Python。',
        '- **公司去重敏感性**：百度（7份）、字节（6份）、阿里家族（4份）合计占 17/24；完整 HTML 页面同时提供“按 JD 等权”与“按公司等权平均”的双重对比图。',
        '',
        '配套文件：[argon_岗位要求统计与解读.html](argon_岗位要求统计与解读.html) · [argon_技术项逐JD编码.csv](argon_技术项逐JD编码.csv) · [argon_岗位统计_可读版.json](../08_证据索引与统计/argon_岗位统计_可读版.json)'
    ]
    return '\n'.join(lines)+'\n'


def main():
    all_records=load('all_evidence_records.json');jobs=[jd for jd in all_records if re.fullmatch(r'JD\d+',jd['id'])]
    jobs.sort(key=lambda jd:int(jd['id'][2:]))
    layer=load('技术要求_明确要求与加分项.json')
    engineering={jd['id'] for jd in jobs if jd.get('matrix_include') and jd.get('reading',{}).get('fulltext')}
    assert len(jobs)==33 and len(engineering)==24 and engineering==set(CODES)
    assert layer['engineering_jd_count']==24 and {row['id'] for row in layer['job_requirement_rows']}==engineering
    assert set(LANGUAGES)==engineering
    rows=coding(jobs);stats=build_stats(jobs,rows)
    assert stats['denominators']['by_track']=={'后端':10,'Agent工程':11,'混合':3}
    stats['findings']=conclusions(stats)
    stats['reading_priorities']={track:[{'id':jid,'title':next(jd['title'] for jd in jobs if jd['id']==jid),'reason':reason,'url':next(jd['url'] for jd in jobs if jd['id']==jid)} for jid,reason in items] for track,items in READING.items()}
    OUT.mkdir(exist_ok=True)
    charts=[layered_chart(stats,'后端',['lang','cs','db','mysql','cache','redis','mq','distributed','quality','observability'],'argon_岗位统计_后端.svg'),
            layered_chart(stats,'Agent工程',['cs','agent','llm','rag','tools','context','state','evaluation','cloud','training'],'argon_岗位统计_Agent.svg'),
            sensitivity_chart(stats,'argon_岗位统计_公司敏感性.svg')]
    stats['charts']=[{'file':'02_招聘岗位资料/'+name} for name in charts]
    # 只写统计交付，不修改主库、原始TXT、已有整合器或原始来源。
    (BASE/'argon_岗位统计_可读版.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'argon_岗位要求统计与解读.html').write_text(render_html(stats,jobs,charts),encoding='utf-8')
    (OUT/'argon_岗位要求统计与解读.md').write_text(render_md(stats,jobs),encoding='utf-8')
    columns=['jd_id','title','track','company','company_family','included','topic_id','topic','R','O','F','P','D','R_basis','O_basis','F_basis','P_basis','D_basis','source_url','source_date','semantic_note','absence_meaning']
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=columns);writer.writeheader();writer.writerows(rows)
    (OUT/'argon_技术项逐JD编码.csv').write_text(stream.getvalue(),encoding='utf-8-sig',newline='')
    print(json.dumps({'denominators':stats['denominators'],'company_groups':{track:g['company_n'] for track,g in stats['groups'].items()},'coding_rows':len(rows),'charts':charts,'findings':stats['findings']},ensure_ascii=False))


if __name__=='__main__':
    main()
