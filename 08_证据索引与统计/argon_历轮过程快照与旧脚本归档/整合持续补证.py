"""把本轮实际核读合入主数据；保留招聘、实现和版本边界。"""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import importlib.util
import json
import re

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
spec=importlib.util.spec_from_file_location('continuous_io',BASE/'整合需求纠偏.py')
io=importlib.util.module_from_spec(spec);spec.loader.exec_module(io)
load,dump,write,flatten=io.load,io.dump,io.write,io.flatten

def tax(track,recruitment,event,known=False,source='未核',basis='原文未明事件年'):
    return {'track':track,'recruitment':recruitment,'experience_date_text':event,
      'date_precision':'范围' if known else '未知','year_confirmed':known,
      'recent_status':'近期确认' if known else '年份未知','source_date_text':source,'date_basis':basis}

def read(note,full=True):
    return {'scope':'全文' if full else '部分','fulltext':full,'scope_note':note,'video_watched':False}

def node(url,basis,gap='',relation='直接点名'):
    return {'url':url,'direct_basis':basis,'relation':relation,'gap':gap}

def refresh_chain(r):
    r['chain_gaps']=list(dict.fromkeys(n['gap'] for nodes in r['chain'].values() for n in nodes if n.get('gap')))

def group(rows):
    return {'total':len(rows),**{k:dict(Counter(r['taxonomy'][k] for r in rows)) for k in ['track','recruitment','recent_status']},
      'reading_scope':dict(Counter(r['reading']['scope'] for r in rows)),'fulltext_count':sum(r['reading']['fulltext'] for r in rows)}

def main():
    rows=load('all_evidence_records.json');by={r['id']:r for r in rows}
    cases=load('candidate_cases.json');pr=load('project_recommendations.json');comp=load('项目统一比较与阅读优先级.json')
    stats=load('需求覆盖统计.json');norm=load('统一样本分类与候选人关联.json')
    if not (BASE/'持续补证前主数据快照.json').exists():
        dump('持续补证前主数据快照.json',{'records':rows,'coverage':stats,'cases':cases,'projects':pr,'comparison':comp})
    cvsource=load('持续补证_实习履历与本人源码.json');ssp=load('持续补证_SSP岗位与批次.json')
    platform=load('持续补证_Agent平台专业观点.json');static=load('持续补证_贡献静态核查.json')
    added=[]
    p=cvsource['candidate'];u=p['fixed_source']['url'];o=p['outcome'];event=p['event_time']
    p['source_url']=u
    c={'id':'CV28','source_key':'DAVIDHLP_DIRECT_CV_CODE','category':'候选人资料',
      'title':'DavidHLP：近期后端实习完整履历与本人开源项目直接关联','url':p['url'],
      'role':'后端开发实习','profile_type':p['profile_type'],'document_type':p['profile_type'],
      'date':event,'source_date':p['source_commit_time'],
      'taxonomy':tax('后端','实习',event,True,p['source_commit_time'],'完整职业履历明确2026.01—06；雇主和服务客户分列'),
      'reading':read(p['reading_scope']),'outcome':'博彦科技后端实习，服务阿里云客户项目；非阿里直签，未分档',
      'outcomes':[{'company':o['employer'],'role':o['role'],'grade':'未披露','status':'internship_experience_self_report',
        'date':event,'evidence_url':u,'basis':'本人完整履历列实习时间、岗位和雇主；客户项目为'+o['client_project'],
        'boundary':'客户不是雇主；不计阿里直签实习或SSP','independent_employer_verified':False}],
      'stack':['Java','Spring Boot','Redis','SQL','消息投递','缓存并发','Arthas','容器排障'],
      'projects':p['direct_project_links'],'complete_redacted_cv_file_received':True,
      'redacted_cv_local_file':p['local_path'],'complete_cv_file_received':False,'cv_file_licensed_for_redistribution':False,
      'ssp_claim_present':False,'ssp_grade_company_explicit':False,'has_direct_named_project_or_contribution':True,
      'personal_source_code_verified':True,'has_confirmed_personal_interview_source':True,'interview_evidence_ids':['INT81'],
      'chain':{'outcome':[node(u,'本人职业履历明确博彦雇主、阿里云客户、后端岗位与2026.01—06','非阿里直签；任职限本人自述，档位未知')],
        'profile':[node(u,'全部公开专业模块；本地去联系方式转录副本','不是已核投递版本')],
        'project':[node(x['fixed_repo'],'完整履历直接点名并链接'+x['name']+'；指定实现与测试已静态核读','当前源码版本晚于实习，个人依赖和逐次贡献未全审') for x in cvsource['projects']],
        'interview':[node(cvsource['interview']['source']['url'],'本人站原版自述两轮Java实习复盘','公司、事件年和录用结果未知；与两仓仅主题对应，不绑定博彦录用')]},
      'source_summary':'目前新增的直接履历→本人源码样本。业务项目和缓存扩展各有侧重，适合比较具体机制。',
      'recommendation':'精读本人职责与两仓指定模块；实习与开源作品、面经时点分别核对。',
      'weaknesses':p['limits'],'source_record':p}
    refresh_chain(c);added.append(c)
    d=cvsource['interview']
    added.append({'id':'INT81','source_key':'DAVIDHLP_LEGACY_INTERVIEW','category':'面经复盘',
      'title':d['title']+'（原版两轮，含事后模板）','url':d['source']['url'],'company':d['company'],
      'role':'Java后端实习','date':'事件年月日未知','source_date':d['publication_time'],
      'taxonomy':tax('后端','实习','事件年月日未知',False,d['publication_time'],'文章时间不是面试时间；两轮不拆为两位候选人'),
      'reading':read(d['reading_scope'],False),'fulltext_verified':False,
      'material_type':'面试问题与部分事后解答混合','candidate_link_ids':['CV28'],
      'strict_recent_internship':False,'publication_recent_event_year_unknown':True,'sample_group':'明确实习面经',
      'result_status':'unknown','outcome':'公司和录用结果未知；不绑定已知实习雇主','outcomes':[],
      'topics':['Spring Cache','缓存并发','OJ','MQ选型','容器隔离','CPU排障'],
      'project_questions':[x['question'] for x in d['questions']],
      'summary':d['question_answer_boundary']+'；'+d['version_difference'],
      'questions_vs_retrospective_answers':d['question_answer_boundary'],'source_record':d})
    # 本人逐轮面经三篇：均为校招，不借新材料增加近期实习数量。
    lewy_ids=[]
    for ident,d in zip(['INT78','INT79','INT80'],ssp['new_interview_material_candidates']):
        lewy_ids.append(ident)
        added.append({'id':ident,'source_key':d['source_key'],'category':'面经复盘','title':d['title'],'url':d['canonical_url'],
          'company':d['company'],'role':d['role'],'date':d['event_date'],'source_date':d['source_dates']['published_utc'],
          'taxonomy':tax('后端','校招',d['event_date'],True,d['source_dates']['published_utc'],d['event_year_basis']),
          'reading':read('公开文字全文已读；同作者主文直接链接、原帖作者ID一致'),
          'fulltext_verified':True,'material_type':'同候选人多场汇总（不拆成独立候选人）',
          'candidate_link_ids':['CV01'],'strict_recent_internship':False,'publication_recent_event_year_unknown':False,
          'sample_group':'明确校招面经','result_status':'next_round_or_waiting_self_report' if ident=='INT80' else 'offer_self_report',
          'outcome':d['result']['single_article'],'outcomes':[{'company':d['company'],'role':d['role'],'grade':'未披露',
            'status':'next_round_or_waiting_self_report' if ident=='INT80' else 'offer_self_report','evidence_url':d['canonical_url'],
            'basis':d['result']['single_article'],'boundary':d['result']['boundary'],'independent_employer_verified':False}],
          'topics':{'INT78':['IM','心跳与连接','时间轮','消息可靠性','Kafka','性能测试'],
            'INT79':['项目瓶颈','IM','消息队列选型','性能瓶颈与排障','全链路','AI业务讨论'],
            'INT80':['Golang并发','IPC/Protobuf','TCP容量','SQL','项目选型']}[ident],
          'project_questions':d['questions_paraphrased'],
          'summary':d.get('questions_vs_answers','本人具体问题与作答自评混合，未给完整答案；不是逐字稿'),
          'rounds':d['rounds'],'source_record':d})
    for update in ssp['existing_candidate_updates']:
        c=by[update['existing_id']];c['latest_source_review']=update
        if c['id']=='CV03':
            t=update['suggested_taxonomy'];c['taxonomy'].update({'recruitment':'混合','experience_date_text':t['experience_date_text'],
              'date_precision':'范围','year_confirmed':True,'recent_status':'近期确认','date_basis':update['date_basis']+'；'+t['boundary']})
            c['date']=t['experience_date_text'];c['outcomes']=[{**o,'evidence_url':update['primary_url'],'date':o['event_date'],'independent_employer_verified':False} for o in update['outcome_updates']]
            c['outcome']='美团2025暑期后同公司SSP、安克SSP；京东SSP与网易SP为作者推定；华为15a单列'
            c['chain']['outcome']=[node(update['primary_url'],o['company']+' '+o['grade']+'；'+o['basis'],o.get('boundary','限本人自述；不推断统一SSP要求')) for o in c['outcomes']]
        else:
            c['outcomes']=[{**o,'evidence_url':update['primary_url'],'date':'2025秋招','independent_employer_verified':False} for o in update['ssp_company_updates']]
            c['ssp_grade_company_explicit']=True;c['has_confirmed_personal_interview_source']=True;c['interview_evidence_ids']=lewy_ids
            c['has_direct_named_project_or_contribution']=True;c['personal_source_code_verified']=False
            c['direct_named_relationship_scope']='主文与面经直接描述本人IM和通知服务；仅项目文字/履历关系，不代表已取得源码。'
            c['outcome']='字节、快手、小鹏SSP为本人最终总结自述；第四家SSP公司未核；滴滴/百度档位未定'
            c['chain']['interview']=[node(d['canonical_url'],d['title']+'；主文直接链接且署名ID一致','单篇阶段结果与后来SSP总结分开；源码仍缺') for d in ssp['new_interview_material_candidates']]
            c['chain']['outcome']=[node(update['primary_url'],o['company']+' '+o['grade']+'；'+o['basis'],'具体公司仅按本人最终总结；第四家公司未知') for o in c['outcomes']]
        refresh_chain(c)
    # 平台文章为教学概念，保留纠错，不能计入真实面经。
    p=platform['sources'][0]
    added.append({'id':'OP13','source_key':p['proposed_key'],'category':'B站与知乎','title':p['title'],'url':p['url'],
      'platform':p['platform'],'author':p['author'],'taxonomy':{**tax('Agent工程','不适用','教学文章，非招聘事件',False,p['source_date']),'recent_status':'不适用'},
      'reading':p['reading'],'platform_native_fulltext_verified':True,'verified_video_viewing':False,
      'identity_evidence':p['identity'],'opinion':p['summary'],'commercial_bias':p['commercial_background'],
      'recommendation':p['recommendation'],'limits':p['quality_limitations'],'required_corrections':p['corrections_required'],
      'official_crosschecks':platform['official_crosschecks'],'source_record':p})
    for review in static['reviews']:
        c=by[review['related_id']];c['static_implementation_review']=review
        if c['id']=='CV22':
            for n in c['chain']['project']:
                if 'AsTimeWheel' in (n.get('url') or ''):n['gap']='同账号关系，未证求职使用；已静态读核心与mock测试，存在初始化/时钟/取消语义风险，未运行'
            refresh_chain(c)
        else:
            for p in c['source_record']['projects']:
                if '#12263' in p['name']:p['caveat']='已核gty111作者、2025-12-14合并与局部实现/测试；76提交为多人协作，不代表全部个人独立贡献或Agent应用岗位'
    # 两个项目只因明确本人关系而新增，不按通用框架数量扩充。
    for ident,p in zip(['PRO20','PRO21'],cvsource['projects']):
        fs=p['implementation_and_tests'];name=p['name'];url=p['fixed_repo'];is_oj=ident=='PRO20'
        def cell(status,finding,index=0):
            f=fs[index];return {'status':status,'finding':finding,'source_URL':f['url'],'read_paths':[f['path']],'read_scope':f['reading_scope']+'；未运行'}
        bd={
          '业务闭环':cell('文档宣称' if is_oj else '不适用','履历点名OJ提交与判题平台；本次仅审投递/结果路径，不证明完整业务验收。' if is_oj else '缓存扩展库，提供可复用机制而非独立业务应用。'),
          '一致性':cell('源码可见','结果写回同时核generation和attempt；不证明消息端到端恰好一次。' if is_oj else 'Lua按缓存值版本CAS缩短TTL，需核版本生成和跨节点并发边界。',1 if is_oj else 2),
          '并发':cell('源码可见','条件更新与租约恢复可定位；所有竞争路径未审。' if is_oj else 'putIfAbsent选择leader、共享Future与身份匹配清理；本地合并不能直接推为全局仅一次回源。',1),
          '缓存MQ':cell('源码可见','Outbox投递与退避有实现，Redis Streams有集成测试；DB事务不自动跨Redis原子提交。' if is_oj else '缓存TTL/CAS及回源并发机制可定位；此项未证明消息队列能力。',0 if is_oj else 2),
          '测试':cell('源码可见','Redis Streams集成测试代码可读，未执行。' if is_oj else '并发共享、异常、重入、超时与竞态测试代码可读，未执行。',3),
          '可运行材料':cell('未核','固定源码包/链接及测试材料已取；本次未构建或验证环境。'),
          '个人贡献':{'status':'文档宣称','finding':p['ownership_evidence']+'；逐提交和AI辅助占比未审。','source_URL':u,'read_paths':[],'read_scope':'完整本人履历直接链接；不将依赖视为原创'}
        }
        ad={k:{'status':'不适用','finding':'后端业务/缓存项目，本次未核自主Agent任务循环，不计Agent项目。','source_URL':url,'read_paths':[],'read_scope':p['reading_scope']} for k in comp['dimensions']['agent']}
        if is_oj:
            entry=next(f for f in fs if f['path'].endswith('DefaultSubmissionWritePort.java'))
            bd['一致性'].update({'finding':'提交与Outbox同DB事务入口可见，写Outbox依特性开关；结果有generation/attempt条件；外部Redis投递不在同DB事务内。',
              'source_URL':entry['url'],'read_paths':[entry['path'],fs[1]['path']],'read_scope':entry['reading_scope']+'；SQL条件与开关同时核，未运行'})
        else:
            bd['测试']['read_paths'].append(fs[4]['path'])
            bd['测试']['read_scope']+='；另核提前过期竞态集成测试的场景与断言'
        build_path='docker/docker-compose.yml' if is_oj else 'pom.xml'
        bd['可运行材料']={'status':'源码可见','finding':'归档有构建描述/容器配置；去联系字段及省图像可能影响构建，未验证。',
          'source_URL':'https://github.com/'+p['repo']+'/blob/'+p['sha']+'/'+build_path,'read_paths':[build_path],
          'read_scope':'固定归档路径存在性；不称构建或测试已通过'}
        archive=p.get('attachment',p.get('archive',{}))
        archive_path=archive.get('local_path')
        if archive_path and archive_path.startswith('05_项目源码归档/'):archive_file=archive_path.split('/',1)[1]
        else:archive_file=None
        relation={'candidate_id':'CV28','relationship_type':'直接点名','direct_evidence_URLs':[u],
          'finding':'完整履历直接链接本人'+name+'，指定实现与测试可读；本人面经仅主题对应。',
          'event_time_boundary':'实习2026.01—06；此源码版本另列','snapshot_boundary':p['source_commit_time']+'；不回填投递版',
          'offer_causality':'不证明项目导致录用；不是大厂直签或SSP样本'}
        comparison={'id':ident,'title':name+'：完整履历直接点名的本人'+('判题平台' if is_oj else '缓存扩展'),
          'repo':p['repo'],'source_URL':url,'commit':p['sha'],'source_nature':['本人开源项目','现版实现，求职版本未知'],
          'candidate_relationships':[relation],'backend_dimensions':bd,'agent_dimensions':ad,
          'backend_priority':{'level':'精读','reason':'适合按消息故障/结果竞争读具体业务实现。' if is_oj else '适合深入缓存并发、清理和测试边界。','read_modules':[f['path'] for f in fs]},
          'agent_priority':{'level':'选读','reason':'可补异步任务可靠性与服务基础；不作为Agent项目证明。','read_modules':[fs[0]['path']]},
          'evidence_completeness':'本人履历→点名源码直接；面经仅主题对应，公司/事件年/结果未知；现版晚于实习。',
          'target_applicability':'后端实习实现阅读样本；外包雇主与互联网大厂直签分别呈现。',
          'attachment':{'status':'固定版本源码文本归档（去联系字段，非完整原ZIP）' if archive_file else '固定源码链接材料','archive_file':archive_file,'exists':bool(archive_file),
            'reason':p.get('archive_status','固定版本公开源码'),'source_manifest':'08_证据索引与统计/持续补证_实习履历与本人源码.json','runtime_verified':False},
          'read_paths':[f['path'] for f in fs],'strengths':[f['finding'] for f in fs],
          'limitations':p['limitations']+(['数据库事务与Redis投递之间的崩溃重复窗口、死信及消费者幂等需全链路另核。'] if is_oj else ['本地single-flight与跨实例互斥不同，不能仅据本地Map推导分布式唯一回源。']),
          'commercial_background':'未核商业关系；公开源码、履历和测试存在不证明录用收益。',
          'run_status':'未运行项目、测试或压测；仅指定版本静态阅读。','source_nature_boundary':p['ownership_evidence'],
          'priority_interpretation':'精读指定机制和局限，不要求整库复刻。'}
        added.append({'id':ident,'source_key':'DAVIDHLP_'+name.upper(),'category':'项目参考','title':comparison['title'],'url':url,
          'author':'DavidHLP','commit':p['sha'],'taxonomy':{**tax('后端','不适用','开源版本，非招聘事件',False,p['source_commit_time']),'recent_status':'不适用'},
          'reading':read(p['reading_scope'],False),'outcomes':[],'source_findings':fs,'strengths':comparison['strengths'],
          'limitations':comparison['limitations'],'recommended_use':p['recommendation'],'archive_file':archive_file,
          'archive_status':comparison['attachment']['status'],'license_notes':p['license'],
          'project_relationship':relation['finding'],'candidate_links':['CV28'],'source_record':p,'comparison':comparison})
        comp['projects']=io.merge(comp['projects'],[comparison])
    for r in added:
        if r['id'] in by:assert by[r['id']].get('source_key')==r['source_key'],r['id']
    rows=io.merge(list(by.values()),added)
    focus={}
    if (BASE/'重点补证构造.py').exists() and (BASE/'重点补证_大厂实习履历.json').exists():
        focus_spec=importlib.util.spec_from_file_location('focused_records',BASE/'重点补证构造.py')
        focus_module=importlib.util.module_from_spec(focus_spec);focus_spec.loader.exec_module(focus_module)
        rows,comp,focus=focus_module.apply(rows,comp)
    agent_extra={}
    if (BASE/'近期Agent补链构造.py').exists() and (BASE/'近期Agent补链_脱敏简历.json').exists():
        spec=importlib.util.spec_from_file_location('agent_chain_records',BASE/'近期Agent补链构造.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        rows,comp,agent_extra=module.apply(rows,comp)
    time_extra={}
    if (BASE/'SSP与时间补核_来源核读.json').exists():
        spec=importlib.util.spec_from_file_location('time_review_records',BASE/'SSP与时间补核构造.py')
        time_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(time_module)
        rows,comp,time_extra=time_module.apply(rows,comp)
    expert_extra={}
    if (BASE/'专业观点交叉核对_来源与比较.json').exists():
        spec=importlib.util.spec_from_file_location('expert_comparison_records',BASE/'专业观点交叉核对构造.py')
        expert_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(expert_module)
        rows,comp,expert_extra=expert_module.apply(rows,comp)
    interview_extra={}
    if (BASE/'近期面经与关联纠错_来源核读.json').exists():
        spec=importlib.util.spec_from_file_location('recent_interview_records',BASE/'近期面经与关联纠错构造.py')
        interview_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(interview_module)
        rows,comp,interview_extra=interview_module.apply(rows,comp)
    archive_extra=[]
    if (BASE/'补齐项目选读归档.py').exists():
        spec=importlib.util.spec_from_file_location('archive_updates',BASE/'补齐项目选读归档.py')
        archive_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(archive_module)
        rows,comp,archive_extra=archive_module.apply(rows,comp)
    by={r['id']:r for r in rows}
    cvs=sorted([r for r in rows if r['category']=='候选人资料'],key=lambda r:r['id'])
    ivs=sorted([r for r in rows if r['category']=='面经复盘'],key=lambda r:r['id'])
    ops=sorted([r for r in rows if r['category']=='B站与知乎'],key=lambda r:r['id'])
    projects=sorted([r for r in rows if r['category']=='项目参考'],key=lambda r:r['id'])
    cvs_stats={**stats['candidate_coverage'],**group(cvs)}
    for key,flag in [('complete_cv_files_received','complete_cv_file_received'),('complete_redacted_cv_files_received','complete_redacted_cv_file_received'),
      ('confirmed_personal_interview_source_cases','has_confirmed_personal_interview_source'),('ssp_claim_cases','ssp_claim_present'),('ssp_company_explicit_cases','ssp_grade_company_explicit')]:
        cvs_stats[key]=sum(bool(r.get(flag)) for r in cvs)
    cvs_stats['profile_type']=dict(Counter(r['profile_type'] for r in cvs))
    cvs_stats['ssp_company_explicit_excluding_CV20_guest_article']=sum(bool(r.get('ssp_grade_company_explicit')) for r in cvs if r['id']!='CV20')
    cvs_stats['source_attribution_note']=f"CV20为第三方收录署名来稿；CV06经技术站点发布/转载。排除CV20后{cvs_stats['ssp_company_explicit_excluding_CV20_guest_article']}份为公司明确SSP自述，不等于全部由作者原账号发布，也不是证据等级计分。"
    strict=[r['id'] for r in ivs if r.get('strict_recent_internship')];aux=[r['id'] for r in ivs if r.get('publication_recent_event_year_unknown')]
    iv_stats={**stats['interview_coverage'],**group(ivs),'strict_recent_explicit_internship_count':len(strict),
      'strict_recent_explicit_internship_ids':strict,'publication_recent_event_year_unknown_count':len(aux),
      'publication_recent_event_year_unknown_ids':aux,'explicit_internship_all_years_count':sum(r['taxonomy']['recruitment']=='实习' for r in ivs),
      'explicit_internship_event_year_unknown_count':sum(r['taxonomy']['recruitment']=='实习' and r['taxonomy']['recent_status']=='年份未知' for r in ivs),
      'mixed_recruitment_count':sum(r['taxonomy']['recruitment']=='混合' for r in ivs),'unconfirmed_recruitment_count':sum(r['taxonomy']['recruitment']=='未知' for r in ivs),
      'result_status':dict(Counter(r['result_status'] for r in ivs)),'material_type':dict(Counter(r['material_type'] for r in ivs)),
      'read_source_material_count':len(ivs),'denominator_note':f'{len(ivs)}份逻辑资料，不等于独立面试场数、候选人数或成功者人数；同作者多场不拆成新人。'}
    op_stats={**stats['opinion_coverage'],**group(ops),'primary_bilibili_or_zhihu_full_content_verified_count':sum(bool(r.get('platform_native_fulltext_verified')) for r in ops),
      'zhihu_native_fulltexts_read':sum(bool(r.get('platform_native_fulltext_verified')) and '知乎' in r.get('platform','') for r in ops),
      'bilibili_native_articles_read':sum(bool(r.get('platform_native_fulltext_verified')) and 'B站' in r.get('platform','') for r in ops),
      'actual_video_watched_count':sum(bool(r['reading'].get('video_watched')) for r in ops),
      'new_native_source_authors':1,'native_authors_scope':'原平台全文篇数与署名作者数分别计算；同一作者多篇材料不当多位独立意见者。',
      'identity_boundary':'HR身份仅自述；鱼皮有商业推广且一篇署名/叙述矛盾；OP13是可核教学内容作者，不升格企业面试官或生产团队。'}
    native_ops=[r for r in ops if r.get('platform_native_fulltext_verified')]
    native_authors={r.get('author','').split('（',1)[0].strip() for r in native_ops}
    op_stats['primary_external_transcripts_selected']=sum(bool(r.get('primary_external_transcript_selected')) for r in ops)
    op_stats['native_authors_scope']=f'原平台{len(native_ops)}篇已读全文来自{len(native_authors)}位署名作者；同一作者多篇材料不当多位独立意见者。'
    archive_count=sum(bool(p['attachment'].get('archive_file')) for p in comp['projects'])
    derived_archives=archive_count-16
    comp['counts']={'projects':len(projects),'source_archives':archive_count,'original_fixed_source_zips':16,'redacted_text_source_zips':derived_archives,'fixed_link_only':len(projects)-archive_count,'executed_projects':0}
    comp['validation'].pop('all_19_backend_and_agent_dimensions_present',None)
    comp['validation']['all_project_dimensions_present']=all(len(p['backend_dimensions'])+len(p['agent_dimensions'])==15 for p in comp['projects'])
    comp['reading_routes']['backend']['精读_本人履历直接点名']=['PRO20','PRO21']
    routes=load('两方向阅读顺序.json');routes['backend']['candidate_ids']=list(dict.fromkeys(['CV28','CV23','CV22','CV27','CV25']+routes['backend']['candidate_ids']))
    routes['backend']['interview_ids']=list(dict.fromkeys(['INT81']+routes['backend']['interview_ids']+lewy_ids))
    routes['backend']['candidate_boundary']='CV28有完整履历直接链接本人源码，雇主博彦、客户阿里云分开；面经仅主题对应。CV23等大厂内部项目仍无公开实现。校招SSP逐轮为进阶对照。'
    routes['backend']['project_routes']['精读_本人履历直接点名']=['PRO20','PRO21'];routes['read_professional_ids']=list(dict.fromkeys(routes['read_professional_ids']+['OP13']))
    if focus:
        routes['backend']['candidate_ids']=list(dict.fromkeys(['CV29','CV30']+routes['backend']['candidate_ids']))
        routes['agent']['candidate_ids']=list(dict.fromkeys(['CV30','CV07']+routes['agent']['candidate_ids']))
        routes['agent']['interview_ids']=list(dict.fromkeys(routes['agent']['interview_ids']+['INT82','INT83']))
        for direction in ['backend','agent']:
            routes[direction]['interview_ids'].sort(key=lambda i:0 if by[i].get('strict_recent_internship') else 1 if by[i]['taxonomy']['recruitment']=='实习' else 2)
        routes['backend']['candidate_boundary']='CV29有2025腾讯/2026 Stripe实习和主页直接项目链接，履历不完整且课程框架边界明确；CV30为字节2025后端/2026 Agent完整CV，无公开内部源码。CV28为交付企业，非阿里直签。'
        routes['agent']['candidate_boundary']='优先CV30完整Agent应用后端实习职责；CV07的2025年仅确认两家后端offer，AML/百度面经批次和年份未知。QuantHarbor为风险对照，不能当成熟Agent。'
        routes['backend']['project_routes']['选读_大厂实习者本人项目']=['PRO22']
        routes['agent']['project_routes']['待核_状态与隔离风险对照']=['PRO23']
        routes['read_professional_ids']=list(dict.fromkeys(routes['read_professional_ids']+['OP14']))
    if agent_extra:
        routes['agent']['candidate_ids']=list(dict.fromkeys(['CV31']+routes['agent']['candidate_ids']))
        routes['agent']['project_routes']['选读_本人Agent实现与风险']=['PRO24','PRO25']
        routes['agent']['candidate_boundary']='CV31近期中科曙光Agent实习有完整CV和本人源码直链；框架继承、模块风险、本人面经及SSP缺口另列。CV30为互联网大厂内部Agent履历，无公开内部源码。'
        routes['read_professional_ids']=list(dict.fromkeys(routes['read_professional_ids']+['OP15']))
    if time_extra:
        routes['agent']['interview_ids']=list(dict.fromkeys(routes['agent']['interview_ids']+time_extra['added_ids']))
        routes['agent']['interview_ids'].sort(key=lambda i:0 if by[i].get('strict_recent_internship') else 1 if by[i]['taxonomy']['recruitment']=='实习' else 2)
    if expert_extra:routes['read_professional_ids']=list(dict.fromkeys(routes['read_professional_ids']+expert_extra['added_ids']))
    if interview_extra:
        routes['backend']['interview_ids']=list(dict.fromkeys(routes['backend']['interview_ids']+interview_extra['added_ids']))
        routes['backend']['interview_ids'].sort(key=lambda i:0 if by[i].get('strict_recent_internship') else 1 if by[i]['taxonomy']['recruitment']=='实习' else 2)
    blocked=load('待手动访问链接.json')
    for p in platform['access_limits']:
        blocked.append({'title':p.get('title','待核原文'),'url':p['url'],'status':p['status'],'to_verify':p.get('check','实际正文、作者关系与技术依据')})
    if (BASE/'持续补证_Agent专业案例原文.json').exists():
        for p in load('持续补证_Agent专业案例原文.json')['manual_links']:
            blocked.append({'title':p.get('title',p.get('discovered_topic','待核专业原文')),'url':p['url'],
              'status':p['actual_status'],'to_verify':p['check']})
    if (BASE/'持续补证_Agent_SSP缺口复核.json').exists():
        for p in load('持续补证_Agent_SSP缺口复核.json')['new_partial_primary_evidence']:
            blocked.append({'title':p['title']+'（本人AI应用SSP文字已读，信息未披露）','url':p['url'],
              'status':'HTTP200公开文字已读；公司/事件年/具体岗位未披露，简历图未读',
              'to_verify':p['next_missing_evidence']})
    if focus:
        blocked=[r for r in blocked if '927156901626810368' not in r['url'] and '/discuss/1674344' not in r['url']]
        blocked+=focus['manual']
        platform_focus=load('重点补证_平台正文与适用范围.json')
        for p in platform_focus['video_subtitle_access_attempts']:
            blocked.append({'title':'B站视频字幕待核','url':p['url'],'status':p['status']+'；未取得CID或字幕，观看0',
              'to_verify':'实际视频/字幕内容与观点；不把公开简介当观看'})
    if (BASE/'继续补证_检索决策与交付.json').exists():
        follow=load('继续补证_检索决策与交付.json');blocked+=follow['manual_additions']
        for update in follow['manual_updates']:
            for item in blocked:
                if update['url_contains'] in item['url']:
                    item.update({k:v for k,v in update.items() if k!='url_contains'})
    if agent_extra:blocked+=agent_extra['manual']
    if time_extra:blocked=time_module.update_manual(blocked)
    if expert_extra:blocked=expert_module.update_manual(blocked)
    if interview_extra:blocked=interview_module.update_manual(blocked)
    blocked=list({io.canonical(r['url']):r for r in blocked}.values())
    stats.update({'candidate_coverage':cvs_stats,'interview_coverage':iv_stats,'opinion_coverage':op_stats,'project_coverage':comp['counts'],
      'new_complete_core_redacted_cvs_this_pass':1,'current_pass':'持续补证',
      'new_qualifying_internship_chains_this_pass':1,'qualifying_chain_scope':'CV28近期后端实习履历→本人点名源码；非大厂直签，未闭合特定面经与录用流程。',
      'current_round_summary':'新增一份完整后端实习履历脱敏副本及两个本人源码项目；补3篇同一SSP作者的校招逐轮面经和1份含事后模板的实习复盘；修正CV03的2025时间线和推测档位。另读1篇Agent知乎教学文并按官方材料纠错。',
      'remaining_gaps':['近期互联网大厂直签后端/Agent成功实习者的完整履历与具体公开本人实现关联仍不足；CV28为交付企业雇主，不能冲抵大厂直签。',
        '近期Agent工程SSP的具体公司、岗位和批次自述仍不足；已有宽泛自述不填入未披露信息，项目和面经关系按实际范围。',
        '已补Agent知乎教学概念文，但真实生产任务、评测/成本、权限与故障取舍的专业平台原文仍需补强；视频0。'],
      'runtime_boundary':'全部项目静态阅读；性能/评测未复现。此为证据范围，不新增必须运行全部项目的验收要求。'})
    if focus:
        stats['current_pass']='重点补证';stats['current_round_summary']=focus['summary']
        stats['qualifying_chain_scope']='新增大厂完整Agent后端CV与大厂实习者直链源码；前者无公开实现，后者仅履历片段，两者不能拼成同一人的完整链。'
        stats['remaining_gaps']=['已取得近期字节Agent完整CV和腾讯实习者本人源码，但分属不同作者；同人完整履历、成熟Agent实现和具体本人面经的关联仍不足。',
          '近期Agent工程SSP的公司、具体岗位、事件年和最终档位仍缺强直接样本；推定/加面、未具名、宽泛大模型岗位分开。',
          'B站已读近期AI工程学习观点，但视频/字幕仍为0；生产任务评测与权限/恢复的专业平台案例仍需补强。']
    if agent_extra:
        stats['current_pass']='近期Agent补链';stats['current_round_summary']=agent_extra['summary']
        stats['remaining_gaps']=agent_extra['remaining']
        stats['qualifying_chain_scope']='CV31完整Agent实习CV→本人项目直接链接；NoWorries仅14文件选读归档，Sprout为编排机制库。本人面经/SSP缺，未运行。'
        stats['project_text_selection_archive_count']=1
    if time_extra:
        stats.update({'current_pass':'SSP与时间补核','current_round_summary':time_extra['summary'],
          'remaining_gaps':time_extra['remaining'],'new_complete_core_redacted_cvs_this_pass':0,
          'new_complete_cv_files_this_pass':0,'new_qualifying_internship_chains_this_pass':0})
    if expert_extra:
        stats.update({'current_pass':'专业观点交叉核对','current_round_summary':expert_extra['summary'],'remaining_gaps':expert_extra['remaining']})
    if interview_extra:
        stats.update({'current_pass':'近期面经与关联纠错','current_round_summary':interview_extra['summary'],'remaining_gaps':interview_extra['remaining']})
    if archive_extra:stats['project_text_selection_archive_count']=1+len(archive_extra)
    stats['totals']['additional_primary_texts']=sum(r['category']=='专业原文补充' for r in rows)
    stats['totals'].update({'logical_evidence_records':len(rows),'candidate_cases':len(cvs),'interview_materials':len(ivs),
      'projects':len(projects),'source_archives':archive_count,'fixed_link_only':len(projects)-archive_count,
      'platform_opinion_records':len(ops),'manual_links':len(blocked),'original_fixed_source_zips':16,'redacted_text_source_zips':derived_archives})
    stats['category_counts']=dict(Counter(r['category'] for r in rows))
    cases['cases']=cvs;cases['counts']={'curated_cases':len(cvs),**cvs_stats};pr['projects']=projects
    for key,value in [('candidates',cvs),('interviews',ivs),('opinions',ops)]:norm['records'][key]=deepcopy(value)
    norm['statistics'].update({'candidates':cvs_stats,'interviews':iv_stats,'opinions':op_stats})
    for issue in norm['issues']:
        if issue['id']=='DATE02':
            issue['record_ids']=[i for i in issue['record_ids'] if i!='CV03']
            resolution_note=' CV03已由后续原文明确2025时间线解除，见latest_source_review。'
            issue['resolution']=issue['resolution'].replace(resolution_note,'')+resolution_note
    norm['methodology']['scope']='当前全部逻辑记录统一方向/招聘/时间/阅读分类；3研究履历另列，新增本人源码样本非大厂直签。'
    cap=load('能力要求四类证据对照.json')
    for a in cap['rows']:
        if a['id'] in ['CAP01','CAP02','CAP03','CAP04','CAP06']:
            a['candidate_ids']=list(dict.fromkeys(a['candidate_ids']+['CV28']))
        if a['id'] in ['CAP01','CAP03','CAP04','CAP06']:
            a['interview_ids']=list(dict.fromkeys(a['interview_ids']+['INT81']))
        if a['id']=='CAP02':a['interview_ids']=[i for i in a['interview_ids'] if i!='INT81']
        if a['id'] in ['CAP02','CAP04']:
            a['project_ids']=list(dict.fromkeys([i for i in a['project_ids'] if i!='PRO21']+['PRO20']))
        if a['id']=='CAP03':a['project_ids']=list(dict.fromkeys(a['project_ids']+['PRO21']))
        if a['id'] in ['CAP09','CAP10']:
            a['opinion_ids']=list(dict.fromkeys(a['opinion_ids']+['OP13']));a['gap']='OP13只提供带纠错的概念阅读；仍缺真实生产任务及故障验证的专业平台案例。'
        if focus:
            if a['id'] in ['CAP02','CAP06','CAP07','CAP09','CAP11']:
                a['candidate_ids']=list(dict.fromkeys(a['candidate_ids']+['CV30']))
            if a['id'] in ['CAP03','CAP04','CAP10']:a['candidate_ids']=[i for i in a['candidate_ids'] if i!='CV30']
            if a['id'] in ['CAP01','CAP02','CAP06']:a['candidate_ids']=list(dict.fromkeys(a['candidate_ids']+['CV29']))
            if a['id'] in ['CAP07','CAP09','CAP10','CAP11']:
                a['interview_ids']=list(dict.fromkeys(a['interview_ids']+['INT82']))
            if a['id'] in ['CAP01','CAP02','CAP03','CAP05','CAP11']:
                a['interview_ids']=list(dict.fromkeys(a['interview_ids']+['INT83']))
            if a['id'] in ['CAP06','CAP09','CAP11']:a['opinion_ids']=list(dict.fromkeys(a['opinion_ids']+['OP14']))
            if a['id'] in ['CAP09','CAP10']:a['project_ids']=list(dict.fromkeys(a['project_ids']+['PRO23']))
        if agent_extra:
            if a['id'] in ['CAP06','CAP07','CAP08','CAP09','CAP10','CAP11']:a['candidate_ids']=list(dict.fromkeys(a['candidate_ids']+['CV31']))
            if a['id'] in ['CAP06','CAP07','CAP09','CAP11']:a['project_ids']=list(dict.fromkeys(a['project_ids']+['PRO24']))
            if a['id'] in ['CAP06','CAP09','CAP10']:a['project_ids']=list(dict.fromkeys(a['project_ids']+['PRO25']))
            if a['id'] in ['CAP07','CAP11']:a['opinion_ids']=list(dict.fromkeys(a['opinion_ids']+['OP15']))
            if a['id'] in ['CAP09','CAP10','CAP11']:a['gap']='已补本人实现和生产访谈选读；实现存在静态风险，未运行；原始逐字稿选读不计B站视频观看，不能将控制流测试当任务正确率。'
        if time_extra and a['id'] in time_extra['capability_ids']:
            a['interview_ids']=list(dict.fromkeys(a['interview_ids']+time_extra['added_ids']))
        if expert_extra and a['id'] in expert_extra['capability_ids']:
            a['opinion_ids']=list(dict.fromkeys(a['opinion_ids']+expert_extra['added_ids']))
        if interview_extra:
            for ident,abilities in interview_extra['capabilities'].items():
                if a['id'] in abilities:a['interview_ids']=list(dict.fromkeys(a['interview_ids']+[ident]))
        a['support']={g:[{'id':k,'title':by[k]['title'],'url':by[k].get('url',''),'taxonomy':by[k]['taxonomy'],'reading_scope':by[k]['reading']['scope']} for k in a[g+'_ids']] for g in ['jd','interview','candidate','opinion','project']}
    for name,value in [('all_evidence_records.json',rows),('candidate_cases.json',cases),('interview_records.json',ivs),('project_recommendations.json',pr),
      ('统一样本分类与候选人关联.json',norm),('需求覆盖统计.json',stats),('项目统一比较与阅读优先级.json',comp),('两方向阅读顺序.json',routes),
      ('待手动访问链接.json',blocked),('能力要求四类证据对照.json',cap)]:dump(name,value)
    catalog=load('履历脱敏副本目录.json');catalog['core_files']=[r for r in cvs if r.get('complete_redacted_cv_file_received')]
    for control in catalog['records']:
        if control['key']=='gty111':control['projects']=by['OBS05']['source_record']['projects']
    dump('履历脱敏副本目录.json',catalog)
    # 原19项目CSV保留为历史快照，当前完整表使用不带固定数量的文件名。
    io.csv_write(ROOT/'06_项目分析与推荐/项目统一比较.csv',['ID','项目','方向','维度','状态','发现','依据','阅读路径','核读范围'],
      [[p['id'],p['title'],direction,dim,v['status'],v['finding'],v['source_URL'],';'.join(v['read_paths']),v['read_scope']]
       for p in comp['projects'] for direction in ['backend','agent'] for dim,v in p[direction+'_dimensions'].items()])
    io.csv_write(ROOT/'03_简历与候选人案例/候选人证据链对照.csv',['ID','标题','方向','招聘路径','事件时间','近期状态','结果自述','资料类型','录用证据','履历证据','项目贡献证据','本人面经','缺口'],
      [[r['id'],r['title'],r['taxonomy']['track'],r['taxonomy']['recruitment'],r['date'],r['taxonomy']['recent_status'],r.get('outcome',''),r['profile_type'],
        *[' | '.join((n.get('url') or '未建立')+'：'+n['direct_basis'] for n in r['chain'][k]) for k in ['outcome','profile','project','interview']],'；'.join(r['chain_gaps'])] for r in cvs])
    io.csv_write(ROOT/'04_面经与专业观点/面经统一分类.csv',['ID','标题','方向','招聘路径','实际时间','发表日期另列','事件年已证','近期状态','阅读范围','资料类型','结果','来源'],
      [[r['id'],r['title'],r['taxonomy']['track'],r['taxonomy']['recruitment'],r['date'],r['source_date'],r['taxonomy']['year_confirmed'],r['taxonomy']['recent_status'],r['reading']['scope'],r['material_type'],r.get('outcome',''),r['url']] for r in ivs])
    io.csv_write(BASE/'全部资料统一分类.csv',['ID','类别','标题','方向','招聘路径','实际事件时间','来源时间','事件年已证','近期状态','阅读范围','来源'],
      [[r['id'],r['category'],r['title'],r['taxonomy']['track'],r['taxonomy']['recruitment'],r['taxonomy']['experience_date_text'],r['taxonomy']['source_date_text'],r['taxonomy']['year_confirmed'],r['taxonomy']['recent_status'],r['reading']['scope'],r.get('url','')] for r in rows])
    io.csv_write(BASE/'能力要求四类证据对照.csv',['能力','后端相关性','Agent相关性','JD','面经','履历','专业原文','提问','考察能力','项目模块主题映射','研究归纳薄弱点','缺口'],
      [[a['ability'],a['backend_relevance'],a['agent_relevance'],*[';'.join(a[k]) for k in ['jd_ids','interview_ids','candidate_ids','opinion_ids']],a['question'],a['competency'],a['module'],a['common_pitfall'],a['gap']] for a in cap['rows']])
    file_rows=[[r['id'],'核心完整专业履历脱敏副本',r['redacted_cv_local_file'],r['source_record']['source_url'],'本人履历；投递版本未知'] for r in cvs if r.get('complete_redacted_cv_file_received')]
    file_rows += [[f'OBS{n:02d}','研究/Infra对照',r['local_path'],r['fixed_pdf_url'],'不计核心应用方向'] for n,r in enumerate(catalog['records'],5)]
    io.csv_write(ROOT/'03_简历与候选人案例/履历文件索引.csv',['资料ID','类型','本地文件','固定原始来源','范围'],file_rows)
    topic=load('interview_topic_index.json')
    for a in topic['themes']:
        matches=[r for r in ivs if re.search(a['rule'],flatten([r.get('topics',[]),r.get('project_questions',[])]),re.I)]
        a.update({'evidence_ids':[r['id'] for r in matches],'record_count':len(matches),
          'explicit_internship_ids':[r['id'] for r in matches if r['taxonomy']['recruitment']=='实习'],
          'strict_recent_internship_ids':[r['id'] for r in matches if r.get('strict_recent_internship')],
          'year_unknown_internship_ids':[r['id'] for r in matches if r['taxonomy']['recruitment']=='实习' and r['taxonomy']['recent_status']=='年份未知']})
    topic['scope_records']=len(ivs);dump('interview_topic_index.json',topic)
    io.csv_write(BASE/'面经主题索引.csv',['主题','全包资料数','明确实习资料数','严格近期实习资料数','实习事件年未知资料数','全包资料ID','严格近期ID'],
      [[a['theme'],a['record_count'],len(a['explicit_internship_ids']),len(a['strict_recent_internship_ids']),len(a['year_unknown_internship_ids']),';'.join(a['evidence_ids']),';'.join(a['strict_recent_internship_ids'])] for a in topic['themes']])
    cumulative_ids=list(dict.fromkeys([r['id'] for r in added]+focus.get('added_ids',[])+agent_extra.get('added_ids',[])+time_extra.get('added_ids',[])+expert_extra.get('added_ids',[])+interview_extra.get('added_ids',[])))
    progress={'date':'2026-10-23','status':'active','new_record_ids':cumulative_ids,'strengthened_ids':list(dict.fromkeys(['CV01','CV03','CV22','OBS05']+focus.get('changed_ids',[]))),
      'current_totals':stats['totals'],'complete_core_redacted_resumes':cvs_stats['complete_redacted_cv_files_received'],
      'new_personal_projects':sum(i.startswith('PRO') for i in cumulative_ids),'new_interview_sources':sum(i.startswith('INT') for i in cumulative_ids),'new_platform_fulltexts':sum(i.startswith('OP') and by[i]['reading']['scope']=='全文' for i in cumulative_ids),
      'remaining_gaps':stats['remaining_gaps'],'runtime_boundary':stats['runtime_boundary'],'completion_audit':'当前为实际补证进展；近期大厂本人源码与Agent具体SSP/专业案例缺口仍未完成。'}
    dump('持续补证统计.json',progress)
    if focus and not agent_extra:
        focus_progress={'date':'2026-10-23','status':'active','new_record_ids':focus['added_ids'],'strengthened_ids':focus['changed_ids'],
          'current_totals':stats['totals'],'complete_core_redacted_resumes':cvs_stats['complete_redacted_cv_files_received'],
          'summary':focus['summary'],'remaining_gaps':stats['remaining_gaps'],'strict_recent_interview_increment':0}
        dump('重点补证统计.json',focus_progress)
        write(ROOT/'00_重点补证_本轮更新说明.md','# 本轮重点补证\n\n'+focus['summary']+'\n\n'+
          '\n'.join('- '+x for x in stats['remaining_gaps'])+'\n\n源码为16份原固定ZIP和'+str(derived_archives)+'份去联系字段文本派生归档，均未运行。\n')
    if agent_extra and not time_extra:
        dump('近期Agent补链统计.json',{'date':'2026-10-23','status':'active','new_record_ids':agent_extra['added_ids'],'current_totals':stats['totals'],'complete_core_redacted_resumes':cvs_stats['complete_redacted_cv_files_received'],'new_interviews':0,'new_candidate_profiles':1,'new_projects':2,'selected_external_transcripts':1,'summary':agent_extra['summary'],'remaining_gaps':agent_extra['remaining']})
        write(ROOT/'00_近期Agent补链_更新说明.md','# 近期Agent补链\n\n'+agent_extra['summary']+'\n\n'+ '\n'.join('- '+x for x in agent_extra['remaining'])+'\n\nNoWorries归档为14文件文本选读；Sprout为固定版本19文本文件派生包；均未运行。完整CV脱敏副本保留全部专业模块。\n')
    if time_extra and not expert_extra:
        dump('SSP与时间补核统计.json',{'date':'2026-10-23','status':'active','new_record_ids':time_extra['added_ids'],
          'current_totals':stats['totals'],'summary':time_extra['summary'],'remaining_gaps':time_extra['remaining'],
          'new_interviews':1,'new_candidate_profiles':0,'new_projects':0,'new_ssp_cases':0,
          'strict_recent_increment':0,'actual_video_watched_increment':0})
        d=time_extra['source']['interview']
        lines=['# 百度Agent日常实习：15问与阅读边界','',d['recommended_use'],'',
          '原帖：'+d['url'],'实际可读入口：'+d['read_url'],'',d['reading_scope'],'',
          '## 问题归纳','']+[str(i)+'. '+q for i,q in enumerate(d['questions_paraphrased'],1)]
        lines+=['','手撕：'+d['coding_question'],'','## 本人自评与结果','',d['self_assessment'],'',d['result'],
          '','## 时间及关联边界','',d['event_date'],'',d['source_version_time'],'',d['year_inference'],'',d['ownership_boundary'],'',d['question_answer_boundary'],'']
        write(ROOT/'04_面经与专业观点/百度Agent日常实习_15问与阅读边界.md','\n'.join(lines))
        write(ROOT/'00_SSP与时间补核_更新说明.md','# SSP与时间补核\n\n'+time_extra['summary']+'\n\n新增INT84一份本人实习面经；未新增候选人、项目或SSP成功案例。事件年仅推定，结果未知；两个公开视频接口200但无返回字幕，观看0。\n\n'+ '\n'.join('- '+x for x in time_extra['remaining'])+'\n')
    if expert_extra and not interview_extra:
        dump('专业观点交叉核对统计.json',{'date':'2026-10-23','status':'active','new_record_ids':expert_extra['added_ids'],
          'current_totals':stats['totals'],'summary':expert_extra['summary'],'remaining_gaps':expert_extra['remaining'],
          'new_interviews':0,'new_candidate_profiles':0,'new_projects':0,'new_ssp_cases':0,'native_platform_increment':0,
          'comparisons':len(expert_extra['source']['comparisons'])})
        write(ROOT/'00_专业观点交叉核对_更新说明.md','# 专业观点交叉核对\n\n'+expert_extra['summary']+'\n\n新增OP16一份平台外原始演讲选读与三项比较；未新增候选人、面经、项目或SSP成功案例。B站/知乎本体已读数不变。\n\n'+ '\n'.join('- '+x for x in expert_extra['remaining'])+'\n')
    if interview_extra:
        dump('近期面经与关联纠错统计.json',{'date':'2026-10-23','status':'active','new_record_ids':interview_extra['added_ids'],
          'current_totals':stats['totals'],'summary':interview_extra['summary'],'remaining_gaps':interview_extra['remaining'],
          'new_interviews':2,'new_candidate_profiles':0,'new_projects':0,'new_ssp_cases':0,'strict_recent_increment':1+len(interview_extra.get('date_confirmations',[])),'existing_interview_year_confirmations':interview_extra.get('date_confirmations',[])})
        write(ROOT/'00_近期面经与关联纠错_更新说明.md','# 近期面经与关联纠错\n\n'+interview_extra['summary']+'\n\n新增2份面经；另补核既有INT68的2026招聘事件年，本批明确近期实习合计增加2份。未新增简历、项目或SSP成功者。候选人总体结果去除单场面经适用标记，修正清单单列。\n\n'+ '\n'.join('- '+x for x in interview_extra['remaining'])+'\n')
    previous=load('目标执行统计.json')
    previous['new_record_ids']=list(dict.fromkeys(previous['new_record_ids']+progress['new_record_ids']))
    previous.update({'current_totals':stats['totals'],'complete_core_redacted_resumes':cvs_stats['complete_redacted_cv_files_received'],
      'remaining_gaps':stats['remaining_gaps'],'latest_increment':'近期面经与关联纠错统计.json' if interview_extra else '专业观点交叉核对统计.json' if expert_extra else 'SSP与时间补核统计.json' if time_extra else '持续补证统计.json','new_core_candidates':len([i for i in previous['new_record_ids'] if i.startswith('CV')]),
      'new_interviews':len([i for i in previous['new_record_ids'] if i.startswith('INT')]),
      'new_platform_fulltexts':len([i for i in previous['new_record_ids'] if i.startswith('OP') and by[i]['reading']['scope']=='全文']),'new_personal_projects':progress['new_personal_projects'],
      'strengthened_existing_ssp_candidates':['CV01','CV03']})
    dump('目标执行统计.json',previous)
    marker='\n\n以下为前轮历史方法说明，不作为当前统计：\n\n';method=io.read(BASE/'source_methodology.txt')
    if marker in method:method=method.split(marker,1)[1]
    write(BASE/'source_methodology.txt',f'持续补证最新口径（2026-10-23）\n{len(rows)}逻辑证据；{len(cvs)}候选人；{len(ivs)}面经；{len(projects)}项目；{archive_count}源码ZIP。\n核心完整脱敏专业履历{cvs_stats["complete_redacted_cv_files_received"]}；研究/Infra对照3，未修改原件0。\nB站图文{op_stats["bilibili_native_articles_read"]}、知乎正文{op_stats["zhihu_native_fulltexts_read"]}、视频0；平台题库不计真实面经。\n严格近期实习面经{len(strict)}，发表近期事件年未知{len(aux)}，校招新3篇另列。\n当前统计需求覆盖统计.json、进展持续补证统计.json。目标仍active。'+marker+method)
    for direction,title in [('backend','后端实习阅读顺序'),('agent','Agent实习阅读顺序')]:
        lines=['# '+title,'',routes['principle'],'',routes[direction]['candidate_boundary'],'','## 履历与面经','']
        for ident in routes[direction]['candidate_ids']+routes[direction]['interview_ids']:
            r=by[ident];lines+=['- ['+ident+' '+r['title']+']('+r['url']+')：'+r['taxonomy']['recruitment']+'／'+r['taxonomy']['recent_status'],'']
        lines+=['## 项目指定模块','']
        for p in comp['projects']:
            q=p[direction+'_priority']
            if q['level']=='非本方向':continue
            lines+=['- ['+p['id']+' '+p['title']+']('+p['source_URL']+')｜'+q['level']+'：'+q['reason'],'  模块：'+'；'.join(q['read_modules']),'  边界：'+p['evidence_completeness'],'']
        lines+=['个人项目设计继续暂缓。',''];write(ROOT/'06_项目分析与推荐'/(title+'.md'),'\n'.join(lines))
    write(ROOT/'00_持续补证_本轮更新说明.md','# 本轮持续补证\n\n'+stats['current_round_summary']+'\n\n'+
      '\n'.join('- '+x for x in stats['remaining_gaps'])+'\n\n'+stats['runtime_boundary']+'\n\n最新入口：01_调研报告/需求核对与阅读优先级.html；当前统计见08_证据索引与统计/持续补证统计.json。\n')
    print(json.dumps(progress,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
