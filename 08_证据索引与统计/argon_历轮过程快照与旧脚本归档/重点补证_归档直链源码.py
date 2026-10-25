"""固定公开源码ZIP仅在内存读取，输出经联系字段清理的源码文本派生包，不运行源码。"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path, PurePosixPath
import hashlib
import io
import json
import re
import warnings
import zipfile

import requests

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "05_项目源码归档/大厂履历直接关联_重点补证"
DISCOVERY = ROOT / "08_证据索引与统计/重点补证_大厂实习履历.json"
EMAIL = re.compile(r"[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<![\w])(?:\+86[- ]?)?1[3-9]\d{9}(?!\w)")
TOKEN = re.compile(r"\b(?:sk-proj-|sk-|ghp_|github_pat_|xox[baprs]-|AIza)[A-Za-z0-9_-]{20,}|\bAKIA[0-9A-Z]{16}")
PRIVATE_KEY = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\r\n]+[A-Za-z0-9+/=]{20,}")
SPECS = [
    {"name": "Distributed-Key-Value-Store", "repo": "shufengc/distributed-kv-store", "sha": "d7132bba33fb2aec2ccd802c357dc1cd1f74fb5e", "license": "Apache-2.0原文已读并原样保留；包含TinyKV继承框架，不能把全包认定为个人原创", "category": "TinyKV课程框架上的进阶系统实现，未运行测试"},
    {"name": "QuantHarbor", "repo": "shufengc/QuantHarbor", "sha": "f0d6380e9846f84f10be5f284fec40d42cfb34f9", "license": "GNU GPL version 3原文已读并原样保留", "category": "Agent风险/反例选读，导入路径缺口与代码执行权限边界未解决，未称成熟可复现Agent"},
]


def collect(spec):
    url = f"https://codeload.github.com/{spec['repo']}/zip/{spec['sha']}"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=90)
    r.raise_for_status()
    original = r.content
    source = zipfile.ZipFile(io.BytesIO(original))
    assert source.testzip() is None
    kept = []
    omitted = []
    modified = []
    raw_license = None
    for member in source.infolist():
        if member.is_dir():
            continue
        parts = PurePosixPath(member.filename).parts
        assert not member.filename.startswith(("/", "\\")) and ".." not in parts
        p = "/".join(parts[1:])
        if not p:
            continue
        if re.search(r"(^|/)(\.env(?:\.[^/]*)?|id_rsa|credentials[^/]*)$", p, re.I) and not re.search(r"example|sample|template", p, re.I):
            omitted.append({"path": p, "reason": "非示例环境或凭据文件，不落盘"})
            continue
        if PurePosixPath(p).suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".pdf", ".docx", ".mp4", ".npy", ".pkl", ".dill", ".zip", ".jar"}:
            omitted.append({"path": p, "reason": "媒体/二进制/缓存数据不纳入源码文本包，未下载依赖/模型/外部数据"})
            continue
        b = source.read(member)
        try:
            text = b.decode("utf-8")
        except UnicodeDecodeError:
            omitted.append({"path": p, "reason": "非UTF-8二进制，不纳入源码文本包"})
            continue
        if TOKEN.search(text) or PRIVATE_KEY.search(text):
            omitted.append({"path": p, "reason": "检测到疑似凭据签名，整文件不落盘；不保存原值"})
            continue
        if p == "LICENSE":
            raw_license = b
        counter = [0]
        def clean_email(m):
            if m.group() == "git@github.com":
                return m.group()
            counter[0] += 1
            return "redacted_" + hashlib.sha256(m.group().encode()).hexdigest()[:10] + "@example.invalid"
        clean = EMAIL.sub(clean_email, text)
        phones = len(PHONE.findall(clean))
        clean = PHONE.sub("REDACTED_PHONE", clean)
        if counter[0] or phones:
            modified.append({"path": p, "email_pattern_replacements": counter[0], "phone_pattern_replacements": phones, "scope": "涵盖开发者署名和测试合成邮件等全部邮箱模式；不记录原始值"})
        kept.append((p, clean.encode("utf-8")))
    assert raw_license is not None
    assert dict(kept)["LICENSE"] == raw_license
    note = {
        **spec, "source_url": url, "source_http_status": r.status_code,
        "original_archive_sha256": hashlib.sha256(original).hexdigest(),
        "original_archive_bytes": len(original), "original_archive_members": len(source.infolist()),
        "original_crc": "全部成员通过CRC", "original_saved": False,
        "archive_type": "固定提交的源码文本派生归档，去联系字段并省略媒体/二进制；不是未经修改的完整原ZIP",
        "execution": "未运行、未构建、未安装依赖、未调用模型/API",
        "license_sha256": hashlib.sha256(raw_license).hexdigest(), "license_unchanged": True,
        "retained_text_members": len(kept), "omitted_members": omitted, "modified_text_members": modified,
        "credential_scan": "UTF-8文本扫描常见API令牌/私钥正文签名；疑似命中文件整文件排除。扫描不等于完整安全审计。非示例环境/凭据文件不纳入。",
        "contact_scan": "除GitHub SSH服务git@github.com外，全部邮箱样式转唯一example.invalid占位；手机号模式替换。原始未脱敏ZIP不落盘。",
        "functional_limit": "继承课程/框架边界及静态风险见发现JSON；联系字段替换及媒体/二进制省略可能影响可构建性，未验证可运行。复现须自行核对固定上游原版。",
    }
    memory = io.BytesIO()
    with zipfile.ZipFile(memory, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as target:
        prefix = f"{spec['name']}-{spec['sha']}/"
        for p, b in sorted(kept):
            zi = zipfile.ZipInfo(prefix + p, date_time=(2026, 10, 23, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            target.writestr(zi, b)
        target.writestr(prefix + "调研归档说明_非原始完整ZIP.json", json.dumps(note, ensure_ascii=False, indent=2).encode("utf-8"))
    result_bytes = memory.getvalue()
    check = zipfile.ZipFile(io.BytesIO(result_bytes))
    assert check.testzip() is None
    assert check.read(next(n for n in check.namelist() if n.endswith("/LICENSE"))) == raw_license
    for member in check.namelist():
        text = check.read(member).decode("utf-8")
        assert all(m.group() == "git@github.com" or m.group().endswith("@example.invalid") for m in EMAIL.finditer(text))
        assert not PHONE.search(text)
        assert not TOKEN.search(text)
        assert not PRIVATE_KEY.search(text)
    DEST.mkdir(parents=True, exist_ok=True)
    output = DEST / f"{spec['name']}_固定源码文本_去联系字段_{spec['sha'][:10]}.zip"
    if output.exists():
        raise RuntimeError("归档已存在，停止覆盖")
    output.write_bytes(result_bytes)
    return {**note, "local_path": output.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(result_bytes).hexdigest(),
            "bytes": len(result_bytes), "members": len(check.infolist()), "crc": "全部成员通过CRC", "post_archive_privacy_scan": "通过：无原始邮箱/手机号模式、无所扫描凭据签名；元数据固定且无原始ZIP信息"}


def main():
    current = json.loads(DISCOVERY.read_text("utf-8"))
    if current.get("archives"):
        raise RuntimeError("已有归档记录，停止覆盖")
    with ThreadPoolExecutor(max_workers=2) as pool:
        records = list(pool.map(collect, SPECS))
    # 在网络工作后重读，保留其他整理者可能已经写入的字段。
    current = json.loads(DISCOVERY.read_text("utf-8"))
    current["archives"] = records
    current["counts"]["new_derived_text_source_archives"] = len(records)
    current["archive_status"] = "两个项目均已归档固定源码文本去联系字段派生副本；不是未经修改完整原ZIP；未运行"
    for profile in current["new_core_partial_profiles"]:
        for project in profile["projects"]:
            for a in records:
                if project.get("repo") == a["repo"]:
                    project["attachment"] = a
    DISCOVERY.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps([{"repo": a["repo"], "path": a["local_path"], "bytes": a["bytes"], "members": a["members"], "omitted": len(a["omitted_members"]), "modified": len(a["modified_text_members"]), "crc": a["crc"]} for a in records], ensure_ascii=False))


if __name__ == "__main__":
    main()
