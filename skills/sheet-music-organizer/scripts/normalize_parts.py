#!/usr/bin/env python3
"""
normalize_parts.py — 乐谱声部标注统一化
用法: python3 normalize_parts.py <重奏文件夹路径> [--dry-run]
"""
import os, re, sys, subprocess

def new_suffix(s):
    """把各种声部后缀统一为标准格式"""
    # 总谱
    if re.fullmatch(r'Score', s):               return 'Full Score'
    if re.fullmatch(r'fullscore', s, re.I):     return 'Full Score'
    if re.fullmatch(r'full', s, re.I):          return 'Full Score'
    # 合集
    if re.fullmatch(r'complete', s, re.I):      return 'Complete'
    if re.fullmatch(r'allparts', s, re.I):      return 'All Parts'
    if re.fullmatch(r'parts', s, re.I):         return 'Parts'
    # Violoncello N → Cello N
    m = re.fullmatch(r'Violoncello\s*(\d)', s, re.I)
    if m: return f'Cello {m.group(1)}'
    if re.fullmatch(r'Violoncello\s*IV', s, re.I):  return 'Cello 4'
    if re.fullmatch(r'Violoncello\s*III', s, re.I): return 'Cello 3'
    if re.fullmatch(r'Violoncello\s*II', s, re.I):  return 'Cello 2'
    if re.fullmatch(r'Violoncello\s*I', s, re.I):   return 'Cello 1'
    if re.fullmatch(r'Violoncello', s, re.I):        return 'Cello Solo'
    # Cello 罗马 → 阿拉伯
    if re.fullmatch(r'Cello\s*IV', s, re.I):   return 'Cello 4'
    if re.fullmatch(r'Cello\s*III', s, re.I):  return 'Cello 3'
    if re.fullmatch(r'Cello\s*II', s, re.I):   return 'Cello 2'
    if re.fullmatch(r'Cello\s*I', s, re.I):    return 'Cello 1'
    # 无空格 / 小写
    m = re.fullmatch(r'[Cc]ello(\d)', s)
    if m: return f'Cello {m.group(1)}'
    m = re.fullmatch(r'cello\s+(\d)', s)
    if m: return f'Cello {m.group(1)}'
    return None

def run(base, dry_run=False):
    ok = skip = err = 0
    for composer in sorted(os.listdir(base)):
        cpath = os.path.join(base, composer)
        if not os.path.isdir(cpath) or composer.startswith('.'): continue
        for fname in sorted(os.listdir(cpath)):
            if not fname.endswith('.pdf'): continue
            stem = fname[:-4]
            parts = stem.split('_')
            if len(parts) < 2: continue
            suffix = parts[-1].strip()
            new = new_suffix(suffix)
            if not new or new == suffix: continue
            new_fname = '_'.join(parts[:-1]) + '_' + new + '.pdf'
            old_path = os.path.join(cpath, fname)
            new_path = os.path.join(cpath, new_fname)
            if os.path.exists(new_path):
                same = os.path.getsize(old_path) == os.path.getsize(new_path)
                if same and not dry_run:
                    subprocess.run(['trash', old_path])
                    print(f"🗑  重复删除: {composer}/{fname}")
                else:
                    print(f"⚠️  冲突跳过: {composer}/{fname}")
                skip += 1
                continue
            if dry_run:
                print(f"[dry] {composer}/{fname}  →  _{new}")
                ok += 1
            else:
                os.rename(old_path, new_path)
                print(f"✅ {composer}/{fname}  →  _{new}")
                ok += 1
    print(f"\n{'[dry-run] ' if dry_run else ''}完成：✅{ok}  ⚠️{skip}  ❌{err}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 normalize_parts.py <文件夹路径> [--dry-run]")
        sys.exit(1)
    base = sys.argv[1]
    dry = '--dry-run' in sys.argv
    run(base, dry)
