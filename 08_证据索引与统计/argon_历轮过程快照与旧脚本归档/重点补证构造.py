"""构造本轮原始来源的增量；由整合持续补证.py统一导出。"""
from pathlib import Path
from copy import deepcopy
import json

BASE=Path(__file__).resolve().parent
def load(name):return json.loads((BASE/name).read_text(encoding='utf-8-sig'))
def taxonomy(track,recruitment,event,source,known=False,basis='未写事件年'):
    return {'track':track,'recruitment':recruitment,'experience_date_text':event,'date_precision':'范围' if known else '未知',
      'year_confirmed':known,'recent_status':'近期确认' if known else '年份未知','source_date_text':source,'date_basis':basis}
def reading(note,full=True):return {'scope':'全文' if full else '部分','fulltext':full,'scope_note':note,'video_watched':False}
def node(url,basis,gap='',relation='直接点名'):return {'url':url,'direct_basis':basis,'gap':gap,'relation':relation}
def chain_gaps(c):
    for key,nodes in c['chain'].items():c['chain'][key]=list({json.dumps(n,ensure_ascii=False,sort_keys=True):n for n in nodes}.values())
    c['chain_gaps']=list(dict.fromkeys(n['gap'] for v in c['chain'].values() for n in v if n.get('gap')))

def apply(rows,comparison):
    by={r['id']:r for r in rows};added=[];manual=[];changed=[]
    if not (BASE/'重点补证_大厂实习履历.json').exists():return rows,comparison,{}
    if not (BASE/'重点补证前主数据快照.json').exists():
        (BASE/'重点补证前主数据快照.json').write_text(json.dumps({'records':rows,'comparison':comparison},ensure_ascii=False,indent=2),encoding='utf-8')
    found=load('重点补证_大厂实习履历.json')
    for ident,p in [('CV29',found['new_core_partial_profiles'][0]),('CV30',found['new_core_complete_profiles'][0])]:
        complete=ident=='CV30';source=p['attachment']['url'] if complete else p['home'];source_time='2026-10-23公开版本读取，非事件时间'
        event='；'.join(o['company']+' '+o['time'] for o in p['outcomes']);projects=p['projects']
        c={'id':ident,'source_key':p['key'],'category':'候选人资料','title':p['author']+'：'+('字节后端与Agent实习完整专业履历' if complete else '腾讯/Stripe实习履历与本人直链项目'),
          'url':p['home'],'role':p['track'],'profile_type':p['profile_type'],'document_type':p['profile_type'],
          'date':event,'source_date':source_time,'taxonomy':taxonomy('混合' if complete else '后端','实习',event,source_time,True,'本人职业经历明确年月；教育背景和所在地不用于推招聘批次或中国薪资档位'),
          'reading':reading('公开完整PDF全部专业模块已读、脱敏副本保留教育/全部经历/项目/技能' if complete else '本人主页专业经历及项目段全文；缺完整教育和CV，仍为履历片段'),
          'outcome':'两段大厂实习经历自述；SSP/SP档位未披露','outcomes':[{'company':o['company'],'role':o['role'],'grade':'未披露',
            'status':'internship_experience_self_report','date':o['time'],'basis':o['basis']+'；'+o['content'],'evidence_url':source,
            'boundary':p.get('event_region','本人自述；当前开源版本不自动代表求职作品'),'independent_employer_verified':False} for o in p['outcomes']],
          'stack':['Go','ReAct','MCP','Agent评测','trace','Kitex','GORM','MySQL'] if complete else ['Java','Spring Boot','Spring Security','Redis','MySQL','Kubernetes','gRPC'],
          'projects':projects,'source_summary':p.get('reading_reason',p['direct_project_relation'] if not complete else ''),
          'complete_redacted_cv_file_received':complete,'complete_cv_file_received':False,'cv_file_licensed_for_redistribution':False,
          'ssp_claim_present':False,'ssp_grade_company_explicit':False,'has_confirmed_personal_interview_source':False,
          'has_direct_named_project_or_contribution':True,'personal_source_code_verified':not complete,
          'chain':{'outcome':[node(source,o['company']+' '+o['role']+' '+o['time'],'任职/职责限本人自述；无SSP') for o in p['outcomes']],
            'profile':[node(source,p['profile_type'],'不是投递版本；'+('脱敏转录不等于未修改原件' if complete else '缺完整教育模块'))],
            'project':[node(x.get('url',x.get('document',x.get('demo',source))),x['name']+'；'+x.get('ownership',x.get('relation',x.get('boundary','本人主页直接点名'))),
              x.get('boundary','课程/复用与当前版本边界逐项说明，未运行')) for x in projects],
            'interview':[node(None,'未定位本人公开求职面经','保持缺口','未建立')]},
          'weaknesses':p['limits'],'recommendation':'精读实习职责及工程机制；公开源码、课程框架、内部项目分别核对，不推导录用因果。',
          'source_record':{**p,'source_url':source}}
        if complete:c['redacted_cv_local_file']=p['attachment']['local_path']
        chain_gaps(c);added.append(c)
    for review in load('重点补证_面经时间与追问.json')['records']:
        r=by[review['record_id']];r['latest_time_and_question_review']=review;changed.append(r['id'])
        for key,v in review.get('proposed_main_fields',{}).items():
            if key.startswith('taxonomy.'):r['taxonomy'][key.split('.',1)[1]]=v
            else:r[key]=v
        if r['id']=='INT11':
            r['taxonomy']['experience_date_text']='面试日期及事件年未知；2025-12-07为原帖发表日期'
            r['date']=r['taxonomy']['experience_date_text']
        if r['id']=='INT09':
            r['rounds']=['6.11一面','6.16二面','6.18三面','6.20 HR面','6.24 OC']
            r['taxonomy']['experience_date_text']='6.11/6.16/6.18技术面、6.20 HR、6.24 OC；实际年未知';r['date']=r['taxonomy']['experience_date_text']
    agent=load('重点补证_Agent录用档位.json');c=by['CV07'];update=agent['existing_candidate_updates'][0]
    annual=update['sources'][0];c['latest_source_review']=update;c.setdefault('old_primary_url',c['url']);c['url']=annual['url']
    c['title']='等闲king：2025后端实习offer与本人Agent项目深挖';c['taxonomy'].update({'track':'混合','experience_date_text':'2025小红书/快手后端实习offer；其他Agent职责、答辩及面试事件年未核',
      'date_precision':'仅年份','year_confirmed':True,'recent_status':'近期确认','date_basis':annual['event_year_basis']+'；仅适用于两项后端实习offer，不推广到全部经历。','source_date_text':annual['source_date']})
    c['date']=c['taxonomy']['experience_date_text'];c['source_date']=annual['source_date']
    c['reading']=reading('新主来源年终总结与新增本人面经的公开文字全文已读；旧主来源可能删除，旧文阅读范围保留在历史记录')
    c['outcomes']=[{'company':o['company'],'role':o['role'],'grade':o['grade'],'status':'offer_self_report','date':o['event_date'],
      'evidence_url':annual['url'],'basis':o['basis'],'boundary':'两项后端实习offer；不改称Agent SSP，不证明所有旧文职责同年','independent_employer_verified':False} for o in annual['confirmed_self_reports']]
    c['outcome']='本人年终总结明确2025小红书、快手后端实习offer；无SSP，Agent具体经历时间另核'
    c['chain']['outcome']=[node(annual['url'],o['company']+' '+o['date']+'；'+o['basis'],'本人录用自述；无SSP') for o in c['outcomes']]
    c['chain']['profile'].append(node(annual['url'],'本人2025年终专业经历自述','非完整CV'))
    plugin=update['sources'][1]
    c['chain']['project'].append(node(plugin['url'],'本人直接称编写Higress语义检索MCP插件','个人GitHub账号/PR归属未闭合；不将Higress整库归个人'))
    c['chain']['interview']=[];c['has_confirmed_personal_interview_source']=True;c['has_direct_named_project_or_contribution']=True;c['interview_evidence_ids']=['INT82','INT83']
    for ident,d in zip(['INT82','INT83'],update['candidate_interview_sources']):
        c['chain']['interview'].append(node(d['url'],d['title']+'；公开主页直接链接且原文署名相同','事件年、招聘批次和最终结果未知'))
        added.append({'id':ident,'source_key':d['source_key'],'category':'面经复盘','title':d['title'],'url':d['url'],'company':d['company'],'role':d['role'],
          'date':d['event_date'],'source_date':d['source_date'],'taxonomy':taxonomy('混合','未知',d['event_date'],d['source_date'],False,'本人回忆未给事件年和招聘类型；已知其别处实习不自动确定本篇批次'),
          'reading':reading(d['access']['scope']),'fulltext_verified':True,'material_type':'本人具体问题记录' if ident=='INT82' else '面试问题与部分事后解答混合',
          'candidate_link_ids':['CV07'],'strict_recent_internship':False,'publication_recent_event_year_unknown':False,'sample_group':'招聘批次未确认',
          'result_status':'unknown','outcome':d['outcome'],'outcomes':[],'rounds':d['rounds'],'project_questions':d['questions_paraphrased'],
          'topics':['MCP网关','多租户','记忆','KV Cache','Agentic RAG','JVM'] if ident=='INT82' else ['SQL','ES','锁','线程池','检索融合','Agent响应延迟'],
          'summary':d['question_answer_boundary'],'source_record':d})
    for stage,nodes in c['chain'].items():
        c['chain'][stage]=list({json.dumps(n,ensure_ascii=False,sort_keys=True):n for n in nodes}.values())
    chain_gaps(c);changed.append('CV07')
    if (BASE/'重点补证_Higress组件贡献.json').exists():c['component_contribution_review']=load('重点补证_Higress组件贡献.json')
    for p in update['manual_access_needed']:manual.append({'title':p['title'],'url':p['url'],'status':p['state'],'to_verify':p['result_boundary']})
    for p in agent['new_partial_or_excluded_sources']:
        manual.append({'title':p['title']+'（已读，录用/岗位关系待核）','url':p['url'],'status':'公开文字按原记录范围已读；'+p['decision'],'to_verify':p.get('gaps',p.get('date_boundary','岗位、批次与最终档位'))})
    p=load('重点补证_平台正文与适用范围.json')['sources'][0]
    added.append({'id':'OP14','source_key':p['key'],'category':'B站与知乎','title':p['title'],'url':p['url'],'platform':p['platform'],'author':p['author'],
      'taxonomy':{**taxonomy('混合','不适用','工程学习观点，非招聘事件',p['source_date']),'recent_status':'不适用'},'reading':p['reading'],
      'platform_native_fulltext_verified':True,'verified_video_viewing':False,'opinion':'；'.join(x['paraphrase'] for x in p['points']),
      'identity_evidence':p['identity_evidence'],'commercial_bias':p['commercial_background'],'limits':p['limits']+[p['application_boundary']],
      'recommendation':p['recommendation'],'source_record':p})
    p=load('重点补证_SSP路线范围核查.json')
    added.append({'id':'DOC12','source_key':'SSP_SENIOR_JD_SCOPE_MISMATCH','category':'观点范围对照','title':'专家JD与校招SSP：路线观点的适用范围核查','url':p['read_url'],
      'taxonomy':{**taxonomy('Agent工程','不适用','观点而非招聘事件','日期未独立核定'),'recent_status':'不适用'},
      'reading':reading(p['scope'],False),'summary':p['analysis'],'limits':[p['boundary']],'source_record':p})
    # 两个主页直接链接的项目；一个进阶课题，一个风险对照，均不冒充全部原创或已运行。
    profile=found['new_core_partial_profiles'][0]
    for ident,p in zip(['PRO22','PRO23'],profile['projects'][:2]):
        kv=ident=='PRO22';repo=p['repo'];sha=p['sha'];url=p['url']
        def cell(status,finding,path='README.md',scope='定点静态阅读；未运行'):
            return {'status':status,'finding':finding,'source_URL':f'https://github.com/{repo}/blob/{sha}/{path}','read_paths':[path],'read_scope':scope}
        bd={
          '业务闭环':cell('源码可见' if kv else '静态风险','KV读写和事务处理可定位；不等于电商业务闭环。' if kv else '报告任务有代码与文档，但入口导入路径不一致，完整链路未运行。','kv/server/server.go' if kv else 'src_rag/core/report_pipeline.py'),
          '一致性':cell('源码可见' if kv else '未核','Prewrite/Commit的锁与write record可定位；全部分区场景一致性未证明。' if kv else '未核数据库事务、检查点与外部动作的端到端一致性。','kv/server/server.go' if kv else 'src/agents/base_agent.py'),
          '并发':cell('源码可见','Raft多数派提交与事务latches可读；未运行并发测试。' if kv else '线程池执行模型代码可读；异步不表示进程隔离或并发正确。','raft/raft.go' if kv else 'src/utils/code_executor_async.py'),
          '缓存MQ':cell('不适用','本次未核业务缓存/MQ能力；不把Raft日志或Agent上下文当消息队列。'),
          '测试':cell('未核','课程测试框架继承范围需分清；本次未审全套断言、未运行。' if kv else '固定树未见单元/集成测试，provider smoke脚本不等于任务验收。'),
          '可运行材料':cell('未核' if kv else '静态风险','课程依赖与构建材料需按原仓核；本次未运行。' if kv else 'RAG导入src.agents但组件在src_rag/agents；Web入口引用树中缺失的src.memory。','README.md' if kv else 'demo/backend/app.py'),
          '个人贡献':cell('文档宣称',p['ownership'])}
        if kv:ad={k:cell('不适用','分布式存储课题，不计Agent实现。') for k in comparison['dimensions']['agent']}
        else:ad={
          '真实任务':cell('文档宣称','金融研究报告任务为作者描述，文档规模不等于任务成功率。'),
          '状态工具':cell('源码可见','保存会话、轮次、工具依赖与executor状态，有迭代上限。','src/agents/base_agent.py'),
          '恢复':cell('源码可见','checkpoint与模型fallback可定位；没有证明外部副作用幂等。','src/agents/base_agent.py'),
          '权限':cell('静态风险','同进程Python exec有完整builtins及os/sys；所读路径不构成安全沙箱。','src/utils/code_executor_async.py'),
          '评测基线':cell('未核','未见可复核任务集、独立成功率或与基线的完整对照。'),
          '成本延迟':cell('未核','未复现token、延迟或费用；fallback存在不证明成本受控。','src_rag/core/llm_client.py'),
          '超API封装证据':cell('源码可见','状态迭代与代码执行超出单次API调用；入口和权限风险阻止将其称成熟成品。','src/agents/base_agent.py'),
          '个人贡献':cell('文档宣称',p['ownership'],'docs/migration_notes.md')}
        attachment=p.get('attachment',{})
        if not attachment:
            attachment=next((x for x in found.get('archives',[]) if x.get('repo',x.get('source_repo'))==repo),{})
        local=attachment.get('local_path');archive_file=local.split('/',1)[1] if local and local.startswith('05_项目源码归档/') else None
        comparison_row={'id':ident,'title':p['name']+'：'+('课程框架上的Raft/MVCC实现' if kv else '多Agent状态与执行隔离风险对照'),
          'repo':repo,'source_URL':url,'commit':sha,'source_nature':['本人主页直接链接','课程/框架复用边界见原文'],
          'candidate_relationships':[{'candidate_id':'CV29','relationship_type':'直接点名','direct_evidence_URLs':[profile['home']],
            'finding':'本人主页逐项直接链接；'+p['ownership'],'event_time_boundary':'腾讯实习2025，当前源码另列','snapshot_boundary':'固定SHA不等于投递版本','offer_causality':'不证明项目促成实习或SSP'}],
          'backend_dimensions':bd,'agent_dimensions':ad,
          'backend_priority':{'level':'选读','reason':'分布式存储进阶，先分清课程框架和个人实现。' if kv else '只选异步与状态机制，完整入口和隔离风险先核。','read_modules':['raft/raft.go','kv/server/server.go'] if kv else ['src/agents/base_agent.py','src/utils/code_executor_async.py']},
          'agent_priority':{'level':'非本方向' if kv else '待核','reason':'不是Agent项目。' if kv else '适合研究状态/工具与权限边界的反例；不作为成熟成品推荐。','read_modules':[] if kv else ['src/agents/base_agent.py','src/utils/code_executor_async.py','src_rag/core/report_pipeline.py']},
          'evidence_completeness':'腾讯实习者主页→本人项目直链成立；课程复用、当前版本和个人比例另核，面经/SSP缺。',
          'target_applicability':p['reading'],'attachment':{'status':'固定版本源码文本归档（去联系字段，非原ZIP）' if archive_file else '固定源码链接材料','archive_file':archive_file,
            'exists':bool(archive_file),'reason':'归档处理清单见重点补证原始记录；未运行' if archive_file else '未取得源码包，只列固定来源','source_manifest':'08_证据索引与统计/重点补证_大厂实习履历.json','runtime_verified':False},
          'read_paths':list(dict.fromkeys(f['file'].split(' + ')[0] for f in p['findings'] if f.get('file'))),
          'strengths':[f['claim'] for f in p['findings'] if f['status']=='已见实现'],'limitations':[f['claim'] for f in p['findings'] if f['status']!='已见实现']+[p['ownership']],
          'commercial_background':'课程来源明确；未核课程合作或商业收益，不据此证明录用回报。','run_status':'未构建、未运行、未调用模型或执行模型代码。',
          'source_nature_boundary':p['ownership'],'priority_interpretation':'按具体模块与风险选读；不把复杂目录或功能宣传当成熟度。'}
        added.append({'id':ident,'source_key':p['repo'],'category':'项目参考','title':comparison_row['title'],'url':url,'author':'shufengc及课程/第三方依赖作者',
          'taxonomy':{**taxonomy('后端' if kv else 'Agent工程','不适用','项目版本，非招聘事件','固定SHA，日期未独立核定'),'recent_status':'不适用'},
          'reading':reading('指定核心源码与README静态选读，范围见逐文件清单',False),'commit':sha,'outcomes':[],
          'source_findings':p['findings'],'source_record':p,'strengths':comparison_row['strengths'],'limitations':comparison_row['limitations'],
          'comparison':comparison_row,'archive_file':archive_file,'license_notes':p['license'],'recommended_use':p['reading']})
        comparison['projects']=[x for x in comparison['projects'] if x['id']!=ident]+[comparison_row]
    for r in added:
        if r['id'] in by:assert by[r['id']].get('source_key')==r['source_key'],r['id']
        by[r['id']]=r
    return sorted(by.values(),key=lambda r:r['id']),comparison,{'added_ids':[r['id'] for r in added],'changed_ids':changed,
      'manual':manual,'resolved_manual_url':load('重点补证_SSP路线范围核查.json')['resolved_url'],
      'summary':'本轮补一份字节2025后端/2026 Agent应用完整专业CV、一份腾讯/Stripe实习主页直链项目；补等闲king2025两家后端实习offer与本人AML/百度面经；确认INT11发表日期类型。新读B站工程学习观点，并排除专家JD直接充当校招SSP门槛的推论。'}
