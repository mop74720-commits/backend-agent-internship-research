import json,hashlib,datetime,re
from pathlib import Path
import fitz
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent; INDEX=ROOT/'08_证据索引与统计'; OUT=ROOT/'03_简历与候选人案例/公开简历原件'
IDS=['CV02','CV05','CV10','CV11','CV12','CV13','CV14','CV15','CV16','CV18','CV19','CV20']
data=json.loads((INDEX/'all_evidence_records.json').read_text(encoding='utf-8')); byid={x['id']:x for x in data if x.get('id') in IDS}
cached=[]
for f in ['公开简历复核_GitHub_采集缓存.json','公开简历复核_GitHub_跟进缓存.json','公开简历复核_GitHub_附件缓存.json','公开简历复核_GitHub_最后跟进缓存.json']:
 cached+=json.loads((INDEX/f).read_text(encoding='utf-8'))
notes={
 'CV02':('已取得作者仓库公开图片；本人投递版关系未完全核定','README把4张PNG放在“简历可以参考如下写法”下；JPG含拼多多实习和本人wxy-rpc项目URL。不能将参考写法直接认证为作者实际SSP投递版，5图也不等于5份简历。PNG中的像素打码来自作者，文件保持原样。'),
 'CV05':('已取得作者公开DOCX及本地PDF导出','profile README明确给出新简历链接，但新网页404。本人profile仓库公开presonal/resume.docx，内容为后端求职、网易/百度实习和GSoC经历，原稿含作者自行匿名占位字段。保留作者原DOCX；PDF是Word排版导出，不是作者原PDF，不能推定为2023正式投递版或2026 Agent最新稿。'),
 'CV10':('本轮未取得本人PNG/PDF','原牛客URL返回200但当前请求仅页面框架；本人博客仓库about页与公开仓库列表未见明确本人CV原件。CalvinNeo/resume是billryan/resume模板fork，只有模板TEX，未认成本人简历。未据此断言作者从未公开。'),
 'CV11':('本轮未取得本人PNG/PDF','原牛客URL返回200但当前请求仅页面框架；本人WebServer README/完整树及公开仓库列表未找到明确本人简历文件。库中datum PNG是项目架构/测试图，不是简历。'),
 'CV12':('本轮未取得本人PNG/PDF','已读interview README、递归树与本人公开仓库列表。树中大量PDF是课程讲义和教材，未发现明确本人CV文件；不把教材PDF当简历。'),
 'CV13':('已取得作者主页直链的公开PDF','本人dong03.github.io主页同时直链Chengbo_Dong_CV.pdf及CV_Interview；PDF姓名/研究方向与主页一致。2页研究CV为算法对照材料，不是后端/Agent工程实习成功投递稿认证，也不直接证明SSP档位。'),
 'CV14':('本轮未取得本人PNG/PDF','已查Java-Gold README和02-resume/README、完整树、本人博客about页和公开仓库列表。02-resume是写法说明，README的“简历模板”链接为空；2019-campus PDF是面经/知识总结，不是简历。'),
 'CV15':('公开HTML履历可读；另有浏览器截图及PDF导出','2018复盘原文直接称“个人简历”并链接本人站。https://cyc2018.github.io/和/page.html均200，站点仓库无明确作者原PNG/PDF。额外PNG和PDF忠实通过浏览器保存实际网页，不是作者原始附件，不证明为每次投递使用版。'),
 'CV16':('本轮未取得本人PNG/PDF','已查Preparation-For-OFFER全文和完整树、本人公开仓库列表；面经提到简历项目，但未发现原简历附件/本人履历下载链接。算法邻近样本不补写为工程候选人。'),
 'CV18':('已从历史提交取得本人公开PDF','2019秋招总结直接链接AboutMe/苏畅的简历.pdf；当前master404。通过该文件提交历史取得2019-08-24 fb1366f1版本1页PDF，与既有同commit TEX一致、含reimu/async项目。另保存2022-03-10更新版，分别标日期；不能把2022版倒推为2019投递稿。'),
 'CV19':('本轮未取得本人PNG/PDF','已核当前本人介绍页及liyupi profile、yupi-skill公开仓库树。简历产品/教程入口不是本人求职原件，不能以其代替作者简历；本人当年求职原件仍待可核公开链接。'),
 'CV20':('本轮未取得来稿作者PNG/PDF','已查署名鬼卞的完整来稿与收录仓库树/文内全部图片上下文。正文图片标注西班牙/广州/广州微信，为生活和实习照片；无原简历下载。puge-up是收录者，不能当鬼卞本人账号，未以收录者材料冒充作者简历。')
}
results=[]
for cid in IDS:
 attempts=[];assets=[];seen=set()
 for x in cached:
  if x.get('candidate_id')!=cid:continue
  u=x.get('url','');kind=x.get('kind','')
  if (u,kind) not in seen:
   attempts.append({'pathway':kind,'url':u,'http_status':x.get('http_status',x.get('status')),'content_type':x.get('content_type','')});seen.add((u,kind))
  if x.get('local_file') and (ROOT/x['local_file']).exists():
   a={k:v for k,v in x.items() if k not in ['data','body','kind','candidate_id']};a['asset_kind']='作者公开原件';a['additional_redaction']=False;assets.append(a)
 for file,source,kind in [
  ('CV05_erdengk_作者公开DOCX_排版导出.pdf','https://raw.githubusercontent.com/erdengk/erdengk/HEAD/presonal/resume.docx','作者DOCX的Word排版导出'),
  ('CV15_CyC2018_作者网页履历_浏览器截图.png','https://cyc2018.github.io/page.html','作者实际网页的浏览器截图'),
  ('CV15_CyC2018_作者网页履历_浏览器导出.pdf','https://cyc2018.github.io/page.html','作者实际网页的浏览器PDF导出')]:
  p=OUT/file
  if file.startswith(cid+'_') and p.exists():
   a={'local_file':p.relative_to(ROOT).as_posix(),'url':source,'source_http_status':200,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'asset_kind':kind,'additional_redaction':False,'not_author_original_format':True}
   if p.suffix=='.pdf':a['pages']=len(fitz.open(p))
   if p.suffix=='.png':a['image_size']=list(Image.open(p).size)
   assets.append(a)
 status,limit=notes[cid]
 results.append({'candidate_id':cid,'title':byid[cid]['title'],'source_article_url':byid[cid]['url'],'status':status,'checked_at':'2026-10-24','attempts':attempts,'assets':assets,'identity_and_version_boundary':limit,'outcome_boundary':'录用档位、岗位、年份仍沿用既有逐条证据；取得简历附件本身不新增或提升offer档位证据。','resume_web_url':'https://cyc2018.github.io/page.html' if cid=='CV15' else ''})
o={'scope':'12位既有GitHub/博客候选人的公开原简历复核；按用户要求不再额外脱敏，不还原作者原有打码','checked_at':'2026-10-24','method':'原文/README内附件→本人仓库树与主页或文件提交历史；只下载明确公开资料。未找到仅表示本轮已查范围未取得，不代表全网没有。','candidates':results,'counts':{'candidate_n':12,'author_original_pdf_candidates':2,'author_original_pdf_files':3,'author_public_docx_candidates':1,'reference_image_candidate':1,'reference_image_files':5,'html_resume_candidate':1,'not_obtained_candidate_n':7},'limits':['CV02图片属原仓库简历参考写法/专业片段，关系未认证成正式投递版。','CV13研究CV作算法对照。','CV05作者原DOCX自带匿名占位，本次不改；派生PDF明确标导出。','CV18提供2019和2022两版，主精读应选2019版。','CV15实际HTML截屏/打印不是作者原PNG/PDF。']}
(INDEX/'公开简历复核_GitHub.json').write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':'公开简历复核_GitHub.json','counts':o['counts'],'asset_paths':[a['local_file'] for r in results for a in r['assets']]},ensure_ascii=False,indent=2))
