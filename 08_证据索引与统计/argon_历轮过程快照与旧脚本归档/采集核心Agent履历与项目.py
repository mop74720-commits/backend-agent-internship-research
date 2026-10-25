"""公开应用工程实习CV脱敏及本人项目文档核读，未下载或运行企业源码。"""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import warnings

import fitz
import requests

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
SHA = "6b8add7398dcbf1f79fd4c850b0c0b047344bc4d"
BASE = f"https://raw.githubusercontent.com/huomalxq/huomalxq.github.io/{SHA}/"


def main():
    specmod = importlib.util.spec_from_file_location("redacted_cv_utils", ROOT / "08_证据索引与统计/采集近期履历_脱敏副本.py")
    mod = importlib.util.module_from_spec(specmod)
    specmod.loader.exec_module(mod)
    mod.DEST = ROOT / "03_简历与候选人案例/核心Agent履历_脱敏副本"
    mod.DEST.mkdir(parents=True, exist_ok=True)
    spec = {
        "key": "huomalxq", "author": "林祥庆 / Huoma LXQ", "track": "Agent应用工程",
        "home": "https://huomalxq.github.io/resume/", "live_pdf": "https://huomalxq.github.io/assets/files/resume.pdf",
        "repo": "huomalxq/huomalxq.github.io", "sha": SHA, "path": "docs/assets/files/resume.pdf",
        "commit_date": "2026-06-15T06:03:59Z", "education_marker": "教育经历",
        "modules": ["教育经历", "项目/科研经历", "实习经历", "获奖情况"],
        "outcomes": [
            {"company": "Philips", "role": "Agent开发实习生（苏州）", "time": "2026.03–2026.05", "basis": "本人公开PDF和HTML均明确职位与时间；均无企业独立核验"},
            {"company": "上海诺基亚贝尔", "role": "后端开发/数据清洗实习生（杭州）", "time": "2023.09–2024.01", "basis": "本人PDF/HTML，历史经历不计近期"},
        ],
        "analysis": "硕士公开完整单页CV，近期Philips Agent应用工程实习对应LangGraph问数链路，职责具体到表结构检索、SQL校验与重试、耗时测试；履历指标为自述。Philips为跨国企业，不将其写成中国互联网大厂SSP。",
        "projects": [
            {"name": "自然语言问数/数据分析Agent后端", "url": "https://huomalxq.github.io/study/data-analysis-agent/", "relation": "简历直接写Philips问数Agent职责，主页Internship卡片和本人后端复盘呼应；复盘正文未写公司名", "caveat": "无公开实现源码，本材料只能审职责与设计说明，不能称源码验证"},
            {"name": "Teco-RAG竞赛", "url": "https://huomalxq.github.io/study/teco-rag-project-summary/", "relation": "CV获奖和本人站学习记录直接列出", "caveat": "本分支未核竞赛官网，不将自述结果叫企业认证"},
        ],
        "limits": ["未披露SSP", "没有本人求职面经", "企业Agent项目没有公开源码", "文中性能/召回指标未经本地复现", "完整CV是实习之后公开版，不等于当时投递版", "后训练科研项目不等于实习岗位全部要求"],
    }
    row = mod.build_copy(spec)
    local = ROOT / row["local_path"]
    original = requests.get(row["fixed_pdf_url"], timeout=40).content
    a = fitz.open(stream=original, filetype="pdf")
    before = "\n".join(p.get_text() for p in a)
    b = fitz.open(local)
    after = "\n".join(p.get_text() for p in b)
    normalize = lambda v: re.sub(r"\s+", "", v[v.index("教育经历"):])
    assert normalize(before) == normalize(after)
    assert not [k for k, v in b.metadata.items() if k != "format" and v]
    row.update({
        "core_application_engineering_sample": True, "is_full_public_profile": True,
        "complete_as_published": True, "resume_file_format": "PDF", "source_role_scope": "非中国互联网大厂，Philips应用工程实习",
        "recruitment": "实习", "recent_status": "近期确认（作者自述）", "enterprise_verified": False,
        "full_core_internship_resume_gap_closed": False,
        "specific_progress": "新增1份Agent应用工程成功实习完整公开CV；中国互联网大厂Agent SSP完整链仍未闭合",
    })
    row["redaction"].update({"professional_body_text_identical_after_header_removal": True, "page_link_annotations_after": sum(len(p.get_links()) for p in b), "nonformat_metadata_fields_after": [], "visual_review": "待查看单页渲染"})
    a.close(); b.close()
    # 将无联系信息的本人项目复盘附在项目材料中，明确它不包含实现源码。
    project_url = BASE + "docs/study/data-analysis-agent.md"
    response = requests.get(project_url, timeout=40)
    response.raise_for_status()
    text = response.text
    assert not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?<!\d)1[3-9]\d{9}(?!\d)", text)
    folder = ROOT / "06_项目分析与推荐/补充本人项目材料"
    folder.mkdir(parents=True, exist_ok=True)
    note = (
        "资料类型：本人项目复盘全文（非源码包）；仅静态读文，未运行。\n\n"
        "作者：林祥庆 / huomalxq。原页：https://huomalxq.github.io/study/data-analysis-agent/\n\n"
        f"固定源文件：{project_url}\n\n"
        "边界：简历直接写Philips问数Agent实习职责，本复盘未写公司名；按本人专业经历补充阅读，不能冒称已审企业实现代码。\n\n---\n\n"
    )
    project_path = folder / "huomalxq_数据分析Agent后端_本人复盘.md"
    project_path.write_text(note + text, encoding="utf-8")
    project = {
        "name": "数据分析Agent后端", "author": "林祥庆 / huomalxq", "source_url": project_url,
        "sha": SHA, "local_path": project_path.relative_to(ROOT).as_posix(), "source_sha256": hashlib.sha256(response.content).hexdigest(),
        "source_kind": "本人技术复盘，非公开实现源码", "reading": "113行全文已读", "run_status": "未运行",
        "relationship_to_internship": "简历直接标注Philips自然语言问数职责，主页Internship卡片和复盘领域相同；复盘未写公司名，不把未公开源码或全部系统归为已验证贡献",
        "declared_stack": ["FastAPI", "LangGraph", "vLLM", "Ollama embedding", "Milvus", "Vertica", "PostgreSQL"],
        "declared_modules": ["意图识别", "实体/表结构/字典多路检索", "SQL生成", "小样本校验与至多3次重试", "查询执行及超时", "结果分析与图表配置", "召回/耗时测试脚本"],
        "state": "文档宣称，无法源码核对",
        "strengths": ["职责和业务链路具体，超出单次模型API调用", "把失败类型分解为schema召回、SQL方言、执行代价和图表解析", "先测召回和节点耗时，再对整体改进作解释"],
        "limitations_from_author": ["明文配置待迁移到环境变量或密钥管理", "绝对路径待改相对路径", "内存checkpoint拟换Redis以支持重启恢复", "更严格SQL parser校验待做", "标准评测集待建立", "缓存优化待做"],
        "static_review": "作者明确列出SQL parser更严格安全校验、状态持久化和标准评测集待完善；文档描述prompt SELECT约束、正则和LIMIT，未提供租户授权或数据库权限隔离实现证据。无法据此认定已实现严格SQL授权/租户隔离；该判断基于文档，不是源码审计。",
        "recommended_modules": ["L9–20本人职责", "L49–79失败处理", "L90–98指标定义", "L106–113作者自列未完成项"],
        "metrics_boundary": "CV写61.4%→81.6%召回、50s→30s响应；复盘列后续应跟踪指标，无数据集/硬件/误差区间，不当已复现实验",
        "offer_grade": "未披露，不是SSP证据",
    }
    index = ROOT / "08_证据索引与统计/目标执行_近期履历发现.json"
    data = json.loads(index.read_text("utf-8"))
    data["new_core_complete_pdf_profiles"] = [row]
    data["new_core_authored_project_materials"] = [project]
    data["counts"].update({"new_core_complete_pdf_files": 1, "new_core_complete_resume_files": 2, "new_core_authored_project_materials": 1})
    data["remaining_gap"] = "已新增近期Go后端完整公开HTML履历1份和Agent应用工程公开完整PDF脱敏副本1份；后者为Philips，未披露SSP，无企业源码和本人面经。中国互联网大厂近期Agent SSP完整链仍未闭合。"
    index.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"profile": row["key"], "local_pdf": row["local_path"], "project": project["local_path"], "counts": data["counts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
