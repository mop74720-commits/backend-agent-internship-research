"""验证补证交付的来源关系、脱敏附件、分类和页面；不证明整体目标已完成。"""
from pathlib import Path
from urllib.parse import urlsplit,unquote
from collections import Counter
import csv,hashlib,json,re
import fitz
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent.parent;BASE=ROOT/'08_证据索引与统计';REPORT=ROOT/'01_调研报告'
def load(n):return json.loads((BASE/n).read_text(encoding='utf-8-sig'))
def main():
    checks=[]
    def check(n,v,detail=None):checks.append({'name':n,'passed':bool(v),'detail':detail})
    bad=[];json_count=0
    for p in ROOT.rglob('*.json'):
        try:json.loads(p.read_text(encoding='utf-8-sig'));json_count+=1
        except Exception as e:bad.append({'file':str(p.relative_to(ROOT)),'error':str(e)})
    check('全部JSON可解析',not bad,{'count':json_count,'errors':bad})
    rows=load('all_evidence_records.json');by={r['id']:r for r in rows};s=load('需求覆盖统计.json');progress=load('目标执行统计.json')
    cv=load('candidate_cases.json')['cases'];iv=load('interview_records.json');projects=load('project_recommendations.json')['projects']
    check('168唯一且22项增量可追溯',len(rows)==len(by)==168 and len(progress['new_record_ids'])==22 and all(i in by for i in progress['new_record_ids']))
    check('新来源不是空摘要',all(by[i]['reading']['fulltext'] for i in progress['new_record_ids']))
    check('主表与目录逐项一致',all(r==by[r['id']] for r in cv+iv+projects))
    check('27四段关联且方向分列',len(cv)==27 and all(set(r['chain'])=={'outcome','profile','project','interview'} for r in cv))
    check('70份阅读64全文6部分',len(iv)==70 and Counter(r['reading']['scope'] for r in iv)=={'全文':64,'部分':6})
    check('新增7份均有本人归属',all(by[i]['candidate_link_ids'] for i in ['INT71','INT72','INT73','INT74','INT75','INT76','INT77']))
    strict=[r['id'] for r in iv if r.get('strict_recent_internship')]
    check('严格近期9不借发表年',len(strict)==9 and 'INT77' in strict and all(by[i]['taxonomy']['year_confirmed'] and by[i]['taxonomy']['recruitment']=='实习' for i in strict) and all(not by[f'INT{i}']['strict_recent_internship'] for i in range(71,77)),strict)
    aux=[r['id'] for r in iv if r.get('publication_recent_event_year_unknown')]
    check('辅助11不混入严格组',len(aux)==11 and set(aux).isdisjoint(strict) and {'INT71','INT73'}<=set(aux))
    check('未知事件年不混明确近期',sum(r['taxonomy']['recruitment']=='实习' for r in iv)==47 and sum(r['taxonomy']['recruitment']=='实习' and r['taxonomy']['recent_status']=='年份未知' for r in iv)==37)
    check('分母说明随70更新','70份' in s['interview_coverage']['denominator_note'] and '63份' not in s['interview_coverage']['denominator_note'])
    check('INT77仅阿里云为offer',by['INT77']['outcomes'][0]['company']=='阿里云' and by['CV27']['outcomes'][0]['date'].startswith('2025'))
    check('CV25各事实使用各直接源',any('917095780249309184' in n['url'] for n in by['CV25']['chain']['outcome']) and any('876046266558398464' in n['url'] for n in by['CV25']['chain']['profile']))
    check('CV26失败和OC不串offer汇总',all('e319aadc' in o['evidence_url'] for o in by['CV26']['outcomes'] if o['company'] in ['小红书','百度']) and all('14b2c379' in o['evidence_url'] for o in by['CV26']['outcomes'] if o['company']=='深信服'))
    check('核心新样本未被升级SSP，匿名自述单列',progress['new_ssp_direct_evidence']==0 and progress['new_agent_ssp_claims_pending']==1 and s['recent_agent_ssp_complete_chain_confirmed']==0 and all(not by[f'CV{i}']['ssp_claim_present'] for i in range(22,28)) and by['OBS09']['outcomes'][0]['status']=='broad_ssp_claim_pending')
    check('原平台3与视频0',s['opinion_coverage']['primary_bilibili_or_zhihu_full_content_verified_count']==3 and s['opinion_coverage']['bilibili_native_articles_read']==1 and s['opinion_coverage']['zhihu_native_fulltexts_read']==2 and s['opinion_coverage']['actual_video_watched_count']==0)
    check('DOC11文档时间不是SHA',by['DOC11']['taxonomy']['source_date_text']=='2026-06-15T06:03:59Z' and by['DOC11']['source_record']['state']=='文档宣称，无法源码核对')
    discovery=load('目标执行_近期履历发现.json');files=[];errors=[]
    pdf_inputs=discovery['complete_redacted_comparison_cvs']+discovery['new_core_complete_pdf_profiles']
    for r in pdf_inputs:
        p=ROOT/r['local_path'];pdf=fitz.open(p);text='\n'.join(p.get_text() for p in pdf)
        valid=hashlib.sha256(p.read_bytes()).hexdigest()==r['redacted_sha256'] and not re.search(r'[\w.+%-]+@[\w.-]+\.[A-Za-z]{2,}|(?<!\d)1[3-9]\d{9}(?!\d)',text)
        valid=valid and not any(p.get_links() or list(p.annots() or []) or p.get_images() for p in pdf)
        valid=valid and not any(v for k,v in pdf.metadata.items() if k not in ['format','encryption']) and not pdf.get_xml_metadata()
        files.append({'file':r['local_path'],'pages':len(pdf),'passed':bool(valid),'professional_body_unchanged_reported':r['redaction']['professional_body_text_identical_after_header_removal']})
    for r in discovery['new_core_complete_profiles']:
        p=ROOT/r['local_html'];text=BeautifulSoup(p.read_text(encoding='utf-8-sig'),'html.parser').get_text(' ',strip=True)
        valid=hashlib.sha256(p.read_bytes()).hexdigest()==r['redacted_html_sha256'] and not re.search(r'[\w.+%-]+@[\w.-]+\.[A-Za-z]{2,}|(?<!\d)1[3-9]\d{9}(?!\d)',text)
        files.append({'file':r['local_html'],'passed':bool(valid),'modules':r['all_original_professional_modules_preserved']})
    check('2核心3对照附件安全与hash',len(files)==5 and all(f['passed'] for f in files),files)
    check('完整专业副本2与研究对照3不混计',sum(r.get('complete_redacted_cv_file_received',False) for r in cv)==2 and len([r for r in rows if r['category']=='履历对照材料'])==3)
    paths={'03_简历与候选人案例/候选人证据链对照.csv':27,'04_面经与专业观点/面经统一分类.csv':70,'06_项目分析与推荐/19项目统一比较.csv':285,'08_证据索引与统计/全部资料统一分类.csv':168,'08_证据索引与统计/能力要求四类证据对照.csv':11,'03_简历与候选人案例/履历文件索引.csv':5}
    for name,n in paths.items():
        with (ROOT/name).open(encoding='utf-8-sig',newline='') as f:count=len(list(csv.reader(f)))-1
        check('CSV行数 '+name,count==n,count)
    cache={}
    def page(p):
        if p not in cache:
            sp=BeautifulSoup(p.read_text(encoding='utf-8-sig'),'html.parser');cache[p]=(sp,{x['id'] for x in sp.select('[id]')}|{x['name'] for x in sp.select('a[name]')})
        return cache[p]
    broken=[];nlinks=0
    for p in REPORT.glob('*.html'):
        sp,ids=page(p.resolve())
        for a in sp.select('a[href]'):
            u=urlsplit(a['href'])
            if u.scheme or u.netloc:continue
            target=(p.parent/unquote(u.path)).resolve() if u.path else p.resolve();nlinks+=1
            if not target.exists():broken.append({'file':p.name,'href':a['href'],'issue':'missing file'})
            elif u.fragment and target.suffix.lower()=='.html' and unquote(u.fragment) not in page(target)[1]:broken.append({'file':p.name,'href':a['href'],'issue':'missing anchor'})
    check('全部报告本地链接与锚点',not broken,{'checked':nlinks,'broken':broken})
    m=(BASE/'source_methodology.txt').read_text(encoding='utf-8-sig').split('以下为前轮历史方法说明')[0]
    check('方法说明最新统计正确','168' in m and '70' in m and '知乎正文2' in m and '知乎本体正文0' not in m)
    doc=fitz.open(REPORT/'需求核对与阅读优先级.pdf');texts=[p.get_text() for p in doc];full='\n'.join(texts)
    check('报告PDF无空白或孤立页',all(len(t.strip())>150 for t in texts),{'pages':len(doc),'characters':[len(t) for t in texts]})
    check('PDF覆盖新增核心履历和原平台材料',all(x in full for x in ['CV23','CV24','OP10','OP11','OP12','INT74','DOC11']))
    check('PDF无横向文字裁切',all(all(b[0]>=0 and b[2]<=p.rect.width+1 for b in p.get_text('blocks')) for p in doc))
    browser=load('目标执行浏览器校验.json');check('浏览器交互均通过',not browser['errors'] and all(c['passed'] for c in browser['checks']),len(browser['checks']))
    check('目标没有因交付验证被缩小或标完成',progress['status']=='active' and bool(progress['remaining_gaps']))
    result={'scope':'本轮交付验证；不是六项目标完成证明','passed':all(c['passed'] for c in checks),'checks':checks,'pdf_pages':len(doc),'local_links':nlinks,'remaining_gaps':s['remaining_gaps'],'goal_status':'active','visual_review':'待根代理目视本轮PDF首/中/末页'}
    (BASE/'目标执行交付校验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'passed':result['passed'],'pdf_pages':len(doc),'links':nlinks,'checks':len(checks),'failures':[c for c in checks if not c['passed']]},ensure_ascii=False,indent=2))
    return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
