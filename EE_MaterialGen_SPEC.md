# 复旦EE招生素材生成器 · 开发规格文档

> 版本：v0.1 | 日期：2026-03-22 | 负责人：璐桁

---

## 一、项目概述

一个本地运行的**营销素材生成工具**，通过调用 Gemini Pro 模型生成 HTML 格式的招生素材，支持实时预览、提示词优化，并可将结
果导出为长图或 PDF。

核心设计原则：

- **无模板**：不预设固定模板，而是从真实素材文件中提取内容和风格，让 Gemini 自主生成 HTML
- **实时预览**：生成后即时在浏览器中渲染，支持提示词优化并重新生成
- **课程感知**：每门课程有独立的 course_id，绑定对应的内容库和品牌配色

---

## 二、课程列表（Course Registry）

每个 course_id 绑定如下属性：

```json
{
  "course_id": "EE-QYJ",
  "name": "企业家战略思维与创新管理课程",
  "short_name": "企业家班",
  "primary_color": "#00349A",
  "accent_color": "#D4AF37",
  "bg_dark": "#051024",
  "logo_path": "08.视觉素材/01_管院VI基础要素/【Logo】[通用]_复旦EE_透明底.png",
  "content_sources": [
    "00.招生相关/02.项目资料/课程画册/【课程手册】企业家战略思维与创新管理课程【最新版】.pdf",
    "00.招生相关/03.招生话术/复旦EE项目素材全百科_2026.md",
    "11.AI生成的招生简章PDF/招生话术精要-企业家班.pdf"
  ],
  "reference_html": "00.招生相关/03.招生话术/企业家班_招生长图_V2.html"
}
```

**初始课程列表**（course_id 规则：EE-[3-4字母缩写]）：

| course_id | 课程名                                 | 主色      | 辅色      |
| --------- | -------------------------------------- | --------- | --------- |
| EE-QYJ    | 企业家战略思维与创新管理课程           | #2E7AB8   | #E8B84A   |
| EE-CMO    | 首席营销官（CMO）课程                  | #1565A8   | #E85A2C   |
| EE-CFO    | 首席财务官（CFO）课程                  | #1A5694   | #E85A2C   |
| EE-GMP    | 高级经理工商管理核心课程               | #00A3D9   | #E85A2C   |
| EE-SCM    | 全球供应链管理课程                     | #2AAA8A   | #C8E550   |
| EE-FCA    | 非财人员的财务管理课程                 | #1E3A5F   | #D4A84B   |
| EE-MA     | 资本运作与并购重组企业家课程           | #C9A86C   | #D4B896   |
| EE-AI     | 人工智能领创计划（第2期）              | #1E4B8E   | #A8C4D9   |
| EE-DH     | 复旦大学生命健康产业领军计划（大健康） | #2DB5A0   | #E8A090   |

配色从对应课程的最新版 PDF 画册中提取（用 PyMuPDF 分析页面主色）。

---

## 三、素材类型（Material Types）

### 招生类

| type_id         | 名称     | 尺寸规格            | 说明                       |
| --------------- | -------- | ------------------- | -------------------------- |
| recruit-poster  | 招生海报 | 750px宽，长度自适应 | 单图竖版，适合微信/朋友圈  |
| recruit-page    | 项目单页 | A4，单页            | 正式对外的精简介绍         |
| student-profile | 学员画像 | A4, 2页。           | 数据可视化，学员背景分析图 |
| landing-page    | 落地页   | 750px宽，长度自适应 | H5风格长页，含CTA          |
| brochure        | 课程画册 | A4，多页            | 完整版招生画册             |

### 运营类

| type_id          | 名称         | 尺寸规格 | 说明                         |
| ---------------- | ------------ | -------- | ---------------------------- |
| class-notice     | 单次课程通知 | A4，单页 | 每次上课前发给学员的正式通知 |
| student-handbook | 学员手册     | A4，多页 | 开学时发放的完整学员手册     |

### 社媒类

| type_id      | 名称     | 尺寸规格            | 说明                |
| ------------ | -------- | ------------------- | ------------------- |
| event-poster | 活动海报 | 1080x1920px         | 朋友圈/社媒竖版海报 |
| long-image   | 招生长图 | 750px宽，长度自适应 | 微信长图，适合转发  |

---

## 四、技术架构

### 技术栈

- **后端**：Python（FastAPI 或 Flask），本地运行
- **前端**：单页 HTML + 内嵌 JS（无需 React，保持轻量）
- **Gemini API**：通过 `google-generativeai` SDK 调用
- **PDF/图片导出**：
  - PDF：wkhtmltopdf（已安装在用户机器）
  - 长图：puppeteer 或 wkhtmltopdf screenshot 模式

### 目录结构

```
~/openclaw/workspace/ee-material-gen/
├── main.py                  # FastAPI 主服务
├── courses.json             # Course registry（含配色、文件路径等）
├── prompts/                 # 提示词模板（按 type_id 分）
│   ├── recruit-poster.txt
│   ├── class-notice.txt
│   └── ...
├── content_cache/           # 从 PDF/HTML 预提取的课程内容缓存
│   ├── EE-QYJ.json
│   └── ...
├── static/
│   ├── index.html           # 前端界面
│   └── preview.html         # 实时预览 iframe
├── exports/                 # 生成的 HTML/PDF/图片
│   └── YYYYMMDD_HHMMSS_EE-QYJ_recruit-poster/
│       ├── output.html
│       ├── output.pdf
│       └── output.png
└── requirements.txt
```

### Gemini 模型配置（含 Fallback）

```python
MODELS = [
    "gemini-3.1-pro-preview",   # 首选
    "gemini-3.0-pro-preview",   # 备选1
    "gemini-2.5-pro",           # 备选2
    "gemini-3.0-flash-preview", # Fallback（不可用时自动降级）
]

def call_gemini_with_fallback(prompt, models=MODELS):
    for model in models:
        try:
            response = genai.GenerativeModel(model).generate_content(prompt)
            return response.text, model
        except Exception as e:
            if "quota" in str(e).lower() or "429" in str(e):
                continue
            raise
    raise Exception("All models exhausted")
```

---

## 五、前端 UI 规格

### 主界面（index.html）布局

```
┌──────────────────────────────────────────────────────────┐
│  复旦EE 素材生成器                            [导出 PDF] [导出图片]
├──────────────────────────────┬───────────────────────────┤
│  左侧控制面板（30%）          │  右侧预览区（70%）          │
│                              │                            │
│  [课程选择] 下拉              │  <iframe preview>          │
│  [素材类型] 下拉              │                            │
│                              │                            │
│  [自定义要求]                 │                            │
│  ┌──────────────────────┐    │                            │
│  │ 例：强调AI赛道，       │    │                            │
│  │ 突出投资人圈层...      │    │                            │
│  └──────────────────────┘    │                            │
│                              │                            │
│  [生成素材] ← 主按钮          │                            │
│                              │                            │
│  ──── 提示词优化 ────         │                            │
│  [当前提示词]（可编辑）        │                            │
│  ┌──────────────────────┐    │                            │
│  │ [Gemini生成的完整     │    │                            │
│  │  提示词，用户可直接    │    │                            │
│  │  修改后重新生成]       │    │                            │
│  └──────────────────────┘    │                            │
│  [用此提示词重新生成]          │                            │
│                              │                            │
│  当前使用模型: gemini-3.1-pro │                            │
└──────────────────────────────┴───────────────────────────┘
```

### 核心交互流程

1. 选择课程 + 素材类型 + 填写自定义要求
2. 点击"生成素材"
3. 后端：① 读取课程内容缓存 → ② 构建完整 Gemini 提示词 → ③ 调用 Gemini → ④ 提取 HTML → ⑤ 返回前端
4. 前端：① 在 iframe 中实时渲染 HTML → ② 在提示词框显示本次使用的提示词
5. 用户可以：修改提示词 → 点击"用此提示词重新生成" → 循环优化
6. 用户也可以直接在窗口修改代码并预览
7. 满意后：点击"导出 PDF" 或"导出图片"

---

## 六、Gemini 提示词策略

### 核心思路

不用固定模板，而是**把真实素材内容直接喂给 Gemini**，让它理解风格后自主生成 HTML。

### 提示词结构（以招生海报为例）

````
你是一位顶级的招生素材设计师，专门为中国顶级商学院（复旦大学管理学院）生成高质量的招生 HTML 页面。

## 课程信息
课程名称：{course_name}
核心定位：{positioning}
目标学员：{target_audience}
学制/学费：{schedule_tuition}
核心师资：{faculty}

## 品牌视觉
主色：{primary_color}（复旦蓝）
辅色：{accent_color}（金色）
整体基调：高端、专业、有温度，参考顶级商学院风格

## 参考风格（从真实 HTML 中提取的设计规范）
{extracted_style_guide}

## 参考内容（从画册/话术文件中提取的关键信息）
{extracted_content}

## 素材类型要求
类型：{material_type}（{width}px 宽，{height_rule}）
用途：{usage_scenario}

## 用户自定义要求
{user_requirements}

## 输出要求
1. 输出完整的、可独立运行的 HTML 代码（含 CSS，不依赖外部库）
2. 字体使用 system-ui, "PingFang SC", "Microsoft YaHei", sans-serif
3. 图片使用 CSS 渐变或 SVG 替代（不依赖外部图片 URL）
4. Logo 使用文字+图形元素模拟（不依赖实际图片文件）
5. 代码用 ```html ... ``` 包裹

直接输出 HTML 代码，不要解释。
````

---

## 七、内容预提取（content_cache）

启动时（或按需）从以下来源提取内容并缓存为 JSON：

- **课程画册 PDF**（PyMuPDF）：提取文字信息（定位、师资、学制、学费、亮点）
- **素材全百科 MD**：直接读取对应课程的话术段落
- **参考 HTML**：提取 CSS 变量（配色）和组件结构（style_guide）

缓存格式（`content_cache/EE-QYJ.json`）：

```json
{
  "course_id": "EE-QYJ",
  "name": "企业家战略思维与创新管理课程",
  "positioning": "...",
  "target_audience": "...",
  "schedule": "...",
  "tuition": "...",
  "faculty": [...],
  "key_points": [...],
  "style_guide": {
    "primary_color": "#00349A",
    "accent_color": "#D4AF37",
    "bg_dark": "#051024",
    "font_family": "...",
    "sample_css_patterns": "..."
  },
  "talking_points": "..."
}
```

---

## 八、API 接口（后端）

```
POST /generate
{
  "course_id": "EE-QYJ",
  "material_type": "recruit-poster",
  "user_requirements": "强调AI赛道，突出投资人圈层",
  "custom_prompt": null  // 如果用户自定义提示词，传入此字段
}
Response: {
  "html": "<!DOCTYPE html>...",
  "prompt_used": "...",
  "model_used": "gemini-3.1-pro-preview"
}

POST /export
{
  "html": "...",
  "format": "pdf" | "png",
  "filename": "EE-QYJ_recruit-poster_20260322"
}
Response: { "file_path": "/exports/..." }

GET /courses
Response: [ { course_id, name, short_name }, ... ]

GET /material-types
Response: [ { type_id, name, description }, ... ]

POST /refresh-cache
{ "course_id": "EE-QYJ" }  // 重新提取该课程内容缓存
```

---

## 九、开发优先级与 Roadmap

### Phase 1（MVP，当前已完成基础框架）
1. 课程 registry（courses.json）和提示词构建
2. Gemini 调用 + Fallback 机制
3. 基础前端 UI（选课程 + 类型 + 生成 + 预览）
4. 导出 PDF 基础功能

### Phase 2（当前阶段：精细控制与交互编辑）
基于 Phase 1 升级前端控制面板与交互逻辑：
5. **生成前细分控制**：在UI增加下拉选项/标签勾选，并动态写入Prompt：
   - **叙事风格**：权威严谨 / 痛点触发 / 圈层吸引 / 设问式沟通（引人深思的设问句激发痛点共鸣）
   - **排版结构 (Layout)**：模块化布局（独立视觉方块便于速读） / 卡片式设计（移动端友好） / 全屏沉浸式（强视觉冲击） / 信息流叙事（纵向动态体验）
   - **视觉元素 (Visuals)**：数字焦点化（大字号数据作为视觉主角） / 高对比度色系（黑白灰+单色点缀） / 极简留白（高端奢侈品呼吸感） / 微动效点缀（细微动画提升质感）
   - **内容呈现 (Content)**：引言高亮（手写体/大字突出金句） / 清单体呈现（项目符号列表） / 数据快照（信息徽章设计）
6. **局部内容开关**：增加复选框（是否包含师资、课表、画像数据等），控制传给大模型的数据粒度。
7. **本地视觉资产接入**：开放本地 `Workfiles/08.视觉素材/` 作为静态资源，支持前端直接选用或用户上传图片，生成素材时自动引入官方Logo及背景图。
8. **代码级可视化编辑**：预览区旁新增代码编辑器（如Monaco Editor），支持手动修改HTML/CSS并实时双向渲染。
9. **对话式微调 (`/edit`接口)**：新增输入框，允许用户基于当前渲染结果进行对话式修改（“标题放大、换个颜色”），大模型进行增量修改而非推翻重来。

### Phase 3（完善体验与资产沉淀）
此阶段由 Assistant 与 Claude Code 协同完成，聚焦于产品级的体验打磨与自动化流转：
10. **工作流自动化：智能提取与扩充新课（由 Assistant 侧实现）**：
    - 后端无需内置定时爬虫，而是由 Assistant 充当 Controller。当用户发布指令（“课程库新增XXX课”）时，Assistant 直接读取项目资料库（PDF/DOCX），提取关键要素（主/辅色、定位、学费、模块等），自动更新至 `courses.json` 及提示词库（`prompts/courses/`），并热更新程序。
11. **前端 UI 现代化重构 (Modern Tech UI)**：
    - 抛弃基础的 HTML 原生控件，全面升级界面视觉。以管院 EE 标志性蓝色系（如深蓝、复旦蓝）为基调，结合色阶透明度、磨砂玻璃（Glassmorphism）、细线条和微光效，打造极具现代感、科技感的 B 端工作台体验。
12. **长图导出完善 (Export to PNG/JPEG)**：
    - 补齐截图能力（建议使用 Puppeteer 或 html2canvas），支持将生成的 HTML 高保真渲染为长图，适应微信群/朋友圈等移动端分享场景。
13. **历史资产沉淀 (History & Library)**：
    - 新增一个“我的素材库/历史记录”面板。自动落盘每次生成的作品（包含生成的 HTML 代码、对应的 Prompt 参数、长图/PDF 文件），支持按时间/课程/类型检索，随时回溯并继续微调。

---

## 十、环境要求

- Python 3.10+
- `google-generativeai`（Gemini SDK）
- `fastapi` + `uvicorn`
- `pymupdf`（PDF 读取）
- `wkhtmltopdf`（导出，已安装）
- 工作路径：`/Users/liuluheng/.openclaw/workspace/ee-material-gen/`
- Workfiles 路径：`/Users/liuluheng/Library/CloudStorage/OneDrive-个人/Workfiles/`

---

## 十一、给 Claude Code 的开发指令

### 阶段一：补齐 Phase 1（MVP）的剩余部分
按以下顺序确保 Phase 1 基础功能完整：
1. 确保 `courses.json` 包含9门核心课程的基础信息与配色（已提取）。
2. 确保 `gemini_client.py` 包含 Fallback 机制（3.1pro -> 3.0pro -> 2.5pro -> 3.0flash）。
3. 确保 `main.py` 提供 `/generate` 接口。
4. 确保 `static/index.html` 能实现基本的左侧表单提交与右侧 iframe 实时预览。

### 阶段二：全面推进 Phase 2（核心目标）
在 Phase 1 基础上，实现精细化控制与交互式修改：
5. **升级前端 UI (`index.html`)**：
   - 增加**生成前细分控制**下拉菜单/复选框：叙事风格（权威/痛点/圈层/设问）、排版结构（模块化/卡片式/全屏沉浸/信息流）、视觉元素（数字焦点化/高对比度/极简留白/微动效）、内容呈现（引言高亮/清单体/数据快照）。
   - 增加**局部内容开关**：控制是否包含师资、课表、画像数据等。
6. **升级提示词构建 (`prompt_builder.py`)**：
   - 接收前端的新增参数，动态将其组合成强有力的结构化 Prompt 注入给 Gemini。
7. **本地视觉资产接入**：
   - 在 `main.py` 中挂载本地 `/Users/liuluheng/Library/CloudStorage/OneDrive-个人/Workfiles/08.视觉素材/` 目录为静态资源。
   - 强制 Prompt 在生成代码时引用复旦 EE 官方 Logo，并支持用户在前端选择或上传背景图。
8. **代码级可视化编辑**：
   - 在预览区旁集成 Monaco Editor 或 CodeMirror，支持手动修改 HTML/CSS 并实时双向渲染。
9. **对话式微调接口 (`/edit`)**：
   - 在 `main.py` 新增 `/edit` 接口。
   - 在前端预览区底部新增“微调对话框”，将**当前渲染的 HTML 代码** + **用户的修改指令** 提交给 Gemini 进行增量修改，而非推翻重来。

### 阶段三：收官与体验跃升（Phase 3）
在目前的 Phase 2 成果（含下拉高级调控、编辑修改、Logo接入等）上，按以下模块深化体验：
10. **导出长图与历史沉淀 (Backend & Frontend)**：
    - **长图导出**：引入长图截图库（如 `playwright`/`puppeteer`），提供 `/export_png` 接口，解决 HTML 长图直接分享朋友圈的问题。
    - **历史沉淀**：在根目录新增 `history/`，每次 `/generate` 均自动归档 `{时间戳}_{course}_{type}.json`（含 Prompt、生成结果 HTML 等）。前端新增“历史库/作品集”侧边栏或独立 Tab，支持调取并预览过去生成的作品，可点击“基于此代码继续微调”。
11. **前端视觉重构 (Modern Tech UI & Fudan EE Theme)**：
    - **全面抛弃原生组件风**。采用以**复旦管院 EE 标志性蓝色**为主轴的现代 B 端工作台设计语言（可引入 TailwindCSS 或直接重写 CSS）。
    - **视觉元素**：大面积深蓝底色/半透明毛玻璃（Glassmorphism）、微发光边框、卡片式模块化布局、扁平化无衬线字体（PingFang SC / System-ui）。使整体呈现出强烈的“高端、智能、前沿”商科科技感。
12. **新课提取与工作流配合 (Agent + System)**：
    - 留一个扩展口（或只需明确 `courses.json` 及 `prompts/courses/` 的绝对规则结构即可）。这部分不要求 Claude Code 编写复杂的定时爬虫服务，未来当用户提出“新增一门课”时，由 Assistant 充当 Controller，自动读文件、提取色值/内容，并将其注入 `courses.json`，程序只需确保前端能实时/热重载获取到新课程即可。
