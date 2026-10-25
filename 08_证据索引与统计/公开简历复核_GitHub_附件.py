import requests, json, concurrent.futures, urllib.parse, hashlib, io, zipfile, re
from pathlib import Path
from PIL import Image
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent.parent; INDEX=ROOT/'08_证据索引与统计'; OUT=ROOT/'03_简历与候选人案例/公开简历原件'; OUT.mkdir(exist_ok=True)
tasks=[]
for name in ['简历.png','简历0.png','简历1.png','简历2.png','简历图片.jpg']:
 tasks.append(('CV02','asset','https://raw.githubusercontent.com/viego1999/JavaWxy/master/asset/'+urllib.parse.quote(name),'CV02_JavaWxy_'+name))
tasks += [('CV05','asset','https://raw.githubusercontent.com/erdengk/erdengk/HEAD/presonal/resume.docx','CV05_erdengk_作者公开简历原稿.docx'),
 ('CV18','asset','https://raw.githubusercontent.com/IcyCC/AboutMe/83a1a3bf881a5089002a7eea24d14e5ef34b2f51/'+urllib.parse.quote('苏畅的简历.pdf'),'CV18_IcyCC_2019历史公开简历原件.pdf'),
 ('CV18','asset','https://raw.githubusercontent.com/IcyCC/AboutMe/fb1366f1dbe5bfa6b1490eef0a30e6f8253568fe/'+urllib.parse.quote('苏畅的简历.tex'),'CV18_IcyCC_历史简历作者原稿.tex')]
for cid,repo in [('CV10','CalvinNeo/resume'),('CV13','dong03/dong03.github.io'),('CV14','mio4/mio4.github.io')]:
 tasks.append((cid,'tree','https://api.github.com/repos/'+repo+'/git/trees/HEAD?recursive=1',None))
 tasks.append((cid,'metadata','https://api.github.com/repos/'+repo,None))
out=[]
def job(t):
 cid,kind,url,name=t
 try:
  r=requests.get(url,headers={'User-Agent':'ResearchResumeVerification/1.0'},timeout=35)
  record={'candidate_id':cid,'kind':kind,'url':url,'http_status':r.status_code,'content_type':r.headers.get('content-type',''),'bytes':len(r.content)}
  if kind=='asset' and r.status_code==200:
   (OUT/name).write_bytes(r.content); record.update(local_file=(OUT/name).relative_to(ROOT).as_posix(),sha256=hashlib.sha256(r.content).hexdigest())
   if name.endswith(('.png','.jpg')):
    im=Image.open(io.BytesIO(r.content));record['image_size']=list(im.size)
   if name.endswith('.pdf'):
    import fitz
    d=fitz.open(stream=r.content,filetype='pdf');record['pages']=len(d)
   if name.endswith('.docx'):
    z=zipfile.ZipFile(io.BytesIO(r.content));txt=BeautifulSoup(z.read('word/document.xml'),'xml').get_text(' ')
    record['professional_keywords']=[w for w in ['沈阳','大学','ShenYu','Apache','SSP','Agent','2022','2023','2024','2025','GSoC','限流','测试','实习'] if w.lower() in txt.lower()]
  elif kind in ['tree','metadata'] and r.status_code==200:
   j=r.json();record['data']=j
  return record
 except Exception as e:return {'candidate_id':cid,'url':url,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
 for r in ex.map(job,tasks):
  out.append(r)
  safe={k:v for k,v in r.items() if k!='data'}
  if r.get('kind')=='tree':safe['matching_paths']=[x['path'] for x in r.get('data',{}).get('tree',[]) if re.search(r'(?i)resume|简历|\.pdf$|cv|about',x['path'])][:50]
  if r.get('kind')=='metadata':safe['fork']=r.get('data',{}).get('fork');safe['description']=r.get('data',{}).get('description');safe['parent']=r.get('data',{}).get('parent',{}).get('full_name')
  print(json.dumps(safe,ensure_ascii=False))
(INDEX/'公开简历复核_GitHub_附件缓存.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
