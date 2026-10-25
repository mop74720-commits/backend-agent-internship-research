"""核对交付资料、源文件、链接及PDF，不验证第三方项目运行效果。"""
from pathlib import Path
from collections import Counter
from urllib.parse import urlsplit,unquote
import csv
import hashlib
import json
import fitz
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'08_证据索引与统计'
REPORT=ROOT/'01_调研报告'
result={'scope':'本地交付完整性与统计一致性；未运行被调研项目','checks':[]}
def load(name):return json.loads((BASE/name).read_text(encoding='utf-8-sig'))
def check(name,ok,details=None):
 result['checks'].append({'name':name,'passed':bool(ok),'details':details})

def main():
 errors=[];json_count=0
 for p in ROOT.rglob('*.json'):
  try:json.loads(p.read_text(encoding='utf-8-sig'));json_count+=1
  except Exception as e:errors.append({'path':str(p.relative_to(ROOT)),'error':str(e)})
 check('全部本地JSON可解析',not errors,{'count':json_count,'errors':errors})
 records=load('all_evidence_records.json');by={x['id']:x for x in records};stats=load('需求覆盖统计.json')
 interviews=load('interview_records.json');cases=load('candidate_cases.json')['cases'];projects=load('project_recommendations.json')['projects']
 check('146唯一资料且分类完整',len(records)==len(by)==146 and all(all(k in x for k in ['taxonomy','reading','outcomes']) for x in records))
 check('主表与146目录逐项一致',all(x==by[x['id']] for x in cases+interviews+projects))
 check('21候选人四段关系完整',len(cases)==21 and all(set(x['chain'])=={'outcome','profile','project','interview'} for x in cases))
 strict=[x['id'] for x in interviews if x.get('strict_recent_internship')]
 aux=[x['id'] for x in interviews if x.get('publication_recent_event_year_unknown')]
 check('严格近期8按事件年且明确实习',strict==stats['interview_coverage']['strict_recent_explicit_internship_ids'] and len(strict)==8 and all(by[i]['taxonomy']['recruitment']=='实习' and by[i]['taxonomy']['recent_status']=='近期确认' and by[i]['taxonomy']['year_confirmed'] for i in strict),strict)
 check('发表近期辅助9不混入严格组',len(aux)==9 and not set(aux)&set(strict),aux)
 check('63面经阅读57全文6部分',len(interviews)==63 and Counter(x['reading']['scope'] for x in interviews)=={'全文':57,'部分':6})
 check('未知批次不计明确实习',sum(x['taxonomy']['recruitment']=='实习' for x in interviews)==40 and sum(x['taxonomy']['recruitment']=='实习' and x['taxonomy']['recent_status']=='年份未知' for x in interviews)==31)
 check('OC意向不升级正式offer',by['INT09']['result_status']=='intention_self_report')
 check('真实简历0和原平台正文0保留',stats['candidate_coverage']['complete_cv_files_received']==0 and stats['opinion_coverage']['actual_video_watched_count']==0 and stats['opinion_coverage']['primary_bilibili_or_zhihu_full_content_verified_count']==0)
 comp=load('项目统一比较与阅读优先级.json');dims=[v for p in comp['projects'] for group in ['backend_dimensions','agent_dimensions'] for v in p[group].values()]
 check('19项目285维均有状态依据范围',len(comp['projects'])==19 and len(dims)==285 and all(all(k in v for k in ['status','source_URL','read_paths','read_scope','finding']) for v in dims))
 manifest=json.loads((ROOT/'05_项目源码归档/SOURCE_MANIFEST.json').read_text(encoding='utf-8-sig'));archive_errors=[]
 for m in manifest:
  f=ROOT/'05_项目源码归档'/m['archive_file']
  if not f.exists() or f.stat().st_size!=m['archive_bytes'] or hashlib.sha256(f.read_bytes()).hexdigest()!=m['archive_sha256']:archive_errors.append(m['archive_file'])
 check('16源码ZIP大小与SHA256一致',len(manifest)==16 and not archive_errors,archive_errors)
 check('三份只保留链接且全部未运行',comp['counts']['fixed_link_only']==3 and comp['counts']['executed_projects']==0 and all(not p['attachment']['runtime_verified'] for p in comp['projects']))
 counts={}
 for name,expected in [('03_简历与候选人案例/候选人证据链对照.csv',21),('04_面经与专业观点/面经统一分类.csv',63),('06_项目分析与推荐/19项目统一比较.csv',285),('08_证据索引与统计/能力要求四类证据对照.csv',11),('08_证据索引与统计/全部资料统一分类.csv',146)]:
  with (ROOT/name).open(encoding='utf-8-sig',newline='') as f:counts[name]=len(list(csv.reader(f)))-1
  check('CSV行数：'+name,counts[name]==expected,counts[name])
 cache={}
 def parsed(p):
  if p not in cache:
   soup=BeautifulSoup(p.read_text(encoding='utf-8-sig'),'html.parser')
   cache[p]=(soup,{a.get('id') for a in soup.select('[id]')}|{a.get('name') for a in soup.select('a[name]')})
  return cache[p]
 broken=[];links=0
 for p in REPORT.glob('*.html'):
  soup,ids=parsed(p.resolve())
  for a in soup.select('a[href]'):
   href=a['href'];u=urlsplit(href)
   if u.scheme or u.netloc:continue
   target=(p.parent/unquote(u.path)).resolve() if u.path else p.resolve();links+=1
   if not target.exists():broken.append({'page':p.name,'href':href,'issue':'missing file'})
   elif u.fragment and target.suffix.lower()=='.html' and unquote(u.fragment) not in parsed(target)[1]:broken.append({'page':p.name,'href':href,'issue':'missing anchor'})
 check('全部HTML本地链接与锚点',not broken,{'checked':links,'broken':broken})
 s,ids=parsed((REPORT/'index.html').resolve())
 check('首页19项目与32手动入口数量一致',len(s.select('.project-detail'))==19 and len(load('待手动访问链接.json'))==stats['totals']['manual_links']==32)
 manual,_=parsed((REPORT/'待手动访问链接.html').resolve());check('32待核JSON与HTML同量',len(manual.select('.manual-card'))==32)
 pdf=fitz.open(REPORT/'需求核对与阅读优先级.pdf');texts=[p.get_text() for p in pdf];text='\n'.join(texts)
 check('PDF无空白页',all(len(t.strip())>150 for t in texts),{'pages':len(pdf),'characters':[len(t) for t in texts]})
 check('PDF覆盖21候选人与19项目',all(x['id'] in text for x in cases+projects))
 check('PDF正文包含核心统计与缺口',all(x in text for x in ['近期','完整CV','57','63','285','知乎','暂缓']))
 overflow=[]
 for i,p in enumerate(pdf):
  for b in p.get_text('blocks'):
   if b[0]<0 or b[2]>p.rect.width+1:overflow.append(i+1)
 check('PDF文本块无水平剪裁',not overflow,overflow)
 browser=load('需求纠偏浏览器校验.json');check('浏览器检查均通过',all(x['passed'] for x in browser['checks']) and not browser['errors'],len(browser['checks']))
 result.update({'passed':all(x['passed'] for x in result['checks']),'pdf_pages':len(pdf),'json_files_parsed':json_count,'csv_rows':counts,'local_links_checked':links,'remaining_gaps':stats['remaining_gaps'],'visual_review':'首、中、末页另行目视；不以脚本代替版面核对'})
 (BASE/'需求纠偏交付校验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(result,ensure_ascii=False,indent=2))
 return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
