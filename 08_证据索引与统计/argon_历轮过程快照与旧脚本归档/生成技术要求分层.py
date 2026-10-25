"""把公开JD要求、优先项、职责与面经观察分层，不推导统一SSP门槛。"""
from pathlib import Path
import importlib.util
import json

BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('data_io',BASE/'整合需求纠偏.py')
io=importlib.util.module_from_spec(spec);spec.loader.exec_module(io)

def generate():
    records=io.load('all_evidence_records.json');by={r['id']:r for r in records}
    jobs=[r for r in records if r['category']=='招聘JD' and r.get('matrix_include')]
    interviews=io.load('interview_records.json')
    abilities=io.load('能力要求四类证据对照.json')['rows']
    fresh={r['id']:r for r in io.load('目标执行_JD原文复核.json')['records']}
    rows=[]
    for r in jobs:
        rows.append({'id':r['id'],'company':r['company'],'role':r['title'],'track':r['taxonomy']['track'],
          'explicit_requirements':r.get('required_stack',[]),'explicit_preferences':r.get('preferred_stack',[]),
          'duties_not_entry_gates':r.get('duties','未列'),'education':r.get('degree_constraint','未列'),
          'availability':r.get('availability_constraint','未列'),'source_URL':r['url'],
          'source_type':r['source_type'],'source_date':r['taxonomy']['source_date_text'],
          'current_access_recheck':fresh.get(r['id']),
          'interpretation_boundary':'要求词按原岗位深度阅读：了解/熟悉/掌握/择一不可互换；未列不等于不考。职责不自动等于入职前必须独立实现。',
          'limitations':r.get('limitations','')})
    backend=[
     {'item':'一门主要后端语言与计算机基础','explicit_requirement_jd_ids':['JD01','JD02','JD03','JD04','JD05','JD06','JD07'],
      'finding':'岗位允许的语言及深度不同；语言择一不表示Java、Go、C++必须全会。网络、操作系统和算法按目标JD及面经定位。',
      'interview_ids':['INT10','INT12','INT20','INT22'],'project_ids':['PRO17','PRO18','PRO19']},
     {'item':'数据库、缓存与消息','explicit_requirement_jd_ids':['JD01','JD05','JD06'],
      'finding':'MySQL、Redis与MQ在这些岗位被明确点名；JD02中数据库/脚本/KV的了解项不能加深成全部精通，JD03也没有列Spring或Redis。',
      'interview_ids':['INT22','INT24','INT27'],'project_ids':['PRO01','PRO02','PRO08']},
     {'item':'Java及服务开发专项','explicit_requirement_jd_ids':['JD11'],
      'finding':'该平台实习岗明确要求JVM、并发、集合、Spring/Boot、REST、MySQL与Redis；消息队列在此岗写为优先，不能和JD01/06的要求混成统一门槛。',
      'interview_ids':['INT20','INT22'],'project_ids':['PRO08','PRO19']},
     {'item':'架构、容灾、开源等加分项','preference_jd_ids':['JD02','JD05','JD11'],
      'finding':'分布式与高可用、AI实践、开源贡献分别是部分岗位的优先项；现有材料不证明必须参与大型框架才能拿实习或SSP。',
      'candidate_ids':['CV01','CV02','CV05'],'project_ids':['PRO09']}
    ]
    agent=[
     {'item':'工程基础及基本Agent认知','explicit_requirement_jd_ids':['JD08','JD09','JD10','JD12','JD13','JD14'],
      'finding':'要求跨度从一门语言和算法，到后端服务、LLM应用架构、RAG与Prompt；不能以一个岗位的最低措辞代表全部团队。',
      'interview_ids':['INT01','INT42','INT47'],'project_ids':['PRO04','PRO11','PRO12']},
     {'item':'工具、上下文、恢复与评测','duties_jd_ids':['JD08','JD09','JD12','JD14'],
      'finding':'这些是多条岗位描述的工作范围，面经也会追问具体实现；JD08却把已有Agent实践写为优先，不能把每项职责都变成前置硬要求。',
      'interview_ids':['INT01','INT02','INT42','INT47'],'project_ids':['PRO06','PRO11','PRO12'],
      'opinion_ids':['OP04','OP08','OP09']},
     {'item':'Java后端与Agent平台交叉','explicit_requirement_jd_ids':['JD11'],'preference_jd_ids':['JD11'],
      'finding':'该岗后端基础是明确要求；Agent/RAG/MCP、模型调用和网关治理是加分。可据此分开审查服务实现与Agent实践，不把工具名堆叠当工程能力。',
      'interview_ids':['INT12','INT47'],'project_ids':['PRO04','PRO10']},
     {'item':'训练、论文与研究能力的适用边界','control_jd_ids':['JD15','JD16','JD17'],'preference_jd_ids':['JD10','JD12'],
      'finding':'策略算法/研究混合岗位有训练和深度学习要求；应用岗里训练、RL或代码分析可能只是优先项。研究履历只能支撑相应方向的比较。',
      'candidate_ids':['CV13','CV16'],'project_ids':[]}
    ]
    advantage_notes={
     'CV01':'Go业务经历把投递、重试去重、索引和性能串起来；代码与性能条件未公开，不能复制自报数字。',
     'CV02':'本人项目、职责与同仓面经可对应；教学来源要说明，历史腾讯SSP不证明当前复刻相同项目的收益。',
     'CV05':'2022年两项合并测试PR有可核增量；2023录用与2026 Agent方向更新分开，其他贡献未审。',
     'CV10':'2018求职文章直接链接三项本人系统项目；能研究领域问题深度，不能变成当前实习必做清单。',
     'CV17':'有多段实习和SSP结果自述，项目优化追问可参考；未定位本人仓库，2024秋招日期边界仍待核。',
     'CV09':'近期后台实习offer与具体面经可对应；个人项目只有描述，不能自动补成纯Agent SSP案例。'
    }
    if 'CV23' in by:advantage_notes['CV23']='完整公开专业履历可对应实习主体、角色和时间，但项目实现与效果细节缺失；有完整履历不代表已能审查技术深度。'
    if 'CV24' in by:advantage_notes['CV24']='Agent实习职责、问数链路和作者自列未完成项具体；源码、指标复现及与企业项目的精确对应仍未核，不称SSP。'
    if 'CV25' in by:advantage_notes['CV25']='2026蚂蚁智能体应用实习offer有明确时间线；RAG技术问题来自本人TikTok面经，不把两家公司的结果与问题串成同一场。'
    if 'CV28' in by:
        advantage_notes['CV28']='完整履历直接链接本人OJ和缓存扩展，指定消息投递、条件写回、single-flight与测试可审；雇主博彦、客户阿里云分开，面经仅主题对应，不证明现版代码导致录用。'
        backend[1]['project_ids']+=['PRO20','PRO21']
        backend[1]['finding']+=' 新增本人项目可具体读Outbox/结果竞争与缓存并发；数据库事务、外部消息投递、本地合并的边界分别核。'
    if 'OP13' in by:
        agent[1]['opinion_ids']+=['OP13']
        agent[1]['finding']+=' OP13为带官方纠错的教学概念材料，不作真实面经或生产团队验证。'
    if by['CV03']['taxonomy']['year_confirmed']:
        advantage_notes['CV03']='原文直接明确2025美团暑期后同公司SSP；外部校招另列，京东SSP/网易SP为作者推定，华为15a不换算。具体项目源码和岗位职称仍缺。'
    if 'CV30' in by:
        advantage_notes['CV30']='完整公开CV明确2026字节Creator Assistant后端实习，写到MCP工具、真实对话评测和trace；仍为本人职责自述，企业内部源码、本人面经与SSP未披露。'
        advantage_notes['CV29']='腾讯2025/Stripe2026实习主页直接链接两项源码；TinyKV继承课程框架，QuantHarbor入口和执行隔离有静态风险，不能用大厂经历替项目成熟度背书。'
        agent[1]['candidate_ids']=['CV30','CV07']
        agent[1]['interview_ids']+=['INT82','INT83']
        agent[1]['finding']+=' CV30补充本人实习职责证据；INT82/83给具体追问，但事件年、批次和结果未披露，不能将问题与CV30拼成同一场。'
        agent[1]['project_ids']+=['PRO23']
        agent[1]['finding']+=' PRO23作为状态/执行权限的风险对照，非成熟成品推荐。'
    if 'CV31' in by:
        advantage_notes['CV31']='近期中科曙光Agent实习完整CV直接链接NoWorries；本人主页另链Sprout及合并PR。可研究编排、记忆与权限，但文本打分、预算和沙箱降级存在静态风险；非互联网大厂SSP，未运行。'
        agent[1]['candidate_ids']=list(dict.fromkeys(agent[1]['candidate_ids']+['CV31']))
        agent[1]['project_ids']=list(dict.fromkeys(agent[1]['project_ids']+['PRO24','PRO25']))
        agent[1]['opinion_ids']=list(dict.fromkeys(agent[1]['opinion_ids']+['OP15']))
        agent[1]['finding']+=' CV31补上同人完整CV与公开实现的直接关系；PRO24/25用于审查机制和失败路径，OP15为原始生产访谈选读，均不证明SSP门槛。'
    if 'INT84' in by:
        agent[1]['interview_ids']=list(dict.fromkeys(agent[1]['interview_ids']+['INT84']))
        agent[1]['finding']+=' INT84为百度日常实习本人15问，具体涉及工具执行兜底、中断恢复和日志定位；原文事件年未直接写，结果未知，不与其他候选人实现拼接。'
    if 'OP16' in by:
        agent[1]['opinion_ids']=list(dict.fromkeys(agent[1]['opinion_ids']+['OP16']))
        agent[1]['finding']+=' OP16为主办方公开的一线演讲选读；与DOC02和OP15对照模型评分器校准，按单题回退、工具失败和恢复轨迹审查实现，不把团队经验升为实习门槛。'
    if 'INT85' in by:
        backend[0]['interview_ids']=list(dict.fromkeys(backend[0]['interview_ids']+['INT85','INT86']))
        backend[3]['finding']+=' INT85直接给出2025面试与失败日期，关注消息组件环境隔离、测试幂等与高可用；INT86的已offer二面追问个人角色、方案调研、容量与排障，事件年未直接写，均不支持统一SSP门槛。'
        backend[3]['interview_ids']=['INT85','INT86']
    # 外部资料按已核岗位分层，不以新增数量或框架名推导求职收益。
    imported=[r for r in records if r.get('external_import')]
    imported_jobs=[r for r in imported if r['category']=='招聘JD']
    new_backend=[r['id'] for r in imported_jobs if r.get('matrix_include') and r['taxonomy']['track'] in ['后端','混合']]
    new_agent=[r['id'] for r in imported_jobs if r.get('matrix_include') and r['taxonomy']['track'] in ['Agent工程','混合']]
    if new_backend:
        backend.append({'item':'新增招聘样本：资格、要求与岗位时效','explicit_requirement_jd_ids':new_backend,
          'finding':'新增平台招聘和官方岗位补充Java并发、消息可靠性、系统后端及跨语言要求。语言择一、了解与掌握分别按原文；许多暑期窗口已结束，页面可读不证明当前HC。平台发帖身份边界单列。'})
    if new_agent:
        agent.append({'item':'新增Agent工程样本：应用、框架与Runtime分开','explicit_requirement_jd_ids':new_agent,
          'finding':'应用工程强调任务、检索、工具与评测；框架或Runtime可能要求C++、Go或Rust，以及隔离、生命周期和状态恢复。不同学历、届次和时长分别筛选，不把研究岗训练要求套给所有应用岗。'})
    advantages=[{'candidate_id':i,'source_URL':by[i]['url'],'event_time':by[i]['taxonomy']['experience_date_text'],
       'recruitment':by[i]['taxonomy']['recruitment'],'observation':note,
       'evidence_level':'公开个人经历/录用自述；具体PR仅核贡献，不核录用原因',
       'causal_claim':'不证明该项目或该技术单独造成offer/SSP'} for i,note in advantage_notes.items()]
    question_rows=[]
    for a in abilities:
        sources=[]
        for i in a['interview_ids']:
            r=by[i]
            sources.append({'id':i,'url':r['url'],'material_type':r['material_type'],
              'event_time':r['taxonomy']['experience_date_text'],'strict_recent_internship':r.get('strict_recent_internship',False),
              'question_examples':r.get('project_questions',[])[:3],
              'scope_boundary':'原文问题的本包归纳；不是面试录音或逐字稿；资料含事后答案时不得升为真实追问'})
        question_rows.append({'ability_id':a['id'],'ability':a['ability'],'question':a['question'],
          'sources':sources,'competency':a['competency'],'project_ids':a['project_ids'],
          'common_pitfall':a['common_pitfall'],'all_four_source_types_present':all(a[k] for k in ['jd_ids','interview_ids','candidate_ids','opinion_ids']),
          'remaining_gap':a['gap']})
    result={'date':io.load('需求覆盖统计.json').get('updated_date','2026-10-23'),'scope':'技术要求证据分层，非个人项目设计',
      'rules':['明确要求、原文优先/加分、工作职责分别呈现。','JD只支持相应岗位和来源时点，不支持统一大厂或SSP评分线。',
       '面经是作者回忆，成功者经历是个案，专业观点是工程判断，不能互相替代。',
       '未提及不表示不要求；公开样本为便利样本，不估计总体市场概率。'],
      'engineering_jd_count':len(rows),'job_requirement_rows':rows,'backend_conclusions':backend,'agent_conclusions':agent,
      'interview_to_ability':question_rows,'success_case_advantages':advantages,
      'ssp_conclusion':{'status':'未建立统一SSP专属门槛','what_is_supported':'可核的个人实现、问题取舍、测试与业务验证能够形成面试深挖材料；具体收益只在个案中观察。',
        'missing':'尚无相同招聘批次、岗位和背景下普通offer与SSP的可比较样本，不能把特定技术、论文、star或项目名称当SSP必要/充分条件。'}}
    io.dump('技术要求_明确要求与加分项.json',result)
    lines=['# 技术要求：明确要求、优先项与个案优势','','本页为证据归纳，个人项目设计继续暂缓。','']
    for group,title in [(backend,'后端实习'),(agent,'Agent工程实习')]:
        lines+=['## '+title,'']
        for r in group:
            ids=list(dict.fromkeys(i for k,v in r.items() if k.endswith('_ids') for i in v))
            lines+=['### '+r['item'],'',r['finding'],'','证据：'+' · '.join(f'[{i}]({by[i]["url"]})' for i in ids),'']
    lines+=[f'## {len(rows)}份工程JD逐条分层','','| 岗位 | 明确要求（深度按原文） | 原文优先/加分 | 工作职责，非统一前置条件 |','|---|---|---|---|']
    for r in rows:lines.append(f'| [{r["id"]} {r["role"]}]({r["source_URL"]}) | '+ '；'.join(r['explicit_requirements'])+' | '+('；'.join(r['explicit_preferences']) or '未单列')+' | '+r['duties_not_entry_gates']+' |')
    lines+=['','## SSP个案的适用边界','',result['ssp_conclusion']['missing'],'']
    for r in advantages:lines+=['- ['+r['candidate_id']+']('+r['source_URL']+')：'+r['observation'],'']
    io.write(io.ROOT/'06_项目分析与推荐/技术要求_明确要求与加分项.md','\n'.join(lines))
    print(json.dumps({'jd_requirement_rows':len(rows),'ability_rows':len(question_rows),'success_advantage_cases':len(advantages)},ensure_ascii=False))

if __name__=='__main__':generate()
