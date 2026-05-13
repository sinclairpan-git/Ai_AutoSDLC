# AI-SDLC 用户指引

当前正式发布版：`v0.7.13`。

普通用户优先使用 GitHub Release 离线包或公司管理员提供的安装包。安装脚本会自己检测运行时；不要一上来就手动创建 venv、拼 pip 依赖或改 PATH。

## 第一章：全新用户 + 全新空项目

### 1. 创建项目目录

Windows 直接复制：

```powershell
# D:\work 是示例父目录，ui-test-platform 是示例项目名；可按需替换
cd D:\work
mkdir ui-test-platform
cd ui-test-platform
```

macOS 直接复制：

```bash
# ~/work 是示例父目录，ui-test-platform 是示例项目名；可按需替换
cd ~/work
mkdir ui-test-platform
cd ui-test-platform
```

Linux 直接复制：

```bash
# ~/work 是示例父目录，ui-test-platform 是示例项目名；可按需替换
cd ~/work
mkdir ui-test-platform
cd ui-test-platform
```

执行成功以后，你应该看到：

- 终端当前目录已经进入刚创建的项目目录；照抄示例时就是 `ui-test-platform`
- 这个目录现在还是空的，里面还没有业务代码

如果失败：

- `cd D:\work` 或 `cd ~/work` 失败：父目录不存在，先创建父目录，或换成真实存在的目录
- `mkdir` 提示目录已存在：换一个项目名，或确认这是你准备使用的空目录

### 2. 安装 AI-SDLC

先从 Release 下载与你机器匹配的 `v0.7.13` 安装包：

```text
https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/tag/v0.7.13
```

Windows x64 直接复制：

```powershell
# 回到项目父目录，让安装包目录和业务项目目录同级
cd ..
Invoke-WebRequest -Uri "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.7.13/ai-sdlc-offline-0.7.13-windows-amd64.zip" -OutFile "ai-sdlc-offline-0.7.13-windows-amd64.zip"
Expand-Archive -LiteralPath .\ai-sdlc-offline-0.7.13-windows-amd64.zip -DestinationPath .
cd .\ai-sdlc-offline-0.7.13-windows-amd64
powershell -ExecutionPolicy Bypass -File .\install_offline.ps1
.\.venv\Scripts\python.exe -m ai_sdlc --help
```

macOS Apple Silicon 直接复制：

```bash
# 回到项目父目录，让安装包目录和业务项目目录同级
cd ..
curl -L -o ai-sdlc-offline-0.7.13-macos-arm64.tar.gz "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.7.13/ai-sdlc-offline-0.7.13-macos-arm64.tar.gz"
tar xzf ai-sdlc-offline-0.7.13-macos-arm64.tar.gz
cd ai-sdlc-offline-0.7.13-macos-arm64
chmod +x install_offline.sh
./install_offline.sh
./.venv/bin/python -m ai_sdlc --help
```

Linux x64 直接复制：

```bash
# 回到项目父目录，让安装包目录和业务项目目录同级
cd ..
curl -L -o ai-sdlc-offline-0.7.13-linux-amd64.tar.gz "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.7.13/ai-sdlc-offline-0.7.13-linux-amd64.tar.gz"
tar xzf ai-sdlc-offline-0.7.13-linux-amd64.tar.gz
cd ai-sdlc-offline-0.7.13-linux-amd64
chmod +x install_offline.sh
./install_offline.sh
./.venv/bin/python -m ai_sdlc --help
```

执行成功以后，你应该看到：

- 安装脚本输出 `当前结果 / Result`
- 安装脚本输出 `下一步 / Next`
- 结果里包含“离线安装完成”或 `Offline installation completed`
- `--help` 输出里包含 `Usage` 和 `Commands`
- 命令列表里至少能看到 `init`、`adapter`、`run`、`self-update`

如果失败：

- 下载失败或 GitHub 访问慢：让公司管理员下载同平台包后拷贝给你，不要自己拼 `curl`、`tar` 或 `pip`
- `offline bundle platform mismatch`：安装包和当前系统 / CPU / Python ABI 不匹配，换对应平台包
- `need Python >= 3.11`：包内没有可用 Python runtime，换带 `python-runtime/` 的包，或让管理员重新发包
- Windows `running scripts is disabled`：继续使用 `powershell -ExecutionPolicy Bypass -File .\install_offline.ps1`
- `ai-sdlc` 不在 PATH：先用包内完整路径，例如 `.\.venv\Scripts\python.exe -m ai_sdlc --help` 或 `./.venv/bin/python -m ai_sdlc --help`

### 3. 回到空项目并初始化

安装包目录只是安装位置，不是业务项目。下一步必须回到刚创建的项目目录。

Windows 直接复制：

```powershell
# 回到你的业务项目目录；如果项目名不是 ui-test-platform，请替换路径
cd D:\work\ui-test-platform
..\ai-sdlc-offline-0.7.13-windows-amd64\.venv\Scripts\python.exe -m ai_sdlc init .
```

macOS 直接复制：

```bash
# 回到你的业务项目目录；如果项目名不是 ui-test-platform，请替换路径
cd ~/work/ui-test-platform
../ai-sdlc-offline-0.7.13-macos-arm64/.venv/bin/python -m ai_sdlc init .
```

Linux 直接复制：

```bash
# 回到你的业务项目目录；如果项目名不是 ui-test-platform，请替换路径
cd ~/work/ui-test-platform
../ai-sdlc-offline-0.7.13-linux-amd64/.venv/bin/python -m ai_sdlc init .
```

`v0.7.5` 起，`init` 会在你完成 AI 代理入口和 shell 选择后自动做安全预演。正常时你应该看到：

- 输出里包含 `Initialized AI-SDLC project`
- 输出里包含 `当前结果 / Result`
- 输出里包含 `下一步 / Next`
- `当前结果 / Result` 告诉你初始化完成，并说明安全预演已自动执行
- `下一步 / Next` 告诉你切换到 AI 对话输入需求

示例片段：

```text
Initialized AI-SDLC project

当前结果 / Result
  项目初始化完成，启动预演已执行。

下一步 / Next
  切换到 AI 对话窗口，输入你的需求。
```

如果失败：

- 只执行 CLI 在 `下一步 / Next` 里给出的那一条命令
- 如果提示 adapter target 不匹配，通常执行 `python -m ai_sdlc adapter select --agent-target <真实聊天入口>` 后再检查
- 如果提示 open gates，新空项目或未开始需求时可能正常；以 `下一步 / Next` 是否让你切换到聊天为准
- 如果你先初始化、后打开 IDE，先用 IDE 打开项目文件夹，再重新执行一次 `init`

### 4. 开始输入需求

完成 `init` 后，再到 Codex / Cursor / Claude Code / VS Code Chat 输入自然语言需求，例如：

```text
我已经在这个空项目根目录执行过 ai-sdlc init .。
现在我要从 0 到 1 做一个：<写你的需求>
```

不要把 `python -m ai_sdlc ...` 或 `ai-sdlc ...` 这类命令粘贴到聊天输入框。

## 第二章：全新用户 + 已有项目

### 1. 进入已有项目根目录

Windows 直接复制：

```powershell
# D:\work\my-existing-project 是示例路径；请替换成你的真实项目路径
cd D:\work\my-existing-project
git status
```

macOS 直接复制：

```bash
# ~/work/my-existing-project 是示例路径；请替换成你的真实项目路径
cd ~/work/my-existing-project
git status
```

Linux 直接复制：

```bash
# ~/work/my-existing-project 是示例路径；请替换成你的真实项目路径
cd ~/work/my-existing-project
git status
```

执行成功以后，你应该看到：

- 当前终端已经位于你的已有项目根目录
- 如果项目使用 Git，`git status` 会显示当前分支和工作区状态
- 如果工作区有未提交业务改动，先确认这些改动是不是你要保留的内容

如果失败：

- `git status` 提示不是 Git 仓库：可以继续，但要确认当前目录确实是你的业务项目根目录
- `cd` 失败：路径写错，先换成真实项目路径

### 2. 安装 AI-SDLC

已有项目也优先使用 `v0.7.13` Release 包或公司安装包。下面的命令会把安装包目录放在已有项目的父目录里，和业务项目目录同级。

Windows x64 直接复制：

```powershell
# 当前假设你还在 D:\work\my-existing-project；先回到父目录 D:\work
cd ..
Invoke-WebRequest -Uri "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.7.13/ai-sdlc-offline-0.7.13-windows-amd64.zip" -OutFile "ai-sdlc-offline-0.7.13-windows-amd64.zip"
Expand-Archive -LiteralPath .\ai-sdlc-offline-0.7.13-windows-amd64.zip -DestinationPath .
cd .\ai-sdlc-offline-0.7.13-windows-amd64
powershell -ExecutionPolicy Bypass -File .\install_offline.ps1
.\.venv\Scripts\python.exe -m ai_sdlc --help
```

macOS Apple Silicon 直接复制：

```bash
# 当前假设你还在 ~/work/my-existing-project；先回到父目录 ~/work
cd ..
curl -L -o ai-sdlc-offline-0.7.13-macos-arm64.tar.gz "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.7.13/ai-sdlc-offline-0.7.13-macos-arm64.tar.gz"
tar xzf ai-sdlc-offline-0.7.13-macos-arm64.tar.gz
cd ai-sdlc-offline-0.7.13-macos-arm64
chmod +x install_offline.sh
./install_offline.sh
./.venv/bin/python -m ai_sdlc --help
```

Linux x64 直接复制：

```bash
# 当前假设你还在 ~/work/my-existing-project；先回到父目录 ~/work
cd ..
curl -L -o ai-sdlc-offline-0.7.13-linux-amd64.tar.gz "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.7.13/ai-sdlc-offline-0.7.13-linux-amd64.tar.gz"
tar xzf ai-sdlc-offline-0.7.13-linux-amd64.tar.gz
cd ai-sdlc-offline-0.7.13-linux-amd64
chmod +x install_offline.sh
./install_offline.sh
./.venv/bin/python -m ai_sdlc --help
```

安装成功以后，你应该看到：

- `当前结果 / Result`
- `下一步 / Next`
- `--help` 输出中包含 `Usage`、`Commands`、`init`、`adapter`、`run`、`self-update`

如果失败：

- 下载失败或 GitHub 访问慢：让公司管理员下载同平台包后拷贝给你，不要自己拼 `curl`、`tar` 或 `pip`
- `offline bundle platform mismatch`：安装包和当前系统 / CPU / Python ABI 不匹配，换对应平台包
- `need Python >= 3.11`：包内没有可用 Python runtime，换带 `python-runtime/` 的包，或让管理员重新发包
- Windows `running scripts is disabled`：继续使用 `powershell -ExecutionPolicy Bypass -File .\install_offline.ps1`
- `ai-sdlc` 不在 PATH：先用包内完整路径，例如 `.\.venv\Scripts\python.exe -m ai_sdlc --help` 或 `./.venv/bin/python -m ai_sdlc --help`

### 3. 初始化已有项目

进入已有项目根目录后执行：

Windows 示例：

```powershell
# 先从安装包目录回到业务项目根目录；如果路径不同，请替换成真实项目路径
cd ..\my-existing-project
..\ai-sdlc-offline-0.7.13-windows-amd64\.venv\Scripts\python.exe -m ai_sdlc init .
```

macOS 示例：

```bash
# 先从安装包目录回到业务项目根目录；如果路径不同，请替换成真实项目路径
cd ../my-existing-project
../ai-sdlc-offline-0.7.13-macos-arm64/.venv/bin/python -m ai_sdlc init .
```

Linux 示例：

```bash
# 先从安装包目录回到业务项目根目录；如果路径不同，请替换成真实项目路径
cd ../my-existing-project
../ai-sdlc-offline-0.7.13-linux-amd64/.venv/bin/python -m ai_sdlc init .
```

正常时你应该看到：

- 输出里包含 `Initialized AI-SDLC project`
- 输出里包含 `当前结果 / Result`
- 输出里包含 `下一步 / Next`
- `下一步 / Next` 告诉你切换到 AI 对话输入增量需求

已有项目会保留你的业务代码；AI-SDLC 会初始化 `.ai-sdlc/`、adapter 指引文件和项目状态文件。若已有同名自定义 adapter 文件，框架不应直接覆盖。

如果失败：

- 只执行 CLI 输出里的 `下一步 / Next` 那一条命令
- 如果提示 target 不匹配，先选择真实聊天入口，再重新执行 `adapter status` 或 `init`
- 如果提示项目已有旧 `.ai-sdlc` 痕迹但状态不完整，按 CLI 给出的初始化 / 修复命令继续
- 如果已有大量未提交改动，先决定是否提交、暂存或继续保留；不要为了初始化而删除业务改动

### 4. 开始输入增量需求

完成 `init` 后，再到 AI 聊天入口输入需求，例如：

```text
我已经在这个已有项目根目录执行过 ai-sdlc init .。
现在我要在已有项目上新增/修改：<写你的需求>
```

## 第三章：老用户升级

### 1. `v0.7.6` 及以后的用户

在已经能正常运行 `ai-sdlc` 的终端里执行：

```bash
ai-sdlc self-update check
```

正常时你应该看到下面两类结果之一：

- 已是最新：输出说明没有可执行更新，当前版本已经满足要求
- 发现新版本：CLI 会检查、下载、安装并验证目标版本

升级成功以后，你应该看到：

- 输出包含更新完成或安装完成的信息
- 输出包含当前安装版本，例如 `Installed version: 0.7.13`
- 后续再执行 `ai-sdlc --version` 或 `ai-sdlc self-update check`，应显示新版本入口可用

如果失败：

- 输出 `Update check failed` 或“无法刷新 update state”：当前网络无法稳定访问 GitHub，改用本章第 2 节的安装包救援路径
- 输出“当前安装渠道未确认可自动升级”：改用本章第 2 节的安装包救援路径
- 更新后版本仍没有变化：说明 PATH 命中的还是旧入口，改用本章第 2 节的 `--upgrade-existing`

### 2. 更旧版本或 `No such command 'install'`

如果旧版本提示 `No such command 'install'`，说明旧 CLI 太老，不能靠旧 CLI 学会新子命令。直接下载最新平台包，并让安装包覆盖当前 `PATH` 命中的旧入口。

Windows x64：

```powershell
Invoke-WebRequest -Uri "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.7.13/ai-sdlc-offline-0.7.13-windows-amd64.zip" -OutFile "ai-sdlc-offline-0.7.13-windows-amd64.zip"
Expand-Archive -LiteralPath .\ai-sdlc-offline-0.7.13-windows-amd64.zip -DestinationPath .
cd .\ai-sdlc-offline-0.7.13-windows-amd64
powershell -ExecutionPolicy Bypass -File .\install_offline.ps1 -UpgradeExisting
ai-sdlc --version
ai-sdlc self-update check
```

macOS Apple Silicon：

```bash
curl -L -o ai-sdlc-offline-0.7.13-macos-arm64.tar.gz "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.7.13/ai-sdlc-offline-0.7.13-macos-arm64.tar.gz"
tar xzf ai-sdlc-offline-0.7.13-macos-arm64.tar.gz
cd ai-sdlc-offline-0.7.13-macos-arm64
./install_offline.sh --upgrade-existing
ai-sdlc --version
ai-sdlc self-update check
```

Linux x64：

```bash
curl -L -o ai-sdlc-offline-0.7.13-linux-amd64.tar.gz "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.7.13/ai-sdlc-offline-0.7.13-linux-amd64.tar.gz"
tar xzf ai-sdlc-offline-0.7.13-linux-amd64.tar.gz
cd ai-sdlc-offline-0.7.13-linux-amd64
./install_offline.sh --upgrade-existing
ai-sdlc --version
ai-sdlc self-update check
```

`--upgrade-existing` 的成功标准不是“安装包运行完”，而是当前 `ai-sdlc` 入口已经换成新版本。安装器会在结束前校验版本和 `self-update` 子命令；如果它无法安全覆盖旧入口，会直接报错并给下一步，不会假装成功。

### 3. 升级后回到项目检查

在业务项目根目录执行：

```bash
ai-sdlc init .
ai-sdlc adapter status
```

正常时你应该看到：

- `init` 或 `adapter status` 输出 `当前结果 / Result`
- `下一步 / Next` 给出唯一下一步
- 如果接入真值已验证，下一步通常是切换到 AI 对话输入需求

如果公司内网不允许访问 GitHub，可以关闭自动更新提醒。

Windows PowerShell：

```powershell
$env:AI_SDLC_DISABLE_UPDATE_CHECK = "1"
```

macOS / Linux：

```bash
export AI_SDLC_DISABLE_UPDATE_CHECK=1
```

## 附录：常用命令和常见报错

### 常用命令

| 命令 | 功能 |
| --- | --- |
| `ai-sdlc --help` | 查看 CLI 是否可用，以及当前支持的命令 |
| `ai-sdlc --version` | 查看当前安装版本 |
| `ai-sdlc init .` | 在当前项目初始化 AI-SDLC；新版本会自动执行必要检查和安全预演 |
| `ai-sdlc status` | 查看项目状态、阶段状态和关键路径 |
| `ai-sdlc adapter status` | 检查 AI 入口、adapter 接入真值和治理激活状态 |
| `ai-sdlc adapter status --json` | 查看机器可读的 adapter 真值 |
| `ai-sdlc adapter select` | 手工选择真实聊天入口 |
| `ai-sdlc adapter shell-select` | 选择项目偏好的终端 shell，并刷新 adapter 指引 |
| `ai-sdlc run --dry-run` | 手动重跑安全预演；通常只在排查时使用 |
| `ai-sdlc run` | 执行完整流水线 |
| `ai-sdlc stage show <阶段名>` | 查看某个阶段的清单 |
| `ai-sdlc stage run <阶段名> --dry-run` | 预演单个阶段 |
| `ai-sdlc workitem init --title "<标题>"` | 创建 formal work item 文档 |
| `ai-sdlc doctor` | 输出当前环境、PATH、shim、项目状态等诊断信息 |
| `ai-sdlc self-update check` | 检查、下载、安装并验证可用更新 |

如果 `ai-sdlc` 不在 PATH，但包内 Python 可用，可以把同一条命令改成：

```bash
python -m ai_sdlc <子命令>
```

### 常见报错

| 报错 / 现象 | 解决办法 |
| --- | --- |
| `ai-sdlc: command not found` / `ai-sdlc 不是内部或外部命令` | 用安装包输出的完整路径，或执行 `python -m ai_sdlc --help`；再用 `ai-sdlc doctor` 排查 PATH |
| `No module named ai_sdlc` | 当前 Python 环境没有安装 AI-SDLC；回到安装包目录重新安装 |
| `No such command 'install'` | 旧 CLI 太老；下载 `v0.7.13` 同平台包并执行 `--upgrade-existing` / `-UpgradeExisting` |
| `Update check failed` | GitHub 网络不可用或超时；用离线包救援升级 |
| `offline bundle platform mismatch` | 安装包平台不匹配；换 Windows x64、macOS arm64 或 Linux x64 对应包 |
| `need Python >= 3.11` | 包内没有可用 Python runtime 且系统 Python 太旧；换带 `python-runtime/` 的安装包 |
| Windows `running scripts is disabled` | 使用 `powershell -ExecutionPolicy Bypass -File .\install_offline.ps1` |
| `tar: command not found` / `curl: command not found` | 让管理员下载并解压包，或在具备这些工具的终端执行 |
| `init` 输出提示 adapter target 不匹配 | 按 `下一步 / Next` 执行 `adapter select`，选择真实聊天入口 |
| `init` 或 `run --dry-run` 显示 open gates | 看 `下一步 / Next` 和 `说明 / Notes`；新项目未开始需求时不一定是错误 |
| 在聊天框里粘贴命令没有反应 | 命令必须在终端执行；聊天框只输入自然语言需求 |
