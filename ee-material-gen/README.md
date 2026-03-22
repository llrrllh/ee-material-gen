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
- ✅ 对话式微调（/api/edit 接口）
- ✅ localStorage状态持久化

### Phase 3 - 完善体验
- ✅ 历史沉淀功能（History & Library）
- ✅ 长图导出功能（Playwright）
- ✅ 热重载支持（新课程自动更新）
- ✅ 前端视觉重构（Modern Tech UI）

## 环境要求

- Python 3.10+
- wkhtmltopdf（用于 PDF 导出）
- Gemini API Key

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

## 运行程序

### 启动服务

```bash
source venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 访问应用

打开浏览器访问：http://localhost:8000

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
   - 点击"导出 PDF"生成 PDF 文件
   - 点击"导出图片"生成长图（PNG）
   - 导出的文件保存在 `exports/` 目录

### 历史记录

- 点击右上角"📚 历史记录"按钮
- 查看所有生成历史
- 点击任意历史记录加载并继续编辑

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
3. 系统会自动使用 fallback 模型（3.1-pro → 3.0-pro → 2.5-pro → 3.0-flash）

### 长图导出失败

1. 确保 Playwright Chromium 已安装：
   ```bash
   playwright install chromium
   ```

2. 检查是否有足够的磁盘空间

## 技术栈

- **后端**: FastAPI + Python 3.10+
- **前端**: HTML + CSS + JavaScript（原生）
- **AI**: Google Gemini API
- **代码编辑器**: Monaco Editor
- **长图导出**: Playwright
- **PDF导出**: wkhtmltopdf

## 开发者

- 负责人：璐桁
- 版本：v1.0.0
- 日期：2026-03-23

## 许可证

内部使用
