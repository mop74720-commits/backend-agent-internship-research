"""Collect public resume images in memory, redact before saving, and build a visual atlas.

No original private/contact-bearing image is written to disk. Existing redacted PDFs/HTML
are reused. This script does not edit the canonical research database or source folders.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import re
import subprocess
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

import fitz
import requests
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
DIR = ROOT / '03_简历与候选人案例'
VISUAL = DIR / '简历视觉材料'
PREVIEW = DIR / '简历预览'
MANIFEST = BASE / '简历视觉材料_整理清单.json'
DATE = '2026-10-24'


def rel(path):
    return Path(path).relative_to(ROOT).as_posix()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def dump(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\r\n')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ocr_in_memory(image):
    image = image.copy()
    image.thumbnail((2400, 2400))
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    payload = json.dumps({'image_b64': base64.b64encode(buffer.getvalue()).decode('ascii')}).encode('utf-8')
    result = subprocess.run([
        'C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe', '-NoProfile',
        '-File', str(BASE / '简历视觉材料_OCR.ps1')
    ], input=payload, capture_output=True, timeout=65)
    if result.returncode:
        # Never forward OCR diagnostics containing unfiltered input data.
        raise RuntimeError('Windows OCR failed; no unredacted image was saved')
    return json.loads(result.stdout.decode('utf-8-sig'))


def source_link(record):
    urls = []
    def walk(value):
        if isinstance(value, dict):
            for key, val in value.items():
                if key in ['source_url', 'fixed_pdf_url', 'live_pdf', 'original_pdf_url'] and isinstance(val, str):
                    urls.append(val)
                else:
                    walk(val)
        elif isinstance(value, list):
            for val in value:
                walk(val)
    walk(record.get('source_record', {}))
    return next((u for u in urls if '.pdf' in u.lower()), record.get('url'))


def collect():
    VISUAL.mkdir(exist_ok=True)
    PREVIEW.mkdir(exist_ok=True)
    rows = load(BASE / 'all_evidence_records.json')
    by = {r['id']: r for r in rows}
    assets, attempts = [], []
    image_sources = [
        ('CV01', '字节实习简历片段_原图脱敏.png', by['CV01']['original_fragment_url'], '实习简历片段', 0),
        ('CV06', '实习与开源简历片段_原图脱敏.png', by['CV06']['original_fragment_url'], '实习与开源简历片段', 0),
        ('OBS11', '公开一页简历_内部实习已打码_原图脱敏.png', 'https://uploadfiles.nowcoder.com/images/20250524/94181036_1748059791014/74BF56629CD487C3F0C3E7419A6107E4', '公开一页简历，内部实习模块由作者打码；录用未知', 52),
    ]
    for rid, filename, url, completeness, header in image_sources:
        try:
            response = requests.get(url, timeout=35, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            original_bytes = response.content
            image = Image.open(io.BytesIO(original_bytes)).convert('RGB')
            original_format = Image.open(io.BytesIO(original_bytes)).format
            original_size = image.size
            first = ocr_in_memory(image)
            draw = ImageDraw.Draw(image)
            rectangles = []
            if header:
                rectangles.append((0, 0, image.width, header))
            scale_x = image.width / first['width']
            scale_y = image.height / first['height']
            for box in first.get('mask_rects', []):
                rectangles.append((max(0, int(box['x'] * scale_x) - 4), max(0, int(box['y'] * scale_y) - 3),
                                   min(image.width, int((box['x'] + box['width']) * scale_x) + 5),
                                   min(image.height, int((box['y'] + box['height']) * scale_y) + 4)))
            for rectangle in rectangles:
                draw.rectangle(rectangle, fill='white')
            second = ocr_in_memory(image)
            if second.get('mask_rects'):
                # The safe image can be kept in memory for repair, but not persisted yet.
                raise RuntimeError('contact-pattern OCR remained after redaction; no image saved')
            output = VISUAL / (rid + '_' + filename)
            image.save(output, format='PNG', optimize=True)
            thumb = PREVIEW / (rid + '_缩略图.png')
            thumb_image = image.copy()
            thumb_image.thumbnail((850, 1100))
            thumb_image.save(thumb, format='PNG', optimize=True)
            assets.append({
                'asset_id': rid + '_PNG', 'candidate_id': rid,
                'material_type': '公开原图的脱敏PNG副本', 'completeness': completeness,
                'local_file': rel(output), 'thumbnail_file': rel(thumb), 'preview_files': [rel(output)],
                'original_url': url, 'source_article_url': by[rid]['url'], 'http_status': response.status_code,
                'page_count': 1, 'image_size': list(original_size), 'original_image_format': original_format,
                'original_sha256': sha(original_bytes), 'redacted_sha256': sha(output.read_bytes()),
                'redaction': {'raw_download_saved': False, 'method': '内存下载；Windows OCR只返回安全文字与联系行坐标；遮白联系行后再保存PNG',
                              'header_mask_pixels': header, 'masked_rectangle_count': len(rectangles),
                              'contact_pattern_count_after': 0, 'layout_preserved': True,
                              'author_existing_mask': 'OBS11内部实习公司和职责由作者遮蔽，未尝试恢复' if rid == 'OBS11' else '未尝试恢复任何作者遮蔽内容'},
                'reading_scope': '实际读取保存后的专业模块；OCR只用于脱敏定位，技术内容以可读原图为准。',
                'classification_boundary': 'PNG原图脱敏，不是原始PDF；片段不冒充完整简历。' if rid != 'OBS11' else '一页简历图，包含作者打码的内部实习；不是完整成功者履历，不改变原5份核心完整专业履历统计。',
                'acquired_on': DATE, 'reused': False,
            })
            attempts.append({'candidate_id': rid, 'original_url': url, 'status': '已取得并保存脱敏PNG', 'http_status': response.status_code, 'raw_file_saved': False})
        except Exception as exc:
            attempts.append({'candidate_id': rid, 'original_url': url, 'status': '未保存', 'reason': str(exc), 'raw_file_saved': False})

    for rid in ['CV23', 'CV24', 'CV28', 'CV30', 'CV31', 'OBS05', 'OBS06', 'OBS07']:
        record = by[rid]
        filename = record.get('redacted_cv_local_file', record.get('redacted_resume_file'))
        path = ROOT / filename
        is_pdf = path.suffix.lower() == '.pdf'
        item = {
            'asset_id': rid + ('_PDF' if is_pdf else '_HTML'), 'candidate_id': rid,
            'material_type': '既有原始PDF的脱敏专业模块副本' if is_pdf else '既有公开网页履历的脱敏转录',
            'completeness': '完整专业履历；研究/AI Infra对照' if rid.startswith('OBS') else '完整专业履历',
            'local_file': filename, 'original_url': source_link(record), 'source_article_url': record['url'],
            'page_count': None, 'thumbnail_file': None, 'preview_files': [],
            'redacted_sha256': sha(path.read_bytes()), 'reused': True,
            'redaction': {'method': '复用本包已有脱敏附件，不恢复联系人、链接或被遮蔽内容', 'raw_download_saved': False},
            'reading_scope': '原有专业模块核读范围沿用；本轮补页面渲染与视觉浏览入口。',
            'classification_boundary': 'PDF脱敏附件保留原页布局；没有重新获取未脱敏原件。' if is_pdf else 'HTML脱敏履历转录及其截图，不冒称文章原附PDF或新取得原始简历。',
        }
        if is_pdf:
            document = fitz.open(path)
            item['page_count'] = len(document)
            text = '\n'.join(page.get_text() for page in document)
            item['redaction']['text_contact_pattern_count'] = len(re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|(?<!\d)1[3-9]\d{9}(?!\d)', text))
            assert item['redaction']['text_contact_pattern_count'] == 0, rid
            for number, page in enumerate(document, 1):
                preview = PREVIEW / f'{rid}_第{number}页.png'
                pixmap = page.get_pixmap(matrix=fitz.Matrix(1.8, 1.8), alpha=False)
                pixmap.save(preview)
                item['preview_files'].append(rel(preview))
            item['thumbnail_file'] = item['preview_files'][0]
        assets.append(item)

    existing_manifest = load(MANIFEST) if MANIFEST.exists() else {}
    for asset in assets:
        if asset['material_type'].startswith('既有公开网页'):
            previous = next((a for a in existing_manifest.get('assets', []) if a['asset_id'] == asset['asset_id']), None)
            if previous:
                for field in ['thumbnail_file', 'preview_files', 'image_size', 'web_capture']:
                    if previous.get(field):
                        asset[field] = previous[field]

    candidates = []
    for record in rows:
        if record['category'] != '候选人资料':
            continue
        selected = [a for a in assets if a['candidate_id'] == record['id']]
        candidates.append({'candidate_id': record['id'], 'asset_ids': [a['asset_id'] for a in selected],
                           'visual_status': selected[0]['completeness'] if selected else '仅经历/面经/履历文章，未取得可归档简历图或PDF',
                           'article_url': record['url'], 'track': record.get('taxonomy', {}).get('track', '未知')})
    assert len(candidates) == 34
    document = {
        'date': DATE, 'canonical_source': '08_证据索引与统计/all_evidence_records.json',
        'atlas_file': '03_简历与候选人案例/argon_候选人与简历图册.html',
        'assets': assets, 'candidates': candidates,
        'controls': [{'candidate_id': rid, 'asset_ids': [a['asset_id'] for a in assets if a['candidate_id'] == rid]}
                     for rid in ['OBS11', 'OBS05', 'OBS06', 'OBS07']],
        'attempts': attempts,
        'counts': {'core_candidates': 34, 'core_candidates_with_visual_material': sum(bool(c['asset_ids']) for c in candidates),
                   'new_public_image_documents': sum(not a['reused'] for a in assets),
                   'new_resume_fragments': sum(not a['reused'] and a['candidate_id'].startswith('CV') for a in assets),
                   'new_masked_resume_controls': sum(not a['reused'] and a['candidate_id'] == 'OBS11' for a in assets),
                   'reused_pdf_documents': sum(a['reused'] and a['local_file'].endswith('.pdf') for a in assets),
                   'reused_html_profiles': sum(a['reused'] and a['local_file'].endswith('.html') for a in assets),
                   'new_original_pdf_documents': 0, 'new_core_complete_profiles': 0,
                   'new_verified_ssp_candidates': 0},
        'boundaries': ['未将TXT卡片排版后冒充简历。', '仅保存脱敏专业内容，原始图片下载只驻留内存。',
                       'OBS11录用未知、内部实习作者打码，单列视觉对照；原5份核心完整专业履历统计不变。',
                       '34候选人方向/时间/结果仍以主证据库分类为准，图片存在不证明SSP或因果。',
                       '网页履历截图、原图脱敏PNG、原PDF脱敏副本分别标明；没有缺图则不绘制假简历。']
    }
    dump(MANIFEST, document)
    print(json.dumps(document['counts'], ensure_ascii=False))


def clean_item(text):
    return str(text or '').strip().rstrip('。；; ')


def as_text(value):
    if isinstance(value, dict):
        parts = [clean_item(v) for v in value.values() if clean_item(v)]
        return '；'.join(parts)
    if isinstance(value, list):
        parts = [clean_item(as_text(v)) for v in value if clean_item(as_text(v))]
        return '；'.join(parts)
    return str(value or '').strip()


def safe(value, limit=600):
    value = as_text(value)
    value = re.sub(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|(?<!\d)1[3-9]\d{9}(?!\d)', '[联系方式已省略]', value)
    return escape(value[:limit] + ('…' if len(value) > limit else ''))


STACK_FALLBACKS = {
    'CV24': 'C++、Python、Java、Go、分布式存储、RAG 与多 Agent 协同',
    'CV23': 'Python、Java、C++、LangGraph、FastAPI、PostgreSQL、Docker',
    'OBS05': 'Python、PyTorch、DeepSpeed、Megatron-LM、CUDA、大模型分布式训练',
    'OBS06': 'Python、PyTorch、强化学习 (RLHF/PPO)、多模态与检索增强',
    'OBS07': 'Python、C++、vLLM、TensorRT-LLM、K8s、AI Infra 推理加速',
}


def atlas():
    manifest = load(MANIFEST)
    rows = load(BASE / 'all_evidence_records.json')
    by = {r['id']: r for r in rows}
    assets_by = {}
    for asset in manifest['assets']:
        assets_by.setdefault(asset['candidate_id'], []).append(asset)
    candidates = [r for r in rows if r['category'] == '候选人资料']
    preferred = ['CV30', 'CV31', 'CV28', 'CV24', 'CV23', 'CV01', 'CV06']
    candidates.sort(key=lambda r: preferred.index(r['id']) if r['id'] in preferred else 100 + int(r['id'][2:]))

    def local_link(filename):
        return '../' + filename

    def card(record, control=False):
        rid = record['id']; materials = assets_by.get(rid, []); tax = record.get('taxonomy', {})
        track = tax.get('track', '未知')
        if materials:
            m0 = materials[0]
            ext_tag = '脱敏PDF' if m0['local_file'].endswith('.pdf') else ('脱敏PNG' if m0['local_file'].endswith('.png') else '脱敏网页履历')
            status = f"{ext_tag} · {m0['completeness']}"
        else:
            status = '经历/面经文章（无公开PDF/图）'
        image_html = ''
        links = []
        if materials:
            first = materials[0]
            thumb = first.get('thumbnail_file')
            if thumb:
                image_html = f'<a class="preview" href="{escape(local_link(first["local_file"]), quote=True)}" target="_blank"><img loading="lazy" src="{escape(local_link(thumb), quote=True)}" alt="{rid} {safe(first["material_type"])}预览"></a>'
            for material in materials:
                label = '打开脱敏PDF' if material['local_file'].endswith('.pdf') else '打开脱敏PNG' if material['local_file'].endswith('.png') else '打开网页履历'
                links.append(f'<a class="primary-link" href="{escape(local_link(material["local_file"]), quote=True)}" target="_blank">{label} ↗</a>')
                if len(material.get('preview_files', [])) > 1:
                    for number, filename in enumerate(material['preview_files'][1:], 2):
                        links.append(f'<a href="{escape(local_link(filename), quote=True)}" target="_blank">第{number}页图</a>')
        else:
            image_html = '<div class="article-label">经历与面经复盘文章<span>无公开简历图/PDF，提炼其项目经历与面试结果供对标</span></div>'
        outcome = record.get('outcome', '')
        if not outcome:
            outcome = '；'.join(f'{x.get("company", "未知公司")}：{x.get("grade", "未知档位")} / {x.get("status", "未知结果")}' for x in record.get('outcomes', [])) or '录用或档位未核'
        raw_projects = record.get('projects') or []
        projects = '；'.join(p.get('name', '未命名项目') if isinstance(p, dict) else clean_item(p) for p in raw_projects) if isinstance(raw_projects, list) else as_text(raw_projects)
        projects = projects or as_text(record.get('source_summary')) or '未公开本人项目细节'
        stack_str = as_text(record.get('stack')) or STACK_FALLBACKS.get(rid, '详见履历附件与项目模块')
        strength = record.get('strengths') or record.get('original_analysis') or record.get('source_summary') or '专业履历的时间线与职责可直接查看；实现细节以具体项目材料为准。'
        weakness = record.get('weaknesses') or record.get('chain_gaps') or '缺少本人源码与录用因果证明'
        recommendation = record.get('recommendation', '作为研究/AI Infra对照，和后端应用目标分开阅读。')
        if rid == 'OBS11':
            outcome = '录用未知；本帖为收藏分享，其他文章的offer不属于本帖作者。'
            projects = '图内个人网盘：分片/断点续传、Redis+Kafka延时任务；轻量RPC：Netty协议、调用链、容错与请求备份（内部实习已由作者打码）'
            strength = '一页图直接展示业务存储项目与网络框架的分工，可研究项目互补与简历组织。'
            weakness = '原图分辨率792×1121，实习模块大幅打码；性能数字为作者简历自报，无测试条件与录用结果证明。'
            recommendation = '建议看项目分工和追问入口；不作为已录用/SSP或完整成功者履历。'
        links.append(f'<a href="../01_调研报告/argon_资料检索与证据详表.html#{rid}">证据详情</a>')
        links.append(f'<a href="{escape(record["url"], quote=True)}" target="_blank" rel="noreferrer">原始来源 ↗</a>')
        tag = '视觉对照' if control else '核心候选人'
        search_text = ' '.join([rid, record['title'], track, stack_str, projects, outcome, as_text(recommendation)]).lower()
        open_attr = ' open' if (materials and not control) else ''
        rec_html = f'<p><b>阅读建议：</b>{safe(recommendation, 500)}</p>' if clean_item(as_text(recommendation)) != clean_item(as_text(strength)) else ''
        return f'''<article class="entry {'has-visual' if materials else 'article-only'}" id="{rid}" data-track="{escape(track, quote=True)}" data-visual="{'yes' if materials else 'no'}" data-control="{'yes' if control else 'no'}" data-search="{escape(search_text, quote=True)}">
<div class="entry-top"><span><b>{rid}</b> · {tag}</span><span>{safe(track)} / {safe(tax.get('recruitment', '未知'))}</span></div>
{image_html}<div class="entry-body"><p class="material-status">{safe(status)}</p><h3>{safe(record['title'], 120)}</h3>
<p class="result">{safe(outcome, 420)}</p><dl><dt>时间</dt><dd>{safe(tax.get('experience_date_text', record.get('date', '未知')), 260)}</dd><dt>技术栈</dt><dd>{safe(stack_str, 350)}</dd><dt>本人项目</dt><dd>{safe(projects, 600)}</dd></dl>
<details{open_attr}><summary>优缺点与借鉴要点</summary><p><b>可借鉴：</b>{safe(strength, 550)}</p><p><b>局限与边界：</b>{safe(weakness, 650)}</p>{rec_html}</details><nav class="entry-links">{' '.join(links)}</nav></div></article>'''

    primary = '\n'.join(card(record) for record in candidates if record['id'] in assets_by)
    article_only = '\n'.join(card(record) for record in candidates if record['id'] not in assets_by)
    controls = '\n'.join(card(by[rid], True) for rid in ['OBS11', 'OBS05', 'OBS06', 'OBS07'])
    html = '''<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>候选人与简历图册</title><style>
:root{--ink:#172735;--muted:#5b6974;--line:#d6dedf;--paper:#ede9e0;--white:#fff;--blue:#1d5c59;--mint:#dfeee8;--gold:#f0e4c6}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.7 "Microsoft YaHei","PingFang SC","Segoe UI",sans-serif}a{color:var(--blue);text-underline-offset:3px}
.top-bar{position:sticky;top:0;z-index:20;background:#1b363acc;backdrop-filter:blur(8px);border-bottom:1px solid #2d4f54;color:#fff}
.top-bar-inner{max-width:1480px;margin:auto;padding:10px 24px;display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}
.top-brand{font-weight:700;font-size:14px;letter-spacing:.8px;color:#e4f2ef;white-space:nowrap}
.top-links{display:flex;gap:6px 10px;flex-wrap:wrap;align-items:center}
.top-links a{color:#d3e6e3;text-decoration:none;font-size:13px;padding:4px 9px;border-radius:4px;transition:background .15s}
.top-links a:hover,.top-links a.active{background:#2c5855;color:#fff}
.top-links a.pdf-pill{background:#a3482d;color:#fff;font-weight:600}
header.hero{background:#173e42;color:white;padding:30px max(24px,calc((100vw - 1480px)/2)) 26px}header.hero a{color:#cbe9e5}.eyebrow{font-size:12px;letter-spacing:2.5px;color:#bcd1d5;font-weight:700}h1{font-size:36px;margin:8px 0 8px;letter-spacing:.5px}header.hero p{max-width:1020px;margin:0;color:#d7e2e5;font-size:16.5px}header.hero nav{margin-top:16px;display:flex;gap:18px;flex-wrap:wrap;font-size:14px}.summary{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;border:1px solid var(--line);margin:24px 0 18px;background:var(--line);border-radius:6px;overflow:hidden}.metric{background:white;padding:16px 20px}.metric b{font-size:29px;display:block;line-height:1.2;color:var(--blue)}.metric span{font-size:13px;color:var(--muted)}main{max-width:1480px;margin:auto;padding:0 24px 50px}.intro{font-size:14px;color:var(--muted);margin:0 0 16px}.toolbar{position:sticky;top:46px;background:rgba(237,233,224,.97);z-index:10;padding:12px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);display:grid;grid-template-columns:minmax(210px,1fr) 190px auto;gap:12px;align-items:center}.toolbar input,.toolbar select{font:inherit;border:1px solid #aebdc2;border-radius:4px;padding:9px 12px;background:white;min-width:0}.filters{display:flex;gap:6px;flex-wrap:wrap}.filters button{font:inherit;font-size:13px;border:1px solid #b5c2c5;background:white;color:var(--ink);padding:8px 12px;cursor:pointer;border-radius:4px}.filters button.active{background:var(--blue);border-color:var(--blue);color:white}.section-title{display:flex;justify-content:space-between;align-items:baseline;margin:26px 0 12px}.section-title h2{font-size:22px;margin:0}.section-title span{color:var(--muted);font-size:13px;font-weight:600}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;align-items:start}.entry{background:white;border:1px solid var(--line);border-radius:4px;min-width:0;scroll-margin-top:110px;box-shadow:0 3px 10px #17273508}.entry-top{display:flex;gap:12px;justify-content:space-between;font-size:11.5px;background:#edf2f0;padding:9px 15px;color:#38504d}.preview{display:block;height:328px;background:#e7ecea;padding:12px;border-bottom:1px solid var(--line)}.preview img{width:100%;height:100%;object-fit:contain;object-position:top}.entry-body{padding:16px 20px 18px}.material-status{display:inline-block;font-size:11px;background:var(--mint);padding:3px 8px;border-radius:3px;margin:0 0 8px;color:#1e5240;font-weight:600}.entry h3{font-size:18px;line-height:1.45;margin:0 0 10px}.result{font-size:13px;border-left:3px solid #c4a35b;background:#faf7f0;padding:6px 10px;margin:0 0 14px}dl{margin:0;font-size:12.5px;display:grid;grid-template-columns:56px minmax(0,1fr);gap:6px 10px}dt{font-weight:700;color:#4a615e}dd{margin:0;overflow-wrap:anywhere}details{border-top:1px solid var(--line);margin-top:14px;padding-top:10px;font-size:12.5px}summary{cursor:pointer;color:var(--blue);font-weight:700}details p{margin:8px 0;line-height:1.6}.entry-links{display:flex;gap:10px 15px;flex-wrap:wrap;border-top:1px solid var(--line);padding-top:12px;margin-top:14px;font-size:12px}.primary-link{font-weight:700;color:#a3482d}.article-label{padding:14px 18px;background:#f7f8f4;border-bottom:1px solid var(--line);font-size:13px;font-weight:700;color:#465956}.article-label span{display:block;font-weight:400;font-size:11.5px;color:var(--muted);margin-top:2px}.article-only .material-status{background:#f0e8d7;color:#6f582e}.empty{padding:35px;text-align:center;color:var(--muted);display:none}.controls-note{margin:0 0 15px;font-size:13px;color:var(--muted)}footer{margin-top:30px;border-top:1px solid var(--line);padding-top:18px;font-size:12px;color:var(--muted)}[hidden]{display:none!important}@media(min-width:1350px){.grid{grid-template-columns:repeat(3,minmax(0,1fr))}.has-visual .preview{height:380px}}@media(max-width:1000px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.toolbar{grid-template-columns:1fr 180px}.filters{grid-column:1/-1}.summary{grid-template-columns:repeat(2,1fr)}}@media(max-width:640px){header.hero{padding:24px 18px}h1{font-size:28px}main{padding:0 14px 35px}.grid{grid-template-columns:1fr;gap:16px}.toolbar{position:relative;top:0;grid-template-columns:1fr}.filters{grid-column:auto}.summary{margin-top:18px}.metric{padding:13px}.metric b{font-size:25px}.section-title{display:block}.preview{height:340px}.entry-body{padding:16px}}@media print{.top-bar,.toolbar{display:none!important}.entry{break-inside:avoid}.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.preview{height:250px}details>p{display:block}details{display:block}header.hero{padding:20px;background:white;color:black;border-bottom:2px solid black}.summary{margin:16px 0}a{text-decoration:none}body{background:white}}
</style></head><body>
<header class="top-bar"><div class="top-bar-inner"><span class="top-brand">后端 &amp; Agent 实习调研</span><nav class="top-links" aria-label="全站导航"><a href="../argon_00_开始阅读.html">开始阅读</a><a href="../01_调研报告/argon_实习求职调研总报告.html">调研总报告</a><a href="../02_招聘岗位资料/argon_岗位要求统计与解读.html">岗位要求统计</a><a class="active" href="argon_候选人与简历图册.html">候选人简历图册</a><a href="../04_面经与专业观点/argon_面经重点与项目追问.html">面经与项目追问</a><a href="../06_项目分析与推荐/argon_项目比较与精读指南.html">25项目精读指南</a><a href="../01_调研报告/argon_资料检索与证据详表.html">239条证据检索</a><a class="pdf-pill" href="../01_调研报告/argon_实习求职调研总报告.pdf">重点版 PDF ↗</a></nav></div></header>
<header class="hero"><div class="eyebrow">BACKEND / AGENT · CANDIDATE &amp; RESUME ATLAS</div><h1>候选人与简历视觉图册</h1><p>优先展示真实获取并脱敏的公开 PDF 简历、PNG 原图片段与网页版完整履历（共 7 位核心候选人 + 4 份视觉对照），其余 27 位以求职经历/面经复盘归档。每张卡片清晰拆解候选人技术栈、个人项目与可借鉴写法。</p><nav><a href="#candidates">01 含视觉附件的核心候选人 (7位)</a><a href="#articles-area">02 经历与面经复盘候选人 (27位)</a><a href="#controls-heading">03 视觉与研究/Infra对照 (4份)</a><a href="../08_证据索引与统计/简历视觉材料_整理清单.json">04 脱敏与视觉附件清单 (JSON)</a></nav></header><main>
<section class="summary"><div class="metric"><b>34</b><span>核心候选人案例（支持按赛道筛选）</span></div><div class="metric"><b>7</b><span>含 PDF / PNG / 网页履历的核心候选人</span></div><div class="metric"><b>5</b><span>核心完整专业履历（3份PDF + 2份网页）</span></div><div class="metric"><b>4</b><span>视觉对照样本（一页打码简历 + 3份研究/Infra）</span></div></section>
<p class="intro"><b>脱敏与阅读口径（全局说明，卡片内不再重复标注）：</b>所有 PDF、PNG 与网页履历均为保留原始排版与专业模块的脱敏副本（已隐去联系方式与隐私信息）。前 7 张核心卡片已默认展开【优缺点与借鉴要点】，方便直接对照简历写法。</p>
<section class="toolbar" aria-label="搜索与筛选"><input id="search" type="search" placeholder="搜索公司、技术栈、项目名或编号(如CV30、CV01)..." aria-label="搜索候选人"><select id="material" aria-label="材料类型"><option value="all">全部材料类型</option><option value="visual">有 PDF / PNG / 网页履历</option><option value="article">仅经历与面经文章</option><option value="control">仅对照材料 (OBS)</option></select><div class="filters" aria-label="岗位方向"><button class="active" data-filter="all">全部赛道</button><button data-filter="后端">后端</button><button data-filter="Agent工程">Agent工程</button><button data-filter="混合">后端+Agent混合</button><button data-filter="算法对照">算法对照</button></div></section>
<div class="section-title"><h2>一、优先精读：含真实简历附件与网页履历的候选人（7位）</h2><span id="visible-count">匹配 34 / 34 位</span></div><p class="intro">建议重点对比：<b>CV30 / CV31</b> 如何描述 Agent 实习工程职责与评测，<b>CV28 / CV24 / CV23</b> 如何将履历与 GitHub 本人仓库直连，以及 <b>CV01 / CV06</b> 的实习与开源项目模块写法。</p><section id="candidates" class="grid">__PRIMARY__</section><div class="empty" id="empty">没有匹配的候选人资料，请清空搜索词或切换筛选条件。</div>
<details class="article-collection" id="articles-area"><summary>二、其余 27 位核心候选人：求职经历与面经复盘索引 <span id="article-count">27 位</span></summary><p class="intro">以下候选人未公开独立 PDF/图片简历，但保留了详实的求职时间线、项目背景与录用档位自述。点击任意卡片内的【优缺点与借鉴要点】可查看提炼结论。</p><section id="article-candidates" class="grid">__ARTICLES__</section></details>
<div class="section-title" id="controls-heading"><h2>三、简历版面与研究 / AI Infra 视觉对照（4份）</h2><span>用于版面参考或赛道边界对照，不计入核心应用工程样本</span></div><p class="controls-note" id="controls-note"><b>OBS11</b> 为一页式后端公开简历图（内部实习已由作者打码，适合参考“一业务项目 + 一底层轮子”的版面布局）；<b>OBS05 / OBS06 / OBS07</b> 为算法研究与 AI Infra 完整脱敏 PDF 简历，用于对照研究岗与工程岗的履历差异。</p><section id="controls" class="grid">__CONTROLS__</section>
<footer>整理日期：2026-10-24 · 原始简历图片仅在内存完成 OCR 定位并遮白联系信息后落盘，绝不保存未脱敏原件；未公开简历附件的候选人按实际文章类型归档。</footer></main><script>
const search=document.getElementById('search'),material=document.getElementById('material'),buttons=[...document.querySelectorAll('[data-filter]')],entries=[...document.querySelectorAll('.entry')];let active='all';function filter(){const q=search.value.trim().toLowerCase(),kind=material.value;let count=0,controlCount=0,articleCount=0;for(const entry of entries){const control=entry.dataset.control==='yes',visual=entry.dataset.visual==='yes';const shown=(!q||entry.dataset.search.includes(q))&&(active==='all'||entry.dataset.track===active)&&(kind==='all'||kind==='visual'&&visual||kind==='article'&&!visual&&!control||kind==='control'&&control);entry.hidden=!shown;if(shown){if(control)controlCount++;else{count++;if(!visual)articleCount++;}}}document.getElementById('visible-count').textContent='匹配 '+count+' / 34 位';document.getElementById('article-count').textContent='当前匹配 '+articleCount+' 位';const area=document.getElementById('articles-area');area.hidden=articleCount===0;if(q||kind==='article'||active!=='all')area.open=true;document.getElementById('empty').style.display=count===0&&kind!=='control'?'block':'none';document.getElementById('controls-heading').hidden=controlCount===0;document.getElementById('controls-note').hidden=controlCount===0;}search.addEventListener('input',filter);material.addEventListener('change',filter);buttons.forEach(button=>button.addEventListener('click',()=>{active=button.dataset.filter;buttons.forEach(b=>b.classList.toggle('active',b===button));filter();}));filter();
</script></body></html>'''
    html = html.replace('__PRIMARY__', primary).replace('__ARTICLES__', article_only).replace('__CONTROLS__', controls)
    html = html.replace('</head>', '<style>.article-collection{margin:34px 0 28px;padding:20px;border:1px solid var(--line);background:#e6e8e1;border-radius:6px}.article-collection>summary{font-size:20px;line-height:1.5}.article-collection>summary span{font-size:12px;font-weight:400;margin-left:12px;color:var(--muted)}.article-collection[open]>summary{margin-bottom:16px}#article-candidates{grid-template-columns:repeat(2,minmax(0,1fr))}.article-only .entry h3{font-size:16px}@media(max-width:640px){.article-collection{padding:14px}.article-collection>summary{font-size:18px}#article-candidates{grid-template-columns:1fr}}</style></head>')
    (DIR / 'argon_候选人与简历图册.html').write_text(html, encoding='utf-8', newline='\r\n')
    if (BASE / '公开简历原件_清单.json').exists():
        import sys
        subprocess.run([sys.executable, str(BASE / 'argon_整合公开简历与直观命名.py')], check=True)
    print('atlas built: 34 core candidate cards plus 4 visual controls')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--collect', action='store_true')
    parser.add_argument('--atlas', action='store_true')
    arguments = parser.parse_args()
    if arguments.collect:
        collect()
    if arguments.atlas:
        atlas()
