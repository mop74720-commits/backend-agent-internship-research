"""核对当前新增证据、静态范围、附件与交付一致性；不认定整体研究完成。"""
from pathlib import Path
from collections import Counter
from urllib.parse import urlsplit,unquote
import csv,hashlib,json,re,zipfile
from bs4 import BeautifulSoup
import fitz

BASE=Path(__file__).resolve().parent;ROOT=BASE.parent;REPORT=ROOT/'01_调研报告'
def load(n):return json.loads((BASE/n).read_text(encoding='utf-8-sig'))

def main():
    checks=[]
    def check(name,ok,detail=None):checks.append({'name':name,'passed':bool(ok),'detail':detail})
    bad=[]
    for p in ROOT.rglob('*.json'):
        try:json.loads(p.read_text(encoding='utf-8-sig'))
        except Exception as e:bad.append({'file':str(p.relative_to(ROOT)),'error':str(e)})
    check('全部JSON可解析',not bad,bad)
    rows=load('all_evidence_records.json');by={r['id']:r for r in rows};s=load('需求覆盖统计.json');progress=load('持续补证统计.json')
    cv=load('candidate_cases.json')['cases'];iv=load('interview_records.json');pr=load('project_recommendations.json')['projects'];comp=load('项目统一比较与阅读优先级.json')
    before=load('持续补证前主数据快照.json');before_ids={r['id'] for r in before['records']}
    check('8条新来源与旧快照差异吻合',len(rows)==len(by)==176 and set(by)-before_ids==set(progress['new_record_ids']) and len(progress['new_record_ids'])==8)
    check('主表与候选人面经项目一致',all(r==by[r['id']] for r in cv+iv+pr))
    check('统计总量与类别一致',Counter(r['category'] for r in rows)==s['category_counts'] and s['totals']['logical_evidence_records']==len(rows) and s['totals']['candidate_cases']==len(cv) and s['totals']['interview_materials']==len(iv) and s['totals']['projects']==len(pr))
    check('28候选人四段关系齐全',len(cv)==28 and all(set(r['chain'])=={'outcome','profile','project','interview'} for r in cv))
    check('74面经67全文7部分且未补造年份',len(iv)==74 and Counter(r['reading']['scope'] for r in iv)=={'全文':67,'部分':7} and sum(r.get('strict_recent_internship',False) for r in iv)==9 and not by['INT81']['taxonomy']['year_confirmed'])
    check('新三篇校招不计近期实习',all(by[i]['taxonomy']['recruitment']=='校招' and not by[i]['strict_recent_internship'] and by[i]['candidate_link_ids']==['CV01'] for i in ['INT78','INT79','INT80']))
    check('CV01本人逐轮已建立且结果时点分开',len(by['CV01']['chain']['interview'])==3 and by['CV01']['has_direct_named_project_or_contribution'] and not by['CV01']['personal_source_code_verified'] and '待HR' in by['INT80']['outcome'] and all(any(o['company']==company and o['grade']=='SSP' for o in by['CV01']['outcomes']) for company in ['快手','字节跳动','小鹏']))
    c3=by['CV03'];o3={o['company']:o for o in c3['outcomes']}
    check('CV03时间线和推测档位未混',c3['taxonomy']['year_confirmed'] and c3['taxonomy']['recruitment']=='混合' and '2025' in c3['date'] and o3['美团']['grade']=='SSP' and '推定' in o3['京东']['grade'] and '猜测' in o3['网易']['grade'] and '15a' in o3['华为']['grade'])
    check('CV28雇主客户与面经结果分开',by['CV28']['outcomes'][0]['company']=='博彦科技' and '阿里直签' in by['CV28']['outcomes'][0]['boundary'] and by['INT81']['company']=='未知' and by['INT81']['result_status']=='unknown' and by['INT81']['source_record']['cannot_link_to_specific_employer_offer'])
    check('INT80主题按本篇原文修正','消息队列' not in by['INT80']['topics'] and '性能测试' not in by['INT80']['topics'] and 'SQL' in by['INT80']['topics'])
    check('平台正文4视频0且教学不计面经',s['opinion_coverage']['primary_bilibili_or_zhihu_full_content_verified_count']==4 and s['opinion_coverage']['zhihu_native_fulltexts_read']==3 and s['opinion_coverage']['actual_video_watched_count']==0 and 'OP13' not in {r['id'] for r in iv} and len(by['OP13']['required_corrections'])==3)
    check('21项目315维且每维可定位',len(comp['projects'])==21 and sum(len(p['backend_dimensions'])+len(p['agent_dimensions']) for p in comp['projects'])==315 and all(v['source_URL'] and v['read_scope'] for p in comp['projects'] for direction in ['backend','agent'] for v in p[direction+'_dimensions'].values()))
    check('两个本人后端项目不冒充Agent',all(all(v['status']=='不适用' for v in p['agent_dimensions'].values()) for p in comp['projects'] if p['id'] in ['PRO20','PRO21']))
    check('16原包2派生3仅链接分列',s['totals']['source_archives']==18 and s['totals']['original_fixed_source_zips']==16 and s['totals']['redacted_text_source_zips']==2 and s['totals']['fixed_link_only']==3)
    d=load('持续补证_实习履历与本人源码.json');artifact_checks=[]
    for p in d['projects']:
        a=p['attachment'];f=ROOT/a['local_path'];ok=f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==a['sha256'] and f.stat().st_size==a['bytes'];details=[]
        with zipfile.ZipFile(f) as z:
            ok=ok and z.testzip() is None
            for src in p['implementation_and_tests']:
                matches=[x for x in z.namelist() if x.endswith('/'+src['path'])]
                match=len(matches)==1 and hashlib.sha256(z.read(matches[0])).hexdigest()==src['sha256'];ok=ok and match
                details.append({'path':src['path'],'identical':match})
            license_paths=[x for x in z.namelist() if x.endswith('/LICENSE') and x.count('/')==1]
            ok=ok and len(license_paths)==1 and hashlib.sha256(z.read(license_paths[0])).hexdigest()==p['license']['sha256']
        artifact_checks.append({'file':a['local_path'],'passed':bool(ok),'read_paths':details})
    check('派生ZIP实物CRC哈希与10核读路径',len(artifact_checks)==2 and all(a['passed'] for a in artifact_checks) and sum(len(a['read_paths']) for a in artifact_checks)==10,artifact_checks)
    c=d['candidate'];f=ROOT/c['local_path'];text=BeautifulSoup(f.read_text(encoding='utf-8-sig'),'html.parser').get_text(' ',strip=True)
    check('新增履历hash专业模块与去联系字段',hashlib.sha256(f.read_bytes()).hexdigest()==c['redacted_sha256'] and all(x in text for x in c['professional_modules']) and not re.search(r'[\w.+%-]+@[\w.-]+\.[A-Za-z]{2,}|(?<!\d)1[3-9]\d{9}(?!\d)',text))
    check('3核心6总履历附件分列',sum(r.get('complete_redacted_cv_file_received',False) for r in cv)==3 and len(load('履历脱敏副本目录.json')['records'])==3)
    paths={'03_简历与候选人案例/候选人证据链对照.csv':28,'04_面经与专业观点/面经统一分类.csv':74,'06_项目分析与推荐/项目统一比较.csv':315,'08_证据索引与统计/全部资料统一分类.csv':176,'08_证据索引与统计/能力要求四类证据对照.csv':11,'03_简历与候选人案例/履历文件索引.csv':6}
    for name,n in paths.items():
        with (ROOT/name).open(encoding='utf-8-sig',newline='') as f:count=len(list(csv.reader(f)))-1
        check('CSV '+name,count==n,count)
    cache={}
    def page(p):
        if p not in cache:
            sp=BeautifulSoup(p.read_text(encoding='utf-8-sig'),'html.parser');cache[p]=(sp,{x['id'] for x in sp.select('[id]')}|{x['name'] for x in sp.select('a[name]')})
        return cache[p]
    broken=[];nlinks=0
    for p in REPORT.glob('*.html'):
        sp,_=page(p.resolve())
        for a in sp.select('a[href]'):
            u=urlsplit(a['href'])
            if u.scheme or u.netloc:continue
            target=(p.parent/unquote(u.path)).resolve() if u.path else p.resolve();nlinks+=1
            if not target.exists():broken.append({'file':p.name,'href':a['href'],'issue':'missing file'})
            elif u.fragment and target.suffix.lower()=='.html' and unquote(u.fragment) not in page(target)[1]:broken.append({'file':p.name,'href':a['href'],'issue':'missing anchor'})
    check('所有报告本地链接与锚点',not broken,{'count':nlinks,'broken':broken})
    doc=fitz.open(REPORT/'需求核对与阅读优先级.pdf');texts=[p.get_text() for p in doc];full='\n'.join(texts)
    check('PDF无空白或孤立页',all(len(t.strip())>150 for t in texts),{'pages':len(doc),'characters':[len(t) for t in texts]})
    check('PDF覆盖新履历项目面经观点',all(i in full for i in ['CV28','PRO20','PRO21','INT81','INT78','INT79','INT80','OP13']))
    check('PDF无横向文本裁切',all(all(b[0]>=0 and b[2]<=p.rect.width+1 for b in p.get_text('blocks')) for p in doc))
    browser=load('持续补证浏览器校验.json');check('实际浏览器检查通过',not browser['errors'] and all(c['passed'] for c in browser['checks']),len(browser['checks']))
    check('目标仍active且未用归档代替研究完成',progress['status']=='active' and len(progress['remaining_gaps'])>=3 and load('目标执行统计.json')['current_totals']==s['totals'])
    result={'passed':all(c['passed'] for c in checks),'scope':'持续补证交付一致性，不证明整体目标完成','checks':checks,'local_links':nlinks,'pdf_pages':len(doc),'goal_status':'active','remaining_gaps':s['remaining_gaps'],'visual_review':'待根代理目视本轮PDF首中末页'}
    (BASE/'持续补证交付校验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'passed':result['passed'],'checks':len(checks),'local_links':nlinks,'pdf_pages':len(doc),'failures':[c for c in checks if not c['passed']]},ensure_ascii=False,indent=2))
    return 0 if result['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
