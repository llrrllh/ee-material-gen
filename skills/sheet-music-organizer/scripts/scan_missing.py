#!/usr/bin/env python3
"""
scan_missing.py — 扫描大提琴重奏文件夹，找出缺失的声部
用法: python3 scan_missing.py <重奏文件夹路径>
输出：
  A类 — 有分谱但缺总谱（Full Score）
  B类 — 缺具体演奏声部（Cello 1/2/3...）
"""
import os, re, sys
from collections import defaultdict

def has_part(parts_set, *targets):
    for t in targets:
        nt = t.lower().replace(' ', '')
        for p in parts_set:
            if nt in p.lower().replace(' ', ''):
                return True
    return False

def run(base):
    pieces = defaultdict(set)
    for composer in sorted(os.listdir(base)):
        cpath = os.path.join(base, composer)
        if not os.path.isdir(cpath) or composer.startswith('.'): continue
        for f in os.listdir(cpath):
            if not f.endswith('.pdf'): continue
            stem = f[:-4]
            parts = stem.split('_')
            part_tag = parts[-1].strip() if len(parts) > 1 else '?'
            m = re.match(r'^(.+?)_(Cello|cello|Score|Full|Viol|complete|Complete|Parts|parts|大提琴|solo|Solo)', stem, re.I)
            piece_base = m.group(1) if m else stem
            pieces[(composer, piece_base)].add(part_tag)

    print("=== B类：缺具体演奏声部 ===\n")
    for (composer, piece), parts in sorted(pieces.items()):
        c1 = has_part(parts, 'Cello 1','cello1','Cello I','Violoncello 1','Violoncello I','大提琴1')
        c2 = has_part(parts, 'Cello 2','cello2','Cello II','Violoncello 2','Violoncello II','大提琴2')
        c3 = has_part(parts, 'Cello 3','cello3','Cello III','Violoncello 3','Violoncello III','大提琴3')
        c4 = has_part(parts, 'Cello 4','cello4','Cello IV','Violoncello 4','Violoncello IV','大提琴4')
        c5 = has_part(parts, 'Cello 5','cello5','Violoncello 5')
        c6 = has_part(parts, 'Cello 6','cello6','Violoncello 6')
        has_score = has_part(parts, 'Full Score','fullscore','Score','Complete')
        num = sum([c1,c2,c3,c4,c5,c6])
        if num == 0: continue
        max_p = 6 if c6 else 5 if c5 else 4 if c4 else 3 if c3 else 2 if c2 else 1
        missing = []
        if max_p >= 2 and not has_score: missing.append('Full Score')
        if max_p >= 2 and not c1: missing.append('Cello 1')
        if max_p >= 3 and not c2: missing.append('Cello 2')
        if max_p >= 4 and not c3: missing.append('Cello 3')
        if max_p >= 5 and not c4: missing.append('Cello 4')
        if max_p >= 6 and not c5: missing.append('Cello 5')
        if missing:
            real_missing = [m for m in missing if m != 'Full Score']
            if real_missing:
                print(f"【{composer}】{piece}")
                print(f"  现有: {', '.join(sorted(parts))}")
                print(f"  缺失: {', '.join(missing)}\n")

    print("=== A类：有分谱但缺总谱 ===\n")
    for (composer, piece), parts in sorted(pieces.items()):
        has_score = has_part(parts, 'Full Score','fullscore','Score','Complete')
        has_any_part = has_part(parts, 'Cello 1','Cello 2','Cello 3','Cello 4','cello1','cello2')
        if has_any_part and not has_score:
            print(f"【{composer}】{piece}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 scan_missing.py <文件夹路径>")
        sys.exit(1)
    run(sys.argv[1])
