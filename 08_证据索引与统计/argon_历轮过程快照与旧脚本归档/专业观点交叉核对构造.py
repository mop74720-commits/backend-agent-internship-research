"""将公开实录的定点阅读与交叉比较合入，平台外材料单列。"""
from copy import deepcopy
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent


def load(name):
    return json.loads((BASE / name).read_text(encoding='utf-8-sig'))


def apply(rows, comparison):
    data = load('专业观点交叉核对_来源与比较.json')
    snapshot = BASE / '专业观点交叉核对前主数据快照.json'
    if not snapshot.exists():
        snapshot.write_text(json.dumps({'records': rows, 'comparison': comparison,
                                       'coverage': load('需求覆盖统计.json')}, ensure_ascii=False, indent=2), encoding='utf-8')
    d = data['record']
    r = {'id': d['id'], 'source_key': d['source_key'], 'category': '专业原文补充',
         'title': d['title'], 'url': d['url'], 'author': d['author'],
         'platform': 'InfoQ／QCon原始演讲实录（平台外）',
         'taxonomy': {'track': 'Agent工程', 'recruitment': '不适用', 'experience_date_text': '专业演讲，非招聘事件',
                      'date_precision': '未知', 'year_confirmed': False, 'recent_status': '不适用',
                      'source_date_text': d['published_date'], 'date_basis': '文章发表与会议日期另列，不作为求职事件年'},
         'reading': {'scope': '部分', 'fulltext': False, 'scope_note': d['reading_scope'], 'video_watched': False},
         'platform_native_fulltext_verified': False, 'verified_video_viewing': False,
         'opinion': '；'.join(d['points']), 'identity_evidence': d['identity_basis'],
         'commercial_bias': d['commercial_background'], 'limitations': [d['qualification'], d['recruitment_boundary'], d['platform_boundary']],
         'recommendation': '与DOC02、OP15及PRO24/25对读评分和恢复；具体对照另见本轮比较表。',
         'source_record': deepcopy(d), 'cross_comparisons': deepcopy(data['comparisons']), 'outcomes': []}
    by = {x['id']: x for x in rows}
    if r['id'] in by:
        assert by[r['id']]['source_key'] == r['source_key'], r['id']
    by[r['id']] = r
    lines = ['# 专业观点交叉核对：评测、工具恢复与上下文', '',
             '本页为已有项目的阅读比较，个人项目设计继续暂缓。', '',
             '原始演讲编辑实录：[' + d['title'] + '](' + d['url'] + ')',
             '会务身份：[讲师](' + d['identity_url'] + ') · [议题](' + d['presentation_url'] + ')', '',
             d['reading_scope'], '', d['commercial_background'], '', d['platform_boundary'], '',
             '## 三项比较', '']
    for x in data['comparisons']:
        lines += ['### ' + x['topic'], '', x['finding'], '', '具体模块：' + x['project_reading'], '',
                  '阅读建议：' + x['recommendation'], '', '证据：' + '、'.join(x['evidence_ids']), '',
                  '定位：' + x['primary_locator'], '']
    lines += ['## 仍未补齐的部分', ''] + ['- ' + x for x in data['remaining']]
    lines += ['', '上述项目均未运行；比较不证明录用因果或SSP专属门槛。', '']
    (ROOT / '06_项目分析与推荐/专业观点交叉核对_评测与工具恢复.md').write_text('\n'.join(lines), encoding='utf-8')
    return sorted(by.values(), key=lambda x: x['id']), comparison, {
        'added_ids': [r['id']], 'summary': data['summary'], 'remaining': data['remaining'],
        'capability_ids': ['CAP07', 'CAP09', 'CAP11'], 'source': data}


def update_manual(items):
    items = deepcopy(items)
    for source in load('专业观点交叉核对_来源与比较.json')['access_reviews']:
        ident = source['url'].rsplit('/', 1)[-1]
        matches = [r for r in items if ident in r['url']]
        if matches:
            for r in matches:
                r.update({'status': source['status'], 'to_verify': source['decision']})
        else:
            items.append({'url': source['url'], 'title': source['title'], 'status': source['status'], 'to_verify': source['decision']})
    return items
