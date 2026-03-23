ai-sdlc 离线安装包
==================

内含:
  wheels/          主包与全部依赖的 wheel（由打包机在联网环境生成）
  install_offline.sh  一键安装脚本
  README.txt       本说明

目标机要求:
  - Python 3.11 或更高（python3 在 PATH 中，或通过环境变量 PYTHON 指定）
  - 与打包机尽量「同操作系统 + 同 CPU 架构」（否则部分带二进制扩展的依赖可能不兼容）

一键安装（在解压后的本目录执行）:

  chmod +x install_offline.sh
  ./install_offline.sh

默认在当前目录创建 .venv。指定虚拟环境路径:

  ./install_offline.sh /opt/ai-sdlc-venv

使用指定 Python:

  PYTHON=/usr/bin/python3.11 ./install_offline.sh

安装完成后:

  source .venv/bin/activate   # 或你传入的 venv 路径
  ai-sdlc --help
  cd /你的项目目录
  ai-sdlc init .
