"""已读面经的独立增量与访问状态修正；不运行被研究项目。"""
from copy import deepcopy
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent


def load(name):
    return json.loads((BASE / name).read_text(encoding='utf-8-sig'))


def apply(rows, comparison):
    source = BASE / 'SSP与时间补核_来源核读.json'
    if not source.exists():
        return rows, comparison, {}
    snapshot = BASE / 'SSP与时间补核前主数据快照.json'
    if not snapshot.exists():
        snapshot.write_text(json.dumps({'records': rows, 'comparison': comparison,
                                       'coverage': load('需求覆盖统计.json')}, ensure_ascii=False, indent=2), encoding='utf-8')
    source = load(source.name)
    d = source['interview']
    r = {'id': d['id'], 'source_key': d['source_key'], 'category': '面经复盘',
         'title': d['title'], 'url': d['url'], 'author': d['author'], 'company': d['company'], 'role': d['role'],
         'date': d['event_date'], 'source_date': d['source_version_time'],
         'taxonomy': {'track': 'Agent工程', 'recruitment': '实习', 'experience_date_text': d['event_date'],
                      'date_precision': '仅月日', 'year_confirmed': False, 'recent_status': '年份未知',
                      'source_date_text': d['source_version_time'],
                      'date_basis': '原文未直接写事件年；展示/编辑字段与相对时间可作推定，未取得初发字段，不纳严格近期'},
         'reading': {'scope': '全文', 'fulltext': True, 'scope_note': d['reading_scope'], 'video_watched': False},
         'fulltext_verified': True, 'material_type': '本人具体问题记录', 'candidate_link_ids': [],
         'strict_recent_internship': False, 'publication_recent_event_year_unknown': False,
         'sample_group': '明确实习，事件年仅推定', 'result_status': 'unknown', 'outcome': d['result'], 'outcomes': [],
         'rounds': [{'round': '本人记录的一场面试；序号未披露', 'questions': d['questions_paraphrased'],
                     'coding': d['coding_question'], 'outcome': '未知'}],
         'project_questions': d['questions_paraphrased'],
         'topics': ['混合检索', 'RAG切片', '开源改造', '工具执行器', '失败兜底', '长期记忆', 'MCP传输', '检查点恢复', '可观测性', '日志', 'Multi-Agent'],
         'summary': d['question_answer_boundary'], 'recommendation': d['recommended_use'],
         'source_record': deepcopy(d)}
    by = {x['id']: x for x in rows}
    if r['id'] in by:
        assert by[r['id']]['source_key'] == r['source_key'], r['id']
    by[r['id']] = r
    return sorted(by.values(), key=lambda x: x['id']), comparison, {
        'added_ids': [r['id']], 'summary': source['summary'], 'remaining': source['remaining'],
        'capability_ids': d['capability_ids'], 'source': source}


def update_manual(items):
    """在所有历史追加后修正最新事实，避免旧访问失败覆盖已核正文。"""
    updated = []
    for old in items:
        r = deepcopy(old)
        if 'bb8c28105f364770b57ff5eb5649cc60' in r['url']:
            r.update({'url': 'https://www.nowcoder.com/feed/main/detail/bb8c28105f364770b57ff5eb5649cc60?sourceSSR=users&weFlow=true',
                      'status': '已读全文15问及本人自评；公开带参数入口HTTP200，普通入口部分请求为空壳。已正式收录INT84。',
                      'to_verify': '最终面试结果、原文未直接写明的事件年、本人履历与源码；不再待取文字正文'})
        if any(b in r['url'] for b in ['BV1P6tN6bEps', 'BV1GVJP6SE23']):
            r.update({'status': '前轮view接口412；本轮pagelist与player公开接口HTTP200/code0，取得CID但字幕列表为空。未观看视频、未读取字幕。',
                      'to_verify': '手动观看或核读平台可见字幕、记录观点与依据；匿名接口空列表不证明视频无字幕'})
        updated.append(r)
    return updated
