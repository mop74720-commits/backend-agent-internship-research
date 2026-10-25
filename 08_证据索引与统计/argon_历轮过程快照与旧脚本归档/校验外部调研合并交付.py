"""离线核对外部调研合并交付；不修改来源目录，不执行第三方项目。"""
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit
import csv
import hashlib
import json
import re
import zipfile

import fitz
from bs4 import BeautifulSoup


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / '01_调研报告'
OUTPUT = BASE / '外部调研合并交付校验.json'
INTERNAL_ID = re.compile(r'^(?:JD|INT|CV|OBS|PRO|OP|DOC)\d+$')
CAP_ID = re.compile(r'^CAP\d+$')


def load(name):
    return json.loads((BASE / name).read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(text):
    return ''.join(str(text).split())


def csv_cell(value):
    # CSV将空值写为空串、结构化历史字段写为文字，并给公式前缀添加字面量保护。
    if value is None:
        return ''
    text = str(value)
    return "'" + text if text.startswith(('=', '+', '-', '@')) else text


def csv_records(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)


def source_key(url):
    part = re.search(r'/(discuss/\d+|feed/main/detail/[a-f0-9]+)', str(url))
    return part.group(1) if part else str(url).split('?')[0].rstrip('/')


def main():
    checks = []
    result = {'date': '2026-10-24', 'passed': False, 'checks': checks,
              'current_totals': {}, 'pdf_sha256': None,
              'source_preserved': {'verified': False},
              'visual_review': '待根代理核对'}

    def check(name, ok, detail=None):
        checks.append({'name': name, 'passed': bool(ok), 'detail': detail})

    try:
        rows = load('all_evidence_records.json')
        by = {r['id']: r for r in rows}
        stats = load('需求覆盖统计.json')
        norm = load('统一样本分类与候选人关联.json')
        ivs = load('interview_records.json')
        cvs = load('candidate_cases.json')['cases']
        projects = load('project_recommendations.json')['projects']
        comparison = load('项目统一比较与阅读优先级.json')
        abilities = load('能力要求四类证据对照.json')['rows']
        layered = load('技术要求_明确要求与加分项.json')
        manual = load('待手动访问链接.json')
        mapping = load('astra合并_实施映射.json')
        iv_review = load('astra合并_面经核对.json')['records']
        jd_review = load('astra合并_JD核对.json')['records']
        other_review = load('astra合并_候选人与观点项目.json')['records']
        reviews = iv_review + jd_review + other_review
        mapped = {m['source_id']: m for m in mapping['mappings']}
        rid = {sid: m.get('destination_id') for sid, m in mapped.items()}
        result['current_totals'] = stats['totals']
        with zipfile.ZipFile(BASE / '外部调研合并前快照_20261024.zip') as snapshot:
            def before(name):
                return json.loads(snapshot.read('08_证据索引与统计/' + name).decode('utf-8-sig'))

            old_rows = before('all_evidence_records.json')
            old_by = {r['id']: r for r in old_rows}
            old_stats = before('需求覆盖统计.json')
            old_comparison = before('项目统一比较与阅读优先级.json')
            old_archives = before('全部项目归档_最终实物核对.json')['entries']
            old_design = {name: hashlib.sha256(snapshot.read(name)).hexdigest()
                          for name in snapshot.namelist()
                          if name.startswith('07_个人项目设计_暂缓/') and not name.endswith('/')}

        source_index = json.loads((BASE / '外部调研来源快照_20261024/资料索引.json').read_text(encoding='utf-8-sig'))
        expected_sids = {r['id'] for r in source_index}
        check('64张源卡、三个核读清单与实施映射逐条一一覆盖',
              len(source_index) == len(expected_sids) == 64 and
              len(reviews) == len({r['source_id'] for r in reviews}) == 64 and
              {r['source_id'] for r in reviews} == expected_sids == set(mapped),
              {'cards': len(source_index), 'reviews': len(reviews), 'mappings': len(mapped)})
        unresolved = [m['source_id'] for m in mapping['mappings']
                      if (m.get('destination_id') and m['destination_id'] not in by) or
                      (not m.get('destination_id') and m.get('action') not in ('待手动访问', '商业背景参考'))]
        check('所有源卡均有有效内部去向或明确保留边界', not unresolved, unresolved)
        new_ids = set(by) - set(old_by)
        new_rows = [by[i] for i in new_ids]
        delta = dict(Counter(r['category'] for r in new_rows))
        check('新增逻辑条目由合并前快照和实施映射独立复算',
              len(rows) == len(by) and set(old_by).issubset(by) and
              new_ids == set(mapping['new_ids']) and delta == mapping['new_by_category'] and
              len(rows) == len(old_rows) + sum(delta.values()),
              {'baseline': len(old_rows), 'delta': delta, 'current': len(rows)})
        expected_iv = {r['source_id'] for r in iv_review if r['decision'] == 'new'}
        expected_jd = {r['source_id'] for r in jd_review if r['decision'] == 'new'}
        check('本批新增20面经14JD3候选与1候选对照',
              len(expected_iv) == delta.get('面经复盘') == 20 and
              len(expected_jd) == delta.get('招聘JD') == 14 and
              delta.get('候选人资料') == 3 and delta.get('候选人对照') == 1,
              {'new_interviews': len(expected_iv), 'new_jds': len(expected_jd)})
        check('全部新增记录来源标记准确且未给重复条目新增ID', all(
              by[rid[sid]].get('external_import', {}).get('source_id') == sid
              and by[rid[sid]]['external_import'].get('review_manifest')
              and by[rid[sid]]['id'] in new_ids for sid in expected_iv | expected_jd))
        duplicate_iv = {r['source_id']: r['existing_id'] for r in iv_review if r['decision'] == 'existing'}
        check('五篇重复面经只补核读记录而不重复计数', len(duplicate_iv) == 5 and all(
              rid[sid] == target and target in old_by and target not in new_ids and
              sid in by[target].get('external_research_reviews', {})
              for sid, target in duplicate_iv.items()), duplicate_iv)

        metadata_errors = []
        for source in iv_review:
            current = by[rid[source['source_id']]]
            if source['decision'] != 'new':
                continue
            tx = current['taxonomy']
            expected_track = '算法对照' if source['track'] == 'AI Infra对照' else source['track']
            values = {'direction': tx['track'] == expected_track,
                      'recruitment': tx['recruitment'] == source['recruitment'],
                      'event_date': tx['experience_date_text'] == source['event_date'],
                      'event_year': tx['year_confirmed'] == source['event_year_confirmed'],
                      'date_basis': tx['date_basis'] == source['date_basis'],
                      'publication_separate': current['source_date'] == source['source_date'],
                      'reading': current['reading']['scope'] == source['read_scope'] == '全文'
                      and current['reading']['fulltext'] is True,
                      'questions': current['project_questions'] == source['questions'],
                      'result': current['result_status'] == source['result_status']
                      and current['outcome'] == source['result'],
                      'ai': bool(current.get('ai_organized')) == source['ai_organized']}
            metadata_errors.extend({'id': current['id'], 'field': k} for k, v in values.items() if not v)
        check('20新增面经主文、日期、结果与AI标记和实读清单一致', not metadata_errors, metadata_errors)
        jd_errors = []
        for source in jd_review:
            if source['decision'] != 'new':
                continue
            current = by[rid[source['source_id']]]
            for field in ('required_stack', 'preferred_stack', 'degree_constraint',
                          'availability_constraint', 'matrix_include', 'recruiting_status'):
                if current.get(field) != source.get(field):
                    jd_errors.append({'id': current['id'], 'field': field})
            if current['reading']['fulltext'] != bool(source['live_access'].get('fulltext')):
                jd_errors.append({'id': current['id'], 'field': 'actual_fulltext'})
        check('14新增JD要求加分资格及受限范围未被改写', not jd_errors, jd_errors)
        job_rows = [r for r in rows if r['category'] == '招聘JD']
        opinion_rows = [r for r in rows if r['category'] == 'B站与知乎']
        project_metadata_only = {'external_research_reviews'}
        project_core_equal = all(
            {k: v for k, v in r.items() if k not in project_metadata_only} ==
            {k: v for k, v in by[r['id']].items() if k not in project_metadata_only}
            for r in projects)
        check('主索引与分类表专业字段一致，项目补核元数据可仅存主表',
              all(r == by.get(r['id']) for r in ivs + cvs) and project_core_equal and
              len(ivs) == sum(r['category'] == '面经复盘' for r in rows) and
              len(cvs) == sum(r['category'] == '候选人资料' for r in rows))
        check('normalized记录和统计与主分类一致',
              norm['records'] == {'candidates': cvs, 'interviews': ivs, 'jobs': job_rows, 'opinions': opinion_rows}
              and norm['statistics'] == {'candidates': stats['candidate_coverage'],
                                        'interviews': stats['interview_coverage'],
                                        'jobs': stats['job_coverage'], 'opinions': stats['opinion_coverage']})
        check('主统计与实施映射及实际分类一致', stats['totals'] == mapping['current_totals'] and
              stats['category_counts'] == dict(Counter(r['category'] for r in rows)) and
              stats['totals']['logical_evidence_records'] == len(rows) and
              stats['totals']['interview_materials'] == len(ivs) and
              stats['totals']['candidate_cases'] == len(cvs) and
              stats['totals']['jd_leads'] == len(job_rows))
        check('面经阅读范围和招聘类型计数一致',
              dict(Counter(r['reading']['scope'] for r in ivs)) == stats['interview_coverage']['reading_scope'] and
              sum(r['taxonomy']['recruitment'] == '实习' for r in ivs) ==
              stats['interview_coverage']['explicit_internship_all_years_count'])

        strict = [r for r in ivs if r.get('strict_recent_internship')]
        engineering = [r for r in strict if r['taxonomy']['track'] != '算法对照']
        expected_strict_sids = {'I07', 'I09', 'I17', 'I25'}
        check('近期总组15工程组14且新增四篇均有正文事件年',
              len(strict) == 15 and len(engineering) == 14 and
              {r['id'] for r in strict if r['id'] in new_ids} == {rid[s] for s in expected_strict_sids} and
              stats['interview_coverage']['strict_recent_explicit_internship_count'] == len(strict) and
              stats['interview_coverage']['strict_recent_engineering_internship_count'] == len(engineering) and
              all(r['taxonomy']['recruitment'] == '实习' and r['taxonomy']['year_confirmed'] for r in strict),
              {'strict': [r['id'] for r in strict], 'engineering_count': len(engineering)})
        infra = by[rid['I25']]
        check('AI Infra明确为算法对照而非Agent工程', infra['taxonomy']['track'] == '算法对照'
              and infra['strict_recent_internship'] and
              all(by[rid[s]]['taxonomy']['track'] == '算法对照' and not by[rid[s]].get('matrix_include')
                  for s in ('J10', 'J11', 'J14')))
        check('OC与未知失败不变成正式offer或SSP',
              all(by[rid[s]]['result_status'] == 'oc_self_report' for s in ('I11', 'I14', 'I15')) and
              all(by[rid[s]]['result_status'] == 'unknown' for s in ('I04', 'I05', 'I17')) and
              by[rid['I23']]['result_status'] == 'rejected_self_report' and
              all(not any(o.get('grade') in ('SP', 'SSP') for o in r.get('outcomes', []))
                  for r in new_rows if r['category'] == '面经复盘'))
        check('两篇明确AI整理均降权包括重复旧条目', all(
              by[rid[s]].get('ai_organized') is True and
              '整理' in by[rid[s]].get('material_type', '') and
              'AI' in by[rid[s]]['reading']['scope_note'] for s in ('I14', 'I22')))
        check('同作者不同轮次和不同流程已互链且不合并人数',
              rid['I17'] in by[rid['I07']].get('related_record_ids', []) and
              rid['I07'] in by[rid['I17']].get('related_record_ids', []) and
              'INT29' in by[rid['I11']].get('related_record_ids', []) and
              rid['I11'] in by['INT29'].get('related_record_ids', []))
        cap_by = {a['id']: a for a in abilities}
        cap_missing = [(r['source_id'], c) for r in iv_review for c in r.get('capability_ids', [])
                       if c not in cap_by or rid[r['source_id']] not in cap_by[c]['interview_ids']]
        check('25篇面经能力映射已完整进入能力对照', not cap_missing, cap_missing)
        matrix_ids = {r['id'] for r in job_rows if r.get('matrix_include') and r['reading']['fulltext']}
        check('技术要求分层只收全文工程JD且要求与加分分别保留',
              {r['id'] for r in layered['job_requirement_rows']} == matrix_ids and
              layered['engineering_jd_count'] == len(matrix_ids) == stats['totals']['engineering_jd_fulltext'] and
              all('explicit_requirements' in r and 'explicit_preferences' in r
                  and 'duties_not_entry_gates' in r for r in layered['job_requirement_rows']))

        r05 = by[rid['R05']]
        r06 = by[rid['R06']]
        check('R05未读简历图仅作对照不增加完整CV或成功候选人',
              r05['category'] == '候选人对照' and r05['reading']['scope'] == '部分' and
              '未读图' in r05.get('profile_type', '') and
              not r05.get('complete_cv_file_received') and not r05.get('complete_redacted_cv_file_received') and
              r05['source_record'].get('eligible_for_success_candidate_count') is False and
              not r05.get('stack') and not r05.get('projects'))
        check('R06教学例子未列作成功者履历或实际项目',
              r06['category'] == '专业原文补充' and not r06.get('outcomes') and
              r06['reading']['scope'] == '部分' and
              r06['source_record'].get('eligible_for_success_candidate_count') is False and
              rid['R06'] not in {r['id'] for r in cvs})
        check('完整CV和核心脱敏副本没有新增',
              mapping['new_cv_files'] == stats['external_merge']['new_resume_files'] == 0 and
              stats['candidate_coverage']['complete_cv_files_received'] ==
              old_stats['candidate_coverage']['complete_cv_files_received'] and
              stats['candidate_coverage']['complete_redacted_cv_files_received'] ==
              old_stats['candidate_coverage']['complete_redacted_cv_files_received'] == 5 and
              all(not r.get('complete_cv_file_received') and not r.get('complete_redacted_cv_file_received')
                  for r in new_rows))
        check('25项目375比较项和原比较内容保持', comparison == old_comparison and
              len(projects) == len(comparison['projects']) == 25 and
              sum(len(p.get('backend_dimensions', {})) + len(p.get('agent_dimensions', {}))
                  for p in comparison['projects']) == 375 and
              not any(r['category'] == '项目源码与分析' for r in new_rows))
        archive_paths = {r['file']: r for r in old_archives}
        actual_archives = {p.relative_to(ROOT).as_posix(): p for p in (ROOT / '05_项目源码归档').rglob('*.zip')}
        archive_bad = [rel for rel, item in archive_paths.items()
                       if rel not in actual_archives or actual_archives[rel].stat().st_size != item['bytes']
                       or digest(actual_archives[rel]) != item['sha256']]
        check('25源码附件文件名大小hash均与合并前相同',
              len(actual_archives) == len(archive_paths) == 25 and not archive_bad and
              set(actual_archives) == set(archive_paths) and mapping['new_source_archives'] == 0,
              {'archive_errors': archive_bad})
        design_now = {p.relative_to(ROOT).as_posix(): digest(p)
                      for p in (ROOT / '07_个人项目设计_暂缓').rglob('*') if p.is_file()}
        unbaselined_design = set(design_now) - set(old_design)
        known_unbaselined_design = {'07_个人项目设计_暂缓/agent_eval_seed_examples.jsonl'}
        snapshotted_design_same = all(design_now.get(name) == checksum for name, checksum in old_design.items())
        result['design_preservation'] = {
            'design_imported': mapping['design_imported'],
            'snapshot_covered_files': len(old_design),
            'snapshot_covered_files_unchanged': snapshotted_design_same,
            'files_without_premerge_hash': sorted(unbaselined_design),
            'whole_directory_historical_hash_verified': False,
            'boundary': '合并前ZIP只收六份txt草案。既有agent_eval_seed_examples.jsonl未入该快照，'
                        '没有合并前hash；本校验不把它判为本轮新增，也不声称其历史字节未变。',
        }
        check('个人项目设计继续暂缓且快照覆盖六份草案未变', mapping['design_imported'] is False
              and len(old_design) == 6 and snapshotted_design_same
              and unbaselined_design == known_unbaselined_design, result['design_preservation'])
        native = [r for r in opinion_rows if r.get('platform_native_fulltext_verified')]
        watched = [r['id'] for r in rows if r.get('verified_video_viewing') or
                   r.get('reading', {}).get('video_watched')]
        check('平台本体全文仍5且视频仍0选读不充全文', len(native) == 5 and not watched and
              stats['opinion_coverage']['primary_bilibili_or_zhihu_full_content_verified_count'] == 5 and
              stats['opinion_coverage']['actual_video_watched_count'] == 0 and all(
                  not by[rid[s]].get('platform_native_fulltext_verified') and
                  by[rid[s]]['reading']['scope'] == '部分' for s in ('V01', 'V02')),
              {'native_fulltexts': [r['id'] for r in native], 'watched': watched})

        id_errors = []
        for name, data in [('records', rows), ('normalized', norm), ('capabilities', abilities),
                           ('layered', layered), ('routes', load('两方向阅读顺序.json'))]:
            for value in strings(data):
                if (INTERNAL_ID.fullmatch(value) and value not in by) or (CAP_ID.fullmatch(value) and value not in cap_by):
                    id_errors.append({'file': name, 'id': value})
        check('内部证据ID和CAP引用没有悬空', not id_errors, id_errors)
        for category, values in [('interview', ivs), ('candidate', cvs)]:
            for key, expected in [('track', Counter(r['taxonomy']['track'] for r in values)),
                                  ('recruitment', Counter(r['taxonomy']['recruitment'] for r in values))]:
                check(category + '分类统计' + key + '可独立复算',
                      dict(expected) == stats[category + '_coverage'][key])
        for relative, count in {
            '08_证据索引与统计/全部资料统一分类.csv': len(rows),
            '04_面经与专业观点/面经统一分类.csv': len(ivs),
            '03_简历与候选人案例/候选人证据链对照.csv': len(cvs),
            '06_项目分析与推荐/项目统一比较.csv': 375,
            '08_证据索引与统计/能力要求四类证据对照.csv': len(abilities),
        }.items():
            with (ROOT / relative).open(encoding='utf-8-sig', newline='') as handle:
                actual = len(list(csv.reader(handle))) - 1
            check('CSV行数 ' + relative, actual == count, {'actual': actual, 'expected': count})

        taxonomy_csv = csv_records(BASE / '全部资料统一分类.csv')
        taxonomy_expected = [{
            'ID': r['id'], '类别': r['category'], '标题': r['title'],
            '方向': r['taxonomy']['track'], '招聘路径': r['taxonomy']['recruitment'],
            '实际事件时间': r['taxonomy']['experience_date_text'],
            '来源时间': r['taxonomy']['source_date_text'],
            '事件年已证': str(r['taxonomy']['year_confirmed']),
            '近期状态': r['taxonomy']['recent_status'],
            '阅读范围': r['reading']['scope'], '来源': r['url'],
        } for r in rows]
        taxonomy_expected = [{key: csv_cell(value) for key, value in row.items()} for row in taxonomy_expected]
        taxonomy_csv_by = {r['ID']: r for r in taxonomy_csv}
        taxonomy_expected_by = {r['ID']: r for r in taxonomy_expected}
        taxonomy_csv_bad = sorted(i for i in set(taxonomy_csv_by) | set(taxonomy_expected_by)
                                  if taxonomy_csv_by.get(i) != taxonomy_expected_by.get(i))
        check('统一分类CSV全部ID及每个字段与主索引一致',
              len(taxonomy_csv_by) == len(taxonomy_csv) and not taxonomy_csv_bad,
              {'mismatched_ids': taxonomy_csv_bad})

        ability_csv = csv_records(BASE / '能力要求四类证据对照.csv')
        ability_expected = [{
            '能力': a['ability'], '后端相关性': a['backend_relevance'],
            'Agent相关性': a['agent_relevance'], 'JD': ';'.join(a['jd_ids']),
            '面经': ';'.join(a['interview_ids']), '履历': ';'.join(a['candidate_ids']),
            '专业原文': ';'.join(a['opinion_ids']), '提问': a['question'],
            '考察能力': a['competency'], '项目模块主题映射': a['module'],
            '研究归纳薄弱点': a['common_pitfall'], '缺口': a['gap'],
        } for a in abilities]
        ability_expected = [{key: csv_cell(value) for key, value in row.items()} for row in ability_expected]
        ability_csv_by = {r['能力']: r for r in ability_csv}
        ability_expected_by = {r['能力']: r for r in ability_expected}
        ability_csv_bad = sorted(i for i in set(ability_csv_by) | set(ability_expected_by)
                                if ability_csv_by.get(i) != ability_expected_by.get(i))
        check('能力CSV逐项来源ID及全部说明与JSON一致',
              len(ability_csv_by) == len(ability_csv) and not ability_csv_bad,
              {'mismatched_abilities': ability_csv_bad})

        topics = load('interview_topic_index.json')
        topic_errors = []
        for theme in topics['themes']:
            matched = [r for r in ivs if re.search(
                theme['rule'], ' '.join(r.get('topics', [])) + ' ' +
                ' '.join(r.get('project_questions', [])), re.I)]
            internship = [r for r in matched if r['taxonomy']['recruitment'] == '实习']
            recomputed = {
                'record_count': len(matched),
                'evidence_ids': [r['id'] for r in matched],
                'explicit_internship_ids': [r['id'] for r in internship],
                'strict_recent_internship_ids': [r['id'] for r in matched
                                                 if r.get('strict_recent_internship')],
                'year_unknown_internship_ids': [r['id'] for r in internship
                                                if not r['taxonomy']['year_confirmed']],
            }
            for field, value in recomputed.items():
                if theme.get(field) != value:
                    topic_errors.append({'theme': theme['theme'], 'field': field,
                                         'actual': theme.get(field), 'expected': value})
        check('主题JSON按主表问题与正则复算所有数量和分组ID',
              topics.get('scope_records') == len(ivs) and not topic_errors, topic_errors)
        topic_csv = csv_records(BASE / '面经主题索引.csv')
        topic_expected = [{
            '主题': t['theme'], '全包资料数': str(t['record_count']),
            '明确实习资料数': str(len(t['explicit_internship_ids'])),
            '严格近期实习资料数': str(len(t['strict_recent_internship_ids'])),
            '实习事件年未知资料数': str(len(t['year_unknown_internship_ids'])),
            '全包资料ID': ';'.join(t['evidence_ids']),
            '严格近期ID': ';'.join(t['strict_recent_internship_ids']),
        } for t in topics['themes']]
        check('主题CSV主题数量与全部ID逐项和JSON一致', topic_csv == topic_expected,
              {'csv_themes': len(topic_csv), 'json_themes': len(topic_expected)})

        routes = load('两方向阅读顺序.json')
        for route, name in [('backend', '后端实习阅读顺序.md'),
                            ('agent', 'Agent实习阅读顺序.md')]:
            route_file = ROOT / '06_项目分析与推荐' / name
            route_text = route_file.read_text(encoding='utf-8-sig')
            route_ids = re.findall(r'^- \[((?:INT|CV)\d+)\s', route_text, re.M)
            expected_route_ids = routes[route]['candidate_ids'] + routes[route]['interview_ids']
            check('阅读Markdown条目与JSON顺序一致 ' + route,
                  route_ids == expected_route_ids,
                  {'actual': route_ids, 'expected': expected_route_ids})

        fingerprint = load('astra来源_合并前文件指纹.json')
        source_root = Path(fingerprint['source_path'])
        expected_files = {r['path']: r for r in fingerprint['files']}
        actual_files = {p.relative_to(source_root).as_posix(): p for p in source_root.rglob('*') if p.is_file()}
        changed = [rel for rel in set(expected_files) & set(actual_files)
                   if actual_files[rel].stat().st_size != expected_files[rel]['bytes'] or
                   digest(actual_files[rel]) != expected_files[rel]['sha256']]
        source_preserved = {'verified': not changed and set(actual_files) == set(expected_files),
                            'source_path': source_root.as_posix(), 'files_before': len(expected_files),
                            'files_after': len(actual_files), 'changed': sorted(changed),
                            'added': sorted(set(actual_files) - set(expected_files)),
                            'removed': sorted(set(expected_files) - set(actual_files))}
        result['source_preserved'] = source_preserved
        check('astra原138文件全部字节和hash不变且无增删', source_preserved['verified']
              and len(expected_files) == len(actual_files) == 138, source_preserved)

        page_cache = {}

        def page(path):
            path = path.resolve()
            if path not in page_cache:
                soup = BeautifulSoup(path.read_text(encoding='utf-8-sig'), 'html.parser')
                anchors = {x['id'] for x in soup.select('[id]')} | {x['name'] for x in soup.select('a[name]')}
                page_cache[path] = soup, anchors
            return page_cache[path]

        broken, link_count = [], 0
        html_files = list(ROOT.rglob('*.html'))
        for file in html_files:
            soup = page(file)[0]
            for node in soup.select('[href], [src], object[data]'):
                for attr in ('href', 'src', 'data'):
                    raw = node.get(attr)
                    if not raw or attr == 'data' and node.name != 'object':
                        continue
                    parts = urlsplit(raw)
                    if parts.scheme and parts.scheme != 'file' or parts.netloc and parts.scheme != 'file':
                        continue
                    if parts.scheme == 'file':
                        raw_path = unquote(parts.path).lstrip('/') if re.match(r'^/[A-Za-z]:/', parts.path) else unquote(parts.path)
                        target = Path(raw_path)
                    else:
                        target = (file.parent / unquote(parts.path)).resolve() if parts.path else file.resolve()
                    link_count += 1
                    fragment = unquote(parts.fragment).split(':~:text=', 1)[0]
                    reason = None
                    if not target.exists():
                        reason = '文件不存在'
                    elif fragment and target.suffix.lower() in ('.html', '.htm') and fragment != 'top':
                        if fragment not in page(target)[1]:
                            reason = '锚点不存在'
                    if reason:
                        broken.append({'file': file.relative_to(ROOT).as_posix(), 'attribute': attr,
                                       'url': raw, 'reason': reason})
        check('本包所有HTML的本地文件和锚点无断链', not broken,
              {'html_files': len(html_files), 'local_links': link_count, 'broken': broken})
        result['local_link_checks'] = link_count

        main_html = REPORT / '需求核对与阅读优先级.html'
        added_html = REPORT / '外部调研增补与去重清单.html'
        modules = ROOT / '06_项目分析与推荐/外部调研_文档判断与阅读模块.md'
        main_soup = page(main_html)[0]
        main_text = compact(main_soup.get_text(' ', strip=True))
        check('主入口首页index和外部新增模块存在',
              (REPORT / 'index.html').read_text(encoding='utf-8-sig') ==
              main_html.read_text(encoding='utf-8-sig') and added_html.exists()
              and modules.exists() and main_soup.select_one('#external-merge') is not None)
        check('首页当前数量和工程对照范围明确',
              all(str(n) in main_text for n in (len(rows), len(ivs), len(cvs), len(manual))) and
              '严格近期实习总组15份' in main_text and '工程14份' in main_text and
              'AIInfra对照1份' in main_text and '个人项目设计继续暂缓' in main_text)
        if added_html.exists():
            addition_text = compact(page(added_html)[0].get_text(' ', strip=True))
            check('增补页列出全部64源卡去重映射及Infra边界',
                  all(sid in addition_text for sid in expected_sids) and '64' in addition_text and
                  ('Infra' in addition_text or '算法对照' in addition_text) and
                  '未读图' in addition_text and ('教学' in addition_text or '示例' in addition_text))
        else:
            check('增补页列出全部64源卡去重映射及Infra边界', False, '增补HTML缺失')
        manual_soup = page(REPORT / '待手动访问链接.html')[0]
        manual_text = compact(manual_soup.get_text(' ', strip=True))
        check('手动JSON首页导航及手动页数量一致', len(manual) == stats['totals']['manual_links'] and
              str(len(manual)) + '条待手动访问' in main_text and
              '待手动访问链接·' + str(len(manual)) + '条' in manual_text and
              all(m['url'] in str(manual_soup) or m['url'].replace('&', '&amp;') in str(manual_soup) for m in manual))
        stale_manual = []
        alias = {source_key(u): r for r in iv_review for u in (r['url'], r.get('resolved_url', '')) if u}
        for item in manual:
            if source_key(item['url']) not in alias:
                continue
            status = str(item.get('status', ''))
            if re.search(r'未取得正文|正文未读|未读取正文|只有标题|页面外壳', status) and not re.search(r'已读.{0,10}全文|全文.{0,10}已读|本轮已.{0,8}(?:读取|核读)', status):
                stale_manual.append({'title': item.get('title'), 'url': item['url']})
        check('已读全文面经手动项不再冒称只有外壳', not stale_manual, stale_manual)

        pdf_file = REPORT / '需求核对与阅读优先级.pdf'
        check('当前PDF存在且非空', pdf_file.exists() and pdf_file.stat().st_size > 10000)
        if pdf_file.exists():
            result['pdf_sha256'] = digest(pdf_file)
            with fitz.open(pdf_file) as pdf:
                text_pages = [p.get_text() for p in pdf]
                pdf_text = compact('\n'.join(text_pages))
                result['pdf_pages'] = len(pdf)
                check('PDF文字含当前外部增补与核心新资料',
                      '外部调研核读增补' in pdf_text and '64张来源卡' in pdf_text and
                      all(i in pdf_text for i in (rid['I07'], rid['I21'], rid['I25'], rid['R05'])) and
                      all(str(n) in pdf_text for n in (len(ivs), len(cvs), len(manual))) and
                      'AIInfra对照1份' in pdf_text)
                check('PDF无空白页且文字块未越出页面', all(len(t.strip()) > 100 for t in text_pages)
                      and all(block[0] >= -1 and block[2] <= p.rect.width + 1
                              for p in pdf for block in p.get_text('blocks')))
        visual_file = BASE / '外部调研合并PDF目视记录.json'
        if visual_file.exists():
            visual = load(visual_file.name)
            reviewed_pages = visual.get('pages_reviewed', [])
            visual_ok = visual.get('passed') is True and result['pdf_sha256'] is not None
            visual_ok = visual_ok and visual.get('pdf_sha256') == result['pdf_sha256']
            visual_ok = visual_ok and visual.get('pdf_pages') == result.get('pdf_pages')
            visual_ok = visual_ok and bool(reviewed_pages) and all(
                type(p) is int and 1 <= p <= result.get('pdf_pages', 0) for p in reviewed_pages)
            visual_ok = visual_ok and len(reviewed_pages) == len(set(reviewed_pages))
            visual_ok = visual_ok and bool(visual.get('observations'))
            check('根代理PDF目视记录绑定当前hash页数及有效抽查页', visual_ok,
                  {'record': visual_file.relative_to(ROOT).as_posix(),
                   'pages_reviewed': reviewed_pages})
            result['pdf_visual_review_record'] = visual
            if visual_ok:
                result['visual_review'] = '根代理已目视抽查，记录绑定当前PDF的hash与页数'
        else:
            check('根代理PDF目视记录绑定当前hash页数及有效抽查页', False,
                  '目视记录尚未生成，保持待核，不声称已完成视觉审查')
        browser_file = BASE / '外部调研合并浏览器校验.json'
        if browser_file.exists():
            browser = load(browser_file.name)
            browser_checks = browser.get('checks', [])
            browser_ok = bool(browser_checks) and not browser.get('errors') and all(c.get('passed') for c in browser_checks)
            browser_ok = browser_ok and browser.get('pdf_exported', True) is not False
            if browser.get('pdf_sha256'):
                browser_ok = browser_ok and browser['pdf_sha256'] == result['pdf_sha256']
            check('根代理浏览器筛选搜索移动端与当前PDF通过', browser_ok, {'checks': len(browser_checks)})
        else:
            check('根代理浏览器筛选搜索移动端与当前PDF通过', False, '浏览器QA文件尚未生成')
    except Exception as error:
        check('校验过程无未处理阻塞', False, {'type': type(error).__name__, 'message': str(error)})

    result['passed'] = bool(checks) and all(c['passed'] for c in checks)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': result['passed'], 'checks': len(checks),
                      'failed': [c['name'] for c in checks if not c['passed']],
                      'source_preserved': result['source_preserved']['verified']}, ensure_ascii=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
