---
name: course-analyzer
description: Extract, analyze, and structure course information from various document formats (PDFs, PPTs, Images, Excel) and prepare competitive analysis. Use when asked to learn, summarize, or extract course details, syllabi, target audience, pricing, and sales talk tracks.
read_when:
  - User asks to "learn about courses", "提炼课程内容", "学习一下课程"
  - Need to analyze course brochures, syllabi, or marketing materials
  - Need to find and compare competitor courses
metadata: {"clawdbot":{"emoji":"📚","requires":{"bins":["python3"]}}}
allowed-tools: Bash(course-analyzer:*)
---

# Course Analyzer

This skill defines the structured workflow for extracting and consolidating High-Level Executive Education (EE) course information into long-term memory.

## 1. Information Extraction Strategy

When tasked with learning courses, you should process files in this order of reliability:
1. `【课程汇总】[通用]_课程信息一览.xlsx` (Global overview, pricing, dates)
2. `课表与教学大纲` (Detailed curriculum, modules)
3. `课程画册` (PDF/Images: Marketing copy, value proposition, target audience)
4. `03.招生话术` (Sales talk tracks, FAQ, objection handling)

## 2. Image and Non-Text Extraction
For image-heavy brochures (PDF/Images), use the `image` tool.
Pass the prompt: *"Extract all text regarding course background, target audience, modules, curriculum, and pricing from this brochure image. Keep the tone professional."*

For Excel/Word files, use the `Data Analysis` skill or `Excel / XLSX` / `Word / DOCX` skills to extract raw text.

## 3. Desired Memory Structure (`memory/courses/<Course_Name>.md`)

For each course, create a dedicated markdown file in `memory/courses/` following this template:

```markdown
# [Course Name]

## 1. 课程概况 (Overview)
- **定位/价值 (Value Proposition):** 
- **目标学员 (Target Audience):** 
- **学制/课表 (Duration & Format):** (e.g., 1年，每月集中授课2天)
- **学费 (Pricing):** 
- **考核与证书 (Certification):** 

## 2. 课程体系与模块 (Curriculum)
- **Module 1:** ...
- **Module 2:** ...

## 3. 招生与话术 (Sales & Admission)
- **核心卖点 (Key Selling Points):**
- **常见问题/异议处理 (FAQ / Objection Handling):**
- **入学流程 (Admission Process):**

## 4. 竞品分析 (Competitive Analysis)
- **竞品A (机构名称 - 课程名):** 
  - 相似点: ...
  - 差异化/优势: ...
  - 价格对比: ...
```

## 4. Competitive Analysis Workflow

After extracting the internal course data:
1. Identify the core theme (e.g., "CMO", "供应链管理", "高管工商管理").
2. Use `web_search` to find similar programs from top institutions (e.g., 中欧(CEIBS), 长江商学院(CKGSB), 交大安泰, 北大光华, 清华经管).
3. Search query example: `"中欧国际工商学院" AND "首席营销官" OR "CMO" 课程 学费`
4. Summarize the competitor's target audience, duration, and price, and append to the "竞品分析" section of the course memory file.

## 5. Execution Hook
Create the directory `memory/courses` if it does not exist.
Run through the available files in `/Users/liuluheng/Library/CloudStorage/OneDrive-个人/Workfiles/00.招生相关/02.项目资料` and `/Users/liuluheng/Library/CloudStorage/OneDrive-个人/Workfiles/03.报审表及简章`.
Build the records iteratively.
