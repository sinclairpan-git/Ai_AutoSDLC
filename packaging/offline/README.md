# 离线一键安装包

## 谁做什么

| 角色 | 环境 | 操作 |
|------|------|------|
| 打包人 | **可联网**（建议与目标机同 OS/CPU） | 在本仓库执行构建脚本 |
| 使用人 | **可完全离线** | 解压归档后执行 `install_offline.sh` |

## 打包（生成可分发的 `.tar.gz`）

在仓库根目录：

```bash
chmod +x packaging/offline/build_offline_bundle.sh
./packaging/offline/build_offline_bundle.sh
```

产物：

- `dist-offline/ai-sdlc-offline-<version>.tar.gz` —— **发给内网/他人/服务器**
- `dist-offline/ai-sdlc-offline-<version>/` —— 未压缩目录（可选一起拷贝）

> **平台提示**：若目标机是 Linux x86_64，最好在相同环境下打包；在 macOS ARM 上打的包里的部分依赖 wheel 可能无法在 Linux 上安装。

## 离线一键安装

把 `ai-sdlc-offline-<version>.tar.gz` 拷到目标机后：

```bash
tar xzf ai-sdlc-offline-0.1.0.tar.gz
cd ai-sdlc-offline-0.1.0
chmod +x install_offline.sh
./install_offline.sh
```

指定 Python 或虚拟环境路径：

```bash
PYTHON=/usr/bin/python3.11 ./install_offline.sh
./install_offline.sh /opt/venvs/ai-sdlc
```

验证并初始化业务项目：

```bash
source .venv/bin/activate
ai-sdlc --help
cd /path/to/your-project
ai-sdlc init .
```

## 脚本说明

- `build_offline_bundle.sh`：构建主 wheel + `pip download` 拉齐依赖 wheel，打成 tar.gz
- `install_offline.sh`：解压包内副本；在目标机用 `--no-index --find-links=wheels` 离线安装

`dist-offline/` 仅本地生成，已加入 `.gitignore`，**不把二进制 wheel 提交进 Git**。
