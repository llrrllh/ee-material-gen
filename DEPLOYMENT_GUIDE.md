# 复旦EE素材生成器 - 完整部署指南

本指南涵盖在 macOS 和 Windows 系统上的完整安装、运行和打包流程。

---

## 目录

- [系统要求](#系统要求)
- [macOS 部署指南](#macos-部署指南)
  - [方式一：本地开发运行](#macos-方式一本地开发运行)
  - [方式二：打包成应用程序](#macos-方式二打包成应用程序)
- [Windows 部署指南](#windows-部署指南)
  - [方式一：本地开发运行](#windows-方式一本地开发运行)
  - [方式二：打包成可执行文件](#windows-方式二打包成可执行文件)
- [常见问题解决](#常见问题解决)
- [功能说明](#功能说明)

---

## 系统要求

### 通用要求
- Python 3.10 或更高版本
- Gemini API Key（[获取地址](https://aistudio.google.com/app/apikey)）
- 至少 2GB 可用磁盘空间
- 稳定的网络连接

### macOS 特定要求
- macOS 10.15 (Catalina) 或更高版本
- Homebrew（推荐，用于安装依赖）

### Windows 特定要求
- Windows 10/11
- 管理员权限（用于安装依赖）

---

## macOS 部署指南

### macOS 方式一：本地开发运行

这是最简单的方式，适合开发和测试。

#### 步骤 1：克隆项目

```bash
# 克隆主分支（macOS 优化版本）
git clone https://github.com/llrrllh/ee-material-gen.git
cd ee-material-gen
```

#### 步骤 2：创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

#### 步骤 3：安装依赖

```bash
# 安装 Python 依赖
pip install -r ee-material-gen/requirements.txt

# 安装 Playwright 浏览器（用于长图导出）
playwright install chromium
```

#### 步骤 4：配置 API Key

```bash
# 进入项目目录
cd ee-material-gen

# 创建 .env 文件
cat > .env << 'EOF'
GEMINI_API_KEY=你的API密钥
EOF
```

或者手动创建 `.env` 文件：
```
GEMINI_API_KEY=your_actual_api_key_here
```

#### 步骤 5：启动服务

```bash
# 确保虚拟环境已激活
source ../venv/bin/activate

# 启动服务
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 步骤 6：访问应用

打开浏览器访问：http://localhost:8000

#### 停止服务

在终端按 `Ctrl + C` 停止服务。

---

### macOS 方式二：打包成应用程序

将项目打包成独立的 macOS 应用程序（.app 文件）。

#### 步骤 1：安装打包工具

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装 PyInstaller
pip install pyinstaller

# 安装 py2app（macOS 专用打包工具）
pip install py2app
```

#### 步骤 2：创建打包配置

在 `ee-material-gen/` 目录下创建 `setup.py`：

```python
from setuptools import setup

APP = ['launcher.py']
DATA_FILES = [
    ('static', ['static']),
    ('prompts', ['prompts']),
    ('', ['courses.json', 'courses_colors.json', '.env.example'])
]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['fastapi', 'uvicorn', 'google.generativeai', 'playwright'],
    'iconfile': None,  # 可以添加 .icns 图标文件
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

#### 步骤 3：执行打包

```bash
cd ee-material-gen

# 清理旧的构建文件
rm -rf build dist

# 打包
python setup.py py2app
```

#### 步骤 4：使用打包后的应用

```bash
# 应用程序位于
ls dist/launcher.app

# 运行应用
open dist/launcher.app
```

#### 分发给其他 macOS 用户

1. 将 `dist/launcher.app` 复制到其他 Mac
2. 在应用程序目录下创建 `.env` 文件
3. 双击运行

---

## Windows 部署指南

### Windows 方式一：本地开发运行

适合开发和测试环境。

#### 步骤 1：克隆项目

```bash
# 克隆 Windows 分支
git clone -b windows https://github.com/llrrllh/ee-material-gen.git
cd ee-material-gen
```

#### 步骤 2：创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate
```

#### 步骤 3：安装依赖

```bash
# 安装 Python 依赖
pip install -r ee-material-gen\requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

#### 步骤 4：配置 API Key

```bash
# 进入项目目录
cd ee-material-gen

# 创建 .env 文件（使用记事本或其他编辑器）
notepad .env
```

在 `.env` 文件中添加：
```
GEMINI_API_KEY=你的API密钥
```

或者使用命令行：
```bash
echo GEMINI_API_KEY=你的API密钥 > .env
```

#### 步骤 5：启动服务

**方式 A：使用启动器（推荐）**
```bash
python launcher.py
```

**方式 B：直接启动 uvicorn**
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 步骤 6：访问应用

浏览器会自动打开，或手动访问：http://localhost:8000

#### 停止服务

关闭命令行窗口或按 `Ctrl + C`。

---

### Windows 方式二：打包成可执行文件

将项目打包成独立的 Windows 可执行文件（.exe），无需安装 Python。

#### 步骤 1：准备环境

```bash
# 确保在 Windows 系统上操作
# 激活虚拟环境
venv\Scripts\activate

# 安装打包工具
pip install pyinstaller
```

#### 步骤 2：执行打包

```bash
cd ee-material-gen

# 运行打包脚本
python build_windows.py
```

打包过程需要 5-10 分钟，请耐心等待。

#### 步骤 3：查看打包结果

```bash
# 打包完成后，可执行文件位于
dir dist\EE素材生成器
```

目录结构：
```
dist/EE素材生成器/
├── EE素材生成器.exe    # 主程序
├── static/              # 前端文件
├── prompts/             # 提示词模板
├── courses.json         # 课程配置
├── .env.example         # 环境变量示例
└── [其他依赖文件]
```

#### 步骤 4：配置和运行

```bash
# 进入打包目录
cd dist\EE素材生成器

# 创建 .env 文件
copy .env.example .env
notepad .env
```

在 `.env` 中填入你的 API Key，然后：

```bash
# 双击运行
EE素材生成器.exe
```

或在命令行运行：
```bash
.\EE素材生成器.exe
```

#### 步骤 5：分发给其他用户

1. 将整个 `dist\EE素材生成器\` 文件夹打包成 ZIP
2. 发送给其他 Windows 用户
3. 用户解压后：
   - 创建 `.env` 文件并填入 API Key
   - 双击 `EE素材生成器.exe` 运行

**注意**：
- 首次运行可能被 Windows Defender 拦截，选择"仍要运行"
- 打包后的文件大小约 150-200MB
- 不需要安装 Python 或其他依赖

---

## 常见问题解决

### 问题 1：端口被占用

**错误信息**：
```
Error: [Errno 48] Address already in use
```

**解决方案**：

**macOS**：
```bash
# 查找占用 8000 端口的进程
lsof -ti:8000

# 终止进程
lsof -ti:8000 | xargs kill -9
```

**Windows**：
```bash
# 查找占用 8000 端口的进程
netstat -ano | findstr :8000

# 终止进程（替换 PID 为实际进程 ID）
taskkill /PID <PID> /F
```

### 问题 2：Gemini API 调用失败

**错误信息**：
```
Error: Invalid API key
```

**解决方案**：
1. 检查 `.env` 文件是否存在
2. 确认 API Key 格式正确（无多余空格）
3. 验证 API Key 是否有效：访问 https://aistudio.google.com/app/apikey
4. 检查 API 配额是否用完

### 问题 3：Playwright 安装失败

**错误信息**：
```
Error: Executable doesn't exist at ...
```

**解决方案**：
```bash
# 重新安装 Playwright 浏览器
playwright install chromium

# 如果仍然失败，尝试完整安装
playwright install
```

### 问题 4：PDF 导出失败

**错误信息**：
```
Error: wkhtmltopdf not found
```

**解决方案**：

**macOS**：
```bash
# 使用 Homebrew 安装
brew install wkhtmltopdf
```

**Windows**：
1. 下载安装包：https://wkhtmltopdf.org/downloads.html
2. 安装到默认路径
3. 将安装路径添加到系统 PATH 环境变量

### 问题 5：虚拟环境激活失败（Windows）

**错误信息**：
```
无法加载文件，因为在此系统上禁止运行脚本
```

**解决方案**：
```bash
# 以管理员身份运行 PowerShell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# 然后重新激活虚拟环境
venv\Scripts\activate
```

### 问题 6：打包后程序无法启动

**Windows 常见原因**：
1. 缺少 `.env` 文件
2. 杀毒软件拦截
3. 缺少 Visual C++ 运行库

**解决方案**：
```bash
# 1. 确保 .env 文件存在且配置正确
# 2. 将程序添加到杀毒软件白名单
# 3. 安装 Visual C++ 运行库
# 下载地址：https://aka.ms/vs/17/release/vc_redist.x64.exe
```

### 问题 7：导入模块失败

**错误信息**：
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案**：
```bash
# 确保虚拟环境已激活
# macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# 重新安装依赖
pip install -r ee-material-gen/requirements.txt
```

---

## 功能说明

### 核心功能

1. **课程选择**
   - 支持多个复旦 EE 课程
   - 自动加载课程信息和配色方案

2. **素材类型**
   - 招生海报
   - 项目单页
   - 课程手册
   - H5 落地页
   - 等多种营销素材

3. **AI 生成**
   - 基于 Gemini Pro 模型
   - 多模型自动 fallback
   - 支持自定义提示词

4. **生成控制**
   - 28 个风格选项
   - 6 个内容模块开关
   - 视觉资产选择器

5. **编辑功能**
   - Monaco 代码编辑器
   - 实时预览
   - 对话式微调

6. **导出功能**
   - PDF 导出
   - PNG 长图导出
   - 自动保存历史记录

### 使用流程

1. **启动程序** → 自动打开浏览器
2. **选择课程** → 选择素材类型
3. **配置选项** → 填写自定义要求
4. **生成素材** → AI 自动生成 HTML
5. **预览编辑** → 实时查看效果
6. **导出保存** → 导出为 PDF 或图片

### 快捷键

- `Ctrl/Cmd + S`：保存当前编辑
- `Ctrl/Cmd + Enter`：应用更改
- `Esc`：关闭弹窗

---

## 技术架构

### 后端
- **框架**：FastAPI
- **AI 模型**：Google Gemini API
- **PDF 导出**：wkhtmltopdf
- **长图导出**：Playwright

### 前端
- **框架**：原生 HTML/CSS/JavaScript
- **代码编辑器**：Monaco Editor
- **UI 风格**：Modern Tech Design

### 打包工具
- **macOS**：py2app
- **Windows**：PyInstaller

---

## 版本信息

- **当前版本**：v1.0.0
- **最后更新**：2026-03-23
- **开发者**：璐桁
- **GitHub**：https://github.com/llrrllh/ee-material-gen

### 分支说明

- **main 分支**：macOS 优化版本，包含完整开发环境
- **windows 分支**：Windows 适配版本，支持打包成 .exe

---

## 许可证

内部使用

---

## 技术支持

如遇到问题，请检查：
1. 本文档的"常见问题解决"部分
2. GitHub Issues：https://github.com/llrrllh/ee-material-gen/issues
3. 项目 README 文件

---

**祝使用愉快！** 🎉
