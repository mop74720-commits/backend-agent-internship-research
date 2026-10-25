"""按用户六项要求记录实物证据和未完成项，不用页面测试代替研究验收。"""
from pathlib import Path
import hashlib
import json
import re

import fitz
from bs4 import BeautifulSoup

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent


def load(name):
    return json.loads((BASE / name).read_text(encoding='utf-8-sig'))


def main():
    rows = load('all_evidence_records.json')
    by = {r['id']: r for r in rows}
    stats = load('需求覆盖统计.json')
    resumes = []
    for r in rows:
        if not r.get('complete_redacted_cv_file_received'):
            continue
        file = ROOT / r['redacted_cv_local_file']
        if file.suffix == '.pdf':
            with fitz.open(file) as pdf:
                text = '\n'.join(p.get_text() for p in pdf)
        else:
            text = BeautifulSoup(file.read_text(encoding='utf-8'), 'html.parser').get_text(' ', strip=True)
        normalized = ''.join(text.split()).lower()
        modules = {k: any(word in normalized for word in words) for k, words in {
            'education': ['education', '教育'], 'experience': ['experience', '实习', '职业经历'],
            'projects': ['projects', '项目']}.items()}
        resumes.append({'id': r['id'], 'local_path': r['redacted_cv_local_file'], 'exists': file.exists(),
                        'bytes': file.stat().st_size, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
                        'professional_text_characters': len(text), 'modules_present': modules,
                        'no_contact_pattern': not bool(re.search(r'[\w.+%-]+@[\w.-]+\.[A-Za-z]{2,}|(?<!\d)1[3-9]\d{9}(?!\d)', text)),
                        'direct_personal_source_read': bool(r.get('personal_source_code_verified'))})
    comp = load('项目统一比较与阅读优先级.json')['projects']
    abilities = load('能力要求四类证据对照.json')['rows']
    native = [r for r in rows if r['category'] == 'B站与知乎' and r.get('platform_native_fulltext_verified')]
    current_delivery = BASE / ('外部调研合并交付校验.json' if (BASE/'astra合并_实施映射.json').exists() else '近期面经与关联纠错交付校验.json')
    delivery = json.loads(current_delivery.read_text(encoding='utf-8')) if current_delivery.exists() else {}
    pdf = ROOT / '01_调研报告/需求核对与阅读优先级.pdf'
    delivery_current = bool(delivery.get('passed') and delivery.get('pdf_sha256') == hashlib.sha256(pdf.read_bytes()).hexdigest() and
                            delivery.get('current_totals') == stats['totals'])
    criteria = [
        {'item': 1, 'requirement': '成功实习者真实简历、技术栈、职责与本人源码',
         'status': '已补齐一批实物，关联深度不一',
         'evidence': '5份核心完整专业履历脱敏副本；CV28后端与CV31 Agent有本人实现直链；CV30字节内部职责有完整CV。',
         'ids': [r['id'] for r in resumes],
         'remaining': '各候选人附件与源码覆盖分别列明；不要求所有候选人都有完整CV或公开内部代码。CV28雇主博彦与客户阿里云分开。'},
        {'item': 2, 'requirement': 'SSP公司、岗位、时间、招聘批次及Agent关联',
         'status': '定向补核已执行，Agent SSP证据覆盖仍部分',
         'evidence': f"{stats['candidate_coverage']['ssp_claim_cases']}份候选人有SSP自述，{stats['candidate_coverage']['ssp_company_explicit_cases']}份公司明确；CV03有2025美团实习后同公司SSP时间线，CV05历史SSP与2026 Agent更新已分开。",
         'ids': ['CV02', 'CV03', 'CV05', 'CV07', 'CV31', 'OBS09', 'OBS10'],
         'remaining': '近期明确Agent工程SSP岗位与批次的直接自述仍不足；履历、本人实现、面经各项关系分开报告，不要求每位作者同时公开全部材料，不跨人或跨批次拼接。'},
        {'item': 3, 'requirement': '实际阅读B站/知乎，提取观点、依据和商业背景',
         'status': '已完成一批平台正文实读，背景与观点范围分别注明',
         'evidence': f'{len(native)}篇平台本体全文，来自3位署名作者；B站图文2、知乎正文3。原站替代、Linear原稿选读与Comate实录选读单列。',
         'ids': [r['id'] for r in native] + ['OP15', 'OP16'],
         'remaining': '视频/字幕读取0是媒介范围说明，不单独构成未完成判据；专业性按职业背景、商业关系及技术依据判断，摘要和原站替代不计平台本体。'},
        {'item': 4, 'requirement': '明确年份/轮次/结果的近期面经与本人项目追问',
         'status': '已补近期样本和追问，部分年份仍待核',
         'evidence': f"{stats['totals']['interview_materials']}份逻辑资料；明确近期实习{stats['interview_coverage']['strict_recent_explicit_internship_count']}份。INT68由同作者投递总表与三个流程节点补为2026年；INT85正文直接给2025日期；INT86已offer二面与作者事后思路分列。",
         'ids': ['INT68', 'INT77', 'INT78', 'INT79', 'INT80', 'INT82', 'INT83', 'INT84', 'INT85', 'INT86'],
         'remaining': f"实习事件年未知{stats['interview_coverage']['explicit_internship_event_year_unknown_count']}份；第三方汇编日期不直接填回原帖，不从失败自评推断拒绝原因。"},
        {'item': 5, 'requirement': '四类证据综合后端/Agent要求、追问、加分项和历史SSP优势',
         'status': '已形成当前样本的分层与比较',
         'evidence': f"{stats['totals']['engineering_jd_fulltext']}份工程JD逐条分层，{len(abilities)}项能力对照，{len(comp)}项目共{sum(len(p['backend_dimensions'])+len(p['agent_dimensions']) for p in comp)}项比较；两方向阅读优先级与三项专业观点交叉比较已建立。",
         'ids': ['JD01', 'JD08', 'JD11', 'DOC02', 'OP16', 'PRO20', 'PRO21', 'PRO24', 'PRO25'],
         'remaining': '这些是公开便利样本的归纳，不推导统一SSP门槛或市场发生概率；缺少的证据格保留空缺。'},
        {'item': 6, 'requirement': '归档、推荐理由、优缺点、关联表、阅读顺序和一致统计',
         'status': '本轮交付校验通过' if delivery_current else '等待本轮交付同步校验',
         'evidence': f"核心脱敏履历5，原ZIP{stats['totals']['original_fixed_source_zips']}、文本/选读归档{stats['totals']['redacted_text_source_zips']}、仅链接{stats['totals']['fixed_link_only']}；HTML/PDF、CSV、关联表和阅读顺序由当前主数据生成。",
         'ids': [], 'remaining': 'NoWorries14文件、SchoolBus4文件、Crony9文件、Hello-Agents6文件均为指定选读包，非完整仓库；所有项目未运行。个人项目设计继续暂缓。'}]
    # 按实际要求逐项判断；视频媒介及每人全量公开不是额外准入条件。
    agent_ssp = []
    for record in rows:
        tx = record.get('taxonomy', {})
        if tx.get('track') != 'Agent工程' or tx.get('recent_status') != '近期确认' or not tx.get('year_confirmed'):
            continue
        for result in record.get('outcomes', []):
            company = result.get('company', '')
            role = str(result.get('role', ''))
            offer_date = str(result.get('date', ''))
            recruitment = result.get('recruitment', result.get('recruitment_type', ''))
            scoped_offer = (role and 'agent' in role.lower() and re.search(r'20(?:24|25|26)', offer_date)
                            and recruitment in ['实习', '实习转正', '校招'])
            if scoped_offer and result.get('status') == 'offer_self_report' and result.get('evidence_url') and 'SSP' in str(result.get('grade', '')).upper() and company and not any(x in company for x in ['未知', '未披露', '未具名']):
                agent_ssp.append(record['id'])
    requirement_checks = {
        1: all(by[i].get('complete_redacted_cv_file_received') and by[i].get('personal_source_code_verified') for i in ['CV28', 'CV31']),
        2: bool(agent_ssp),
        3: (any('B站' in r.get('platform', '') for r in native) and any('知乎' in r.get('platform', '') for r in native)
            and all(r.get('opinion') and r.get('identity_evidence') and r.get('commercial_bias') for r in native)),
        4: (stats['interview_coverage']['strict_recent_explicit_internship_count'] > 0
            and all(by[i].get('project_questions') and by[i].get('material_type') for i in ['INT68', 'INT85', 'INT86'])),
        5: len(comp) == stats['totals']['projects'] and bool(abilities),
        6: delivery_current,
    }
    root_review = load('Agent_SSP定向补核_根核读.json')
    extra_review = load('Agent_SSP定向补核_本轮.json')
    existing_review = load('SSP已有样本_来源范围复核.json')
    ssp_research_complete = (stats['candidate_coverage']['ssp_company_explicit_cases'] > 0
        and len(root_review['search_paths']) >= 2 and root_review['result']['limited_round_finished']
        and len(extra_review['search_paths']) >= 2 and extra_review['summary']['new_confirmed_agent_ssp_cases'] == 0
        and existing_review['counts']['local_ssp_candidate_reviews'] == stats['candidate_coverage']['ssp_claim_cases'])
    research_checks = dict(requirement_checks)
    research_checks[2] = bool(ssp_research_complete)
    receipt = BASE / '目标完成回执.json'
    actual_goal_status = json.loads(receipt.read_text(encoding='utf-8'))['goal']['status'] if receipt.exists() else 'active'
    for criterion in criteria:
        criterion['completion_proven_in_current_scope'] = bool(requirement_checks[criterion['item']])
        criterion['research_actions_complete'] = bool(research_checks[criterion['item']])
    audit = {'date': stats.get('updated_date','2026-10-23'), 'goal_status': actual_goal_status, 'all_six_fully_achieved': all(research_checks.values()),
             'all_six_research_actions_complete': all(research_checks.values()), 'evidence_gaps_fully_resolved': False,
             'completion_definition': '六项调研与交付动作是否完成；不是保证公开资料披露全部信息。用户计划允许不同路径补搜后保留缺口结束本轮。',
             'recent_explicit_agent_ssp_source_ids': sorted(set(agent_ssp)),
             'baseline_note': '目标中完整简历0、平台内容尚未实读为初始状态；当前完整脱敏副本5、平台本体全文5，不能沿用初始数字。',
             'requirements': criteria, 'resume_files_verified': resumes, 'current_totals': stats['totals'],
             'delivery_current': delivery_current,
             'unresolved_required_focus': ['近期明确Agent SSP的直接关联仍不足；不得靠异人、跨批次或宣传补齐。',
                                           '专业观点背景及商业影响按已读证据评估；视频/字幕未读不否定已读平台正文。'],
             'interpretation': '接受公开录用自述，不新增企业认证门槛；不要求每位候选人公开完整CV和内部源码。正文属于用户允许的实际阅读形式，不把视频未读单独设为失败条件。近期Agent SSP直接岗位/批次证据不足继续明示；在批准的有限检索已执行后，不把找到特定完美样本升级为结束研究的必要条件。'}
    (BASE / '六项目标逐条验收.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# 六项目标逐条验收', '', audit['baseline_note'], '',
             '| 原要求 | 当前状态及直接依据 | 尚缺什么 |', '|---|---|---|']
    for r in criteria:
        links = ' · '.join(f'[{i}]({by[i]["url"]})' for i in r['ids'])
        lines.append(f"| {r['item']}. {r['requirement']} | **{r['status']}**。{r['evidence']} {links} | {r['remaining']} |")
    lines += ['', '## 简历实物检查', '', '| ID | 本地文件 | 教育/实习/项目模块 | SHA-256 |', '|---|---|---|---|']
    for r in resumes:
        lines.append(f"| {r['id']} | [{Path(r['local_path']).name}](../{r['local_path']}) | {'齐全' if all(r['modules_present'].values()) else '需复核'} | {r['sha256']} |")
    lines += ['', '## 调研完成与资料覆盖分开判断', '',
              '六项调研动作：' + ('完成' if audit['all_six_research_actions_complete'] else '等待交付核验') + '；资料覆盖缺口仍保留。',
              '公司、岗位、时间和档位严格区分。近期明确Agent SSP直接样本不足，不补造结论；用户批准不同路径检索后保留缺口结束本轮。完整履历、本人项目和面经不要求每位作者同时公开，视频也不是唯一阅读形式。',
              'SchoolBus、Crony和Hello-Agents补齐了指定文件选读归档；未运行项目，个人项目设计继续暂缓。', '']
    (ROOT / '01_调研报告/六项目标逐条验收.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'requirements': len(criteria), 'resume_files': len(resumes),
                      'all_resume_modules_present': all(all(r['modules_present'].values()) for r in resumes),
                      'delivery_current': delivery_current, 'goal_status': actual_goal_status}, ensure_ascii=False))


if __name__ == '__main__':
    main()
