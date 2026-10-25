"""核对本轮真实增量、日期/结果边界及当前交付；不证明调研全目标完成。"""
from collections import Counter
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
    prior = load('SSP与时间补核前主数据快照.json')
    old = {r['id']: r for r in prior['records']}
    stats = load('需求覆盖统计.json')
    progress = load('SSP与时间补核统计.json')
    check('仅新增INT84且旧189条记录保持一致', len(rows) == len(by) == 190 and len(old) == 189 and
          set(by) - set(old) == {'INT84'} and all(by[k] == v for k, v in old.items()))
    check('上一轮189快照统计保留', load('近期Agent补链统计.json')['current_totals']['logical_evidence_records'] == 189)
    check('当前统计和累计目标一致', stats['totals'] == progress['current_totals'] == load('目标执行统计.json')['current_totals'] and
          Counter(r['category'] for r in rows) == stats['category_counts'] and progress['new_record_ids'] == ['INT84'])
    iv = load('interview_records.json')
    cv = load('candidate_cases.json')['cases']
    projects = load('project_recommendations.json')['projects']
    check('分类表实物与主记录一致', all(r == by[r['id']] for r in iv + cv + projects) and
          len(iv) == 77 and len(cv) == 31 and len(projects) == 25)
    check('77面经70全文7部分49明确实习', Counter(r['reading']['scope'] for r in iv) == {'全文': 70, '部分': 7} and
          sum(r['taxonomy']['recruitment'] == '实习' for r in iv) == 49)
    check('严格近期9与辅助13不因推定年增加', sum(bool(r.get('strict_recent_internship')) for r in iv) == 9 and
          sum(bool(r.get('publication_recent_event_year_unknown')) for r in iv) == 13 and
          sum(r['taxonomy']['recruitment'] == '实习' and r['taxonomy']['recent_status'] == '年份未知' for r in iv) == 39)
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
          load('interview_topic_index.json')['scope_records'] == 77)
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
    check('既有25项目375维与附件统计保持', load('项目统一比较与阅读优先级.json') == prior['comparison'] and
          stats['project_coverage']['source_archives'] == 22 and stats['project_coverage']['executed_projects'] == 0 and
          sum(bool(c.get('complete_redacted_cv_file_received')) for c in cv) == 5)
    for rel, count in {'03_简历与候选人案例/候选人证据链对照.csv': 31, '04_面经与专业观点/面经统一分类.csv': 77,
                       '06_项目分析与推荐/项目统一比较.csv': 375, '08_证据索引与统计/全部资料统一分类.csv': 190,
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
    browser = load('SSP与时间补核浏览器校验.json')
    check('当前浏览器筛选搜索及手机显示通过', browser.get('pdf_exported') and not browser['errors'] and all(c['passed'] for c in browser['checks']), len(browser['checks']))
    check('仍保留完整目标及未满足项', progress['status'] == 'active' and len(stats['remaining_gaps']) >= 3 and
          stats['opinion_coverage']['actual_video_watched_count'] == 0 and stats['current_pass'] == 'SSP与时间补核')
    result = {'passed': all(c['passed'] for c in checks), 'checks': checks, 'local_links': links,
              'pdf_pages': pages, 'pdf_sha256': hashlib.sha256(report_file.read_bytes()).hexdigest(),
              'goal_status': 'active', 'scope': '本轮新增面经及当前交付核对，不证明全目标完成',
              'visual_review': '待根代理目视本轮PDF首中末页'}
    (BASE / 'SSP与时间补核交付校验.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'local_links': links, 'pdf_pages': pages,
                      'failures': [c for c in checks if not c['passed']]}, ensure_ascii=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
