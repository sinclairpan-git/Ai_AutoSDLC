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
- `dist-offline/ai-sdlc-offline-<version>/bundle-manifest.json`（记录 bundle 适用的 OS/CPU 平台）

> 平台合同：新 bundle 会写出 `bundle-manifest.json`，安装脚本会校验目标机 OS/CPU 是否匹配；请尽量在和目标机相同的 OS/CPU 环境打包。

## 二、离线安装（目标机器）

### Linux/macOS

```bash
tar xzf ai-sdlc-offline-<version>.tar.gz
cd ai-sdlc-offline-<version>
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

如果 bundle 的 `bundle-manifest.json` 与当前机器 OS/CPU 不匹配，安装脚本会直接拒绝安装。

## 三、安装后验证

**Linux / macOS**（已 `source .venv/bin/activate`）：

```bash
ai-sdlc --help
```

**Windows**（推荐先激活 venv；若未激活，用完整路径或模块方式）：

```powershell
# 激活后
ai-sdlc --help

# 或未激活时
& .\.venv\Scripts\ai-sdlc.exe --help
# 或
& .\.venv\Scripts\python.exe -m ai_sdlc --help
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
- `bundle-manifest.json`：记录 bundle 的 package version、build OS、CPU 架构
- `install_offline.sh`：Linux/macOS 一键离线安装，并校验 `bundle-manifest.json`
- `install_offline.ps1` / `install_offline.bat`：Windows 一键离线安装，并校验 `bundle-manifest.json`

`dist-offline/` 是本地构建产物，已在 `.gitignore` 中忽略，不提交二进制包。

## 五、发布检查清单（维护者）

发布或分发离线包前建议逐项确认：

1. **平台匹配**：在 **Windows** 上构建/下载的 `wheels` 只给 Windows 用；在 **Linux/macOS** 上生成的依赖 wheel 不要与 Windows 混用（否则会出现缺依赖或无法安装的二进制包）。
2. **版本一致**：`wheels/` 内仅保留一个 `ai_sdlc-<version>-*.whl`，与 `pyproject.toml` / 标签版本一致。
3. **冒烟**：在目标平台解压后运行对应 `install_offline` 脚本，再按上文「安装后验证」执行 `ai-sdlc --help` 或 `python -m ai_sdlc --help`。
4. **发行说明**：在 Release Notes 中写明「离线包需与目标操作系统一致」，并指向本文档。
