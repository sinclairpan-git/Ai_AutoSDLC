# 离线一键安装包（含 Windows）

## 角色分工

- 打包人（联网机器）：生成离线归档
- 使用人（离线机器）：解压后一键安装

## 一、打包（联网机器）

在仓库根目录执行：

```bash
chmod +x packaging/offline/build_offline_bundle.sh
./packaging/offline/build_offline_bundle.sh
```

产物：

- `dist-offline/ai-sdlc-offline-<version>.tar.gz`（Linux/macOS 推荐）
- `dist-offline/ai-sdlc-offline-<version>.zip`（Windows 推荐）

> 兼容建议：尽量在和目标机相同的 OS/CPU 环境打包。

## 二、离线安装（目标机器）

### Linux/macOS

```bash
tar xzf ai-sdlc-offline-0.2.0.tar.gz
cd ai-sdlc-offline-0.2.0
chmod +x install_offline.sh
./install_offline.sh
```

### Windows

```bat
powershell -ExecutionPolicy Bypass -File .\install_offline.ps1
```

或直接：

```bat
install_offline.bat
```

## 三、安装后验证

```bash
ai-sdlc --help
```

然后进入业务项目目录：

```bash
ai-sdlc init .
```

## 平台兼容提醒

离线包中的依赖 wheel 可能与操作系统/CPU 架构相关。请尽量：

- 在与目标机相同的平台打包
- 或为 Windows、macOS 分别提供对应离线包

避免将 macOS 打出的离线包直接用于 Windows（反之亦然）。

## 四、脚本说明

- `build_offline_bundle.sh`：构建主包并下载依赖，输出 `.tar.gz` + `.zip`
- `install_offline.sh`：Linux/macOS 一键离线安装
- `install_offline.ps1` / `install_offline.bat`：Windows 一键离线安装

`dist-offline/` 是本地构建产物，已在 `.gitignore` 中忽略，不提交二进制包。
