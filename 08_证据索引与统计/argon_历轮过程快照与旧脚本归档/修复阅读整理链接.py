"""根据原位置修复归档后的本地HTML/Markdown链接，一次性执行。"""
from pathlib import Path
from urllib.parse import urlsplit, unquote, quote
from html import unescape, escape
import json
import os
import re

ROOT = Path(__file__).resolve().parent.parent
BASE=ROOT/'08_证据索引与统计'
MAPPING=json.loads((BASE/'可读性整理_路径映射.json').read_text(encoding='utf-8'))['moves']
INVERSE={v:k for k,v in MAPPING.items()}
LOG=BASE/'可读性整理_链接修复.json'
OLD_INDEX='01_调研报告/index.html'
DETAIL='01_调研报告/资料检索与证据详表.html'


def main():
    if LOG.exists():
        print('已按原位置修复，不重复套用原路径。'); return
    changed=[]
    for current in ROOT.rglob('*'):
        if not current.is_file() or current.suffix.lower() not in ['.html','.md']:
            continue
        # 源码包展开材料/外部来源快照维持原样。
        if current.parts[len(ROOT.parts)] in ['05_项目源码归档','07_个人项目设计_暂缓']:
            continue
        path=current.relative_to(ROOT).as_posix()
        original=ROOT/INVERSE.get(path,path)
        before=current.read_text(encoding='utf-8-sig')
        def update(value):
            raw=unescape(value); u=urlsplit(raw)
            if not raw or raw.startswith('#') or (u.scheme and u.scheme!='file') or u.netloc:
                return value
            if not u.path: return value
            decoded=unquote(u.path).replace('\\','/')
            if u.scheme=='file':
                decoded=decoded.lstrip('/')
                target=Path(decoded)
            else:
                target=original.parent/decoded
            target=target.resolve()
            if not target.is_relative_to(ROOT.resolve()): return value
            old=target.relative_to(ROOT).as_posix()
            if old==OLD_INDEX and u.fragment:
                new=DETAIL
            elif old==OLD_INDEX:
                new='01_调研报告/实习求职调研总报告.html'
            else:
                new=MAPPING.get(old,old)
            if new==old and original.parent==current.parent:
                return value
            relative=Path(os.path.relpath(ROOT/new,current.parent)).as_posix()
            return escape(relative+('?' + u.query if u.query else '')+('#'+u.fragment if u.fragment else ''),quote=True)
        after=re.sub(r'(?P<prefix>\b(?:href|src)\s*=\s*)(?P<q>[\"\x27])(?P<url>.*?)(?P=q)',
            lambda m:m['prefix']+m['q']+update(m['url'])+m['q'],before,flags=re.I)
        if current.suffix.lower()=='.md':
            after=re.sub(r'(?P<start>\]\()(?P<url>[^\s)]+)(?P<end>\))',lambda m:m['start']+update(m['url'])+m['end'],after)
        if after!=before:
            # 保留原有CRLF/LF。
            newline='\r\n' if b'\r\n' in current.read_bytes() else '\n'
            with current.open('w',encoding='utf-8',newline=newline) as f:f.write(after)
            changed.append(path)
    LOG.write_text(json.dumps({'changed_files':changed,'count':len(changed),'note':'按移动前位置解析，仅执行一次；后续新生成页使用新路径。'},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'rewritten_files':len(changed)},ensure_ascii=False))


if __name__=='__main__':main()
