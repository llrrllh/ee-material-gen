# Windows 可执行文件使用指南

**适用场景**：Windows 系统禁止运行脚本，无法使用虚拟环境和 pip 安装

本指南提供两种方案：
1. 使用预打包的 exe 文件（最简单）
2. 请他人帮忙打包 exe 文件

---

## 方案一：使用预打包的 exe 文件（推荐）

### 前提条件

需要有人在 Windows 系统上完成打包，然后将打包好的文件夹发送给你。

### 打包步骤（需要在有 Python 环境的 Windows 电脑上完成）

如果你有另一台可以运行脚本的 Windows 电脑，或者请朋友帮忙：

#### 1. 安装必要工具

```bash
# 安装 Python 3.10+
# 从 https://www.python.org/downloads/ 下载安装

# 安装 Git
# 从 https://git-scm.com/download/win 下载安装
```

#### 2. 克隆项目

```bash
# 打开命令提示符（CMD）
git clone -b windows https://github.com/llrrllh/ee-material-gen.git
cd ee-material-gen\ee-material-gen
```

#### 3. 创建虚拟环境并安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate.bat

# 安装依赖
pip install -r requirements.txt
pip install pyinstaller
playwright install chromium
```

#### 4. 执行打包

```bash
# 运行打包脚本
python build_windows.py
```

打包完成后，可执行文件位于：`dist\EE素材生成器\`

#### 5. 打包成 ZIP 文件

```bash
# 进入 dist 目录
cd dist

# 将整个文件夹压缩成 ZIP
# 使用 Windows 资源管理器：
# 右键点击 "EE素材生成器" 文件夹 → 发送到 → 压缩(zipped)文件夹
```

---

## 方案二：使用打包好的 exe 文件

### 步骤 1：获取 exe 文件包

从打包者那里获取 `EE素材生成器.zip` 文件。

### 步骤 2：解压文件

1. 将 `EE素材生成器.zip` 复制到你想要的位置，例如：
   ```
   C:\Users\你的用户名\Documents\
   ```

2. 右键点击 ZIP 文件 → **"全部解压缩"**

3. 解压后的目录结构：
   ```
   EE素材生成器/
   ├── EE素材生成器.exe      # 主程序
   ├── _internal/             # 依赖文件（不要删除）
   ├── static/                # 前端文件
   ├── prompts/               # 提示词模板
   ├── courses.json           # 课程配置
   ├── courses_colors.json    # 课程配色
   └── .env.example           # 环境变量示例
   ```

### 步骤 3：配置 API Key

1. **复制示例文件**
   - 找到 `.env.example` 文件
   - 复制一份，重命名为 `.env`（注意：文件名只有扩展名，没有前缀）

2. **编辑 .env 文件**
   - 右键点击 `.env` → **"打开方式"** → **"记事本"**
   - 将内容修改为：
     ```
     GEMINI_API_KEY=你的实际API密钥
     ```
   - 保存并关闭

**获取 API Key**：
- 访问：https://aistudio.google.com/app/apikey
- 登录 Google 账号
- 创建新的 API Key
- 复制 API Key 到 `.env` 文件

### 步骤 4：运行程序

1. **双击运行**
   - 双击 `EE素材生成器.exe`
   - 会弹出一个黑色的命令行窗口（不要关闭）
   - 程序会自动打开浏览器

2. **首次运行可能遇到的问题**

   **Windows Defender 拦截**：
   - 如果看到 "Windows 已保护你的电脑" 提示
   - 点击 **"更多信息"**
   - 点击 **"仍要运行"**

   **防火墙提示**：
   - 如果弹出防火墙提示
   - 勾选 **"专用网络"**
   - 点击 **"允许访问"**

3. **访问应用**
   - 浏览器会自动打开 http://localhost:8000
   - 如果没有自动打开，手动在浏览器输入该地址

### 步骤 5：使用程序

1. **选择课程和素材类型**
2. **填写自定义要求**
3. **点击"生成素材"**
4. **预览和编辑**
5. **导出为 PDF 或图片**

### 步骤 6：停止程序

- 关闭命令行窗口
- 或在命令行窗口按 `Ctrl + C`

---

## 无需打包的替代方案

如果无法获取打包好的 exe 文件，可以考虑以下方案：

### 方案 A：使用在线服务

将项目部署到云服务器或在线平台：
- **Replit**：https://replit.com/
- **Render**：https://render.com/
- **Railway**：https://railway.app/

这些平台提供免费的 Python 运行环境，可以直接运行项目。

### 方案 B：使用 Docker（如果允许）

如果你的系统允许运行 Docker：

1. 安装 Docker Desktop for Windows
2. 使用 Docker 运行项目（无需 Python 环境）

### 方案 C：临时解除脚本限制

如果你有管理员权限，可以临时解除限制：

1. **以管理员身份运行 PowerShell**
   - 右键点击 PowerShell → **"以管理员身份运行"**

2. **临时允许脚本运行**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **完成安装后恢复限制**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope CurrentUser
   ```

---

## 常见问题

### 问题 1：双击 exe 文件没有反应

**解决方案**：
1. 检查是否有杀毒软件拦截
2. 将程序添加到杀毒软件白名单
3. 尝试以管理员身份运行：
   - 右键点击 `EE素材生成器.exe`
   - 选择 **"以管理员身份运行"**

### 问题 2：提示缺少 .env 文件

**解决方案**：
1. 确保 `.env` 文件在 exe 文件的同一目录下
2. 检查文件名是否正确（只有 `.env`，没有其他前缀）
3. 确保文件内容格式正确

### 问题 3：API 调用失败

**解决方案**：
1. 检查 `.env` 文件中的 API Key 是否正确
2. 确认 API Key 没有多余的空格或引号
3. 验证 API Key 是否有效和有配额
4. 检查网络连接

### 问题 4：端口被占用

**错误信息**：`Address already in use`

**解决方案**：
1. 打开任务管理器（`Ctrl + Shift + Esc`）
2. 找到占用 8000 端口的进程
3. 结束该进程
4. 重新运行程序

### 问题 5：缺少 Visual C++ 运行库

**错误信息**：`无法启动此程序，因为计算机中丢失 VCRUNTIME140.dll`

**解决方案**：
1. 下载并安装 Visual C++ 运行库
2. 下载地址：https://aka.ms/vs/17/release/vc_redist.x64.exe
3. 安装后重启电脑

### 问题 6：导出 PDF 失败

**解决方案**：
- PDF 导出功能需要 wkhtmltopdf
- 打包时应该已经包含，如果仍然失败：
  1. 下载 wkhtmltopdf：https://wkhtmltopdf.org/downloads.html
  2. 安装到默认路径
  3. 重启程序

### 问题 7：导出图片失败

**解决方案**：
- 图片导出功能需要 Chromium 浏览器
- 打包时应该已经包含，如果仍然失败：
  - 使用 PDF 导出功能替代
  - 或使用浏览器的截图功能

---

## 文件说明

### 必需文件
- `EE素材生成器.exe` - 主程序（必需）
- `_internal/` - 依赖文件夹（必需，不要删除）
- `.env` - API Key 配置（必需）
- `static/` - 前端文件（必需）
- `prompts/` - 提示词模板（必需）
- `courses.json` - 课程配置（必需）

### 可选文件
- `courses_colors.json` - 课程配色方案
- `history/` - 历史记录（自动创建）
- `exports/` - 导出文件（自动创建）

### 不要删除
- 不要删除 `_internal/` 文件夹中的任何文件
- 不要修改 exe 文件名
- 不要移动 exe 文件到其他位置（除非连同整个文件夹一起移动）

---

## 性能说明

### 文件大小
- 打包后的完整文件夹大小：约 150-200MB
- 压缩后的 ZIP 文件大小：约 80-100MB

### 启动时间
- 首次启动：5-10 秒
- 后续启动：3-5 秒

### 系统要求
- **操作系统**：Windows 10/11（64位）
- **内存**：至少 4GB RAM
- **磁盘空间**：至少 500MB 可用空间
- **网络**：需要联网（调用 Gemini API）

---

## 分发给其他用户

如果你需要将程序分发给其他用户：

1. **打包文件**
   - 将整个 `EE素材生成器` 文件夹压缩成 ZIP
   - 不要只发送 exe 文件

2. **提供说明**
   - 附上本文档
   - 说明如何配置 `.env` 文件
   - 提供 API Key 获取方法

3. **注意事项**
   - 不要在 ZIP 文件中包含你的 `.env` 文件（包含 API Key）
   - 让用户自己创建 `.env` 文件并填入自己的 API Key
   - 提醒用户首次运行可能被 Windows Defender 拦截

---

## 技术支持

如遇到问题：
1. 查看本文档的"常见问题"部分
2. 查看 GitHub Issues：https://github.com/llrrllh/ee-material-gen/issues
3. 查看完整部署指南：`DEPLOYMENT_GUIDE.md`

---

## 版本信息

- **版本**：v1.0.0 (Windows Portable)
- **更新日期**：2026-03-23
- **GitHub**：https://github.com/llrrllh/ee-material-gen
- **分支**：windows

---

**祝使用愉快！** 🎉
