"""核对184条重点补证的来源边界及交付；不代表整体调研已经完成。"""
from pathlib import Path
from collections import Counter
from urllib.parse import urlsplit, unquote
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


def load(name):
    return json.loads((BASE / name).read_text(encoding='utf-8-sig'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    checks = []

    def check(name, passed, detail=None):
        checks.append({'name': name, 'passed': bool(passed), 'detail': detail})

    malformed = []
    for file in ROOT.rglob('*.json'):
        try:
            json.loads(file.read_text(encoding='utf-8-sig'))
        except Exception as error:
            malformed.append({'file': str(file.relative_to(ROOT)), 'error': str(error)})
    check('全部JSON可解析', not malformed, malformed)
    rows = load('all_evidence_records.json')
    by = {r['id']: r for r in rows}
    stats = load('需求覆盖统计.json')
    progress = load('重点补证统计.json')
    cv = load('candidate_cases.json')['cases']
    iv = load('interview_records.json')
    projects = load('project_recommendations.json')['projects']
    comp = load('项目统一比较与阅读优先级.json')['projects']
    previous = load('重点补证前主数据快照.json')['records']
    check('8条增量与176条旧快照吻合', len(rows) == len(by) == 184 and len(previous) == 176 and
          set(by) - {r['id'] for r in previous} == set(progress['new_record_ids']) and len(progress['new_record_ids']) == 8)
    check('三份分类主表均与总表相同', all(r == by[r['id']] for r in cv + iv + projects))
    check('30候选人76面经23项目与统计一致', len(cv) == 30 and len(iv) == 76 and len(projects) == 23 and
          Counter(r['category'] for r in rows) == stats['category_counts'] and stats['totals'] == progress['current_totals'])
    check('30候选人均呈现四段关系', all(set(r['chain']) == {'outcome', 'profile', 'project', 'interview'} for r in cv))
    check('69全文7部分严格近期9实习事件年未知38', Counter(r['reading']['scope'] for r in iv) == {'全文': 69, '部分': 7} and
          sum(bool(r.get('strict_recent_internship')) for r in iv) == 9 and
          sum(r['taxonomy']['recruitment'] == '实习' and r['taxonomy']['recent_status'] == '年份未知' for r in iv) == 38)
    check('INT11发表年不冒充面试年', by['INT11']['publication_recent_event_year_unknown'] and
          not by['INT11']['taxonomy']['year_confirmed'] and not by['INT11']['strict_recent_internship'] and
          '发表' in by['INT11']['taxonomy']['experience_date_text'] and
          stats['interview_coverage']['publication_recent_event_year_unknown_count'] == 13)
    check('CV07两项后端offer只确认2025而非AgentSSP', len(by['CV07']['outcomes']) == 2 and
          all(o['role'] == '后端实习' and o['grade'] == '未披露' and '2025' in o['date'] for o in by['CV07']['outcomes']) and
          by['CV07']['taxonomy']['year_confirmed'] and 'PR归属未闭合' in str(by['CV07']['chain']))
    check('两篇本人面经与offer批次年份结果分开', all(by[i]['candidate_link_ids'] == ['CV07'] and
          by[i]['taxonomy']['recruitment'] == '未知' and not by[i]['taxonomy']['year_confirmed'] and
          by[i]['result_status'] == 'unknown' and not by[i]['strict_recent_internship'] for i in ['INT82', 'INT83']))
    check('两位新候选人保持独立缺口', not by['CV29']['complete_redacted_cv_file_received'] and
          by['CV30']['complete_redacted_cv_file_received'] and by['CV29']['personal_source_code_verified'] and
          not by['CV30']['personal_source_code_verified'] and not by['CV30']['ssp_claim_present'] and
          all(not by[i]['has_confirmed_personal_interview_source'] for i in ['CV29', 'CV30']))
    check('23项目345维均有来源及阅读范围', len(comp) == 23 and
          sum(len(p['backend_dimensions']) + len(p['agent_dimensions']) for p in comp) == 345 and
          all(d['source_URL'] and d['read_scope'] for p in comp for track in ['backend', 'agent'] for d in p[track + '_dimensions'].values()))
    cp = {p['id']: p for p in comp}
    check('课程项目边界与Agent反例风险明确', 'TinyKV' in cp['PRO22']['source_nature_boundary'] and
          all(v['status'] == '不适用' for v in cp['PRO22']['agent_dimensions'].values()) and
          cp['PRO23']['agent_priority']['level'] == '待核' and cp['PRO23']['agent_dimensions']['权限']['status'] == '静态风险' and
          '同进程' in cp['PRO23']['agent_dimensions']['权限']['finding'])
    check('平台5正文与视频0分列且未重复作者', stats['opinion_coverage']['primary_bilibili_or_zhihu_full_content_verified_count'] == 5 and
          stats['opinion_coverage']['zhihu_native_fulltexts_read'] == 3 and stats['opinion_coverage']['bilibili_native_articles_read'] == 2 and
          stats['opinion_coverage']['actual_video_watched_count'] == 0 and '5篇' in stats['opinion_coverage']['native_authors_scope'] and
          '3位' in stats['opinion_coverage']['native_authors_scope'] and not by['OP14']['reading']['video_watched'])
    check('专家JD观点未计成功者面经且已移出正文待核', by['DOC12']['category'] == '观点范围对照' and
          by['DOC12']['reading']['scope'] == '部分' and not any('927156901626810368' in r['url'] for r in load('待手动访问链接.json')))
    check('16原ZIP4派生3仅链接总量分开', stats['project_coverage'] == {'projects': 23, 'source_archives': 20,
          'original_fixed_source_zips': 16, 'redacted_text_source_zips': 4, 'fixed_link_only': 3, 'executed_projects': 0})
    found = load('重点补证_大厂实习履历.json')
    file_checks = []
    for archive in found['archives']:
        file = ROOT / archive['local_path']
        ok = sha(file.read_bytes()) == archive['sha256'] and file.stat().st_size == archive['bytes']
        with zipfile.ZipFile(file) as z:
            ok = ok and z.testzip() is None and len(z.namelist()) == archive['members']
            licenses = [n for n in z.namelist() if n.endswith('/LICENSE') and n.count('/') == 1]
            ok = ok and len(licenses) == 1 and sha(z.read(licenses[0])) == archive['license_sha256']
            source_checks = []
            for source in found['read_source_files']:
                if source['repo'] != archive['repo']:
                    continue
                names = [n for n in z.namelist() if '/' in n and n.split('/', 1)[1] == source['path']]
                match = len(names) == 1 and sha(z.read(names[0])) == source['sha256']
                source_checks.append({'path': source['path'], 'passed': match})
                ok = ok and match
        file_checks.append({'file': archive['local_path'], 'passed': ok, 'read_files': source_checks})
    check('新2ZIP实物CRC哈希许可及12条核读文件', len(file_checks) == 2 and all(x['passed'] for x in file_checks) and
          sum(len(x['read_files']) for x in file_checks) == 12, file_checks)
    resume = found['new_core_complete_profiles'][0]['attachment']
    file = ROOT / resume['local_path']
    with fitz.open(file) as pdf:
        text = '\n'.join(p.get_text() for p in pdf)
        clean = not re.search(r'[\w.+%-]+@[\w.-]+\.[A-Za-z]{2,}|(?<!\d)1[3-9]\d{9}(?!\d)', text)
        no_extras = not pdf.get_xml_metadata() and all(not p.get_links() and not list(p.annots() or []) and not p.get_images() for p in pdf)
        private_keys = ['author', 'subject', 'keywords', 'creator', 'producer', 'creationDate', 'modDate']
        check('新完整脱敏PDF实物hash全部专业模块及隐私', sha(file.read_bytes()) == resume['sha256'] and len(pdf) == 1 and clean and no_extras and
              all(not pdf.metadata.get(k) for k in private_keys) and all(x in text for x in resume['professional_modules']))
    check('4核心完整脱敏履历与3研究对照分列', sum(bool(r.get('complete_redacted_cv_file_received')) for r in cv) == 4 and
          len(load('履历脱敏副本目录.json')['core_files']) == 4 and len(load('履历脱敏副本目录.json')['records']) == 3)
    expected_csv = {'03_简历与候选人案例/候选人证据链对照.csv': 30, '04_面经与专业观点/面经统一分类.csv': 76,
                    '06_项目分析与推荐/项目统一比较.csv': 345, '08_证据索引与统计/全部资料统一分类.csv': 184,
                    '08_证据索引与统计/能力要求四类证据对照.csv': 11, '03_简历与候选人案例/履历文件索引.csv': 7}
    for name, expected in expected_csv.items():
        with (ROOT / name).open(encoding='utf-8-sig', newline='') as f:
            count = len(list(csv.reader(f))) - 1
        check('CSV ' + name, count == expected, count)
    cache = {}

    def page(file):
        if file not in cache:
            soup = BeautifulSoup(file.read_text(encoding='utf-8-sig'), 'html.parser')
            cache[file] = (soup, {x['id'] for x in soup.select('[id]')} | {x['name'] for x in soup.select('a[name]')})
        return cache[file]

    broken, count = [], 0
    for file in REPORT.glob('*.html'):
        for link in page(file.resolve())[0].select('a[href]'):
            url = urlsplit(link['href'])
            if url.scheme or url.netloc:
                continue
            target = (file.parent / unquote(url.path)).resolve() if url.path else file.resolve()
            count += 1
            if not target.exists() or (url.fragment and target.suffix.lower() == '.html' and unquote(url.fragment) not in page(target)[1]):
                broken.append({'file': file.name, 'href': link['href']})
    check('全部报告本地文件链接及锚点', not broken, {'count': count, 'broken': broken})
    with fitz.open(REPORT / '需求核对与阅读优先级.pdf') as pdf:
        texts = [p.get_text() for p in pdf]
        full = '\n'.join(texts)
        pages = len(pdf)
        check('PDF无空白孤立页且覆盖全部本轮ID', all(len(t.strip()) > 150 for t in texts) and all(i in full for i in progress['new_record_ids']),
              {'pages': pages, 'characters': [len(t) for t in texts]})
        check('PDF文本无横向裁切', all(all(b[0] >= 0 and b[2] <= p.rect.width + 1 for b in p.get_text('blocks')) for p in pdf))
    browser = load('重点补证浏览器校验.json')
    check('当前真实浏览器与移动端交互通过', browser.get('pdf_exported') and not browser['errors'] and all(c['passed'] for c in browser['checks']), len(browser['checks']))
    check('维持未完成目标及缺口', progress['status'] == 'active' and len(stats['remaining_gaps']) >= 3 and
          load('目标执行统计.json')['current_totals'] == stats['totals'] and stats['recent_agent_ssp_complete_chain_confirmed'] == 0)
    result = {'passed': all(x['passed'] for x in checks), 'scope': '重点补证来源边界与交付一致性，不证明整体目标完成',
              'checks': checks, 'local_links': count, 'pdf_pages': pages, 'goal_status': 'active',
              'visual_review': '待根代理目视本轮报告PDF首中末页及新履历PDF'}
    (BASE / '重点补证交付校验.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'local_links': count, 'pdf_pages': pages,
                      'failures': [c for c in checks if not c['passed']]}, ensure_ascii=False, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
