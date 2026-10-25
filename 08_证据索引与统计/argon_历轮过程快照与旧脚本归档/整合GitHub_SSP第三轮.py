"""合并第三轮已读证据与待手动访问清单；不执行第三方项目。"""
from collections import Counter
from html import escape
from pathlib import Path
import ast
import csv
import io
import json
import re

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "08_证据索引与统计"
REPORT = ROOT / "01_调研报告"
TITLE = "GitHub_SSP第三轮补充与待核链接"

if __name__ == "__main__" and (INDEX / "GitHub_SSP第四轮统计.json").exists():
    raise SystemExit("已有第四轮交付；停止旧整合脚本，避免覆盖最新目录与统计。")


def read(path):
    return path.read_text(encoding="utf-8-sig")


def write(path, text):
    newline = "\r\n" if not path.exists() or b"\r\n" in path.read_bytes() else "\n"
    with path.open("w", encoding="utf-8", newline="") as stream:
        stream.write(text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", newline))


def load(name):
    return json.loads(read(INDEX / name))


def dump(name, value):
    write(INDEX / name, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def merge(old, added):
    items = {r["id"]: r for r in old}
    items.update({r["id"]: r for r in added})
    return list(items.values())


labels = {}
for node in ast.parse(read(INDEX / "整合增补资料.py")).body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "LABELS" for t in node.targets):
        labels = ast.literal_eval(node.value)
labels.update({"document_type": "资料形式", "source_findings": "已核来源与发现", "location": "定位", "finding": "发现", "strengths": "值得参考之处", "static_findings": "代码静态观察", "limits": "局限", "verified_contributions": "已核本人贡献", "author_login": "作者账号", "merged_at": "合并日期", "merge_commit": "合并提交", "code_url": "固定代码入口", "scope": "范围", "verification_boundary": "验证范围", "historical_profile": "历史履历专业模块", "project_relationship": "项目与求职关系", "outcome_evidence": "档位证据边界", "interview_attribution": "面经归属", "sources": "来源", "short_excerpt": "短摘录", "commit_date": "提交日期", "license_notes": "许可证说明", "archive_status": "源码归档情况", "read_scope": "已读范围", "contribution_boundary": "贡献范围", "company_boundary": "公司档位边界", "source_summary": "来源归纳", "rounds": "面试内容", "status": "状态", "name": "名称"})


def value_html(value):
    if isinstance(value, list):
        return "<ul>" + "".join("<li>" + value_html(v) + "</li>" for v in value) + "</ul>"
    if isinstance(value, dict):
        return "<br>".join(escape(labels.get(k, k)) + "：" + value_html(v) for k, v in value.items())
    if isinstance(value, bool):
        return "是" if value else "否"
    text = str(value)
    if re.fullmatch(r"https?://[^\s]+", text):
        return '<a href="' + escape(text, quote=True) + '">' + escape(text) + '</a>'
    if text.endswith(".zip") and Path(text).name == text and (ROOT / "05_项目源码归档" / text).is_file():
        return '<a href="../05_项目源码归档/' + escape(text, quote=True) + '">' + escape(text) + '</a>'
    return escape(text).replace("\n", "<br>")


def card(r, opened=False):
    fields = ''.join('<div class="field"><b>' + escape(labels.get(k, k)) + '</b><div>' + value_html(v) + '</div></div>' for k, v in r.items() if k not in {"id", "title", "category", "retrieved_at", "retrieved_date"} and v not in (None, [], ""))
    return '<details class="card" id="' + r["id"] + '" data-category="' + escape(r.get("category", "")) + '"' + (' open' if opened else '') + '><summary><span class="tag">' + r["id"] + '</span> ' + escape(r["title"]) + '</summary>' + fields + '</details>'


def flatten(value):
    if isinstance(value, list): return " ".join(flatten(v) for v in value)
    if isinstance(value, dict): return " ".join(flatten(v) for v in value.values())
    return str(value)


def integrate(new_candidates, new_interviews, new_projects, blocked):
    root = load("github_ssp_round3_root_discovery.json")
    cases = load("candidate_cases.json")
    cases.setdefault("pre_round3_counts", dict(cases["counts"]))
    cases["cases"] = merge(cases["cases"], new_candidates)
    cases["counts"]["curated_cases"] = len(cases["cases"])
    cases["counts"]["successful_self_report_without_resume"] = cases["pre_round3_counts"]["successful_self_report_without_resume"] + 1
    cases["counts"]["successful_historical_tex_profile_without_complete_cv"] = 1
    cases["round3_scope"] = "新增IcyCC历史SP/SSP混合结果自述与鱼皮腾讯实习转正SSP自述；前者有2019历史履历专业模块。没有取得可打包完整CV原件。"
    strengthened = root["existing_candidate_strengthening"]
    for r in cases["cases"]:
        if r["id"] == "CV05":
            r["verified_contributions"] = strengthened["verified_contributions"]
            r["round3_contribution_boundary"] = strengthened["verification_boundary"] + "；" + strengthened["finding"]
    interviews = merge(load("interview_records.json"), new_interviews)
    project_file = load("project_recommendations.json")
    project_file["projects"] = merge(project_file["projects"], new_projects)
    for r in project_file["projects"]:
        if r["id"] == "PRO09":
            r["verified_contributions"] = strengthened["verified_contributions"]
            r["round3_recommended_use"] = strengthened["recommended_use"]
            r["round3_boundary"] = strengthened["verification_boundary"]
    project_file["round3_scope"] = "新增Crony工程阅读参考；未证作者SSP，不增加源码ZIP；补强ShenYu同账号已合并PR。"
    changed = new_candidates + new_interviews + new_projects
    changed += [next(r for r in cases["cases"] if r["id"] == "CV05"), next(r for r in project_file["projects"] if r["id"] == "PRO09")]
    all_records = merge(load("all_evidence_records.json"), changed)
    assert len(all_records) == len({r["id"] for r in all_records})
    dump("candidate_cases.json", cases)
    dump("interview_records.json", interviews)
    dump("project_recommendations.json", project_file)
    dump("all_evidence_records.json", all_records)
    dump("github_ssp_round3_records.json", {"new_candidates": new_candidates, "new_interviews": new_interviews, "new_projects": new_projects, "strengthened_existing_ids": ["CV05", "PRO09"]})
    dump("待手动访问链接.json", blocked)
    manifest = json.loads(read(ROOT / "05_项目源码归档/SOURCE_MANIFEST.json"))
    stats = {"date": "2026-10-23", "scope": "第三轮扩搜；未穷尽", "new_candidate_self_reports": 2, "new_interview_records": len(new_interviews), "new_project_analysis": len(new_projects), "new_source_archives": 0, "strengthened_existing_ids": ["CV05", "PRO09"], "manual_access_links": len(blocked), "recent_agent_complete_chain": "本轮未新增已核实案例；不能推断不存在", "totals": {"candidate_cases": len(cases["cases"]), "interview_material_records": len(interviews), "project_analysis": len(project_file["projects"]), "source_archives": len(manifest), "logical_evidence_records": len(all_records)}, "category_counts": dict(Counter(r["category"] for r in all_records)), "boundary": "SP/SSP混合结果不逐家公司指定档位；实习转正与秋招分开；未读链接不计录用成功；PR合并不证明SSP因果。"}
    dump("GitHub_SSP第三轮统计.json", stats)
    for r in changed:
        folder = "04_面经与专业观点" if r["id"].startswith("INT") else "06_项目分析与推荐" if r["id"].startswith("PRO") else "03_简历与候选人案例"
        write(ROOT / folder / (r["id"] + ".txt"), r["id"] + " | " + r["title"] + "\n\n" + "\n\n".join(labels.get(k, k) + "：" + (json.dumps(v, ensure_ascii=False, indent=2) if isinstance(v, (list, dict)) else str(v)) for k, v in r.items() if k not in {"id", "title"}) + "\n")
    topics = load("interview_topic_index.json")
    for row in topics["themes"]:
        row["evidence_ids"] = [r["id"] for r in interviews if re.search(row["rule"], flatten([r.get("topics", []), r.get("project_questions", [])]), re.I)]
        row["record_count"] = len(row["evidence_ids"])
    topics.update({"updated_at": "2026-10-23", "scope_records": len(interviews), "scope_note": "截至第三轮；只按正文主题值匹配，逻辑资料数不是独立场次数。"})
    dump("interview_topic_index.json", topics)
    buf = io.StringIO(newline="")
    writer = csv.writer(buf)
    writer.writerow(["主题", "资料条数_非独立场次", "资料ID", "复核规则"])
    for row in topics["themes"]: writer.writerow([row["theme"], row["record_count"], ";".join(row["evidence_ids"]), row["rule"]])
    write(INDEX / "面经主题索引.csv", buf.getvalue())
    make_reports(new_candidates, new_interviews, new_projects, strengthened, blocked, all_records, stats)
    print(json.dumps(stats, ensure_ascii=False, indent=2))


def make_reports(candidates, interviews, projects, strengthened, blocked, all_records, stats):
    previous = read(REPORT / "GitHub_SSP第二轮补充.html")
    css = re.search(r"<style>([\s\S]*?)</style>", previous).group(1)
    css += "\na{overflow-wrap:anywhere} .field{break-inside:auto} @media print{aside{break-inside:auto}}"
    prefix = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>' + css + '</style>'
    manual = '<section id="manual"><h2>受限及待手动访问原始链接</h2><p>这些链接尚未核到完整正文或所需文件。HTTP403、429、521、正文空壳、404、证书错误、超时分别记录，不把它们统称为限流。标题可能来自搜索索引，不能据此认定作者已获SSP。</p><p>打开后优先找：本人身份、岗位和年月、SSP是正式录用还是面试资格、项目名与GitHub、逐轮面经、课程或转载属性。可以只提供相关正文，隐去联系方式。</p>'
    for i, r in enumerate(blocked, 1):
        manual += '<article class="manual-link"><h3>' + str(i) + '. ' + escape(r["title"]) + '</h3><p><a href="' + escape(r["url"], quote=True) + '">' + escape(r["url"]) + '</a></p><p><b>访问状态：</b>' + escape(r["status"]) + '</p><p><b>待核实：</b>' + value_html(r["to_verify"]) + '</p></article>'
    manual += '</section>'
    manual_html = prefix + '<title>待手动访问链接</title></head><body><header><h1>待手动访问链接</h1><p>2026-10-23 · <a href="' + TITLE + '.html">第三轮报告</a> · <a href="index.html">完整目录</a></p></header><main>' + manual + '</main></body></html>'
    write(REPORT / "待手动访问链接.html", manual_html)
    md = "# 待手动访问链接\n\n这些是待核线索，未计为已确认录用或已读面经。\n\n"
    for i, r in enumerate(blocked, 1):
        md += f'{i}. [{r["title"]}]({r["url"]})\n\n   访问状态：{r["status"]}\n\n   待核实：{flatten(r["to_verify"])}\n\n'
    write(ROOT / "04_面经与专业观点/待手动访问链接.md", md)
    html = prefix + '<title>GitHub SSP第三轮补充与待核链接</title></head><body><header><p>2026-10-23 · 第三轮继续搜集</p><h1>新增历史履历与面经，补到具体开源贡献</h1><p>新增IcyCC历史SP/SSP混合结果自述、鱼皮腾讯实习转正SSP自述；补核erdengk两项已合并PR，并新增Crony工程分析。待手动访问链接单列，个人项目设计继续暂缓。</p><p><a href="index.html">完整目录</a> · <a href="待手动访问链接.html">单独打开待核链接清单</a> · <a href="' + TITLE + '.pdf">PDF</a> · <a href="GitHub_SSP第二轮补充.html">第二轮快照</a></p></header><main>'
    html += '<section><h2>本轮真正补了什么</h2><ul><li>IcyCC：2019求职复盘＋2019历史TeX履历专业模块，直接对应reimu、async_easyapi等项目；只有总体技术追问，不能写成逐公司逐轮面经。</li><li>鱼皮：本人站点明确腾讯实习转正SSP；当年项目与本人面经仍待核，后来的教程和AI项目不能回填为当年求职项目。</li><li>erdengk：从笼统开源关联补到两个已合并本人PR，静态分析OAuth2与RocketMQ测试的覆盖及不足；不是整套网关的个人原创证明。</li><li>Crony：有Etcd注册、调度、故障转移的个人重写项目；尚未核到作者SSP，作为独立工程参考。</li></ul><p>本轮新增2份候选人分析、1份面经复盘、1份项目分析，没有新增源码ZIP。当前全包' + str(stats["totals"]["candidate_cases"]) + '份候选人分析、' + str(stats["totals"]["interview_material_records"]) + '份面经资料、' + str(stats["totals"]["project_analysis"]) + '份项目分析、' + str(stats["totals"]["source_archives"]) + '个固定源码包。</p></section>'
    html += '<section><h2>为什么前面漏掉了</h2><p>此前检索词覆盖、对历史版本的追踪和正文失败后的核查都不够充分。第三轮补到的2019历史简历，正是不能只看当前README或当前简历的例子。此前“未找到”只代表当轮访问结果，不能说没有更多。</p><p>这轮继续做GitHub README检索、原作者追源和固定版本核查；不覆盖私有仓库、未公开经历或所有文件。近期Agent“正式SSP录用＋成熟本人项目＋本人面经”的完整关系本轮仍未新增已核案例，不能据此推断不存在。</p></section>'
    html += '<section><h2>新候选人和本人面经</h2>' + ''.join(card(r, True) for r in candidates + interviews) + '</section>'
    contribution_card = {"id": "CV05", "title": "erdengk／已有案例补强：两项本人已合并PR", "category": "候选人资料", "url": "https://github.com/erdengk", "verified_contributions": strengthened["verified_contributions"], "recommended_use": strengthened["recommended_use"], "limitations": strengthened["finding"], "verification_boundary": strengthened["verification_boundary"]}
    html += '<section><h2>已有SSP作者：开源贡献落到具体变更</h2>' + card(contribution_card, True) + '</section>'
    html += '<section><h2>新增工程参考：作者SSP尚未核到</h2>' + ''.join(card(r, True) for r in projects) + '</section>'
    html += manual
    html += '<section><h2>核查记录</h2><p><a href="../08_证据索引与统计/github_ssp_backend_round3_discovery.json">后端与历史履历</a> · <a href="../08_证据索引与统计/github_ssp_systems_round3_discovery.json">系统项目</a> · <a href="../08_证据索引与统计/github_ssp_agent_round3_discovery.json">Agent与受限原帖</a> · <a href="../08_证据索引与统计/github_ssp_round3_root_discovery.json">本人站点与PR补强</a> · <a href="../08_证据索引与统计/GitHub_SSP第三轮统计.json">最新统计</a></p><p>录用与历史经历仍以作者自述为限；PR作者与合并状态由GitHub公开记录核实。源码仅静态阅读，未运行第三方项目、调用模型或联系作者。完整CV原件仍未取得。</p></section></main><footer>本轮为可审查的公开材料补充，不保证检索穷尽。</footer></body></html>'
    write(REPORT / (TITLE + ".html"), html)
    main_path = REPORT / "index.html"
    main = read(main_path)
    for historical_banner in ["github-ssp-round2", "github-ssp-update"]:
        main = re.sub(r'<aside id="' + historical_banner + r'">[\s\S]*?</aside>', '', main)
    main = main.replace("上轮信息搜集增补：", "历史增补快照（非最新统计）：").replace("现有48条面经、13份项目分析、12个源码包", "当时为48条面经、13份项目分析、12个源码包")
    main = re.sub(r'<aside id="github-ssp-round3">[\s\S]*?</aside>', '', main)
    banner = '<aside id="github-ssp-round3"><b>最新第三轮：</b><a href="' + TITLE + '.html">IcyCC历史履历、鱼皮转正SSP自述与具体PR补强</a> · <a href="待手动访问链接.html">受限原始链接清单</a>。当前' + str(len(all_records)) + '条逻辑资料；未保证穷尽。</aside>'
    main = main.replace('<article>', '<article>' + banner, 1)
    totals = stats["totals"]
    main = re.sub(r'<div class="stats">[\s\S]*?</div>', '<div class="stats"><span><strong>19</strong>JD线索 / 14全文工程实习</span><span><strong>' + str(totals["candidate_cases"]) + '</strong>候选人分析 / 非完整CV原件</span><span><strong>' + str(totals["interview_material_records"]) + '</strong>面经与复盘</span><span><strong>7</strong>B站/知乎资料</span><span><strong>' + str(totals["source_archives"]) + '</strong>固定版本源码</span></div>', main, count=1)
    intro = '<section id="s0"><h2>01 本轮阅读入口</h2><p>最新：<a href="' + TITLE + '.html">GitHub SSP第三轮补充</a>，优先读CV18／INT63及CV05新增PR；CV19为转正SSP自述，PRO18不是已核SSP项目。<a href="待手动访问链接.html">受限与待核原始链接可直接点击</a>。</p><p>全包' + str(totals["candidate_cases"]) + '份候选人分析、' + str(totals["interview_material_records"]) + '份面经资料、' + str(totals["project_analysis"]) + '份项目分析、' + str(totals["source_archives"]) + '个源码包。旧报告保留各轮快照。历史HTML履历专业页1份，新增2019 TeX履历专业模块1份；可打包完整CV原件0。个人项目设计暂缓。</p></section>'
    main = re.sub(r'<section id="s0">[\s\S]*?</section>', lambda _: intro, main, count=1)
    categories = list(dict.fromkeys(r["category"] for r in all_records))
    catalog = '<section id="evidence"><h2>15 可搜索资料目录</h2><p>新增CV18、CV19、INT63、PRO18；CV05／PRO09补强。同作者多轮不计为独立成功者，待核原帖不计为已读资料。</p><div class="tools"><input id="q" type="search" placeholder="例如：IcyCC、INT63、Crony、RocketMQ"><select id="category"><option>全部类别</option>' + ''.join('<option>' + escape(c) + '</option>' for c in categories) + '</select><button id="expand">展开匹配</button><button id="collapse">全部收起</button></div><p class="muted" id="count"></p>' + ''.join(card(r) for r in all_records) + '</section>'
    main = re.sub(r'<section id="evidence">[\s\S]*?</section>', lambda _: catalog, main, count=1)
    main = main.replace('现共55份面经资料', '现共56份面经资料（截至第三轮）').replace('55份面经资料与7份B站/知乎资料卡', '56份面经资料与7份B站/知乎资料卡').replace('17份候选人分析，含公开HTML履历页与跨站参考；非完整CV原件', '19份候选人分析，含历史HTML/TeX履历模块；非完整CV原件')
    write(main_path, main)
    for name in ["GitHub_SSP项目与面经专项.html", "GitHub_SSP第二轮补充.html", "信息搜集增补报告.html"]:
        p = REPORT / name
        old = re.sub(r'<aside id="round3-followup">[\s\S]*?</aside>', '', read(p))
        old = old.replace('<main>', '<main><aside id="round3-followup"><b>已有第三轮更新：</b><a href="' + TITLE + '.html">新增历史履历、面经及本人PR补强</a> · <a href="待手动访问链接.html">受限原始链接</a>。以下仍保留当轮快照。</aside>', 1)
        write(p, old)
    write(ROOT / "00_START_HERE.txt", "大厂后端与Agent信息搜集包 | SSP第三轮更新 | 2026-10-23\n\n先看01_调研报告/" + TITLE + ".html或同名PDF。\n受限原始链接：01_调研报告/待手动访问链接.html。\n完整可搜索入口：01_调研报告/index.html。\n\n本轮新增IcyCC历史SP/SSP自述＋2019履历专业模块＋本人总体面试复盘，鱼皮腾讯实习转正SSP自述，Crony非SSP工程参考；补核erdengk两个已合并PR。不新增源码ZIP。\n全包：19份候选人分析、56份面经资料、18份项目分析、16个固定源码包。完整CV原件仍0。\n\n不能保证搜尽；近期Agent完整SSP录用、本人项目与面经关联本轮未新增已核案例，不等于不存在。个人项目设计继续暂缓。\n最新统计：08_证据索引与统计/GitHub_SSP第三轮统计.json。旧报告和PDF为各轮快照。\n")
    write(ROOT / "00_GitHub_SSP第三轮更新说明.md", "# GitHub SSP第三轮补充\n\n- [第三轮报告](01_调研报告/" + TITLE + ".html)\n- [PDF](01_调研报告/" + TITLE + ".pdf)\n- [受限原始链接](01_调研报告/待手动访问链接.html)\n- [完整搜索目录](01_调研报告/index.html)\n\n新增2份候选人分析、1份面经复盘、1份工程项目分析，补强CV05/PRO09本人已合并PR；无新增源码ZIP。未保证搜尽，个人项目设计暂缓。\n")
    method_path = INDEX / "source_methodology.txt"
    method = read(method_path).split("\nGitHub SSP第三轮最新更新：")[0]
    write(method_path, method.rstrip() + "\n\nGitHub SSP第三轮最新更新：\n" + json.dumps(stats, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    records = load("github_ssp_round3_curated_input.json")
    integrate(records["candidates"], records["interviews"], records["projects"], records["blocked"])
