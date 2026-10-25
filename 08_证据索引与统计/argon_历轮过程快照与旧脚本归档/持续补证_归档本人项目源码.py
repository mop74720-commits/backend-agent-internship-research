"""内存核查公开源ZIP；只写去联系字段的源码文本归档，不执行源码。"""
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
DEST = ROOT / "05_项目源码归档/本人履历直接关联_持续补证"
EMAIL = re.compile(r"[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<![\w])(?:\+86[- ]?)?1[3-9]\d{9}(?!\w)")
TOKEN = re.compile(r"\b(?:sk-proj-|sk-|ghp_|github_pat_|xox[baprs]-|AIza)[A-Za-z0-9_-]{20,}|\bAKIA[0-9A-Z]{16}")
SPECS = [("UltiCode", "d53b582e2fae32ef644642651086df0e5ed3163d"), ("ResiCache", "1ed3be36af0795a363d624d38de676c0d00b4cf7")]


def download(spec):
    name, sha = spec
    url = f"https://codeload.github.com/DavidHLP/{name}/zip/{sha}"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=90)
    r.raise_for_status()
    return name, sha, url, r.content


def archive(item):
    name, sha, url, original = item
    src = zipfile.ZipFile(io.BytesIO(original))
    assert src.testzip() is None
    omitted = []
    modifications = []
    service_git_matches = 0
    source_text_count = 0
    retained = []
    for member in src.infolist():
        if member.is_dir():
            continue
        assert not member.filename.startswith(("/", "\\")) and ".." not in PurePosixPath(member.filename).parts
        path = "/".join(PurePosixPath(member.filename).parts[1:])
        if not path:
            continue
        if re.search(r"(^|/)(\.env(?:\.[^/]*)?|id_rsa|credentials[^/]*)$", path, re.I) and not re.search(r"(?:example|sample|template)", path, re.I):
            omitted.append({"path": path, "reason": "非示例环境/凭据文件，不写入归档"})
            continue
        content = src.read(member)
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            omitted.append({"path": path, "reason": "二进制图像/图标未纳入文本源码包，避免未经逐图审查的信息"})
            continue
        source_text_count += 1
        if TOKEN.search(text):
            raise ValueError(f"疑似凭据签名，未落原包且停止该项目归档：{name}")
        if re.search(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\r\n]+[A-Za-z0-9+/=]{20,}", text):
            raise ValueError(f"疑似私钥正文，未落原包且停止该项目归档：{name}")
        email_count = 0
        def redact_email(match):
            nonlocal email_count, service_git_matches
            value = match.group()
            if value == "git@github.com":
                service_git_matches += 1
                return value  # GitHub SSH服务语法，不是个人联系方式。
            email_count += 1
            key = hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]
            return f"redacted_{key}@example.invalid"
        cleaned = EMAIL.sub(redact_email, text)
        phone_count = len(PHONE.findall(cleaned))
        cleaned = PHONE.sub("REDACTED_PHONE", cleaned)
        if email_count or phone_count:
            modifications.append({"path": path, "email_pattern_replacements": email_count, "phone_pattern_replacements": phone_count, "note": "包括开发者元数据及合成测试邮件等全部邮箱样式；仅记录数量，不记录原值"})
        retained.append((path, cleaned.encode("utf-8")))
    note = {
        "project": name, "source_repo": f"DavidHLP/{name}", "commit": sha,
        "source_archive_url": url, "source_archive_sha256": hashlib.sha256(original).hexdigest(),
        "source_archive_bytes": len(original), "source_archive_crc": "全部成员通过CRC",
        "archive_type": "固定提交的源码文本归档（去联系字段），不是未经修改的完整原ZIP",
        "execution": "未运行、未构建、未安装依赖",
        "retained_text_members": len(retained), "omitted_members": omitted,
        "modified_text_members": modifications,
        "contact_policy": "GitHub SSH服务git@github.com保留；其余邮箱样式均转唯一example.invalid占位；手机号样式去除；不保存原始未脱敏ZIP",
        "credential_scan": "全部UTF-8文本扫描常见API令牌/私钥正文签名；未发现。RsaKeyMaterial中的PEM头去除字符串是解析代码，不是私钥正文。非示例.env/凭据文件不纳入包。扫描不等于完整安全审计。",
        "functional_limit": "内容有联系字段替换、UltiCode前端图片/图标省略；测试邮件可能变化，未验证可构建性。复现实验应自行核对固定上游原版，不能把本包当已通过测试的原始发行物。",
        "license": "保留上游LICENSE原文；UltiCode标准MIT，ResiCache为MIT标题及许可/免责声明的原有短文本。",
    }
    DEST.mkdir(parents=True, exist_ok=True)
    target = DEST / f"{name}_固定源码文本_去联系字段_{sha[:10]}.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as out:
        prefix = f"{name}-{sha}/"
        for path, content in sorted(retained):
            zi = zipfile.ZipInfo(prefix + path, date_time=(2026, 10, 23, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            out.writestr(zi, content)
        out.writestr(prefix + "调研归档说明_非原始完整ZIP.json", json.dumps(note, ensure_ascii=False, indent=2).encode("utf-8"))
    check = zipfile.ZipFile(target)
    assert check.testzip() is None
    assert any(n.endswith("/LICENSE") for n in check.namelist())
    for filename in check.namelist():
        t = check.read(filename).decode("utf-8")
        assert all(m.group() == "git@github.com" or m.group().endswith("@example.invalid") for m in EMAIL.finditer(t))
        assert not PHONE.search(t)
        assert not TOKEN.search(t)
    return {
        **note, "local_path": target.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "bytes": target.stat().st_size, "members": len(check.infolist()), "crc_result": "全部成员通过CRC",
        "post_archive_contact_scan": "所有文本仅保留GitHub SSH服务语法和example.invalid占位，无原始邮件/手机号样式",
    }


def main():
    with ThreadPoolExecutor(max_workers=2) as pool:
        downloaded = list(pool.map(download, SPECS))
    archives = [archive(x) for x in downloaded]
    p = ROOT / "08_证据索引与统计/持续补证_实习履历与本人源码.json"
    data = json.loads(p.read_text("utf-8"))
    data["source_archives"] = archives
    for project in data["projects"]:
        project["attachment"] = next(a for a in archives if a["project"] == project["name"])
        project["archive_status"] = "已归档固定源码文本去联系字段副本；不是原始完整ZIP，未运行"
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps([{"project": a["project"], "local_path": a["local_path"], "bytes": a["bytes"], "members": a["members"], "modified_files": len(a["modified_text_members"]), "omitted_files": len(a["omitted_members"]), "crc": a["crc_result"]} for a in archives], ensure_ascii=False))


if __name__ == "__main__":
    main()
