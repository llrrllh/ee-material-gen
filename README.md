# 复旦EE 素材生成器

一个本地运行的营销素材生成工具，通过调用 Gemini Pro 模型生成 HTML 格式的招生素材，支持实时预览、提示词优化，并可将结果导出为长图或 PDF。

## 功能特性

### Phase 1 - 基础功能
- ✅ 课程和素材类型选择
- ✅ Gemini API 集成（多模型fallback）
- ✅ 实时预览
- ✅ 导出 PDF/PNG

### Phase 2 - 精细控制
- ✅ 生成前细分控制（28个风格选项）
- ✅ 局部内容开关（6个内容模块）
- ✅ 本地视觉资产接入（Logo选择器）
- ✅ 代码级可视化编辑（Monaco Editor）
- ✅ 对话式微调（支持 Gemini/Claude/GPT）
- ✅ localStorage状态持久化

### Phase 3 - 完善体验
- ✅ 历史沉淀功能（History & Library）
- ✅ 长图导出功能（Playwright）
- ✅ 热重载支持（新课程自动更新）
- ✅ 前端视觉重构（Modern Tech UI）

## 环境要求

- Python 3.10+
- wkhtmltopdf（用于 PDF 导出）
- Gemini API Key（推荐）
- Claude API Key（可选，用于高级优化）
- GPT API Key（可选，通过 cc-switch 配置）

## 安装步骤

### 1. 进入项目目录

```bash
cd /Users/liuluheng/.openclaw/workspace/ee-material-gen/
```

### 2. 创建并激活虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 安装 Playwright 浏览器（用于长图导出）

```bash
playwright install chromium
```

### 5. 配置 Gemini API Key

在项目根目录创建 `.env` 文件（如果还没有的话）：

```bash
echo "GEMINI_API_KEY=你的API密钥" > .env
```

或者编辑现有的 `.env` 文件，确保包含你的 Gemini API Key。

说明：`gemini_client` 会优先读取 `GEMINI_API_KEY`，若未设置则自动回退读取 `GOOGLE_API_KEY`（适配 `cc switch` 场景）。

可选的 Gemini 稳定性配置（建议）：

```bash
# 单次 Gemini HTTP 请求超时（秒），默认 30
GEMINI_REQUEST_TIMEOUT_SECONDS=30

# 一次 /api/generate 中 Gemini 总尝试时间上限（秒），默认 120
GEMINI_TOTAL_TIMEOUT_SECONDS=120

# 模型故障冷却时间（秒）：503/超时后临时跳过，默认 300
GEMINI_MODEL_COOLDOWN_SECONDS=300

# 快速模式：true 时每个模型只尝试 1 次（失败更快切换）
GEMINI_FAST_MODE=false

# 全局默认输出上限（tokens），0 表示不限制
GEMINI_MAX_OUTPUT_TOKENS=0

# /api/generate 默认输出上限（按素材类型会再覆盖）
GEMINI_GENERATE_MAX_OUTPUT_TOKENS_DEFAULT=7600

# /api/edit 输出上限
GEMINI_EDIT_MAX_OUTPUT_TOKENS=12000

# 临时调整首选模型（仅重排优先级，不改默认列表）
GEMINI_PREFERRED_MODEL=models/gemini-3.1-pro-preview

# 或者直接显式指定尝试顺序（逗号分隔）
# GEMINI_MODELS=models/gemini-3.1-pro-preview,models/gemini-3-pro-preview,models/gemini-2.5-pro,models/gemini-3-flash-preview
```

若你使用 `cc-switch`，现在也支持直接读取 `cc-switch` 当前 Gemini Provider 的配置：

- 默认读取：`~/.cc-switch/cc-switch.db`
- 可自定义：在 `.env` 里设置 `CC_SWITCH_DB_PATH=/your/path/cc-switch.db`

推荐写法（通用配置）：

```bash
# 有独立项目密钥时优先使用
GEMINI_API_KEY=

# 与 cc-switch 统一时可不填 GEMINI_API_KEY，
# 程序会自动从 cc-switch 当前 Gemini Provider 读取
CC_SWITCH_DB_PATH=~/.cc-switch/cc-switch.db
```

### 6. 可选：配置 Claude API（高级优化）

在 `.env` 文件中添加：

```bash
# Claude API Key
ANTHROPIC_API_KEY=your_claude_api_key

# 可选：自定义 API 端点
ANTHROPIC_BASE_URL=https://api.anthropic.com
```

### 7. 可选：配置 GPT API（精修功能）

GPT 客户端支持两种配置方式：

**方式 1：从 cc-switch 读取（推荐）**
- 自动从 `cc-switch` 的 codex provider 读取配置
- 默认路径：`~/.cc-switch/cc-switch.db`
- 可自定义：在 `.env` 里设置 `CC_SWITCH_DB_PATH=/your/path/cc-switch.db`

**方式 2：从 openclaw 读取**
- 自动从 `openclaw` 的 openai provider 读取配置
- 默认路径：`~/.openclaw/openclaw.db`
- 如果 cc-switch codex 未配置，会自动回退到 openclaw openai provider

配置优先级：cc-switch codex > openclaw openai

### 8. 可选配置（路径/跨域）

项目已支持通过 `.env` 覆盖关键路径和运行配置：

```bash
# 逗号分隔多个域名；默认 *
CORS_ALLOW_ORIGINS=*

# 视觉素材目录（默认指向 OneDrive Workfiles）
VISUAL_ASSETS_DIR=/path/to/08.视觉素材

# 历史记录目录
HISTORY_DIR=/path/to/history

# 师资同步脚本目录
MEMORY_COURSES_DIR=/path/to/memory/courses
PROMPT_COURSES_DIR=/path/to/prompts/courses

# 配色提取脚本目录
BROCHURE_DIR=/path/to/课程画册
COURSES_COLORS_OUTPUT_FILE=/path/to/courses_colors.json
```

## 运行程序

### 启动服务

```bash
source venv/bin/activate
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 访问应用

打开浏览器访问：http://localhost:8000

### 一键运行（推荐）

```bash
cd /Users/liuluheng/.openclaw/workspace/ee-material-gen
source venv/bin/activate
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 使用说明

### 基本流程

1. **选择课程和素材类型**
   - 从下拉菜单选择课程（如 EE-QYJ）
   - 选择素材类型（如招生海报、项目单页等）

2. **配置生成选项**
   - 填写自定义要求
   - 选择叙事风格、排版结构、视觉元素等
   - 勾选需要包含的内容模块

3. **生成素材**
   - 点击"生成素材"按钮
   - 等待 Gemini 生成 HTML 代码
   - 在右侧预览区查看效果

4. **编辑和微调**
   - 点击"显示代码编辑器"手动修改 HTML/CSS
   - 使用"对话式微调"进行增量修改
   - 点击"应用更改"查看效果

5. **导出素材**
   - 点击"导出 HTML"保存源码文件（.html）
   - 点击"导出 PDF"生成 PDF 文件
   - 点击"导出图片"生成长图（PNG）
   - 导出的文件保存在 `exports/` 目录

### 历史记录

- 点击右上角"📚 历史记录"按钮
- 查看所有生成历史
- 点击任意历史记录加载并继续编辑

## 测试

运行单元测试：

```bash
source venv/bin/activate
python3 -m unittest discover -s tests -p "test_*.py" -v
```

## 全局检查（推荐）

执行语法检查 + 单元测试 + 依赖一致性检查：

```bash
cd /Users/liuluheng/.openclaw/workspace/ee-material-gen
source venv/bin/activate
python3 -m py_compile *.py tests/test_*.py
python3 -m unittest discover -s tests -p "test_*.py" -v
python3 -m pip check
```

## 目录结构

```
ee-material-gen/
├── main.py                  # FastAPI 主服务
├── gemini_client.py         # Gemini API 客户端
├── prompt_builder.py        # 提示词构建器
├── courses.json             # 课程配置
├── requirements.txt         # Python 依赖
├── .env                     # 环境变量（API Key）
├── venv/                    # 虚拟环境
├── static/                  # 前端文件
│   └── index.html
├── prompts/                 # 提示词模板
├── history/                 # 历史记录
└── exports/                 # 导出文件
```

## 故障排除

### 服务无法启动

1. 确保虚拟环境已激活：
   ```bash
   source venv/bin/activate
   ```

2. 检查端口是否被占用：
   ```bash
   lsof -ti:8000
   ```

3. 如果端口被占用，停止占用进程：
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

### Gemini API 调用失败

1. 检查 `.env` 文件中的 API Key 是否正确
2. 确认 API Key 有足够的配额
3. 系统会自动使用 fallback 模型（3.1-pro → 3-pro → 2.5-pro → 3-flash）

### 长图导出失败

1. 确保 Playwright Chromium 已安装：
   ```bash
   playwright install chromium
   ```

2. 检查是否有足够的磁盘空间

## 技术栈

- **后端**: FastAPI + Python 3.10+
- **前端**: HTML + CSS + JavaScript（原生）
- **AI**: Google Gemini API / Claude API / OpenAI GPT API
- **代码编辑器**: Monaco Editor
- **长图导出**: Playwright
- **PDF导出**: wkhtmltopdf

## 开发者

- 负责人：璐桁
- 版本：v1.0.0
- 日期：2026-03-23

## 许可证

内部使用
