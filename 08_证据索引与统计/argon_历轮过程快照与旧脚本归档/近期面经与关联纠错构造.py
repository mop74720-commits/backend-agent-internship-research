"""合入可核原帖；候选人总体录用与单场面经的范围分别保存。"""
from copy import deepcopy
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent


def update_manual(items):
    path = BASE / 'B站字幕访问_双路径复核.json'
    if not path.exists():
        return items
    for video in load(path.name)['records']:
        entry = {'title': video['title'], 'url': video['original_url'],
                 'status': '匿名pagelist及player/v2均HTTP200/code0；字幕列表为空，need_login_subtitle=true。原视频页访问412；未观看或核读字幕。',
                 'to_verify': ['用户可自行登录原平台观看或核对字幕；当前空列表不证明视频没有字幕。',
                               '具体观点、适用范围、作者职业与商业背景待实际内容核读。']}
        matches = [i for i in items if i['url'].rstrip('/') == entry['url'].rstrip('/')]
        if matches:
            matches[0].update(entry)
        else:
            items.append(entry)
    return items


def load(name):
    return json.loads((BASE / name).read_text(encoding='utf-8-sig'))


def apply(rows, comparison):
    data = load('近期面经与关联纠错_来源核读.json')
    snapshot = BASE / '近期面经与关联纠错前主数据快照.json'
    if not snapshot.exists():
        snapshot.write_text(json.dumps({'records': rows, 'comparison': comparison,
                                       'coverage': load('需求覆盖统计.json')}, ensure_ascii=False, indent=2), encoding='utf-8')
    by = {r['id']: r for r in rows}
    added = []
    for d in data['interviews']:
        known = d['year_confirmed']
        r = {'id': d['id'], 'source_key': d['source_key'], 'category': '面经复盘', 'title': d['title'],
             'url': d['url'], 'company': d['company'], 'role': d['role'], 'date': d['event_date'], 'source_date': d['source_date'],
             'taxonomy': {'track': '后端', 'recruitment': '实习', 'experience_date_text': d['event_date'],
                          'date_precision': '完整日期' if known else '未知', 'year_confirmed': known,
                          'recent_status': '近期确认' if known else '年份未知', 'source_date_text': d['source_date'],
                          'date_basis': d['date_basis']},
             'reading': {'scope': '全文', 'fulltext': True, 'scope_note': d['access']['scope'], 'video_watched': False},
             'fulltext_verified': True, 'material_type': '本人具体问题记录' if known else '面试问题与部分事后解答混合',
             'candidate_link_ids': [], 'strict_recent_internship': known, 'publication_recent_event_year_unknown': False,
             'sample_group': '明确事件年实习' if known else '明确实习、事件年未知',
             'result_status': d['result_status'], 'outcome': d['result'],
             'outcomes': [{'company': d['company'], 'role': d['role'], 'grade': '未披露', 'status': d['result_status'],
                           'date': d['event_date'], 'evidence_url': d['read_url'], 'basis': d['result'],
                           'applies_to_this_interview': True, 'independent_employer_verified': False}],
             'rounds': [{'round': '一面' if known else '二面', 'questions': d['questions_paraphrased'],
                         'outcome': d['result'], 'coding': d.get('coding_question', '字符串求和函数测试用例设计')}],
             'topics': d['topics'], 'project_questions': d['questions_paraphrased'], 'summary': d['reading_boundary'],
             'commercial_bias': d['commercial_background'], 'recommendation': d['recommended_use'], 'source_record': deepcopy(d)}
        if r['id'] in by:
            assert by[r['id']]['source_key'] == r['source_key'], r['id']
        by[r['id']] = r
        added.append(r['id'])
    # 同作者正文提供的招聘流程年份；不从编辑时间或届别补年。
    date_confirmations = []
    date_source = BASE / '实习事件年份补核_来源.json'
    if date_source.exists():
        review = load(date_source.name)
        evidence = next(d for d in review['records'] if d['id'] == 'INT68')
        assert evidence['primary']['public_author_path'] == evidence['supporting']['public_author_path']
        assert len(evidence['direct_relationship']['matching_event_nodes']) == 3
        r = by['INT68']
        before = deepcopy(r)
        decision = evidence['recommended_changes']
        r['date'] = decision['date']
        r['taxonomy'].update(decision['taxonomy'])
        r['taxonomy']['experience_date_text'] = decision['date']
        r['strict_recent_internship'] = True
        r['sample_group'] = '明确事件年实习'
        r['supporting_url'] = decision['supporting_url']
        r['event_date_verification'] = deepcopy(evidence)
        manifest = BASE / '实习事件年份补核_变更清单.json'
        if not manifest.exists():
            manifest.write_text(json.dumps({'id': 'INT68', 'before': before, 'after': r,
                'allowed_fields': ['date', 'taxonomy', 'strict_recent_internship', 'sample_group',
                                   'supporting_url', 'event_date_verification']},
                ensure_ascii=False, indent=2), encoding='utf-8')
        date_confirmations.append('INT68')
    changes = []
    for r in by.values():
        if r['category'] != '候选人资料':
            continue
        for index, outcome in enumerate(r.get('outcomes', [])):
            if 'applies_to_this_interview' not in outcome:
                continue
            changes.append({'id': r['id'], 'outcome_index': index, 'old_value': outcome.pop('applies_to_this_interview'),
                            'company': outcome.get('company'), 'grade': outcome.get('grade')})
            outcome['result_scope'] = '候选人总体录用自述；是否对应某一场面经，以该面经卡及直接关联证据为准'
    change_file = BASE / '近期面经与关联纠错_修正清单.json'
    if changes and not change_file.exists():
        change_file.write_text(json.dumps({'date': '2026-10-23', 'scope': data['candidate_outcome_correction'],
                                           'changes': changes}, ensure_ascii=False, indent=2), encoding='utf-8')
    return sorted(by.values(), key=lambda r: r['id']), comparison, {
        'added_ids': added, 'summary': data['summary'] + ('另由同作者投递总表补核INT68为2026年实习流程，保留登记与投递日期差别。' if date_confirmations else ''),
        'remaining': ['近期Agent SSP的具体岗位、招聘批次与本人履历/源码/面经关联仍不足。',
                      '已读B站图文和知乎正文按实际内容计入；视频/字幕未读仅为阅读范围，专业观点仍按背景、商业关系和技术依据分别评估。',
                      '部分实习面经事件年、项目源码与个人贡献范围仍缺；不能从编辑时间、第三方汇编或同账号仓库补齐。'],
        'source': data, 'date_confirmations': date_confirmations,
        'capabilities': {d['id']: d['capability_ids'] for d in data['interviews']}}
