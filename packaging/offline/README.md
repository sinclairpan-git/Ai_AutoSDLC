# 离线一键安装包（含 Windows）

> 当前 staged release：`v0.7.4`
>
> 发布入口口径：
> - Windows 使用 `ai-sdlc-offline-0.7.4.zip`
> - Linux/macOS 使用 `ai-sdlc-offline-0.7.4.tar.gz`
> - Release Notes：`docs/releases/v0.7.4.md`

## 角色分工

- 打包人（联网机器）：生成离线归档
- 使用人（离线机器）：解压后一键安装

## 一、打包（联网机器）

在仓库根目录执行：

```bash
chmod +x packaging/offline/build_offline_bundle.sh
./packaging/offline/build_offline_bundle.sh
```

若要让离线目标机在**完全没有 Python 3.11 预装**的情况下也能安装，请在打包时额外提供可分发的便携 Python runtime：

```bash
AI_SDLC_OFFLINE_PYTHON_RUNTIME=/path/to/python-runtime \
  ./packaging/offline/build_offline_bundle.sh
```

产物：

- `dist-offline/ai-sdlc-offline-<version>.tar.gz`（Linux/macOS 推荐）
- `dist-offline/ai-sdlc-offline-<version>.zip`（Windows 推荐）
- `dist-offline/ai-sdlc-offline-<version>/bundle-manifest.json`（记录 bundle 适用的 OS/CPU 平台）
- `dist-offline/ai-sdlc-offline-<version>/python-runtime/`（可选；若打包时提供，则离线机无需自备 Python）

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

如果 bundle 的 `bundle-manifest.json` 与当前机器 OS/CPU 不匹配，安装脚本会直接拒绝安装。若 bundle 内含 `python-runtime/`，安装脚本会优先使用 bundle 自带 runtime；否则才回退到系统已安装的 Python 3.11+。

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

然后进入业务项目目录，执行初始化入口。`init` 会自动完成必要检查和安全预演：

```bash
ai-sdlc init .
```

CLI 安装器与后续命令提示均会以中英双语输出以下信息：

- 当前结果 / Result
- 下一步 / Next
- 说明 / Notes（仅在需要时出现）

## 平台兼容提醒

离线包中的依赖 wheel 可能与操作系统/CPU 架构相关。请尽量：

- 在与目标机相同的平台打包
- 或为 Windows、macOS 分别提供对应离线包

避免将 macOS 打出的离线包直接用于 Windows（反之亦然）。

补充约束：

- `.zip` 已生成，只代表 Windows 分发归档已产出，不代表 Windows 安装已经冒烟通过
- `.tar.gz` 已生成，只代表 POSIX 分发归档已产出，不代表 Linux/macOS 安装已经冒烟通过
- 若要对外同时承诺 Windows 和 POSIX 都支持“无需预装 Python 3.11+”，必须分别在对应目标平台执行真实安装验证
- 若当前手里没有 Windows 实机，可运行 GitHub Actions 工作流 [windows-offline-smoke.yml](/Users/sinclairpan/project/Ai_AutoSDLC/.github/workflows/windows-offline-smoke.yml) 获取 Windows 目标机安装证据；只有工作流成功并产出 artifact 后，才能把它记为 Windows smoke 证据
- 上述 CI 工作流产出的是 Windows smoke 证据，不是正式对外交付的离线包来源；正式发布物仍应来自你认可的目标平台构建流程
- 若希望由云端生成正式发布资产，可运行 GitHub Actions 工作流 [release-build.yml](/Users/sinclairpan/project/Ai_AutoSDLC/.github/workflows/release-build.yml)。该 workflow 在 Windows / macOS / Linux runner 上分别构建、安装 smoke，并把通过 smoke 的平台资产上传到既有 GitHub Release
- 发布 `v0.7.4` 后，可运行 GitHub Actions 工作流 [release-artifact-smoke.yml](/Users/sinclairpan/project/Ai_AutoSDLC/.github/workflows/release-artifact-smoke.yml) 从 GitHub Release 下载正式 `.zip` / `.tar.gz` 资产并执行安装冒烟；该证据证明的是发布资产，而不是当前源码树临时构建产物

## 四、脚本说明

- `build_offline_bundle.sh`：构建主包并下载依赖，输出 `.tar.gz` + `.zip`；若提供 `AI_SDLC_OFFLINE_PYTHON_RUNTIME`，会一并打入便携 Python runtime
- `bundle-manifest.json`：记录 bundle 的 package version、build OS、CPU 架构
- `install_offline.sh`：Linux/macOS 一键离线安装，并校验 `bundle-manifest.json`
- `install_offline.ps1` / `install_offline.bat`：Windows 一键离线安装，并校验 `bundle-manifest.json`

`dist-offline/` 是本地构建产物，已在 `.gitignore` 中忽略，不提交二进制包。

## 五、发布检查清单（维护者）

基础检查仍然是：

1. **平台匹配**：在 **Windows** 上构建/下载的 `wheels` 只给 Windows 用；在 **Linux/macOS** 上生成的依赖 wheel 不要与 Windows 混用（否则会出现缺依赖或无法安装的二进制包）。若捆绑 `python-runtime/`，runtime 本身也必须与目标机 OS/CPU 匹配。
2. **版本一致**：`wheels/` 内仅保留一个 `ai_sdlc-<version>-*.whl`，与 `pyproject.toml` / 标签版本一致。
3. **冒烟**：在目标平台解压后运行对应 `install_offline` 脚本，再按上文「安装后验证」执行 `ai-sdlc --help` 或 `python -m ai_sdlc --help`。
4. **发行说明**：在 Release Notes 中写明「离线包需与目标操作系统一致」，并指向本文档。

若本次离线 bundle 要对外承诺“**目标机无需预装 Python 3.11+**”，则必须额外执行专门的 runtime 发布清单：

- [RELEASE_CHECKLIST.md](/Users/sinclairpan/project/Ai_AutoSDLC/packaging/offline/RELEASE_CHECKLIST.md)

该清单把 `python-runtime/` 的必备产物、manifest 要求、无系统 Python 冒烟、以及 release notes 文案一并锁成正式收口条件。
