import concurrent.futures, json, re, urllib.parse, requests
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
INDEX=ROOT/'08_证据索引与统计'
def fetch(url):
 try:
  r=requests.get(url,headers={'User-Agent':'ResearchResumeVerification/1.0'},timeout=30)
  return {'url':url,'status':r.status_code,'content_type':r.headers.get('content-type',''),'final_url':r.url,'body':r.text}
 except Exception as e:return {'url':url,'status':'error','error':str(e)}
urls=[
 ('CV05','profile_readme','https://raw.githubusercontent.com/erdengk/erdengk/HEAD/README.md'),
 ('CV05','resume_page','https://erdengk.github.io/cv/'),
 ('CV10','about','https://raw.githubusercontent.com/CalvinNeo/CalvinNeo.github.io/HEAD/about/index.html'),
 ('CV15','resume_page','https://cyc2018.github.io/page.html'),
 ('CV15','resume_home','https://cyc2018.github.io/'),
 ('CV18','pdf_current','https://raw.githubusercontent.com/IcyCC/AboutMe/master/'+urllib.parse.quote('苏畅的简历.pdf')),
 ('CV18','pdf_history','https://api.github.com/repos/IcyCC/AboutMe/commits?path='+urllib.parse.quote('苏畅的简历.pdf')+'&per_page=100'),
 ('CV14','resume_guidance','https://raw.githubusercontent.com/mio4/Java-Gold/HEAD/02-resume/README.md'),
]
for cid,user in [('CV10','CalvinNeo'),('CV11','linyacool'),('CV12','muluoleiguo'),('CV13','dong03'),('CV14','mio4'),('CV16','LittleChild')]:
 urls.append((cid,'repositories','https://api.github.com/users/'+user+'/repos?per_page=100'))
out=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
 for (cid,kind,url),r in zip(urls,ex.map(lambda t:fetch(t[2]),urls)):
  out.append({'candidate_id':cid,'kind':kind,**r})
  body=r.get('body','')
  if kind=='repositories' and r.get('status')==200:
   j=json.loads(body);print(cid,kind,[(x['name'],x.get('homepage')) for x in j])
  elif kind=='pdf_history' and r.get('status')==200:
   print(cid,kind,json.dumps([{'sha':x['sha'],'msg':x['commit']['message']} for x in json.loads(body)],ensure_ascii=False))
  else:
   print(cid,kind,r.get('status'),json.dumps([x[:500] for x in body.splitlines() if re.search(r'(?i)简历|resume|\.pdf|github.io|自我|教育',x)][:12],ensure_ascii=False))
(INDEX/'公开简历复核_GitHub_跟进缓存.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
