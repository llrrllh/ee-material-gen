"""
复旦EE素材生成器 - Windows 启动器
自动启动服务并打开浏览器
"""

import os
import sys
import time
import webbrowser
import subprocess
from pathlib import Path


def main():
    print("=" * 60)
    print("复旦EE素材生成器 - 启动中...")
    print("=" * 60)

    # 获取程序所在目录
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件
        base_dir = Path(sys._MEIPASS)
    else:
        # 开发环境
        base_dir = Path(__file__).parent

    print(f"工作目录: {base_dir}")

    # 检查必要文件
    required_files = ['main.py', 'gemini_client.py', 'prompt_builder.py']
    for file in required_files:
        if not (base_dir / file).exists():
            print(f"错误: 缺少必要文件 {file}")
            input("按回车键退出...")
            sys.exit(1)

    # 检查 .env 文件
    env_file = base_dir / '.env'
    if not env_file.exists():
        print("\n警告: 未找到 .env 文件")
        print("请在程序目录下创建 .env 文件，并添加以下内容：")
        print("GEMINI_API_KEY=你的API密钥")
        input("\n按回车键退出...")
        sys.exit(1)

    # 启动 FastAPI 服务
    print("\n正在启动服务...")
    port = 8000

    try:
        # 启动 uvicorn 服务（在后台）
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app",
             "--host", "0.0.0.0", "--port", str(port)],
            cwd=str(base_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # 等待服务启动
        print("等待服务启动...")
        time.sleep(3)

        # 检查服务是否正常运行
        if process.poll() is not None:
            print("错误: 服务启动失败")
            stdout, stderr = process.communicate()
            print(f"错误信息: {stderr.decode('utf-8', errors='ignore')}")
            input("按回车键退出...")
            sys.exit(1)

        # 打开浏览器
        url = f"http://localhost:{port}"
        print(f"\n服务已启动: {url}")
        print("正在打开浏览器...")
        webbrowser.open(url)

        print("\n" + "=" * 60)
        print("服务正在运行中...")
        print("关闭此窗口将停止服务")
        print("=" * 60)

        # 保持运行
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n正在关闭服务...")
            process.terminate()
            process.wait()
            print("服务已关闭")

    except Exception as e:
        print(f"\n错误: {str(e)}")
        input("按回车键退出...")
        sys.exit(1)


if __name__ == "__main__":
    main()
