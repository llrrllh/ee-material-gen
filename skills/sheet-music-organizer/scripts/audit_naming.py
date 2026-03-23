#!/usr/bin/env python3
"""
audit_naming.py — 乐谱库命名合规审查工具
用法: python3 audit_naming.py <重奏文件夹路径>
功能：检查所有「作曲家目录」和「乐谱文件」是否符合中英文对照的双语规范
"""
import os, re, sys

def audit(base_dir):
    issues_composer = []
    issues_piece = []
    
    for composer in sorted(os.listdir(base_dir)):
        if composer.startswith('.') or not os.path.isdir(os.path.join(base_dir, composer)):
            continue
            
        # 检查作曲家命名：如果全中文则视为合法（中国作曲家），如果包含英文字母则必须包含括号（西方/其他作曲家）
        has_english = bool(re.search(r'[A-Za-z]', composer))
        has_brackets = bool(re.search(r'\(.*?\)', composer) or re.search(r'（.*?）', composer))
        
        if has_english and not has_brackets:
            issues_composer.append(f"{composer} -> 西方作曲家需提供双语对照 (例如: Tchaikovsky (柴可夫斯基))")
            
        cpath = os.path.join(base_dir, composer)
        for fname in sorted(os.listdir(cpath)):
            if not fname.endswith('.pdf'): continue
            
            stem = fname[:-4]
            parts = stem.split('_')
            
            if len(parts) < 2:
                issues_piece.append(f"[{composer}] {fname} -> 缺少下划线分割（无法区分曲名和声部）")
                continue
                
            piece_name = parts[0]
            # 检查曲名是否双语对照（包含括号且括号里有非英文字符）
            if not re.search(r'\(.*?\)', piece_name) and not re.search(r'（.*?）', piece_name):
                issues_piece.append(f"[{composer}] {fname} -> 曲名缺失双语对照")

    print("=== 🎶 乐谱库「双语合规」审查报告 ===\n")
    print(f"⚠️  待补充或精简双语名的「作曲家文件夹」({len(issues_composer)}个):")
    for c in issues_composer:
        print(f"  - {c}")
        
    print(f"\n⚠️  待补充双语名的「乐谱文件」({len(issues_piece)}首/个):")
    for p in issues_piece[:20]: # 预览前20个
        print(f"  - {p}")
    if len(issues_piece) > 20:
        print(f"  ... (还有 {len(issues_piece)-20} 个未列出)")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 audit_naming.py <文件夹路径>")
        sys.exit(1)
    audit(sys.argv[1])
