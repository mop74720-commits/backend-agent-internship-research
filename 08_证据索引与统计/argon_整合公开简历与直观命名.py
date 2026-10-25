"""汇总逐人原件复核，以方向/结果/作者命名；保留当前图册已有内容。"""
from pathlib import Path
from collections import Counter
from html import escape as E
import hashlib,io,json,os,re,zipfile
import fitz
from PIL import Image
from bs4 import BeautifulSoup

BASE=Path(__file__).resolve().parent; ROOT=BASE.parent
DIR=ROOT/'03_简历与候选人案例'; ORIG=DIR/'公开简历原件'
MANIFEST=BASE/'公开简历原件_清单.json'
LABELS={
 'CV01':'后端+SSP自述｜通知服务与IM', 'CV02':'后端+RPC与业务项目｜JavaWxy参考写法',
 'CV03':'后端+美团实习后SSP自述｜Richard奇', 'CV04':'后端+字节转正｜大学四年复盘',
 'CV05':'后端+SSP自述+开源贡献｜erdengk', 'CV06':'后端+字节SSP自述｜wasabi',
 'CV07':'后端+Agent+实习offer｜等闲king', 'CV08':'大模型应用+商汤实习offer｜本人面经',
 'CV09':'后端+腾讯IEG实习offer｜游戏安全', 'CV10':'C++后端+腾讯转正SSP自述+历史｜CalvinNeo',
 'CV11':'C++后端+SSP自述+历史｜linyacool', 'CV12':'C++后端+SP与SSP自述+2021｜muluoleiguo',
 'CV13':'算法研究+SSP自述｜dong03', 'CV14':'Java后端+SSP自述+2019｜mio4',
 'CV15':'后端+头条SSP自述+2018｜CyC2018', 'CV16':'自动驾驶算法+地平线SSP自述｜LittleChild',
 'CV17':'Java后端+SSP自述+2025届｜码间烟火录', 'CV18':'后端+SP与SSP自述+历史｜IcyCC',
 'CV19':'后端+腾讯转正SSP自述｜鱼皮', 'CV20':'后端+字节SSP自述+2019｜鬼卞',
 'CV21':'Java后端+京东offer｜DreamCats班车项目', 'CV22':'后端+Agent+实习经历｜Stochastic',
 'CV23':'后端+实习履历｜张恒华', 'CV24':'Agent工程+实习履历｜林祥庆',
 'CV25':'Agent+蚂蚁实习offer｜TikTok后端OC另列', 'CV26':'Agent工程+360实习offer｜金蝶与讯飞经历',
 'CV27':'C++后端+阿里云存储实习offer｜2025暑期', 'CV28':'后端+博彦实习｜DavidHLP',
 'CV29':'后端+腾讯与Stripe实习｜AlexChen', 'CV30':'后端+Agent+字节实习｜AndrewWang',
 'CV31':'Agent+中科曙光实习｜黄一航', 'CV32':'后端+秋招经历｜无实习背景',
 'CV33':'后端+字节财经实习offer｜非科班转码', 'CV34':'后端+春招offer｜四非学院本',
 'OBS11':'后端+录用未知｜网盘与RPC简历图', 'OBS05':'大模型训练+研究对照｜郭天宇',
 'OBS06':'强化学习与多模态+研究对照｜李忠智', 'OBS07':'AI Infra+研究对照｜HanrongZhang',
}
STEMS={
 'CV01':'后端+SSP自述_通知服务与IM', 'CV02':'后端+RPC与业务项目_JavaWxy',
 'CV05':'后端+SSP自述+开源贡献_erdengk', 'CV06':'后端+字节SSP自述_wasabi',
 'CV13':'算法研究+SSP自述_dong03', 'CV15':'后端+头条SSP自述+2018_CyC2018',
 'CV18':'后端+SP与SSP自述+历史_IcyCC', 'CV23':'后端+实习履历_张恒华',
 'CV24':'Agent工程+实习履历_林祥庆', 'CV28':'后端+博彦实习_DavidHLP',
 'CV29':'后端+腾讯与Stripe实习_AlexChen', 'CV30':'后端+Agent+字节实习_AndrewWang',
 'CV31':'Agent+中科曙光实习_黄一航', 'OBS11':'后端+录用未知_网盘与RPC',
 'OBS05':'大模型训练+研究对照_郭天宇', 'OBS06':'强化学习与多模态+研究对照_李忠智',
 'OBS07':'AI_Infra+研究对照_HanrongZhang',
}


def load(name):return json.loads((BASE/name).read_text(encoding='utf-8-sig'))
def relative(path):return Path(path).relative_to(ROOT).as_posix()
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def link(path,label):return '<a href="'+E(str(path),quote=True)+'">'+E(label)+'</a>'
def rewrite(value,mapping):
    if isinstance(value,dict):return {k:rewrite(v,mapping) for k,v in value.items()}
    if isinstance(value,list):return [rewrite(v,mapping) for v in value]
    return mapping.get(value,value) if isinstance(value,str) else value


def collect():
    records=load('all_evidence_records.json'); by={r['id']:r for r in records}
    assets=[]; cases={}
    existing=load('公开简历复核_既有附件.json')['results']
    for row in existing:
        rid=row['candidate_id'];cases[rid]=dict(row)
        if row.get('local_file'):
            assets.append(dict(row,format_origin='作者原始PDF' if row['local_file'].endswith('.pdf') else '文章原始图片'))
    github=load('公开简历复核_GitHub.json')
    for case in github['candidates']:
        rid=case['candidate_id'];cases[rid]=case
        for row in case['assets']:
            kind='参考写法原图' if rid=='CV02' else ('网页导出' if rid=='CV15' else ('DOCX排版导出' if row.get('not_author_original_format') else ('作者原始PDF' if row['local_file'].endswith('.pdf') else '作者原稿')))
            assets.append(dict(row,candidate_id=rid,format_origin=kind,
                original_url=row.get('url'),source_article_url=case['source_article_url'],
                identity_boundary=case.get('identity_and_version_boundary',''),outcome_boundary=case.get('outcome_boundary','')))
    for name,key in [('公开简历复核_牛客甲.json','results'),('公开简历复核_牛客乙.json','cases')]:
        for c in load(name)[key]:cases[c['candidate_id']]=c
    for name in ['公开简历复核_网页导出.json','公开简历复核_CV29网页导出.json']:
        for row in load(name)['results']:
            if row.get('local_file'):
                assets.append(dict(row,format_origin='网页导出'))
                cases.setdefault(row['candidate_id'],{}).update({'candidate_id':row['candidate_id'],'status':'已取得网页浏览器导出，未取得作者原始PDF','original_url':row['original_url']})
    for rid in ['CV23','CV28']:
        cases[rid]['attempts']=[r for r in load('公开简历复核_网页来源.json')['results'] if r['candidate_id']==rid]
    return by,assets,cases


def rename_and_previews(assets):
    mapping={};names=Counter()
    # 本轮新增文件的所有路径先核验，再逐个重命名。历史脱敏附件不动。
    for row in assets:
        rid=row['candidate_id']; old=ROOT/row['local_file'];suffix=old.suffix.lower();stem=STEMS[rid]
        if rid=='CV02':
            names[rid]+=1;detail='参考简历图'+str(names[rid])+'_投递版本未核'
        elif rid=='CV18':
            year='2019' if '2019' in old.name or suffix=='.tex' else '2022'
            detail=year+('_作者原稿' if suffix=='.tex' else '_原版简历')
        elif row['format_origin']=='网页导出':detail='网页履历_'+('浏览器截图' if suffix in ['.png','.jpg'] else '浏览器导出')
        elif row['format_origin']=='DOCX排版导出':detail='Word排版导出'
        elif suffix=='.docx':detail='作者公开原稿'
        elif row['format_origin']=='作者原始PDF':detail='公开原版简历'
        else:detail='简历片段原图' if rid in ['CV01','CV06'] else '作者打码的一页简历原图'
        target=ORIG/(stem+'_'+detail+suffix)
        source=old.resolve();dest=target.resolve()
        if not source.is_relative_to(ORIG.resolve()) or not dest.is_relative_to(ORIG.resolve()):raise ValueError('命名越界')
        if source!=dest:
            if dest.exists() and digest(dest)!=digest(source):raise FileExistsError(dest)
            mapping[relative(source)]=relative(dest)
    for old,new in mapping.items():
        source=ROOT/old;dest=ROOT/new
        if source.exists():
            if not dest.exists():os.rename(source,dest)
            elif digest(source)==digest(dest):
                # 不删除同内容重名文件；正常首轮不会进入此分支。
                pass
    assets=rewrite(assets,mapping)
    for row in assets:
        p=ROOT/row['local_file'];row['sha256']=digest(p);row['additional_redaction']=False
        if p.suffix.lower()=='.pdf':
            previews=[]
            with fitz.open(p) as doc:
                row['page_count']=len(doc)
                for i,page in enumerate(doc):
                    q=ORIG/'预览'/(p.stem+f'_第{i+1}页.png');q.parent.mkdir(exist_ok=True)
                    page.get_pixmap(matrix=fitz.Matrix(1.6,1.6)).save(q);previews.append(relative(q))
            row['preview_files']=previews
        elif p.suffix.lower() in ['.png','.jpg','.jpeg']:
            row['preview_files']=[relative(p)]
            with Image.open(p) as img:row['image_size']=list(img.size)
        else:row.setdefault('preview_files',[])
    # 保留各组检索日志；路径同步，校验值不变。
    for p in BASE.glob('公开简历复核_*.json'):
        before=json.loads(p.read_text(encoding='utf-8-sig'));after=rewrite(before,mapping)
        if after!=before:p.write_text(json.dumps(after,ensure_ascii=False,indent=2),encoding='utf-8')
    return assets,mapping


CSS='''*{box-sizing:border-box}body{margin:0;background:#f0eee8;color:#20313a;font:16px/1.7 "Microsoft YaHei",sans-serif}main{max-width:1280px;margin:auto;padding:32px 24px 60px}h1{font-size:34px;line-height:1.35}h2{margin-top:36px}a{color:#176562;text-underline-offset:3px}header{border-top:6px solid #a74a2f;padding:18px 0}p{max-width:1000px}.tools{position:sticky;top:0;background:#f0eee8;padding:12px 0;display:flex;gap:12px;z-index:5;flex-wrap:wrap}input,select{font:inherit;padding:9px 12px;border:1px solid #a4b8b1;border-radius:4px}input{flex:1;min-width:190px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}.asset{min-width:0;background:white;border:1px solid #cfd9d3;padding:18px}.asset h3{font-size:18px;margin:12px 0}.asset img{width:100%;height:300px;object-fit:contain;background:#f5f5f2;object-position:top}.tag{font-size:12px;padding:3px 7px;background:#e8efe8;display:inline-block;margin-bottom:10px}.small{font-size:13px;color:#5d6a69}.links{display:flex;gap:12px;flex-wrap:wrap}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;background:white;font-size:14px}th,td{padding:12px;border-bottom:1px solid #d8dfd8;text-align:left;vertical-align:top}th{background:#e3ece7}details{margin-top:8px}summary{cursor:pointer;color:#176562}[hidden]{display:none!important}@media(max-width:850px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:560px){main{padding:20px 14px}.grid{grid-template-columns:1fr}h1{font-size:28px}table{min-width:750px}.asset img{height:360px}}'''


def write_index(data,by):
    assets=data['assets'];cases=data['cases'];counts=data['counts']
    order={'作者原始PDF':0,'作者原稿':1,'文章原始图片':2,'DOCX排版导出':3,'网页导出':4,'参考写法原图':5}
    body='<header><p>'+link('../argon_候选人与简历图册.html','返回候选人图册')+'</p><h1>后端 / Agent · 公开简历直达</h1><p>按方向、录用结果和材料类型直接命名。作者原PDF '+str(counts['original_pdfs'])+'份、DOCX原稿 '+str(counts['original_docx'])+'份；文章原图 '+str(counts['article_original_images'])+'份，参考写法原图 '+str(counts['reference_images'])+'份。网页与Word导出另列。</p><p class="small">本轮没有增加遮盖；作者原有打码保持原样。“SSP自述”表示本人公开声明，附件与正式投递版本的关系以各项说明为准。</p></header>'
    body+='<div class="tools"><input id="q" placeholder="搜索：后端、SSP、Agent、字节、作者名"><select id="kind"><option value="">全部材料</option>'+''.join('<option>'+x+'</option>' for x in order)+'</select><span id="shown"></span></div><section class="grid">'
    preferred=['CV30','CV31','CV24','CV18','CV05','CV01','CV06','CV23','CV28','CV15','CV29','CV02','CV13','OBS11','OBS05','OBS06','OBS07']
    for a in sorted(assets,key=lambda a:(preferred.index(a['candidate_id']),order.get(a['format_origin'],9),a['local_file'])):
        if Path(a['local_file']).suffix not in ['.pdf','.docx','.png','.jpg','.jpeg']:continue
        rid=a['candidate_id'];filename=Path(a['local_file']).name
        preview=a.get('preview_files',[])
        image='<a href="'+E(os.path.relpath(ROOT/a['local_file'],ORIG).replace('\\','/'),quote=True)+'"><img loading="lazy" src="'+E(os.path.relpath(ROOT/preview[0],ORIG).replace('\\','/'),quote=True)+'" alt="'+E(filename)+'"></a>' if preview else ''
        boundary='；'.join(str(a.get(k) or '') for k in ['version_boundary','identity_boundary','completeness','outcome_boundary'] if a.get(k))
        if rid=='CV02':boundary='README称“参考如下写法”；未认证为本人正式投递简历。保留作者原打码。'
        source=a.get('original_url') or a.get('url') or by[rid]['url']
        search=(LABELS[rid]+' '+filename+' '+a['format_origin']).lower()
        short={'CV02':'参考写法图片，未认证为本人正式投递简历。','CV13':'算法研究对照；当前公开CV与历史SSP事件分开。','CV18':a.get('version_boundary','作者历史公开稿，具体投递版本另核。'),'CV05':'公开DOCX原稿与Word导出分开；SSP为本人自述。','CV01':'通知服务的实习简历片段，非完整简历。','CV06':'实习与开源片段，保留作者原打码。','CV30':'字节后端与Agent实习；未披露SSP档位。','CV31':'中科曙光Agent实习；未披露SSP档位。','OBS11':'作者已遮盖内部实习内容；录用未知。'}.get(rid,'网页导出不是作者原始PDF。' if a['format_origin']=='网页导出' else '直接打开作者公开原件。')
        body+='<article class="asset" data-kind="'+E(a['format_origin'])+'" data-search="'+E(search,quote=True)+'"><span class="tag">'+E(a['format_origin'])+' · '+rid+'</span>'+image+'<h3>'+E(filename)+'</h3><div class="links">'+link(os.path.relpath(ROOT/a['local_file'],ORIG).replace('\\','/'),'打开文件')+link(source,'原始来源')+'</div><p class="small">'+E(short)+'</p><details class="small"><summary>来源、版本与录用关系</summary><p>'+E(boundary or '公开专业履历；录用或SSP关系按候选人原文判断。')+'</p></details></article>'
    body+='</section><h2>34位候选人：逐人复核结果</h2><p class="small">“本轮未取得”只对应已检查位置；遇到访问受限，保留原始链接供手动核查。</p><div class="scroll"><table><thead><tr><th>方向与录用特征</th><th>目前取得什么</th><th>本轮复核与原文</th></tr></thead><tbody>'
    for rid in sorted((x for x in by if re.fullmatch('CV\\d+',x)),key=lambda x:int(x[2:])):
        c=cases.get(rid,{}); own=[a for a in assets if a['candidate_id']==rid]
        kinds=list(dict.fromkeys(a['format_origin'] for a in own))
        finding=c.get('finding') or c.get('conclusion') or c.get('identity_and_version_boundary') or c.get('status') or c.get('result') or '见复核记录'
        body+='<tr><td>'+E(LABELS[rid])+'<br><small>'+rid+'</small></td><td>'+E(' / '.join(kinds) if kinds else '本轮未取得PNG/PDF简历')+'</td><td>'+E(str(finding))+'<br>'+link(by[rid]['url'],'作者原文')+' · '+link('../argon_候选人与简历图册.html#'+rid,'候选人卡片')+'</td></tr>'
    body+='</tbody></table></div><p class="small">'+link('../../08_证据索引与统计/公开简历原件_清单.json','文件来源、版本与逐人复核清单')+'</p>'
    js='''const cards=[...document.querySelectorAll('.asset')],q=document.getElementById('q'),k=document.getElementById('kind');function run(){let n=0;for(const c of cards){c.hidden=!!((q.value&&!c.dataset.search.includes(q.value.trim().toLowerCase()))||(k.value&&c.dataset.kind!==k.value));if(!c.hidden)n++;}document.getElementById('shown').textContent=n+' / '+cards.length;}q.oninput=run;k.onchange=run;run();'''
    html='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>后端与Agent公开简历直达</title><style>'+CSS+'</style><main>'+body+'</main><script>'+js+'</script></html>'
    (ORIG/'简历原件直达.html').write_text(html,encoding='utf-8')


def update_atlas(data):
    p=DIR/'argon_候选人与简历图册.html';soup=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    for old in soup.select('#public-originals-update'):old.decompose()
    banner=BeautifulSoup('<section id="public-originals-update" style="padding:20px 24px;background:#fff4df;border:1px solid #d6c29a;margin:22px 0"><h2 style="margin:0 0 8px">公开原件已补齐：按方向与录用结果直达</h2><p>已重新取得作者原PDF和图片，另找回IcyCC历史PDF、dong03研究CV与erdengk原DOCX。文件名直接标明“后端+SSP自述”“后端+Agent+字节实习”等特征。作者原有打码保留。</p><p><a style="font-weight:bold" href="公开简历原件/简历原件直达.html">打开PNG / PDF原件与34人复核表 →</a></p></section>','html.parser')
    main=soup.find('main');main.insert(0,banner)
    grouped={}
    for a in data['assets']:grouped.setdefault(a['candidate_id'],[]).append(a)
    for entry in soup.select('article.entry[id]'):
        rid=entry['id']
        if rid not in LABELS:continue
        factual_updates={
            'CV05':{'新的完整简历链接404':'新cv网页链接仍404；本轮已从本人profile仓库取得公开DOCX与Word导出PDF'},
            'CV13':{'未获取完整成功者CV':'本轮已取得本人主页直链的2页研究CV；未证明为当年SSP投递版本'},
            'CV18':{'全文HTTP取得后仅保留专业归纳，未打包原件/联系方式；PDF未视觉核验':'本轮已取得2019原PDF与2022更新版，公开原件不额外脱敏',
                    '当前可用固定版本晚于2019秋招；不当作2019提交版本或当年面试代码':'2019简历稿与2022更新版分列；项目当前源码不等同2019面试代码'},
        }
        for text in list(entry.find_all(string=True)):
            updated=str(text)
            for old,new in factual_updates.get(rid,{}).items():updated=updated.replace(old,new)
            if updated!=str(text):text.replace_with(updated)
        heading=entry.find('h3')
        if heading:heading.string=LABELS[rid]
        entry['data-search']=(entry.get('data-search','')+' '+LABELS[rid]).lower()
        own=grouped.get(rid,[])
        if not own:continue
        prioritized=sorted(own,key=lambda a:({'作者原始PDF':0,'DOCX排版导出':1,'网页导出':2,'文章原始图片':3,'参考写法原图':4,'作者原稿':5}.get(a['format_origin'],9), '2022' in a['local_file']))
        first=next((a for a in prioritized if a.get('preview_files')),prioritized[0])
        entry['data-visual']='yes';entry['class']=[x for x in entry.get('class',[]) if x!='article-only']
        if 'has-visual' not in entry['class']:entry['class'].append('has-visual')
        oldpreview=entry.select_one('.preview') or entry.select_one('.article-label')
        preview=first.get('preview_files',[])
        if preview:
            tag=soup.new_tag('a',attrs={'class':'preview','href':'../'+first['local_file'],'target':'_blank'})
            tag.append(soup.new_tag('img',attrs={'src':'../'+preview[0],'loading':'lazy','alt':LABELS[rid]+'公开材料预览'}))
            if oldpreview:oldpreview.replace_with(tag)
        status=entry.select_one('.material-status')
        if status:status.string=' / '.join(dict.fromkeys(a['format_origin'] for a in own))
        nav=entry.select_one('.entry-links')
        if nav:
            legacy_links=[a for a in nav.select('a:not(.public-original-link)') if '脱敏' in a.get_text()]
            if legacy_links:
                details=entry.select_one('details.legacy-redacted')
                if not details:
                    details=soup.new_tag('details',attrs={'class':'legacy-redacted'})
                    title=soup.new_tag('summary');title.string='旧版脱敏副本（备查）';details.append(title)
                    nav.insert_after(details)
                for a in legacy_links:details.append(a.extract())
            for a in nav.select('a.public-original-link'):a.decompose()
            for a in reversed(prioritized):
                if Path(a['local_file']).suffix=='.tex':continue
                tag=soup.new_tag('a',href='../'+a['local_file'],attrs={'class':'primary-link public-original-link','target':'_blank'})
                tag.string=Path(a['local_file']).name
                nav.insert(0,tag)
        if entry.parent and entry.parent.get('id')=='article-candidates':
            entry.extract();soup.select_one('#candidates').append(entry)
        for details in entry.select('details'):
            if 'legacy-redacted' in details.get('class',[]):details.attrs.pop('open',None)
            elif details.get('class')!=['article-collection']:details['open']=''
    visual=len(soup.select('#candidates article.entry[id]'));article=len(soup.select('#article-candidates article.entry[id]'))
    for metric,value,description in zip(soup.select('.summary .metric'),[34,data['counts']['original_pdfs'],data['counts']['article_original_images'],data['counts']['reference_images']],['核心候选人已逐人复核','作者原PDF（含历史版本与研究对照）','文章原始简历图（含片段与作者打码）','参考写法图片（投递版本未核）']):
        if metric.find('b'):metric.find('b').string=str(value)
        if metric.find('span'):metric.find('span').string=description
    hero=soup.select_one('header.hero p')
    if hero:hero.string='直接看作者公开PDF、简历原图及网页履历导出，再结合项目、面经与录用自述分析。原件不增加遮盖；“参考写法”和作者已打码的片段分别标明。'
    intro=soup.select_one('p.intro')
    if intro:intro.string='本轮优先链接重新下载的公开原件。旧脱敏附件保留备查；网页/Word导出均明确标注来源格式。'
    for el in soup.find_all(['summary','h2','a','p']):
        if el.find(['article','section','table']):continue
        for t in list(el.find_all(string=True,recursive=False)):
            value=str(t)
            value=value.replace('其余 27 位','其余 '+str(article)+' 位').replace('其余27位','其余'+str(article)+'位')
            value=value.replace('（7位）','（'+str(visual)+'位）').replace('(7位)','('+str(visual)+'位)')
            value=value.replace('以下候选人未公开独立 PDF/图片简历','以下候选人本轮尚未取得独立 PDF/图片简历')
            value=value.replace('无公开简历图/PDF','本轮未取得简历图/PDF').replace('无公开PDF/图','本轮未取得PDF/图')
            if value!=str(t):t.replace_with(value)
    first_heading=soup.select_one('#candidates').find_previous('div',class_='section-title')
    if first_heading and first_heading.find('h2'):
        first_heading.find('h2').string='一、可直接阅读的简历与履历材料（'+str(visual)+'条，含1条参考写法）'
    for text in soup.find_all(string=True):
        if text.parent.name in ['script','style']:continue
        replacement=str(text).replace('无公开简历图/PDF','本轮未取得简历图/PDF').replace('未公开简历附件的候选人','本轮未取得简历附件的候选人')
        if replacement!=str(text):text.replace_with(replacement)
    footer=soup.find('footer')
    if footer:footer.string='2026-10-24原件复核更新：作者公开文件保留原字节，不额外脱敏；网页与DOCX导出按实际格式标注。缺失结论仅限本轮已查路径。'
    # 外部模板也用了entry类；只筛选真正的候选人卡片，避免搜索报错。
    for script in soup.find_all('script',src=False):
        text=script.string or script.get_text()
        if "querySelectorAll('.entry')" in text:
            text=text.replace("querySelectorAll('.entry')","querySelectorAll('.entry[data-search]')")
            script.string=text
    p.write_text(str(soup),encoding='utf-8')
    # 用户仍开着旧文件名的标签，保留轻量跳转入口。
    alias=DIR/'候选人与简历图册.html'
    if not alias.exists():alias.write_text('<!doctype html><meta charset="utf-8"><title>候选人与简历图册</title><a href="argon_候选人与简历图册.html">打开更新后的图册</a><script>location.replace("argon_候选人与简历图册.html"+location.hash)</script>',encoding='utf-8')


def main():
    backup=BASE/'历史更新说明/公开原件更新前_图册与导览.zip';backup.parent.mkdir(exist_ok=True)
    if not backup.exists():
        with zipfile.ZipFile(backup,'x',zipfile.ZIP_DEFLATED) as z:
            for p in [DIR/'argon_候选人与简历图册.html',DIR/'argon_README_简历目录导览.md',BASE/'argon_整理简历视觉材料.py']:
                z.write(p,relative(p))
    if MANIFEST.exists():
        data=load(MANIFEST.name);by={r['id']:r for r in load('all_evidence_records.json')}
    else:
        by,assets,cases=collect();assets,mapping=rename_and_previews(assets);cases=rewrite(cases,mapping)
        counts=Counter(a['format_origin'] for a in assets)
        data={'checked_on':'2026-10-24','naming_rule':'方向+录用特征_作者_材料类型；SSP仅有自述则写SSP自述。','assets':assets,'cases':cases,'display_labels':LABELS,'path_mapping':mapping,
            'counts':{'checked_core_candidates':len([x for x in cases if x.startswith('CV')]),'original_pdfs':counts['作者原始PDF'],'original_docx':sum(a['local_file'].endswith('.docx') for a in assets),'article_original_images':counts['文章原始图片'],'reference_images':counts['参考写法原图'],'web_exports':counts['网页导出'],'word_exports':counts['DOCX排版导出']},
            'boundaries':['公开原件不新增遮盖；不恢复作者打码。','网页及DOCX导出不是作者原始PDF。','CV02参考写法未认证为本人投递版。','CV13研究方向与后端/Agent应用工程分开。','CV18 2019与2022版本分开，未证明每次实际投递使用。']}
        MANIFEST.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    source_mapping={f'03_简历与候选人案例/公开简历原件/网页来源/{rid}_公开网页原始来源.html':f'03_简历与候选人案例/公开简历原件/网页来源/{rid}_公开网页原始来源.html.txt' for rid in ['CV23','CV28']}
    data=rewrite(data,source_mapping)
    MANIFEST.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    p=BASE/'公开简历复核_网页来源.json'
    p.write_text(json.dumps(rewrite(load(p.name),source_mapping),ensure_ascii=False,indent=2),encoding='utf-8')
    write_index(data,by);update_atlas(data)
    guide='# 后端与Agent简历：直接打开原件\n\n首选入口：[按方向与录用结果查看PNG/PDF](公开简历原件/简历原件直达.html)。\n\n文件名直接写方向、录用特征、作者和材料类型。例如：\n\n- 后端+Agent+字节实习_AndrewWang_公开原版简历.pdf\n- Agent+中科曙光实习_黄一航_公开原版简历.pdf\n- 后端+SP与SSP自述+历史_IcyCC_2019_原版简历.pdf\n\n[完整候选人图册](argon_候选人与简历图册.html)保留项目、技术栈和面经分析。原版、作者打码片段、网页导出与参考写法分别标注。旧版脱敏附件保留备查。\n'
    (DIR/'argon_README_简历目录导览.md').write_text(guide,encoding='utf-8')
    print(json.dumps(data['counts'],ensure_ascii=False))


if __name__=='__main__':main()
