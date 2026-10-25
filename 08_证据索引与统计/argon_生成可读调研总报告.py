"""把已核材料写成读者可直接使用的报告；不新增招聘或录用事实。"""
from pathlib import Path
from html import escape
import json
import os
import re

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / '01_调研报告'
TITLE = 'argon_实习求职调研总报告'
DETAIL = 'argon_资料检索与证据详表.html'


def load(name):
    return json.loads((BASE / name).read_text(encoding='utf-8-sig'))


def E(value):
    if isinstance(value, (list, dict)):
        return escape(json.dumps(value, ensure_ascii=False))
    return escape(str(value or ''))


def rel(root_relative, parent=REPORT):
    return Path(os.path.relpath(ROOT / root_relative, parent)).as_posix()


def link(url, label, cls=''):
    attr = f' class="{cls}"' if cls else ''
    return f'<a{attr} href="{E(url)}">{E(label)}</a>'


def clean_item(text):
    return str(text or '').strip().rstrip('。；; ')


def join_clean(values, sep='；'):
    if isinstance(values, str):
        return values.strip()
    parts = [clean_item(v) for v in (values or []) if clean_item(v)]
    if not parts:
        return ''
    return sep.join(parts) + '。'


def bullet_html(values, cls='compact-list', limit=None):
    if isinstance(values, str):
        items = [clean_item(x) for x in re.split(r'[；\n]+', values) if clean_item(x)]
    else:
        items = [clean_item(x) for x in (values or []) if clean_item(x)]
    if limit:
        items = items[:limit]
    if not items:
        return ''
    return f'<ul class="{cls}">' + ''.join(f'<li>{E(x)}。</li>' for x in items) + '</ul>'


def ownership_text(value):
    if isinstance(value, list):
        parts = []
        for v in value:
            if isinstance(v, dict):
                cid = str(v.get('candidate_id') or '工程参照')
                finding = clean_item(v.get('finding', ''))
                parts.append(f'{cid}：{finding}' if finding else cid)
            elif clean_item(v):
                parts.append(clean_item(v))
        return join_clean(parts)
    return str(value or '')


def top_nav_html(current_dir, active_key=''):
    entries = [
        ('start', 'argon_00_开始阅读.html', '开始阅读'),
        ('report', f'01_调研报告/{TITLE}.html', '调研总报告'),
        ('jobs', '02_招聘岗位资料/argon_岗位要求统计与解读.html', '岗位要求统计'),
        ('atlas', '03_简历与候选人案例/argon_候选人与简历图册.html', '候选人简历图册'),
        ('interviews', '04_面经与专业观点/argon_面经重点与项目追问.html', '面经与项目追问'),
        ('projects', '06_项目分析与推荐/argon_项目比较与精读指南.html', '25项目精读指南'),
        ('detail', f'01_调研报告/{DETAIL}', '239条证据检索'),
    ]
    links = []
    for key, target, label in entries:
        href = rel(target, current_dir)
        cls = 'active' if key == active_key else ''
        links.append(link(href, label, cls))
    pdf_href = rel(f'01_调研报告/{TITLE}.pdf', current_dir)
    links.append(link(pdf_href, '重点版 PDF ↗', 'pdf-pill'))
    return (
        '<header class="top-bar screen-only"><div class="top-bar-inner">'
        '<span class="top-brand">后端 &amp; Agent 实习调研</span>'
        '<nav class="top-links" aria-label="全站导航">' + ''.join(links) + '</nav>'
        '</div></header>'
    )


CSS = '''
:root{--ink:#1e292d;--muted:#5c6b68;--paper:#fffefb;--bg:#ede9e0;--teal:#1d5c59;--teal-soft:#e6f0ee;--rust:#a3482d;--rust-soft:#f9eee8;--line:#d6dcd4;--tint:#f2f5f0}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:68px}body{margin:0;color:var(--ink);background:var(--bg);font:16px/1.72 "Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;overflow-wrap:anywhere}a{color:var(--teal);text-underline-offset:3px}a:hover{color:var(--rust)}
.top-bar{position:sticky;top:0;z-index:20;background:#1b363acc;backdrop-filter:blur(8px);border-bottom:1px solid #2d4f54;color:#fff}
.top-bar-inner{max-width:1410px;margin:auto;padding:10px 24px;display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}
.top-brand{font-weight:700;font-size:14px;letter-spacing:.8px;color:#e4f2ef;white-space:nowrap}
.top-links{display:flex;gap:6px 10px;flex-wrap:wrap;align-items:center}
.top-links a{color:#d3e6e3;text-decoration:none;font-size:13px;padding:4px 9px;border-radius:4px;transition:background .15s}
.top-links a:hover,.top-links a.active{background:#2c5855;color:#fff}
.top-links a.pdf-pill{background:#a3482d;color:#fff;font-weight:600}
.layout{max-width:1410px;margin:auto;display:grid;grid-template-columns:210px minmax(0,1fr);gap:28px;padding:26px 24px 70px}.sidebar{position:sticky;top:68px;align-self:start}.brand{font:700 20px/1.4 "SimSun","Noto Serif CJK SC",serif;border-top:5px solid var(--rust);padding-top:14px;margin-bottom:16px}.sidebar a{display:block;text-decoration:none;padding:7px 0;border-bottom:1px solid var(--line);font-size:14px}.sidebar .small{font-size:12px;line-height:1.6;margin-top:18px}main{min-width:0}.report-page{background:var(--paper);padding:40px 46px;margin-bottom:26px;border:1px solid #dddcd2;box-shadow:0 5px 18px #28353408;border-radius:4px}.kicker{color:var(--rust);font-size:12px;letter-spacing:2px;font-weight:700;margin-bottom:12px;text-transform:uppercase}h1,h2,h3{font-family:"SimSun","Noto Serif CJK SC",serif;line-height:1.35;letter-spacing:.3px}h1{font-size:38px;margin:0 0 18px}h2{font-size:28px;margin:0 0 14px}h3{font-size:20px;margin:22px 0 9px}p{margin:9px 0 14px}.lead{font-size:18px;line-height:1.65;color:#2c3a3e}.muted,.small{color:var(--muted)}.small{font-size:13px}.thesis{border-left:5px solid var(--rust);padding:14px 20px;background:var(--rust-soft);font-size:18px;line-height:1.6;margin:20px 0}.two{display:grid;grid-template-columns:1fr 1fr;gap:18px}.three{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.box{padding:16px 18px;background:var(--tint);border-top:3px solid var(--teal);min-width:0;border-radius:2px}.box.warn-box{background:#fbf5ee;border-top-color:var(--rust)}.box h3{margin:0 0 8px;font-family:"Microsoft YaHei",sans-serif;font-size:17px}.box p:last-child,.box ul:last-child{margin-bottom:0}.number{color:var(--rust);font:700 26px/1.3 Georgia,serif;margin-right:8px}.insight{display:grid;grid-template-columns:38px 1fr;gap:12px;margin:18px 0;padding:12px 14px;background:#faf9f5;border-left:3px solid #c8d3cc}.insight h3{font-family:"Microsoft YaHei",sans-serif;font-size:18px;margin:0 0 5px}.insight p{margin:0;font-size:15px}.evidence{font-size:12px;color:var(--muted);margin-top:6px}.evidence a{margin-right:7px}.rule{height:1px;background:var(--line);margin:24px 0}.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:14px;line-height:1.6}th,td{padding:10px 11px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{border-top:2px solid var(--ink);background:#f3f4ee;font-size:13px;white-space:nowrap}td strong{display:block;margin-bottom:3px}.num{font-family:Georgia,serif;font-size:16px;font-weight:700;white-space:nowrap;color:var(--teal)}.pill{display:inline-block;font-size:11px;line-height:1.5;border:1px solid #b5c9bb;border-radius:3px;padding:2px 7px;margin:0 5px 4px 0;color:#274c47;background:#edf4f0;font-weight:600}.pill.core{background:#1d5c59;color:#fff;border-color:#1d5c59}.pill.select{background:#e7eff5;color:#234969;border-color:#b8cde0}.pill.warn{background:#fbf0e1;border-color:#dbc4a1;color:#71512f}.note{padding:12px 16px;background:#f4f2ec;color:#4f5d5b;border-left:3px solid #9bafa4;font-size:13px;margin:14px 0}.reading{display:grid;grid-template-columns:88px 1fr;gap:12px;border-top:1px solid var(--line);padding:11px 0}.reading strong{color:var(--rust)}.candidate-preview{border:1px solid var(--line);padding:16px;min-width:0;background:#fff}.candidate-preview img{display:block;width:100%;height:225px;object-fit:contain;object-position:top;background:#f5f4ef;border:1px solid #e2e4db;margin-bottom:10px}.candidate-preview h3{font-size:18px;margin:8px 0;font-family:"Microsoft YaHei",sans-serif}.candidate-preview p{font-size:14px;line-height:1.6}.qa-block{padding:13px 0;border-top:1px solid var(--line)}.qa-block h3{font-family:"Microsoft YaHei",sans-serif;font-size:18px;margin:0 0 5px}.qa-block p{margin:4px 0;font-size:14px}.question{color:var(--teal);font-weight:700}.project-table td{font-size:13px}.project-table td:first-child{width:21%}.project-table td:nth-child(2){width:31%}.project-table td:nth-child(3){width:30%}.module{font:11.5px/1.6 Consolas,monospace;color:#4a5d56;overflow-wrap:anywhere}.bottom-links{display:flex;flex-wrap:wrap;gap:10px 18px;margin-top:16px}.bottom-links a{background:var(--teal-soft);padding:6px 12px;border-radius:4px;text-decoration:none;font-weight:600;font-size:14px}.page-foot{margin-top:20px;padding-top:10px;border-top:1px solid var(--line);font-size:12px;color:var(--muted)}ul{padding-left:20px}li{margin:5px 0}.compact-list{margin:6px 0;padding-left:18px;font-size:14px;line-height:1.6}.compact-list li{margin:4px 0}
.catalog-controls{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0;align-items:center;background:#f4f6f2;padding:12px 14px;border:1px solid var(--line);border-radius:4px}input,select,button{font:inherit;font-size:14px;padding:8px 12px;border:1px solid #aabbb0;border-radius:4px;max-width:100%;background:white}input{flex:1;min-width:200px}button{cursor:pointer;transition: all .15s}button.filter-btn.active{background:var(--teal);color:#fff;border-color:var(--teal)}.project-card{border:1px solid var(--line);border-top:3px solid var(--teal);padding:20px 22px;margin:20px 0;background:#fff;border-radius:3px}.project-card.tier-core{border-top-color:var(--rust);background:#fffdfa}.project-card h2{font-size:22px;font-family:"Microsoft YaHei",sans-serif;margin:4px 0 8px}.project-card[hidden]{display:none}.tier-banner{margin:30px 0 12px;padding:10px 14px;background:#e6eeeb;border-left:4px solid var(--teal);font-weight:700;font-size:16px}.screen-only{display:block}
@media(max-width:1000px){.layout{grid-template-columns:1fr;max-width:1000px}.sidebar{position:static;display:flex;gap:8px 15px;flex-wrap:wrap}.brand{width:100%;margin:0;padding-top:8px}.sidebar a{padding:3px 0;font-size:13px}.sidebar .small{display:none}.three{grid-template-columns:1fr}}
@media(max-width:600px){.layout{padding:14px 10px 30px;gap:17px}.report-page{padding:24px 18px;margin-bottom:18px}h1{font-size:30px}h2{font-size:24px}.lead,.thesis{font-size:16px}.two{grid-template-columns:1fr}.scroll table{min-width:650px}.insight{gap:8px;grid-template-columns:30px 1fr}.candidate-preview img{height:280px}.module{font-size:11px}}
@page{size:A4;margin:13mm 14mm 14mm}
@media print{html{scroll-behavior:auto}body{background:white;font-size:11.5px;line-height:1.58}.layout{display:block;max-width:none;margin:0;padding:0}.sidebar,.screen-only,.catalog-controls,.top-bar{display:none!important}.report-page{border:0;box-shadow:none;padding:0;margin:0;break-after:page}.report-page:last-child{break-after:auto}.kicker{font-size:9px;margin:0 0 6px;letter-spacing:1px}h1{font-size:26px;margin-bottom:12px}h2{font-size:21px;margin-bottom:10px}h3{font-size:14.5px;margin:13px 0 6px}.lead{font-size:13px;line-height:1.58}.thesis{font-size:13.5px;padding:10px 14px;margin:14px 0}.two{gap:13px}.box{padding:10px 12px}.box h3{font-size:14px}.number{font-size:20px}.insight{grid-template-columns:28px 1fr;gap:8px;margin:11px 0;padding:8px 10px}.insight h3{font-size:13.5px}.insight p{font-size:11.5px}.evidence{font-size:9px;margin-top:4px}.rule{margin:14px 0}p{margin:6px 0 9px}table,th{font-size:10.3px;line-height:1.5}.scroll{overflow:visible}.scroll table{min-width:0}th,td{padding:6px 6px}tr{break-inside:avoid}.num{font-size:11.5px}.note,.small{font-size:9.8px}.note{padding:8px 11px;margin:10px 0}.reading{grid-template-columns:68px 1fr;padding:8px 0}.candidate-preview{padding:10px}.candidate-preview img{height:210px}.candidate-preview h3{font-size:13px;margin:6px 0}.candidate-preview p{font-size:10.5px;margin:5px 0;line-height:1.55}.qa-block{padding:8px 0}.qa-block h3{font-size:13.5px}.qa-block p{font-size:11.2px;line-height:1.55}.project-table td{font-size:10.8px}.project-table .module{font:10px/1.5 "Microsoft YaHei",sans-serif}.module{font-size:9px;line-height:1.5}.pill{font-size:8.5px;padding:1px 5px}.page-foot{font-size:9px;margin-top:11px;padding-top:8px}a{text-decoration:none;color:#1d5c59}li{margin:3px 0}ul,.compact-list{padding-left:16px;font-size:10.8px}.bottom-links{font-size:10px;gap:6px 12px}.bottom-links a{padding:2px 6px}}
.number{white-space:nowrap;margin-right:0}.qa-block .number{margin-right:8px}
'''


def shell(title, body, navigation=True, current_dir=REPORT, active_key='report'):
    nav = ''.join(link('#'+anchor, text) for anchor, text in [
        ('conclusions','01 核心结论'),('jobs','02 岗位要求对比'),('backend','03 后端面试追问'),
        ('agent','04 Agent面试追问'),('candidates','05 真实履历对标'),('backend-projects','06 后端项目取舍'),
        ('agent-projects','07 Agent项目取舍'),('ssp','08 SSP与工业界观点')])
    side = (
        '<aside class="sidebar"><div class="brand">后端 / Agent<br>实习求职调研</div>'
        + nav
        + link(TITLE+'.pdf','下载重点版 PDF')
        + link('../argon_README.md','查看全局 README')
        + '<p class="small">基于 239 条已核公开证据<br>2026-10-24 精炼整理版</p></aside>'
    ) if navigation else ''
    layout = 'layout' if navigation else 'layout standalone'
    extra = '' if navigation else '<style>.standalone{display:block;max-width:1180px}</style>'
    topbar = top_nav_html(current_dir, active_key)
    return (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>'+E(title)+'</title><style>'+CSS+'</style>'+extra+'</head><body>'
        + topbar
        + '<div class="'+layout+'">'+side+'<main>'+body+'</main></div></body></html>'
    )


def build_interview_pages(synthesis, by, comp):
    """生成 04_面经与专业观点/argon_面经重点与项目追问.html 与 .md，消除重复免责声明与双标点。"""
    out_dir = ROOT / '04_面经与专业观点'
    out_dir.mkdir(exist_ok=True)
    counts = synthesis['counts']

    def detail_ref(rid, label=None):
        return link(f'../01_调研报告/{DETAIL}#{rid}', label or rid)

    # HTML 构建
    html_parts = [
        '<section class="report-page" id="overview">',
        '<div class="kicker">99份面经材料 · 10大能力追问簇 · 8个重点项目对照</div>',
        '<h1>面经重点与项目追问指南</h1>',
        '<p class="lead">面试官不会孤立考察组件名词，而是沿着“业务职责 → 架构取舍 → 极端故障与评测验证”逐层追问。本页将 99 份面经提炼为后端 5 大问题簇与 Agent 5 大问题簇，并直接映射到可核读的项目源码模块。</p>',
        '<div class="three">',
        f'<div class="box"><h3>99 份面经样本构成</h3><p>全文核读 <b>{counts["reading_scope"]["全文"]}</b> 份、部分核读 <b>{counts["reading_scope"]["部分"]}</b> 份。其中严格近期（2025–2026）工程实习 <b>{counts["strict_recent_engineering_internships"]}</b> 份、AI Infra 实习对照 1 份、明确实习但未标年份 <b>{counts["internship_event_year_unknown"]}</b> 份。</p></div>',
        '<div class="box"><h3>后端追问核心主线</h3><p>围绕<b>真实请求链</b>展开：本人负责边界 → SQL/索引与缓存并发回源 → MQ 幂等/补偿与死信 → 线上容量估算与排障验证。</p></div>',
        '<div class="box"><h3>Agent 追问核心主线</h3><p>围绕<b>可控执行闭环</b>展开：多步编排必要性 → RAG 召回重排与工具 Schema 约束 → 持久化恢复与写操作沙箱 → 留出集回归评测。</p></div>',
        '</div>',
        '<p class="note"><b>阅读口径统一说明（全文适用，各条目不再重复标注）：</b>① 原帖提问源自作者面后回忆或复盘转述，用于定位考察机制，非逐字录音或企业统一题库；② “准备深度”为本报告归纳的工程自查目标，不代表原作者现场完整答出；③ 项目与面经按技术主题对照，仅标有候选人编号（如 CV21、CV28、CV31、CV05）的项目存在候选人本人归属关系。</p>',
        '<div class="bottom-links">',
        link('#backend', '01 后端五大追问簇'),
        link('#agent', '02 Agent五大追问簇'),
        link('#projects', '03 八个重点项目源码落点'),
        link('#topics', '04 十个高频主题分布表'),
        link('#ssp', '05 SSP案例共性与阅读路线'),
        '</div></section>'
    ]

    def render_findings_section(key, sec_id, kicker, title, desc):
        sec = [f'<section class="report-page" id="{sec_id}"><div class="kicker">{E(kicker)}</div><h2>{E(title)}</h2><p class="lead">{E(desc)}</p>']
        for f in synthesis[key]:
            sec.append(f'<div class="qa-block" id="{E(f["id"])}">')
            sec.append(f'<h3><span class="number">{E(f["id"])}</span>{E(f["title"])}</h3>')
            sec.append(f'<p><strong>核心判断：</strong>{E(f["conclusion"])}</p>')
            sec.append('<div class="two">')
            sec.append('<div class="box"><h3>面试官怎么追问（问题簇与原题）</h3>')
            sec.append('<p class="small"><b>考察切入点：</b>' + E(join_clean(f.get('question_clusters', []))) + '</p>')
            q_items = []
            for s in f.get('sources', []):
                sid = s['id']
                tag = '近期工程实习' if s.get('strict_recent_engineering') else s.get('group', '面经样本')
                qs = join_clean(s.get('source_questions', []))
                q_items.append(
                    f'<li>{detail_ref(sid)} <a href="{E(s["url"])}" target="_blank" rel="noreferrer">{E(s["title"])} ↗</a> '
                    f'<span class="pill">{E(tag)} · {E(s.get("event_date","时间未标"))}</span><br>'
                    f'<span class="question">追问：</span>{E(qs)}</li>'
                )
            sec.append('<ul class="compact-list">' + ''.join(q_items) + '</ul></div>')
            sec.append('<div class="box"><h3>建议准备到什么程度</h3>')
            sec.append(bullet_html(f.get('preparation_depth', [])))
            pids = [ detail_ref(pid, f'{pid} {comp[pid]["title"].split("：")[0]}') for pid in f.get('project_ids', []) if pid in comp ]
            cids = [ detail_ref(cid) for cid in f.get('capability_ids', []) ]
            sec.append(f'<p class="evidence"><b>关联精读项目：</b>{" · ".join(pids)}<br><b>对应能力矩阵：</b>{" · ".join(cids)}</p>')
            sec.append('</div></div></div>')
        sec.append('</section>')
        return ''.join(sec)

    html_parts.append(render_findings_section(
        'backend_findings', 'backend', '01 · 后端面试核心追问',
        '后端面试：从“用过组件”追问到“边界与故障处理”',
        '后端实习面试极少停留在概念背诵，往往从简历上的一句描述切入，连续追问数据流转、并发冲突、异常恢复与线上指标验证。'
    ))
    html_parts.append(render_findings_section(
        'agent_findings', 'agent', '02 · AGENT工程面试核心追问',
        'Agent 面试：从“调用模型”追问到“可控执行与评测闭环”',
        'Agent 工程岗重点考察候选人是否真正解决过检索噪声、工具失败、状态中断、权限隔离与评测回归等工程问题，同时保留服务端并发与代码实现考察。'
    ))

    # 8个重点项目
    proj_sec = [
        '<section class="report-page" id="projects"><div class="kicker">03 · 八个重点项目源码精读落点</div>',
        '<h2>把面试追问落到具体代码文件与缺陷边界</h2>',
        '<p class="lead">精选 4 个后端代表项目与 4 个 Agent 代表项目。精读时既要吸收其核心机制实现，也要看清静态核查暴露出的并发/评测短板，切勿盲目整仓照搬。</p>',
        '<div class="scroll"><table class="project-table"><thead><tr><th>项目与归属关系</th><th>值得精读的机制与模块入口</th><th>静态核查短板与勿照搬项</th></tr></thead><tbody>'
    ]
    for p in synthesis['projects']:
        pid = p['id']
        own = ownership_text(p.get('ownership', []))
        mods = []
        for m in p.get('modules', []):
            mods.append(
                f'<li><a href="{E(m["url"])}" target="_blank" rel="noreferrer"><b>{E(m["name"])}</b></a> '
                f'<span class="module">({E(m["path"])})</span>：{E(clean_item(m.get("why","")))}。</li>'
            )
        gaps_html = bullet_html(p.get('gaps', []) + ([f'勿照搬：{p["do_not_copy"]}'] if p.get('do_not_copy') else []))
        arch = p.get('attachment', {}).get('archive_file', '')
        arch_link = ''
        if arch:
            found = list((ROOT / '05_项目源码归档').rglob(Path(arch).name))
            if found:
                arch_link = ' · ' + link(rel(found[0].relative_to(ROOT), out_dir), '本地源码归档')
        proj_sec.append(
            f'<tr id="{E(pid)}"><td><strong>{E(pid)} · {E(p["name"])}</strong>'
            f'<span class="pill">{E(p["kind"])}</span><p class="small">{E(own)}</p>'
            f'<p class="evidence">{detail_ref(pid, "证据详情")} · <a href="{E(p["source_url"])}" target="_blank" rel="noreferrer">仓库主页 ↗</a>{arch_link}</p></td>'
            f'<td><p>{E(p["learn"])}</p><ul class="compact-list">{"".join(mods)}</ul></td>'
            f'<td>{gaps_html}</td></tr>'
        )
    proj_sec.append('</tbody></table></div></section>')
    html_parts.append(''.join(proj_sec))

    # 主题分布与 SSP 共性 & 阅读路线
    topic_rows = ''.join(
        f'<tr><td><b>{E(t["theme"])}</b></td><td class="num">{t["all_materials"]}</td>'
        f'<td class="num">{t["strict_recent_engineering_materials"]}</td>'
        f'<td class="num">{t["internship_event_year_unknown_materials"]}</td></tr>'
        for t in counts['topic_index']
    )
    ssp_obs = synthesis['ssp_observations']
    obs_items = []
    for ob in ssp_obs['observations']:
        c_links = ' '.join(detail_ref(cid) for cid in ob.get('candidate_ids', []))
        i_links = ' '.join(detail_ref(iid) for iid in ob.get('interview_ids', []))
        obs_items.append(
            f'<div class="box"><h3>案例共性结论</h3><p>{E(ob["claim"])}</p>'
            + bullet_html(ob.get('basis', []))
            + f'<p class="evidence">关联案例：{c_links} {i_links}</p></div>'
        )
    routes = synthesis['reading_routes']
    html_parts.append(
        '<section class="report-page" id="topics"><div class="kicker">04 · 主题分布与阅读路线</div>'
        '<h2>十个面试高频主题覆盖统计与分方向精读顺序</h2>'
        '<div class="scroll"><table><thead><tr><th>面试考察主题（同一份面经可涉及多个主题）</th><th>全部面经提及 / 99</th><th>严格近期工程实习 / 14</th><th>明确实习但年份未知 / 48</th></tr></thead>'
        f'<tbody>{topic_rows}</tbody></table></div>'
        '<h3 id="ssp">公开 SSP 案例的共性特征与证据边界</h3>'
        f'<div class="two">{"".join(obs_items)}</div>'
        '<div class="two" style="margin-top:16px">'
        '<div class="box"><h3>后端实习精读三步走</h3>' + bullet_html(routes['backend']['steps']) + '</div>'
        '<div class="box"><h3>Agent 工程实习精读三步走</h3>' + bullet_html(routes['agent']['steps']) + '</div>'
        '</div>'
        '<p class="page-foot">'
        + link('../01_调研报告/argon_实习求职调研总报告.html', '返回调研总报告') + ' · '
        + link('../06_项目分析与推荐/argon_项目比较与精读指南.html', '查看全部25个项目精读指南') + ' · '
        + link('../06_项目分析与推荐/argon_后端实习阅读顺序.md', '后端阅读顺序(MD)') + ' · '
        + link('../06_项目分析与推荐/argon_Agent实习阅读顺序.md', 'Agent阅读顺序(MD)')
        + '</p></section>'
    )

    (out_dir / 'argon_面经重点与项目追问.html').write_text(
        shell('面经重点与项目追问', ''.join(html_parts), False, out_dir, 'interviews'),
        encoding='utf-8'
    )

    # Markdown 构建（干净无重复免责声明、无 。；）
    md = [
        '# 面经重点与项目追问指南',
        '',
        '> **核心阅读提示**：',
        f'> - **样本范围**：共核读 **99 份**面经材料（全文 {counts["reading_scope"]["全文"]}、部分 {counts["reading_scope"]["部分"]}），含 **14 份**严格近期（2025–2026）工程实习面经、1 份 AI Infra 对照及 48 份未标事件年的明确实习面经。',
        '> - **口径说明**：面经提问为作者回忆要点转述（非逐字录音）；“建议准备深度”为本报告归纳的自查标准，不代表原作者现场答出；项目与面经按技术主题对照，仅标有候选人编号的项目为候选人本人项目。',
        '',
        '---',
        '',
        '## 一、后端实习面试：五大核心追问簇',
        ''
    ]
    for f in synthesis['backend_findings']:
        md += [
            f'### {f["id"]} · {f["title"]}',
            f'- **核心结论**：{f["conclusion"]}',
            f'- **高频追问切入点**：{join_clean(f.get("question_clusters", []))}',
            '- **建议准备深度**：'
        ]
        for step in f.get('preparation_depth', []):
            md.append(f'  - {clean_item(step)}。')
        md.append('- **代表性原题与来源**：')
        for s in f.get('sources', []):
            tag = '近期工程实习' if s.get('strict_recent_engineering') else s.get('group', '面经')
            md.append(f'  - [{s["id"]} {s["title"]}]({s["url"]})（{tag} · {s.get("event_date","时间未标")}）：{join_clean(s.get("source_questions", []))}')
        md.append(f'- **对照精读项目**：{"、".join(f"[{pid}](../06_项目分析与推荐/argon_项目比较与精读指南.html#{pid})" for pid in f.get("project_ids", []))}')
        md.append('')

    md += ['---', '', '## 二、Agent 工程实习面试：五大核心追问簇', '']
    for f in synthesis['agent_findings']:
        md += [
            f'### {f["id"]} · {f["title"]}',
            f'- **核心结论**：{f["conclusion"]}',
            f'- **高频追问切入点**：{join_clean(f.get("question_clusters", []))}',
            '- **建议准备深度**：'
        ]
        for step in f.get('preparation_depth', []):
            md.append(f'  - {clean_item(step)}。')
        md.append('- **代表性原题与来源**：')
        for s in f.get('sources', []):
            tag = '近期工程实习' if s.get('strict_recent_engineering') else s.get('group', '面经')
            md.append(f'  - [{s["id"]} {s["title"]}]({s["url"]})（{tag} · {s.get("event_date","时间未标")}）：{join_clean(s.get("source_questions", []))}')
        md.append(f'- **对照精读项目**：{"、".join(f"[{pid}](../06_项目分析与推荐/argon_项目比较与精读指南.html#{pid})" for pid in f.get("project_ids", []))}')
        md.append('')

    md += ['---', '', '## 三、八个重点项目：精读模块与避坑清单', '']
    for p in synthesis['projects']:
        md += [
            f'### {p["id"]} · {p["title"]}（{p["kind"]}）',
            f'- **核心学习目标**：{p["learn"]}',
            f'- **候选人归属与结果边界**：{ownership_text(p.get("ownership", []))}',
            '- **推荐精读源码模块**：'
        ]
        for m in p.get('modules', []):
            md.append(f'  - [{m["name"]}]({m["url"]}) (`{m["path"]}`)：{clean_item(m.get("why",""))}。')
        md.append('- **静态核查短板与勿照搬项**：')
        for g in p.get('gaps', []):
            md.append(f'  - {clean_item(g)}。')
        if p.get('do_not_copy'):
            md.append(f'  - **切勿照搬**：{clean_item(p["do_not_copy"])}。')
        md.append('')

    md += [
        '---',
        '',
        '## 四、面试高频主题覆盖统计（99 份面经）',
        '',
        '| 考察主题 | 全部面经提及 (n=99) | 严格近期工程实习 (n=14) | 明确实习但年份未知 (n=48) |',
        '| :--- | :---: | :---: | :---: |'
    ]
    for t in counts['topic_index']:
        md.append(f'| {t["theme"]} | {t["all_materials"]} | {t["strict_recent_engineering_materials"]} | {t["internship_event_year_unknown_materials"]} |')

    md += [
        '',
        '## 五、分方向精读路线建议',
        '',
        '### 1. 后端方向三步精读',
        *[f'- {clean_item(s)}。' for s in routes['backend']['steps']],
        '',
        '### 2. Agent 工程方向三步精读',
        *[f'- {clean_item(s)}。' for s in routes['agent']['steps']],
        ''
    ]
    (out_dir / 'argon_面经重点与项目追问.md').write_text('\n'.join(md) + '\n', encoding='utf-8')


def build_project_and_reading_mds(by, comp, visuals):
    """生成 06_项目分析与推荐/ 下的 5 份高质量可读 Markdown 指南。"""
    rec_dir = ROOT / '06_项目分析与推荐'
    rec_dir.mkdir(exist_ok=True)
    order = load('两方向阅读顺序.json')
    layer = load('技术要求_明确要求与加分项.json')
    cap = load('能力要求四类证据对照.json')
    op_cross = load('专业观点交叉核对_来源与比较.json')
    visual_cids = {a['candidate_id'] for a in visuals.get('assets', []) if a.get('candidate_id')}

    def interview_digest(r):
        qs = r.get('questions') or r.get('key_questions') or []
        if isinstance(qs, list) and qs:
            q_preview = '；'.join(clean_item(x) for x in qs[:3] if clean_item(x))
            if q_preview:
                return f'核心追问：{q_preview[:110]}{"…" if len(q_preview)>110 else ""}。'
        topics = r.get('topics') or []
        if isinstance(topics, list) and topics:
            return '考察主题：' + '、'.join(str(x) for x in topics[:5]) + '。'
        summary = clean_item(r.get('source_summary') or r.get('summary') or '')
        return (summary[:110] + ('…' if len(summary) > 110 else '') + '。') if summary else '详见原文复盘记录。'

    def candidate_digest(r):
        out = clean_item(r.get('outcome', ''))
        if not out and r.get('outcomes'):
            out = '；'.join(f'{x.get("company","")}{x.get("grade","")}/{x.get("status","")}' for x in r['outcomes'][:3])
        take = clean_item(r.get('recommendation') or r.get('strengths') or r.get('source_summary') or '')
        if len(take) > 105:
            take = take[:105] + '…'
        parts = [p for p in [f'结果：{out}' if out else '', f'看点：{take}' if take else ''] if p]
        return ' ｜ '.join(parts) if parts else '详见候选人案例卡。'

    def write_direction_md(key, filename, title, track_key, intro):
        cfg = order[key]
        lines = [
            f'# {title}',
            '',
            f'> **核心原则**：{intro}',
            '> - **配套可视化页面**：[argon_项目比较与精读指南.html](argon_项目比较与精读指南.html) · [argon_面经重点与项目追问.html](../04_面经与专业观点/argon_面经重点与项目追问.html) · [argon_候选人与简历图册.html](../03_简历与候选人案例/argon_候选人与简历图册.html)',
            '',
            '---',
            '',
            '## 一、项目源码分级精读清单（先读机制与缺陷，切勿整仓照搬）',
            ''
        ]
        for group_name, val in cfg['project_routes'].items():
            clean_group = group_name.replace('_', ' · ')
            if isinstance(val, str):
                lines += [f'### {clean_group}', '', f'- {clean_item(val)}。', '']
            elif isinstance(val, list):
                lines += [f'### {clean_group}', '']
                for pid in val:
                    p = comp[pid]
                    prio = p[f'{track_key}_priority']
                    lines.append(f'#### [{pid} · {p["title"]}](argon_项目比较与精读指南.html#{pid})（{prio["level"]}｜[原仓库]({p["source_URL"]})）')
                    lines.append(f'- **为什么读**：{clean_item(prio["reason"])}。')
                    if p.get('limitations'):
                        lines.append(f'- **避坑提示**：{clean_item(p["limitations"][0])}。')
                    if prio.get('read_modules'):
                        lines.append('- **推荐精读模块**：')
                        for m in prio['read_modules']:
                            lines.append(f'  - `{m}`')
                    lines.append('')
            elif isinstance(val, dict):
                lines += [f'### {clean_group}', '']
                for sub_k, pids in val.items():
                    lines.append(f'- **{sub_k}方向**：')
                    for pid in pids:
                        p = comp[pid]
                        prio = p[f'{track_key}_priority']
                        mods = '；'.join(f'`{m}`' for m in prio.get('read_modules', [])[:3])
                        lines.append(f'  - **[{pid} · {p["title"]}](argon_项目比较与精读指南.html#{pid})**（[原仓库]({p["source_URL"]})）：{clean_item(prio["reason"])}。精读入口：{mods}')
                lines.append('')

        # 候选人分级
        cids = cfg['candidate_ids']
        vis_list = [cid for cid in cids if cid in visual_cids]
        art_list = [cid for cid in cids if cid not in visual_cids]
        lines += [
            '---',
            '',
            f'## 二、对标候选人案例（共 {len(cids)} 位，按证据形态分级）',
            '',
            f'> **阅读提示**：{clean_item(cfg["candidate_boundary"])}。',
            '',
            f'### 1. 含公开脱敏简历 / 网页履历的标杆案例（优先对标，共 {len(vis_list)} 位）',
            ''
        ]
        for cid in vis_list:
            r = by[cid]
            lines.append(f'- **[{cid} · {r["title"]}](../03_简历与候选人案例/argon_候选人与简历图册.html#{cid})**（[原始来源]({r["url"]})）：{candidate_digest(r)}')
        lines += ['', f'### 2. 求职经历与面经复盘案例（补充对标，共 {len(art_list)} 位）', '']
        for cid in art_list:
            r = by[cid]
            lines.append(f'- **[{cid} · {r["title"]}](../03_简历与候选人案例/argon_候选人与简历图册.html#{cid})**（[原始来源]({r["url"]})）：{candidate_digest(r)}')

        # 面经分级
        iids = cfg['interview_ids']
        recent_iids = [iid for iid in iids if by[iid].get('taxonomy', {}).get('strict_recent_internship')]
        other_iids = [iid for iid in iids if iid not in recent_iids]
        lines += [
            '',
            '---',
            '',
            f'## 三、精选面经阅读顺序（共 {len(iids)} 份，按时效与代表性分级）',
            '',
            f'### 1. 严格近期（2025–2026）工程实习面经（必读，共 {len(recent_iids)} 份）',
            ''
        ]
        for iid in recent_iids:
            r = by[iid]
            tax = r.get('taxonomy', {})
            dt = tax.get('event_date_text') or r.get('date') or '近期确认'
            lines.append(f'- **[{iid} · {r["title"]}]({r["url"]})**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#{iid}) · {dt}）：{interview_digest(r)}')
        lines += ['', f'### 2. 高价值专项追问与经典实习面经（选读，共 {len(other_iids)} 份）', '']
        for iid in other_iids:
            r = by[iid]
            tax = r.get('taxonomy', {})
            rec = tax.get('recruitment', '实习')
            yr = '年份已核' if tax.get('year_confirmed') else '年份未标'
            lines.append(f'- **[{iid} · {r["title"]}]({r["url"]})**（[证据卡](../01_调研报告/argon_资料检索与证据详表.html#{iid}) · {rec}/{yr}）：{interview_digest(r)}')
        lines.append('')
        (rec_dir / filename).write_text('\n'.join(lines) + '\n', encoding='utf-8')

    write_direction_md(
        'backend', 'argon_后端实习阅读顺序.md', '后端开发实习：分级阅读与源码精读清单', 'backend',
        '先看 2025–2026 严格近期工程实习面经与含完整履历的候选人案例，明确“数据库/缓存/MQ/并发排障”的追问深度，再对照精读 SchoolBus、UltiCode、ResiCache 与 ShenYu 的核心模块。'
    )
    write_direction_md(
        'agent', 'argon_Agent实习阅读顺序.md', 'Agent 工程实习：分级阅读与源码精读清单', 'agent',
        '先看字节/中科曙光等真实 Agent 实习履历（CV30、CV31）与近期 Agent 面经，重点掌握“状态图编排、RAG 召回重排、工具约束与回归评测”，再对照精读 Spring AI Alibaba、open_deep_research、Sprout 与 NoWorries。'
    )

    # 3. 生成 argon_技术要求_明确要求与加分项.md（去除拼接补丁备注，结构化呈现）
    t_lines = [
        '# 岗位技术要求分层与四类证据对照表',
        '',
        '> **统计范围**：基于 **24 份**可比工程实习 JD 全文（后端 10、Agent 工程 11、混合 3），严格区分 **明确要求（硬门槛）**、**优先/加分项** 与 **工作职责**，并与候选人履历、99 份面经及 25 个项目源码交叉印证。',
        '> - 更详细的图表与公司去重敏感性分析见：[argon_岗位要求统计与解读.html](../02_招聘岗位资料/argon_岗位要求统计与解读.html)',
        '',
        '---',
        '',
        '## 一、核心结论：硬门槛 vs 加分项 vs 面试追问',
        '',
        '### 1. 后端开发方向',
        '- **一门主力服务端语言与计算机基础**：岗位允许 Java / Go / C++ 择一，重点考察并发模型、内存机制、网络协议与数据结构算法，不要求多语言全会。',
        '- **数据库、缓存与消息队列**：MySQL、Redis 与 MQ 在多数岗位明确点名（部分岗位将数据库/KV 列为“有一定了解”或将 MQ 列为“优先项”）；面试必追问事务隔离、缓存并发回源（Single-Flight/锁）与消息幂等补偿（参考 [PRO19](argon_项目比较与精读指南.html#PRO19)、[PRO20](argon_项目比较与精读指南.html#PRO20)、[PRO21](argon_项目比较与精读指南.html#PRO21)）。',
        '- **分布式架构与开源贡献**：高并发容灾、微服务治理与开源 PR 多为优先加分项或入职职责；可通过 [PRO09 ShenYu](argon_项目比较与精读指南.html#PRO09) 学习如何用高价值测试 PR 证明工程能力。',
        '',
        '### 2. Agent 工程方向',
        '- **服务端基础 + Agent/LLM 基本认知**：从基础语言与算法，到 RAG 检索、Prompt 与 Agent 框架原理；不同团队门槛跨度较大，需区分应用开发岗与底层 Runtime 岗（如 JD26）。',
        '- **工具协议、异常恢复与自动化评测**：多出现在工作职责与高频面试追问中（参考 [CV30](../03_简历与候选人案例/argon_候选人与简历图册.html#CV30)、[CV31](../03_简历与候选人案例/argon_候选人与简历图册.html#CV31)、[INT84](../01_调研报告/argon_资料检索与证据详表.html#INT84)）；准备项目时重点打磨状态持久化、工具失败兜底与留出集回归评测（对照 [PRO04](argon_项目比较与精读指南.html#PRO04)、[PRO06](argon_项目比较与精读指南.html#PRO06)、[PRO24](argon_项目比较与精读指南.html#PRO24)、[PRO25](argon_项目比较与精读指南.html#PRO25)）。',
        '- **训练微调与论文要求边界**：仅策略算法对照岗（JD15/16/28/29）将深度学习训练列为核心门槛；应用工程岗中 SFT/RL 多为了解或加分项。',
        '',
        '---',
        '',
        '## 二、11 项核心能力 × 四类证据对照表',
        '',
        '| 能力编号与名称 | 核心考察问题 | 需证明的工程深度 | 常见准备误区（避坑） | 推荐精读项目 |',
        '| :--- | :--- | :--- | :--- | :--- |'
    ]
    for r in cap['rows']:
        pro_links = '、'.join(f"[{pid}](argon_项目比较与精读指南.html#{pid})" for pid in r.get('project_ids', [])[:4])
        t_lines.append(
            f"| **{r['id']} · {r['ability']}**<br><small>方向：{r.get('track','通用')}</small> "
            f"| {clean_item(r.get('question',''))}。 "
            f"| {clean_item(r.get('competency',''))}。 "
            f"| {clean_item(r.get('common_pitfall',''))}。 "
            f"| {pro_links} |"
        )

    t_lines += [
        '',
        '---',
        '',
        '## 三、24 份可比工程 JD 逐条分层速查表',
        '',
        '| JD 编号与岗位 | 公司与方向 | 明确要求（硬门槛） | 优先/加分项 | 工作职责要点 |',
        '| :--- | :--- | :--- | :--- | :--- |'
    ]
    for r in layer['job_requirement_rows']:
        req = '；'.join(clean_item(x) for x in r.get('explicit_requirements', []) if clean_item(x)) or '未单列'
        pref = '；'.join(clean_item(x) for x in r.get('explicit_preferences', []) if clean_item(x)) or '未单列'
        duty = clean_item(r.get('duties_not_entry_gates', '')) or '未单列'
        t_lines.append(f"| **[{r['id']}]({r['source_URL']})**<br>{r['role']} | {r['company']}<br>（{r['track']}） | {req} | {pref} | {duty} |")

    t_lines += [
        '',
        '---',
        '',
        '## 四、代表性候选人案例的竞争力亮点与边界',
        '',
        f'> **SSP 归因准则**：{clean_item(layer["ssp_conclusion"]["what_is_supported"])}；{clean_item(layer["ssp_conclusion"]["missing"])}。',
        ''
    ]
    for r in layer['success_case_advantages']:
        cid = r['candidate_id']
        t_lines.append(f"- **[{cid}](../03_简历与候选人案例/argon_候选人与简历图册.html#{cid})**（[原文链接]({r['source_URL']}) · {r.get('event_time','')}）：{clean_item(r['observation'])}。")
    t_lines.append('')
    (rec_dir / 'argon_技术要求_明确要求与加分项.md').write_text('\n'.join(t_lines) + '\n', encoding='utf-8')

    # 4. 生成 argon_专业观点交叉核对_评测与工具恢复.md
    rec_op = op_cross.get('record', {})
    op_lines = [
        '# 工业界专业观点交叉核对：Agent 评测、工具恢复与上下文工程',
        '',
        '> **核心目的**：将工业界一线团队（Anthropic、百度 Comate、字节/阿里工程实践）的方法论与本包精读项目的源码实现做交叉核对，帮你把专家经验转化为可落地的**项目自检清单**。',
        '',
        '---',
        '',
        '## 一、三大核心议题交叉核对表（工业界观点 × 源码对照 × 行动建议）',
        '',
        '| 核对议题 | 工业界核心结论与面经印证 | 对应项目源码精读落点 | 备考与项目打磨建议 | 关联证据编号 |',
        '| :--- | :--- | :--- | :--- | :--- |'
    ]
    for c in op_cross['comparisons']:
        ev_links = '、'.join(f"[{eid}](../01_调研报告/argon_资料检索与证据详表.html#{eid})" for eid in c.get('evidence_ids', []))
        op_lines.append(
            f"| **{c['topic']}** "
            f"| {clean_item(c['finding'])}。 "
            f"| {clean_item(c['project_reading'])}。<br><small>定位：`{c.get('primary_locator','')}`</small> "
            f"| {clean_item(c['recommendation'])}。 "
            f"| {ev_links} |"
        )

    op_lines += [
        '',
        '---',
        '',
        f'## 二、重点工业界实录解析：{rec_op.get("id","OP16")} · {rec_op.get("title","")}',
        '',
        f'- **原文来源**：[{rec_op.get("title","")}]({rec_op.get("url","")})（讲师：{rec_op.get("author","")} · 发布日期：{rec_op.get("published_date","")}）',
        f'- **会务核验**：[讲师主页]({rec_op.get("identity_url","")}) · [议题详情]({rec_op.get("presentation_url","")})',
        '- **核心工程论点提炼**：',
        *[f'  - {clean_item(x)}。' for x in rec_op.get('points', [])],
        f'- **阅读与采信边界**：{clean_item(rec_op.get("reading_scope",""))}；{clean_item(rec_op.get("recruitment_boundary",""))}。',
        '',
        '---',
        '',
        '## 三、项目自检四问（面试前必查）',
        '',
        '1. **评测闭环**：你的 Agent 项目是否只有几个手工成功截图？能否提供固定留出集、基线对比与 Bad Case 逐题退化分类（参考 [PRO06](argon_项目比较与精读指南.html#PRO06)）？',
        '2. **工具与状态恢复**：当外部 API 超时、模型传参格式错误或进程中断时，是直接报错退出，还是有 Schema 校验、重试退避与 Checkpoint 状态恢复（参考 [PRO04](argon_项目比较与精读指南.html#PRO04)）？',
        '3. **安全与写操作隔离**：如果 Agent 具备文件读写或命令执行能力，权限拦截在服务端哪一层？切勿把“修改环境变量”误当成系统级安全沙箱（避坑 [PRO25](argon_项目比较与精读指南.html#PRO25)）。',
        '4. **个人贡献边界**：如果项目基于开源框架或团队脚手架修改，能否在 1 分钟内指明哪几个文件/PR 是你本人的核心增量（参考 [PRO09](argon_项目比较与精读指南.html#PRO09)、[CV28](../03_简历与候选人案例/argon_候选人与简历图册.html#CV28)）？',
        ''
    ]
    (rec_dir / 'argon_专业观点交叉核对_评测与工具恢复.md').write_text('\n'.join(op_lines) + '\n', encoding='utf-8')

    # 5. 生成 argon_外部调研_文档判断与阅读模块.md
    docs = [by[f'DOC{str(i).zfill(2)}'] for i in range(1, 11) if f'DOC{str(i).zfill(2)}' in by]
    doc_lines = [
        '# 外部调研文档（DOC01–DOC10）价值判断与对应精读模块',
        '',
        '> **使用说明**：本表对外部调研合入的 10 份综述文档（`DOC01`–`DOC10`）进行证据去重与工程价值评估，并将其中有价值的结论直接映射到本包已核实的 **JD、候选人履历、面经与源码模块**，避免重复阅读二手综述。',
        '',
        '---',
        '',
        '## 一、10 份外部调研文档（DOC01–DOC10）逐份评估表',
        '',
        '| 编号 | 文档主题与摘要 | 推荐动作 | 可采信的工程分析 | 需剔除的夸大或未核推断 |',
        '| :---: | :--- | :---: | :--- | :--- |'
    ]
    for d in docs:
        act = d.get('recommended_action') or ('降权参考' if '降权' in str(d.get('status','')) else '核验后吸收')
        accept = clean_item(d.get('accepted_points') or d.get('strengths') or d.get('source_summary') or '提供方向性综述视角')
        reject = clean_item(d.get('rejected_claims') or d.get('weaknesses') or d.get('boundary') or '二手汇总不直接计入原始样本分母')
        doc_lines.append(f"| **{d['id']}** | **{d['title']}**<br><small>{clean_item(d.get('source_summary',''))[:80]}</small> | `{act}` | {accept} | {reject} |")

    doc_lines += [
        '',
        '---',
        '',
        '## 二、外部调研提及项目（PRO01–PRO25）精读模块速查表',
        '',
        '> 完整优缺点对比与交互筛选请打开：[argon_项目比较与精读指南.html](argon_项目比较与精读指南.html)',
        '',
        '| 项目编号与名称 | 后端优先级 | Agent 优先级 | 核心精读模块路径 | 主要静态核查短板 |',
        '| :--- | :---: | :---: | :--- | :--- |'
    ]
    for p in comp.values():
        b_p = p['backend_priority']
        a_p = p['agent_priority']
        mods = (b_p.get('read_modules', []) if b_p['level'] != '非本方向' else []) + (a_p.get('read_modules', []) if a_p['level'] != '非本方向' else [])
        seen = []
        for m in mods:
            if m not in seen:
                seen.append(m)
        mod_str = '<br>'.join(f'`{m}`' for m in seen[:3]) or '见详情页'
        lim_str = clean_item(p.get('limitations', [''])[0])
        doc_lines.append(f"| **[{p['id']}](argon_项目比较与精读指南.html#{p['id']})**<br>{p['title']} | {b_p['level']} | {a_p['level']} | {mod_str} | {lim_str} |")
    doc_lines.append('')
    (rec_dir / 'argon_外部调研_文档判断与阅读模块.md').write_text('\n'.join(doc_lines) + '\n', encoding='utf-8')


def polish_detail_and_pending_html():
    """为 01_调研报告/argon_资料检索与证据详表.html 和 argon_待手动访问链接.html 注入统一顶栏，并折叠 7 轮历史更新日志。"""
    detail_path = REPORT / DETAIL
    if detail_path.exists():
        text = detail_path.read_text(encoding='utf-8')
        text = text.replace('。；', '；')
        # 注入顶栏样式与结构（幂等替换）
        topbar_css = (
            '.top-bar{position:sticky;top:0;z-index:30;background:#1b363acc;backdrop-filter:blur(8px);border-bottom:1px solid #2d4f54;color:#fff}'
            '.top-bar-inner{max-width:1440px;margin:auto;padding:10px 24px;display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}'
            '.top-brand{font-weight:700;font-size:14px;letter-spacing:.8px;color:#e4f2ef;white-space:nowrap}'
            '.top-links{display:flex;gap:6px 10px;flex-wrap:wrap;align-items:center}'
            '.top-links a{color:#d3e6e3;text-decoration:none;font-size:13px;padding:4px 9px;border-radius:4px}'
            '.top-links a:hover,.top-links a.active{background:#2c5855;color:#fff}'
            '.top-links a.pdf-pill{background:#a3482d;color:#fff;font-weight:600}'
            'details.history-rounds{margin:18px 0;padding:14px 18px;background:#f4f1ea;border:1px solid #d5d0c5;border-radius:8px}'
            'details.history-rounds>summary{cursor:pointer;font-weight:700;color:#1d5c59;font-size:15px}'
            '@media print{.top-bar,details.history-rounds{display:none!important}}'
        )
        if '.top-bar{' not in text:
            text = text.replace('</style>', topbar_css + '</style>', 1)
        topbar_el = top_nav_html(REPORT, 'detail')
        text = re.sub(r'<header class="top-bar screen-only">.*?</header>', '', text, flags=re.S)
        text = text.replace('<body>', '<body>' + topbar_el, 1)
        # 折叠 7 个历史批次更新区块（保留全部 section id 供锚点跳转与校验）
        if '<details class="history-rounds">' not in text and '<section id="external-merge">' in text and '<section id="coverage">' in text:
            text = text.replace(
                '<section id="external-merge">',
                '<details class="history-rounds"><summary>展开历轮专题补证与增量核读记录（7个历史过程批次，日常查表可跳过，直接看下方【资料覆盖与239条证据检索】）</summary><section id="external-merge">',
                1
            )
            text = text.replace(
                '<section id="coverage">',
                '</details><section id="coverage">',
                1
            )
        # 优化页头导航顺序：把高频查表入口放在前面
        old_nav_pattern = r'<nav><a href="#external-merge">.*?</nav>'
        new_nav = (
            '<nav>'
            '<a href="argon_实习求职调研总报告.html"><b>← 返回调研总报告</b></a>'
            '<a href="#coverage">01 资料覆盖总表</a>'
            '<a href="#catalog">02 239条证据检索器</a>'
            '<a href="#capabilities">03 11项能力×四类证据</a>'
            '<a href="#chains">04 34位候选人证据链</a>'
            '<a href="#projects">05 25项目375维矩阵</a>'
            '<a href="#routes">06 分方向阅读路线</a>'
            '<a href="#downloads">07 数据与附件索引</a>'
            '</nav>'
        )
        text = re.sub(old_nav_pattern, new_nav, text, count=1, flags=re.S)
        detail_path.write_text(text, encoding='utf-8')

    pending_path = REPORT / 'argon_待手动访问链接.html'
    if pending_path.exists():
        ptext = pending_path.read_text(encoding='utf-8').replace('。；', '；')
        topbar_css = (
            '.top-bar{position:sticky;top:0;z-index:30;background:#1b363acc;backdrop-filter:blur(8px);border-bottom:1px solid #2d4f54;color:#fff}'
            '.top-bar-inner{max-width:1280px;margin:auto;padding:10px 24px;display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}'
            '.top-brand{font-weight:700;font-size:14px;letter-spacing:.8px;color:#e4f2ef;white-space:nowrap}'
            '.top-links{display:flex;gap:6px 10px;flex-wrap:wrap;align-items:center}'
            '.top-links a{color:#d3e6e3;text-decoration:none;font-size:13px;padding:4px 9px;border-radius:4px}'
            '.top-links a:hover{background:#2c5855;color:#fff}'
            '.top-links a.pdf-pill{background:#a3482d;color:#fff;font-weight:600}'
        )
        if '.top-bar{' not in ptext:
            ptext = ptext.replace('</style>', topbar_css + '</style>', 1)
        ptext = re.sub(r'<header class="top-bar screen-only">.*?</header>', '', ptext, flags=re.S)
        ptext = ptext.replace('<body>', '<body>' + top_nav_html(REPORT, ''), 1)
        pending_path.write_text(ptext, encoding='utf-8')


def main():
    rows = load('all_evidence_records.json'); by = {r['id']: r for r in rows}
    stats = load('需求覆盖统计.json')
    jobs = load('argon_岗位统计_可读版.json')
    synthesis = load('面经项目_阅读结论.json')
    visuals = load('简历视觉材料_整理清单.json')
    comparison = load('项目统一比较与阅读优先级.json')['projects']; comp = {p['id']: p for p in comparison}
    assets = {}
    for asset in visuals['assets']:
        if asset.get('candidate_id') and asset.get('preview_files'):
            assets.setdefault(asset['candidate_id'], asset)

    def refs(ids, labels=None):
        return ' '.join(link(DETAIL+'#'+rid, (labels or {}).get(rid, rid)) for rid in ids if rid in by)

    def foot(text):
        return '<p class="page-foot">'+text+'</p>'

    # Page 1: 核心结论
    cover = '''<section class="report-page" id="conclusions"><div class="kicker">01 · 核心结论 · 大厂后端与 AGENT 工程实习调研</div>
<h1>技术广度要能串成系统，<br>项目亮点要经得起追问。</h1>
<p class="lead">本报告围绕大厂后端与 Agent 工程实习求职整理：先拆解 24 份可比工程 JD 的真实门槛，再用 34 位候选人履历、99 份面经和 25 个项目源码核对“应该学到多深、怎么表达贡献”。</p>
<div class="thesis"><strong>后端主线：</strong>真实请求链路、数据一致性、高并发容量与故障排障闭环。<br><strong>Agent 主线：</strong>任务状态编排、RAG 与工具约束、异常恢复、留出集回归评测。</div>
<div class="two"><div class="box"><h3>后端：先把一条请求链讲透</h3><p>语言并发、MySQL、Redis 和 MQ 不能只列名词。面试高分的关键是能结合具体业务解释：为什么这样选型、并发或宕机时哪里会不一致、压测瓶颈在哪里。</p></div><div class="box"><h3>Agent：要有可检查的执行与评测闭环</h3><p>只会调大模型 API 或套框架模板已不具区分度。面试重点追问：多步状态怎么持久化、工具失败怎么兜底回退、准确率与耗时怎么用数据集量化验证。</p></div></div>'''
    for no, title, text, ids in [
        ('01','广度通过“问题链”体现，而非组件堆砌','SQL、Redis、MQ、RPC 与 Agent 组件的价值，取决于你能否说明它们在具体业务中的职责边界、性能瓶颈和故障降级策略。',['CV01','CV33','INT85']),
        ('02','成功案例赢在“个人增量清晰”，而非仓库庞大','CV01 将字节实习通知服务与个人 IM 侧重分开；CV21 的班车项目被字节、京东连续追问下单补偿与幂等。清晰界定本人职责比照搬大型脚手架更有说服力。',['CV01','CV21','INT66']),
        ('03','SSP 案例适合借鉴“深度证据链”，而非迷信固定配方','公开 SSP 案例的共同点是“业务责任明确 + 核心机制扎实 + 能复盘失败与指标”，但项目题材各异，不存在一套照抄即拿 SSP 的固定技术栈。',['CV01','CV03','CV18']),
    ]:
        cover += '<div class="insight"><span class="number">'+no+'</span><div><h3>'+title+'</h3><p>'+text+'</p><div class="evidence">核心依据：'+refs(ids)+'</div></div></div>'
    cover += '''<div class="rule"></div><div class="reading"><strong>第 1 步（10分钟）</strong><span>读第 2 页【岗位要求对比】与第 3–4 页【面试高频追问】，分清硬门槛与职责项，确定复习优先级。</span></div><div class="reading"><strong>第 2 步（精读）</strong><span>看第 5 页【真实履历附件】，再按第 6–7 页【项目取舍表】精读核心源码模块，避开常见工程短板。</span></div><div class="reading"><strong>第 3 步（查核）</strong><span>第 8 页汇总 SSP 证据与工业界评测标准；需要查单条 JD、面经或源码时再打开专题页与检索表。</span></div>'''
    cover += foot('样本基数：239 条已核公开记录（33 条 JD、34 份候选人案例、99 份面经、18 份专业观点、25 个代码项目）。所有项目均基于固定源码静态审阅。')+'</section>'

    # Page 2: 岗位要求统计（消除重复机械的“只统计明确要求层”，改为具体分层数据与实战解读）
    groups = jobs['groups']
    topic_keys = ['lang','cs','db','cache','mq','distributed','agent','rag','tools','evaluation']
    labels = {
        'lang':'编程语言',
        'cs':'算法 / OS / 网络',
        'db':'数据库 / 存储',
        'cache':'缓存 (含 Redis)',
        'mq':'消息队列',
        'distributed':'分布式 / 高可用',
        'agent':'Agent / 框架',
        'rag':'RAG / 检索',
        'tools':'工具调用 / MCP',
        'evaluation':'评测 / 效果指标'
    }
    topic_guidance = {
        'lang': '两方向均必考；多为 Go/Java/Python/C++ 择一，重点考并发模型与内存机制而非多语言罗列',
        'cs': '数据结构算法、OS 与网络是共同硬门槛；Agent 岗同样会在一面考察现场手撕代码与网络协议',
        'db': '后端 7/10 明确要求（另 2 份单列了解 MySQL）；常追问索引失效、事务隔离与深分页优化',
        'cache': '后端 6/10 明确要求（精确点名 Redis 占 4 份）；必考缓存穿透/击穿、双写一致性与锁边界',
        'mq': '后端 4/10 明确要求、混合 1/3 优先；重点准备异步解耦、重复消费幂等、延迟队列与死信补偿',
        'distributed': '除明确要求外，后端 3 份优先 + 4 份职责提及；实习生重在理解限流、降级与多实例竞争窗口',
        'agent': 'Agent 岗 10/11 明确要求（后端/混合多列为职责或优先）；需讲清状态机编排原理而非仅调 API',
        'rag': 'Agent 岗 6/11 明确要求（含择一）、3/11 列为职责；常考分块策略、混合召回重排与幻觉溯源',
        'tools': 'Agent 岗 6/11 明确要求、5/11 列为职责；重点考察 Function Call/MCP 协议约束、鉴权与失败回退',
        'evaluation': '明确要求仅 1 份，但 Agent 优先(2)与职责(5)高频出现；有无留出集与回归评测是核心加分项',
    }
    job_page = '<section class="report-page" id="jobs"><div class="kicker">02 · 岗位要求对比</div><h2>先分清岗位方向与要求层级，再决定技术广度。</h2><p class="lead">33 条 JD 线索中，24 份工程岗位全文可比：后端 10 份、Agent 工程 11 份、混合 3 份（另 9 份算法研究或摘要受限材料单列排除）。阅读 JD 时务必区分<b>明确要求</b>、<b>优先加分</b>与<b>入职后工作职责</b>。</p><div class="two"><div class="box"><h3>后端开发（10 份可比全文）</h3><p>以一门主力服务端语言 + 计算机基础 + 数据库/缓存为共同底座。Redis、MQ 与分布式高可用按岗位梯度出现，重在考察完整链路一致性与排障深度。</p></div><div class="box"><h3>Agent 工程（11 份可比全文）</h3><p>在服务端编程基础上，明确要求 LLM/Agent 认知、RAG 检索与工具调用；而多 Agent 记忆状态机、自动化评测与沙箱隔离更多出现在<b>优先项或工作职责</b>中。</p></div></div><h3>核心技术主题出现频次：明确要求数（附优先/职责分层提示）</h3><div class="scroll"><table><thead><tr><th>技术主题</th><th>后端 / 10</th><th>Agent / 11</th><th>混合 / 3</th><th>分层结构与备考解读</th></tr></thead><tbody>'
    for key in topic_keys:
        values = [groups[t]['features'].get(key) for t in ['后端','Agent工程','混合']]
        if not any(values):
            continue
        cells = []
        for v in values:
            if not v:
                cells.append('<td class="num">0</td>')
                continue
            req = v.get('required_any_count', 0)
            opt = v.get('required_option_count', 0)
            pref = v.get('preferred_count', 0)
            duty = v.get('duties_count', 0)
            sub_parts = []
            if opt:
                sub_parts.append(f'含择一{opt}')
            if pref:
                sub_parts.append(f'优{pref}')
            if duty:
                sub_parts.append(f'职{duty}')
            sub_html = f' <span class="small">({"·".join(sub_parts)})</span>' if sub_parts else ''
            cells.append(f'<td class="num">{req}{sub_html}</td>')
        job_page += '<tr><td><strong>'+labels[key]+'</strong></td>'+''.join(cells)+'<td>'+E(topic_guidance[key])+'</td></tr>'
    job_page += '</tbody></table></div><p class="note"><b>读表说明：</b>大号数字为<b>明确要求提及数</b>（括号内“含择一”代表多项技术任选其一，“优”代表优先/加分，“职”代表工作职责）。例如 JD08 将记忆、鉴权和观测列在职责；JD11 将 MQ、Agent/RAG/MCP 列为优先项。混合组 3 条均来自百度，不外推为全行业通用赛道。</p>'
    job_page += '<h3>对求职准备顺序的实际影响</h3><p><strong>投递后端：</strong>优先打磨一条涵盖 MySQL 索引与事务、Redis 缓存一致性、MQ 异步解耦与幂等补偿的闭环项目，再按 Java / Go / C++ 岗位补充运行时与网络排障细节。</p><p><strong>投递 Agent 工程：</strong>保持服务端工程与数据结构功底，将核心精力投入任务编排、检索召回质量、工具调用约束、异常恢复与评测基准，不必把算法研究岗的预训练/RL 当成应用工程硬门槛。</p>'
    job_page += foot(link('../02_招聘岗位资料/argon_岗位要求统计与解读.html','查看完整岗位统计：五层编码表、SVG图表与公司去重敏感性')+' · 代表性 JD：'+refs(['JD08','JD11','JD20','JD23','JD26','JD27']))+'</section>'

    # Pages 3 & 4: 后端面试与 Agent 面试（消除 。； 双标点，结构更清晰）
    def findings_page(direction, anchor, title, introduction):
        out = '<section class="report-page" id="'+anchor+'"><div class="kicker">'+('03 · 后端面试高频追问' if direction=='backend' else '04 · AGENT面试高频追问')+'</div><h2>'+title+'</h2><p class="lead">'+introduction+'</p>'
        for index, finding in enumerate(synthesis[direction+'_findings'], 1):
            questions = [(source, clean_item(q)) for source in finding.get('sources', []) for q in source.get('source_questions', []) if clean_item(q)]
            if questions:
                q_str = '；'.join(f'{q}（{s["id"]}）' for s, q in questions[:2]) + '。'
            else:
                q_str = join_clean(finding.get('question_clusters', [])[:1])
            depth = join_clean(finding.get('preparation_depth', [])[:2])
            source_ids = [s.get('id',s.get('interview_id',s.get('source_id',''))) for s in finding.get('sources',[])]
            out += (
                '<div class="qa-block"><h3><span class="number">'+str(index).zfill(2)+'</span>'+E(finding['title'])+'</h3>'
                '<p>'+E(finding.get('conclusion',''))+'</p>'
                '<p class="question">典型追问：'+E(q_str)+'</p>'
                '<p><strong>准备标准：</strong>'+E(depth)+'</p>'
                '<div class="evidence">面经来源：'+refs(source_ids)+' · 对照项目：'+refs(finding.get('project_ids',[]))+'</div></div>'
            )
        out += '<p class="note">注：典型追问提炼自候选人面后回忆，准备标准为本报告基于考察意图归纳的自查深度。各轮次原问、面试时间与完整上下文详见面经专题页。</p>'
        out += foot(link('../04_面经与专业观点/argon_面经重点与项目追问.html','打开面经专题：查看全部追问簇、年份标注与项目源码映射')+' · 99 份面经含 14 份严格近期工程实习与 1 份 AI Infra 对照。')+'</section>'
        return out

    backend_page = findings_page('backend','backend','后端面试要准备的是“解释链”，<br>而不是组件名词清单。','面试官会将你的项目职责、底层原理和极端故障串起来追问。以下五类高频问题都应落到你写过的具体代码或排查过程上。')
    agent_page = findings_page('agent','agent','Agent 项目要回答“为什么有效，<br>以及失败时会发生什么”。','考察重心已从“调通大模型接口”转向任务执行全链路：检索质量、工具边界、中断恢复与定量评测缺一不可。')

    # Page 5: 真实履历对标
    def candidate_card(rid, name, label, learn, boundary):
        asset = assets.get(rid)
        preview = ''
        if asset:
            image = asset.get('thumbnail_file') or (asset.get('preview_files') or [''])[0]
            if image:
                preview = '<a href="'+E(rel(asset['local_file']))+'"><img loading="lazy" src="'+E(rel(image))+'" alt="'+E(name+'公开履历专业模块预览')+'"></a>'
        return '<article class="candidate-preview">'+preview+'<span class="pill core">'+label+'</span><h3>'+name+'</h3><p><strong>可借鉴写法：</strong>'+learn+'</p><p class="small"><strong>样本背景与边界：</strong>'+boundary+'</p><div class="evidence">'+refs([rid])+' · '+link('../03_简历与候选人案例/argon_候选人与简历图册.html#'+rid,'打开简历图册与脱敏附件')+'</div></article>'

    candidate_page = '<section class="report-page" id="candidates"><div class="kicker">05 · 真实履历对标</div><h2>先看真实简历怎么组织专业模块，<br>再看这份经历能证明什么。</h2><p class="lead">本调研包优先展示已获取的公开脱敏 PDF、PNG 简历片段与完整网页履历（共 7 位核心候选人 + 4 份视觉对照），其余 27 位以经历/面经文章归档，绝不用纯文本卡片伪造简历图片。</p><div class="two">'
    candidate_page += candidate_card('CV30','Andrew Wang：字节后端 / Agent 实习履历','公开PDF · 脱敏专业模块','清晰呈现 Go 服务端基础与 Creator Assistant Agent 实习职责（MCP 工具接入、真实对话评测与 Trace 埋点），适合学习如何量化表达大厂内部工程贡献。','2025–2026 实习履历（美本背景）；未披露国内校招 SSP 档位或内部闭源仓库。')
    candidate_page += candidate_card('CV31','黄一航：Agent 实习与本人开源项目直连','公开PDF · 脱敏专业模块','实习年月与技术职责明确，且简历直接链接本人多 Agent 仓库（Sprout / NoWorries），适合对照“简历亮点描述”与“实际代码实现”的对应关系。','产业企业 Agent 实习（非互联网大厂 SSP）；项目基于开源框架演进，静态审阅可见沙箱隔离短板。')
    candidate_page += '</div><h3>其他代表性履历材料的阅读侧重</h3><div class="scroll"><table><thead><tr><th>候选人案例</th><th>最值得学习的写法与结构</th><th>阅读时需注意的样本边界</th></tr></thead><tbody>'
    for name, text, boundary, ids in [
        ('CV01 · 字节后端 SSP 与简历片段','实习通知服务（重业务责任、幂等去重、告警排障）与个人 IM 项目（重网络协议与性能机制）形成互补。','仅公开实习简历截图片段与面经复盘；SSP 档位与性能指标为本人自述。',['CV01']),
        ('CV28 · 后端完整网页履历 (DavidHLP)','网页履历直接链接本人 UltiCode（在线判题）与 ResiCache（并发缓存）仓库，职责与代码可一并核验。','实习雇主为博彦科技（服务阿里云项目），非阿里直签校招 SSP。',['CV28']),
        ('CV33 · 2026 后端 + RAG 求职经历','展示同一求职周期内如何同时应对传统 Java/Go 后端追问与 RAG 检索流水线追问，体现复合竞争力。','为求职经历与面经复盘文章，无独立 PDF 简历附件；不同公司面试结果已分别标注。',['CV33']),
        ('OBS11 · 一页式后端公开简历图（对照）','个人网盘（分片上传/断点续传/延时任务）与轻量 RPC（Netty/容错/请求备份）一业务一轮子搭配清晰。','作者已将内部实习模块打码且未披露录用结果，仅作一页式版面与项目分工参考。',['OBS11']),
    ]:
        candidate_page += '<tr><td><strong>'+E(name)+'</strong>'+refs(ids)+'</td><td>'+E(text)+'</td><td>'+E(boundary)+'</td></tr>'
    candidate_page += '</tbody></table></div>'+foot(link('../03_简历与候选人案例/argon_候选人与简历图册.html','打开候选人与简历图册：浏览全部 34 位候选人案例与 4 份视觉对照附件'))+'</section>'

    # Pages 6 & 7: 后端项目取舍 & Agent项目取舍
    selected = synthesis['projects']
    selected_by = {p['id']: p for p in selected}
    short_projects = {
        'PRO19': ('CV21 本人面经直连项目（字节/京东追问）','学习预约、支付、取消与 MQ 补偿如何串成业务闭环，并结合面经真题对照源码中的状态流转。','v1 补偿消息发送失败仅打印日志；取消消费“先查标记→执行业务→再写标记”存在并发窗口。'),
        'PRO20': ('CV28 完整网页履历直连本人仓库','学习“提交→Outbox表→Redis投递→租约抢占→结果竞争”的状态机设计与异步消息可靠性权衡。','DB 本地事务未覆盖 Redis 投递；死信重投与幂等闭环仍待补齐；当前仓库提交晚于实习期。'),
        'PRO21': ('CV28 完整网页履历直连本人仓库','学习 CompletableFuture 单飞（Single-Flight）共享回源、异常清理与 CAS 更新 TTL 的并发缓存实现。','进程内 ConcurrentHashMap 选 Leader 仅防单机并发回源，不等同于跨节点分布式互斥锁。'),
        'PRO09': ('CV05 本人 2022 合并 PR（开源网关贡献）','先读本人提交的 OAuth2 与 logging-rocketmq 集成测试 PR，再看网关插件链与响应式生命周期设计。','仅借鉴如何通过可验证 PR 切入大型开源项目；切勿把整个 ShenYu 网关或后续新特性包装成个人原创。'),
        'PRO04': ('生产级工程框架参照（Java / Graph）','学习 Java 生态下 Workflow/Agent 状态图编排、Checkpoint 持久化接口与工具人工确认钩子的分层设计。','检查点持久化不等于外部副作用自动回滚；人工确认钩子不能替代服务端硬权限校验。'),
        'PRO06': ('深度研究与评测参照（LangGraph）','先看评测脚本如何定义留出集、基线与成对比较，再回看 Supervisor 研究协调、工具调用与上下文压缩。','LLM-as-a-Judge 裁判受位置与长度偏见影响；缺少同 Token 预算下的尾延迟与外部写操作恢复验证。'),
        'PRO24': ('CV31 主页直连本人多 Agent 项目','学习树形任务递归拆解、并发 Worker 调度、Straggler 拖慢检测与动态重拆机制。','基准评测用正则匹配代替代码真实执行；Token 消耗为事后累加而非调用前硬预算熔断；无持久化检查点。'),
        'PRO25': ('CV31 简历直列本人桌面 Agent 项目','学习情景记忆检索、桌面动作执行器抽象，以及 Windows / Linux / macOS 跨平台权限边界处理。','修改 HOME/TMPDIR 环境变量不等于操作系统级沙箱隔离；macOS 降级回退分支存在重复执行风险。'),
    }

    def projects_page(ids, anchor, title, lead, direction):
        out = '<section class="report-page" id="'+anchor+'"><div class="kicker">'+('06 · 后端代表项目取舍' if direction=='backend' else '07 · AGENT代表项目取舍')+'</div><h2>'+title+'</h2><p class="lead">'+lead+'</p><div class="scroll"><table class="project-table"><thead><tr><th>项目与候选人关联</th><th>核心机制（拿来学什么）</th><th>静态核查短板（切勿照搬什么）</th><th>精读代码入口</th></tr></thead><tbody>'
        for rid in ids:
            p = comp[rid]; s = selected_by[rid]; priority = p[direction+'_priority']
            modules = s.get('modules', priority['read_modules'])
            module_links = []
            if isinstance(modules, list):
                for m in modules[:2]:
                    if isinstance(m, dict):
                        module_links.append(link(m.get('url',p['source_URL']), m.get('name') or Path(m.get('path','代码入口')).name))
                    else:
                        module_links.append(E(m))
            else:
                module_links.append(E(modules))
            identity, takeaway, limitation = short_projects[rid]
            out += '<tr><td><strong>'+E(s.get('name',p['title']))+'</strong>'+refs([rid])+'<p class="small">'+E(identity)+'</p></td><td>'+E(takeaway)+'</td><td>'+E(limitation)+'</td><td class="module">'+'<br>'.join(module_links)+'<p>'+link(p['source_URL'],'固定源码 / 仓库 ↗')+'</p></td></tr>'
        out += '</tbody></table></div>'
        if direction == 'backend':
            out += '<h3>后端项目精读顺序建议</h3><p>① 先读 <b>SchoolBus (PRO19)</b>，体会字节、京东面试官如何从普通预约业务深挖并发与补偿漏洞；② 再读 <b>UltiCode (PRO20)</b> 与 <b>ResiCache (PRO21)</b>，掌握状态流转、Outbox 消息投递与 Single-Flight 并发控制的代码写法；③ 有志于开源贡献的同学可参考 <b>ShenYu (PRO09)</b>，看如何用高覆盖率集成测试切入成熟项目。</p><p class="note">排序原则：优先推荐“有候选人本人归属或真实面经追问、能清晰定位个人工程增量与失败边界”的项目，不按 GitHub Star 数或商业课程宣传包装排序。</p>'
        else:
            out += '<h3>如何让 Agent 项目超越“简单 API 套壳”</h3><p>面试官眼中合格的 Agent 工程项目至少需具备三项代码证据：① <b>可追踪的状态流转与恢复机制</b>（参考 <b>PRO04</b> 的 Checkpoint 与状态图）；② <b>可复现的评测基准与回归脚本</b>（参考 <b>PRO06</b> 的评测器，同时避免 <b>PRO24</b> 正则打分的局限）；③ <b>严格的工具副作用控制与权限隔离</b>（对照 <b>PRO25</b> 的执行器边界）。</p><p class="note">以上对比基于固定版本源码静态审阅，旨在帮助你提炼架构设计与识别常见工程缺陷，切勿直接复制仓库代码充当个人项目。</p>'
        out += foot(link('../06_项目分析与推荐/argon_项目比较与精读指南.html','打开 25 个项目精读指南：按优先级筛选、查看完整优缺点与本地源码包'))+'</section>'
        return out

    backend_projects = projects_page(['PRO19','PRO20','PRO21','PRO09'],'backend-projects','后端项目：精读状态流转与并发机制，<br>切勿整仓照搬。','以下四个项目分别代表“真实面经直连业务”、“异步状态机”、“并发缓存组件”与“开源网关测试贡献”四类切入方式。','backend')
    agent_projects = projects_page(['PRO04','PRO06','PRO24','PRO25'],'agent-projects','Agent 项目：吸收编排与评测长处，<br>看清隔离与恢复边界。','以下四个项目分别提供“生产级状态图框架”、“自动化评测闭环”、“动态任务树拆解”与“桌面动作执行边界”的代码范例。','agent')

    # Page 8: SSP与工业界观点
    last = '<section class="report-page" id="ssp"><div class="kicker">08 · SSP案例与工业界标准</div><h2>冲击高档位录用（SSP）靠什么证据支撑？</h2><p class="lead">本包收录的 16 份含 SSP 自述案例（其中 11 份公司明确）表明：高档位录用依赖<b>可验证的实习业务责任、扎实的底层机制理解与清晰的失败复盘</b>，而非某套固定技术名词。</p><div class="scroll"><table><thead><tr><th>代表性 SSP 案例</th><th>值得吸收的竞争力要素</th><th>阅读时应避免的归因误区</th></tr></thead><tbody>'
    for label, yes, no, ids in [
        ('CV01 · 2025 字节后端 SSP 自述','将实习中的通知服务（重试去重、慢 SQL 索引、线上排障）与个人 IM 项目（网络协议、消息可靠投递）结合，业务与底层互补。','不能倒推“只要做了 IM 或用了 RocketMQ 就必拿 SSP”；其自报性能指标需结合压测条件理解。',['CV01']),
        ('CV03 · 2025 美团实习转正及多厂 SSP','展现“早期项目练手 → 大厂实习承接核心模块 → 秋招把实习产出讲透”的连续进阶时间线。','帖子标题概括了多段经历，需按正文区分实习转正与秋招不同公司的具体录用档位。',['CV03']),
        ('CV18 · 历史 C++/Go 后端 SP/SSP','业务开发、网络底层机制、语言互操作与效能工具各有侧重，且均关联本人可查代码仓库。','2019 年历史案例重在印证“工程深度与代码实证”的长期价值，不可将其技术栈直接等同于 2026 Agent 门槛。',['CV18']),
    ]:
        last += '<tr><td><strong>'+label+'</strong>'+refs(ids)+'</td><td>'+yes+'</td><td>'+no+'</td></tr>'
    last += '</tbody></table></div><h3>把工业界技术团队的方法论变成项目自检表</h3><div class="scroll"><table><thead><tr><th>工业界专业观点</th><th>如何用于打磨与自检你的项目</th><th>来源性质与阅读说明</th></tr></thead><tbody>'
    for label, use, scope, ids in [
        ('工具设计与任务级评测 (Anthropic)','围绕真实任务边界合并精简工具 Schema；建立留出集验证任务成功率，同时监控工具调用次数、Token 与错误率。','Anthropic 官博工程实践全文（OP09）；聚焦工具工程与评测方法。',['OP09']),
        ('生产反馈与逐题回归分析 (百度 Comate)','不要只报一个笼统的总准确率；需记录单题退化、工具调用失败、自愈重试与成本分布，能讲清 Bad Case 归因。','百度 Comate 架构师公开演讲实录（OP16）；适合指导评测闭环设计。',['OP16']),
        ('项目差异化定位与完整交付证据','用“个人职责 + 业务约束 + 改造前后实测对比”替代空泛套话；需求分析、接口设计、单测与排障日志都应留有证据。','工业界技术专栏选读（OP17、OP18）；作为简历表达与工程规范自查参考。',['OP17','OP18']),
    ]:
        last += '<tr><td><strong>'+label+'</strong>'+refs(ids)+'</td><td>'+use+'</td><td>'+scope+'</td></tr>'
    last += '</tbody></table></div><p class="note"><b>样本全貌：</b>目前公开渠道中“明确 2025–2026 Agent 专岗 + 正式 SSP 档位 + 本人源码 + 本人面经”四合一的完整样本依然稀缺，报告已将正式 Offer、OC、意向书与面经复盘严格分列，助你客观评估竞争态势。</p><h3>专题深读导航</h3><div class="bottom-links">'+link('../argon_00_开始阅读.html','00 开始阅读导航')+link('../02_招聘岗位资料/argon_岗位要求统计与解读.html','02 岗位要求统计')+link('../03_简历与候选人案例/argon_候选人与简历图册.html','03 候选人简历图册')+link('../04_面经与专业观点/argon_面经重点与项目追问.html','04 面经与项目追问')+link('../06_项目分析与推荐/argon_项目比较与精读指南.html','05 25项目精读指南')+link(DETAIL,'06 全部239条证据检索')+link('argon_待手动访问链接.html','受限原始链接清单')+'</div>'
    last += foot('调研报告完 · 统计覆盖：33 条 JD 线索、34 份候选人资料、99 份面经、18 份专业观点、25 个项目。历史过程文档已收入归档目录。')+'</section>'

    body = cover + job_page + backend_page + agent_page + candidate_page + backend_projects + agent_projects + last
    html = shell(TITLE, body, True, REPORT, 'report')
    REPORT.mkdir(exist_ok=True)
    (REPORT / (TITLE+'.html')).write_text(html, encoding='utf-8')
    (REPORT / 'argon_index.html').write_text(html, encoding='utf-8')

    # 生成 04_面经与专业观点/argon_面经重点与项目追问.html 与 .md
    build_interview_pages(synthesis, by, comp)
    # 生成 06_项目分析与推荐/ 下的 5 份可读 Markdown 指南，并优化 01_调研报告/ 详表与受限链接页
    build_project_and_reading_mds(by, comp, visuals)
    polish_detail_and_pending_html()

    # 生成 06_项目分析与推荐/argon_项目比较与精读指南.html（按优先级分层排序、去除无意义的“非本方向”半卡占位、左右分栏展示长处与短板）
    core_order = ['PRO19', 'PRO20', 'PRO21', 'PRO09', 'PRO04', 'PRO06', 'PRO24', 'PRO25']
    def proj_sort_key(p):
        pid = p['id']
        if pid in core_order:
            return (0, core_order.index(pid))
        b_lvl = p['backend_priority']['level']
        a_lvl = p['agent_priority']['level']
        if '精读' in (b_lvl, a_lvl):
            return (1, int(pid[3:]))
        if '选读' in (b_lvl, a_lvl):
            return (2, int(pid[3:]))
        return (3, int(pid[3:]))

    sorted_projects = sorted(comparison, key=proj_sort_key)

    project_body = (
        '<section class="report-page">'
        '<div class="kicker">25个代码项目静态审阅 · 按精读优先级与技术方向组织</div>'
        '<h1>项目比较与精读指南</h1>'
        '<p class="lead">本页汇总全部 25 个项目的架构长处、静态核查短板、候选人本人归属证据与推荐精读代码模块。项目已按<b>核心精读（8项）→ 专项选读 → 降权/待核参考</b>排序，方便你直接从高价值源码读起。</p>'
        '<div class="catalog-controls">'
        '<input id="project-query" type="search" placeholder="搜索项目名、编号(如PRO19)、技术栈、模块或候选人(如CV28)...">'
        '<select id="project-track" aria-label="方向筛选">'
        '<option value="">全部方向 (25)</option>'
        '<option value="backend">后端推荐项目</option>'
        '<option value="agent">Agent 推荐项目</option>'
        '<option value="core">仅看【精读】级项目</option>'
        '<option value="candidate">仅看【候选人本人关联】项目</option>'
        '</select>'
        '<span class="pill core" id="project-shown">显示 25 / 25</span>'
        '</div>'
    )

    for p in sorted_projects:
        pid = p['id']
        rp = next((s for s in selected if s['id'] == pid), {})
        b_prio = p['backend_priority']
        a_prio = p['agent_priority']
        is_core = (pid in core_order) or ('精读' in (b_prio['level'], a_prio['level']))
        has_candidate = bool(p.get('linked_candidates'))
        search = json.dumps(p, ensure_ascii=False).lower()

        badges = []
        if b_prio['level'] != '非本方向':
            b_cls = 'core' if b_prio['level'] == '精读' else ('select' if b_prio['level'] == '选读' else 'warn')
            badges.append(f'<span class="pill {b_cls}">后端 · {E(b_prio["level"])}</span>')
        if a_prio['level'] != '非本方向':
            a_cls = 'core' if a_prio['level'] == '精读' else ('select' if a_prio['level'] == '选读' else 'warn')
            badges.append(f'<span class="pill {a_cls}">Agent · {E(a_prio["level"])}</span>')
        if has_candidate:
            c_list = ' / '.join(c['candidate_id'] for c in p.get('linked_candidates', []))
            badges.append(f'<span class="pill warn">候选人关联：{E(c_list)}</span>')
        else:
            badges.append('<span class="pill">工程/教学参照</span>')

        archive = p.get('attachment', {}).get('archive_file')
        arch_html = ''
        if archive:
            candidates_zip = list((ROOT / '05_项目源码归档').rglob(Path(archive).name))
            if candidates_zip:
                arch_html = ' · ' + link(rel(candidates_zip[0].relative_to(ROOT), ROOT / '06_项目分析与推荐'), '下载本地源码包') + f' <span class="small">({E(p["attachment"].get("status","本地归档"))})</span>'

        card_cls = 'project-card tier-core' if is_core else 'project-card'
        project_body += (
            f'<article class="{card_cls}" data-search="{E(search)}" '
            f'data-backend="{"yes" if b_prio["level"]!="非本方向" else "no"}" '
            f'data-agent="{"yes" if a_prio["level"]!="非本方向" else "no"}" '
            f'data-core="{"yes" if is_core else "no"}" '
            f'data-candidate="{"yes" if has_candidate else "no"}" id="{E(pid)}">'
            f'<div>{"".join(badges)}</div>'
            f'<h2>{E(pid)} · {E(p["title"])}</h2>'
            f'<p class="small">{link(p["source_URL"], "原仓库 / 固定源码 ↗")} · {link("../01_调研报告/"+DETAIL+"#"+pid, "375维详细证据卡")}{arch_html}</p>'
        )

        # 只展示有效方向的精读指引（不浪费版面渲染“非本方向”空盒子）
        active_dirs = [(d, lbl, p[d+'_priority']) for d, lbl in [('backend','后端方向'),('agent','Agent 方向')] if p[d+'_priority']['level'] != '非本方向']
        if not active_dirs:
            active_dirs = [('backend','后端方向', b_prio), ('agent','Agent 方向', a_prio)]
        dir_grid_cls = 'two' if len(active_dirs) > 1 else ''
        if dir_grid_cls:
            project_body += f'<div class="{dir_grid_cls}">'
        for _, lbl, q in active_dirs:
            mods_html = '<ul class="compact-list module">' + ''.join(f'<li>{E(m)}</li>' for m in q.get('read_modules', [])) + '</ul>' if q.get('read_modules') else ''
            project_body += (
                f'<div class="box" style="margin-bottom:12px"><h3>{lbl}阅读建议（{E(q["level"])}）</h3>'
                f'<p>{E(q["reason"])}</p>'
                f'<p class="small" style="margin-bottom:4px"><b>重点精读模块 / 路径：</b></p>{mods_html}</div>'
            )
        if dir_grid_cls:
            project_body += '</div>'

        # 左右分栏展示：核心长处 vs 实现短板
        project_body += (
            '<div class="two">'
            '<div class="box"><h3>值得借鉴的机制（长处）</h3>' + bullet_html(p.get('strengths', [])) + '</div>'
            '<div class="box warn-box"><h3>静态核查短板与勿照搬项（局限）</h3>' + bullet_html(p.get('limitations', [])) + '</div>'
            '</div>'
        )
        own_str = ownership_text(rp.get('ownership', p.get('source_nature_boundary', p['evidence_completeness'])))
        out_str = clean_item(rp.get('outcome_boundary', ''))
        project_body += f'<p class="note"><strong>归属与证据边界：</strong>{E(own_str)}' + (f'；{E(out_str)}。' if out_str else '') + '</p></article>'

    project_body += (
        '<p class="page-foot">'
        + link('../01_调研报告/' + TITLE + '.html', '返回调研总报告') + ' · '
        + link('argon_后端实习阅读顺序.md', '后端实习阅读顺序 (MD)') + ' · '
        + link('argon_Agent实习阅读顺序.md', 'Agent实习阅读顺序 (MD)') + ' · '
        + link('argon_专业观点交叉核对_评测与工具恢复.md', '评测与工具恢复交叉核对 (MD)')
        + '</p></section>'
        '<script>(()=>{'
        'const rows=[...document.querySelectorAll(".project-card")],q=document.getElementById("project-query"),t=document.getElementById("project-track");'
        'function run(){let n=0;const s=q.value.trim().toLowerCase(),v=t.value;'
        'for(const r of rows){'
        'const matchQ=!s||r.dataset.search.includes(s);'
        'const matchT=!v||(v==="backend"&&r.dataset.backend==="yes")||(v==="agent"&&r.dataset.agent==="yes")||(v==="core"&&r.dataset.core==="yes")||(v==="candidate"&&r.dataset.candidate==="yes");'
        'r.hidden=!(matchQ&&matchT);if(!r.hidden)n++;}'
        'document.getElementById("project-shown").textContent="显示 "+n+" / "+rows.length;}'
        'q.addEventListener("input",run);t.addEventListener("change",run);})();</script>'
    )
    (ROOT / '06_项目分析与推荐/argon_项目比较与精读指南.html').write_text(
        shell('项目比较与精读指南', project_body, False, ROOT / '06_项目分析与推荐', 'projects'),
        encoding='utf-8'
    )

    # 生成 argon_00_开始阅读.html（带3分钟全局结论速览 + 3步阅读路线 + 6大专题入口）
    guide = '''<section class="report-page"><div class="kicker">START HERE · 阅读总导航与核心结论速览</div>
<h1>大厂后端与 Agent 工程实习求职调研</h1>
<p class="lead">本文件夹汇集了 <b>239 条</b>经过交叉核验的公开求职证据（33 条 JD 线索、34 位候选人案例、99 份面经、18 份工业界观点、25 个代码项目）。你无需按历史采集轮次翻阅，只需按以下三步即可快速掌握核心结论与代码精读抓手。</p>
<div class="thesis"><strong>一句话抓核心：</strong><br>• <b>后端实习</b>：不靠罗列中间件数量，靠把一条真实业务链路（数据库索引/事务 → Redis 缓存并发 → MQ 幂等补偿 → 压测与故障排查）讲深讲透。<br>• <b>Agent 工程实习</b>：不靠简单调 API 或堆砌多 Agent 名词，靠展示<b>可控状态图编排、RAG 召回重排、工具 Schema 约束与失败恢复、以及留出集回归评测</b>。</div>

<h2>一、3 分钟核心数据与备考速览</h2>
<div class="scroll"><table><thead><tr><th>维度</th><th>后端开发方向</th><th>Agent 工程方向</th><th>关键备考抓手</th></tr></thead><tbody>
<tr><td><strong>岗位门槛<br>(24份可比工程JD)</strong></td><td>编程语言(10/10)、CS基础(8/10)、数据库(7/10)、缓存/Redis(6/10)、消息队列(4/10)</td><td>编程语言(11/11)、Agent框架认知(10/11)、RAG检索(6/11)、工具/MCP(6/11)；评测与状态恢复多在职责(5/11)</td><td>区分 JD 中的“硬门槛”与“加分/职责项”；混合岗(3份)均来自百度，以服务端底座接 AI 网关/检索。</td></tr>
<tr><td><strong>高频面试追问<br>(99份面经提炼)</strong></td><td>① 本人负责边界与选型代价<br>② SQL 索引与缓存并发回源边界<br>③ 异步补偿、幂等窗口与线上排障</td><td>① 为何用多步/多Agent而非单次调用<br>② 混合召回重排与工具参数校验<br>③ 中断恢复、写操作沙箱与回归评测集</td><td>所有追问都会落回“如果并发冲突/外部调用超时/模型输出越界会发生什么”，背诵概念无法过关。</td></tr>
<tr><td><strong>标杆履历与项目<br>(优先精读入口)</strong></td><td>• 履历：<a href="03_简历与候选人案例/argon_候选人与简历图册.html#CV01">CV01</a>、<a href="03_简历与候选人案例/argon_候选人与简历图册.html#CV28">CV28</a><br>• 项目：<a href="06_项目分析与推荐/argon_项目比较与精读指南.html#PRO19">PRO19 SchoolBus</a>、<a href="06_项目分析与推荐/argon_项目比较与精读指南.html#PRO20">PRO20 UltiCode</a>、<a href="06_项目分析与推荐/argon_项目比较与精读指南.html#PRO21">PRO21 ResiCache</a>、<a href="06_项目分析与推荐/argon_项目比较与精读指南.html#PRO09">PRO09 ShenYu</a></td><td>• 履历：<a href="03_简历与候选人案例/argon_候选人与简历图册.html#CV30">CV30</a>、<a href="03_简历与候选人案例/argon_候选人与简历图册.html#CV31">CV31</a><br>• 项目：<a href="06_项目分析与推荐/argon_项目比较与精读指南.html#PRO04">PRO04 Spring AI Alibaba</a>、<a href="06_项目分析与推荐/argon_项目比较与精读指南.html#PRO06">PRO06 open_deep_research</a>、<a href="06_项目分析与推荐/argon_项目比较与精读指南.html#PRO24">PRO24 Sprout</a>、<a href="06_项目分析与推荐/argon_项目比较与精读指南.html#PRO25">PRO25 NoWorries</a></td><td>精读代码时重点看“状态流转 + 异常处理 + 测试/评测”，同时避开各项目静态核查出的并发或隔离短板。</td></tr>
</tbody></table></div>

<h2>二、六大专题阅读入口（按需点击进入）</h2>
<div class="two">'''
    for href, title, badge, desc in [
        ('01_调研报告/'+TITLE+'.html','01 · 实习求职调研总报告','必读主报告 · 配 8 页 PDF','串联岗位要求 → 后端/Agent 面试追问 → 真实简历对标 → 8 个重点项目取舍 → SSP 与工业界评测标准。支持直接阅读或下载 A4 打印版 PDF。'),
        ('02_招聘岗位资料/argon_岗位要求统计与解读.html','02 · 招聘岗位要求统计与解读','24 份工程 JD · 五层编码','将明确要求、择一选项、单列了解、优先加分、工作职责严格拆开统计，附带 SVG 分层图与公司去重敏感性对比。'),
        ('03_简历与候选人案例/argon_候选人与简历图册.html','03 · 候选人与简历视觉图册','34 位候选人 + 4 份对照','优先展示 7 位核心候选人的公开脱敏 PDF、PNG 简历片段与网页履历；可按后端、Agent、混合方向快速筛选。'),
        ('04_面经与专业观点/argon_面经重点与项目追问.html','04 · 面经重点与项目追问指南','99 份面经 · 10 大问题簇','提炼后端 5 大问题簇与 Agent 5 大问题簇，列出代表性真题、准备深度标准，并映射到 8 个项目的具体源码文件。'),
        ('06_项目分析与推荐/argon_项目比较与精读指南.html','05 · 25 个代码项目比较与精读','按优先级排序 · 含源码包','支持一键筛选“精读级项目”、“候选人本人项目”、“后端/Agent 方向”，左右对比每个项目的核心长处与静态核查短板。'),
        ('01_调研报告/'+DETAIL,'06 · 239 条底层证据全量检索表','全库检索 · 证据链溯源','包含能力要求四类证据对照表、候选人-项目-面经关联链、25 项目 375 维核查矩阵及 239 条记录搜索器。'),
    ]:
        guide += f'<div class="box"><span class="pill core">{E(badge)}</span><h3>{link(href, title)}</h3><p>{E(desc)}</p></div>'
    guide += '''</div>
<h2>三、配套 Markdown 速查清单</h2>
<div class="bottom-links">''' + (
        link('argon_README.md', '全局 README 与目录说明')
        + link('01_调研报告/' + TITLE + '.pdf', '调研总报告 PDF (可打印)')
        + link('06_项目分析与推荐/argon_后端实习阅读顺序.md', '后端实习分级阅读顺序 (.md)')
        + link('06_项目分析与推荐/argon_Agent实习阅读顺序.md', 'Agent 实习分级阅读顺序 (.md)')
        + link('06_项目分析与推荐/argon_技术要求_明确要求与加分项.md', '岗位技术要求分层速查 (.md)')
        + link('06_项目分析与推荐/argon_专业观点交叉核对_评测与工具恢复.md', '工业界评测与工具恢复核对 (.md)')
        + link('01_调研报告/argon_待手动访问链接.html', '受限资料原始链接备查')
    ) + '''</div>
<p class="page-foot">整理日期：2026-10-24 · 各专题目录下的历史过程文档与逐条原始文本卡均已归入归档子目录，日常阅读只需使用上述入口。</p></section>'''
    (ROOT / 'argon_00_开始阅读.html').write_text(shell('开始阅读 · 大厂后端与Agent实习调研', guide, False, ROOT, 'start'), encoding='utf-8')

    (ROOT / 'argon_00_START_HERE.txt').write_text(
        '====================================================================\n'
        '  大厂后端与 Agent 工程实习求职调研（2026 精炼整理版）\n'
        '====================================================================\n\n'
        '【推荐阅读顺序】\n'
        '1. 首站总览导航：双击打开 argon_00_开始阅读.html（或阅读根目录 argon_README.md）\n'
        '2. 核心调研总报告：01_调研报告/argon_实习求职调研总报告.html（配套同名 8 页 PDF）\n'
        '3. 岗位要求统计：  02_招聘岗位资料/argon_岗位要求统计与解读.html\n'
        '4. 真实简历图册：  03_简历与候选人案例/argon_候选人与简历图册.html\n'
        '5. 面经与项目追问：04_面经与专业观点/argon_面经重点与项目追问.html\n'
        '6. 25项目精读指南：06_项目分析与推荐/argon_项目比较与精读指南.html\n'
        '7. 239条证据检索： 01_调研报告/argon_资料检索与证据详表.html\n\n'
        '【核心结论速记】\n'
        '- 后端实习主线：把一条涵盖 DB + Redis + MQ + 异常补偿与排障的请求链讲透，重在边界与一致性。\n'
        '- Agent实习主线：超越简单 API 调用，重点准备状态图编排、RAG 召回重排、工具约束与留出集回归评测。\n'
        '- 目录说明：旧轮次过程报告与逐条 TXT 原始卡已收入各目录的“归档”子文件夹，保持主目录清爽。\n',
        encoding='utf-8'
    )
    summary = {
        'main_report': f'01_调研报告/{TITLE}.html',
        'pdf': f'01_调研报告/{TITLE}.pdf',
        'intended_sections': 8,
        'evidence_records': len(rows),
        'project_cards': len(comparison),
        'new_resume_visual_assets': visuals.get('counts', {}),
        'source': '现有主数据、岗位语义编码、面经项目归纳与视觉附件清单'
    }
    (BASE / 'argon_可读性整理_报告生成统计.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
