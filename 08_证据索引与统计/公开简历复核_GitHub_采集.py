import json, re, hashlib, concurrent.futures, urllib.parse, datetime
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parent.parent
INDEX=ROOT/'08_证据索引与统计'
IDS=['CV02','CV05','CV10','CV11','CV12','CV13','CV14','CV15','CV16','CV18','CV19','CV20']
REPOS={'CV02':['viego1999/JavaWxy'],'CV05':['erdengk/erdengk','erdengk/erdengk.github.io'],'CV10':['CalvinNeo/CalvinNeo','CalvinNeo/CalvinNeo.github.io'],'CV11':['linyacool/linyacool','linyacool/WebServer'],'CV12':['muluoleiguo/interview'],'CV13':['dong03/CV_Interview'],'CV14':['mio4/Java-Gold'],'CV15':['CyC2018/CyC2018.github.io'],'CV16':['LittleChild/Preparation-For-OFFER'],'CV18':['IcyCC/AboutMe'],'CV19':['liyupi/liyupi','liyupi/yupi-skill'],'CV20':['puge-up/programming-play']}
data=json.loads((INDEX/'all_evidence_records.json').read_text(encoding='utf-8'))
rows=[x for x in data if x.get('id') in IDS]
headers={'User-Agent':'ResearchResumeVerification/1.0','Accept':'application/vnd.github+json'}
def fetch(url):
 try:
  r=requests.get(url,headers=headers,timeout=30)
  return {'url':url,'status':r.status_code,'content_type':r.headers.get('content-type',''),'final_url':r.url,'body':r.text}
 except Exception as e:return {'url':url,'status':'error','error':str(e)}
def raw(url):
 p=urllib.parse.urlsplit(url); pieces=p.path.strip('/').split('/')
 if p.hostname=='github.com' and len(pieces)>4 and pieces[2]=='blob':return 'https://raw.githubusercontent.com/'+'/'.join(pieces[:2]+pieces[3:])
 return url.split('#')[0]
tasks=[]
for x in rows:
 cid=x['id']; url=raw(x['url']);tasks.append((cid,'original',url))
 for repo in REPOS[cid]:tasks.append((cid,'tree','https://api.github.com/repos/'+repo+'/git/trees/HEAD?recursive=1'))
 # The public account profile is a distinct second path when the source is a guest post.
 user=REPOS[cid][0].split('/')[0]
 tasks.append((cid,'profile','https://github.com/'+user))
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
 for (cid,kind,url),r in zip(tasks,ex.map(lambda t:fetch(t[2]),tasks)):
  item={'candidate_id':cid,'kind':kind,**r};results.append(item)
  if kind=='tree' and r.get('status')==200:
   try:
    j=json.loads(r['body']); paths=[t['path'] for t in j.get('tree',[]) if re.search(r'(?i)resume|curriculum|简历|(^|/)cv[/. _-]|\.pdf$|\.docx?$',t['path'])]
    print(cid,kind,r['status'],'candidates',json.dumps(paths[:30],ensure_ascii=False))
   except:pass
  else:
   body=r.get('body',''); hits=[]
   for line in body.splitlines():
    if re.search(r'(?i)resume|curriculum|简历|\.pdf|\.png|\.jpg|github.io|blog|homepage',line) and len(line)<1800:hits.append(line)
   print(cid,kind,r.get('status'),json.dumps(hits[:14],ensure_ascii=False))
(INDEX/'公开简历复核_GitHub_采集缓存.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
