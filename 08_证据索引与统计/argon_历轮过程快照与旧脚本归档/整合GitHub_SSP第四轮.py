"""合并本轮新证据；历史报告保留快照，最新目录与待核链接统一更新。"""
import csv
import importlib.util
import io
import json
import re
from collections import Counter
from html import escape
from pathlib import Path

INDEX = Path(__file__).resolve().parent
ROOT = INDEX.parent
REPORT = ROOT / "01_调研报告"
TITLE = "GitHub_SSP第四轮_新面经与项目对照"
if (INDEX / "需求覆盖统计.json").exists():
    raise SystemExit("需求纠偏版已存在；请使用整合需求纠偏.py，禁止用第四轮快照覆盖当前主表。")
spec = importlib.util.spec_from_file_location("evidence_renderer", INDEX / "整合GitHub_SSP第三轮.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
read, write, load, dump, merge, card, flatten = module.read, module.write, module.load, module.dump, module.merge, module.card, module.flatten
module.labels.update({"static_risks": "固定版本代码的静态风险", "version_check_url": "技术版本核对来源", "role": "岗位与范围", "finding": "观察", "commit": "固定提交", "candidate_group": "关联候选人", "sample_group": "资料计数边界"})
data = load("github_ssp_round4_records.json")
new = data["candidates"] + data["interviews"] + data["projects"]
cases = load("candidate_cases.json")
cases["cases"] = merge(cases["cases"], data["candidates"])
cases["counts"]["curated_cases"] = len(cases["cases"])
cases["round4_scope"] = "新增鬼卞署名历史SSP来稿（原发布页待核）、DreamCats本人面经与项目案例（SSP未证）；不算新增近期Agent SSP完整链。"
cases["counts"]["round4_historical_guest_ssp_self_report"] = 1
cases["counts"]["round4_non_ssp_offer_intention_project_case"] = 1
interviews = merge(load("interview_records.json"), data["interviews"])
projects = load("project_recommendations.json")
projects["projects"] = merge(projects["projects"], data["projects"])
projects["round4_scope"] = "新增SchoolBus本人面经关联项目分析，含v1局限；未确认整库许可，不新增ZIP。"
records = merge(load("all_evidence_records.json"), new)
assert len(records) == len({r["id"] for r in records})
dump("candidate_cases.json", cases)
dump("interview_records.json", interviews)
dump("project_recommendations.json", projects)
dump("all_evidence_records.json", records)

blocked_old = load("待手动访问链接.json")
blocked = list({r["url"].split("?")[0]: r for r in blocked_old + data["blocked_new"]}.values())
dump("待手动访问链接.json", blocked)
manifest = json.loads(read(ROOT / "05_项目源码归档/SOURCE_MANIFEST.json"))
stats = {"date": "2026-10-23", "scope": "第四轮继续搜集，不保证穷尽", "new_candidates": 2, "new_historical_guest_ssp_self_report": 1, "new_non_ssp_project_interview_case": 1, "new_interview_records": 7, "new_project_analysis": 1, "new_source_archives": 0, "manual_access_links_new": len(data["blocked_new"]), "manual_access_links_total": len(blocked), "totals": {"candidate_cases": len(cases["cases"]), "interview_material_records": len(interviews), "project_analysis": len(projects["projects"]), "source_archives": len(manifest), "logical_evidence_records": len(records)}, "category_counts": dict(Counter(r["category"] for r in records)), "boundary": data["limits"], "method": data["method"]}
dump("GitHub_SSP第四轮统计.json", stats)

for r in new:
    folder = "03_简历与候选人案例" if r["id"].startswith("CV") else "04_面经与专业观点" if r["id"].startswith("INT") else "06_项目分析与推荐"
    text = r["id"] + " | " + r["title"] + "\n\n"
    for k, v in r.items():
        if k not in {"id", "title"}:
            text += module.labels.get(k, k) + "：" + (json.dumps(v, ensure_ascii=False, indent=2) if isinstance(v, (dict, list)) else str(v)) + "\n\n"
    write(ROOT / folder / (r["id"] + ".txt"), text)

topics = load("interview_topic_index.json")
for row in topics["themes"]:
    row["evidence_ids"] = [r["id"] for r in interviews if re.search(row["rule"], flatten([r.get("topics", []), r.get("project_questions", [])]), re.I)]
    row["record_count"] = len(row["evidence_ids"])
topics.update({"updated_at": "2026-10-23", "scope_records": len(interviews), "scope_note": "截至第四轮；按主题值匹配。逻辑资料数不是独立候选人数或面试场次数。"})
dump("interview_topic_index.json", topics)
buf = io.StringIO(newline="")
writer = csv.writer(buf)
writer.writerow(["主题", "资料条数_非独立场次", "资料ID", "复核规则"])
for row in topics["themes"]: writer.writerow([row["theme"], row["record_count"], ";".join(row["evidence_ids"]), row["rule"]])
write(INDEX / "面经主题索引.csv", buf.getvalue())

previous = read(REPORT / "GitHub_SSP第三轮补充与待核链接.html")
css = re.search(r"<style>([\s\S]*?)</style>", previous).group(1)
css += "\n.manual-link{break-inside:avoid} a{overflow-wrap:anywhere} @media print{.field{break-inside:auto}}"
prefix = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>' + css + '</style>'


def manual_section(rows):
    text = '<section id="manual"><h2>本轮新增加的待核原始链接</h2><p>标题可读不等于正文已核；以下只是待核线索。完整清单含前轮资料，共' + str(len(blocked)) + '条。</p>'
    for n, r in enumerate(rows, 1):
        text += '<article class="manual-link"><h3>' + str(n) + '. ' + escape(r["title"]) + '</h3><p><a href="' + escape(r["url"], quote=True) + '">' + escape(r["url"]) + '</a></p><p><b>访问状态：</b>' + escape(r["status"]) + '</p><p><b>待核事项：</b>' + module.value_html(r["to_verify"]) + '</p></article>'
    return text + '</section>'


manual_html = prefix + '<title>待手动访问链接｜第四轮更新</title></head><body><header><h1>待手动访问链接</h1><p>已累计' + str(len(blocked)) + '条；新增10条排在前面。<a href="' + TITLE + '.html">第四轮报告</a> · <a href="index.html">完整目录</a></p></header><main>' + manual_section(data["blocked_new"] + [r for r in blocked_old if r["url"].split("?")[0] not in {x["url"].split("?")[0] for x in data["blocked_new"]}]) + '<p>只需提供相关专业正文并隐去联系方式；无需付费购买，也不以验证码/空壳判断没有更多资料。</p></main></body></html>'
write(REPORT / "待手动访问链接.html", manual_html)
write(REPORT / "待手动访问链接.html", manual_html.replace("本轮新增加的待核原始链接", "全部待核原始链接"))
manual_md = "# 待手动访问链接（第四轮更新）\n\n正文尚未核实的线索不计为已读面经或已确认SSP成功。\n\n"
for r in data["blocked_new"] + blocked_old:
    manual_md += f'- [{r["title"]}]({r["url"]})\n\n  状态：{r["status"]}\n\n  待核：{flatten(r["to_verify"])}\n\n'
write(ROOT / "04_面经与专业观点/待手动访问链接.md", manual_md)

html = prefix + '<title>GitHub SSP第四轮：新面经与项目对照</title></head><body><header><p>2026-10-23 · 第四轮继续搜集</p><h1>还有新材料：7份面经与一个可直接对照的本人项目</h1><p>新增署名历史SSP来稿1例、普通offer/意向书项目案例1例，补充Go与Agent面经7份、SchoolBus项目分析1份。SSP、普通offer、意向书、失败和结果未知分别记录。</p><p><a href="index.html">完整搜索目录</a> · <a href="待手动访问链接.html">全部待核原始链接</a> · <a href="' + TITLE + '.pdf">本报告PDF</a> · <a href="GitHub_SSP第三轮补充与待核链接.html">第三轮快照</a></p></header><main>'
html += '<section><h2>这轮优先看哪些</h2><div class="tablewrap"><table><thead><tr><th>资料</th><th>新增价值</th><th>边界</th></tr></thead><tbody>'
rows = [("CV20", "鬼卞2019来稿", "字节SSP自述，GSoC＋数据库比赛经历", "第三方收录；原公众号验证页；本人代码未定位"), ("CV21", "DreamCats＋INT66＋PRO19", "项目名、本人多轮问题与源码能直接对照", "京东offer、字节意向书，SSP未证；源码未运行"), ("INT64", "Go面经INT64–65", "字节三轮与B站两轮失败对照", "历史题单，项目细节缺失，答案需另核"), ("INT67", "Agent面经INT67–70", "阿里云热更新AI Coding、华为项目贡献、百度上下文与工具循环", "仅华为明确普通offer；年份、结果或正文范围逐条说明")]
for ident, name, value, limits in rows:
    html += '<tr><td><a href="#' + ident + '">' + name + '</a></td><td>' + value + '</td><td>' + limits + '</td></tr>'
html += '</tbody></table></div><p>没有新增源码ZIP或完整CV原件。当前共21份候选人分析、63份面经逻辑资料、19份项目分析、16个固定源码包；同一作者多轮不算多位成功者。</p></section>'
html += '<section><h2>新的候选人材料</h2>' + ''.join(card(r, True) for r in data["candidates"]) + '</section>'
html += '<section><h2>新面经：逐项区分原文、结果和阅读范围</h2>' + ''.join(card(r, True) for r in data["interviews"]) + '</section>'
html += '<section><h2>项目与面经对照：能学什么，哪里需要反查</h2>' + ''.join(card(r, True) for r in data["projects"]) + '</section>'
html += '<section><h2>本轮没有混入的材料</h2><ul><li>小米暑期Agent问答只公开部分内容，页尾提示付费。没有购买，也没有按标题当作完整本人面经或真实项目代码证据。</li><li>AgentGuide、行业指南、第三方薪资表用来发现链接；没有把收录者当成全部经历的本人，也没有按题库数量虚增面经数。</li><li>广告平台SSP、语言学SSP、RISC-V寄存器等同名缩写不计招聘结果。</li><li>百度两篇原帖没有核实同一作者，不拼成同一人的连续面试；产品参数、内部架构和延迟口号不当已证事实。</li></ul></section>'
html += manual_section(data["blocked_new"])
html += '<section><h2>覆盖范围和核验日志</h2><p>' + escape(data["method"]) + '</p><p>' + escape(data["limits"]) + '</p><p><a href="../08_证据索引与统计/github_ssp_round4_records.json">本轮整理记录</a> · <a href="../08_证据索引与统计/github_ssp_backend_round4_search.json">GitHub定向检索</a> · <a href="../08_证据索引与统计/github_ssp_agent_round4_search.json">Agent索引检索</a> · <a href="../08_证据索引与统计/github_ssp_round4_follow_paths.json">原帖发现与去重</a> · <a href="../08_证据索引与统计/github_ssp_round4_fulltext_access.json">第一批正文访问</a> · <a href="../08_证据索引与统计/github_ssp_round4_follow_article_reads.json">补充正文访问</a> · <a href="../08_证据索引与统计/GitHub_SSP第四轮统计.json">最新统计</a></p><p>本轮未核实新的近期Agent正式SSP＋本人项目＋本人面经完整关联；不等于不存在。个人项目设计继续暂缓。</p></section></main><footer>公开来源与原创归纳 · 固定版本代码仅静态阅读 · 检索未穷尽</footer></body></html>'
write(REPORT / (TITLE + ".html"), html)

main = read(REPORT / "index.html")
main = re.sub(r'<aside id="github-ssp-round[34]">[\s\S]*?</aside>', '', main)
banner = '<aside id="github-ssp-round4"><b>第四轮最新：</b><a href="' + TITLE + '.html">7份新面经、署名SSP来稿与本人项目对照</a> · <a href="待手动访问链接.html">21条待核原始入口</a>。全包144条逻辑资料，未保证穷尽。</aside>'
main = re.sub(r'<aside id="github-ssp-round4">[\s\S]*?</aside>', '', main)
main = main.replace('<article>', '<article>' + banner, 1)
main = re.sub(r'<div class="stats">[\s\S]*?</div>', '<div class="stats"><span><strong>19</strong>JD线索 / 14全文工程实习</span><span><strong>21</strong>候选人分析 / 非完整CV原件</span><span><strong>63</strong>面经与复盘</span><span><strong>7</strong>B站/知乎资料</span><span><strong>16</strong>固定版本源码</span></div>', main, count=1)
intro = '<section id="s0"><h2>01 最新阅读入口</h2><p><a href="' + TITLE + '.html">第四轮：新的面经与项目对照</a>，优先看CV21／INT66／PRO19。CV20为GitHub收录的署名历史SSP来稿；不是仓主经历。<a href="待手动访问链接.html">21条待手动核查的原始链接</a>。</p><p>全包21份候选人分析、63份面经逻辑资料、19份项目分析、16个源码包。旧报告和PDF保留各轮快照；完整CV原件未取得。个人项目设计暂缓。</p></section>'
main = re.sub(r'<section id="s0">[\s\S]*?</section>', lambda _: intro, main, count=1)
categories = list(dict.fromkeys(r["category"] for r in records))
catalog = '<section id="evidence"><h2>15 可搜索资料目录</h2><p>第四轮新增CV20–21、INT64–70、PRO19。SSP、普通offer、意向书、失败、结果未知分别标注；原帖未读不计已读面经。</p><div class="tools"><input id="q" type="search" placeholder="例如：DreamCats、INT67、鬼卞、SchoolBus"><select id="category"><option>全部类别</option>' + ''.join('<option>' + escape(c) + '</option>' for c in categories) + '</select><button id="expand">展开匹配</button><button id="collapse">全部收起</button></div><p class="muted" id="count"></p>' + ''.join(card(r) for r in records) + '</section>'
main = re.sub(r'<section id="evidence">[\s\S]*?</section>', lambda _: catalog, main, count=1)
main = main.replace('现共56份面经资料（截至第三轮）', '现共63份面经资料（截至第四轮）').replace('56份面经资料与7份B站/知乎资料卡', '63份面经资料与7份B站/知乎资料卡').replace('19份候选人分析，含历史HTML/TeX履历模块；非完整CV原件', '21份候选人分析，含历史HTML/TeX履历模块及署名来稿；非完整CV原件')
write(REPORT / "index.html", main)
for name in ["GitHub_SSP项目与面经专项.html", "GitHub_SSP第二轮补充.html", "GitHub_SSP第三轮补充与待核链接.html", "信息搜集增补报告.html"]:
    old = read(REPORT / name)
    old = re.sub(r'<aside id="round4-followup">[\s\S]*?</aside>', '', old)
    old = old.replace('<main>', '<main><aside id="round4-followup"><b>第四轮已更新：</b><a href="' + TITLE + '.html">7份新面经与本人项目分析</a> · <a href="待手动访问链接.html">最新待核链接</a>。以下保留当轮快照。</aside>', 1)
    write(REPORT / name, old)
write(ROOT / "00_START_HERE.txt", "大厂后端与Agent信息搜集包 | 第四轮更新 | 2026-10-23\n\n最新报告：01_调研报告/" + TITLE + ".html（或同名PDF）。\n完整搜索目录：01_调研报告/index.html。\n受限与待核原帖：01_调研报告/待手动访问链接.html（21条）。\n\n本轮新增：7份面经、2份候选人资料、1份SchoolBus项目分析。鬼卞为第三方收录的历史SSP来稿；DreamCats只有普通offer/意向书证据。没有新增源码ZIP或完整CV原件。\n\n全包：21份候选人分析、63份面经逻辑资料、19份项目分析、16个固定源码包。\n不保证搜尽；近期Agent SSP完整关联本轮未核实新例，不等于不存在。个人项目设计继续暂缓。\n旧报告及PDF保留各轮快照，最新统计见08_证据索引与统计/GitHub_SSP第四轮统计.json。\n")
write(ROOT / "00_GitHub_SSP第四轮更新说明.md", "# 第四轮继续搜集\n\n- [新面经与项目对照](01_调研报告/" + TITLE + ".html)\n- [PDF](01_调研报告/" + TITLE + ".pdf)\n- [21条待核原始入口](01_调研报告/待手动访问链接.html)\n- [完整搜索目录](01_调研报告/index.html)\n\n新增2份候选人资料、7份面经、1份项目分析；无新增源码ZIP。历史署名来稿、普通offer、意向书、失败和结果未知均标明。个人项目设计暂缓。\n")
method_path = INDEX / "source_methodology.txt"
method = read(method_path).split("\nGitHub SSP第四轮最新更新：")[0]
write(method_path, method.rstrip() + "\n\nGitHub SSP第四轮最新更新：\n" + json.dumps(stats, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(stats, ensure_ascii=False, indent=2))
