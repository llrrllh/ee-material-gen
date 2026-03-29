#!/usr/bin/env python3
"""
sync_course_faculty.py
将 memory/courses/*.md 中的"核心师资"章节，自动同步到
ee-material-gen/prompts/courses/EE-*.txt 中对应的师资段落。

只替换师资部分，不动 prompt 文件中的其他内容（品牌定位/话术/颜色等）。
"""

import re
from pathlib import Path

from settings import get_settings

settings = get_settings()
MEMORY_DIR = settings.memory_courses_dir
PROMPT_DIR = settings.prompt_courses_dir

# Memory 文件名 → Prompt 文件 ID 的映射
COURSE_MAP = {
    "AI领创": "EE-AI",
    "大健康": "EE-DH",
    "非财": "EE-FCA",
    "高经班": "EE-GMP",
    "企业家班": "EE-QYJ",
    "复旦大学首席营销官(CMO)课程": "EE-CMO",
    "复旦大学首席财务官(CFO)课程": "EE-CFO",
    "供应链": "EE-SCM",
    "资本并购": "EE-MA",
}


def extract_section(md_content: str, heading: str) -> str:
    """从 Markdown 中提取指定 ## heading 的内容（到下一个 ## 为止）
    支持带序号的标题，如 '## 3. 核心师资' 也能匹配 '核心师资'
    """
    pattern = rf"(## (?:\d+\.\s*)?{re.escape(heading)}.*?)(?=\n## |\Z)"
    m = re.search(pattern, md_content, re.DOTALL)
    return m.group(1).strip() if m else ""


def replace_faculty_in_prompt(prompt_content: str, new_faculty_md: str) -> str:
    """
    将 prompt 文件中 "### 核心师资" 段落替换为从 memory 同步过来的内容。
    把 ## 标题降级为 ### 以匹配 prompt 文件的层级。
    """
    # 把 memory 里的 ## 核心师资 转成 ### 核心师资
    new_section = new_faculty_md.replace("## 核心师资", "### 核心师资", 1)
    # 去掉子标题的 ## → **（memory 里没有三级标题，这里做一层美化）

    # 找到 prompt 里 "### 核心师资" 到下一个 ### 或 ## 为止
    pattern = r"(### 核心师资.*?)(?=\n### |\n## |\Z)"
    if re.search(pattern, prompt_content, re.DOTALL):
        return re.sub(pattern, new_section, prompt_content, flags=re.DOTALL)
    else:
        # 如果 prompt 里找不到该段，直接追加
        return prompt_content + "\n\n" + new_section


def sync(memory_dir: Path = MEMORY_DIR, prompt_dir: Path = PROMPT_DIR):
    synced = []
    skipped = []

    for memory_name, prompt_id in COURSE_MAP.items():
        memory_path = memory_dir / f"{memory_name}.md"
        prompt_path = prompt_dir / f"{prompt_id}.txt"

        if not memory_path.exists():
            skipped.append(f"{memory_name}.md 不存在")
            continue
        if not prompt_path.exists():
            skipped.append(f"{prompt_id}.txt 不存在")
            continue

        memory_content = memory_path.read_text(encoding="utf-8")
        faculty_section = extract_section(memory_content, "核心师资")

        if not faculty_section:
            skipped.append(f"{memory_name} — memory 中未找到「核心师资」章节")
            continue

        prompt_content = prompt_path.read_text(encoding="utf-8")
        updated = replace_faculty_in_prompt(prompt_content, faculty_section)

        if updated != prompt_content:
            prompt_path.write_text(updated, encoding="utf-8")
            synced.append(f"✅ {memory_name} → {prompt_id}.txt")
        else:
            synced.append(f"✔ {memory_name} → {prompt_id}.txt（无变化）")

    print("=== 同步结果 ===")
    for s in synced:
        print(s)
    if skipped:
        print("\n=== 跳过 ===")
        for s in skipped:
            print(s)


if __name__ == "__main__":
    sync()
