"""生成外部调研的去重入口；只读来源目录，不执行旧整合器或第三方项目。"""
from collections import Counter
from html import escape
from pathlib import Path
import ast
import hashlib
import json
import re


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
SOURCE = Path('C:/Users/GW/Downloads/astra/backend_agent_research_2026-10-24')
PAGE = ROOT / '01_调研报告/外部调研增补与去重清单.html'
MODULES = ROOT / '06_项目分析与推荐/外部调研_文档判断与阅读模块.md'
TITLE = '外部调研增补与去重清单'
E = lambda value: escape(str(value), quote=True)


def load(name, required=True):
    path = BASE / name
    if not path.exists():
        if required:
            raise FileNotFoundError(f'数据尚未就绪：{path.name}')
        return {}
    return json.loads(path.read_text(encoding='utf-8-sig'))


def text(value):
    if value is None:
        return ''
    if isinstance(value, bool):
        return '是' if value else '否'
    if isinstance(value, dict):
        return '；'.join(f'{key}：{text(item)}' for key, item in value.items()
                        if item not in (None, '', [], {}))
    if isinstance(value, (list, tuple)):
        return '；'.join(text(item) for item in value if item not in (None, '', [], {}))
    return str(value)


def get(record, *paths, default=''):
    for path in paths:
        value = record
        for key in path.split('.'):
            if not isinstance(value, dict) or key not in value:
                value = None
                break
            value = value[key]
        if value not in (None, '', [], {}):
            return value
    return default


def objects(value):
    """允许核读清单使用任意分组，不依赖其顶层字段名称。"""
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


def matching_reviews(manifest, mapping):
    sid, did = mapping.get('source_id'), mapping.get('destination_id')
    result = []
    for node in objects(manifest):
        ids = [node.get(key) for key in ('source_id', 'id', 'existing_id', 'destination_id')]
        if (sid and sid in ids) or (did and did in ids):
            result.append(node)
    return result


def html_link(url, label):
    if not url:
        return '未建立'
    value = str(url)
    if not value.startswith(('https://', 'http://', '../', '#')):
        return E(label)
    extra = ' target="_blank" rel="noopener noreferrer"' if value.startswith('http') else ''
    return f'<a href="{E(value)}"{extra}>{E(label)}</a>'


def unified_link(mapping):
    did = mapping.get('destination_id')
    return html_link(f'../01_调研报告/需求核对与阅读优先级.html#{did}', did) if did else '未纳入主表'


def reuse_shell():
    """仅提取原生成器的常量和 shell，不 import 含旧数据装载的模块。"""
    path = BASE / '生成需求核对报告.py'
    tree = ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
    env = {'E': E}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            names = [target.id for target in node.targets if isinstance(target, ast.Name)]
            if len(names) == 1 and names[0] in ('CSS', 'JS'):
                env[names[0]] = ast.literal_eval(node.value)
        elif isinstance(node, ast.FunctionDef) and node.name == 'shell':
            function = ast.Module(body=[node], type_ignores=[])
            exec(compile(ast.fix_missing_locations(function), str(path), 'exec'), env)
    if not all(key in env for key in ('CSS', 'JS', 'shell')):
        raise ValueError('原报告的 shell/CSS/JS 未完整取得')
    return env['shell']


def review_roots(mapping, record, manifest=None):
    roots = matching_reviews(manifest, mapping) if manifest else []
    sid = mapping.get('source_id', '')
    embedded = get(record, f'external_research_reviews.{sid}.review', 'source_record', default={})
    if isinstance(embedded, dict) and embedded:
        roots.append(embedded)
    return roots


def reading_scope(mapping, record, manifest=None):
    for review in review_roots(mapping, record, manifest):
        value = get(review, 'reading_scope', 'read_scope', 'live_access.read_scope', default='')
        if value and text(value) not in ('部分', '全文', '资料索引'):
            return text(value)
    return text(get(record, 'reading.scope_note', 'access_level', 'reading.scope', default=get(
        mapping, 'reading_scope', 'read_scope', default='未核')))


def category(mapping, record):
    value = text(get(mapping, 'category', default=record.get('category', '')))
    if value:
        return value
    sid = str(mapping.get('source_id', ''))
    return {'J': '招聘JD', 'R': '候选人资料', 'I': '面经复盘',
            'V': '专业观点', 'P': '工程参考文档'}.get(sid[:1], '其他')


def is_new(mapping, new_ids):
    action = str(mapping.get('action', '')).lower()
    return action in ('new', '新增', 'append') or mapping.get('destination_id') in new_ids


def disposition(mapping, new_ids):
    action = str(mapping.get('action', ''))
    if action == '待手动访问':
        return 'manual'
    if action == '商业背景参考':
        return 'commercial'
    return 'new' if is_new(mapping, new_ids) else 'reuse'


def restricted(mapping, record, manifest=None):
    if mapping.get('action') == '待手动访问':
        return True
    if mapping.get('action') == '商业背景参考':
        return False
    roots = review_roots(mapping, record, manifest)
    # 只读明确的 HTTP/访问字段，绝不在哈希、ID 或正文数字中匹配状态码。
    accesses = []
    for root in roots:
        for key in ('live_access', 'access'):
            access = root.get(key)
            if isinstance(access, dict):
                accesses.append(access)
        evidence = root.get('read_evidence', [])
        if isinstance(evidence, list):
            accesses.extend(item for item in evidence if isinstance(item, dict))
    successful_read = False
    for access in accesses:
        status = get(access, 'http_status', 'status_code', 'status', default=None)
        try:
            status = int(status)
        except (TypeError, ValueError):
            status = None
        title = str(access.get('title', ''))
        scope = text(get(access, 'read_scope', 'reading_scope', default=''))
        if status in (401, 403, 412, 429, 451, 521) or 'Security Verification' in title:
            return True
        if re.search(r'受限页|验证页|未取得.*正文', scope):
            return True
        if status is not None and 200 <= status < 300 and (access.get('body_text_chars', 0) > 0
                                                          or access.get('fulltext') is True):
            successful_read = True
    if successful_read:
        return False
    scope = text(get(record, 'reading.scope', default=mapping.get('reading_scope', '')))
    if scope in ('摘要', '未读', '资料索引', '待核'):
        return True
    note = text(get(record, 'reading.scope_note', 'access_level', default=''))
    access = get(record, 'source_record.live_access', 'source_record.access', default={})
    if isinstance(access, dict) and access.get('status') in (401, 403, 429, 451, 521):
        return True
    return bool(re.search(r'Security Verification|仅(?:外部|搜索|索引).{0,10}(?:摘要|片段)|验证页|原页受限', note))


def verify_source():
    """指纹核对只读源目录；有差异则停止，避免生成“原样保留”的错误陈述。"""
    before = load('astra来源_合并前文件指纹.json', required=False)
    files = before.get('files', []) if isinstance(before, dict) else []
    source_path = Path(before.get('source_path', str(SOURCE))) if isinstance(before, dict) else SOURCE
    if not files:
        return {'status': '未取得合并前指纹，不声称已通过字节级核对', 'count': 0,
                'path': source_path.as_posix(), 'verified': False}
    if not source_path.is_dir():
        raise FileNotFoundError(f'来源目录不可读取：{source_path}')
    expected = {row['path']: row for row in files if isinstance(row, dict) and row.get('path')}
    actual = {path.relative_to(source_path).as_posix(): path
              for path in source_path.rglob('*') if path.is_file()}
    mismatches = sorted(set(expected) ^ set(actual))
    for rel in sorted(set(expected) & set(actual)):
        raw = actual[rel].read_bytes()
        row = expected[rel]
        if len(raw) != row.get('bytes') or hashlib.sha256(raw).hexdigest() != row.get('sha256'):
            mismatches.append(rel)
    if mismatches:
        raise ValueError(f'来源指纹与合并前不同，共 {len(set(mismatches))} 项；停止生成，保留现场供检查。')
    return {'status': '文件清单、字节数与 SHA-256 全部一致', 'count': len(expected),
            'path': source_path.as_posix(), 'verified': True}


def interview_group(record):
    tx = record.get('taxonomy') if isinstance(record.get('taxonomy'), dict) else {}
    recruitment = text(get(tx, 'recruitment', default=record.get('recruitment', '未知')))
    confirmed = tx.get('year_confirmed') is True
    if recruitment == '实习' and confirmed and (record.get('strict_recent_internship') is True
                                               or tx.get('recent_status') == '近期确认'):
        track = text(get(record, 'source_record.track', default=tx.get('track', '')))
        if 'Infra' in track or tx.get('track') == '算法对照':
            return '近期实习 AI Infra 对照'
        return '近期明确实习（后端/Agent工程）'
    if '校招' in recruitment or '秋招' in recruitment or '春招' in recruitment:
        return '校招及混合批次'
    if '转正' in recruitment:
        return '转正材料'
    if not confirmed:
        return '事件年份未知'
    if recruitment == '实习':
        return '其他明确年份实习'
    return '其他或招聘类型未知'


def ai_note(record):
    for key in ('ai_organized', 'ai_generated', 'ai_assisted', 'ai_summary'):
        value = record.get(key)
        if isinstance(value, bool):
            return '原文明确标注 AI 整理/辅助' if value else '该字段标记为否；不据此认证现场逐字记录'
        if value:
            return text(value)
    corpus = text({key: record.get(key) for key in (
        'material_type', 'limitations', 'source_summary', 'summary', 'source_record', 'reading')})
    if re.search(r'AI.{0,8}(?:整理|润色|生成|补写)|(?:整理|润色|生成).{0,8}AI', corpus, re.I):
        return '材料涉及 AI 整理/辅助，按原记录边界阅读；不能把补写答案当真实追问'
    return '原文是否使用 AI 整理未披露/未核；本卡问题为研究者归纳'


def interview_table(items):
    result = []
    for mapping, record in items:
        tx = record.get('taxonomy') if isinstance(record.get('taxonomy'), dict) else {}
        event = get(tx, 'experience_date_text', default=get(record, 'date', 'event_date', default='未知'))
        source_date = get(record, 'source_date', default=tx.get('source_date_text', '未核'))
        known = '已证实事件年份' if tx.get('year_confirmed') is True else '事件年份未知'
        result.append('<tr><td>' + E(mapping.get('source_id', '')) + ' → ' + unified_link(mapping)
                      + '<br>' + E(mapping.get('title', record.get('title', ''))) + '</td><td>'
                      + E(event) + '<br><small>' + E(known) + '</small></td><td>' + E(source_date)
                      + '</td><td>' + E(tx.get('recruitment', '未知')) + '</td><td>'
                      + E(text(get(record, 'outcome', 'result_status', default='结果未知')))
                      + '</td><td>' + E(ai_note(record)) + '<br><small>'
                      + E(reading_scope(mapping, record)) + '</small></td><td>'
                      + html_link(mapping.get('url', record.get('url', '')), '原始面经') + '</td></tr>')
    return ('<div class="scroll"><table><thead><tr><th>资料</th><th>招聘事件时间</th>'
            '<th>发表/编辑日期</th><th>招聘类型</th><th>结果</th><th>整理与阅读边界</th>'
            '<th>来源</th></tr></thead><tbody>' + ''.join(result) + '</tbody></table></div>')


def urls(value):
    result = []
    for node in objects(value):
        for key, child in node.items():
            if isinstance(child, str) and key.lower() in (
                    'url', 'source_url', 'source_urls', 'read_url', 'official_url',
                    'primary_url', 'evidence_url', 'source_link', 'link'):
                if child.startswith(('https://', 'http://')):
                    result.append(child)
            elif key.lower() in ('urls', 'source_urls', 'sources') and isinstance(child, list):
                result.extend(item for item in child if isinstance(item, str)
                              and item.startswith(('https://', 'http://')))
    return list(dict.fromkeys(result))


def document_info(mapping, record, manifest):
    reviews = review_roots(mapping, record, manifest)
    joined = [record] + reviews
    scope = reading_scope(mapping, record, manifest)
    modules, findings, limits = [], [], []
    segments = []
    for node in joined:
        for key in ('read_paths', 'read_modules', 'inspect_paths', 'reading_modules',
                    'project_reading_modules', 'official_read_scope'):
            value = node.get(key)
            if value:
                modules.append(text(value))
        for key in ('source_findings', 'findings', 'finding', 'strengths', 'value',
                    'recommendation', 'recommended_use', 'own_summary', 'summary', 'source_summary',
                    'unique_value'):
            value = node.get(key)
            if value:
                findings.append(text(value))
        for key in ('limitations', 'limits', 'weaknesses', 'boundary', 'reading_boundary',
                    'inspection_boundary', 'claims_not_to_make', 'runtime_boundary', 'facts_boundary'):
            value = node.get(key)
            if value:
                limits.append(text(value))
        for evidence in node.get('read_evidence', []):
            if not isinstance(evidence, dict):
                continue
            segment = {key: evidence.get(key, '') for key in (
                'read_url', 'read_scope', 'short_original_basis', 'http_status')}
            if segment not in segments:
                segments.append(segment)
            if segment['read_scope']:
                modules.append(text(segment['read_scope']))
    links = list(dict.fromkeys([mapping.get('url', record.get('url', ''))] + urls(joined)))
    return {'mapping': mapping, 'record': record, 'reviews': reviews, 'scope': scope,
            'modules': list(dict.fromkeys(modules)), 'findings': list(dict.fromkeys(findings)),
            'limits': list(dict.fromkeys(limits)), 'urls': [url for url in links if url],
            'segments': segments, 'corpus': text(joined)}


def confirmed_read(info):
    if restricted(info['mapping'], info['record'], info['reviews']):
        return False
    record = info['record']
    if get(record, 'reading.scope', default='') in ('全文', '部分'):
        return True
    for review in info['reviews']:
        for evidence in review.get('read_evidence', []):
            if (isinstance(evidence, dict) and evidence.get('http_status') == 200
                    and evidence.get('body_text_chars', 0) > 0
                    and not re.search(r'受限|未取得|验证页', text(evidence.get('read_scope', '')))):
                return True
        if get(review, 'live_access.fulltext', 'access.fulltext', default=False) is True:
            return True
        if re.search(r'实读|实际读|已读|正文|README|文档', text(get(
                review, 'read_scope', 'reading_scope', 'live_access.read_scope', default=''))):
            return True
    return False


def retained_judgments(documents):
    """只在已核文档含相关依据时吸收技术判断，不自动扩写个人项目。"""
    rules = [
        ('LangGraph', ('langgraph',), ('checkpoint', '检查点', '持久化'),
         'Checkpoint 保存和恢复图执行状态，不会自动保证外部业务副作用幂等。',
         '阅读持久化、恢复/重放和外部工具副作用的处理范围；区分图状态恢复与业务写入语义。'),
        ('Ragas', ('ragas',), ('faithfulness', '忠实'),
         'Faithfulness 衡量回答与检索上下文的一致性，不能直接代表故障修复正确率。',
         '阅读指标定义、所需输入和评分边界；任务成功或修复有效性需要独立结果依据。'),
        ('Temporal', ('temporal',), ('activity', '重试', '幂等'),
         'Activity 可能重试，外部副作用仍需按操作语义处理幂等；持久化执行不自动保证外部写入恰好一次。',
         '阅读 Activity 执行、重试策略与幂等说明，并区分 Workflow 状态和外部系统效果。'),
        ('OpenHands', ('openhands',), ('隔离', 'sandbox', '沙箱', 'runtime'),
         '隔离能力只按已读 SDK/部署文档的范围记录；沙箱名称本身不能证明所有网络、文件和凭据边界均已隔离。',
         '阅读实际运行方式、执行位置和隔离配置；SDK 说明不能替代具体部署的安全验证。'),
        ('Dify', ('dify',), ('license', '许可', '多租户', '商业'),
         'Dify 的使用与再分发条件应以已核许可文本和版本为准，不能仅据“开源”标签推断没有附加条件。',
         '对照仓库 LICENSE 及补充条款的适用范围；本轮不作付费、部署或法律适用性认证。'),
    ]
    result = []
    for name, identity, evidence, finding, module in rules:
        for info in documents:
            corpus = info['corpus'].lower()
            identity_corpus = text([info['mapping'].get('title'), info['record'].get('title'),
                                    info['mapping'].get('url'), info['record'].get('url')]).lower()
            if (confirmed_read(info) and any(term in identity_corpus for term in identity)
                    and any(term.lower() in corpus for term in evidence)):
                result.append({'name': name, 'finding': finding, 'module': module, 'info': info})
                break
    return result


def markdown_documents(documents, judgments):
    lines = ['# 外部调研：文档判断与阅读模块', '',
             '本文件吸收已读技术文档中的判断，不启动个人项目设计。资料按文档或选读范围呈现，'
             '不增加原有 25 个项目的比较分母；本轮新增完整简历附件和源码附件均为 0。', '',
             '## 可保留的技术判断', '']
    if not judgments:
        lines += ['当前数据没有足够的已读依据生成跨文档判断，暂保留待核。', '']
    for item in judgments:
        info = item['info']
        lines += [f'### {item["name"]}', '', item['finding'], '',
                  '阅读模块：' + item['module'], '', '实际核读范围：' + info['scope'], '']
        for url in info['urls'][:8]:
            lines.append(f'- [原始依据]({url})')
        lines.append('')
    lines += ['## 按资料阅读', '']
    for info in documents:
        mapping = info['mapping']
        lines += [f'### {mapping.get("source_id", "")} → {mapping.get("destination_id", "未纳入")}'
                  + ' ' + str(mapping.get('title', info['record'].get('title', ''))), '',
                  '实际核读范围：' + info['scope'], '',
                  '指定模块：' + ('；'.join(info['modules']) or '依原文已读范围；未取得更细模块定位'), '',
                  '阅读价值：' + ('；'.join(info['findings']) or '尚无足够实读发现，保留入口待核'), '',
                  '局限：' + ('；'.join(info['limits']) or '仅此文档/选读范围；未执行项目或验证生产适用性'), '']
        if info['segments']:
            lines += ['原核读段与短依据：', '']
            for segment in info['segments']:
                lines.append('- ' + text(segment['read_scope']) + '：'
                             + text(segment['short_original_basis'])
                             + (f' [原文]({segment["read_url"]})' if segment['read_url'] else ''))
            lines.append('')
        for url in info['urls'][:8]:
            lines.append(f'- [原始资料]({url})')
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def selection_panel(mapping, record, manifest):
    reviews = review_roots(mapping, record, manifest)
    reason = ''
    limits = []
    for review in reviews:
        if not reason:
            reason = text(get(review, 'unique_value', 'recommendation', 'recommended_use', default=''))
        value = get(review, 'facts_boundary', 'limitations', 'limits', default='')
        if value:
            limits.append(text(value))
    reason = reason or text(get(record, 'recommendation', 'recommended_use', 'original_analysis', default='待核'))
    if not limits:
        limits.append(text(get(record, 'limitations', 'weaknesses', 'limits', default='按实际阅读范围使用')))
    body = '<article class="panel"><h3>' + E(mapping.get('title', record.get('title', ''))) + ' · ' + unified_link(mapping) + '</h3>'
    form = get(record, 'profile_type', 'document_type', 'material_type', default='')
    if form:
        body += '<p><b>材料形式：</b>' + E(text(form)) + '</p>'
    outcome = get(record, 'outcome', default='')
    if outcome:
        body += '<p><b>结果边界：</b>' + E(text(outcome)) + '</p>'
    body += '<p><b>实际选读：</b>' + E(reading_scope(mapping, record, manifest)) + '</p>'
    body += '<p><b>推荐理由：</b>' + E(reason) + '</p>'
    body += '<p><b>局限：</b>' + E('；'.join(dict.fromkeys(limits))) + '</p>'
    business = get(record, 'commercial_bias', 'commercial_background', default='')
    if not business:
        for review in reviews:
            business = get(review, 'commercial_background', 'commercial_bias', default='')
            if business:
                break
    if business:
        body += '<p><b>商业及选择偏差：</b>' + E(text(business)) + '</p>'
    evidence = []
    for review in reviews:
        evidence.extend(item for item in review.get('read_evidence', []) if isinstance(item, dict))
    if evidence:
        body += '<ul>'
        seen = set()
        for item in evidence:
            key = (item.get('read_url'), item.get('read_scope'), item.get('short_original_basis'))
            if key in seen:
                continue
            seen.add(key)
            body += '<li>' + E(text(item.get('read_scope', ''))) + '：' + E(text(item.get('short_original_basis', '')))
            body += ' ' + html_link(item.get('read_url', ''), '核读原文') + '</li>'
        body += '</ul>'
    body += '<p>' + html_link(mapping.get('url', record.get('url', '')), '原始入口') + '</p></article>'
    return body


def generate():
    mapping_data = load('astra合并_实施映射.json')
    mappings = mapping_data.get('mappings', []) if isinstance(mapping_data, dict) else []
    if len(mappings) != 64 or len({row.get('source_id') for row in mappings}) != 64:
        raise ValueError('实施映射尚未完整：必须为 64 条唯一 source_id，不生成部分页面。')
    all_records = load('all_evidence_records.json')
    if not isinstance(all_records, list):
        raise TypeError('主证据数据应为数组')
    by = {row['id']: row for row in all_records if isinstance(row, dict) and row.get('id')}
    missing = [row.get('destination_id') for row in mappings
               if row.get('destination_id') and row['destination_id'] not in by]
    if missing:
        raise ValueError('主导入尚未就绪，目标资料不存在：' + ', '.join(sorted(set(missing))))
    manifest = load('astra合并_候选人与观点项目.json')
    source = verify_source()
    new_ids = set(mapping_data.get('new_ids', []))
    pairs = [(mapping, by.get(mapping.get('destination_id'), {})) for mapping in mappings]
    new_pairs = [(mapping, record) for mapping, record in pairs if disposition(mapping, new_ids) == 'new']
    reused = [(mapping, record) for mapping, record in pairs if disposition(mapping, new_ids) == 'reuse']
    manual = [(mapping, record) for mapping, record in pairs if disposition(mapping, new_ids) == 'manual']
    commercial = [(mapping, record) for mapping, record in pairs if disposition(mapping, new_ids) == 'commercial']
    blocked = [(mapping, record) for mapping, record in pairs if restricted(mapping, record, manifest)]
    new_interviews = [(mapping, record) for mapping, record in new_pairs
                      if str(mapping.get('source_id', '')).startswith('I')
                      or '面经' in category(mapping, record)]
    doc_pairs = [(mapping, record) for mapping, record in pairs
                 if str(mapping.get('source_id', '')).startswith('P')]
    docs = [document_info(mapping, record, manifest) for mapping, record in doc_pairs]
    new_docs = [info for info in docs if is_new(info['mapping'], new_ids)]
    judgments = retained_judgments(docs)
    shell = reuse_shell()

    body = f'''<header><div class="eyebrow">2026-10-24 · 来源合并与证据范围</div>
<h1>{TITLE}</h1><p class="lead">将另一份调研中的独特材料补入现有证据体系，并保留重复来源映射。</p>
<nav><a href="#changes">本轮增量</a><a href="#interviews">新增面经</a><a href="#selections">候选人与观点选读</a><a href="#documents">参考文档</a>
<a href="#catalog">64 条去重清单</a><a href="需求核对与阅读优先级.html">统一阅读入口</a></nav></header>'''
    metrics = [(len(new_pairs), '新增逻辑证据（含 1 份待核摘要）'), (len(reused), '复用/补核，未重复计数'),
               (len(manual), '待手动访问，不增加主库证据'),
               (len(commercial), '商业背景参考，不增加主库证据'),
               (len(blocked), '受限/摘要来源，与新增和手动类别重叠'), (0, '新增完整简历与源码附件')]
    body += '<section id="changes"><h2>本轮新增、复用与访问边界</h2><div class="metrics">'
    for count, label in metrics:
        body += f'<div class="metric"><b>{count}</b><span>{E(label)}</span></div>'
    actual_categories = dict(Counter(category(mapping, record) for mapping, record in new_pairs))
    body += '</div><p>新增分类：' + E('；'.join(f'{key} {value}' for key, value in actual_categories.items())) + '。</p>'
    body += ('<p>源目录原样保留：<code>' + E(source['path']) + '</code>。指纹核对：'
             + E(source['status']) + '，共 ' + str(source['count']) + ' 个文件。'
             + html_link('../08_证据索引与统计/astra来源_合并前文件指纹.json', '查看合并前指纹清单') + '。</p>')
    body += ('<p>指纹按相对路径、字节数和 SHA-256 比较。只将核过范围的独特证据写入本包；'
             '外部报告、其目录结构及个人项目设计不替代现有主报告。</p>'
             '<div class="note">本轮新增完整简历附件 0 份、源码附件 0 份。原有 25 个项目的横向比较分母保留，'
             '技术文档和框架说明另列；所有第三方项目仍未运行。个人项目设计继续暂缓。</div>')
    totals = mapping_data.get('current_totals', {})
    if isinstance(totals, dict) and totals:
        body += '<p class="muted">主库当前统计：' + E(text(totals)) + '。</p>'
    body += '</section>'

    body += ('<section id="interviews"><h2>新增面经：事件时间与发表日期分开</h2>'
             '<p>近期实习只按可证实的招聘事件时间归类；页面编辑时间、届次及文章发表时间不补面试年份。'
             'SSP、SP、未分档 offer、OC/意向、失败和结果未知保留原分类。</p>')
    groups = ['近期明确实习（后端/Agent工程）', '近期实习 AI Infra 对照', '事件年份未知', '校招及混合批次', '转正材料',
              '其他明确年份实习', '其他或招聘类型未知']
    if not new_interviews:
        body += '<p>本轮没有新增面经逻辑资料；既有面经的补证见去重清单。</p>'
    for name in groups:
        items = [(mapping, record) for mapping, record in new_interviews if interview_group(record) == name]
        if items:
            body += f'<h3>{E(name)}（{len(items)}）</h3>'
            if name == '近期实习 AI Infra 对照':
                body += '<p class="note">AI Infra 的 CUDA、算子与推理调度材料单列，不计入本轮后端/Agent应用工程近期实习组，也不作为应用工程统一要求。</p>'
            body += interview_table(items)
    body += '</section>'

    body += '<section id="selections"><h2>新增候选人及观点正文选读</h2>'
    case_pairs = [(mapping, record) for mapping, record in new_pairs
                  if str(mapping.get('source_id', '')).startswith('R')
                  and '候选人' in category(mapping, record)]
    opinion_pairs = [(mapping, record) for mapping, record in new_pairs
                     if str(mapping.get('source_id', '')).startswith(('R', 'V'))
                     and (mapping, record) not in case_pairs]
    if case_pairs:
        body += '<h3>候选人与对照材料（' + str(len(case_pairs)) + '）</h3>'
        body += '<p>下面包括成功自述及结果未知的对照材料。正文中的局部履历、本人项目叙述与简历附件分别看待；本轮未新增完整简历实物。</p>'
        for mapping, record in case_pairs:
            body += selection_panel(mapping, record, manifest)
    if opinion_pairs:
        body += '<h3>专业观点正文选读（' + str(len(opinion_pairs)) + '）</h3>'
        body += '<p>按实际读到的图文或正文段落评价；未观看视频，也不以其他作者/站点内容代替受限原文。</p>'
        for mapping, record in opinion_pairs:
            body += selection_panel(mapping, record, manifest)
    if manual:
        body += '<h3>保留给用户自行查看的入口（' + str(len(manual)) + '）</h3><ul>'
        for mapping, record in manual:
            body += '<li>' + html_link(mapping.get('url', ''), mapping.get('title', '原始入口'))
            body += '：' + E(text(mapping.get('boundary', '本次未取得正文'))) + '</li>'
        body += '</ul>'
    if commercial:
        body += '<h3>另列商业背景参考</h3><ul>'
        for mapping, record in commercial:
            body += '<li>' + html_link(mapping.get('url', ''), mapping.get('title', '原始介绍'))
            body += '：' + E(text(mapping.get('boundary', '卖方材料不计成功者证据'))) + '</li>'
        body += '</ul>'
    body += '</section>'

    body += ('<section id="documents"><h2>新增官方文档与工程参考</h2>'
             '<p>以下按指定章节、README 或许可文本的实读范围呈现，不能推成已审查完整仓库、'
             '生产部署或成功候选人本人的项目。</p>')
    for info in new_docs:
        mapping = info['mapping']
        body += '<article class="panel"><h3>' + E(mapping.get('title', '')) + ' · ' + unified_link(mapping) + '</h3>'
        for label, value in [('实际阅读范围', info['scope']),
                             ('指定模块', '；'.join(info['modules']) or '依原文已读范围；未取得更细模块定位'),
                             ('阅读价值', '；'.join(info['findings']) or '保留入口，尚无足够实读发现'),
                             ('局限', '；'.join(info['limits']) or '仅限指定阅读范围；未执行或验证生产适用性')]:
            body += '<p><b>' + E(label) + '：</b>' + E(value) + '</p>'
        if info['segments']:
            body += '<p><b>原核读段与短依据：</b></p><ul>'
            for segment in info['segments']:
                body += '<li>' + E(text(segment['read_scope'])) + '：' + E(text(segment['short_original_basis']))
                body += ' ' + html_link(segment['read_url'], '核读原文') + '</li>'
            body += '</ul>'
        body += '<p>' + ' · '.join(html_link(url, '原始文档') for url in info['urls'][:8]) + '</p></article>'
    if not new_docs:
        body += '<p>本轮没有新增独立文档；已有框架的补读范围见去重清单。</p>'
    if judgments:
        body += '<h3>吸收的技术判断</h3><ul>'
        for item in judgments:
            body += '<li>' + E(item['finding']) + ' ' + unified_link(item['info']['mapping']) + '</li>'
        body += '</ul>'
    body += '<p>' + html_link('../06_项目分析与推荐/外部调研_文档判断与阅读模块.md', '文档判断与具体阅读模块') + '</p></section>'

    body += '''<section id="catalog"><h2>64 条来源与目标资料映射</h2>
<p>每个外部来源只映射到一个主库资料 ID；复用、补证与新增分别标记。受限项保留原始链接。</p>
<div class="merge-controls"><label>搜索 <input id="merge-query" type="search" placeholder="标题、来源 ID、目标 ID、边界"></label>
<label>类别 <select id="merge-category"><option value="">全部</option>'''
    categories = sorted({category(mapping, record) for mapping, record in pairs})
    for value in categories:
        body += '<option value="' + E(value) + '">' + E(value) + '</option>'
    body += '''</select></label><label>处理 <select id="merge-action"><option value="">全部</option>
<option value="new">新增</option><option value="reuse">复用/补核</option><option value="manual">待手动访问</option>
<option value="commercial">商业背景参考</option><option value="restricted">仅看受限/摘要</option>
</select></label><button id="merge-reset" type="button">重置</button><span>显示 <b id="merge-shown">64</b>/64</span></div>
<div class="scroll"><table id="merge-table"><thead><tr><th>来源 ID</th><th>标题与类别</th><th>处理</th>
<th>统一报告</th><th>阅读范围与边界</th><th>原始来源</th></tr></thead><tbody>'''
    for mapping, record in pairs:
        kind = disposition(mapping, new_ids)
        new = kind == 'new'
        block = restricted(mapping, record, manifest)
        cat = category(mapping, record)
        raw_action = text(mapping.get('action', ''))
        action = {'new': '新增摘要/待核入口' if block else '新增原文资料', 'reuse': '复用/补核',
                  'manual': '待手动访问', 'commercial': '商业背景参考'}[kind]
        boundary = text(get(mapping, 'boundary', default=get(record, 'limitations', 'limits', default='未核')))
        search = text([mapping.get('source_id'), mapping.get('destination_id'), mapping.get('title'),
                       cat, raw_action, boundary, reading_scope(mapping, record, manifest)]).lower()
        body += ('<tr class="merge-row" data-search="' + E(search) + '" data-category="' + E(cat)
                 + '" data-action="' + kind + '" data-restricted="'
                 + ('yes' if block else 'no') + '"><td>' + E(mapping.get('source_id', ''))
                 + '</td><td>' + E(mapping.get('title', record.get('title', ''))) + '<br><small>' + E(cat)
                 + '</small></td><td>' + E(action) + ('<br><b>原文受限/仅摘要</b>' if block else '')
                 + '</td><td>' + unified_link(mapping) + '</td><td>' + E(reading_scope(mapping, record, manifest))
                 + '<br><small>' + E(boundary) + '</small></td><td>'
                 + html_link(mapping.get('url', record.get('url', '')), '原始来源') + '</td></tr>')
    body += '</tbody></table></div></section>'
    body += '''<style>.merge-controls{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:16px 0}
.merge-controls input,.merge-controls select,.merge-controls button{font:inherit;padding:7px;border:1px solid var(--line);border-radius:5px}
.merge-controls input{min-width:260px}.merge-row[hidden]{display:none}article.panel{margin:16px 0}
@media screen{.scroll table{min-width:940px}}
@media print{.merge-controls{display:none}.scroll{overflow:visible}.scroll table{min-width:0}table{font-size:10px}tr{break-inside:avoid}}</style>
<script>(()=>{const rows=[...document.querySelectorAll('.merge-row')];
const q=document.getElementById('merge-query'),c=document.getElementById('merge-category'),a=document.getElementById('merge-action');
function apply(){let n=0;const query=q.value.trim().toLocaleLowerCase();for(const row of rows){
const hit=(!query||row.dataset.search.includes(query))&&(!c.value||row.dataset.category===c.value)&&
(!a.value||(a.value==='restricted'?row.dataset.restricted==='yes':row.dataset.action===a.value));row.hidden=!hit;if(hit)n++;}
document.getElementById('merge-shown').textContent=n;}
q.addEventListener('input',apply);c.addEventListener('change',apply);a.addEventListener('change',apply);
document.getElementById('merge-reset').addEventListener('click',()=>{q.value='';c.value='';a.value='';apply()});apply();})();</script>'''

    # 所有数据、目标 ID 和源目录指纹核对成功后，才写两个明确的交付文件。
    PAGE.parent.mkdir(parents=True, exist_ok=True)
    MODULES.parent.mkdir(parents=True, exist_ok=True)
    PAGE.write_text(shell(TITLE, body), encoding='utf-8', newline='\n')
    MODULES.write_text(markdown_documents(docs, judgments), encoding='utf-8', newline='\n')
    print(json.dumps({'page': PAGE.as_posix(), 'modules': MODULES.as_posix(),
                      'mappings': len(mappings), 'new': len(new_pairs), 'reused': len(reused),
                      'manual': len(manual), 'commercial': len(commercial),
                      'restricted': len(blocked), 'new_interviews': len(new_interviews),
                      'new_documents': len(new_docs), 'source_fingerprint_verified': source['verified']},
                     ensure_ascii=False))


if __name__ == '__main__':
    generate()
