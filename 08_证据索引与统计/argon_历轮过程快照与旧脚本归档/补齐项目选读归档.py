"""合入三份明确选读附件；只读ZIP，不运行第三方源码。"""
from pathlib import Path
from copy import deepcopy
import hashlib
import json
import re
import zipfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
SOURCES = ['Hello_Agents_选读归档补齐.json', 'Crony_选读归档补齐.json', '项目选读归档补齐.json']


def apply(rows, comparison):
    if not all((BASE / name).exists() for name in SOURCES):
        return rows, comparison, []
    by = {r['id']: r for r in rows}
    cp = {r['id']: r for r in comparison['projects']}
    changes = []
    for source in SOURCES:
        item = json.loads((BASE / source).read_text(encoding='utf-8-sig'))['projects'][0]
        ident = item['id']
        relative = item.get('archive_relative_path') or item.get('local_path') or item['archive_file']
        file = ROOT / relative
        digest = item.get('archive_sha256') or item['sha256']
        assert file.is_file() and hashlib.sha256(file.read_bytes()).hexdigest() == digest
        with zipfile.ZipFile(file) as archive:
            assert archive.testzip() is None
            for source_file in item['files']:
                name = source_file['path']
                assert '..' not in Path(name).parts and not Path(name).is_absolute()
                matches = [x for x in archive.namelist() if x == name or x.endswith('/' + name)]
                assert len(matches) == 1, name
                raw = archive.read(matches[0])
                assert hashlib.sha256(raw).hexdigest() == source_file['archived_sha256']
                text = raw.decode('utf-8-sig')
                assert not re.search(r'[\w.+%-]+@[\w.-]+\.[A-Za-z]{2,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', text)
        record_before, comparison_before = deepcopy(by[ident]), deepcopy(cp[ident])
        scope = f"固定{len(item['files'])}文件源码选读派生ZIP；保留原路径并附来源/hash，非完整或可构建仓库；未运行"
        attachment = {'status': '固定源码选读派生ZIP已归档', 'archive_file': Path(relative).name, 'exists': True,
                      'reason': scope, 'archive_sha256': digest, 'source_manifest': '08_证据索引与统计/' + source,
                      'source_file_count': len(item['files']), 'selection_only': True, 'runtime_verified': False}
        cp[ident]['attachment'] = attachment
        cp[ident]['backend_dimensions']['可运行材料']['finding'] = scope
        record = by[ident]
        record['source_archive'] = True
        record['archive_status'] = scope
        record['attachment_status'] = deepcopy(attachment)
        record['comparison'] = deepcopy(cp[ident])
        record['source_selection_manifest'] = '08_证据索引与统计/' + source
        changes.append({'id': ident, 'before': record_before, 'after': deepcopy(record),
                        'comparison_before': comparison_before, 'comparison_after': deepcopy(cp[ident]),
                        'source_manifest': source, 'source_files': len(item['files']), 'zip_sha256': digest})
    target = BASE / '项目选读归档_变更清单.json'
    if not target.exists():
        target.write_text(json.dumps({'date': '2026-10-23', 'changes': changes,
            'scope': '仅PRO13/18/19附件、可运行材料范围和来源清单；录用、归属、风险和推荐依据不变。'}, ensure_ascii=False, indent=2), encoding='utf-8')
    return sorted(by.values(), key=lambda r: r['id']), comparison, [r['id'] for r in changes]
