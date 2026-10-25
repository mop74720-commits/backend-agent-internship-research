"""将本次新建与修改的文件原地重命名为 argon_ 前缀，并同步更新全站引用链接。"""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from html import unescape, escape
import json
import os
import re

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent

RENAME_MAP = {
    'README.md': 'argon_README.md',
    '00_START_HERE.txt': 'argon_00_START_HERE.txt',
    '00_开始阅读.html': 'argon_00_开始阅读.html',
    '01_调研报告/实习求职调研总报告.html': '01_调研报告/argon_实习求职调研总报告.html',
    '01_调研报告/index.html': '01_调研报告/argon_index.html',
    '01_调研报告/实习求职调研总报告.pdf': '01_调研报告/argon_实习求职调研总报告.pdf',
    '01_调研报告/资料检索与证据详表.html': '01_调研报告/argon_资料检索与证据详表.html',
    '01_调研报告/待手动访问链接.html': '01_调研报告/argon_待手动访问链接.html',
    '02_招聘岗位资料/岗位要求统计与解读.html': '02_招聘岗位资料/argon_岗位要求统计与解读.html',
    '02_招聘岗位资料/岗位要求统计与解读.md': '02_招聘岗位资料/argon_岗位要求统计与解读.md',
    '02_招聘岗位资料/岗位统计_后端.svg': '02_招聘岗位资料/argon_岗位统计_后端.svg',
    '02_招聘岗位资料/岗位统计_Agent.svg': '02_招聘岗位资料/argon_岗位统计_Agent.svg',
    '02_招聘岗位资料/岗位统计_公司敏感性.svg': '02_招聘岗位资料/argon_岗位统计_公司敏感性.svg',
    '02_招聘岗位资料/技术项逐JD编码.csv': '02_招聘岗位资料/argon_技术项逐JD编码.csv',
    '03_简历与候选人案例/候选人与简历图册.html': '03_简历与候选人案例/argon_候选人与简历图册.html',
    '04_面经与专业观点/面经重点与项目追问.html': '04_面经与专业观点/argon_面经重点与项目追问.html',
    '04_面经与专业观点/面经重点与项目追问.md': '04_面经与专业观点/argon_面经重点与项目追问.md',
    '06_项目分析与推荐/项目比较与精读指南.html': '06_项目分析与推荐/argon_项目比较与精读指南.html',
    '06_项目分析与推荐/后端实习阅读顺序.md': '06_项目分析与推荐/argon_后端实习阅读顺序.md',
    '06_项目分析与推荐/Agent实习阅读顺序.md': '06_项目分析与推荐/argon_Agent实习阅读顺序.md',
    '06_项目分析与推荐/技术要求_明确要求与加分项.md': '06_项目分析与推荐/argon_技术要求_明确要求与加分项.md',
    '06_项目分析与推荐/专业观点交叉核对_评测与工具恢复.md': '06_项目分析与推荐/argon_专业观点交叉核对_评测与工具恢复.md',
    '06_项目分析与推荐/外部调研_文档判断与阅读模块.md': '06_项目分析与推荐/argon_外部调研_文档判断与阅读模块.md',
    '08_证据索引与统计/生成可读调研总报告.py': '08_证据索引与统计/argon_生成可读调研总报告.py',
    '08_证据索引与统计/生成岗位统计_可读版.py': '08_证据索引与统计/argon_生成岗位统计_可读版.py',
    '08_证据索引与统计/整理简历视觉材料.py': '08_证据索引与统计/argon_整理简历视觉材料.py',
    '08_证据索引与统计/导出重点报告.cjs': '08_证据索引与统计/argon_导出重点报告.cjs',
    '08_证据索引与统计/校验可读性整理.py': '08_证据索引与统计/argon_校验可读性整理.py',
    '08_证据索引与统计/可读性整理_报告生成统计.json': '08_证据索引与统计/argon_可读性整理_报告生成统计.json',
    '08_证据索引与统计/岗位统计_可读版.json': '08_证据索引与统计/argon_岗位统计_可读版.json',
    '08_证据索引与统计/可读性整理_浏览器校验.json': '08_证据索引与统计/argon_可读性整理_浏览器校验.json',
    '08_证据索引与统计/可读性整理_交付校验.json': '08_证据索引与统计/argon_可读性整理_交付校验.json',
}


def main():
    # 1. 原地重命名文件
    for old_rel, new_rel in RENAME_MAP.items():
        old_p = ROOT / old_rel
        new_p = ROOT / new_rel
        if old_p.exists():
            if new_p.exists():
                new_p.unlink()
            old_p.rename(new_p)

    # 2. 同步更新 可读性整理_路径映射.json
    map_file = BASE / '可读性整理_路径映射.json'
    if map_file.exists():
        mp = json.loads(map_file.read_text('utf-8-sig'))
        for k, v in list(mp.get('moves', {}).items()):
            if v in RENAME_MAP:
                mp['moves'][k] = RENAME_MAP[v]
        map_file.write_text(json.dumps(mp, ensure_ascii=False, indent=2), encoding='utf-8')

    # 3. 同步更新 简历视觉材料_整理清单.json 中的 atlas_file 字段
    vis_file = BASE / '简历视觉材料_整理清单.json'
    if vis_file.exists():
        vis = json.loads(vis_file.read_text('utf-8-sig'))
        if vis.get('atlas_file') in RENAME_MAP:
            vis['atlas_file'] = RENAME_MAP[vis['atlas_file']]
            vis_file.write_text(json.dumps(vis, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    # 4. 更新生成与校验脚本中的文件名引用
    basename_map = {Path(k).name: Path(v).name for k, v in RENAME_MAP.items()}
    for script_rel in [
        '08_证据索引与统计/argon_生成可读调研总报告.py',
        '08_证据索引与统计/argon_生成岗位统计_可读版.py',
        '08_证据索引与统计/argon_整理简历视觉材料.py',
        '08_证据索引与统计/argon_导出重点报告.cjs',
        '08_证据索引与统计/argon_校验可读性整理.py',
    ]:
        sp = ROOT / script_rel
        if not sp.exists():
            continue
        txt = sp.read_text('utf-8')
        txt = txt.replace("TITLE = '实习求职调研总报告'", "TITLE = 'argon_实习求职调研总报告'")
        for old_b, new_b in sorted(basename_map.items(), key=lambda x: -len(x[0])):
            txt = txt.replace(old_b, new_b)
        while 'argon_argon_' in txt:
            txt = txt.replace('argon_argon_', 'argon_')
        sp.write_text(txt, encoding='utf-8')

    # 5. 更新全站 HTML 与 Markdown 文件中指向已重命名文件的相对链接
    updated_files = 0
    for p in ROOT.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in ['.html', '.md']:
            continue
        if p.relative_to(ROOT).parts[0] in ['05_项目源码归档', '07_个人项目设计_暂缓']:
            continue
        before = p.read_text('utf-8-sig')

        def fix_url(val):
            raw = unescape(val)
            u = urlsplit(raw)
            if not raw or raw.startswith('#') or u.scheme or u.netloc or not u.path:
                return val
            target = (p.parent / unquote(u.path)).resolve()
            if not target.is_relative_to(ROOT.resolve()):
                return val
            rel_old = target.relative_to(ROOT).as_posix()
            if rel_old in RENAME_MAP:
                rel_new = RENAME_MAP[rel_old]
                new_rel_path = Path(os.path.relpath(ROOT / rel_new, p.parent)).as_posix()
                res = new_rel_path + ('?' + u.query if u.query else '') + ('#' + u.fragment if u.fragment else '')
                return escape(res, quote=True) if p.suffix.lower() == '.html' else res
            return val

        after = re.sub(
            r'(?P<prefix>\b(?:href|src)\s*=\s*)(?P<q>["\'])(?P<url>.*?)(?P=q)',
            lambda m: m['prefix'] + m['q'] + fix_url(m['url']) + m['q'],
            before,
            flags=re.I
        )
        if p.suffix.lower() == '.md':
            after = re.sub(
                r'(?P<start>\]\()(?P<url>[^\s)]+)(?P<end>\))',
                lambda m: m['start'] + fix_url(m['url']) + m['end'],
                after
            )
        if after != before:
            p.write_text(after, encoding='utf-8')
            updated_files += 1

    print(json.dumps({'renamed': len(RENAME_MAP), 'updated_link_files': updated_files}, ensure_ascii=False))


if __name__ == '__main__':
    main()
