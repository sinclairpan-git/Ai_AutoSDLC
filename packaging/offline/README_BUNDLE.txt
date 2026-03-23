ai-sdlc 离线安装包
==================

内含:
  wheels/               主包与依赖 wheel（由联网打包机生成）
  install_offline.sh    Linux/macOS 一键安装
  install_offline.ps1   Windows PowerShell 一键安装
  install_offline.bat   Windows 双击/命令行入口
  README.txt            本说明

目标机要求:
  - Python 3.11 或更高
  - 与打包机尽量同 OS/CPU 架构

Linux/macOS 安装:
  chmod +x install_offline.sh
  ./install_offline.sh

Windows 安装:
  install_offline.bat
  或
  powershell -ExecutionPolicy Bypass -File .\install_offline.ps1

可选参数:
  Linux/macOS:
    PYTHON=/usr/bin/python3.11 ./install_offline.sh
    ./install_offline.sh /opt/venvs/ai-sdlc

  Windows:
    powershell -ExecutionPolicy Bypass -File .\install_offline.ps1 -PythonExe "py -3.11" -VenvPath ".venv"

安装后:
  ai-sdlc --help
  cd 到你的项目目录
  ai-sdlc init .
