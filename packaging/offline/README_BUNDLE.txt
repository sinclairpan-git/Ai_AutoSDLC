ai-sdlc 离线安装包
==================

内含:
  wheels/               主包与依赖 wheel（由联网打包机生成）
  bundle-manifest.json  bundle 对应的 OS/CPU 平台信息
  python-runtime/       可选；若打包时内置，则离线机无需预装 Python
  install_offline.sh    Linux/macOS 一键安装
  install_offline.ps1   Windows PowerShell 一键安装
  install_offline.bat   Windows 双击/命令行入口
  README.txt            本说明

目标机要求:
  - 若 bundle 内含 `python-runtime/`，则无需预装 Python
  - 若 bundle 未内含 `python-runtime/`，需提供 Python 3.11+
  - 与 `bundle-manifest.json` 中记录的平台一致

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
  当前状态 / Current status
    离线安装完成
    Offline installation completed

  下一步命令 / Next command
    ai-sdlc adapter status
    ai-sdlc run --dry-run

  命令作用 / What this command does
    先检查 adapter 接入真值，再执行安全预演。
    First inspect adapter ingress truth, then run the safe startup rehearsal.
