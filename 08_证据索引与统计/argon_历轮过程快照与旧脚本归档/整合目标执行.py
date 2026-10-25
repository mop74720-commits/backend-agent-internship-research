"""整合实际核读增量；保留原始证据强弱，不把对照履历计为核心样本。"""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import importlib.util
import json
import re

BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('audit_io',BASE/'整合需求纠偏.py')
io=importlib.util.module_from_spec(spec);spec.loader.exec_module(io)
load,dump,write,flatten=io.load,io.dump,io.write,io.flatten
ROOT=BASE.parent
CV_IDS={'Asthenia0412':'CV22','zhh2001':'CV23','huomalxq':'CV24',
 'ANT_BYTE_590781977':'CV25','AGENT_216541357':'CV26','CPP_INTERN_564739493':'CV27'}
INT_IDS={'TIKTOK_876046266':'INT71','SANGFOR_14b2c379':'INT72','NINEBOT_c0b53fdd':'INT73',
 'MINISO_f844a4ac':'INT74','XHS_BAIDU_e319aadc':'INT75','IFLYTEK_1c425483':'INT76','CPP_SUMMER_737813386':'INT77'}

def taxonomy(track,recruitment,event,known=False,source='未核',basis='原文未明确事件年',applicable=True):
    return {'track':track,'recruitment':recruitment,'experience_date_text':event,
      'date_precision':'范围' if known else '未知','year_confirmed':known,
      'recent_status':('近期确认' if known else '年份未知') if applicable else '不适用',
      'date_basis':basis,'source_date_text':source}

def reading(note,scope='全文',native=False):
    r={'scope':scope,'fulltext':scope=='全文','scope_note':note,'video_watched':False}
    if native:r['primary_platform_scope']='全文'
    return r

def node(url,basis,relation='直接点名',gap=''):
    return {'url':url,'direct_basis':basis,'relation':relation,'gap':gap}

def unknown(basis):return [node(None,basis,'未建立',basis)]

def finish_candidate(r):
    r['category']='候选人资料';r['date']=r['taxonomy']['experience_date_text'];r['source_date']=r['taxonomy']['source_date_text']
    r['chain_gaps']=list(dict.fromkeys(n['gap'] for stage in r['chain'].values() for n in stage if n.get('gap')))
    r.setdefault('ssp_claim_present',False);r.setdefault('ssp_grade_company_explicit',False)
    r.setdefault('has_direct_named_project_or_contribution',False)
    r.setdefault('has_confirmed_personal_interview_source',False)
    r.setdefault('complete_cv_file_received',False);r.setdefault('cv_file_licensed_for_redistribution',False)
    r.setdefault('complete_redacted_cv_file_received',False)
    return r

def outcomes_from(raw,url):
    out=[]
    for o in raw:
        text=o.get('status','实习经历自述')
        status='internship_experience_self_report' if 'role' in o and 'status' not in o else 'offer_self_report' if ('offer' in text.lower() and 'OC' not in text) else 'intention_self_report' if 'OC' in text else 'failure_self_report' if ('感谢信' in text or '失败' in text) else 'mixed_or_overall_self_report'
        out.append({'company':o['company'],'role':o.get('role','未披露'),'grade':o.get('grade','未披露'),
          'status':status,'date':o.get('time',o.get('date','事件年未确认')),
          'evidence_url':o.get('evidence_url',url),'basis':o.get('basis',o.get('evidence',o.get('boundary','作者职业经历自述'))),
          'boundary':o.get('boundary','公开自述，不证明项目导致录用'),'independent_employer_verified':False})
    return out

def main():
    all_records=load('all_evidence_records.json');norm=load('统一样本分类与候选人关联.json')
    cases=load('candidate_cases.json');interviews=load('interview_records.json');projects=load('project_recommendations.json')
    stats=load('需求覆盖统计.json');old_stats=deepcopy(stats)
    if not (BASE/'目标执行前主数据快照.json').exists():
        dump('目标执行前主数据快照.json',{'all_evidence_records':all_records,'candidate_cases':cases,'interview_records':interviews,'coverage':stats,'normalized':norm})
    profiles=load('目标执行_近期履历发现.json');documents=load('目标执行_SSP与近期面经核读.json')
    platform=load('目标执行_平台正文核读.json');bili=load('目标执行_B站专业图文核读.json')
    added=[]
    for p in profiles['new_core_partial_profiles']:
        ident=CV_IDS[p['key']];url=p['url'];event='；'.join(o['company']+' '+o['time'] for o in p['outcomes'])
        added.append(finish_candidate({'id':ident,'source_key':p['key'],'title':p['author']+'：2025—2026后端与Agent工程实习履历片段','url':url,
          'role':'后端与Agent工程交叉','profile_type':p['profile_type'],'document_type':'本人公开GitHub职业履历片段，非完整简历',
          'outcome':'本人列出2025—2026多段后端实习；未披露SSP','stack':p['skills'],'projects':p['projects'],
          'taxonomy':taxonomy('混合','实习',event,True,p['commit_date'],'职业经历段直接列事件起止年；至今只指来源版本，不核抓取日任职'),
          'reading':reading(p['reading']),'outcomes':outcomes_from(p['outcomes'],url),
          'chain':{'outcome':[node(url,'本人profile直接列公司、实习岗位、年月','直接点名','未企业独立核验；未分档')],
            'profile':[node(url,p['profile_type'],'直接点名','缺教育及完整项目模块')],
            'project':[node(x['url'],x['content'],'同账号','profile未点名该项目；未证明求职使用，未读实现或运行') for x in p['projects']],
            'interview':unknown('未定位本人公开面经')},'source_summary':'近期明确后端实习事实更直接；个人项目与求职关系未建立。',
          'recommendation':'选读岗位时间线；不以同账号仓库填成个人求职项目','weaknesses':p['missing'],
          'source_record':p}))

    complete_profiles=deepcopy(profiles.get('new_core_complete_profiles',[]))
    for original in profiles.get('new_core_complete_pdf_profiles',[]):
        p=deepcopy(original)
        p.update({'url':p['home'],'source_url':p['fixed_pdf_url'],'profile_type':'完整公开PDF履历的脱敏专业模块副本',
          'reading':'固定PDF全部专业模块、本人公开HTML和相关项目文档核读','recommendation':p['analysis'],'limitations':p['limits']})
        complete_profiles.append(p)
    for p in complete_profiles:
        ident=CV_IDS[p['key']];url=p['url'];event='；'.join(o['company']+' '+o.get('time','未核') for o in p['outcomes'])
        local=p.get('local_html',p.get('local_path',p.get('local_pdf')))
        assert local and (ROOT/local).exists(),(p['key'],local)
        project_nodes=[]
        for x in p.get('projects',[]):
            repo=x.get('source_code',x.get('url'))
            project_nodes.append(node(repo or p.get('source_url',url),x.get('relation',x.get('name','本人项目描述')),
              '直接点名','企业/个人实现仅按已核范围；无公开实现时不补参考框架，未运行'))
        added.append(finish_candidate({'id':ident,'source_key':p['key'],'title':p['author']+'：近期实习完整公开履历脱敏副本','url':url,
          'role':p['track']+'实习','profile_type':p['profile_type'],'document_type':p['profile_type'],
          'outcome':'本人完整履历明确实习公司、岗位和起止时间；档位未披露','taxonomy':taxonomy('Agent工程' if 'Agent' in p['track'] else '后端','实习',event,True,p['commit_date'],'完整履历实习段直接标年月；非从届别/仓库日期推事件年'),
          'reading':reading(p['reading']),'outcomes':outcomes_from(p['outcomes'],p.get('source_url',url)),
          'complete_redacted_cv_file_received':True,'redacted_cv_local_file':local,
          'stack':p.get('skills',[]),'projects':p.get('projects',[]),'source_summary':p.get('analysis',p.get('recommendation','本人公开完整专业履历')),
          'chain':{'outcome':[node(o.get('evidence_url',p.get('source_url',url)),o['company']+' '+o['role']+' '+o.get('time',''),'直接点名','岗位经历为本人自述；网易客户端不计后端/Agent') for o in p['outcomes']],
            'profile':[node(p.get('source_url',url),'固定来源完整专业模块；本地提供去联系方式副本','直接点名','副本不是未修改原件；不能证明是求职当时投递版本')],
            'project':project_nodes or unknown('完整履历未给具体项目实现'),'interview':unknown('未定位本人公开求职面经；项目开发复盘单列')},
          'recommendation':p.get('recommendation','精读个人职责与项目机制；指标限本人自述'),
          'has_direct_named_project_or_contribution':bool(p.get('projects')),'personal_source_code_verified':False,
          'direct_named_relationship_scope':'只表示本人履历/文档直接点名；不表示具体源码已审或求职因果成立',
          'weaknesses':p.get('limitations',p.get('limits',[])),'source_record':p}))

    for p in documents['candidate_leads']:
        if p['lead_key'] not in CV_IDS:continue
        ident=CV_IDS[p['lead_key']];url=p['primary_url'];ints=[INT_IDS[i] for i in p['interview_keys'] if i in INT_IDS]
        pn=p['project_chain'];facts=pn.get('facts','；'.join(pn.get('projects',[])))
        added.append(finish_candidate({'id':ident,'source_key':p['lead_key'],'title':p['title'],'url':url,'role':p['track']+'实习',
          'outcome':'；'.join(o['company']+' '+o['status'] for o in p['outcomes']),
          'document_type':'本人职业经历与面经自述，非完整简历','profile_type':p['profile']['type'],
          'taxonomy':taxonomy(p['track'],'实习',p['event_date'],p['event_year_confirmed'],p.get('source_date','见原文/未核独立发表年'),p.get('date_basis','事件年份未明确，不按发表年补写')),
          'reading':reading(p['reading']),'outcomes':outcomes_from(p['outcomes'],url),
          'chain':{'outcome':[node(url,'；'.join(o['company']+' '+o['status'] for o in p['outcomes']),'直接点名','录用/OC/实习经历分别记录；无SSP')],
            'profile':[node(url,'；'.join(p['profile']['facts']),'直接点名','仅职业经历片段，非完整简历')],
            'project':[node(pn.get('source_url',url),facts or pn.get('relation','本人项目叙述'),'直接点名',pn['gap'])],
            'interview':[node(next(x['url'] for x in documents['interview_documents'] if x['key']==k),'本人主页直接串联该面经','直接点名','提问为本人回忆；公司结果不可串用') for k in p['interview_keys'] if k in INT_IDS]},
          'has_confirmed_personal_interview_source':bool(ints),'interview_evidence_ids':ints,
          'projects':pn,'stack':[],'source_summary':p['recommendation'],'recommendation':p['recommendation'],
          'weaknesses':p.get('limits',[pn['gap']]),'source_record':p}))

    author_cv={'590781977':'CV25','216541357':'CV26','564739493':'CV27'}
    for d in documents['interview_documents']:
        if d['key'] not in INT_IDS:continue
        ident=INT_IDS[d['key']];known=d['event_year_confirmed'];mixed=any(s in d['questions_vs_answers'] for s in ['事后解释','事后答案','问题与解答混合'])
        cv_id=author_cv[d['author_id']]
        outcome_status='failure_self_report' if d['key'] in ['SANGFOR_14b2c379','XHS_BAIDU_e319aadc'] else 'intention_self_report' if d['key']=='NINEBOT_c0b53fdd' else 'next_round_or_waiting_self_report' if d['key'] in ['MINISO_f844a4ac','IFLYTEK_1c425483'] else 'offer_self_report' if d['key']=='CPP_SUMMER_737813386' else 'unknown'
        material='本人总体/主题复盘（非逐轮原题）' if d['key']=='CPP_SUMMER_737813386' else '面试问题与部分事后解答混合' if mixed else '同候选人多场汇总（不拆成独立候选人）' if len(d['rounds'])>1 else '本人具体问题记录'
        added.append({'id':ident,'source_key':d['key'],'category':'面经复盘','title':d['title'],'url':d['url'],
          'role':d['role'],'company':d['company'],'date':d['event_date'],'source_date':d.get('source_date','发表时间未核'),
          'taxonomy':taxonomy('后端' if d['author_id'] in ['590781977','564739493'] else 'Agent工程','实习',d['event_date'],known,d.get('source_date','未核'),
             '正文直接年份与同一职业时间线；不使用届别推年' if known else '单篇事件年未明；同作者导航或发表元数据不自动绑定具体场次'),
          'reading':reading(d['scope']),'fulltext_verified':True,'material_type':material,'candidate_link_ids':[cv_id],
          'strict_recent_internship':known,'publication_recent_event_year_unknown':not known and d.get('source_date','').startswith('2026'),
          'sample_group':'明确实习面经','result_status':outcome_status,'outcome':d['outcome'],
          'outcomes':[{'company':d['company'],'grade':'未披露','status':outcome_status,'evidence_url':d['url'],'basis':d['outcome'],'independent_employer_verified':False}],
          'topics':d['project_modules'],'project_questions':d['questions_paraphrased'],'summary':d['questions_vs_answers'],
          'questions_vs_retrospective_answers':d['questions_vs_answers'],'rounds':d['rounds'],'access_level':d['scope'],'source_record':d})

    controls=profiles['complete_redacted_comparison_cvs']
    for n,p in enumerate(controls,5):
        added.append({'id':f'OBS{n:02d}','category':'履历对照材料','source_key':p['key'],'title':p['author']+'：研究/AI Infra完整履历脱敏对照','url':p['home'],
          'taxonomy':taxonomy('算法对照','实习','；'.join(o['time'] for o in p['outcomes']),True,p['commit_date'],'研究/Infra方向单列；职业经历自述不计核心应用实习'),
          'reading':reading('完整公开PDF专业模块及本人主页核读；脱敏副本专业正文逐项核对'),
          'outcomes':outcomes_from(p['outcomes'],p['home']),'source_summary':p['analysis'],'projects':p['projects'],
          'redacted_resume_file':p['local_path'],'weaknesses':p['limits'],'source_record':p})
    for p in profiles.get('new_core_authored_project_materials',[]):
        added.append({'id':'DOC11','source_key':'HUOMA_AGENT_DOCUMENT','category':'本人项目文档',
          'title':'huomalxq数据分析Agent后端：本人复盘与未完成项','url':p['source_url'],
          'taxonomy':taxonomy('Agent工程','不适用','项目文档固定版本，非面试事件',False,'2026-06-15T06:03:59Z','文档固定提交日期另列；不能推求职事件年',False),
          'reading':reading(p['reading']),'outcomes':[],'candidate_id':'CV24','stack':p['declared_stack'],
          'summary':p['static_review'],'strengths':p['strengths'],'weaknesses':p['limitations_from_author'],
          'source_record':p,'run_status':p['run_status'],'local_document':p['local_path']})
    tom=next(p for p in documents['candidate_leads'] if p['lead_key']=='BACKEND_AGENT_835271855')
    added.append({'id':'OBS08','category':'候选人对照','source_key':tom['lead_key'],'title':tom['title']+'（混合批次对照）','url':tom['primary_url'],
       'taxonomy':taxonomy('混合','混合',tom['event_date'],False,tom['source_date'],'暑期去年不补绝对年；另篇2026春招明确为校招'),
       'reading':reading(tom['reading']),'outcomes':outcomes_from(tom['outcomes'],tom['primary_url']),
       'summary':tom['recommendation'],'source_record':tom,
       'comparison_documents':[x for x in documents['interview_documents'] if x['author_id']=='835271855']})

    for n,p in enumerate(platform['sources'],10):
        added.append({'id':f'OP{n:02d}','source_key':p['proposed_key'],'category':'B站与知乎','title':p['title'],'platform':p['platform'],
          'author':p['author'],'url':p['url'],'date':p['source_date_text'],
          'taxonomy':taxonomy('后端','不适用','历史专业/项目观点，非招聘事件',False,p['source_date_text'],'发表年不作招聘事件年',False),
          'reading':reading(p['reading']['read_scope_note'],native=True),'verified_video_viewing':False,'platform_native_fulltext_verified':True,
          'identity_evidence':p['identity_evidence'],'opinion':p['观点归纳'],'limits':p['依据与局限'],
          'commercial_bias':p['商业背景'],'recommendation':p['recommended_level'],'outcomes':[],'source_record':p})
    p=bili['sources'][0]
    added.append({'id':'OP12','source_key':p['lead_key'],'category':'B站与知乎','title':p['title'],'platform':'B站公开长图文','author':p['author'],
      'url':p['canonical_url'],'original_url':p['original_url'],'date':p['source_date'],
      'taxonomy':taxonomy('后端','不适用','2024历史简历/项目建议，非招聘事件',False,p['source_date'],'不作近期Agent或SSP门槛',False),
      'reading':reading(p['reading']['method']+'；图片细字未核，不含关联视频',native=True),'outcomes':[],
      'platform_native_fulltext_verified':True,'verified_video_viewing':False,'identity_evidence':p['author_basis'],
      'opinion':'；'.join(v['point'] for v in p['substantive_findings_paraphrased']),
      'limits':'；'.join(p['limitations']),'commercial_bias':p['commercial_background'],
      'recommendation':p['recommendation'],'source_record':p})
    follow=load('目标执行_SSP继续补核.json') if (BASE/'目标执行_SSP继续补核.json').exists() else None
    if follow:
        p=next(x for x in follow['verified_sources'] if x['key']=='AGENT_SSP_3fc0f728')
        added.append({'id':'OBS09','source_key':p['key'],'category':'候选人对照','title':'匿名Agent校招SSP自述：实际年与本人项目关系待核','url':p['url'],
          'taxonomy':taxonomy('Agent工程','校招','秋招，实际年份未知',False,p['source_dates']['published_utc'],'不以届别或发表年补事件年'),
          'reading':reading('公开文字正文全文已读，图片未核；公司逐项、事件年、履历与项目关系未建立'),
          'outcomes':[{'company':'标题提及字节、阿里；其余公司未逐项披露','role':'Agent开发（宽泛自述）','grade':'SSP自述',
            'status':'broad_ssp_claim_pending','evidence_url':p['url'],'basis':p['claim_paraphrased'],'independent_employer_verified':False}],
          'summary':p['decision'],'weaknesses':p['remaining_unknowns'],'identity_boundary':p['identity_discrepancy']['resolution'],
          'source_record':{k:p[k] for k in ['source_dates','taxonomy','claim_paraphrased','project_or_interview_chain','decision','remaining_unknowns']}})

    old_by={r['id']:r for r in all_records}
    for r in added:
        if r['id'] in old_by:assert old_by[r['id']].get('source_key')==r['source_key'],r['id']
    all_records=io.merge(all_records,added);by={r['id']:r for r in all_records}
    # 结果与直接来源逐项对应，不能把同作者另一帖当当前事实的证据。
    for ident in ['CV23','CV24']:
        if ident in by:
            for n,o in zip(by[ident]['chain']['outcome'],by[ident]['outcomes']):
                n['gap']='该段为客户端实习，不计后端/Agent实习证据' if '网易' in o['company'] else '本人公开履历自述，任职未企业独立核验，档位未披露'
    c=by['CV25']
    c['chain']['outcome']=[node(o['evidence_url'],o['company']+' '+o['role']+'；'+o['basis'],'直接点名',o['boundary']) for o in c['outcomes']]
    c['chain']['profile']=[node('https://www.nowcoder.com/discuss/876046266558398464?sourceSSR=users' if 'RAG' in fact else c['url'],fact,'直接点名','职业经历/项目片段，非完整简历') for fact in c['source_record']['profile']['facts']]
    c=by['CV26'];fixed=[]
    for o in c['outcomes']:
        o=deepcopy(o)
        if o['company']=='深信服':o['evidence_url']=by['INT72']['url']
        if o['company']=='九号公司':
            o['evidence_url']=by['INT73']['url'];o['basis']='本人九号公司单篇面经称OC；不提升为正式offer'
            later=deepcopy(o);later.update({'status':'declined_opportunity_self_report','evidence_url':c['url'],'basis':'后续同作者汇总称九号机会已拒绝；不倒写单篇面试时状态'})
            fixed.append(later)
        if o['company']=='小红书/百度':
            for company in ['小红书','百度']:
                v=deepcopy(o);v.update({'company':company,'evidence_url':by['INT75']['url'],'basis':'本人合并面经分别叙述两家一面失败；拒绝原因仍为自我复盘'})
                fixed.append(v)
            continue
        fixed.append(o)
    c['outcomes']=fixed;c['chain']['outcome']=[node(o['evidence_url'],o['company']+'；'+o['basis'],'直接点名',o['boundary']) for o in fixed]
    c['chain']['project']=[node(by['INT73']['url'],fact,'直接点名','企业内部项目，无公开实现源码；指标与职责限作者回忆') for fact in c['source_record']['project_chain']['projects']]
    by['INT77']['outcomes'][0]['company']='阿里云'
    by['INT77']['outcomes'][0]['basis']='本人总结明确最终阿里云基架存储实习offer；其他公司结果不得合并'
    by['CV27']['outcomes'][0]['date']='2025暑期；确切offer日未核'
    by['OBS08']['outcomes'][1].update({'evidence_url':'https://www.nowcoder.com/discuss/869231276035760128?sourceSSR=users','date':'2026年2月至4月校招'})
    for r in all_records:
        if r['category']=='候选人资料':finish_candidate(r)
    for r in load('目标执行_JD原文复核.json')['records']:by[r['id']]['latest_access_recheck']=r
    # 新观点与新问题形成主题证据；主题关系不冒充项目归属。
    cap=load('能力要求四类证据对照.json')
    topic_map={'CAP01':['INT71','INT75'],'CAP02':['INT74'],'CAP04':['INT74'],
      'CAP06':['INT72','INT73','INT77'],'CAP07':['INT72','INT76'],'CAP08':['INT71'],
      'CAP09':['INT74','INT75'],'CAP10':['INT74'],'CAP11':['INT72','INT73','INT76']}
    for row in cap['rows']:
        row['interview_ids']=list(dict.fromkeys(row['interview_ids']+topic_map.get(row['id'],[])))
        if row['id']=='CAP08':
            row['candidate_ids']=list(dict.fromkeys(row['candidate_ids']+['CV25']))
            row['profile_boundary']='新增CV25有本人面经点名RAG；仍缺源码与指标证明，不能当已审实现。'
        if row['id']=='CAP06':row['opinion_ids']=list(dict.fromkeys(row['opinion_ids']+['OP10','OP12']))
        row['support']={group:[{'id':k,'title':by[k]['title'],'url':by[k].get('url',''),'taxonomy':by[k]['taxonomy'],'reading_scope':by[k]['reading']['scope']} for k in row[group+'_ids']] for group in ['jd','interview','candidate','opinion','project']}
    dump('能力要求四类证据对照.json',cap)
    cases['cases']=sorted([r for r in all_records if r['category']=='候选人资料'],key=lambda r:r['id'])
    interviews=sorted([r for r in all_records if r['category']=='面经复盘'],key=lambda r:r['id'])
    projects['projects']=[by[r['id']] for r in projects['projects']]
    def group_stats(rows):
        return {'total':len(rows),**{k:dict(Counter(r['taxonomy'][k] for r in rows)) for k in ['track','recruitment','recent_status']},
          'reading_scope':dict(Counter(r['reading']['scope'] for r in rows)),'fulltext_count':sum(r['reading']['fulltext'] for r in rows)}
    cvstats={**stats['candidate_coverage'],**group_stats(cases['cases'])}
    cvstats.update({'profile_type':dict(Counter(r['profile_type'] for r in cases['cases'])),
       'complete_cv_files_received':sum(r.get('complete_cv_file_received',False) for r in cases['cases']),
       'complete_redacted_cv_files_received':sum(r.get('complete_redacted_cv_file_received',False) for r in cases['cases']),
       'confirmed_personal_interview_source_cases':sum(r.get('has_confirmed_personal_interview_source',False) for r in cases['cases']),
       'denominator_note':'候选人分析卡包含历史和混合方向，不是同等质量的完整简历。完整脱敏专业履历单独计；研究/Infra三份对照不纳此分母。'})
    ivstats={**stats['interview_coverage'],**group_stats(interviews)}
    strict=[r['id'] for r in interviews if r.get('strict_recent_internship')]
    aux=[r['id'] for r in interviews if r.get('publication_recent_event_year_unknown')]
    ivstats.update({'strict_recent_explicit_internship_count':len(strict),'strict_recent_explicit_internship_ids':strict,
      'explicit_internship_all_years_count':sum(r['taxonomy']['recruitment']=='实习' for r in interviews),
      'explicit_internship_event_year_unknown_count':sum(r['taxonomy']['recruitment']=='实习' and r['taxonomy']['recent_status']=='年份未知' for r in interviews),
      'publication_recent_event_year_unknown_count':len(aux),'publication_recent_event_year_unknown_ids':aux,
      'read_source_material_count':len(interviews),'result_status':dict(Counter(r['result_status'] for r in interviews)),
      'material_type':dict(Counter(r['material_type'] for r in interviews)),
      'denominator_note':f'{len(interviews)}份逻辑资料，包含多轮/多公司汇总和同作者跨公司记录，不等于{len(interviews)}位独立候选人、场次或成功者。明确实习、混合、未知分列；近期按事件年。'})
    ops=[r for r in all_records if r['category']=='B站与知乎']
    opstats={**stats['opinion_coverage'],**group_stats(ops),
      'primary_bilibili_or_zhihu_full_content_verified_count':sum(r.get('platform_native_fulltext_verified',False) for r in ops),
      'actual_video_watched_count':0,'zhihu_native_fulltexts_read':2,'bilibili_native_articles_read':1,
      'bilibili_articles_read_excluded':1,'new_native_source_authors':2,
      'identity_boundary':'新增HR资质仅自述；两条鱼皮材料同作者且有商业利益，不能算两个独立专业者；一篇知乎有叙述署名不一致。'}
    stats.update({'candidate_coverage':cvstats,'interview_coverage':ivstats,'opinion_coverage':opstats,
      'current_round_summary':f'本轮实际核读7份核心面经、3篇B站/知乎原平台正文；取得{cvstats["complete_redacted_cv_files_received"]}份核心公开履历脱敏副本及3份研究/Infra对照。另有匿名Agent校招SSP宽泛自述待核，未新增近期实习完整SSP关系或本人源码包。',
      'new_complete_cv_files_this_pass':0,'new_complete_core_redacted_cvs_this_pass':cvstats['complete_redacted_cv_files_received'],
      'remaining_gaps':['核心成功实习者履历与具体本人源码仍缺：内部项目不能开源，公开仓库尚未证明求职使用。',
        '近期Agent正式SSP、本人履历、本人项目和面经的完整关联仍未取得。',
        '已读B站图文1、知乎正文2，但均为历史通用或项目推广；近期Agent工程专业者平台正文仍缺，视频观看0。',
        '19项目均未运行，未复现性能与评测效果。']})
    stats['totals'].update({'logical_evidence_records':len(all_records),'candidate_cases':len(cases['cases']),
      'interview_materials':len(interviews),'platform_opinion_records':len(ops),'redacted_resume_controls':len(controls)})
    stats['source_boundaries']['scope']='现有基础资料与本轮实际核读增量统一分类；研究/Infra履历对照另列。日期、结果、源码归属及正文阅读分别验证。'
    blocked=load('待手动访问链接.json')
    if follow:
        solved=next(x for x in follow['verified_sources'] if x['key']=='OLD_SSP_667800837791461376')
        blocked=[r for r in blocked if '667800837791461376' not in r['url']]
        claim=next(x for x in follow['verified_sources'] if x['key']=='AGENT_SSP_3fc0f728')
        blocked.append({'title':claim['title']+'（正文已读，关系待核）','url':claim['url'],'status':'HTTP200已读公开文字全文；公司逐项、事件年、项目/面经归属未核','to_verify':claim['remaining_unknowns']})
        dump('已解决访问线索.json',{'date':'2026-10-23','records':[solved],'scope':'由未读转为已读后按方向与时间排除核心；不再列入待访问。'})
    extra=[{'title':r.get('title',by.get(r.get('related_id'),{}).get('title','待核原文：'+r['url'])),'url':r['url'],'status':r['status'],'to_verify':r.get('need',r.get('manual_check','正文与来源待核'))} for r in documents['manual_links']+platform['access_observations']]
    blocked=list({io.canonical(r['url']):r for r in blocked+extra}.values())
    stats['totals']['manual_links']=len(blocked);stats['category_counts']=dict(Counter(r['category'] for r in all_records))
    dump('待手动访问链接.json',blocked)
    cases['counts']={'curated_cases':len(cases['cases']),**cvstats}
    cases['goal_execution_scope']='新增近期真实职业履历及脱敏专业副本；研究/Infra对照另列，SSP未新增。'
    norm['records']['candidates']=deepcopy(cases['cases']);norm['records']['interviews']=deepcopy(interviews)
    norm['records']['opinions']=deepcopy(ops)
    norm['statistics'].update({'candidates':cvstats,'interviews':ivstats,'opinions':opstats})
    norm['methodology']['scope']='原110条统一分类加本轮实际核读增量；不包含研究/Infra对照履历作为核心候选人。'
    dump('all_evidence_records.json',all_records);dump('candidate_cases.json',cases);dump('interview_records.json',interviews)
    dump('project_recommendations.json',projects);dump('统一样本分类与候选人关联.json',norm);dump('需求覆盖统计.json',stats)
    dump('履历脱敏副本目录.json',{'date':'2026-10-23','records':controls,'core_files':[r for r in cases['cases'] if r.get('complete_redacted_cv_file_received')],
       'note':'研究/Infra副本不计核心简历分母；完整指原公开版本专业模块完整，不保证投递版本/企业核验。'})
    routes=load('两方向阅读顺序.json')
    routes['backend']['candidate_ids']=list(dict.fromkeys(['CV23','CV22','CV27','CV25']+routes['backend']['candidate_ids']))
    routes['agent']['candidate_ids']=list(dict.fromkeys((["CV24"] if 'CV24' in by else [])+['CV25','CV26']+routes['agent']['candidate_ids']))
    routes['backend']['interview_ids']=list(dict.fromkeys(['INT71','INT77']+routes['backend']['interview_ids']))
    routes['agent']['interview_ids']=list(dict.fromkeys(['INT74','INT72','INT73','INT75','INT76']+routes['agent']['interview_ids']))
    routes['backend']['candidate_boundary']='优先CV23完整公开履历脱敏副本、CV22近期职业片段、CV27明确2025实习；均不补未核源码或SSP。历史对照随后。'
    routes['agent']['candidate_boundary']='CV24为Philips应用工程实习，标明非中国互联网公司；CV25蚂蚁offer与TikTok面经不能串用公司结果；CV26年份未知。均无SSP。'
    routes['read_professional_ids']=list(dict.fromkeys(routes['read_professional_ids']+['OP10','OP11','OP12']))
    dump('两方向阅读顺序.json',routes)
    # 重新导出明细，不沿用前轮硬编码数量。
    io.csv_write(ROOT/'03_简历与候选人案例/候选人证据链对照.csv',['ID','标题','方向','招聘路径','事件时间','近期状态','结果自述','资料类型','录用证据','履历证据','项目贡献证据','本人面经','缺口'],[
      [r['id'],r['title'],r['taxonomy']['track'],r['taxonomy']['recruitment'],r['date'],r['taxonomy']['recent_status'],r.get('outcome',''),r['profile_type'],
       *[' | '.join((n.get('url') or '未建立')+'：'+n['direct_basis'] for n in r['chain'][k]) for k in ['outcome','profile','project','interview']],'；'.join(r['chain_gaps'])] for r in cases['cases']])
    io.csv_write(ROOT/'04_面经与专业观点/面经统一分类.csv',['ID','标题','方向','招聘路径','实际时间','发表日期另列','事件年已证','近期状态','阅读范围','资料类型','结果','来源'],[
      [r['id'],r['title'],r['taxonomy']['track'],r['taxonomy']['recruitment'],r['date'],r['source_date'],r['taxonomy']['year_confirmed'],r['taxonomy']['recent_status'],r['reading']['scope'],r['material_type'],r.get('outcome',''),r['url']] for r in interviews])
    io.csv_write(BASE/'全部资料统一分类.csv',['ID','类别','标题','方向','招聘路径','实际事件时间','来源时间','事件年已证','近期状态','阅读范围','来源'],[
      [r['id'],r['category'],r['title'],r['taxonomy']['track'],r['taxonomy']['recruitment'],r['taxonomy']['experience_date_text'],r['taxonomy']['source_date_text'],r['taxonomy']['year_confirmed'],r['taxonomy']['recent_status'],r['reading']['scope'],r.get('url','')] for r in all_records])
    io.csv_write(BASE/'能力要求四类证据对照.csv',['能力','后端相关性','Agent相关性','JD','面经','履历','专业原文','提问','考察能力','项目模块主题映射','研究归纳薄弱点','缺口'],[
      [x['ability'],x['backend_relevance'],x['agent_relevance'],';'.join(x['jd_ids']),';'.join(x['interview_ids']),';'.join(x['candidate_ids']),';'.join(x['opinion_ids']),x['question'],x['competency'],x['module'],x['common_pitfall'],x['gap']] for x in cap['rows']])
    topic=load('interview_topic_index.json')
    for row in topic['themes']:
        matches=[r for r in interviews if re.search(row['rule'],flatten([r.get('topics',[]),r.get('project_questions',[])]),re.I)]
        row.update({'evidence_ids':[r['id'] for r in matches],'record_count':len(matches),
          'explicit_internship_ids':[r['id'] for r in matches if r['taxonomy']['recruitment']=='实习'],
          'strict_recent_internship_ids':[r['id'] for r in matches if r.get('strict_recent_internship')],
          'year_unknown_internship_ids':[r['id'] for r in matches if r['taxonomy']['recruitment']=='实习' and r['taxonomy']['recent_status']=='年份未知']})
    topic['scope_records']=len(interviews);dump('interview_topic_index.json',topic)
    io.csv_write(BASE/'面经主题索引.csv',['主题','全包资料数','明确实习资料数','严格近期实习资料数','实习事件年未知资料数','全包资料ID','严格近期ID'],[
      [x['theme'],x['record_count'],len(x['explicit_internship_ids']),len(x['strict_recent_internship_ids']),len(x['year_unknown_internship_ids']),';'.join(x['evidence_ids']),';'.join(x['strict_recent_internship_ids'])] for x in topic['themes']])
    progress={'date':'2026-10-23','status':'active','new_record_ids':[r['id'] for r in added],
      'before_totals':load('目标执行前主数据快照.json')['coverage']['totals'],'current_totals':stats['totals'],
      'new_core_candidates':len([r for r in added if r['category']=='候选人资料']),
      'new_interviews':len([r for r in added if r['category']=='面经复盘']),
      'new_platform_fulltexts':3,'new_ssp_direct_evidence':0,'new_agent_ssp_claims_pending':1 if follow else 0,
      'ssp_evidence_boundary':'新增匿名Agent校招SSP宽泛自述已实际读到，但未建立公司、批次和本人材料的直接关联；不计近期实习完整案例。',
      'complete_core_redacted_resumes':cvstats['complete_redacted_cv_files_received'],
      'remaining_gaps':stats['remaining_gaps'],'completion_audit':'六项整体目标尚未完成；不得因归档与页面检查通过标记目标完成。'}
    dump('目标执行统计.json',progress)
    note=f'''# 本轮实际补证进展（目标仍在进行）

统一入口：01_调研报告/需求核对与阅读优先级.html（同名PDF）。

- 核心方向完整专业履历脱敏副本{cvstats['complete_redacted_cv_files_received']}份：CV23 Go后端公开HTML、CV24 Philips Agent应用工程公开PDF；均不是未修改原件或已核投递版。
- CV22近期后端/Agent实习职业片段；CV25蚂蚁暑期智能体应用offer、CV26多篇Agent实习项目深挖、CV27明确2025阿里云存储实习。
- 新入核心面经7份，目前{len(interviews)}份逻辑资料；全文{ivstats['reading_scope'].get('全文',0)}、部分{ivstats['reading_scope'].get('部分',0)}。严格近期{len(strict)}、近期发表但事件年未知{len(aux)}，分开计算。
- 实际阅读B站图文1篇、知乎正文2篇，视频观看0；历史通用建议、项目推广与近期Agent专项要求分开。两篇鱼皮材料同作者，不当独立意见样本。
- 本人问数Agent复盘DOC11有业务链路、SQL校验重试和作者自列未完成项；它是文档，不是实现源码。
- 3份完整研究/AI Infra脱敏PDF单列为OBS05—07，不计核心履历。
- 14份工程JD已拆明确要求、优先项、工作职责；11项能力对照补入新问题；仍不推导统一SSP门槛。

当前总量：{len(all_records)}条逻辑证据、{len(cases['cases'])}候选人分析、{len(interviews)}面经、19项目比较、16源码包、{len(blocked)}条待核原始链接。

本轮新增一条匿名Agent校招SSP宽泛自述待核，但没有新增合格近期实习SSP关联或本人实现源码包。旧受限6678原文已读，为历史视觉算法校招，移出待访问。核心履历—源码关联、近期Agent SSP完整关联、近期Agent专业者平台正文仍缺；所有项目未运行。六项整体目标尚未完成，个人项目设计继续暂缓。
'''
    write(ROOT/'00_目标执行_本轮补证说明.md',note)
    for direction,title in [('backend','后端实习阅读顺序'),('agent','Agent实习阅读顺序')]:
        path=ROOT/'06_项目分析与推荐'/(title+'.md')
        previous=io.read(path) if path.exists() else ''
        lines=['# '+title,'',routes['principle'],'',routes[direction]['candidate_boundary'],'','## 面经与履历','']
        for ident in routes[direction]['candidate_ids']+routes[direction]['interview_ids']:
            r=by[ident];lines += [f'- [{ident} {r["title"]}]({r["url"]})：{r["taxonomy"]["recruitment"]}／{r["taxonomy"]["recent_status"]}。','']
        lines += ['## 模块阅读','']
        for p in load('项目统一比较与阅读优先级.json')['projects']:
            q=p[direction+'_priority']
            if q['level']=='非本方向':continue
            lines += [f'- [{p["id"]} {p["title"]}]({p["source_URL"]})｜{q["level"]}：{q["reason"]}','  阅读模块：'+'；'.join(q['read_modules']),'  证据边界：'+p['evidence_completeness'],'']
        lines+=['个人项目设计暂缓；本页推荐模块阅读，不把框架全量算个人贡献。','']
        write(path,'\n'.join(lines))
    method_path=BASE/'source_methodology.txt';method=io.read(method_path)
    marker='\n\n以下为前轮历史方法说明，不作为当前统计：\n\n'
    if marker in method:method=method.split(marker,1)[1]
    write(method_path,f'目标执行补证版最新口径（2026-10-23）\n{len(all_records)}逻辑证据；{len(cases["cases"])}候选人；{len(interviews)}面经；19项目；16源码ZIP。\n核心完整专业履历脱敏副本{cvstats["complete_redacted_cv_files_received"]}；研究/Infra对照3，未修改原件0。\nB站合格图文全文1、知乎正文2、视频0；身份强弱和商业利益逐条说明。\n严格近期面经{len(strict)}、发表近期事件年未知{len(aux)}；岗位类型/结果/时间不混计。\n最新统计需求覆盖统计.json；补证进展目标执行统计.json；目标仍未完成。'+marker+method)
    file_rows=[]
    for r in cases['cases']:
        if r.get('complete_redacted_cv_file_received'):file_rows.append([r['id'],'核心方向完整脱敏履历',r['redacted_cv_local_file'],r['source_record']['source_url'],'履历自述；源码与投递版本未核'])
    for n,p in enumerate(controls,5):file_rows.append([f'OBS{n:02d}','研究/Infra对照脱敏履历',p['local_path'],p['fixed_pdf_url'],'不计核心应用工程简历'])
    io.csv_write(ROOT/'03_简历与候选人案例/履历文件索引.csv',['资料ID','类型','本地文件','固定原始来源','范围'],file_rows)
    print(json.dumps(progress,ensure_ascii=False,indent=2))

if __name__=='__main__':
    if (BASE/'持续补证统计.json').exists():
        raise SystemExit('已有持续补证增量，请运行整合持续补证.py，避免恢复旧范围。')
    main()
