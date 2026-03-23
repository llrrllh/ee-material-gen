"""
Windows 打包脚本
使用 PyInstaller 将项目打包成 Windows 可执行文件
"""

import os
import sys
import shutil
from pathlib import Path


def main():
    print("=" * 60)
    print("开始打包 Windows 可执行文件...")
    print("=" * 60)

    # 检查是否在 Windows 系统上
    if sys.platform != "win32":
        print("\n警告: 此脚本应在 Windows 系统上运行")
        print("当前系统:", sys.platform)
        response = input("\n是否继续? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)

    # 检查 PyInstaller 是否已安装
    try:
        import PyInstaller
        print(f"✓ PyInstaller 已安装 (版本: {PyInstaller.__version__})")
    except ImportError:
        print("\n错误: PyInstaller 未安装")
        print("请运行: pip install pyinstaller")
        sys.exit(1)

    # 获取项目目录
    base_dir = Path(__file__).parent
    os.chdir(base_dir)

    # 清理旧的构建文件
    print("\n清理旧的构建文件...")
    for dir_name in ['build', 'dist']:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  已删除: {dir_name}/")

    # 运行 PyInstaller
    print("\n开始打包...")
    cmd = [
        "pyinstaller",
        "--clean",
        "--noconfirm",
        "ee-material-gen.spec"
    ]

    print(f"执行命令: {' '.join(cmd)}")
    result = os.system(' '.join(cmd))

    if result != 0:
        print("\n错误: 打包失败")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("打包完成!")
    print("=" * 60)
    print(f"\n可执行文件位置: {base_dir / 'dist' / 'EE素材生成器'}")
    print("\n使用说明:")
    print("1. 将 dist/EE素材生成器/ 文件夹复制到目标 Windows 系统")
    print("2. 在文件夹中创建 .env 文件，添加 GEMINI_API_KEY")
    print("3. 双击 EE素材生成器.exe 启动程序")


if __name__ == "__main__":
    main()
