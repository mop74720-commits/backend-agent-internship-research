"""按用户要求保存作者主动公开的原始简历文件，不增加遮盖。"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import csv,hashlib,io,json
import requests
import fitz
from PIL import Image

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
DEST=ROOT/'03_简历与候选人案例/公开简历原件'
PREVIEW=DEST/'预览'
DATE='2026-10-24'


def run():
    DEST.mkdir(exist_ok=True);PREVIEW.mkdir(exist_ok=True)
    old=json.loads((BASE/'简历视觉材料_整理清单.json').read_text(encoding='utf-8-sig'))
    sources=[]
    for a in old['assets']:
        if a['candidate_id'] in ['CV01','CV06','OBS11']:
            sources.append({'candidate_id':a['candidate_id'],'urls':[a['original_url']],
                'source_article_url':a['source_article_url'],'completeness':a['completeness'],
                'previous_original_sha256':a.get('original_sha256')})
    with (ROOT/'03_简历与候选人案例/履历文件索引.csv').open(encoding='utf-8-sig') as f:
        entries=list(csv.DictReader(f))
    by_asset={a['candidate_id']:a for a in old['assets']}
    for row in entries:
        rid=row['资料ID']
        if rid not in ['CV24','CV30','CV31','OBS05','OBS06','OBS07']:continue
        live={'CV31':'https://imyihang.com/api/resume'}.get(rid,by_asset[rid]['original_url'])
        sources.append({'candidate_id':rid,'urls':list(dict.fromkeys([row['固定原始来源'],live])),
            'source_article_url':by_asset[rid]['source_article_url'],'completeness':'完整公开PDF简历'})
    def download(item):
        rid=item['candidate_id'];attempts=[]
        for url in item['urls']:
            try:
                response=requests.get(url,timeout=30,headers={'User-Agent':'Mozilla/5.0'})
                data=response.content
                attempt={'url':url,'status':response.status_code,'final_url':response.url,
                    'content_type':response.headers.get('Content-Type',''),'bytes':len(data)}
                attempts.append(attempt)
                if response.status_code!=200:continue
                if data.startswith(b'%PDF-'):
                    doc=fitz.open(stream=data,filetype='pdf')
                    path=DEST/f'{rid}_作者公开原始简历.pdf'
                    preview=[]
                    for i,page in enumerate(doc):
                        file=PREVIEW/f'{rid}_原件第{i+1}页.png'
                        page.get_pixmap(matrix=fitz.Matrix(1.7,1.7)).save(file)
                        preview.append(file.relative_to(ROOT).as_posix())
                    page_count=len(doc);doc.close();kind='作者公开PDF原件';size=None
                else:
                    try:
                        image=Image.open(io.BytesIO(data));image.load()
                    except Exception:
                        attempt['validation']='不是PDF或图片，未保存';continue
                    suffix={'PNG':'png','JPEG':'jpg','WEBP':'webp'}.get(image.format)
                    if not suffix:
                        attempt['validation']='图片格式未支持，未保存';continue
                    path=DEST/f'{rid}_文章原始简历图.{suffix}'
                    file=PREVIEW/f'{rid}_原图预览.png';image.save(file,format='PNG')
                    preview=[file.relative_to(ROOT).as_posix()];size=list(image.size);page_count=1
                    kind='文章公开原始图片'
                if path.exists() and path.read_bytes()!=data:
                    path=path.with_stem(path.stem+'_本轮'+hashlib.sha256(data).hexdigest()[:8])
                path.write_bytes(data)
                digest=hashlib.sha256(data).hexdigest()
                return {'candidate_id':rid,'status':'已取得公开原件','material_type':kind,
                    'original_url':url,'source_article_url':item['source_article_url'],
                    'local_file':path.relative_to(ROOT).as_posix(),'preview_files':preview,
                    'page_count':page_count,'image_size':size,'sha256':digest,
                    'matches_previously_downloaded_original':digest==item.get('previous_original_sha256') if item.get('previous_original_sha256') else None,
                    'completeness':item['completeness'],'additional_redaction':False,
                    'author_masking_boundary':'保留作者原有内容与遮盖，未尝试恢复作者打码。',
                    'acquired_on':DATE,'attempts':attempts}
            except Exception as exc:
                attempts.append({'url':url,'status':'请求/解析异常','error_type':type(exc).__name__})
        return {'candidate_id':rid,'status':'本轮未重新取得原件','attempts':attempts}
    with ThreadPoolExecutor(max_workers=6) as pool:
        results=list(pool.map(download,sources))
    record={'date':DATE,'authorization':'用户明确要求不用额外脱敏，保存作者公开原件；不恢复作者打码。','results':results}
    (BASE/'公开简历复核_既有附件.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps([{'id':r['candidate_id'],'status':r['status'],'kind':r.get('material_type'),'pages':r.get('page_count')} for r in results],ensure_ascii=False))


if __name__=='__main__':run()
