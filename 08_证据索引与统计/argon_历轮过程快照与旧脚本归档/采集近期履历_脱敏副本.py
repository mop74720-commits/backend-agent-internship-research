"""公开履历调研：原件仅在内存读取，写出去联系方式的专业模块副本。"""
from pathlib import Path
import hashlib
import json
import re
import warnings

import fitz
import requests

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "03_简历与候选人案例" / "履历对照_脱敏副本"
QA = Path("C:/Users/GW/.codex/visualizations/2026/10/23/01a16839-9742-7672-812b-1576a3dd064f")
S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0"

SPECS = [
    {
        "key": "gty111", "author": "郭天宇 / Tianyu Guo", "track": "AI Infra与Code Agent训练系统对照",
        "home": "https://gty111.github.io/info/index.html",
        "live_pdf": "https://gty111.github.io/info/doc/resume.pdf",
        "repo": "gty111/gty111.github.io", "sha": "9a56393b93ff495dfef1587ff995fbc96a98c4c1",
        "path": "source/info/doc/resume.pdf", "commit_date": "2026-06-14T00:54:56Z",
        "education_marker": "Education",
        "modules": ["Education", "Skills", "Publications", "Experience and Projects", "Honors and Awards"],
        "outcomes": [
            {"company": "腾讯混元", "role": "Intern", "time": "2026.03–至今", "basis": "本人主页Experience；PDF的Scheduling for RL Training直接标注Tencent Hunyuan Intern"},
            {"company": "小红书Hilab", "role": "RedStar Intern", "time": "2025.08–2025.12", "basis": "本人主页Experience；PDF的REDServe直接标注RedNote Hilab Intern"},
            {"company": "Moonshot AI", "role": "Intern", "time": "2025.12–2026.03", "basis": "本人主页Experience；不将此经历误写为PDF已列出的项目"},
        ],
        "analysis": "博士履历，突出LLM serving、KV cache、RL路由和PD分离。gLLM/EFIM有本人主页直链，简历将系统项目与实习职责相连；不等于普通Agent应用开发门槛。",
        "projects": [
            {"name": "gLLM", "url": "https://github.com/gty111/gLLM", "relation": "本人主页直接链接；PDF直接点名本人参与的分布式LLM serving研究", "caveat": "研究合作项目，不把整仓算独立开发"},
            {"name": "EFIM", "url": "https://github.com/gty111/EFIM", "relation": "本人主页直接链接；PDF直接点名腾讯Code Buddy实习项目（2024，历史）", "caveat": "不把2024实习计入近两年新获实习"},
            {"name": "SGLang PR #12263", "url": "https://github.com/sgl-project/sglang/pull/12263", "relation": "PDF Skills直接点名该PR", "caveat": "本分支尚未核PR作者与修改内容，不能称已审贡献"},
        ],
        "limits": ["无本人求职面经", "未披露SSP档位", "研究/Infra对照，不能冲抵后端或Agent应用工程完整简历缺口", "论文和性能数据为作者自述，未复现实验"],
    },
    {
        "key": "Zhongzhi660", "author": "李忠智 / Zhongzhi Li", "track": "Agent算法研究对照",
        "home": "https://zhongzhi660.github.io/personal_website/",
        "live_pdf": "https://zhongzhi660.github.io/personal_website/data/resume.pdf",
        "repo": "Zhongzhi660/personal_website", "sha": "6c910277e2f6bc740d431809d53f6808959c9eb9",
        "path": "data/resume.pdf", "commit_date": "2026-08-25T03:24:10Z",
        "education_marker": "Education",
        "modules": ["Education", "Research projects & Interests", "Intern Experience", "Awards & Achievements", "Skills"],
        "outcomes": [
            {"company": "腾讯", "role": "Agent Algorithm Intern", "time": "2026.05–至今", "basis": "本人站index.html的Experience明确列出；PDF版本较旧，没有这段"},
            {"company": "X Square Robot", "role": "Robotics Algorithm Intern", "time": "2025.05–2025.07", "basis": "本人站index.html；PDF没有这段"},
        ],
        "analysis": "官网履历明确近期腾讯Agent算法实习；两页PDF保留教育、科研、过往实习、奖项与技术技能。PDF与官网经历不同步，必须分别引用，不能拼成同一投递版本。",
        "projects": [
            {"name": "FAC-Synthesis", "url": "https://github.com/Zhongzhi660/FAC-Synthesis", "relation": "本人站论文code直接链接；PDF直接描述Feature Activation Coverage研究", "caveat": "尚未按提交记录细分个人代码贡献；不能倒推2026腾讯实习由该项目带来"},
            {"name": "长程Terminal任务/后训练研究", "url": "https://zhongzhi660.github.io/personal_website/", "relation": "本人主页当前研究方向与论文材料", "caveat": "不是已核完整Agent应用工程求职项目"},
        ],
        "limits": ["当前官网与PDF有版本差异", "没有本人面经", "没有SSP自述", "研究方向单列，不计核心应用工程完整简历", "尚未核企业录用"],
    },
    {
        "key": "Zhang-Henry", "author": "Hanrong Zhang", "track": "Agent研究实习对照",
        "home": "https://zhang-henry.github.io/",
        "live_pdf": "https://zhang-henry.github.io/assets/pdf/CV_Hanrong_Zhang.pdf",
        "repo": "Zhang-Henry/zhang-henry.github.io", "sha": "2e8c9924537d823d07ea8470ddeff0ae99d14bf7",
        "path": "assets/pdf/CV_Hanrong_Zhang.pdf", "commit_date": "2026-10-20T20:59:07Z",
        "education_marker": "EDUCATION",
        "modules": ["EDUCATION", "INTERNSHIP", "RESEARCH EXPERIENCE", "OPEN-SOURCE PROJECTS", "INVITED TALKS", "ACADEMIC SERVICE"],
        "outcomes": [
            {"company": "阿里巴巴", "role": "Research Intern", "time": "2025.05–2025.08", "basis": "本人主页与PDF INTERNSHIP均明确，工作为人机多轮Agent交互RL研究"},
            {"company": "Google", "role": "Student Researcher", "time": "2026.05–至今", "basis": "本人主页与PDF INTERNSHIP均明确，工作为GUI Agent数据合成及benchmark"},
        ],
        "analysis": "两页博士履历直接展示Agent安全评测、自演化技能、图记忆和科研工作台贡献，适合观察研究问题、个人贡献、评测与边界怎样写在一起；不代表普通应用工程实习或SSP标准。",
        "projects": [
            {"name": "Agent Security Bench", "url": "https://github.com/agiresearch/ASB", "relation": "本人主页和PDF研究经历直接点名，标注first author", "caveat": "多人研究仓库；不能将整仓工作全部归作者独立完成"},
            {"name": "CoEvoSkills", "url": "https://github.com/Zhang-Henry/CoEvoSkills", "relation": "本人主页和PDF直接点名，标注first author", "caveat": "本分支未运行，结果是简历宣称而非复现"},
            {"name": "Dr. Claw", "url": "https://github.com/OpenLAIR/dr-claw", "relation": "PDF OPEN-SOURCE PROJECTS直接标注second author/core contributor", "caveat": "协作项目，未逐commit审个人实现范围；不能当2025阿里求职时项目"},
        ],
        "limits": ["博士研究方向，不冲抵核心后端/Agent应用工程简历缺口", "无本人求职面经", "未披露SSP档位", "2026项目不能回填为2025阿里录用时项目", "未运行项目/评测"],
    },
]


def build_copy(spec):
    fixed = f"https://raw.githubusercontent.com/{spec['repo']}/{spec['sha']}/{spec['path']}"
    response = S.get(fixed, timeout=45)
    response.raise_for_status()
    original = response.content  # 原始文件不落盘
    doc = fitz.open(stream=original, filetype="pdf")
    before_text = "\n".join(p.get_text() for p in doc)
    headings = doc[0].search_for(spec["education_marker"])
    if not headings:
        raise ValueError("缺少教育模块，禁止猜测脱敏边界")
    header_bottom = min(x.y0 for x in headings) - 3
    doc[0].add_redact_annot(fitz.Rect(0, 0, doc[0].rect.width, header_bottom), fill=(1, 1, 1))
    redactions = 1
    # 删除所有页面的链接注释，避免隐藏mailto/tel/社交联系地址残留。
    # 可见专业项目/论文文本与模块不删；原链接另保留在证据JSON。
    link_count = 0
    for page in doc:
        for link in page.get_links():
            page.delete_link(link)
            link_count += 1
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                text = "".join(s["text"] for s in line["spans"])
                suspicious = (
                    re.search(r"[\w.+-]+\s*@\s*[\w.-]+\.[A-Za-z]{2,}", text)
                    or re.search(r"(?:mailto:|tel:|微信|WeChat|微信号|phone:|E-?mail:|住址|通讯地址)", text, re.I)
                    or re.search(r"\+\d[\d ()-]{8,}\d", text)
                    or re.search(r"(?<!\d)1[3-9]\d{9}(?!\d)", text)
                )
                if suspicious and not (page.number == 0 and line["bbox"][3] <= header_bottom):
                    page.add_redact_annot(fitz.Rect(line["bbox"]), fill=(1, 1, 1))
                    redactions += 1
        page.apply_redactions()
    doc.set_metadata({})
    doc.del_xml_metadata()
    image_count = sum(len(p.get_images()) for p in doc)
    if image_count:
        raise ValueError("存在未审图片/二维码，禁止自动落盘")
    output = DEST / f"{spec['key']}_公开简历_脱敏副本.pdf"
    doc.save(output, garbage=4, deflate=True, clean=True)
    doc.close()
    check = fitz.open(output)
    after = "\n".join(p.get_text() for p in check)
    email_found = bool(re.search(r"[\w.+-]+\s*@\s*[\w.-]+\.[A-Za-z]{2,}", after))
    phone_found = bool(re.search(r"\+\d[\d ()-]{8,}\d|(?<!\d)1[3-9]\d{9}(?!\d)", after))
    missing_modules = [m for m in spec["modules"] if m not in after]
    if email_found or phone_found or missing_modules:
        raise ValueError(f"副本验证失败: {spec['key']}，仅报告类型不输出原联系内容")
    for no, p in enumerate(check):
        p.get_pixmap(matrix=fitz.Matrix(1.2, 1.2), alpha=False).save(QA / f"履历脱敏_{spec['key']}_第{no+1}页.png")
    result = {
        **{k: v for k, v in spec.items() if k not in ["education_marker"]},
        "fixed_pdf_url": fixed,
        "original_sha256": hashlib.sha256(original).hexdigest(),
        "source_status": 200, "original_saved": False,
        "local_path": output.relative_to(ROOT).as_posix(),
        "redacted_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "pages": len(check), "professional_modules_complete": not missing_modules,
        "packaging_type": "公开完整履历的整理者脱敏PDF副本，不是原始未修改文件",
        "redaction": {
            "operations": ["移除首页教育模块之前的个人信息/联系区（含姓名）", "删除所有可点击链接注释以清除隐藏联系方式", "清除原始PDF元数据及XML元数据", "扫描全页邮箱/电话/微信/地址标记", "保留完整教育、经历、项目、论文、技能与专业其他模块（原文件有的全部保留）"],
            "redaction_regions": redactions, "removed_link_annotations": link_count,
            "visible_contact_email_or_phone_after": False, "image_or_qr_count": image_count,
            "visual_review": "待整理者逐页查看渲染图后更新", "visible_url_kinds": "页面原有的专业项目/论文/机构等可见文本可能保留；链接注释已全部移除；原来源/项目URL由JSON列明",
        },
        "outcome_grade": "未披露", "enterprise_verified": False,
        "core_application_engineering_sample": False,
        "full_core_internship_resume_gap_closed": False,
    }
    check.close()
    return result


def main():
    previous = ROOT / "08_证据索引与统计/目标执行_近期履历发现.json"
    if previous.exists():
        existing = json.loads(previous.read_text("utf-8"))
        if existing.get("new_core_complete_profiles") or existing.get("new_core_complete_pdf_profiles"):
            raise SystemExit("已有后续核心履历记录，停止整包重建以免覆盖；可单独调用build_copy。")
    DEST.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    records = [build_copy(s) for s in SPECS]
    partial = {
        "key": "Asthenia0412", "author": "Stochastic / Asthenia0412",
        "url": "https://github.com/Asthenia0412/Asthenia0412/blob/61058d605bbf82efeb0ef451d77d1b049c71a20e/README.md",
        "repo": "Asthenia0412/Asthenia0412", "sha": "61058d605bbf82efeb0ef451d77d1b049c71a20e", "commit_date": "2026-09-26T06:13:24Z",
        "reading": "完整profile README已读；非完整CV", "profile_type": "本人GitHub公开履历片段",
        "track": "后端与Agent应用工程", "recruitment": "实习", "recent_status": "近期确认（作者自述事件时间）",
        "outcomes": [
            {"company": "TikTok LIVE", "role": "Backend Engineer Intern", "time": "2026.09–至今", "evidence_lines": "L50–53", "responsibilities": "直播后台、高并发、基础设施"},
            {"company": "TikTok Monetization", "role": "Backend Engineer Intern", "time": "2026.01–2026.09", "evidence_lines": "L58–61", "responsibilities": "通信基础设施、消息系统、可靠性"},
            {"company": "Anker Innovations", "role": "Backend Engineer Intern", "time": "2025.09–2025.12", "evidence_lines": "L66–69", "responsibilities": "后台服务与AI Agent工程"},
            {"company": "Valiantsec", "role": "Backend Engineer Intern", "time": "2025.06–2025.08", "evidence_lines": "L74–77", "responsibilities": "企业后台系统"},
        ],
        "grade": "未披露", "enterprise_verified": False,
        "skills": ["Go", "Java", "分布式系统", "高并发", "云原生", "AI Infra"],
        "projects": [
            {"name": "AsTimeWheel", "url": "https://github.com/Asthenia0412/AsTimeWheel/tree/b8fb7ddf6dcc90f53c7090ffe1ae245b23f542cc", "sha": "b8fb7ddf6dcc90f53c7090ffe1ae245b23f542cc", "read_scope": "README完整读取、仓库非fork元数据", "relation": "同账号非fork仓库，profile没有点名具体项目", "status": "不可称已核用于求职或由其带来录用", "content": "Java哈希时间轮调度中间件，README宣称单线程调度、延迟任务、重试资源管理；本分支未读实现、未运行"},
        ],
        "missing": ["完整CV（教育和项目模块）", "本人面经", "SSP档位", "求职时项目与个人贡献范围"],
        "access": [{"url": "https://asthenia0412.github.io/", "status": 404, "meaning": "本人profile直接链接的博客当前不可读"}],
        "is_new_core_partial_profile": True, "is_full_resume": False,
    }
    data = {
        "research_date": "2026-10-23", "recent_window": ["2024-10-23", "2026-10-23"],
        "scope": "公开完整CV脱敏研究对照与核心近期后端/Agent实习履历片段；无企业录用独立核验",
        "privacy_method": "未将未脱敏PDF或联系方式写入文件；所有副本与JSON均排除联系信息",
        "complete_redacted_comparison_cvs": records,
        "new_core_partial_profiles": [partial],
        "counts": {"redacted_complete_comparison_pdf_files": 3, "new_core_complete_resume_files": 0, "new_core_partial_profiles": 1, "new_verified_ssp": 0},
        "search_method": "Web搜索中英求职/个人主页/履历PDF关键词，追作者GitHub主页和固定提交；不因同账号仓库认定求职项目",
        "remaining_gap": "核心后端/Agent应用工程完整近期成功实习履历仍待补；这三份博士/研究/Infra履历有专业完整性，但不偷换为核心样本",
    }
    out = ROOT / "08_证据索引与统计/目标执行_近期履历发现.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(out), "copies": [r["local_path"] for r in records], "counts": data["counts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
