"""合并已核外部资料；源目录只读，不重跑旧批次构造器。"""
from collections import Counter
from copy import deepcopy
from html import escape
from pathlib import Path
import csv
import hashlib
import importlib.util
import io
import json
import re

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
SOURCE = Path('C:/Users/GW/Downloads/astra/backend_agent_research_2026-10-24')
DATE = '2026-10-24'
spec = importlib.util.spec_from_file_location('merge_io', BASE / '整合需求纠偏.py')
util = importlib.util.module_from_spec(spec)
spec.loader.exec_module(util)
load, dump, write = util.load, util.dump, util.write


def group(rows):
    return {'total': len(rows), **{k: dict(Counter(r['taxonomy'][k] for r in rows))
            for k in ['track', 'recruitment', 'recent_status']},
            'reading_scope': dict(Counter(r['reading']['scope'] for r in rows)),
            'fulltext_count': sum(bool(r['reading']['fulltext']) for r in rows)}


def values(value):
    if isinstance(value, list):
        return value
    return [str(value)] if value else []


def joined(value):
    return util.flatten(value) if isinstance(value, (list, dict)) else str(value or '')


def taxonomy(track, recruitment, event, source_date, known=False, basis='原文未直接给出事件年', recent=None):
    return {'track': track, 'recruitment': recruitment, 'experience_date_text': event,
            'date_precision': '范围' if known else '未知', 'year_confirmed': bool(known),
            'recent_status': recent or ('近期确认' if known else '年份未知'),
            'source_date_text': source_date, 'date_basis': basis}


def reading(scope, note):
    scope = scope if scope in ['全文', '部分', '摘要', '未读'] else '部分'
    return {'scope': scope, 'fulltext': scope == '全文', 'scope_note': note, 'video_watched': False}


def provenance(x):
    return {'source_folder': SOURCE.as_posix(), 'source_id': x['source_id'], 'merged_on': DATE,
            'review_manifest': '08_证据索引与统计/' + x['_manifest'],
            'scope_boundary': '本包核读与外部卡片自述分别记录；原目录保持原样。'}


def source_review(x):
    return {k: deepcopy(v) for k, v in x.items() if k not in ['body', 'header', '_manifest']}


def make_job(x, original):
    f = original['fields']; access = x.get('live_access', {})
    full = bool(access.get('fulltext'))
    tx = taxonomy(x.get('track', '未知'), x.get('recruitment', '实习'),
                  x.get('publish_date', f.get('来源与时间', '未核')), x.get('publish_date', '未核'),
                  x.get('date_year_confirmed', False), x.get('source_date_basis', '原文日期/窗口'))
    title = original['title']
    company = title.split(' ')[0]
    return {'category': '招聘JD', 'title': title, 'company': company, 'role_type': f.get('方向与资格', ''),
            'url': original['url'], 'publish_date': tx['source_date_text'], 'retrieved_date': DATE,
            'source_type': x.get('source_type', '外部调研入口；身份未核'),
            'own_summary': x.get('duties', f.get('工作摘要', '')),
            'required_stack': x.get('required_stack', []), 'preferred_stack': x.get('preferred_stack', []),
            'degree_constraint': x.get('degree_constraint', '未核'),
            'availability_constraint': x.get('availability_constraint', '未核'),
            'recruiting_status': x.get('recruiting_status', f.get('岗位状态', '未核')),
            'matrix_include': bool(full and x.get('matrix_include')), 'duties': x.get('duties', ''),
            'recommendation': x.get('recommendation', f.get('推荐理由', '')),
            'limitations': x.get('limitations', f.get('局限', '')),
            'access_level': '正文全文' if full else '仅外部调研摘要；本轮原页受限',
            'taxonomy': tx, 'reading': reading('全文' if full else '摘要', access.get('read_scope', '未取得原文')),
            'outcomes': [], 'tags': x.get('required_stack', []) + x.get('preferred_stack', []),
            'source_record': source_review(x)}


def make_interview(x, original):
    f = original['fields']
    scope = x.get('read_scope', x.get('reading_scope', '部分'))
    if isinstance(scope, dict):
        note = scope.get('scope_note', '')
        scope = scope.get('scope', '部分')
    else:
        note = x.get('reading_boundary', x.get('reading_note', x.get('scope_note', '已定位作者正文；问题为归纳，非录音逐字稿')))
    track = '算法对照' if x.get('track') == 'AI Infra对照' else x.get('track', '后端')
    tx = taxonomy(track, x.get('recruitment', '未知'),
                  x.get('event_date', '事件年份未知'), x.get('source_date', '未核'),
                  x.get('event_year_confirmed', False), x.get('date_basis', '不以编辑日期替代面试年份'),
                  x.get('recent_status'))
    questions = values(x.get('questions', x.get('questions_paraphrased', [])))
    topics = values(x.get('topics', []))
    result = x.get('result', f.get('轮次与结果', '未披露'))
    status = x.get('result_status', 'unknown')
    strict = tx['recruitment'] == '实习' and tx['year_confirmed'] and tx['recent_status'] == '近期确认'
    summary = f.get('事实摘要', '')
    return {'category': '面经复盘', 'title': original['title'], 'url': original['url'],
            'company': x.get('company', f.get('公司与类型', '').split('；')[0]),
            'role': x.get('role', f.get('公司与类型', '')), 'date': tx['experience_date_text'],
            'source_date': tx['source_date_text'], 'taxonomy': tx, 'reading': reading(scope, note),
            'fulltext_verified': scope == '全文',
            'material_type': x.get('material_type', '面经与整理/协作笔记混合' if x.get('ai_organized') else '本人具体问题记录'),
            'candidate_link_ids': x.get('candidate_link_ids', []), 'strict_recent_internship': strict,
            'publication_recent_event_year_unknown': False,
            'sample_group': '明确事件年实习' if strict else ('明确实习、事件年未知' if tx['recruitment'] == '实习' else tx['recruitment'] + '对照'),
            'result_status': status, 'outcome': result,
            'outcomes': [{'company': x.get('company', f.get('公司与类型', '').split('；')[0]),
                          'role': x.get('role', f.get('公司与类型', '')), 'grade': '未披露',
                          'status': status, 'date': tx['experience_date_text'], 'evidence_url': x.get('resolved_url', original['url']),
                          'basis': result, 'applies_to_this_interview': True, 'independent_employer_verified': False}],
            'rounds': [{'round': x.get('rounds_text', f.get('轮次与结果', '原帖所列流程')),
                        'questions': questions, 'outcome': result}],
            'topics': topics, 'project_questions': questions, 'summary': summary,
            'commercial_bias': x.get('commercial_bias', x.get('commercial_background', '仅核定位正文；未对作者全部商业关系审计')),
            'recommendation': x.get('recommendation', f.get('阅读价值', '')),
            'limitations': x.get('limitations', f.get('可读性与限制', '')),
            'ai_organized': bool(x.get('ai_organized')), 'ai_marker_basis': x.get('ai_marker_basis', ''),
            'same_author_relations': x.get('same_author_relations', []),
            'related_record_ids': x.get('related_record_ids', []), 'source_record': source_review(x)}


def node(url, basis, gap='', relation='直接点名'):
    return {'url': url, 'direct_basis': basis, 'gap': gap, 'relation': relation}


def make_candidate(x, original):
    f = original['fields']
    source_tax = x.get('taxonomy', {})
    known = bool(source_tax.get('event_year'))
    event = x.get('event_date', ('2026-01面试；2025-12开始投递' if x['source_id'] == 'R04' else '原文未直接给出招聘事件年'))
    tx = taxonomy(source_tax.get('track', '后端'), source_tax.get('recruitment', '未知'),
                  event, x.get('source_date', f.get('时间及可读性', '未核')),
                  known, source_tax.get('date_basis', '不能据发表或届别补事件年'),
                  x.get('recent_status'))
    source_dates = {'R02': '页面2023-11-10编辑；不等于招聘事件日期',
                    'R04': '页面04-05编辑，展示年未核；正文另明确2025-12投递及2026-01面试',
                    'R05': '页面2025-05-31编辑；本轮未读取简历图',
                    'R08': '页面2025-07-08编辑；招聘事件年未知'}
    tx['source_date_text'] = source_dates.get(x['source_id'], tx['source_date_text'])
    profile = x.get('profile_type', '经历/求职自述（非简历原件）')
    scope = x.get('reading_scope', '部分')
    if scope not in ['全文', '部分', '摘要', '未读']:
        scope = '全文' if x.get('fulltext') else '部分'
    result = x.get('outcome', x.get('result', x.get('status', f.get('录用状态', '未披露'))))
    out = x.get('outcomes', [])
    for outcome in out:
        outcome.setdefault('date', tx['experience_date_text'])
        outcome.setdefault('evidence_url', original['url'])
        outcome.setdefault('role', '后端开发；具体岗位按本人原文')
        outcome.setdefault('independent_employer_verified', False)
        outcome['status'] = {'intent_self_report': 'intention_self_report', 'rejected_self_report': 'failure_self_report'}.get(outcome['status'], outcome['status'])
        if outcome.get('grade') == '未知':
            outcome['grade'] = '未披露'
    if not out:
        out = [{'company': x.get('company', '原帖自述，逐公司见来源'), 'role': x.get('role', '后端'),
                'grade': '未披露', 'status': x.get('result_status', 'unknown'),
                'date': tx['experience_date_text'], 'basis': result, 'evidence_url': original['url'],
                'independent_employer_verified': False}]
    projects = values(x.get('personal_project_summary', x.get('projects', f.get('项目事实摘要', ''))))
    chain = {'outcome': [node(original['url'], result, '录用仅本人自述；未披露档位不标SSP')],
             'profile': [node(original['url'], x.get('profile_boundary', f.get('实际简历情况', profile)), '本轮没有新增完整CV实物')],
             'project': [node(original['url'], f.get('项目事实摘要', ''), '仅作者描述；未取得本人源码，不拼接框架')],
             'interview': [node(original['url'], x.get('interview_boundary', '同篇经历中出现面试描述'),
                                '是否逐轮具体问题仅按实际阅读，不与其他作者拼接')]}
    return {'category': '候选人资料', 'title': original['title'], 'url': original['url'],
            'role': x.get('role', '后端开发'), 'date': tx['experience_date_text'], 'source_date': tx['source_date_text'],
            'taxonomy': tx, 'reading': reading(scope, x.get('reading_boundary', x.get('reading_scope', '本人公开文字正文；简历图片未作本轮新读图'))),
            'outcome': result, 'outcomes': out, 'profile_type': profile, 'document_type': profile,
            'stack': values(x.get('stack', f.get('技术关键词', ''))), 'projects': projects,
            'source_summary': x.get('personal_project_summary', f.get('项目事实摘要', '')), 'original_analysis': x.get('unique_value', f.get('推荐理由', '')),
            'strengths': values(x.get('strengths', f.get('推荐理由', ''))),
            'weaknesses': values(x.get('facts_boundary', x.get('limitations', f.get('不足与风险', '')))),
            'recommendation': f.get('推荐理由', ''), 'commercial_bias': x.get('commercial_bias', '依据本人公开叙述；存在主动分享与结果选择偏差'),
            'chain': chain, 'chain_gaps': [n['gap'] for ns in chain.values() for n in ns if n.get('gap')],
            'has_confirmed_personal_interview_source': x.get('import_target') == 'candidate_and_interview_evidence',
            'has_direct_named_project_or_contribution': False, 'ssp_claim_present': bool(x.get('ssp_claim_present', False)),
            'ssp_grade_company_explicit': bool(x.get('ssp_grade_company_explicit', False)),
            'complete_cv_file_received': False, 'complete_redacted_cv_file_received': False,
            'cv_file_licensed_for_redistribution': False, 'personal_source_code_verified': False,
            'source_record': source_review(x)}


def make_reference(x, original):
    f = original['fields']; sid = x['source_id']
    project = sid.startswith('P')
    platform = sid.startswith('V') and sid not in ['V07', 'V08']
    category = '官方技术资料' if project else 'B站与知乎' if platform else '专业原文补充'
    scope = x.get('reading_scope', '部分')
    if scope not in ['全文', '部分', '摘要', '未读']:
        scope = '部分'
    text = x.get('opinion', x.get('unique_value', x.get('analysis', f.get('可见观点', f.get('功能摘要', f.get('项目事实摘要', ''))))))
    track = x.get('track', 'Agent工程' if project or sid in ['R06', 'V05', 'V07', 'V08'] else '混合')
    identity = f.get('身份与利益', '来源为项目官方仓库或官方文档；非成功求职者作品证明' if project else '个人署名专业/教学正文；职业背景仅公开自述')
    return {'category': category, 'title': original['title'], 'url': original['url'],
            'platform': '牛客个人教学正文' if sid == 'R06' else x.get('platform', f.get('作者与平台', '官方仓库/文档补充' if project else '作者原站')),
            'author': x.get('author', f.get('作者与平台', '项目维护者' if project else '原文署名作者')),
            'date': f.get('日期', '文档版本以核读清单为准'),
            'taxonomy': taxonomy(track, '不适用', '技术文档/教学观点，非招聘事件', DATE, False,
                                 '不把文档读取日期当招聘事件', '不适用'),
            'reading': reading(scope, x.get('reading_boundary', x.get('read_scope', x.get('reading_scope', f.get('访问程度', f.get('已核实范围', '本次指定内容核读')))))),
            'outcomes': [], 'opinion': joined(text),
            'identity_evidence': '个人署名教学原文；字节offer仅自述，200+及xx%是写法示范，未建立真实项目成绩关系。' if sid == 'R06' else x.get('identity_evidence', identity),
            'commercial_bias': x.get('commercial_context', x.get('commercial_bias', f.get('商业背景', f.get('身份与利益', '项目供应商或作者自述；不视为独立效果验证')))),
            'limits': values(x.get('facts_boundary', x.get('limitations', f.get('限制', f.get('不宜照搬', '文档能力不等于运行结果'))))),
            'recommendation': x.get('recommendation', f.get('推荐理由', '')),
            'platform_native_fulltext_verified': bool(platform and x.get('platform_native_fulltext_verified')),
            'verified_video_viewing': False, 'source_record': source_review(x),
            'source_nature_boundary': '教学/官方能力或卖方介绍；不当本人SSP项目，不计新增源码附件或25项目实现审查分母。'}


def main():
    fingerprint = load('astra来源_合并前文件指纹.json')
    expected = {f['path']: f for f in fingerprint['files']}
    current = {p.relative_to(SOURCE).as_posix(): p for p in SOURCE.rglob('*') if p.is_file()}
    assert current.keys() == expected.keys(), '来源目录文件集合改变，停止合并'
    assert all(p.stat().st_size == expected[name]['bytes'] and
               hashlib.sha256(p.read_bytes()).hexdigest() == expected[name]['sha256']
               for name, p in current.items()), '来源目录文件内容改变，停止合并'
    original = {r['id']: r for r in json.loads((SOURCE / '07_数据与方法/资料索引.json').read_text(encoding='utf-8-sig'))}
    reviews = []
    for name in ['astra合并_JD核对.json', 'astra合并_面经核对.json', 'astra合并_候选人与观点项目.json']:
        d = load(name)
        assert d.get('status') != '核读中', name
        for r in d['records']:
            r = deepcopy(r); r['_manifest'] = name; reviews.append(r)
    assert len(reviews) == 64 and len({r['source_id'] for r in reviews}) == 64
    rows = load('all_evidence_records.json'); by = {r['id']: r for r in rows}
    before = load('需求覆盖统计.json')
    initial = {r['id'] for r in rows if not r.get('source_key', '').startswith('ASTRA_')}
    counters = {p: max([int(re.sub(r'\D', '', r['id'])) for r in rows if re.fullmatch(p + r'\d+', r['id'])] or [0]) for p in ['JD', 'INT', 'CV', 'OP', 'DOC', 'OBS']}
    mappings = []; new_ids = []
    for x in reviews:
        sid = x['source_id']; src = original[sid]
        existing = x.get('existing_id')
        if isinstance(existing, list):
            existing = existing[0] if existing else None
        decision = x.get('decision', 'new')
        if existing and existing in by:
            for mapped_id in x.get('existing_ids', [existing]):
                if mapped_id in by:
                    by[mapped_id].setdefault('external_research_reviews', {})[sid] = {'provenance': provenance(x), 'review': source_review(x)}
            mappings.append({'source_id': sid, 'destination_id': existing, 'action': '重复核读/补充说明',
                             'original_decision': decision, 'title': src['title'], 'url': src['url'],
                             'boundary': x.get('facts_boundary', x.get('enrichment_note', x.get('limitations', '不新增逻辑资料计数')))})
            continue
        if x.get('import_target') in ['manual_only', 'commercial_context_only']:
            mappings.append({'source_id': sid, 'destination_id': None,
                             'action': '待手动访问' if x['import_target'] == 'manual_only' else '商业背景参考',
                             'title': src['title'], 'url': src['url'],
                             'boundary': x.get('status', '') + '；' + x.get('facts_boundary', '')})
            continue
        if decision in ['rejected', 'exclude', 'duplicate']:
            mappings.append({'source_id': sid, 'destination_id': None, 'action': '保留核查记录',
                             'title': src['title'], 'url': src['url'], 'boundary': x.get('limitations', x.get('reason', '不新增计数'))})
            continue
        if sid.startswith('J'):
            prefix = 'JD'; r = make_job(x, src)
        elif sid.startswith('I'):
            # 没有定位并实际核读作者正文的帖子只留手动入口。
            if x.get('read_scope', x.get('reading_scope')) in ['未读', '摘要'] or x.get('decision') in ['manual', 'pending']:
                mappings.append({'source_id': sid, 'destination_id': None, 'action': '待手动访问',
                                 'title': src['title'], 'url': src['url'], 'boundary': x.get('limitations', '原页未取得正文，不计已读面经')})
                continue
            prefix = 'INT'; r = make_interview(x, src)
        elif sid.startswith('R') and sid != 'R06':
            prefix = 'CV'; r = make_candidate(x, src)
            if x.get('import_target') == 'candidate_control_and_manual_resume':
                prefix = 'OBS'; r['category'] = '候选人对照'
                r['source_summary'] = '本轮只读文字分享与简历图片入口；图内项目和性能细节仅为外部卡片主张，本包未独立图核。'
                r['stack'] = []; r['projects'] = []
                r['recommendation'] = '外部摘要提到网盘/RPC互补结构；仅作待图核线索，不算本包已读简历或本人实现。'
                r['chain']['profile'] = [node(src['url'], '文字正文有公开简历图片入口；本轮未读取图片', '图内专业模块与脱敏范围待人工核对')]
                r['chain']['project'] = [node(None, '未核简历图与本人项目', '外部摘要不能冒充本包已核履历', '未建立')]
                r['chain']['interview'] = [node(None, '所读文字是收藏分享，外链面经不能算本人面经', '未定位本人面经', '未建立')]
                r['chain_gaps'] = [n['gap'] for ns in r['chain'].values() for n in ns if n.get('gap')]
        else:
            prefix = 'DOC' if sid.startswith('P') or sid in ['R06', 'V07', 'V08'] else 'OP'
            r = make_reference(x, src)
        key = 'ASTRA_' + sid + '_20261024'
        prior = next((q for q in rows if q.get('source_key') == key), None)
        if prior:
            rid = prior['id']; by[rid].update(r); r = by[rid]
        else:
            counters[prefix] += 1; rid = prefix + f'{counters[prefix]:02d}'
            r['id'] = rid; r['source_key'] = key; rows.append(r); by[rid] = r
        r['id'] = rid; r['source_key'] = key; r['external_import'] = provenance(x)
        new_ids.append(rid)
        mappings.append({'source_id': sid, 'destination_id': rid, 'action': '新增原文资料' if r['reading']['scope'] in ['全文', '部分'] else '新增摘要/待核入口',
                         'title': src['title'], 'url': src['url'], 'category': r['category'],
                         'reading_scope': r['reading']['scope'], 'boundary': x.get('limitations', '')})
    cvs = [r for r in rows if r['category'] == '候选人资料']
    ivs = [r for r in rows if r['category'] == '面经复盘']
    jobs = [r for r in rows if r['category'] == '招聘JD']
    ops = [r for r in rows if r['category'] == 'B站与知乎']
    stats = deepcopy(before)
    stats['updated_date'] = DATE; stats['current_pass'] = '外部调研核读合并'
    cvstat = {**stats['candidate_coverage'], **group(cvs)}
    for k, flag in [('complete_cv_files_received', 'complete_cv_file_received'), ('complete_redacted_cv_files_received', 'complete_redacted_cv_file_received'),
                    ('confirmed_personal_interview_source_cases', 'has_confirmed_personal_interview_source'), ('ssp_claim_cases', 'ssp_claim_present'), ('ssp_company_explicit_cases', 'ssp_grade_company_explicit')]:
        cvstat[k] = sum(bool(r.get(flag)) for r in cvs)
    cvstat['profile_type'] = dict(Counter(r['profile_type'] for r in cvs))
    strict = [r['id'] for r in ivs if r.get('strict_recent_internship')]
    aux = [r['id'] for r in ivs if r.get('publication_recent_event_year_unknown')]
    ivstat = {**stats['interview_coverage'], **group(ivs),
              'strict_recent_explicit_internship_count': len(strict), 'strict_recent_explicit_internship_ids': strict,
              'explicit_internship_all_years_count': sum(r['taxonomy']['recruitment'] == '实习' for r in ivs),
              'explicit_internship_event_year_unknown_count': sum(r['taxonomy']['recruitment'] == '实习' and r['taxonomy']['recent_status'] == '年份未知' for r in ivs),
              'publication_recent_event_year_unknown_count': len(aux), 'publication_recent_event_year_unknown_ids': aux,
              'mixed_recruitment_count': sum(r['taxonomy']['recruitment'] == '混合' for r in ivs),
              'unconfirmed_recruitment_count': sum(r['taxonomy']['recruitment'] == '未知' for r in ivs),
              'result_status': dict(Counter(r['result_status'] for r in ivs)),
              'material_type': dict(Counter(r['material_type'] for r in ivs)), 'read_source_material_count': len(ivs),
              'denominator_note': f'{len(ivs)}份逻辑资料；不是独立候选人或成功人数；同作者和AI整理分别标注。'}
    ivstat['strict_recent_engineering_internship_ids'] = [r['id'] for r in ivs if r.get('strict_recent_internship') and r['taxonomy']['track'] != '算法对照']
    ivstat['strict_recent_engineering_internship_count'] = len(ivstat['strict_recent_engineering_internship_ids'])
    ivstat['strict_recent_control_internship_count'] = len(strict) - ivstat['strict_recent_engineering_internship_count']
    jobstat = {**stats['job_coverage'], **group(jobs),
               'strict_recent_explicit_internship_count': sum(r['taxonomy']['recruitment'] == '实习' and r['taxonomy']['year_confirmed'] for r in jobs),
               'first_party_engineering_matrix_fulltext_count': sum(bool(r.get('matrix_include')) for r in jobs)}
    opstat = {**stats['opinion_coverage'], **group(ops)}
    native = [r for r in ops if r.get('platform_native_fulltext_verified')]
    opstat.update({'primary_bilibili_or_zhihu_full_content_verified_count': len(native),
                   'bilibili_native_articles_read': sum('B站' in r.get('platform', '') for r in native),
                   'zhihu_native_fulltexts_read': sum('知乎' in r.get('platform', '') for r in native)})
    stats.update({'candidate_coverage': cvstat, 'interview_coverage': ivstat, 'job_coverage': jobstat,
                  'opinion_coverage': opstat, 'category_counts': dict(Counter(r['category'] for r in rows))})
    stats['totals'].update({'logical_evidence_records': len(rows), 'candidate_cases': len(cvs), 'interview_materials': len(ivs),
                            'jd_leads': len(jobs), 'engineering_jd_fulltext': jobstat['first_party_engineering_matrix_fulltext_count'],
                            'platform_opinion_records': len(ops),
                            'additional_primary_texts': sum(r['category'] == '专业原文补充' for r in rows)})
    blocked = load('待手动访问链接.json')
    # 同一帖的feed/discuss长短链接可并存；实读后的入口继续保留，但更新过期的未读状态。
    def post_key(url):
        match = re.search(r'/(feed/main/detail|discuss)/(\w+)', str(url))
        return match.group(0).lower() if match else str(url).split('?')[0].rstrip('/')
    for x in reviews:
        if not x['source_id'].startswith('I') or x.get('read_scope', x.get('reading_scope')) != '全文':
            continue
        m = next((m for m in mappings if m['source_id'] == x['source_id']), None)
        if not m or not m.get('destination_id'):
            continue
        aliases = {post_key(x.get(key, '')) for key in ['url', 'resolved_url'] if x.get(key)}
        aliases.add(post_key(original[x['source_id']]['url']))
        for item in blocked:
            if post_key(item['url']) not in aliases:
                continue
            if not item.get('status_before_external_merge'):
                item['status_before_external_merge'] = item.get('status', '')
            item['status'] = f"2026-10-24已核读作者主文全文，对应{m['destination_id']}；不再标记正文未取得。"
            item['to_verify'] = ['原文未披露的事件年、岗位/轮次与结果范围，具体见关联资料卡',
                                 '本人完整履历和项目源码；不由面经或同账号仓库补造关系']
            item['current_record_id'] = m['destination_id']
            item['updated_date'] = DATE
    for m in mappings:
        if m['action'] == '待手动访问' or (m.get('reading_scope') == '摘要' and m['source_id'].startswith('J')):
            if not any(q['url'].split('?')[0] == m['url'].split('?')[0] for q in blocked):
                blocked.append({'title': m['title'], 'url': m['url'], 'status': joined(m['boundary']),
                                'to_verify': '原文正文、作者、实际事件年份和结果；外部卡片摘要不代替正文'})
    stats['totals']['manual_links'] = len(blocked)
    added = [r for r in rows if r['id'] not in initial]
    delta = dict(Counter(r['category'] for r in added))
    stats['external_merge'] = {'date': DATE, 'source_cards': 64, 'new_by_category': delta,
                               'source_preservation': f'通过：{len(current)}个来源文件的路径、大小和SHA-256均与合并前一致',
                               'source_fingerprint_verified': True,
                               'project_document_references': sum(r['category'] == '官方技术资料' for r in added),
                               'design_imported': False, 'new_resume_files': 0, 'new_project_source_archives': 0}
    stats['current_round_summary'] = ('外部64张卡逐条去重并核读；本轮新增' + '、'.join(f'{n}份{k}' for k, n in delta.items())
                                     + '。重复来源补核说明不重复计数；受限正文保留手动链接。个人项目设计继续暂缓。')
    norm = load('统一样本分类与候选人关联.json')
    norm['updated_date'] = DATE
    norm['records'] = {'candidates': cvs, 'interviews': ivs, 'jobs': jobs, 'opinions': ops}
    norm['statistics'] = {'candidates': cvstat, 'interviews': ivstat, 'jobs': jobstat, 'opinions': opstat}
    cases = load('candidate_cases.json'); cases['cases'] = cvs; cases['counts'].update(cvstat); cases['counts']['curated_cases'] = len(cvs)
    routes = load('两方向阅读顺序.json')
    for direction in ['backend', 'agent']:
        tracks = ['后端', '混合'] if direction == 'backend' else ['Agent工程', '混合']
        eligible = [r for r in added if r['category'] == '面经复盘' and r['taxonomy']['track'] in tracks and r['taxonomy']['recruitment'] == '实习']
        routes[direction]['interview_ids'] = list(dict.fromkeys(routes[direction]['interview_ids'] + [r['id'] for r in eligible]))
        routes[direction]['interview_ids'].sort(key=lambda i: (0 if by[i].get('strict_recent_internship') else 1 if by[i]['taxonomy']['recruitment'] == '实习' else 2))
        new_candidates = [r['id'] for r in added if r['category'] == '候选人资料' and r['taxonomy']['track'] in tracks]
        routes[direction]['candidate_ids'] = list(dict.fromkeys(routes[direction]['candidate_ids'] + new_candidates))
    if 'CV33' not in routes['backend']['candidate_boundary']:
        routes['backend']['candidate_boundary'] += ' 本轮CV33为明确2026后端实习offer的经历选读；CV32为校招、CV34事件年未知，均无新增完整CV或本人源码。'
    routes['read_professional_ids'] = list(dict.fromkeys(routes['read_professional_ids'] +
        [r['id'] for r in added if r['category'] == 'B站与知乎' and r['reading']['scope'] in ['全文', '部分']]))
    routes['updated_date'] = DATE
    mapped = {m['source_id']: m['destination_id'] for m in mappings if m.get('destination_id')}
    for x in reviews:
        rid = mapped.get(x['source_id'])
        if not rid or not x['source_id'].startswith('I'):
            continue
        record = by[rid]
        if x.get('ai_organized'):
            record['ai_organized'] = True
            record['ai_marker_basis'] = x.get('ai_marker_basis', '')
            record['material_type'] = '面经与整理/协作笔记混合'
        record['same_author_relations'] = x.get('same_author_relations', [])
    related = [('I07', 'I17'), ('I11', 'INT29')]
    for left, right in related:
        left_id = mapped.get(left); right_id = mapped.get(right, right)
        if left_id in by and right_id in by:
            for a, b in [(left_id, right_id), (right_id, left_id)]:
                by[a]['related_record_ids'] = list(dict.fromkeys(by[a].get('related_record_ids', []) + [b]))
    ivstat['material_type'] = dict(Counter(r['material_type'] for r in ivs))
    abilities = load('能力要求四类证据对照.json')
    ability_by = {a['id']: a for a in abilities['rows']}
    for x in reviews:
        rid = mapped.get(x['source_id'])
        if not rid or not x['source_id'].startswith('I'):
            continue
        for cap in x.get('capability_ids', []):
            if cap in ability_by:
                a = ability_by[cap]
                a['interview_ids'] = list(dict.fromkeys(a['interview_ids'] + [rid]))
    jd_caps = {
        'CAP01': ['J02', 'J03', 'J04', 'J05', 'J06', 'J07', 'J08', 'J09', 'J12', 'J15'],
        'CAP02': ['J02', 'J04', 'J06', 'J12'], 'CAP03': ['J02', 'J04'], 'CAP04': ['J02', 'J04'],
        'CAP05': ['J02', 'J05'], 'CAP06': ['J08', 'J09'], 'CAP07': ['J04', 'J05', 'J06', 'J07', 'J09'],
        'CAP08': ['J04', 'J05', 'J06', 'J09'], 'CAP09': ['J05', 'J08', 'J09'],
        'CAP10': ['J06', 'J07', 'J08'], 'CAP11': ['J04', 'J06', 'J08', 'J09']}
    for cap, sids in jd_caps.items():
        a = ability_by[cap]
        a['jd_ids'] = list(dict.fromkeys(a['jd_ids'] + [mapped[s] for s in sids if mapped.get(s) and by[mapped[s]].get('matrix_include')]))
    for a in abilities['rows']:
        for key, field in [('jd', 'jd_ids'), ('interview', 'interview_ids'), ('candidate', 'candidate_ids'), ('opinion', 'opinion_ids')]:
            a.setdefault('support', {})[key] = [{'id': rid, 'title': by[rid]['title'], 'url': by[rid]['url'],
                                                'taxonomy': by[rid]['taxonomy'], 'reading_scope': by[rid]['reading']['scope']}
                                               for rid in a[field]]
    abilities['updated_date'] = DATE
    for name, value in [('all_evidence_records.json', rows), ('candidate_cases.json', cases), ('interview_records.json', ivs),
                        ('统一样本分类与候选人关联.json', norm), ('需求覆盖统计.json', stats),
                        ('待手动访问链接.json', blocked), ('两方向阅读顺序.json', routes), ('能力要求四类证据对照.json', abilities)]:
        dump(name, value)
    topic = load('interview_topic_index.json')
    for t in topic['themes']:
        ids = [r['id'] for r in ivs if re.search(t['rule'], joined(r.get('topics', [])) + ' ' + joined(r.get('project_questions', [])), re.I)]
        t['evidence_ids'] = ids; t['record_count'] = len(ids)
        t['explicit_internship_ids'] = [rid for rid in ids if by[rid]['taxonomy']['recruitment'] == '实习']
        t['strict_recent_internship_ids'] = [rid for rid in ids if by[rid].get('strict_recent_internship')]
        t['year_unknown_internship_ids'] = [rid for rid in ids if by[rid]['taxonomy']['recruitment'] == '实习'
                                            and by[rid]['taxonomy']['recent_status'] == '年份未知']
    topic['scope_records'] = len(ivs); topic['updated_at'] = DATE
    dump('interview_topic_index.json', topic)
    util.csv_write(ROOT / '04_面经与专业观点/面经统一分类.csv',
                   ['ID', '标题', '方向', '招聘路径', '实际时间', '发表日期另列', '事件年已证', '近期状态', '阅读范围', '资料类型', '结果', '来源'],
                   [[r['id'], r['title'], r['taxonomy']['track'], r['taxonomy']['recruitment'], r['taxonomy']['experience_date_text'],
                     r['taxonomy']['source_date_text'], r['taxonomy']['year_confirmed'], r['taxonomy']['recent_status'], r['reading']['scope'],
                     r['material_type'], r.get('outcome', ''), r['url']] for r in ivs])
    util.csv_write(ROOT / '03_简历与候选人案例/候选人证据链对照.csv',
                   ['ID', '标题', '方向', '招聘路径', '事件时间', '近期状态', '结果自述', '资料类型', '录用证据', '履历证据', '项目贡献证据', '本人面经', '缺口'],
                   [[r['id'], r['title'], r['taxonomy']['track'], r['taxonomy']['recruitment'], r['taxonomy']['experience_date_text'],
                     r['taxonomy']['recent_status'], r.get('outcome', ''), r.get('profile_type', ''),
                     *[joined(r['chain'][stage]) for stage in ['outcome', 'profile', 'project', 'interview']], joined(r['chain_gaps'])] for r in cvs])
    util.csv_write(BASE / '全部资料统一分类.csv',
                   ['ID', '类别', '标题', '方向', '招聘路径', '实际事件时间', '来源时间', '事件年已证', '近期状态', '阅读范围', '来源'],
                   [[r['id'], r['category'], r['title'], r['taxonomy']['track'], r['taxonomy']['recruitment'],
                     r['taxonomy']['experience_date_text'], r['taxonomy']['source_date_text'], r['taxonomy']['year_confirmed'],
                     r['taxonomy']['recent_status'], r['reading']['scope'], r.get('url', '')] for r in rows])
    util.csv_write(BASE / '能力要求四类证据对照.csv',
                   ['能力', '后端相关性', 'Agent相关性', 'JD', '面经', '履历', '专业原文', '提问', '考察能力', '项目模块主题映射', '研究归纳薄弱点', '缺口'],
                   [[a['ability'], a['backend_relevance'], a['agent_relevance'],
                     *[';'.join(a[k]) for k in ['jd_ids', 'interview_ids', 'candidate_ids', 'opinion_ids']],
                     a['question'], a['competency'], a['module'], a['common_pitfall'], a['gap']] for a in abilities['rows']])
    util.csv_write(BASE / '面经主题索引.csv',
                   ['主题', '全包资料数', '明确实习资料数', '严格近期实习资料数', '实习事件年未知资料数', '全包资料ID', '严格近期ID'],
                   [[t['theme'], t['record_count'], len(t['explicit_internship_ids']), len(t['strict_recent_internship_ids']),
                     len(t['year_unknown_internship_ids']), ';'.join(t['evidence_ids']), ';'.join(t['strict_recent_internship_ids'])]
                    for t in topic['themes']])
    comp = load('项目统一比较与阅读优先级.json')
    for direction, title in [('backend', '后端实习阅读顺序'), ('agent', 'Agent实习阅读顺序')]:
        lines = ['# ' + title, '', '当前更新：' + DATE, '', routes['principle'], '',
                 routes[direction]['candidate_boundary'], '', '## 履历与面经', '']
        for ident in routes[direction]['candidate_ids'] + routes[direction]['interview_ids']:
            r = by[ident]
            lines += ['- [' + ident + ' ' + r['title'] + '](' + r['url'] + ')：' + r['taxonomy']['recruitment']
                      + '／' + r['taxonomy']['recent_status'] + '／' + r['reading']['scope'], '']
        lines += ['## 项目指定模块', '']
        for p in comp['projects']:
            q = p[direction + '_priority']
            if q['level'] == '非本方向':
                continue
            lines += ['- [' + p['id'] + ' ' + p['title'] + '](' + p['source_URL'] + ')｜' + q['level'] + '：' + q['reason'],
                      '  模块：' + '；'.join(q['read_modules']), '  边界：' + p['evidence_completeness'], '']
        lines += ['个人项目设计继续暂缓。', '']
        write(ROOT / '06_项目分析与推荐' / (title + '.md'), '\n'.join(lines))
    change = {'date': DATE, 'source_folder': SOURCE.as_posix(), 'source_card_count': 64, 'mappings': mappings,
              'new_ids': [r['id'] for r in added], 'new_by_category': delta, 'current_totals': stats['totals'],
              'new_cv_files': 0, 'new_source_archives': 0, 'design_imported': False,
              'boundary': '新增官方文档不纳25项目源码比较分母；录用与SSP仍按逐条自述，未知年份不补写。'}
    dump('astra合并_实施映射.json', change)
    if not (ROOT / '00_外部调研合并_更新说明.md').exists():
        write(ROOT / '00_外部调研合并_更新说明.md', '# 外部调研合并 · 2026-10-24\n\n' + stats['current_round_summary']
              + '\n\n新入口：[外部调研增补与去重清单](01_调研报告/外部调研增补与去重清单.html)。\n\n'
              + '原astra目录保留原样；4份源JSON另存只读来源快照。没有导入两套个人项目设计，没有新增完整简历附件或源码ZIP。\n')
    print(json.dumps({'new_by_category': delta, 'total': len(rows), 'mapped_cards': len(mappings)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
