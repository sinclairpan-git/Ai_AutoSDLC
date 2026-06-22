# AI-SDLC 用户指引

当前正式发布版：`v0.8.4`。

普通用户优先使用 GitHub Release 离线包或公司管理员提供的安装包。安装脚本会自己检测运行时；不要一上来就手动创建 venv、拼 pip 依赖或改 PATH。

## 企业 AgentOps 接入

个人单机用户不需要配置 AgentOps。本手册后续章节只描述普通个人/项目使用路径，不混入企业接入步骤。

如果你所在部门要求 AI-SDLC 强制接入 AgentOps，请先按企业内部提供的一次性脚本完成接入。脚本会写入用户级企业 profile，并设置 AgentOps token 环境变量；之后 `ai-sdlc run` 会自动进入企业 required 上报模式。

企业接入步骤单独见：[企业 AgentOps 接入指南](docs/enterprise-agentops-setup.zh-CN.md)。

## 命令入口规则：PATH 与无 PATH

本手册推荐安装时显式同意写入 PATH，这样后续可以直接执行 `ai-sdlc ...`。Windows 用 `-AddToPath`，macOS / Linux 用 `--add-to-path`。这些参数本身就是写入 PATH 的确认信号；安装器不会再弹出第二次确认。

Windows 注意：如果你是用 `powershell -ExecutionPolicy Bypass -File ... -AddToPath` 启动安装脚本，PATH 会写入用户 PATH，通常需要新开一个终端后裸 `ai-sdlc ...` 才会被父终端识别。安装完成后的当前终端如果要立刻初始化项目，请使用安装脚本最后打印的 Direct shim；否则裸 `ai-sdlc init .` 可能仍解析到机器上已有的旧版本。可用 `Get-Command ai-sdlc | Select-Object Source` 检查当前命中的入口。

写入 PATH 后并且新终端已经识别新 PATH 时，通用命令就是：

| 命令 | 用途 |
| --- | --- |
| `ai-sdlc --help` | 查看 CLI 是否可用，以及当前支持的命令 |
| `ai-sdlc --version` | 查看当前安装版本 |
| `ai-sdlc init .` | 在当前项目初始化 AI-SDLC |
| `ai-sdlc adapter status` | 排查 AI 入口和规则安装状态；普通开发主路径通常不需要手动执行 |
| `ai-sdlc workitem guard` | 查看当前是否已绑定下一条可执行任务 |

如果没有写入 PATH，不能直接照抄 `ai-sdlc ...`。必须把命令前缀替换为安装包内 Python 入口。

注意：下面的相对路径只适用于你还在安装包目录里验证 CLI 的场景。如果要先 `cd` 到业务项目目录再执行 `init .`，必须使用安装脚本最后打印的**完整 Python 路径**，因为 `.\.venv` 或 `./.venv` 已经不再指向安装包里的运行环境。

| 平台 | 前缀 |
| --- | --- |
| Windows | `.\.venv\Scripts\python.exe -m ai_sdlc` |
| macOS / Linux | `./.venv/bin/python -m ai_sdlc` |

例如：`ai-sdlc init .` 要改成安装脚本输出里的 `...\python.exe -m ai_sdlc init .` 或 `.../bin/python -m ai_sdlc init .`。

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

这里分两种场景。不要把两套命令混用：

- **场景 A：安装包已经提前下载好**，并且放在当前终端目录里
- **场景 B：当前机器可以访问 GitHub**，直接从 Release 下载、解压并安装

```text
https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/tag/v0.8.4
```

#### 场景 A：已提前下载离线包

Windows x64 直接复制：

```powershell
# 当前假设你已经 cd 到 zip 所在目录；脚本只检查当前目录，不扫描其他目录
# This assumes you have cd'ed into the directory containing the zip. The script checks only the current directory.
$PackageName = "ai-sdlc-offline-0.8.4-windows-amd64.zip"
$BundleName = "ai-sdlc-offline-0.8.4-windows-amd64"
$PackageDir = (Get-Location).Path
$ExtractRoot = Join-Path $PackageDir ".ai-sdlc-install"
$Zip = Get-ChildItem -LiteralPath . -Filter $PackageName -File | Select-Object -First 1
if (-not $Zip) {
  Write-Host "当前目录没有找到安装包：$PackageDir\$PackageName"
  Write-Host "Package not found in the current directory: $PackageDir\$PackageName"
  throw "请把 zip 放到当前目录，并先 cd 到该目录后重试。Place the zip in the current directory, cd into that directory, then retry."
}
New-Item -ItemType Directory -Path $ExtractRoot -Force | Out-Null
Write-Host "正在解压安装包；如果已经解压过，会安静覆盖同名文件。"
Write-Host "Extracting package; existing installer files will be overwritten quietly."
Expand-Archive -LiteralPath $Zip.FullName -DestinationPath $ExtractRoot -Force
Set-Location (Join-Path $ExtractRoot $BundleName)
powershell -ExecutionPolicy Bypass -File .\install_offline.ps1 -AddToPath
.\.venv\Scripts\python.exe -m ai_sdlc --help
```

如果你的 PowerShell 粘贴多行时把命令显示成连续的 `>>` 提示，改复制下面这一行执行：

```powershell
$PackageName = "ai-sdlc-offline-0.8.4-windows-amd64.zip"; $BundleName = "ai-sdlc-offline-0.8.4-windows-amd64"; $PackageDir = (Get-Location).Path; $ExtractRoot = Join-Path $PackageDir ".ai-sdlc-install"; New-Item -ItemType Directory -Path $ExtractRoot -Force | Out-Null; Expand-Archive -LiteralPath (Join-Path $PackageDir $PackageName) -DestinationPath $ExtractRoot -Force; Set-Location (Join-Path $ExtractRoot $BundleName); powershell -ExecutionPolicy Bypass -File .\install_offline.ps1 -AddToPath; .\.venv\Scripts\python.exe -m ai_sdlc --help
```

macOS Apple Silicon 直接复制：

```bash
# 当前假设你已经 cd 到 tar.gz 所在目录；脚本只检查当前目录，不扫描其他目录
# This assumes you have cd'ed into the directory containing the tar.gz. The script checks only the current directory.
install_ai_sdlc_offline() {
  PackageName="ai-sdlc-offline-0.8.4-macos-arm64.tar.gz"
  PackageDir="$(pwd)"
  if [ ! -f "$PackageName" ]; then
    echo "当前目录没有找到安装包：$PackageDir/$PackageName"
    echo "Package not found in the current directory: $PackageDir/$PackageName"
    echo "请把 tar.gz 放到当前目录，并先 cd 到该目录后重试。Place the tar.gz in the current directory, cd into that directory, then retry."
    return 1
  fi
  tar xzf "$PackageName"
  cd ai-sdlc-offline-0.8.4-macos-arm64
  chmod +x install_offline.sh
  ./install_offline.sh --add-to-path
  ai-sdlc --help
}
install_ai_sdlc_offline
```

Linux x64 直接复制：

```bash
# 当前假设你已经 cd 到 tar.gz 所在目录；脚本只检查当前目录，不扫描其他目录
# This assumes you have cd'ed into the directory containing the tar.gz. The script checks only the current directory.
install_ai_sdlc_offline() {
  PackageName="ai-sdlc-offline-0.8.4-linux-amd64.tar.gz"
  PackageDir="$(pwd)"
  if [ ! -f "$PackageName" ]; then
    echo "当前目录没有找到安装包：$PackageDir/$PackageName"
    echo "Package not found in the current directory: $PackageDir/$PackageName"
    echo "请把 tar.gz 放到当前目录，并先 cd 到该目录后重试。Place the tar.gz in the current directory, cd into that directory, then retry."
    return 1
  fi
  tar xzf "$PackageName"
  cd ai-sdlc-offline-0.8.4-linux-amd64
  chmod +x install_offline.sh
  ./install_offline.sh --add-to-path
  ai-sdlc --help
}
install_ai_sdlc_offline
```

#### 场景 B：在线从 Release 下载并安装

Windows x64 直接复制：

```powershell
# 回到项目父目录，让安装包目录和业务项目目录同级
cd ..
$BundleName = "ai-sdlc-offline-0.8.4-windows-amd64"
$PackageName = "$BundleName.zip"
$PackageDir = (Get-Location).Path
$ExtractRoot = Join-Path $PackageDir ".ai-sdlc-install"
Invoke-WebRequest -Uri "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.8.4/$PackageName" -OutFile (Join-Path $PackageDir $PackageName)
New-Item -ItemType Directory -Path $ExtractRoot -Force | Out-Null
Write-Host "正在解压安装包；如果已经解压过，会安静覆盖同名文件。"
Write-Host "Extracting package; existing installer files will be overwritten quietly."
Expand-Archive -LiteralPath (Join-Path $PackageDir $PackageName) -DestinationPath $ExtractRoot -Force
Set-Location (Join-Path $ExtractRoot $BundleName)
powershell -ExecutionPolicy Bypass -File .\install_offline.ps1 -AddToPath
.\.venv\Scripts\python.exe -m ai_sdlc --help
```

如果你的 PowerShell 粘贴多行时把命令显示成连续的 `>>` 提示，改复制下面这一行执行：

```powershell
Set-Location ..; $BundleName = "ai-sdlc-offline-0.8.4-windows-amd64"; $PackageName = "$BundleName.zip"; $PackageDir = (Get-Location).Path; $ExtractRoot = Join-Path $PackageDir ".ai-sdlc-install"; Invoke-WebRequest -Uri "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.8.4/$PackageName" -OutFile (Join-Path $PackageDir $PackageName); New-Item -ItemType Directory -Path $ExtractRoot -Force | Out-Null; Expand-Archive -LiteralPath (Join-Path $PackageDir $PackageName) -DestinationPath $ExtractRoot -Force; Set-Location (Join-Path $ExtractRoot $BundleName); powershell -ExecutionPolicy Bypass -File .\install_offline.ps1 -AddToPath; .\.venv\Scripts\python.exe -m ai_sdlc --help
```

macOS Apple Silicon 直接复制：

```bash
# 回到项目父目录，让安装包目录和业务项目目录同级
cd ..
curl -L -o ai-sdlc-offline-0.8.4-macos-arm64.tar.gz "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.8.4/ai-sdlc-offline-0.8.4-macos-arm64.tar.gz"
tar xzf ai-sdlc-offline-0.8.4-macos-arm64.tar.gz
cd ai-sdlc-offline-0.8.4-macos-arm64
chmod +x install_offline.sh
./install_offline.sh --add-to-path
ai-sdlc --help
```

Linux x64 直接复制：

```bash
# 回到项目父目录，让安装包目录和业务项目目录同级
cd ..
curl -L -o ai-sdlc-offline-0.8.4-linux-amd64.tar.gz "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.8.4/ai-sdlc-offline-0.8.4-linux-amd64.tar.gz"
tar xzf ai-sdlc-offline-0.8.4-linux-amd64.tar.gz
cd ai-sdlc-offline-0.8.4-linux-amd64
chmod +x install_offline.sh
./install_offline.sh --add-to-path
ai-sdlc --help
```

执行成功以后，你应该看到：

- 安装脚本输出 `Result` / `Next`；macOS 和 Linux 也可能显示 `当前结果 / Result` / `下一步 / Next`
- 结果里包含“离线安装完成”或 `Offline installation completed`
- `--help` 输出里包含 `Usage` 和 `Commands`
- 命令列表里至少能看到 `init`、`adapter`、`run`、`self-update`

如果失败：

- 下载失败或 GitHub 访问慢：让公司管理员下载同平台包后拷贝给你，不要自己拼 `curl`、`tar` 或 `pip`
- `offline bundle platform mismatch`：安装包和当前系统 / CPU / Python ABI 不匹配，换对应平台包
- `need Python >= 3.11`：包内没有可用 Python runtime，换带 `python-runtime/` 的包，或让管理员重新发包
- Windows `running scripts is disabled`：继续使用 `powershell -ExecutionPolicy Bypass -File .\install_offline.ps1`
- Windows `ExpandArchiveFileExists`：说明旧命令正在重复解压到同一目录；改用本章带 `.ai-sdlc-install` 和 `-Force` 的 Windows 命令
- `ai-sdlc` 不在 PATH：先用包内完整路径，例如 `.\.venv\Scripts\python.exe -m ai_sdlc --help` 或 `./.venv/bin/python -m ai_sdlc --help`

### 3. 回到空项目并初始化

安装包目录只是安装位置，不是业务项目。下一步统一回到刚创建的项目目录执行初始化；不要在安装包目录里执行 `init`。

Windows 当前终端立即初始化时，不要直接照抄裸 `ai-sdlc init .`。先回到项目根目录，然后复制安装脚本刚刚输出的 `Direct shim` 里的 `init .` 那一行执行；下面是形状示例，路径必须替换成你终端里实际打印的完整路径：

```powershell
# D:\work\ui-test-platform 是示例路径；请替换成你的真实项目根目录
cd D:\work\ui-test-platform
& "D:\work\.ai-sdlc-install\ai-sdlc-offline-0.8.4-windows-amd64\.venv\Scripts\ai-sdlc.exe" init .
```

如果你已经新开了一个终端，并且 `Get-Command ai-sdlc | Select-Object Source` 显示的是刚安装的 `0.8.4` 路径，也可以执行：

```powershell
cd D:\work\ui-test-platform
ai-sdlc init .
```

macOS 直接复制：

```bash
# ~/work/ui-test-platform 是示例路径；请替换成你的真实项目根目录
cd ~/work/ui-test-platform
ai-sdlc init .
```

Linux 直接复制：

```bash
# ~/work/ui-test-platform 是示例路径；请替换成你的真实项目根目录
cd ~/work/ui-test-platform
ai-sdlc init .
```

如果 `ai-sdlc` 不在 PATH，使用安装脚本最后输出的完整 Python 路径，把 `--help` 换成 `init .` 后在业务项目根目录执行。

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

已有项目也优先使用 `v0.8.4` Release 包或公司安装包。这里也分两种场景：已提前下载离线包，或在线从 Release 下载并安装。

#### 场景 A：已提前下载离线包

Windows x64 直接复制：

```powershell
# 当前假设你已经 cd 到 zip 所在目录；脚本只检查当前目录，不扫描其他目录
# This assumes you have cd'ed into the directory containing the zip. The script checks only the current directory.
$PackageName = "ai-sdlc-offline-0.8.4-windows-amd64.zip"
$BundleName = "ai-sdlc-offline-0.8.4-windows-amd64"
$PackageDir = (Get-Location).Path
$ExtractRoot = Join-Path $PackageDir ".ai-sdlc-install"
$Zip = Get-ChildItem -LiteralPath . -Filter $PackageName -File | Select-Object -First 1
if (-not $Zip) {
  Write-Host "当前目录没有找到安装包：$PackageDir\$PackageName"
  Write-Host "Package not found in the current directory: $PackageDir\$PackageName"
  throw "请把 zip 放到当前目录，并先 cd 到该目录后重试。Place the zip in the current directory, cd into that directory, then retry."
}
New-Item -ItemType Directory -Path $ExtractRoot -Force | Out-Null
Write-Host "正在解压安装包；如果已经解压过，会安静覆盖同名文件。"
Write-Host "Extracting package; existing installer files will be overwritten quietly."
Expand-Archive -LiteralPath $Zip.FullName -DestinationPath $ExtractRoot -Force
Set-Location (Join-Path $ExtractRoot $BundleName)
powershell -ExecutionPolicy Bypass -File .\install_offline.ps1 -AddToPath
.\.venv\Scripts\python.exe -m ai_sdlc --help
```

macOS Apple Silicon 直接复制：

```bash
# 当前假设你已经 cd 到 tar.gz 所在目录；脚本只检查当前目录，不扫描其他目录
# This assumes you have cd'ed into the directory containing the tar.gz. The script checks only the current directory.
install_ai_sdlc_offline() {
  PackageName="ai-sdlc-offline-0.8.4-macos-arm64.tar.gz"
  PackageDir="$(pwd)"
  if [ ! -f "$PackageName" ]; then
    echo "当前目录没有找到安装包：$PackageDir/$PackageName"
    echo "Package not found in the current directory: $PackageDir/$PackageName"
    echo "请把 tar.gz 放到当前目录，并先 cd 到该目录后重试。Place the tar.gz in the current directory, cd into that directory, then retry."
    return 1
  fi
  tar xzf "$PackageName"
  cd ai-sdlc-offline-0.8.4-macos-arm64
  chmod +x install_offline.sh
  ./install_offline.sh --add-to-path
  ai-sdlc --help
}
install_ai_sdlc_offline
```

Linux x64 直接复制：

```bash
# 当前假设你已经 cd 到 tar.gz 所在目录；脚本只检查当前目录，不扫描其他目录
# This assumes you have cd'ed into the directory containing the tar.gz. The script checks only the current directory.
install_ai_sdlc_offline() {
  PackageName="ai-sdlc-offline-0.8.4-linux-amd64.tar.gz"
  PackageDir="$(pwd)"
  if [ ! -f "$PackageName" ]; then
    echo "当前目录没有找到安装包：$PackageDir/$PackageName"
    echo "Package not found in the current directory: $PackageDir/$PackageName"
    echo "请把 tar.gz 放到当前目录，并先 cd 到该目录后重试。Place the tar.gz in the current directory, cd into that directory, then retry."
    return 1
  fi
  tar xzf "$PackageName"
  cd ai-sdlc-offline-0.8.4-linux-amd64
  chmod +x install_offline.sh
  ./install_offline.sh --add-to-path
  ai-sdlc --help
}
install_ai_sdlc_offline
```

#### 场景 B：在线从 Release 下载并安装

Windows x64 直接复制：

```powershell
# 当前假设你还在 D:\work\my-existing-project；先回到父目录 D:\work
cd ..
$BundleName = "ai-sdlc-offline-0.8.4-windows-amd64"
$PackageName = "$BundleName.zip"
$PackageDir = (Get-Location).Path
$ExtractRoot = Join-Path $PackageDir ".ai-sdlc-install"
Invoke-WebRequest -Uri "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.8.4/$PackageName" -OutFile (Join-Path $PackageDir $PackageName)
New-Item -ItemType Directory -Path $ExtractRoot -Force | Out-Null
Write-Host "正在解压安装包；如果已经解压过，会安静覆盖同名文件。"
Write-Host "Extracting package; existing installer files will be overwritten quietly."
Expand-Archive -LiteralPath (Join-Path $PackageDir $PackageName) -DestinationPath $ExtractRoot -Force
Set-Location (Join-Path $ExtractRoot $BundleName)
powershell -ExecutionPolicy Bypass -File .\install_offline.ps1 -AddToPath
.\.venv\Scripts\python.exe -m ai_sdlc --help
```

macOS Apple Silicon 直接复制：

```bash
# 当前假设你还在 ~/work/my-existing-project；先回到父目录 ~/work
cd ..
curl -L -o ai-sdlc-offline-0.8.4-macos-arm64.tar.gz "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.8.4/ai-sdlc-offline-0.8.4-macos-arm64.tar.gz"
tar xzf ai-sdlc-offline-0.8.4-macos-arm64.tar.gz
cd ai-sdlc-offline-0.8.4-macos-arm64
chmod +x install_offline.sh
./install_offline.sh --add-to-path
ai-sdlc --help
```

Linux x64 直接复制：

```bash
# 当前假设你还在 ~/work/my-existing-project；先回到父目录 ~/work
cd ..
curl -L -o ai-sdlc-offline-0.8.4-linux-amd64.tar.gz "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.8.4/ai-sdlc-offline-0.8.4-linux-amd64.tar.gz"
tar xzf ai-sdlc-offline-0.8.4-linux-amd64.tar.gz
cd ai-sdlc-offline-0.8.4-linux-amd64
chmod +x install_offline.sh
./install_offline.sh --add-to-path
ai-sdlc --help
```

安装成功以后，你应该看到：

- `Result` / `Next`；macOS 和 Linux 也可能显示 `当前结果 / Result` / `下一步 / Next`
- `--help` 输出中包含 `Usage`、`Commands`、`init`、`adapter`、`run`、`self-update`

如果失败：

- 下载失败或 GitHub 访问慢：让公司管理员下载同平台包后拷贝给你，不要自己拼 `curl`、`tar` 或 `pip`
- `offline bundle platform mismatch`：安装包和当前系统 / CPU / Python ABI 不匹配，换对应平台包
- `need Python >= 3.11`：包内没有可用 Python runtime，换带 `python-runtime/` 的包，或让管理员重新发包
- Windows `running scripts is disabled`：继续使用 `powershell -ExecutionPolicy Bypass -File .\install_offline.ps1`
- Windows `ExpandArchiveFileExists`：说明旧命令正在重复解压到同一目录；改用本章带 `.ai-sdlc-install` 和 `-Force` 的 Windows 命令
- `ai-sdlc` 不在 PATH：先用包内完整路径，例如 `.\.venv\Scripts\python.exe -m ai_sdlc --help` 或 `./.venv/bin/python -m ai_sdlc --help`

### 3. 初始化已有项目

进入已有项目根目录后执行；不要在安装包目录里执行 `init`。

Windows 当前终端立即初始化时，不要直接照抄裸 `ai-sdlc init .`。先进入已有项目根目录，然后复制安装脚本刚刚输出的 `Direct shim` 里的 `init .` 那一行执行；下面是形状示例，路径必须替换成你终端里实际打印的完整路径：

```powershell
# D:\work\my-existing-project 是示例路径；请替换成你的真实项目根目录
cd D:\work\my-existing-project
& "D:\work\.ai-sdlc-install\ai-sdlc-offline-0.8.4-windows-amd64\.venv\Scripts\ai-sdlc.exe" init .
```

如果你已经新开了一个终端，并且 `Get-Command ai-sdlc | Select-Object Source` 显示的是刚安装的 `0.8.4` 路径，也可以执行：

```powershell
cd D:\work\my-existing-project
ai-sdlc init .
```

macOS 示例：

```bash
# ~/work/my-existing-project 是示例路径；请替换成你的真实项目根目录
cd ~/work/my-existing-project
ai-sdlc init .
```

Linux 示例：

```bash
# ~/work/my-existing-project 是示例路径；请替换成你的真实项目根目录
cd ~/work/my-existing-project
ai-sdlc init .
```

如果 `ai-sdlc` 不在 PATH，使用安装脚本最后输出的完整 Python 路径，把 `--help` 换成 `init .` 后在业务项目根目录执行。

正常时你应该看到：

- 输出里包含 `Initialized AI-SDLC project`
- 输出里包含 `当前结果 / Result`
- 输出里包含 `下一步 / Next`
- `下一步 / Next` 告诉你切换到 AI 对话输入增量需求

已有项目会保留你的业务代码；AI-SDLC 会初始化 `.ai-sdlc/`、adapter 指引文件和项目状态文件。若已有同名自定义 adapter 文件，框架不应直接覆盖。

如果失败：

- 只执行 CLI 输出里的 `下一步 / Next` 那一条命令
- 如果提示 target 不匹配，先选择真实聊天入口；普通开发主路径不需要手动证明宿主已加载规则
- 如果提示项目已有旧 `.ai-sdlc` 痕迹但状态不完整，按 CLI 给出的初始化 / 修复命令继续
- 如果已有大量未提交改动，先决定是否提交、暂存或继续保留；不要为了初始化而删除业务改动

### 4. 接入已有任务进度

如果项目里已经有 JSON、Markdown、TODO、issue 导出或 Git 提交记录承载任务进度，初始化后可以直接执行：

```bash
ai-sdlc adopt .
```

正常时你应该看到：

- 输出标题包含“接入已有项目”
- 输出说明“原任务文件不会被修改”
- 生成 `.ai-sdlc/adoption/adoption-map.json`
- 生成 `.ai-sdlc/adoption/bridge.md`
- 生成继续点候选文件（`.ai-sdlc/adoption/checkpoint-candidate.json`）；普通用户不需要手动理解或编辑这个文件
- 输出推荐继续点和置信度

如果推荐继续点不对，用自然语言纠偏，不需要学习 checkpoint 或 reconcile：

```bash
ai-sdlc adopt . --prefer "支付回调"
```

### 5. 开始输入增量需求

完成 `init` 后，再到 AI 聊天入口输入需求，例如：

```text
我已经在这个已有项目根目录执行过 ai-sdlc init .。
现在我要在已有项目上新增/修改：<写你的需求>
```

## 第三章：老用户升级

### 1. `v0.7.6` 及以后的用户

在已经能正常运行 `ai-sdlc` 的终端里执行。执行目录不要求是业务项目根目录；`self-update check` 会使用系统临时目录完成下载和解压，不会把升级安装包或 `.ai-sdlc-install` 写进当前项目。

```bash
ai-sdlc self-update check
```

正常时你应该看到下面两类结果之一：

- 已是最新：输出说明没有可执行更新，当前版本已经满足要求
- 发现新版本：CLI 会检查、下载、安装并验证目标版本

升级成功以后，你应该看到：

- 输出包含更新完成或安装完成的信息
- 输出包含当前安装版本，例如 `Installed version: 0.8.4`
- 后续再执行 `ai-sdlc --version` 或 `ai-sdlc self-update check`，应显示新版本入口可用

如果失败：

- 输出 `Update check failed` 或“无法刷新 update state”：当前网络无法稳定访问 GitHub，改用本章第 2 节的安装包救援路径
- 输出“当前安装渠道未确认可自动升级”：改用本章第 2 节的安装包救援路径
- 更新后版本仍没有变化：说明 PATH 命中的还是旧入口，改用本章第 2 节的 `--upgrade-existing`

### 2. 更旧版本或 `No such command 'install'`

如果旧版本提示 `No such command 'install'`，说明旧 CLI 太老，不能靠旧 CLI 学会新子命令。直接下载最新平台包，并让安装包覆盖当前 `PATH` 命中的旧入口。

下面的救援升级命令请在业务项目父目录或临时下载目录执行，不要在业务项目根目录执行。命令会把安装包和 `.ai-sdlc-install` 解压目录放到当前目录，并自动进入解压后的安装包目录运行升级脚本；升级完成后再回到业务项目根目录继续。

Windows x64：

```powershell
$BundleName = "ai-sdlc-offline-0.8.4-windows-amd64"
$PackageName = "$BundleName.zip"
$PackageDir = (Get-Location).Path
$ExtractRoot = Join-Path $PackageDir ".ai-sdlc-install"
Invoke-WebRequest -Uri "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.8.4/$PackageName" -OutFile (Join-Path $PackageDir $PackageName)
New-Item -ItemType Directory -Path $ExtractRoot -Force | Out-Null
Write-Host "正在解压安装包；如果已经解压过，会安静覆盖同名文件。"
Write-Host "Extracting package; existing installer files will be overwritten quietly."
Expand-Archive -LiteralPath (Join-Path $PackageDir $PackageName) -DestinationPath $ExtractRoot -Force
Set-Location (Join-Path $ExtractRoot $BundleName)
powershell -ExecutionPolicy Bypass -File .\install_offline.ps1 -UpgradeExisting
ai-sdlc --version
ai-sdlc self-update check
```

如果你的 PowerShell 粘贴多行时把命令显示成连续的 `>>` 提示，改复制下面这一行执行：

```powershell
$BundleName = "ai-sdlc-offline-0.8.4-windows-amd64"; $PackageName = "$BundleName.zip"; $PackageDir = (Get-Location).Path; $ExtractRoot = Join-Path $PackageDir ".ai-sdlc-install"; Invoke-WebRequest -Uri "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.8.4/$PackageName" -OutFile (Join-Path $PackageDir $PackageName); New-Item -ItemType Directory -Path $ExtractRoot -Force | Out-Null; Expand-Archive -LiteralPath (Join-Path $PackageDir $PackageName) -DestinationPath $ExtractRoot -Force; Set-Location (Join-Path $ExtractRoot $BundleName); powershell -ExecutionPolicy Bypass -File .\install_offline.ps1 -UpgradeExisting; ai-sdlc --version; ai-sdlc self-update check
```

macOS Apple Silicon：

```bash
curl -L -o ai-sdlc-offline-0.8.4-macos-arm64.tar.gz "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.8.4/ai-sdlc-offline-0.8.4-macos-arm64.tar.gz"
tar xzf ai-sdlc-offline-0.8.4-macos-arm64.tar.gz
cd ai-sdlc-offline-0.8.4-macos-arm64
./install_offline.sh --upgrade-existing
ai-sdlc --version
ai-sdlc self-update check
```

Linux x64：

```bash
curl -L -o ai-sdlc-offline-0.8.4-linux-amd64.tar.gz "https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/v0.8.4/ai-sdlc-offline-0.8.4-linux-amd64.tar.gz"
tar xzf ai-sdlc-offline-0.8.4-linux-amd64.tar.gz
cd ai-sdlc-offline-0.8.4-linux-amd64
./install_offline.sh --upgrade-existing
ai-sdlc --version
ai-sdlc self-update check
```

`--upgrade-existing` 的成功标准不是“安装包运行完”，而是当前 `ai-sdlc` 入口已经换成新版本。安装器会在结束前校验版本和 `self-update` 子命令；如果它无法安全覆盖旧入口，会直接报错并给下一步，不会假装成功。

### 3. 升级后回到项目继续

升级命令不在业务项目根目录执行；升级完成以后，才回到业务项目根目录执行：

```bash
ai-sdlc init .
```

正常时你应该看到：

- `init` 输出 `当前结果 / Result`
- `下一步 / Next` 给出唯一下一步
- 下一步通常是切换到 AI 对话输入需求；只有排查时才需要手动运行 `ai-sdlc adapter status`

如果升级后看到 `adapter ingress`、`materialized`、`unverified`、`host ingress` 这类英文诊断词，不要先判断为升级失败。它们的意思通常是：

- 规则文件已经写入项目，例如 Codex 的 `AGENTS.md` 已存在
- 当前普通终端不能机器证明 AI 聊天宿主已经自动读取这些规则
- `run --dry-run` 可以继续做安全预演，但 dry-run 本身不等于“治理已被 AI 宿主自动加载”

普通用户下一步仍然是回到 Codex / AI 对话，先发送 CLI 给出的“请先读取 AGENTS.md ...”那句话，再输入需求。只有在以下情况才需要排查：`init` 明确提示 adapter target 不匹配、正式 `ai-sdlc run` 被阻断、或 AI 对话明显没有遵守项目规则。排查时再运行 `ai-sdlc adapter status` 或 `ai-sdlc adapter status --json`。

如果这个项目本来就有 JSON、Markdown、TODO 或 issue 导出的任务进度，再执行一次：

```bash
ai-sdlc adopt .
```

正常时你会看到“接入已有项目”的摘要、推荐继续点，以及原任务文件不会被修改的说明。

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

## 前端组件库默认选择和质量门

当前源码版本的普通前端推荐默认值是：

- `frontend_stack=vue3`
- `provider_id=public-primevue`
- `style_pack_id=modern-saas`

这条路径会生成框架托管的 Vue3 / PrimeVue 前端模板，并配套 Vite、UnoCSS、CSS Variables、Pinia、Vue Router 和 Base 组件层。除非需求明确要求公司内置 Vue2 企业组件库，否则普通新前端需求默认走这条 Vue3 公共 PrimeVue provider。

如果你的目标就是框架自带 Vue2 企业组件库，需要在方案确认时显式选择：

```bash
ai-sdlc program solution-confirm --execute --yes --frontend-stack vue2 --provider-id enterprise-vue2 --style-pack-id enterprise-default --enterprise-provider-eligible
```

前端实现前必须先完成方案确认；未确认技术栈 / 组件库前，不应进入 execute，也不应运行 managed delivery apply。

生成 Vue3 `public-primevue` 前端后，`browser-gate-probe --execute` 会启动 Vite 页面进行 Web smoke。白屏、无法打开页面、fatal console error 或 page error 属于 blocker。桌面 `1440x900` 和移动 `390x844` 截图、视觉结构、Button/Input/Select/Dialog/Form 交互、缺失 label/aria、焦点可见性和 Dialog 焦点回收等首版证据会作为 warning/advisory 输出，用于质量闭环和后续升级为更严格 blocker。

## AI 写代码时的质量底线

AI-SDLC 会把下面几条作为写代码时的默认约束；普通用户不需要每次在对话里重复强调：

- 写代码前必须先有可执行任务；不能只看 `spec.md` 就直接改业务代码。
- 原有注释默认保留；如果确实要删除，必须在执行日志或交接记录里说明删除原因、文件路径和被删注释摘要。
- 新增注释跟随当前或近期用户主要沟通语言；无法判断时默认使用简体中文。
- 中文内容使用 UTF-8 和简体中文，避免繁体误用、乱码、替换字符和常见 mojibake。
- 注释只写业务规则、复杂意图、边界条件、兼容性、并发、缓存、事务、安全和错误处理等有价值的信息；不要复述显而易见的代码。
- 后续 agent 或人工要维护的脚本/模块，如果包含认证、XHR/API 调用、payload 字段映射、加密、阶段流程、重试或副作用边界，必须补维护契约、关键函数 docstring 或边界注释，并在交付说明里确认。

### 常用命令

| 命令 | 功能 |
| --- | --- |
| `ai-sdlc --help` | 查看 CLI 是否可用，以及当前支持的命令 |
| `ai-sdlc --version` | 查看当前安装版本 |
| `ai-sdlc init .` | 在当前项目初始化 AI-SDLC；新版本会自动执行必要检查和安全预演 |
| `ai-sdlc adopt .` | 接入已有项目的 JSON、Markdown、TODO、issue 或 Git 任务进度，不修改原任务文件 |
| `ai-sdlc status` | 查看项目状态、阶段状态和关键路径 |
| `ai-sdlc adapter status` | 排查 AI 入口和规则安装状态；普通开发主路径通常不需要手动执行 |
| `ai-sdlc adapter status --json` | 查看机器可读的 adapter 诊断状态 |
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
| `No such command 'install'` | 旧 CLI 太老；下载 `v0.8.4` 同平台包并执行 `--upgrade-existing` / `-UpgradeExisting` |
| `Update check failed` | GitHub 网络不可用或超时；用离线包救援升级 |
| `offline bundle platform mismatch` | 安装包平台不匹配；换 Windows x64、macOS arm64 或 Linux x64 对应包 |
| `need Python >= 3.11` | 包内没有可用 Python runtime 且系统 Python 太旧；换带 `python-runtime/` 的安装包 |
| Windows `running scripts is disabled` | 使用 `powershell -ExecutionPolicy Bypass -File .\install_offline.ps1` |
| Windows `ExpandArchiveFileExists` | 旧解压目录里已有同名文件；改用本指南带 `.ai-sdlc-install` 和 `-Force` 的 Windows 命令 |
| `tar: command not found` / `curl: command not found` | 让管理员下载并解压包，或在具备这些工具的终端执行 |
| `init` 输出提示 adapter target 不匹配 | 按 `下一步 / Next` 执行 `adapter select`，选择真实聊天入口 |
| `adapter ingress truth not yet verified` / `materialized (unverified)` / `host ingress` | 这通常不是升级失败，而是当前终端无法机器证明 AI 聊天宿主已自动读取规则；按 `下一步 / Next` 回到 AI 对话，让 AI 先读取 `AGENTS.md` |
| `init` 或 `run --dry-run` 显示 open gates | 看 `下一步 / Next` 和 `说明 / Notes`；新项目未开始需求时不一定是错误 |
| 在聊天框里粘贴命令没有反应 | 命令必须在终端执行；聊天框只输入自然语言需求 |
