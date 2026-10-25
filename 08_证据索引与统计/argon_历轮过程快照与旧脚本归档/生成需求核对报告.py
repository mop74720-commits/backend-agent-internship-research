"""从已核数据生成统一阅读入口；不访问网络或执行第三方代码。"""
from collections import Counter
from html import escape
from pathlib import Path
import importlib.util
import json
import re
import shutil

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / '01_调研报告'
spec = importlib.util.spec_from_file_location('requirements_data', BASE / '整合需求纠偏.py')
data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data)
read, write, load, dump, flatten = data.read, data.write, data.load, data.dump, data.flatten
TITLE = '需求核对与阅读优先级'
E = lambda x: escape(str(x), quote=True)

LABELS = {
 'title':'标题','url':'原始来源','date':'事件时间／原文日期（依分类）','source_date':'发表／来源日期',
 'role':'方向与岗位','company':'公司','outcome':'结果自述','outcomes':'逐项结果与档位','grade':'档位',
 'supporting_url':'关联原文','event_date_verification':'招聘事件年份补核','result_scope':'结果适用范围','status':'状态','basis':'依据','evidence_url':'证据','independent_employer_verified':'企业独立验证',
 'reading':'阅读范围','scope':'范围','scope_note':'核读说明','fulltext':'已读定位正文全文','video_watched':'实际观看视频',
 'taxonomy':'统一分类','track':'方向','recruitment':'招聘类型','experience_date_text':'事件时间',
 'date_precision':'时间精度','year_confirmed':'事件年份可证','recent_status':'近期归类','date_basis':'时间依据','source_date_text':'来源日期',
 'stack':'技术栈','projects':'本人项目与经历描述','source_summary':'来源归纳','summary':'内容归纳',
 'original_analysis':'整理者分析','strengths':'值得学习之处','weaknesses':'局限与静态风险',
 'limitations':'局限','limits':'局限','recommendation':'阅读建议','recommended_use':'建议用途',
 'commercial_bias':'商业与选择偏差','commercial_background':'商业背景','access_level':'原访问范围','confidence':'证据边界',
 'profile_type':'履历材料形式','chain':'四段证据关联','chain_gaps':'未建立或未核的关系',
 'outcome_evidence':'录用证据边界','document_type':'资料形式','anonymous_background':'专业背景',
 'topics':'涉及主题','project_questions':'原文提问（归纳）','material_type':'面经形式',
 'sample_group':'统计组','result_status':'结果分类','strict_recent_internship':'严格近期明确实习',
 'publication_recent_event_year_unknown':'近期发表但事件年份未知','candidate_link_ids':'候选人关联ID',
 'repo':'仓库','commit':'固定源码提交','commit_date':'源码提交时间','license':'许可标识',
 'source_archive':'取得源码ZIP','archive_file':'源码包文件','archive_sha256':'源码包SHA-256',
 'inspect_paths':'已定位阅读路径','source_findings':'静态阅读发现','tests_and_evaluation':'测试材料与评测边界',
 'runtime_dependencies':'运行依赖说明','run_status':'运行验证范围','candidate_links':'候选人与项目关系',
 'verified_contributions':'已核个人贡献','relation':'直接关系','offer_causality':'录用因果边界',
 'backend_priority':'后端方向阅读建议','agent_priority':'Agent方向阅读建议','level':'阅读级别','reason':'理由','read_modules':'指定模块',
 'attachment_status':'附件状态','attachment':'附件','source_nature':'来源性质','evidence_completeness':'证据完整度',
 'target_applicability':'目标适用性','author':'作者','platform':'平台','opinion':'具体观点与适用边界',
 'identity_evidence':'作者身份依据','content_validation':'正文核读边界','latest_access_review':'本轮访问复核',
 'secondary_url':'作者原站','source_discrepancy':'来源不一致待核','read_scope':'已读部分',
 'project_reading_modules':'关联模块','adoptable_checks':'可采纳的核查方法','claims_not_to_make':'不能由此推出的结论',
 'source_URL':'依据链接','read_paths':'阅读路径','finding':'观察','id':'资料ID','category':'类别'
}

def link(url, label='原始来源'):
    if not url: return '未建立'
    if not str(url).startswith(('http://','https://','#','../')): return E(url)
    attrs = ' target="_blank" rel="noopener noreferrer"' if str(url).startswith('http') else ''
    return f'<a href="{E(url)}"{attrs}>{E(label)}</a>'

def refs(ids):
    return ' · '.join(link('#'+i, i) for i in ids) if ids else '<span class="muted">未取得对应证据</span>'

def ul(items):
    return '<ul>'+''.join('<li>'+E(i)+'</li>' for i in items)+'</ul>' if items else '<span class="muted">未核</span>'

def pretty(value):
    if value is None: return '<span class="muted">未核／无</span>'
    if isinstance(value, bool): return '是' if value else '否'
    if isinstance(value, dict):
        return '<dl>'+''.join(f'<dt>{E(LABELS.get(k,k))}</dt><dd>{pretty(v)}</dd>' for k,v in value.items())+'</dl>'
    if isinstance(value, list): return '<ul>'+''.join('<li>'+pretty(x)+'</li>' for x in value)+'</ul>' if value else '—'
    return link(value) if str(value).startswith(('http://','https://')) and '\n' not in str(value) else E(value)

CSS = '''
:root{--ink:#1d2e37;--muted:#53666f;--accent:#14696c;--line:#d6e0df;--paper:#fff;--bg:#eef3f1;--warm:#fff6df}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:18px}body{margin:0;color:var(--ink);background:var(--bg);font:16px/1.7 "Microsoft YaHei",sans-serif;overflow-wrap:anywhere}main{max-width:1320px;margin:auto;padding:32px 28px 70px}h1{font-size:36px;line-height:1.3;margin:12px 0 20px}h2{font-size:25px;margin:0 0 18px}h3{font-size:20px;margin:22px 0 12px}p{margin:10px 0 15px}a{color:var(--accent);text-underline-offset:3px}section{padding:28px;margin:24px 0;background:var(--paper);border:1px solid var(--line);border-radius:12px}header{padding:30px;background:#173e42;color:#fff;border-radius:14px}header a{color:#bfece1}nav{display:flex;gap:10px 20px;flex-wrap:wrap;margin-top:20px}.eyebrow{font-size:13px;letter-spacing:2px}.lead{font-size:18px}.muted,small{color:var(--muted)}.note{padding:14px 18px;background:var(--warm);border-left:4px solid #c49b3c;border-radius:4px}.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.metric{padding:16px;border:1px solid var(--line);border-radius:8px;background:#f7faf8}.metric b{display:block;font-size:29px;color:var(--accent);line-height:1.3}.metric span{font-size:14px}.metric small{display:block;font-size:12px;margin-top:6px}.columns{display:grid;grid-template-columns:1fr 1fr;gap:20px}.panel{padding:18px;background:#f6f9f7;border-radius:8px;min-width:0}table{width:100%;border-collapse:collapse;font-size:14px}th,td{border:1px solid var(--line);padding:10px;vertical-align:top;text-align:left}th{background:#eaf2ee;font-weight:600}td p{margin:4px 0 8px}.scroll{overflow-x:auto}caption{text-align:left;font-size:18px;font-weight:bold;margin:0 0 14px}.matrix{table-layout:fixed;font-size:12px;min-width:900px}.matrix th:first-child{width:19%}.matrix th:not(:first-child),.matrix td:not(:first-child){text-align:center}.matrix td{padding:8px 5px}.pill{display:inline-block;border:1px solid #bfd0cd;border-radius:5px;padding:1px 7px;font-size:12px;background:#edf4f0;margin:2px 3px 2px 0}.pill.risk{background:#fff2dd;border-color:#d8b986}.pill.unknown{background:#f1f2f2;color:#59666d}.badge-row{margin:10px 0}details{border:1px solid var(--line);border-radius:7px;margin:10px 0;background:#fff}summary{cursor:pointer;padding:12px 16px;font-weight:600}details>.inside{padding:0 17px 17px}dl{display:grid;grid-template-columns:minmax(90px,155px) minmax(0,1fr);margin:0}dt,dd{margin:0;padding:6px 8px;border-bottom:1px solid #e4ebe7}dt{font-weight:600;color:#45616a}dd dl{grid-template-columns:minmax(70px,130px) minmax(0,1fr)}ul,ol{padding-left:23px;margin:8px 0}li{margin:5px 0}.paths{font:12px/1.7 Consolas,monospace;background:#f2f5f3;padding:12px;overflow-wrap:anywhere}.route-item{border-top:1px solid var(--line);padding:10px 0}.filters{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:9px}input,select,button{font:inherit;max-width:100%;padding:9px;border:1px solid #9db8b2;border-radius:5px;background:white;color:var(--ink)}input{width:100%;margin:0 0 12px}button{cursor:pointer}button:hover{background:#e7f2ed}.controls{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}.record h3{margin:0}.record{scroll-margin-top:20px}.record[hidden]{display:none}mark{background:#fff0ac}.count{font-size:14px;color:var(--muted)}.chain{table-layout:fixed}.chain th:first-child{width:15%}.chain td{font-size:12px}.chain small{display:block}.print-only{display:none}.footer{font-size:13px;color:var(--muted)}.cap-table{min-width:1050px}.cap-table td{font-size:13px}.manual-card{margin:14px 0;padding:16px;background:#fff;border:1px solid var(--line);border-radius:8px}
@media(max-width:760px){main{padding:14px 12px 40px}header,section{padding:18px}h1{font-size:28px}h2{font-size:22px}.metrics{grid-template-columns:1fr 1fr}.columns{grid-template-columns:1fr}.filters{grid-template-columns:1fr 1fr}dl,dd dl{grid-template-columns:1fr}dt{background:#f2f6f3}dd{padding-bottom:12px}.chain{min-width:1000px}.coverage-table{min-width:650px}}
@page{size:A4;margin:15mm 12mm 16mm}
@media print{body{background:#fff;font-size:9px;line-height:1.45}main{padding:0;max-width:none}header{padding:16px;background:#fff;color:var(--ink);border:2px solid #245f61}header a{color:#245f61}h1{font-size:25px}h2{font-size:18px;break-after:avoid}h3{font-size:13px;break-after:avoid}section{padding:0;border:0;margin:22px 0}nav,.screen-only,.catalog,.project-details{display:none!important}.print-only{display:block}.metrics{grid-template-columns:repeat(4,1fr);gap:5px}.metric{padding:8px;break-inside:avoid}.metric b{font-size:21px}.metric span{font-size:9px}.metric small{font-size:8px}.columns{display:block}.panel{padding:9px;margin:12px 0;break-inside:avoid}.note{padding:8px 10px}table{font-size:8px}.scroll{overflow:visible}.matrix{min-width:0;width:100%;font-size:7.5px}.matrix th:first-child{width:20%}.matrix th,.matrix td{padding:5px 2px}.matrix .pill{border:0;padding:0;background:transparent;font-size:7.5px}.chain{min-width:0;width:100%}.chain td{font-size:7.5px}.chain th:first-child{width:15%}.chain td,.chain th{padding:5px}.chain small{font-size:7px}.cap-table{min-width:0;table-layout:fixed}.cap-table td{font-size:7.3px;padding:5px}.cap-table th{font-size:8px;padding:5px}tr{break-inside:avoid}thead{display:table-header-group}a{color:#235f62;text-decoration:none}details{break-inside:avoid}p{margin:6px 0}li{margin:3px 0}.route-item{padding:7px 0}.pill{font-size:8px;padding:0 4px}.footer{font-size:8px}}
'''

JS = '''
const cards=[...document.querySelectorAll('.record')];
const query=document.querySelector('#query');const selectors=[...document.querySelectorAll('[data-filter]')];
function filter(){const q=(query?.value||'').trim().toLocaleLowerCase();let n=0;for(const c of cards){const match=(!q||c.dataset.search.includes(q))&&selectors.every(s=>!s.value||c.dataset[s.dataset.filter]===s.value);c.hidden=!match;if(match)n++}const nEl=document.querySelector('#shown');if(nEl)nEl.textContent=n;}
query?.addEventListener('input',filter);selectors.forEach(s=>s.addEventListener('change',filter));
document.querySelector('#reset')?.addEventListener('click',()=>{query.value='';selectors.forEach(s=>s.value='');filter()});
document.querySelector('#open-visible')?.addEventListener('click',()=>cards.filter(c=>!c.hidden).forEach(c=>c.querySelector('details').open=true));
document.querySelector('#close-visible')?.addEventListener('click',()=>cards.forEach(c=>c.querySelector('details').open=false));
function jump(){if(!location.hash)return;let id;try{id=decodeURIComponent(location.hash.slice(1))}catch{return}const el=document.getElementById(id);if(!el)return;if(el.classList.contains('record')){query.value='';selectors.forEach(s=>s.value='');filter();el.querySelector('details').open=true}if(el.tagName==='DETAILS')el.open=true;for(let p=el.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;setTimeout(()=>el.scrollIntoView({block:'start'}),50)}
window.addEventListener('hashchange',jump);filter();jump();
document.querySelector('#manual-search')?.addEventListener('input',e=>{let n=0;for(const c of document.querySelectorAll('.manual-card')){c.hidden=!c.textContent.toLowerCase().includes(e.target.value.toLowerCase());if(!c.hidden)n++}document.querySelector('#manual-shown').textContent=n});
'''

def shell(title, body):
    return '<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+E(title)+'</title><style>'+CSS+'</style></head><body><main>'+body+'</main><script>'+JS+'</script></body></html>'

def generate():
    records=load('all_evidence_records.json'); by={r['id']:r for r in records}
    stats=load('需求覆盖统计.json'); totals=stats['totals']; iv=stats['interview_coverage']; cv=stats['candidate_coverage']; op=stats['opinion_coverage']
    comparisons=load('项目统一比较与阅读优先级.json'); projects=comparisons['projects']
    dimension_count=sum(len(p['backend_dimensions'])+len(p['agent_dimensions']) for p in projects)
    comparison_csv='项目统一比较.csv' if (ROOT/'06_项目分析与推荐/项目统一比较.csv').exists() else '19项目统一比较.csv'
    archive_note=f"原固定ZIP {totals.get('original_fixed_source_zips',totals['source_archives'])}；去联系字段文本归档 {totals.get('redacted_text_source_zips',0)}；仅链接 {totals['fixed_link_only']}"
    routes=load('两方向阅读顺序.json'); abilities=load('能力要求四类证据对照.json')['rows']
    blocked=load('待手动访问链接.json'); gap=load('近期实习缺口核查结论.json')
    assert len(records)==totals['logical_evidence_records'] and len(blocked)==totals['manual_links']
    old=REPORT/'历史资料目录_第四轮快照.html'
    if not old.exists(): shutil.copyfile(REPORT/'index.html',old)
    header=f'''<header><div class="eyebrow">大厂后端 · AGENT 工程 · 实习优先 / 2026-10-24</div><h1>{TITLE}</h1><p class="lead">从岗位要求、候选人履历、面试追问与专业原文，比较值得学习的能力和模块。</p><p>近期窗口：{stats['recent_window']['start']} 至 {stats['recent_window']['end']}，按实际事件时间确认。发现轮次和 star 不参与推荐排序。</p><nav><a href="#coverage">实际覆盖</a><a href="#routes">两方向阅读</a><a href="#abilities">能力对照</a><a href="#chains">候选人关联</a><a href="#projects">{len(projects)}项目比较</a><a href="#opinions">专业观点</a><a href="#catalog">搜索全部资料</a><a href="待手动访问链接.html">{len(blocked)}条待手动访问</a></nav></header>'''
    metrics=[
     (totals['candidate_cases'],'候选人分析（含历史与对照）',f"核心完整脱敏副本 {cv.get('complete_redacted_cv_files_received',0)}；分析卡不等于简历文件"),
     (cv['actual_resume_fragments_read'],'实际读图的简历片段','另有既有HTML/TeX履历；完整脱敏副本在下方单列'),
     (iv['strict_recent_explicit_internship_count'],'事件时间明确的近期实习面经','优先阅读组；资料份数不等于成功者人数'),
     (iv['explicit_internship_all_years_count'],'明确实习面经（所有年份）',f"其中事件年未知 {iv['explicit_internship_event_year_unknown_count']}；混合 {iv['mixed_recruitment_count']} 另列"),
     (totals['interview_materials'],'已读面经逻辑资料',f"全文 {iv['reading_scope']['全文']}；部分 {iv['reading_scope']['部分']}；不等于独立面试场数"),
     (totals['projects'],'统一比较的项目',archive_note+'；均未运行'),
     (op['primary_bilibili_or_zhihu_full_content_verified_count'],'B站／知乎本体完整内容已读',f"B站图文 {op.get('bilibili_native_articles_read',0)}；知乎正文 {op.get('zhihu_native_fulltexts_read',0)}；视频 {op['actual_video_watched_count']}"),
     (totals['jd_leads'],'招聘JD资料',f"工程要求比较分母 {totals['engineering_jd_fulltext']}；其余对照/摘要单列")]
    if stats.get('project_text_selection_archive_count'):archive_note+='；其中1份为14文件定点选读包'
    coverage='<section id="coverage"><h2>原需求与当前覆盖</h2><div class="metrics">'+''.join(f'<div class="metric"><b>{n}</b><span>{E(t)}</span><small>{E(s)}</small></div>' for n,t,s in metrics)+'</div>'
    coverage+=f'''<p class="note">还有 {iv['publication_recent_event_year_unknown_count']} 份明确在近两年发表、但事件年份未确认的实习面经，仅作辅助组。历史校招、实习转正、算法对照、未知招聘批次分别标注。核心完整CV原件 {cv['complete_cv_files_received']} 份，核心完整脱敏副本 {cv.get('complete_redacted_cv_files_received',0)} 份；研究／AI Infra履历脱敏对照 {totals.get('redacted_resume_controls',0)} 份另列。已核近期Agent正式SSP完整关联 {stats['recent_agent_ssp_complete_chain_confirmed']}；缺失关系不能由同账号仓库补齐。</p>'''
    if iv.get('strict_recent_control_internship_count'):
        coverage+='<p class="note">严格近期实习总组 '+str(iv['strict_recent_explicit_internship_count'])+' 份，其中后端／Agent／混合工程 '+str(iv['strict_recent_engineering_internship_count'])+' 份，AI Infra对照 '+str(iv['strict_recent_control_internship_count'])+' 份；对照题目不作为Agent应用统一要求。</p>'
    requirement_rows=[
     ('大厂后端／Agent实习，特别SSP','严格近期实习先读；历史SSP为专项进阶对照','SSP自述仍需核公司、批次与本人材料；不视企业认证'),
     ('已获岗者简历、技术栈、本人项目',f"{cv['total']}份四段关联表；完整专业履历脱敏副本{cv.get('complete_redacted_cv_files_received',0)}份，片段与历史履历另列",stats.get('qualifying_chain_scope',f"未修改完整原件{cv['complete_cv_files_received']}；本人源码关联按逐条缺口")),
     ('大量面经与要求分析',f"{iv['total']}份按方向／批次／事件时间／阅读范围整理；11项能力映射",'多场汇总不拆成独立人；提问与事后答案分开'),
     ('B站、知乎专业者评价',f"{totals['platform_opinion_records']}条平台资料逐条标范围；本体正文/视频已读{op['primary_bilibili_or_zhihu_full_content_verified_count']}；平台外原文另列",f"实际观看视频{op['actual_video_watched_count']}；作者身份和商业背景分别核对"),
     ('打包并比较项目优缺点',f"{totals['projects']}个项目全部比较，{dimension_count}项状态；"+archive_note,'全部未运行；团队框架不算个人实现，文本派生归档不冒充完整原ZIP')]
    coverage+='<div class="scroll"><table class="coverage-table"><thead><tr><th>原要求</th><th>本轮改进</th><th>仍需注意</th></tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+E(c)+'</td>' for c in row)+'</tr>' for row in requirement_rows)+'</tbody></table></div><p>SSP、SP、未分档offer、意向／OC、进入下一轮、失败与未知逐条保存。录用均来自公开自述；已合并PR只核贡献事实，不证明录用因果。个人项目设计继续暂缓。</p></section>'

    def route_block(key,heading):
        r=routes[key]; out=f'<div class="panel"><h3>{heading}</h3><p>{E(r["candidate_boundary"])}</p><b>先读面经</b>'
        for i in r['interview_ids']:
            x=by[i];t=x['taxonomy'];out+=f'<div class="route-item">{refs([i])} {E(x["title"])}<br><small>{E(t["recruitment"])} · {E(t["recent_status"])} · {E(t["experience_date_text"])}</small><br>{E(x.get("summary",x.get("recommended_use","")))}</div>'
        out+='<p><b>候选人对照：</b>'+refs(r['candidate_ids'])+'</p><b>项目按模块选读</b>'
        for label,items in r['project_routes'].items():
            if isinstance(items,list): out+='<p>'+E(label.replace('_',' · '))+'：'+refs(items)+'</p>'
            elif isinstance(items,dict):out+='<p>'+E(label.replace('_',' · '))+'：'+'；'.join(E(k)+' '+refs(v) for k,v in items.items())+'</p>'
            else:out+='<p>'+E(items)+'</p>'
        return out+'</div>'
    route='<section id="routes"><h2>两套阅读顺序：按目标选模块</h2><p>'+E(routes['principle'])+'</p><p>精读表示该方向的指定模块值得仔细读；不是整库复刻建议，也不是项目成熟度或SSP保证。证据完整度与目标适用性分别呈现，不合成总分。</p><div class="columns">'+route_block('backend','后端实习')+route_block('agent','Agent实习')+'</div></section>'

    cap='<section id="abilities"><h2>面试问题如何对应能力与项目模块</h2><div class="columns"><div class="panel"><b>后端技术栈的阅读主线</b><p>先按目标岗位选Java／Go／C++语言路线，再核并发、网络、SQL与索引，以及缓存、消息、幂等和失败恢复。这里的广度落实为可解释的实现和取舍，不以列出组件数量衡量。</p>'+refs(['JD01','JD02','JD06','INT10','INT22','CV01'])+'</div><div class="panel"><b>Agent技术栈的阅读主线</b><p>在服务端基础上，重点核工具输入与返回、状态和上下文、RAG检索、异常恢复、权限、评测及成本。具体框架名按岗位和模块选读，实际任务结果与失败轨迹更值得审查。</p>'+refs(['JD08','JD11','INT01','INT42','INT47','OP04','OP09'])+'</div></div><p>以上为本包证据的阅读归纳，岗位语言与职责仍按每份JD。JD含官方招聘及公开员工招募描述，当前HC未核。提问为原文记录的归纳；“常见失误”为本次研究归纳，不是拒绝原因统计。项目列为主题映射，除候选人关联中直接证实外，不表示受访者做过这些参考项目。INT70混有事后解答，INT58／59含整理或协作笔记，不能全部当本人现场追问。缺少的证据类留空。</p><div class="scroll"><table class="cap-table"><thead><tr><th>能力与提问</th><th>JD／面经证据</th><th>履历／专业观点</th><th>对应模块与阅读</th><th>失误与缺口</th></tr></thead><tbody>'
    for a in abilities:
        cap+=f'<tr id="{a["id"]}"><td><b>{E(a["ability"])}</b><p>{E(a["question"])}</p>{E(a["competency"])}<p><small>后端：{E(a["backend_relevance"])}；Agent：{E(a["agent_relevance"])}</small></p></td><td>JD：{refs(a["jd_ids"])}<p>面经：{refs(a["interview_ids"])}</p></td><td>履历：{refs(a["candidate_ids"])}<p>观点：{refs(a["opinion_ids"])}</p>{E(a["profile_boundary"])}</td><td>{E(a["module"])}<p>{refs(a["project_ids"])}</p></td><td>{E(a["common_pitfall"])}<p>{E(a["gap"])}</p></td></tr>'
    cap+='</tbody></table></div></section>'

    chains=f'<section id="chains"><h2>{totals["candidate_cases"]}份候选人资料：四段关系逐项核对</h2><p>本表含原有历史与算法对照，按方向与批次阅读。“直接点名”可能只有文字项目描述，仍须看源码缺口；“同账号”不等于简历使用证明。空链不补齐。详细范围、逐公司结果和来源见对应资料卡与CSV。</p><div class="scroll"><table class="chain"><thead><tr><th>候选人／时间</th><th>录用自述</th><th>履历材料</th><th>项目／贡献</th><th>本人面经</th></tr></thead><tbody>'
    for c in sorted([r for r in records if r['category']=='候选人资料'],key=lambda r:r['id']):
        t=c['taxonomy'];cells=[f'{refs([c["id"]])}<b> {E(c["title"])}</b><small>{E(t["track"])} · {E(t["recruitment"])} · {E(t["recent_status"])}</small><small>{E(t["experience_date_text"])}</small>']
        for stage in ['outcome','profile','project','interview']:
            parts=[]
            grouped={}
            for node in c['chain'][stage]:
                key=(node['relation'],node['direct_basis'],node.get('gap',''))
                grouped.setdefault(key,[]).append(node)
            for (relation,basis,gaptext),nodes in grouped.items():
                node=nodes[0]
                basis=node['direct_basis'];gaptext=node.get('gap','')
                evidence=' · '.join(link(n['url'],'证据'+str(i+1)) for i,n in enumerate(nodes) if n.get('url')) or '—'
                parts.append(f'<b>{E(relation)}</b> '+evidence+f'<p>{E(basis[:150])}{"…" if len(basis)>150 else ""}</p><small>{E(gaptext[:130])}{"…" if len(gaptext)>130 else ""}</small>')
            cells.append(''.join(parts))
        chains+='<tr>'+''.join('<td>'+c+'</td>' for c in cells)+'</tr>'
    chains+='</tbody></table></div><p class="note">ShenYu：已确认erdengk的PR3848、3672在2022年合并；只静态读了两项测试改动，其余贡献未审。2026固定版本的整库能力不能回填为2023 SSP时的个人实现。</p></section>'

    def badge(status):
        cls='risk' if status=='静态风险' else 'unknown' if status in ['未核','不适用'] else ''
        return f'<span class="pill {cls}">{E(status)}</span>'
    projectsec=f'<section id="projects"><h2>{len(projects)}个项目的统一横向比较</h2><p>源码可见＝指定实现能定位；文档宣称＝未独立验证运行；静态风险＝读代码发现需验证的边界；未核＝本次证据不足；不适用＝不是该方向证明。均未运行。<a href="../06_项目分析与推荐/{comparison_csv}">下载{dimension_count}项比较CSV</a>。</p>'
    for direction,heading in [('backend','后端：业务与工程基础'),('agent','Agent：任务执行与可靠性')]:
        dims=comparisons['dimensions'][direction]
        projectsec+='<h3>'+heading+'</h3><div class="scroll"><table class="matrix"><thead><tr><th>项目／方向建议</th>'+''.join('<th>'+E(d)+'</th>' for d in dims)+'</tr></thead><tbody>'
        for p in projects:
            projectsec+='<tr><td>'+link('#project-'+p['id'],p['id']+' '+p['title'])+'<br>'+E(p[direction+'_priority']['level'])+'</td>'+''.join('<td>'+badge(p[direction+'_dimensions'][d]['status'])+'</td>' for d in dims)+'</tr>'
        projectsec+='</tbody></table></div>'
    projectsec+='<div class="project-details screen-only"><h3>每项推荐的理由、局限与指定模块</h3>'
    for p in projects:
        projectsec+=f'<details id="project-{p["id"]}" class="project-detail"><summary>{E(p["id"]+" · "+p["title"])} — 后端{E(p["backend_priority"]["level"])}／Agent{E(p["agent_priority"]["level"])}</summary><div class="inside"><p>{link(p["source_URL"],p["repo"])} · {E(" / ".join(p["source_nature"]))}</p><p><b>证据完整度：</b>{E(p["evidence_completeness"])}</p><p><b>目标适用性：</b>{E(p["target_applicability"])}</p><p><b>后端：</b>{E(p["backend_priority"]["reason"])}</p><p><b>Agent：</b>{E(p["agent_priority"]["reason"])}</p>'
        for direction in ['backend','agent']:
            paths=p[direction+'_priority']['read_modules']
            if paths: projectsec+='<b>'+('后端' if direction=='backend' else 'Agent')+'指定模块</b><div class="paths">'+'<br>'.join(link(x,'历史PR／测试源码') if x.startswith('http') else E(x) for x in paths)+'</div>'
        projectsec+='<p><b>来源性质边界：</b>'+E(p.get('source_nature_boundary','依上述关系与静态阅读范围限定'))+'</p>'
        projectsec+='<div class="columns"><div><b>值得学习</b>'+ul(p['strengths'])+'</div><div><b>局限</b>'+ul(p['limitations'])+'</div></div><p><b>商业背景：</b>'+E(flatten(p['commercial_background']))+'</p>'
        att=p['attachment'];projectsec+='<p><b>附件：</b>'+E(att['status'])
        if att.get('archive_file'):projectsec+=' · '+link('../05_项目源码归档/'+att['archive_file'],'固定ZIP')
        projectsec+='。'+E(p['run_status'])+'</p><h4>候选人关系及时间边界</h4>'+pretty(p['candidate_relationships'])
        projectsec+='<h4>逐维依据</h4><table><thead><tr><th>方向／维度</th><th>状态与发现</th><th>来源、路径与阅读范围</th></tr></thead><tbody>'
        for direction in ['backend','agent']:
            for dim,v in p[direction+'_dimensions'].items():
                projectsec+='<tr><td>'+E(('后端' if direction=='backend' else 'Agent')+' / '+dim)+'</td><td>'+badge(v['status'])+'<p>'+E(v['finding'])+'</p></td><td>'+link(v['source_URL'],'定位依据')+'<div class="paths">'+'<br>'.join(E(x) for x in v['read_paths'])+'</div><small>'+E(v['read_scope'])+'</small></td></tr>'
        projectsec+='</tbody></table><p>'+refs([p['id']])+' 查看原分析卡</p></div></details>'
    projectsec+='</div><div class="print-only"><h3>逐项目阅读依据与局限</h3><table><thead><tr><th>项目／原始依据</th><th>两方向建议与指定模块</th><th>证据及局限</th></tr></thead><tbody>'
    for p in projects:
        modulelinks=[]
        for direction in ['backend','agent']:
            q=p[direction+'_priority'];items=q['read_modules'][:2]
            if items:
                labels=[x if len(x)<65 else '…/'+x.rsplit('/',1)[-1] for x in items]
                modulelinks.append(('后端' if direction=='backend' else 'Agent')+'：'+'；'.join(labels))
        projectsec+='<tr><td>'+link(p['source_URL'],p['id']+' '+p['repo'])+'</td><td><b>后端'+E(p['backend_priority']['level'])+'</b>：'+E(p['backend_priority']['reason'])+'<p><b>Agent'+E(p['agent_priority']['level'])+'</b>：'+E(p['agent_priority']['reason'])+'</p><small>'+E('；'.join(modulelinks))+'</small></td><td>'+E(p['evidence_completeness'])+'<p>'+E('；'.join(p['limitations'][:2]))+'</p></td></tr>'
    projectsec+=f'</tbody></table><p>HTML的{len(projects)}个展开卡包含完整逐维发现、依据、路径及商业背景。{dimension_count}项完整细节另见同包CSV；全部项目未运行。源码文本派生归档删除联系字段，并省略未审二进制图像，清单见来源记录。</p></div></section>'

    opinions=f'<section id="opinions"><h2>专业观点：实际读到了什么</h2><p>平台资料{totals["platform_opinion_records"]}条；平台本体完整内容实际已读{op["primary_bilibili_or_zhihu_full_content_verified_count"]}条，实际观看视频{op["actual_video_watched_count"]}条。官网替代全文{op["author_original_fulltext_substitute_count"]}篇、章节选读{op["author_original_selected_sections_substitute_count"]}份，另有平台外官方全文{totals["additional_primary_texts"]}篇，分别计数。实际正文可读不等于作者专业资格已证，署名及商业背景见逐条说明。</p><div class="scroll"><table><thead><tr><th>资料</th><th>实际阅读范围／观点</th><th>依据与商业背景</th></tr></thead><tbody>'
    for x in sorted([r for r in records if r['id'].startswith('OP')],key=lambda r:r['id']):
        opinions+='<tr><td>'+refs([x['id']])+' '+E(x['title'])+'<p>'+E(x['platform'])+'</p></td><td>'+E(x['reading']['scope_note'])+'<p>'+E(x.get('opinion',''))+'</p></td><td>'+link(x.get('secondary_url') or x['url'],'原文／原始线索')+'<p>'+E(x.get('commercial_bias','未核'))+'</p>'+E(x.get('limits',x.get('limitations','')))+'</td></tr>'
    opinions+='</tbody></table></div><p class="note">OP03原卡BV1EE411T7HF，与作者README当前所链接BV1XE411P7s8不一致，保留两个原始入口待核，未将它们视为同一个已观看视频。</p></section>'

    remaining=f'<section id="gaps"><h2>补搜结果与仍未满足的部分</h2><p>'+E(stats.get('current_round_summary','前轮已完成两条检索路径，未补到合格完整CV或近期Agent SSP关联；该结论只限当轮。本轮继续按实际证据更新。'))+'</p>'+ul(stats['remaining_gaps'])+f'<p>{link("../01_调研报告/待手动访问链接.html",str(len(blocked))+"条原始待访问链接")}：状态按HTTP403／412／521、标题空壳、证书失败或许可证未知等分别记录，不把所有失败统称限流。可手动核对作者、招聘批次、实际结果、本人项目与原始提问。</p><p>{link("../08_证据索引与统计/近期实习缺口核查结论.json","前轮检索与排除理由")} · {link("../08_证据索引与统计/专业观点补核与缺口检索.json","前轮专业观点核读记录")}</p></section>'

    if (BASE/'Agent_SSP定向补核_根核读.json').exists():
        supplement='<div class="ssp-verification"><h3>Agent SSP：本轮岗位、批次与最终结果补核</h3><p>新命中的字节财经AI应用入职帖，SSP来自其他评论者昵称；炒肉多原帖为加面后的SSP预期，未见后续定档；舟杨波后续正文10.20更新蚂蚁未通过、快手等待结果。均不新增Agent SSP成功者。</p><p>现有16份SSP候选人已审查本地主表依据，其中CV14与OBS09重新取得原文；没有把这两份原文复读说成16份全部重新访问。普通GET能读的同站替代入口与空壳分别记录，本轮无新增必须手动访问链接。</p><p>'+link('../08_证据索引与统计/Agent_SSP定向补核_根核读.json','原帖与根核读范围')+' · '+link('../08_证据索引与统计/Agent_SSP定向补核_本轮.json','作者后续及排除理由')+' · '+link('../08_证据索引与统计/Agent_SSP定向检索_岗位与批次.json','两路径检索范围')+' · '+link('../08_证据索引与统计/SSP已有样本_来源范围复核.json','既有SSP样本复核')+'</p><p>本轮有限路径已结束；仍缺具体Agent工程岗位、公司、招聘时间/批次和最终SSP的明确本人自述。不据此宣称全网没有，完整CV、本人项目与面经关系继续分项呈现。</p></div>'
        remaining=remaining.replace('</section>',supplement+'</section>')

    exports=[('../03_简历与候选人案例/候选人证据链对照.csv',f'{totals["candidate_cases"]}份候选人关联CSV'),('../04_面经与专业观点/面经统一分类.csv',f'{totals["interview_materials"]}份面经分类CSV'),('../06_项目分析与推荐/'+comparison_csv,f'{dimension_count}项项目比较CSV'),('../08_证据索引与统计/能力要求四类证据对照.csv','11项能力对照CSV'),('../08_证据索引与统计/全部资料统一分类.csv',f'{len(records)}条统一分类CSV'),('../06_项目分析与推荐/后端实习阅读顺序.md','后端阅读模块'),('../06_项目分析与推荐/Agent实习阅读顺序.md','Agent阅读模块'),('../08_证据索引与统计/需求覆盖统计.json','统计原始数据'),('../01_调研报告/'+TITLE+'.pdf','本报告PDF'),('../01_调研报告/历史资料目录_第四轮快照.html','第四轮完整目录快照')]
    downloads='<section id="downloads"><h2>文件、统计口径与历史报告</h2><p>'+ ' · '.join(link(u,t) for u,t in exports)+f'</p><p>统计来源为统一主记录与《需求覆盖统计.json》，页面由脚本生成。资料数量为逻辑记录，跨类别重复原文不代表独立样本。主题频次只描述本包覆盖，不是招聘市场概率。{len(projects)}项目均未运行；源码压缩包完整性通过不代表运行效果通过。</p><p>前四轮报告和PDF保留历史快照。历史目录中原个人项目设计仍仅作旧资料保留，当前继续暂缓。</p></section>'

    filters=[('category','类别'),('track','方向'),('recruitment','招聘类型'),('recent','时间分组'),('reading','阅读范围')]
    catalog=f'<section id="catalog" class="catalog"><h2>搜索全部 {len(records)} 条资料</h2><p>用于查证，不代表按显示顺序推荐。可组合筛选；从其他章节点资料ID会清除筛选并打开该卡。</p><label for="query">关键词、技术栈、原始问题或ID</label><input id="query" type="search" placeholder="如：INT42、幂等、工具、SSP"><div class="filters">'
    for field,label in filters:
        vals=sorted({r['category'] if field=='category' else r['reading']['scope'] if field=='reading' else r['taxonomy'][{'recent':'recent_status'}.get(field,field)] for r in records})
        catalog+=f'<label>{label}<select data-filter="{field}"><option value="">全部</option>'+''.join(f'<option value="{E(v)}">{E(v)}</option>' for v in vals)+'</select></label>'
    catalog+=f'</div><div class="controls"><button id="reset">重置筛选</button><button id="open-visible">展开当前结果</button><button id="close-visible">收起资料卡</button><span class="count">显示 <b id="shown">{len(records)}</b> / {len(records)}</span></div>'
    for r in records:
        t=r['taxonomy'];rd=r['reading'];search=flatten({k:v for k,v in r.items() if k!='comparison'}).lower()
        catalog+=f'<article id="{r["id"]}" class="record" data-category="{E(r["category"])}" data-track="{E(t["track"])}" data-recruitment="{E(t["recruitment"])}" data-recent="{E(t["recent_status"])}" data-reading="{E(rd["scope"])}" data-search="{E(search)}"><details><summary>{E(r["id"]+" · "+r["title"])}</summary><div class="inside"><div class="badge-row">'+''.join('<span class="pill">'+E(s)+'</span>' for s in [r['category'],t['track'],t['recruitment'],t['recent_status'],'阅读：'+rd['scope']])+'</div>'
        catalog+='<p><b>事件时间：</b>'+E(t['experience_date_text'])+'<br><b>来源时间：</b>'+E(t['source_date_text'])+'<br><small>'+E(t['date_basis'])+'</small></p><p>'+link(r.get('url'), '原始来源')+' · '+E(rd['scope_note'])+'</p>'
        if r['id'].startswith('PRO'):catalog+='<p>'+link('#project-'+r['id'],f'展开两方向推荐与{dimension_count}项比较中的本项目')+'</p>'
        excluded={'id','title','category','url','taxonomy','reading','comparison','date','source_date'}
        catalog+=pretty({k:v for k,v in r.items() if k not in excluded})+'</div></details></article>'
    catalog+='</section>'
    technical=''
    if (BASE/'技术要求_明确要求与加分项.json').exists():
        tiers=load('技术要求_明确要求与加分项.json')
        technical='<section id="requirements"><h2>技术要求分层：明确要求、优先项与实际追问</h2><p>以下归纳来自'+str(tiers['engineering_jd_count'])+'份工程JD。了解、熟悉、掌握及语言择一按各岗位原文区分；工作职责不自动等于申请者必须已独立实现的所有模块。</p><div class="columns">'
        for key,title in [('backend_conclusions','后端实习'),('agent_conclusions','Agent工程实习')]:
            technical+='<div class="panel"><h3>'+title+'</h3>'
            for row in tiers[key]:
                ids=list(dict.fromkeys(i for k,v in row.items() if k.endswith('_ids') for i in v))
                technical+='<div class="route-item"><b>'+E(row['item'])+'</b><p>'+E(row['finding'])+'</p>'+refs(ids)+'</div>'
            technical+='</div>'
        technical+='</div><p class="note"><b>SSP结论边界：</b>'+E(tiers['ssp_conclusion']['missing'])+'</p><details class="screen-only"><summary>逐岗位：明确要求、优先项、工作职责</summary><div class="inside"><table><thead><tr><th>岗位与来源</th><th>明确要求</th><th>优先／加分</th><th>工作职责及局限</th></tr></thead><tbody>'
        for row in tiers['job_requirement_rows']:
            technical+='<tr><td>'+refs([row['id']])+' '+E(row['role'])+'<p>'+link(row['source_URL'],'原文')+'</p></td><td>'+ul(row['explicit_requirements'])+'</td><td>'+ul(row['explicit_preferences'])+'</td><td>'+E(row['duties_not_entry_gates'])+'<p>'+E(row['limitations'])+'</p></td></tr>'
        technical+='</tbody></table></div></details><p>'+link('../06_项目分析与推荐/技术要求_明确要求与加分项.md','完整分层表与SSP个案适用边界')+'</p></section>'
    resume_controls=''
    if (BASE/'履历脱敏副本目录.json').exists():
        controls=load('履历脱敏副本目录.json')['records']
        resume_controls=f'<section id="resume-controls"><h2>{len(controls)}份公开履历脱敏副本：研究／AI Infra对照</h2><p>保留原文件所有专业模块，删除联系区、链接注释和可识别元数据；这是整理者脱敏副本。它们是研究／Infra方向，不填补核心应用工程完整简历缺口；当前版本项目也不倒推为求职当时作品。</p><div class="scroll"><table><thead><tr><th>履历与副本</th><th>实习及时间依据</th><th>本人项目关系</th><th>局限与脱敏范围</th></tr></thead><tbody>'
        for x in controls:
            resume_controls+='<tr><td>'+E(x['author'])+'<p>'+link('../'+x['local_path'],'打开完整专业履历脱敏PDF')+'</p>'+link(x['fixed_pdf_url'],'固定版本原始来源')+'</td><td>'+E(x['track'])+ul([o['company']+' · '+o['role']+' · '+o['time']+'；'+o['basis'] for o in x['outcomes']])+'</td><td>'+''.join('<p>'+link(p['url'],p['name'])+'：'+E(p['relation'])+'<small> '+E(p['caveat'])+'</small></p>' for p in x['projects'])+'</td><td>'+ul(x['limits'])+'<p>完整专业模块：'+E('、'.join(x['modules']))+'</p><small>'+E(x['redaction']['visual_review'])+'</small></td></tr>'
        resume_controls+='</tbody></table></div><p>“至今”均为来源版本原文用语，不证明抓取当日仍在职。'+link('../08_证据索引与统计/履历脱敏副本目录.json','来源、原始/脱敏SHA-256与版本说明')+'</p></section>'
    core_files=[r for r in records if r.get('complete_redacted_cv_file_received')]
    core_resumes=''
    if core_files:
        core_resumes=f'<section id="core-resumes"><h2>{len(core_files)}份核心方向完整公开履历脱敏副本</h2><p>完整指保留原公开版本全部专业模块；联系区已删除。它们是实习后公开履历，不能证明当时投递版本。公司任职与指标为本人自述。</p>'
        for r in core_files:
            p=r['source_record'];core_resumes+='<div class="panel"><h3>'+refs([r['id']])+' '+E(r['title'])+'</h3><p>'+link('../'+r['redacted_cv_local_file'],'打开完整专业履历脱敏副本')+' · '+link(p['source_url'],'固定原始来源')+'</p><p>'+E(r['source_summary'])+'</p><p><b>实习时间：</b>'+E(r['taxonomy']['experience_date_text'])+'</p><b>项目与局限</b>'+ul(r['weaknesses'])+'</div>'
        if 'DOC11' in by and by['DOC11'].get('source_key')=='HUOMA_AGENT_DOCUMENT':
            r=by['DOC11'];p=r['source_record'];core_resumes+='<h3>本人问数Agent复盘：文档与实现分开</h3><p>'+refs(['DOC11','CV24'])+' · '+link('../'+p['local_path'],'本地本人复盘')+' · '+link(p['source_url'],'固定原文')+'</p><p>'+E(p['relationship_to_internship'])+'</p><p>作者声明技术栈：'+E('、'.join(p['declared_stack']))+'</p><p>'+E(p['static_review'])+'</p><div class="columns"><div><b>值得研究的模块</b>'+ul(p['strengths'])+ul(p['recommended_modules'])+'</div><div><b>作者自列待做</b>'+ul(p['limitations_from_author'])+'</div></div><p>'+E(p['metrics_boundary'])+'</p>'
        core_resumes+='</section>'
    added_nav=(link('#requirements','技术要求分层') if technical else '')+' '+(link('#core-resumes','完整脱敏履历') if core_resumes else '')+' '+(link('#resume-controls','研究履历对照') if resume_controls else '')
    header=header.replace('</nav>',added_nav+'</nav>')
    continuous=''
    if (BASE/'持续补证统计.json').exists():
        continuous='<section id="continuous"><h2>本轮补强：本人源码、SSP逐轮与实现差距</h2><p>'+refs(['CV28','PRO20','PRO21','INT81'])+'：完整履历直接点名UltiCode和ResiCache。实习雇主博彦、服务客户阿里云分开；原版面经只作主题对应，Kafka回答与现版Redis Streams不能混为同一实现。</p><p>'+refs(['CV01','INT78','INT79','INT80'])+'：新增同作者快手四轮、字节四轮、小鹏两轮校招记录；最终SSP来自后来总结，单篇待HR时点仍保留。'+refs(['CV03'])+'：原文明确2025年，美团暑期后同公司SSP；京东SSP与网易SP保留作者推测，华为15a单列。</p><p>'+refs(['OP13'])+'：已读Agent知乎教学文，按官方资料区分内存/持久化、检查点重放/副作用、线程ID/授权；它不是真实面经或生产案例。</p><p>'+refs(['CV22'])+'：AsTimeWheel代码存在初始化顺序、时间基准和重复任务取消语义的静态风险，mock包装层测试不覆盖核心构造。'+refs(['OBS05'])+'：已核SGLang PR12263作者与合并，审到资源接收和测试局部；多人协作不全归一人。</p><p>'+link('../08_证据索引与统计/持续补证_贡献静态核查.json','固定路径、行号与静态依据')+' · '+link('../08_证据索引与统计/持续补证_实习履历与本人源码.json','履历、源码归档修改/省略清单')+'</p></section>'
        header=header.replace('</nav>',link('#continuous','本轮补强')+'</nav>')
    if (BASE/'重点补证统计.json').exists():
        focused='<section id="focused"><h2>重点补证：大厂实习职责、本人源码与项目风险</h2><p>'+refs(['CV30'])+'：Andrew公开完整CV明确2025字节后端、2026 Creator Assistant Agent应用后端实习，包含MCP工具、评测harness及trace职责。脱敏副本保留全部专业模块；内部项目未有公开源码，本人面经/SSP未披露。美国高校背景与中国招聘分档不直接等同。</p><p>'+refs(['CV29','PRO22','PRO23'])+'：Shufeng的2025腾讯、2026 Stripe实习主页逐项直链源码，但缺完整教育CV。TinyKV为课程框架上的Raft/MVCC实现；QuantHarbor有状态与工具代码，同时存在入口导入与同进程exec权限风险，按反例/待核阅读。两个项目均已作固定源码文本派生归档，未运行。</p><p>'+refs(['CV07','INT82','INT83'])+'：本人年终总结明确2025小红书/快手后端实习offer；AML两轮、百度一轮原文补上追问，批次/事件年/结果仍未知。Higress组件已定位，但本人账号与PR关系未闭合，不将框架或他人修复归个人。</p><p>'+refs(['INT11'])+'：确认2025-12-07是发表时间，辅助组增加而严格近期组不增加。'+refs(['OP14','DOC12'])+'：B站AI工程学习建议按目标采用；以5年专家JD推校招SSP统一门槛的观点缺同批次证据，未采作实习要求。</p><p>'+link('../08_证据索引与统计/重点补证_大厂实习履历.json','来源、固定版本及归档清单')+' · '+link('../08_证据索引与统计/重点补证_Higress组件贡献.json','组件实现与个人归属边界')+'</p></section>'
        if (BASE/'继续补证_检索决策与交付.json').exists():
            focused=focused.replace('</section>','<p>'+link('../08_证据索引与统计/继续补证_检索决策与交付.json','后续定向补搜：访问事实与排除理由')+'：前轮两篇腾讯工程知乎原文403、公开视频view接口412；本轮两个视频的pagelist/player接口已200但字幕列表空，最新事实见本轮15问与时间核对。原始链接保留待手动访问。付费汇编和参考答案未充作本人成功材料。</p></section>')
        continuous=focused+continuous
        header=header.replace('</nav>',link('#focused','重点补证')+'</nav>')
    agentlink=''
    if (BASE/'近期Agent补链统计.json').exists():
        agentlink='<section id="agent-link"><h2>近期Agent补链：完整CV、本人实现与实际风险</h2><p>'+refs(['CV31'])+'：中科曙光2025.12–2026.02 Agent开发实习。完整公开CV脱敏副本保留教育、实习、全部项目与技能；CV直接链接NoWorries，主页另链Sprout和本人PR3064。产业企业应用工程与互联网大厂分别呈现；SSP和本人求职面经未披露。</p><p>'+refs(['PRO24','PRO25'])+'：Sprout可读任务拆分、并行、拖慢重拆和合成，但benchmark仅按输出文本特征打分，token检查不能当硬费用上限。NoWorries可读记忆与执行组件，Windows/Linux环境变量隔离、macOS静默成功后的重复执行回退均需重点核。完整应用未运行，不以功能或目录规模推定成熟。</p><p>Sprout归档为固定版本19文本文件派生包；NoWorries归档为14指定文本选读，未包含完整仓库、bundled Python及运行依赖。'+refs(['OP15'])+'：已选读发布者公开的原访谈转写稿（'+link(by['OP15']['source_record']['primary_url'],'打开固定版本原稿')+'），B站只读公开导读，视频/字幕仍未观看或读取。'+refs(['OBS10'])+'：中兴大模型开发SSP自述明确，但Agent职责未披露，作为邻近对照。托马斯两篇面经已有OBS08，未重复增加数量。</p><p>'+link('../08_证据索引与统计/近期Agent补链_来源核读.json','原始关系、逐项比较与缺口')+' · '+link('../08_证据索引与统计/近期Agent补链_Sprout源码归档.json','Sprout固定源码清单')+' · '+link('../08_证据索引与统计/近期Agent补链_NoWorries选读归档.json','NoWorries的14文件选读范围')+'</p></section>'
        header=header.replace('</nav>',link('#agent-link','近期Agent补链')+'</nav>')
    time_review=''
    if 'INT84' in by:
        time_review='<section id="time-review"><h2>近期补充：百度Agent日常实习的15个追问</h2><p>'+refs(['INT84'])+'：已读本人文字全文，包括混合检索、切片依据、开源改造贡献、工具执行兜底、长期记忆、中断续跑及日志定位。作者自认没有做可观测性，LC297手撕未完成；最终结果没有公布。</p><p>标题9.7与正文刚面完的表述，可与2026-09-07展示/编辑字段相互参照，但事件年仍属推定，初发字段未取得；不增加严格近期实习分母。没有取得该作者完整履历或源码，不与CV31等其他作者拼接。</p><p>两个B站视频本轮公开pagelist/player接口均200/code0并取得CID，字幕列表为空；仍未观看或读字幕。两处SSP线索分别为标题党及岗位未明确，本轮未新增SSP成功者。</p><p>'+link('../04_面经与专业观点/百度Agent日常实习_15问与阅读边界.md','问题归纳与阅读建议')+' · '+link('../08_证据索引与统计/SSP与时间补核_来源核读.json','来源、时间与排除理由')+' · '+link('../08_证据索引与统计/SSP与时间补核_公开字幕接口.json','公开字幕接口实际状态')+'</p></section>'
        header=header.replace('</nav>',link('#time-review','本轮15问与时间核对')+'</nav>')
    expert_review=''
    if 'OP16' in by:
        expert_review='<section id="expert-review"><h2>专业观点交叉核对：从评分到实际结果</h2><p>'+refs(['OP16'])+'：百度Comate公开演讲实录选读，会务讲师与议题页可对应。关注按模型分组观测、单题回退和工具失败后的恢复。平台外原文不计B站/知乎本体全文，视频仍0。</p><p>'+refs(['DOC02','OP15','PRO24','PRO25','INT84'])+'：LLM判分要人工校准并核环境结果；Sprout输出文本特征分不能等同代码正确率，NoWorries的重复执行风险要与一般重试分开。项目仅作主题对照，不冒充面经作者本人实现。</p><p>课程会员页虽有美团智能客服SSP等匿名推荐语，但未取得本人原账号、年份、履历和代码，本轮未新增SSP成功者。知乎受限原始链接继续保留。</p><p>'+link('../06_项目分析与推荐/专业观点交叉核对_评测与工具恢复.md','三项对照与指定模块')+' · '+link('../08_证据索引与统计/专业观点交叉核对_来源与比较.json','来源、商业背景和检索结束记录')+'</p></section>'
        header=header.replace('</nav>',link('#expert-review','专业观点交叉核对')+'</nav>')
    recent_review=''
    if 'INT85' in by:
        recent_review='<section id="recent-interviews"><h2>明确日期与成功二面：项目怎样被追问</h2><p>'+refs(['INT68'])+'：同作者投递总表的华为AI应用岗位行直接列2026-04-01，并列5.14面试、5.15杭州、5.25offer；与原面经三个节点对应，已补为2026年。原面经3.31登记/投递与总表4.1日期分别保留，未披露SSP。</p><p>'+link("../08_证据索引与统计/实习事件年份补核_来源.json","同作者关联正文、日期差别与核读范围")+'</p><p>'+refs(['INT85'])+'：作者正文直接写2025-03-14一面、次日未通过，新增到明确近期实习组。追问MQ/RPC环境隔离、OOM和消费慢、非幂等测试数据、高可用及熔断限流；题名为阿里控股爱橙科技，不改称阿里集团直营录用。</p><p>'+refs(['INT86'])+'：美团后端暑期二面，标题和正文均明确后续已offer，未披露SP/SSP。项目角色、同类方案调研、容量、分片、线程池和负载排查有具体问题；当前只核到编辑年，事件年不补写。作者夹入事后思路并推广题库，题库统计不采为本包结论。</p><p>已修正候选人总体录用的旧单场面试适用标记。例如CV02腾讯SSP与INT56携程/菜鸟/美团记录不能直接拼成同一场；公司、档位和原始来源保留，具体对应仍看关联表。</p><p>'+link('../08_证据索引与统计/近期面经与关联纠错_来源核读.json','日期、结果与阅读范围')+' · '+link('../08_证据索引与统计/近期面经与关联纠错_修正清单.json','旧字段修正清单')+'</p></section>'
        if (REPORT/'六项目标逐条验收.md').exists():recent_review=recent_review.replace('</section>','<p>'+link('../01_调研报告/六项目标逐条验收.md','六项目标逐条验收：实物、已完成项与重点缺口')+'</p></section>')
        header=header.replace('</nav>',link('#recent-interviews','后端实习新追问')+'</nav>')
    external_merge=''
    if (BASE/'astra合并_实施映射.json').exists():
        addition=load('astra合并_实施映射.json')
        counts='、'.join(str(n)+'份'+k for k,n in addition['new_by_category'].items())
        external_merge='<section id="external-merge"><h2>2026-10-24：外部调研核读增补</h2><p>64张来源卡逐条去重并核对原文，新增'+E(counts)+'。重复来源只补核读说明，不重复计数；受限来源保留实际状态。</p><p>新增官方文档按指定段落作参考，不增加25项目源码比较分母。完整简历和源码新附件均为0；个人项目设计继续暂缓。原astra目录保留原样，合并前后文件指纹另核。</p><p>'+link('../01_调研报告/外部调研增补与去重清单.html','查看64条去重映射、新面经与指定文档')+' · '+link('../06_项目分析与推荐/外部调研_文档判断与阅读模块.md','新增技术判断、依据与局限')+'</p></section>'
        external_merge=external_merge.replace('</section>',
            '<p>新增面经先读：'+refs(['INT91','INT93','INT101'])+'为事件时间明确的近期后端实习；'+refs(['INT102','INT103','INT104','INT105'])+'补充Agent工具、RAG与项目追问，事件年未知；'+refs(['INT106'])+'为2025春招AI Infra对照，单列，不作为Agent应用统一要求。</p>'
            '<p>新增候选人：'+refs(['CV32','CV33','CV34'])+'为本人经历与面经选读。其中CV33明确2026字节财经后端实习offer，其他流程失败分别记录，档位未披露；'+refs(['OBS11'])+'只读文字和图片入口，本轮未读简历图，不增加完整CV分母。</p></section>')
        header=header.replace('</nav>',link('#external-merge','外部资料增补')+'</nav>')
    body=header+coverage+external_merge+recent_review+expert_review+time_review+agentlink+continuous+route+technical+cap+core_resumes+chains+resume_controls+projectsec+opinions+remaining+downloads+catalog+'<p class="footer">公开自述及指定静态版本的研究资料。最近增补：2026-10-24。个人项目设计暂缓。</p>'
    html=shell(TITLE,body).replace('</style>','@media print{#gaps,#downloads{break-inside:avoid}#routes{break-before:page}#routes .panel{break-inside:auto}.route-item{break-inside:avoid}.footer{display:none}}</style>')
    write(REPORT/(TITLE+'.html'),html);write(REPORT/'index.html',html)

    manual=f'<header><div class="eyebrow">原始链接 · 访问事实 · 待核事项</div><h1>待手动访问链接 · {len(blocked)}条</h1><p>未取得正文的资料不计已读面经或成功者证据。已读材料当前访问不稳定的，也明确标注历史核读范围。搜索“优先”可筛选本轮建议先核的原文；编号按资料组织顺序，不代表质量排序。</p><nav><a href="{TITLE}.html">返回统一报告</a></nav></header><section><label for="manual-search">按标题、状态或待核事项筛选</label><input id="manual-search" type="search"><p>显示 <b id="manual-shown">{len(blocked)}</b> / {len(blocked)}</p>'
    md=[f'# 待手动访问链接（需求核对版，{len(blocked)}条）','', '正文未核的线索不计已读面经或已确认SSP。已读材料的当前访问限制不抹去历史阅读事实。','']
    for n,x in enumerate(blocked,1):
        checks=x.get('to_verify',x.get('manual_check','作者、时间、批次、本人项目与结果'));checks=flatten(checks)
        priority=('<p><b>'+E(x['priority'])+'</b>：'+E(x.get('priority_reason',''))+'</p>') if x.get('priority') else ''
        manual+=f'<article class="manual-card"><h3>{n}. {link(x["url"],x["title"])}</h3>{priority}<p><b>实际状态：</b>{E(x["status"])}</p><p><b>待核：</b>{E(checks)}</p><p class="muted">{E(x["url"])}</p></article>'
        md += [f'{n}. [{x["title"]}]({x["url"]})','',f'   状态：{x["status"]}','',f'   待核：{checks}','']
        if x.get('priority'):md += ['   阅读优先级：'+x['priority']+'；'+x.get('priority_reason',''),'']
    write(REPORT/'待手动访问链接.html',shell('待手动访问链接',manual+'</section>'))
    write(ROOT/'04_面经与专业观点/待手动访问链接.md','\n'.join(md))

    # 原文本先存快照，再用当前记录输出；历史报告不回写为当前口径。
    folders={'JD':'02_招聘岗位资料','CV':'03_简历与候选人案例','INT':'04_面经与专业观点','OP':'04_面经与专业观点','PRO':'06_项目分析与推荐'}
    old_texts={}
    for r in records:
        prefix=re.match(r'[A-Z]+',r['id']).group();folder=folders.get(prefix)
        if not folder:continue
        path=ROOT/folder/(r['id']+'.txt')
        if path.exists():old_texts[str(path.relative_to(ROOT)).replace('\\','/')]=read(path)
    if not (BASE/'纠偏前文本卡快照.json').exists():dump('纠偏前文本卡快照.json',old_texts)
    def plain(v,indent=''):
        if isinstance(v,dict):return '\n'.join(indent+LABELS.get(k,k)+'：\n'+plain(x,indent+'  ') for k,x in v.items())
        if isinstance(v,list):return '\n'.join(indent+'- '+plain(x,indent+'  ').lstrip() for x in v) if v else indent+'—'
        if isinstance(v,bool):return indent+('是' if v else '否')
        return indent+('未核／无' if v is None else str(v))
    for r in records:
        prefix=re.match(r'[A-Z]+',r['id']).group();folder=folders.get(prefix)
        if folder:write(ROOT/folder/(r['id']+'.txt'),r['id']+' | '+r['title']+'\n\n需求核对版 · 2026-10-24\n\n'+plain({k:v for k,v in r.items() if k not in ['comparison','id','title']})+'\n')
    write(ROOT/'00_START_HERE.txt',f'''大厂后端与Agent实习调研包 | 需求核对版 | 2026-10-24

统一入口：01_调研报告/{TITLE}.html（同名PDF），或index.html。
外部增补清单：01_调研报告/外部调研增补与去重清单.html（64条去重映射与原文阅读范围）。
待手动访问：01_调研报告/待手动访问链接.html（{len(blocked)}条原链接与实际状态）。

{totals['candidate_cases']}份候选人分析（含原有历史/算法对照），核心完整CV原件{cv['complete_cv_files_received']}；核心完整脱敏副本{cv.get('complete_redacted_cv_files_received',0)}，研究/Infra完整脱敏对照{totals.get('redacted_resume_controls',0)}份另列。
{totals['interview_materials']}份已读面经逻辑资料：{iv['reading_scope'].get('全文',0)}全文、{iv['reading_scope'].get('部分',0)}部分；明确实习{iv['explicit_internship_all_years_count']}，事件时间可确认近期{iv['strict_recent_explicit_internship_count']}，实习事件年未知{iv['explicit_internship_event_year_unknown_count']}。
另有{iv['publication_recent_event_year_unknown_count']}份近期发表但事件年未知，不能混入严格近期组。
{totals['projects']}项目统一比较；{archive_note}，全部未运行。派生文本归档的修改/省略清单单列。
B站实际观看{op['actual_video_watched_count']}；B站/知乎本体完整内容已读{op['primary_bilibili_or_zhihu_full_content_verified_count']}；另有原始生产访谈逐字稿选读{op.get('primary_external_transcripts_selected',0)}份，不计B站字幕或观看。作者官网替代与平台外原文分别呈现。
现有证据{len(records)}条；统计自动取自08_证据索引与统计/需求覆盖统计.json。

阅读按目标适用性、证据完整度与指定模块分别推荐，无总分；发现顺序和star不参与排序。
近期明确Agent工程SSP的公司、岗位与招聘批次直接自述仍不足；各段履历、项目和面经关系分别报告，不以四段齐全作为每位候选人的门槛。个人项目设计继续暂缓。
保留各轮历史报告；第四轮旧完整目录为01_调研报告/历史资料目录_第四轮快照.html。
''')
    note=f'''# 按最初需求完成资料纠偏

新统一入口：01_调研报告/{TITLE}.html（同名PDF）与index.html。

- 统一146条方向、招聘类型、事件时间和阅读范围；21候选人逐项关联录用、履历、项目/贡献、本人面经。
- 63份面经重新分类，11项能力对照分别列JD、提问、履历、专业观点与模块来源；不强凑四类齐备。
- 19项目全部进入后端7维、Agent8维比较；每项有状态、来源、范围、局限与具体阅读路径。
- 两套阅读顺序分别按方向推荐；不按发现轮次、star或单一总分排序。
- 本轮新增2篇平台外官方正文；没有新增合格成功实习关联、完整CV文件或源码ZIP。
- {len(blocked)}条待核链接同步HTML、Markdown和JSON。完整CV、近期Agent SSP关联及B站/知乎本体阅读缺口仍保留。

当前精确统计以08_证据索引与统计/需求覆盖统计.json为准。辅助“近期发表但事件年未知”按更严口径为9，INT11未确认发表年，不计入该组。所有项目未运行；个人项目设计暂缓。

旧首页另存历史快照，文本卡旧内容另存纠偏前文本卡快照.json；历史报告和PDF保留原轮次，新增最新入口。
'''
    if not (BASE/'目标执行统计.json').exists():write(ROOT/'00_需求核对与资料优先级更新说明.md',note)
    methodology=BASE/'source_methodology.txt';oldmethod=read(methodology)
    start='需求核对版最新口径（2026-10-23）'
    if not oldmethod.startswith(start) and not (BASE/'目标执行统计.json').exists():
        write(methodology,start+'\n最新统计：需求覆盖统计.json；统一报告：01_调研报告/'+TITLE+'.html。\n146逻辑记录；21候选人分析；63面经（57全文、6部分）；19项目；16ZIP；完整CV文件0。\n明确实习40；事件时间明确近期8；实习事件年未知31；辅助近期发表事件年未知9。\nB站实际观看0、知乎本体正文0；官网替代全文1、选读1；另补官方原文2。\n结果、个人贡献、源码快照和实际运行分开；全部项目未运行；个人项目设计暂缓。\n\n以下均为历史轮次快照，不能代替最新统计：\n\n'+oldmethod)
    latest_banner=f'<div data-requirement-entry style="padding:15px;margin:12px;background:#fff4cc;color:#213f3c">此页保留历史轮次快照。最新分类、完整{len(projects)}项目比较与阅读顺序见 <a href="{TITLE}.html">需求核对与阅读优先级</a>。</div>'
    for path in REPORT.glob('*.html'):
        if path.name in ['index.html',TITLE+'.html','待手动访问链接.html','外部调研增补与去重清单.html']:continue
        text=read(path)
        if 'data-requirement-entry' not in text:
            text=re.sub(r'(<body[^>]*>)',lambda m:m.group(1)+latest_banner,text,count=1,flags=re.I)
        else:
            text=re.sub(r'<div data-requirement-entry\b[^>]*>.*?</div>',lambda m:latest_banner,text,count=1,flags=re.S)
        write(path,text)
    dump('需求报告生成统计.json',{'records':len(records),'candidate_chains':len(cv) and totals['candidate_cases'],'project_details':len(projects),'dimension_items':sum(len(p['backend_dimensions'])+len(p['agent_dimensions']) for p in projects),'manual_links':len(blocked),'html_entry':TITLE+'.html','all_projects_executed':False,'source':'需求覆盖统计.json'})
    print(json.dumps({'html':TITLE+'.html','evidence_cards':len(records),'project_details':len(projects),'manual_links':len(blocked)},ensure_ascii=False))

if __name__=='__main__':generate()
