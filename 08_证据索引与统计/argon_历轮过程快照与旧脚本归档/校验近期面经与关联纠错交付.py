"""核对新增近期原帖、候选人结果范围纠错、六项验收与当前交付。"""
from collections import Counter
from copy import deepcopy
from pathlib import Path
from urllib.parse import unquote, urlsplit
import csv
import hashlib
import json

import fitz
from bs4 import BeautifulSoup

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / '01_调研报告'


def load(name):
    return json.loads((BASE / name).read_text(encoding='utf-8-sig'))


def main():
    checks = []

    def check(name, ok, detail=None):
        checks.append({'name': name, 'passed': bool(ok), 'detail': detail})

    malformed = []
    for file in ROOT.rglob('*.json'):
        try:
            json.loads(file.read_text(encoding='utf-8-sig'))
        except Exception:
            malformed.append(str(file.relative_to(ROOT)))
    check('全部JSON可解析', not malformed, malformed)
    rows = load('all_evidence_records.json')
    by = {r['id']: r for r in rows}
    prior = load('近期面经与关联纠错前主数据快照.json')
    old = {r['id']: r for r in prior['records']}
    stats = load('需求覆盖统计.json')
    progress = load('近期面经与关联纠错统计.json')
    expected_old = deepcopy(old)
    changes = load('近期面经与关联纠错_修正清单.json')['changes']
    for record in expected_old.values():
        if record['category'] == '候选人资料':
            for outcome in record.get('outcomes', []):
                if 'applies_to_this_interview' in outcome:
                    outcome.pop('applies_to_this_interview')
                    outcome['result_scope'] = '候选人总体录用自述；是否对应某一场面经，以该面经卡及直接关联证据为准'
    date_change = load('实习事件年份补核_变更清单.json')
    check('日期补核只改指定专业字段', date_change['before'] == old['INT68'] and
          all(date_change['before'].get(k) == date_change['after'].get(k) for k in
              (set(date_change['before']) | set(date_change['after'])) - set(date_change['allowed_fields'])))
    expected_old['INT68'] = date_change['after']
    archive_changes = load('项目选读归档_变更清单.json')['changes']
    expected_comp = deepcopy(prior['comparison'])
    for item in archive_changes:
        check('归档前记录保持 ' + item['id'], item['before'] == old[item['id']])
        expected_old[item['id']] = item['after']
        expected_comp['projects'] = [item['comparison_after'] if p['id'] == item['id'] else p for p in expected_comp['projects']]
    expected_comp['counts'] = stats['project_coverage']
    check('新增2原帖且旧191条只发生指定范围日期和附件修正', len(rows) == len(by) == 193 and len(old) == 191 and
          set(by) - set(old) == {'INT85', 'INT86'} and all(by[k] == v for k, v in expected_old.items()))
    check('上一轮189快照统计保留', load('近期Agent补链统计.json')['current_totals']['logical_evidence_records'] == 189)
    check('当前统计和累计目标一致', stats['totals'] == progress['current_totals'] == load('目标执行统计.json')['current_totals'] and
          Counter(r['category'] for r in rows) == stats['category_counts'] and progress['new_record_ids'] == ['INT85', 'INT86'])
    iv = load('interview_records.json')
    cv = load('candidate_cases.json')['cases']
    projects = load('project_recommendations.json')['projects']
    check('分类表实物与主记录一致', all(r == by[r['id']] for r in iv + cv + projects) and
          len(iv) == 79 and len(cv) == 31 and len(projects) == 25)
    check('79面经72全文7部分51明确实习', Counter(r['reading']['scope'] for r in iv) == {'全文': 72, '部分': 7} and
          sum(r['taxonomy']['recruitment'] == '实习' for r in iv) == 51)
    check('严格近期11含同作者正文补年且辅助13保持', sum(bool(r.get('strict_recent_internship')) for r in iv) == 11 and
          sum(bool(r.get('publication_recent_event_year_unknown')) for r in iv) == 13 and
          sum(r['taxonomy']['recruitment'] == '实习' and r['taxonomy']['recent_status'] == '年份未知' for r in iv) == 39)
    i68 = by['INT68']
    proof = i68['event_date_verification']
    check('INT68补年保留同作者三节点及日期口径差别', i68['taxonomy']['year_confirmed'] and i68['strict_recent_internship'] and
          '2026-05-14' in i68['date'] and '2026-04-01' in i68['date'] and '03-31' in i68['date'] and
          proof['primary']['public_author_path'] == proof['supporting']['public_author_path'] and
          len(proof['direct_relationship']['matching_event_nodes']) == 3 and
          i68['result_status'] == 'offer_self_report' and i68['outcomes'][0]['grade'] == '未披露')
    access = load('B站字幕访问_双路径复核.json')['records']
    check('新2视频只记录字幕登录要求不计观看', len(access) == 2 and all(
          x['player_v2']['need_login_subtitle'] and x['player_v2']['subtitles_count'] == 0 for x in access) and
          stats['totals']['manual_links'] == 70 and stats['opinion_coverage']['actual_video_watched_count'] == 0)
    r = by['INT84']
    source = load('SSP与时间补核_来源核读.json')
    check('新面经15问全文范围及来源', r['reading']['fulltext'] and len(r['project_questions']) == 15 and
          r['source_record'] == source['interview'] and 'bb8c28105f364770b57ff5eb5649cc60' in r['url'])
    check('结果未知不从算法失误推拒绝或SSP', r['result_status'] == 'unknown' and r['outcomes'] == [] and
          '不能从算法' in r['outcome'] and '未完成' in r['rounds'][0]['coding'])
    check('展示编辑时间不冒充事件直接年或初发', not r['taxonomy']['year_confirmed'] and
          not r['strict_recent_internship'] and not r['publication_recent_event_year_unknown'] and
          r['taxonomy']['date_precision'] == '仅月日' and '未取得createTime' in r['source_date'])
    time = load('SSP与时间补核_百度时间字段.json')['records'][-1]
    check('目标UUID白名单时间字段可追溯', time['uuid'] == 'bb8c28105f364770b57ff5eb5649cc60' and
          set(time['time_fields']) == {'editTime', 'showTime'} and
          set(time['converted_times'].values()) == {'2026-09-07T16:02:34+08:00'})
    check('没有将新作者拼到既有候选人', r['candidate_link_ids'] == [] and all(
          not any('bb8c28105f364770b57ff5eb5649cc60' in str(n) for n in c['chain']['interview']) for c in cv))
    capabilities = load('能力要求四类证据对照.json')['rows']
    check('具体追问映射5项能力且未误作权限证据', {a['id'] for a in capabilities if 'INT84' in a['interview_ids']} ==
          set(source['interview']['capability_ids']) and all(
          any(s['id'] == 'INT84' for s in a['support']['interview']) for a in capabilities if a['id'] in source['interview']['capability_ids']))
    layered = load('技术要求_明确要求与加分项.json')
    check('技术要求分层及Agent阅读路线纳入新面经', 'INT84' in layered['agent_conclusions'][1]['interview_ids'] and
          'INT84' in load('两方向阅读顺序.json')['agent']['interview_ids'] and
          load('interview_topic_index.json')['scope_records'] == 79)
    subtitles = load('SSP与时间补核_公开字幕接口.json')['attempts']
    check('两视频接口200空字幕不计观看', len(subtitles) == 2 and all(
          x['pagelist_http_status'] == x['player_status'] == 200 and x['pagelist_code'] == x['player_code'] == 0 and
          x['cid'] and x['public_subtitles'] == [] and not x['video_watched'] and not x['subtitle_read'] and
          not x['media_downloaded'] for x in subtitles))
    manual = load('待手动访问链接.json')
    target = [x for x in manual if 'bb8c28105f364770b57ff5eb5649cc60' in x['url']]
    check('手动清单不再误标新面经正文未读', len(target) == 1 and '已读全文15问' in target[0]['status'] and
          'sourceSSR=users&weFlow=true' in target[0]['url'])
    videos = [x for x in manual if any(v['bvid'] in x['url'] for v in subtitles)]
    check('两视频手动状态已合并最新事实', len(videos) == 2 and all('200/code0' in x['status'] and '字幕列表为空' in x['status'] for x in videos))
    check('SSP复核排除不虚增成功者', progress['new_candidate_profiles'] == progress['new_projects'] == progress['new_ssp_cases'] == 0 and
          len(source['ssp_review']) == 3 and stats['recent_agent_ssp_complete_chain_confirmed'] == 0)
    check('既有25项目375维与附件统计保持', load('项目统一比较与阅读优先级.json') == expected_comp and
          stats['project_coverage']['source_archives'] == 25 and stats['project_coverage']['executed_projects'] == 0 and
          sum(bool(c.get('complete_redacted_cv_file_received')) for c in cv) == 5)
    for rel, count in {'03_简历与候选人案例/候选人证据链对照.csv': 31, '04_面经与专业观点/面经统一分类.csv': 79,
                       '06_项目分析与推荐/项目统一比较.csv': 375, '08_证据索引与统计/全部资料统一分类.csv': 193,
                       '08_证据索引与统计/能力要求四类证据对照.csv': 11}.items():
        with (ROOT / rel).open(encoding='utf-8-sig', newline='') as f:
            actual = len(list(csv.reader(f))) - 1
        check('CSV ' + rel, actual == count, actual)
    cache = {}

    def page(file):
        if file not in cache:
            soup = BeautifulSoup(file.read_text(encoding='utf-8-sig'), 'html.parser')
            cache[file] = soup, {x['id'] for x in soup.select('[id]')} | {x['name'] for x in soup.select('a[name]')}
        return cache[file]

    broken, links = [], 0
    for file in REPORT.glob('*.html'):
        for a in page(file.resolve())[0].select('a[href]'):
            url = urlsplit(a['href'])
            if url.scheme or url.netloc:
                continue
            target = (file.parent / unquote(url.path)).resolve() if url.path else file.resolve()
            links += 1
            if not target.exists() or (url.fragment and target.suffix.lower() == '.html' and unquote(url.fragment) not in page(target)[1]):
                broken.append({'file': file.name, 'href': a['href']})
    check('全部报告本地链接和锚点可达', not broken, {'count': links, 'broken': broken})
    report_file = REPORT / '需求核对与阅读优先级.pdf'
    with fitz.open(report_file) as pdf:
        texts = [p.get_text() for p in pdf]
        joined = '\n'.join(texts)
        joined_without_whitespace = ''.join(joined.split())
        pages = len(pdf)
        check('PDF包含本轮结论且无空白孤页', all(len(t.strip()) > 150 for t in texts) and
              'INT84' in joined and 'LC297' in joined and '200/code0' in joined and '最终结果没有公布' in joined_without_whitespace)
        check('PDF文字不越出页面', all(b[0] >= 0 and b[2] <= p.rect.width + 1 for p in pdf for b in p.get_text('blocks')))
    browser = load('近期面经与关联纠错浏览器校验.json')
    check('当前浏览器筛选搜索及手机显示通过', browser.get('pdf_exported') and not browser['errors'] and all(c['passed'] for c in browser['checks']), len(browser['checks']))
    expert = by['OP16']
    expert_source = load('专业观点交叉核对_来源与比较.json')
    check('实录原始发布与会务身份可追溯', expert['url'] == 'https://www.infoq.cn/article/l7BXlstUWDOBwI30miJU' and
          expert['source_record']['identity_url'].endswith('/speaker/10191') and
          expert['source_record']['presentation_url'].endswith('/presentation/6939'))
    check('平台外实录选读不冒充本体全文或视频', expert['category'] == '专业原文补充' and
          expert['reading']['scope'] == '部分' and not expert['reading']['fulltext'] and
          not expert['reading']['video_watched'] and not expert['platform_native_fulltext_verified'] and
          stats['totals']['platform_opinion_records'] == 13 and stats['totals']['additional_primary_texts'] == 3 and
          stats['opinion_coverage']['primary_bilibili_or_zhihu_full_content_verified_count'] == 5)
    check('商业背景及招聘边界明确', '商业会议' in expert['commercial_bias'] and
          '不是招聘JD' in expert['source_record']['recruitment_boundary'] and expert['outcomes'] == [])
    check('三项比较均有指定来源和模块局限', len(expert['cross_comparisons']) == 3 and all(
          c['evidence_ids'] and c['primary_locator'] and c['project_reading'] and c['recommendation'] for c in expert['cross_comparisons']))
    check('模型判分校准观点不偷换成无偏保证', '人工校准' in expert['source_record']['qualification'] and
          '无偏保证' in expert['source_record']['qualification'] and
          any('DOC02' in c['evidence_ids'] and 'OP15' in c['evidence_ids'] for c in expert['cross_comparisons']))
    check('原文观点关联能力和阅读路线', {a['id'] for a in capabilities if 'OP16' in a['opinion_ids']} ==
          {'CAP07', 'CAP09', 'CAP11'} and 'OP16' in load('两方向阅读顺序.json')['read_professional_ids'] and
          'OP16' in layered['agent_conclusions'][1]['opinion_ids'])
    check('销售推荐语未新增成功者且保留检索结束边界', progress['new_ssp_cases'] == 0 and
          '不新增成功者' in expert_source['ssp_review']['decision'] and '结束本轮' in expert_source['search_stop'])
    current_soup = page((REPORT / '需求核对与阅读优先级.html').resolve())[0]
    check('页面与PDF均呈现新比较', current_soup.select_one('#expert-review') is not None and
          'OP16' in joined and '三项对照与指定模块' in ''.join(joined.split()) and
          (ROOT / '06_项目分析与推荐/专业观点交叉核对_评测与工具恢复.md').exists())
    fresh = load('近期面经与关联纠错_来源核读.json')['interviews']
    i85, i86 = by['INT85'], by['INT86']
    check('INT85事件日期来自正文且失败结果直接', i85['taxonomy']['year_confirmed'] and i85['strict_recent_internship'] and
          i85['result_status'] == 'failure_self_report' and '25.3.14' in i85['taxonomy']['date_basis'] and
          '2025-03-14' in i85['date'] and i85['source_record']['access']['body_sha256'] == fresh[0]['access']['body_sha256'])
    check('INT86已offer不冒充SSP且编辑年不代事件年', i86['result_status'] == 'offer_self_report' and
          not i86['taxonomy']['year_confirmed'] and not i86['strict_recent_internship'] and
          not i86['publication_recent_event_year_unknown'] and i86['outcomes'][0]['grade'] == '未披露' and
          i86['material_type'] == '面试问题与部分事后解答混合')
    check('18候选人37标记修正且具体面经对应保留', len(changes) == 37 and len({c['id'] for c in changes}) == 18 and
          all('applies_to_this_interview' not in o for c in cv for o in c.get('outcomes', [])) and
          i85['outcomes'][0]['applies_to_this_interview'] and i86['outcomes'][0]['applies_to_this_interview'] and
          not by['INT56']['outcomes'][0]['applies_to_this_interview'])
    check('新原帖不是同人履历或源码的拼接', i85['candidate_link_ids'] == i86['candidate_link_ids'] == [] and
          i85['company'].startswith('爱橙科技') and '不改写为阿里集团' in i85['company'] and '题库专栏' in i86['commercial_bias'])
    check('两篇新追问映射明确能力并进入后端路线', all(
          {a['id'] for a in capabilities if d['id'] in a['interview_ids']} == set(d['capability_ids']) for d in fresh) and
          all(d['id'] in load('两方向阅读顺序.json')['backend']['interview_ids'] for d in fresh))
    six = load('六项目标逐条验收.json')
    check('六项验收含5份实物且不沿用初始零份口径', len(six['requirements']) == 6 and len(six['resume_files_verified']) == 5 and
          all(r['exists'] and r['no_contact_pattern'] and all(r['modules_present'].values()) for r in six['resume_files_verified']) and
          not six['evidence_gaps_fully_resolved'] and six['goal_status'] in ['active', 'complete'] and six['current_totals'] == stats['totals'])
    check('PDF及页面包含新日期结果和验收入口', all(x in joined_without_whitespace for x in ['INT85', 'INT86', '2025-03-14']) and
          current_soup.select_one('#recent-interviews a[href$="六项目标逐条验收.md"]') is not None)
    check('正文阅读不被视频零读取否定', '不单独构成未完成判据' in six['requirements'][2]['remaining'] and
          '不要求每位作者同时公开全部材料' in six['requirements'][1]['remaining'])
    check('仍保留完整目标及未满足项', progress['status'] == 'active' and len(stats['remaining_gaps']) >= 3 and
          stats['opinion_coverage']['actual_video_watched_count'] == 0 and stats['current_pass'] == '近期面经与关联纠错')
    result = {'passed': all(c['passed'] for c in checks), 'checks': checks, 'local_links': links,
              'pdf_pages': pages, 'current_totals': stats['totals'], 'pdf_sha256': hashlib.sha256(report_file.read_bytes()).hexdigest(),
              'goal_status': 'active', 'scope': '新增两篇原帖、37处候选人范围修正与六项验收；保留既有材料边界回归检查，不证明全目标完成',
              'visual_review': '待根代理目视本轮PDF首中末页'}
    (BASE / '近期面经与关联纠错交付校验.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'local_links': links, 'pdf_pages': pages,
                      'failures': [c for c in checks if not c['passed']]}, ensure_ascii=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
