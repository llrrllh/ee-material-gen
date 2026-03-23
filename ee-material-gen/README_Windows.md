# 复旦EE素材生成器 - Windows 版本使用说明

这是专为 Windows 系统优化的版本，可以打包成独立的可执行文件。

## 方式一：直接运行（开发模式）

### 环境要求
- Windows 10/11
- Python 3.10 或更高版本
- Gemini API Key

### 安装步骤

1. **克隆或下载项目**
   ```bash
   git clone https://github.com/llrrllh/ee-material-gen.git
   cd ee-material-gen
   git checkout windows
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **配置 API Key**

   复制 `.env.example` 为 `.env`，然后编辑 `.env` 文件：
   ```
   GEMINI_API_KEY=你的API密钥
   ```

5. **启动程序**
   ```bash
   python launcher.py
   ```

   程序会自动启动服务并打开浏览器。

## 方式二：打包成可执行文件（推荐）

### 打包步骤

1. **安装打包工具**
   ```bash
   pip install pyinstaller
   ```

2. **运行打包脚本**
   ```bash
   python build_windows.py
   ```

3. **打包完成**

   可执行文件位于 `dist/EE素材生成器/` 目录下。

### 分发给其他用户

1. 将整个 `dist/EE素材生成器/` 文件夹复制到目标电脑
2. 在文件夹中创建 `.env` 文件，添加：
   ```
   GEMINI_API_KEY=你的API密钥
   ```
3. 双击 `EE素材生成器.exe` 启动程序
4. 程序会自动打开浏览器访问 http://localhost:8000

## 功能特性

### 核心功能
- ✅ 课程和素材类型选择
- ✅ Gemini AI 生成营销素材
- ✅ 实时预览
- ✅ 代码编辑器（Monaco Editor）
- ✅ 对话式微调
- ✅ 导出 PDF/PNG
- ✅ 历史记录管理

### 生成控制
- 28 个风格选项（叙事风格、排版结构、视觉元素等）
- 6 个内容模块开关
- 自定义要求输入

## 使用流程

1. **选择课程和素材类型**
   - 从下拉菜单选择课程（如 EE-QYJ）
   - 选择素材类型（如招生海报、项目单页等）

2. **配置生成选项**
   - 填写自定义要求
   - 选择风格和视觉元素
   - 勾选需要的内容模块

3. **生成素材**
   - 点击"生成素材"按钮
   - 在右侧预览区查看效果

4. **编辑和微调**
   - 使用代码编辑器手动修改
   - 或使用对话式微调进行增量修改

5. **导出素材**
   - 导出为 PDF 或 PNG 长图
   - 文件保存在 `exports/` 目录

## 故障排除

### 程序无法启动

1. **检查 .env 文件**
   - 确保 `.env` 文件存在
   - 确认 API Key 正确

2. **端口被占用**
   - 关闭其他占用 8000 端口的程序
   - 或修改 `launcher.py` 中的端口号

3. **缺少依赖**
   - 重新安装依赖：`pip install -r requirements.txt`

### Gemini API 调用失败

1. 检查 API Key 是否正确
2. 确认 API Key 有足够的配额
3. 检查网络连接

### 导出功能失败

**PDF 导出失败**：
- 需要安装 wkhtmltopdf
- 下载地址：https://wkhtmltopdf.org/downloads.html

**PNG 导出失败**：
- 确保 Playwright Chromium 已安装
- 运行：`playwright install chromium`

## 与 macOS 版本的区别

### Windows 分支的改进
1. ✅ 移除了硬编码的 macOS 路径
2. ✅ 添加了 Windows 启动器
3. ✅ 提供了 PyInstaller 打包配置
4. ✅ 优化了跨平台兼容性

### 主分支保留
- 完整的开发环境配置
- macOS 特定的路径和配置
- 所有原始功能和文档

## 技术栈

- **后端**: FastAPI + Python 3.10+
- **前端**: HTML + CSS + JavaScript
- **AI**: Google Gemini API
- **代码编辑器**: Monaco Editor
- **长图导出**: Playwright
- **PDF 导出**: wkhtmltopdf
- **打包工具**: PyInstaller

## 开发者信息

- 负责人：璐桁
- 版本：v1.0.0 (Windows)
- 日期：2026-03-23
- GitHub: https://github.com/llrrllh/ee-material-gen

## 许可证

内部使用
