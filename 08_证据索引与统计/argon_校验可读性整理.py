"""检查新阅读入口、本地链接、附件、原始来源指纹与PDF。"""
from pathlib import Path
from urllib.parse import urlsplit,unquote
from bs4 import BeautifulSoup
import json,hashlib,re
import fitz

ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'08_证据索引与统计'


def main():
    errors=[]; checks=0; anchors={}; files=0
    def check(ok,desc):
        nonlocal checks
        checks+=1
        if not ok:errors.append(desc)
    for p in ROOT.rglob('*.html'):
        if p.relative_to(ROOT).parts[0] in ['05_项目源码归档','07_个人项目设计_暂缓']:continue
        files+=1
        soup=BeautifulSoup(p.read_text(encoding='utf-8-sig'),'html.parser')
        for element in soup.find_all(['a','img','iframe','source']):
            url=element.get('href') if element.name=='a' else element.get('src')
            if not url:continue
            u=urlsplit(url)
            if u.scheme or u.netloc:continue
            target=(p.parent/unquote(u.path)).resolve() if u.path else p.resolve()
            if not target.is_relative_to(ROOT.resolve()):continue
            desc=f'{p.relative_to(ROOT).as_posix()} → {url}'
            check(target.exists(),desc)
            if target.exists() and target.suffix=='.html' and u.fragment:
                if target not in anchors:
                    doc=BeautifulSoup(target.read_text(encoding='utf-8-sig'),'html.parser')
                    anchors[target]={el['id'] for el in doc.select('[id]')}|{el['name'] for el in doc.select('[name]')}
                check(unquote(u.fragment) in anchors[target],desc+' [锚点]')
    for p in ROOT.rglob('*.md'):
        if p.relative_to(ROOT).parts[0] in ['05_项目源码归档','07_个人项目设计_暂缓']:continue
        for url in re.findall(r'\]\(([^\s)]+)\)',p.read_text(encoding='utf-8-sig')):
            u=urlsplit(url)
            if u.scheme or u.netloc:continue
            target=(p.parent/unquote(u.path)).resolve() if u.path else p.resolve()
            if not target.is_relative_to(ROOT.resolve()):continue
            check(target.exists(),f'{p.relative_to(ROOT).as_posix()} → {url} [Markdown]')
    archive=json.loads((BASE/'可读性整理_路径映射.json').read_text(encoding='utf-8-sig'))
    check(Path(archive['backup_path']).exists(),'整理前备份缺失')
    for old,new in archive['moves'].items():check((ROOT/new).exists(),'归档文件缺失：'+new)
    # 权威数据不因目录整理变化。
    stats=json.loads((BASE/'需求覆盖统计.json').read_text(encoding='utf-8-sig'))['totals']
    check(stats['logical_evidence_records']==239,'主数据证据数')
    check(stats['candidate_cases']==34,'主数据候选人数')
    check(stats['interview_materials']==99,'主数据面经数')
    check(stats['projects']==25,'主数据项目数')
    source=json.loads((BASE/'astra来源_合并前文件指纹.json').read_text(encoding='utf-8-sig'))
    for entry in source['files']:
        p=Path(source['source_path'])/entry['path']
        check(p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256'],'astra原文件改变：'+entry['path'])
    visuals=json.loads((BASE/'简历视觉材料_整理清单.json').read_text(encoding='utf-8-sig'))
    for asset in visuals['assets']:
        check((ROOT/asset['local_file']).exists(),'缺视觉附件：'+asset['asset_id'])
        for preview in asset.get('preview_files',[]):check((ROOT/preview).exists(),'缺预览：'+preview)
    pdf=ROOT/'01_调研报告/argon_实习求职调研总报告.pdf'
    pages=[]
    if pdf.exists():
        with fitz.open(pdf) as doc:
            for i,page in enumerate(doc):
                text=page.get_text()
                pages.append({'page':i+1,'chars':len(text),'opening':text[:70].replace('\n',' ')})
            check(8<=len(doc)<=12,'PDF页数应为8至12页：'+str(len(doc)))
    else:check(False,'PDF未导出')
    result={'checked_html_files':files,'checks':checks,'errors':errors,'pdf_pages':pages,'source_files_unchanged':len(source['files']),'note':'本地链接/锚点与原始来源文件检查；第三方项目未运行。'}
    (BASE/'argon_可读性整理_交付校验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
