"""备份后归档旧轮次及逐条底稿；不删除附件，不改外部来源目录。"""
from pathlib import Path
import hashlib
import json
import zipfile
import os

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / '08_证据索引与统计'
MANIFEST = BASE / '可读性整理_路径映射.json'


def safe(path):
    resolved = path.resolve()
    if not resolved.is_relative_to(ROOT.resolve()) or resolved == ROOT.resolve():
        raise ValueError('越出任务资料目录：' + str(path))
    return resolved


def main():
    if MANIFEST.exists():
        print('已整理；保留现有映射，不重复移动。')
        return
    mapping = {}

    def add(source, target):
        safe(source); safe(target)
        if target.exists():
            raise FileExistsError(target)
        mapping[source.relative_to(ROOT).as_posix()] = target.relative_to(ROOT).as_posix()

    report = ROOT / '01_调研报告'
    for p in report.iterdir():
        if not p.is_file() or p.name == '待手动访问链接.html':
            continue
        if p.name == '需求核对与阅读优先级.html':
            add(p, report/'资料检索与证据详表.html')
        else:
            add(p, report/'历史报告'/p.name)
    for p in ROOT.glob('00_*.md'):
        add(p, BASE/'历史更新说明'/p.name)
    for dirname, subfolder, pattern in [
        ('02_招聘岗位资料','逐条岗位资料','*.txt'),
        ('03_简历与候选人案例','逐条分析底稿','*.txt'),
        ('04_面经与专业观点','逐条面经与观点','*.txt'),
        ('06_项目分析与推荐','逐项分析底稿','PRO*.txt')]:
        folder = ROOT/dirname
        for p in folder.glob(pattern):
            add(p, folder/subfolder/p.name)
    for name in ['待手动访问链接.md', '百度Agent日常实习_15问与阅读边界.md']:
        p=ROOT/'04_面经与专业观点'/name
        if p.exists(): add(p,p.parent/'逐条面经与观点'/p.name)
    p=ROOT/'06_项目分析与推荐/19项目统一比较.csv'
    if p.exists(): add(p,p.parent/'逐项分析底稿'/p.name)
    # 快照覆盖将移动/改写的读者文件；源码和实际简历附件原地保留。
    snapshot_files = set(ROOT.glob('00_*.*'))
    for dirname in ['01_调研报告','02_招聘岗位资料','03_简历与候选人案例','04_面经与专业观点','06_项目分析与推荐']:
        snapshot_files.update(p for p in (ROOT/dirname).glob('*') if p.is_file())
    backup=ROOT.parent/'可读性整理前快照_20261024.zip'
    if backup.exists(): raise FileExistsError(backup)
    fingerprints=[]
    with zipfile.ZipFile(backup,'x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(snapshot_files):
            safe(p)
            relative=p.relative_to(ROOT).as_posix()
            z.write(p,relative)
            fingerprints.append({'path':relative,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    record={'backup_path':str(backup),'moves':mapping,'before_files':fingerprints,
            'note':'文件只归档，不删资料。链接在后续独立步骤按原位置重写；外部astra目录未操作。'}
    # 先写映射；若中断可据此核查源/目标，禁止盲目覆盖重跑。
    MANIFEST.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    for old,new in mapping.items():
        src=safe(ROOT/old); dst=safe(ROOT/new)
        dst.parent.mkdir(parents=True,exist_ok=True)
        os.rename(src,dst)
    print(json.dumps({'backup':str(backup),'archived_or_renamed':len(mapping)},ensure_ascii=False))


if __name__=='__main__':
    main()
