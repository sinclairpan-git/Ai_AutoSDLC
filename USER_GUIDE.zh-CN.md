# AI-SDLC 小白实操手册

## 升级兼容提示（2026-04）

- adapter 的 canonical path 已切换到厂商默认入口：
  - Codex -> `AGENTS.md`
  - Cursor -> `.cursor/rules/ai-sdlc.mdc`
  - VS Code -> `.github/copilot-instructions.md`
  - Claude Code -> `.claude/CLAUDE.md`
- 旧路径（`.vscode/AI-SDLC.md` / `.claude/AI-SDLC.md` / `.codex/AI-SDLC.md` / `.cursor/rules/ai-sdlc.md`）只作为迁移输入；新版会把内容迁到 canonical path，但不会覆盖你在新路径上的自定义修改。
- `adapter activate` 现在只保留为兼容/调试入口，不代表 “verified_loaded”；是否已验证以 `adapter status` 的 ingress truth 为准。
- 示例输出（`Adapter acknowledged` / `Pipeline completed`）不代表 verified_loaded；以 `adapter status` 的 ingress truth 为准。
- `close-check` 只在 `execute_progress` 缺失时作为可信补证，仍要求 tasks.md / execution-log / fresh verification，不能替代正常 execute 收口。
- 如果 status 仍显示 `materialized only` 或 `unsupported`，请在 IDE 自带终端重新运行 `python -m ai_sdlc adapter select`，或按提示设置宿主环境变量后再跑 `status`。

## 目录

- 使用前先记住
- 第一章：空项目完整演练
  - 第 1 步：先用 IDE 打开你准备放项目的目录一次
  - 第 2 步：在终端里创建一个空项目文件夹
  - 第 3 步：检查 Python 版本
  - 第 4 步：在这个空项目里创建虚拟环境并安装 AI-SDLC
  - 第 5 步：验证 AI-SDLC 安装成功
  - 第 6 步：初始化这个空项目
  - 第 7 步：先确认 adapter 已被宿主认可
  - 第 8 步：现在不要聊天，先在终端里做一次预演启动
  - 第 9 步：到这里，才切换到 IDE 聊天输入框
- 第二章：已有项目完整演练
  - 第 1 步：先用你的 IDE 打开这个已有项目一次
  - 第 2 步：在终端里进入这个已有项目根目录
  - 第 3 步：检查 Python 版本
  - 第 4 步：在这个已有项目里安装 AI-SDLC
  - 第 5 步：验证安装成功
  - 第 6 步：初始化这个已有项目
  - 第 7 步：看一下当前状态
  - 第 8 步：先确认 adapter 已被宿主认可
  - 第 9 步：先在终端做一次预演启动
  - 第 10 步：到这里，才切换到 IDE 聊天输入框
- Telemetry 运维边界（status/doctor）
- 交付完成（DoD）与计划 / 任务状态
- 框架自身开发补充

## 使用前先记住

这份文档只有两章。
第一章用一个空项目，从 0 开始，完整跑到“可以开始在 IDE 聊天窗里说需求”。
第二章用一个已有项目，从安装一直跑到“可以开始在 IDE 聊天窗里说增量需求”。

**先记住一条铁规则：**

- `python -m ai_sdlc ...` 这类命令，永远在**终端**执行。
- Cursor / Codex / Claude Code 的**聊天输入框**，永远只发自然语言，不发 shell 命令。

如果你问“最合适在哪里执行命令”，我的答案是：

- 最合适：先用 Cursor / Codex / Claude Code 打开项目文件夹一次，然后在这个 IDE 自带的 Terminal 里执行本文命令。
- 也可以：Windows 用 PowerShell，macOS / Linux 用 Terminal。
- 但是不管你用哪种终端，**都不要把 `python -m ai_sdlc init .` 这种命令粘贴到 IDE 聊天输入框里。**

如果你问“PowerShell 怎么识别 IDE”，答案是：

- 不是 PowerShell 识别 IDE。
- AI-SDLC 识别的是项目里的 IDE 标记目录，例如 `.cursor`、`.codex`、`.claude`、`.vscode`。
- 所以最稳的做法是：**先用你的 IDE 打开项目文件夹一次，再去终端跑 `init`。**
- 如果你先在 PowerShell 跑了 `init`，后面才打开 IDE，也没关系。打开 IDE 以后，再在终端执行一次 `python -m ai_sdlc status`，AI-SDLC 仍然可以补装 IDE 适配文件；补装完以后，再执行一次 `python -m ai_sdlc adapter activate`。

如果你问“AI-SDLC 到底应该认哪个工具”，答案是：

- 认的是你**真正用来聊天输入需求的 AI 入口**，不是最外层编辑器壳。
- 例如你在 VS Code 里用 Codex 聊天，AI-SDLC 应该认 `codex`，不是只认 `vscode`。
- 例如你在 VS Code 里用 Claude Code 聊天，AI-SDLC 应该认 `claude_code`。
- 如果自动识别错了，也不用怕。交互式 `init` 会先给你一个五项列表；如果后面还想改，可以直接运行 `python -m ai_sdlc adapter select` 进入同一个列表，`--agent-target` 只作为非交互 override。

## 第一章：空项目完整演练

下面用这个需求做完整示范：

```text
我想开发一个全自动的UI测试平台。
```

### 第 1 步：先用 IDE 打开你准备放项目的目录一次

这一小步**不执行命令**，只做一个动作：

- 如果你用 Cursor，就先用 Cursor 打开你准备放项目的目录
- 如果你用 Codex，就先用 Codex 打开你准备放项目的目录
- 如果你用 Claude Code，就先进入这个目录，后面聊天也在这个项目上下文里进行

这样做的目的只有一个：
让 AI-SDLC 后面更容易识别你实际在用哪个 IDE。

### 第 2 步：在终端里创建一个空项目文件夹

**这一步在哪执行：**

- Windows：PowerShell，或 IDE 自带 Terminal
- macOS：Terminal / iTerm，或 IDE 自带 Terminal
- Linux：Terminal，或 IDE 自带 Terminal

**Windows 直接复制：**

```powershell
# D:\work 是示例父目录，ui-test-platform 是示例项目名；可按需替换
cd D:\work
mkdir ui-test-platform
cd ui-test-platform
```

**macOS 直接复制：**

```bash
# ~/work 是示例父目录，ui-test-platform 是示例项目名；可按需替换
cd ~/work
mkdir ui-test-platform
cd ui-test-platform
```

**Linux 直接复制：**

```bash
# ~/work 是示例父目录，ui-test-platform 是示例项目名；可按需替换
cd ~/work
mkdir ui-test-platform
cd ui-test-platform
```

**执行成功以后，你应该看到：**

- 终端当前目录已经进入你刚创建的项目目录；如果你直接照抄示例，这里就是 `ui-test-platform`
- 这个目录现在还是空的，里面还没有业务代码

### 第 3 步：检查 Python 版本

**这一步在哪执行：**

- 终端

**Windows 直接复制：**

```powershell
py -3.11 --version
```

**macOS 直接复制：**

```bash
python3 --version
```

**Linux 直接复制：**

```bash
python3 --version
```

**执行成功以后，你应该看到：**

- Windows 至少显示 `Python 3.11.x`
- macOS 至少显示 `Python 3.11.x`
- Linux 至少显示 `Python 3.11.x`

**如果报错：**

- Windows 如果提示找不到 `py` 或没有 3.11，直接复制：

```powershell
winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
winget install -e --id Python.Launcher --accept-package-agreements --accept-source-agreements
py -3.11 --version
```

- macOS 如果版本低于 3.11，直接复制：

如果你的 Mac 还没装 Homebrew，先复制：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

然后继续复制：

```bash
if [ -x /opt/homebrew/bin/brew ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -x /usr/local/bin/brew ]; then
  eval "$(/usr/local/bin/brew shellenv)"
fi
brew install python@3.11
export PATH="$(brew --prefix python@3.11)/libexec/bin:$PATH"
python3 --version
```

- Linux 如果版本低于 3.11，直接复制：

下面这组命令按 Ubuntu / Debian 写法准备；如果你用的是其他发行版，思路不变，但安装系统依赖的命令要换成你自己的包管理器。

```bash
sudo apt-get update
sudo apt-get install -y build-essential procps curl file git
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
brew install python@3.11
export PATH="$(brew --prefix python@3.11)/libexec/bin:$PATH"
python3 --version
```

- Python 没装好之前，不要继续往下执行

### 第 4 步：在这个空项目里创建虚拟环境并安装 AI-SDLC

**这一步在哪执行：**

- 终端

**Windows 直接复制：**

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install "https://github.com/sinclairpan-git/Ai_AutoSDLC/archive/refs/tags/v0.6.0.zip"
```

**macOS 直接复制：**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install "https://github.com/sinclairpan-git/Ai_AutoSDLC/archive/refs/tags/v0.6.0.tar.gz"
```

**Linux 直接复制：**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install "https://github.com/sinclairpan-git/Ai_AutoSDLC/archive/refs/tags/v0.6.0.tar.gz"
```

**执行成功以后，你应该看到：**

- 当前项目目录里出现 `.venv`
- `pip install` 最后没有报错
- 终端回到输入提示符

**如果报错：**

- Windows 如果卡在 `Activate.ps1`，先确认已经执行了：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

- 如果 `pip install` 网络失败，说明当前机器访问 GitHub 有问题。先解决网络，再重试安装。

**如果你已经装过旧版本，想直接升级：**

前提：

- 当前项目目录里已经有 `.venv`
- 下面命令是在项目根目录执行

**Windows 升级直接复制：**

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install --upgrade --force-reinstall "https://github.com/sinclairpan-git/Ai_AutoSDLC/archive/refs/tags/v0.6.0.zip"
```

**Linux 升级直接复制：**

```bash
source .venv/bin/activate
python -m pip install -U pip
pip install --upgrade --force-reinstall "https://github.com/sinclairpan-git/Ai_AutoSDLC/archive/refs/tags/v0.6.0.tar.gz"
```

**macOS 升级直接复制：**

```bash
source .venv/bin/activate
python -m pip install -U pip
pip install --upgrade --force-reinstall "https://github.com/sinclairpan-git/Ai_AutoSDLC/archive/refs/tags/v0.6.0.tar.gz"
```

### 第 5 步：验证 AI-SDLC 安装成功

**这一步在哪执行：**

- 终端

**Windows / macOS / Linux 都直接复制：**

```bash
python -m ai_sdlc --help
python -m ai_sdlc doctor
```

**执行成功以后，你应该看到：**

- `python -m ai_sdlc --help` 打印出 AI-SDLC 的命令帮助
- `python -m ai_sdlc doctor` 正常执行
- 没有出现 `No module named ai_sdlc`

**如果报错：**

- 先重新激活虚拟环境

Windows：

```powershell
.\.venv\Scripts\Activate.ps1
python -m ai_sdlc --help
```

macOS：

```bash
source .venv/bin/activate
python -m ai_sdlc --help
```

Linux：

```bash
source .venv/bin/activate
python -m ai_sdlc --help
```

- 如果重新激活后还是不行，回到上一步重新安装，不要继续往下走

### 第 6 步：初始化这个空项目

**这一步在哪执行：**

- 终端
- 不在 IDE 聊天输入框执行

**Windows / macOS / Linux 都直接复制：**

```bash
python -m ai_sdlc init .
```

如果当前终端是交互式 TTY，`init` 会先给你一个五项 selector，自动识别只负责默认聚焦，不会替你自动确认。

如果你非常确定自己真正聊天的工具是谁，也可以第一次就直接指定。例如你是在 VS Code 里用 Codex 聊天，可以直接执行：

```bash
python -m ai_sdlc init . --agent-target codex
```

**执行成功以后，你应该看到：**

- 输出里出现 `Initialized AI-SDLC project`
- 当前项目目录里出现 `.ai-sdlc`
- 输出的下一步提示里会出现 `adapter activate`

你可以把结果大致对照成下面这样：

```text
╭─ ai-sdlc init ─────────────────────────╮
│ Initialized AI-SDLC project            │
│   Name: ui-test-platform               │
│   Path: .../ui-test-platform/.ai-sdlc  │
│                                        │
│ Next step:                             │
│   Acknowledge adapter:                 │
│     ai-sdlc adapter activate           │
│   Start framework in safe mode:        │
│     ai-sdlc run --dry-run              │
╰────────────────────────────────────────╯
```

**如果你前面忘了先打开 IDE：**

没关系。现在先去用你的 IDE 打开这个项目文件夹一次，然后回到终端执行：

```bash
python -m ai_sdlc status
```

执行成功以后，你应该看到：

- `status` 正常输出项目状态
- IDE 适配文件有机会在这一步补装
- 但这一步还不算“已认可”，后面还要执行一次 `adapter activate`

你可以把结果大致对照成下面这样：

```text
AI-SDLC Status
Project        ui-test-platform
Status         initialized
Pipeline Stage init
```

### 第 7 步：先确认 adapter 已被宿主认可

**这一步在哪执行：**

- 终端
- 不在 IDE 聊天输入框执行

**Windows / macOS / Linux 都直接复制：**

```bash
python -m ai_sdlc adapter activate
```

**执行成功以后，你应该看到：**

- 输出里出现 `Adapter acknowledged`
- 行尾会看到类似 `(acknowledged)` 的状态字样
- 这只表示你在 CLI 里人工确认了当前 adapter target
- 对目前的 Markdown / 文件型 adapter（`codex`、`cursor`、`claude_code`、`vscode`、`generic`），这还不是“宿主可验证激活”；治理侧仍按 `soft_prompt_only` 看待

你可以把结果大致对照成下面这样：

```text
IDE adapter (codex): installed 1 file(s)
Adapter acknowledged: codex (acknowledged)
```

**如果你怀疑它认错了工具：**

比如你实际在 VS Code 里用的是 Codex，而不是只想装 VS Code 工作区提示，那么不要硬着头皮往下走。先改成真正的聊天工具，再重新激活：

```bash
python -m ai_sdlc adapter select
python -m ai_sdlc adapter activate --agent-target codex
```

`adapter select` 会进入和 `init` 相同的五项列表；如果你在 CI 或非交互终端里操作，再改用 `--agent-target` 明确指定。

选项固定只有 5 个：

- `cursor`
- `codex`
- `claude_code`
- `vscode`
- `generic`

### 第 8 步：现在不要聊天，先在终端里做一次预演启动

**这一步在哪执行：**

- 终端
- 不在 IDE 聊天输入框执行

**Windows / macOS / Linux 都直接复制：**

```bash
python -m ai_sdlc run --dry-run
```

**这一步的真实含义：**

- 这是“启动框架的预演”
- 不是在这里输入需求
- 它会检查阶段路由和 gate，但不会把 adapter 状态推进成“可验证激活”
- 所以 `run --dry-run` 成功，不等于宿主已经对治理提示做了可核验握手
- 不是在这里手工写 `spec.md`
- 按当前框架设计，**第一次空项目 `init` 之后，不要求你先手工创建 `spec.md` 再执行这条命令**

**执行成功以后，你至少应该看到：**

- 命令执行结束，回到终端提示符
- 没有出现 `No module named ai_sdlc`
- 没有出现 `Not inside an AI-SDLC project`
- 如果是正常预演，最后一般会看到 `Pipeline completed.`

你可以把结果大致对照成下面这样：

```text
Pipeline completed. Stage: verify
```

**注意：**这只是示例输出，不代表治理已激活；以 `python -m ai_sdlc adapter status` 的 ingress truth 为准。

**如果报错说需要 `recover --reconcile`：**

直接复制下面四条：

```bash
python -m ai_sdlc recover --reconcile
python -m ai_sdlc status
python -m ai_sdlc adapter activate
python -m ai_sdlc run --dry-run
```

如果照做仍失败，不要继续往下走，先回到第 5～7 步检查安装与路径。

**如果它提示你先执行 `adapter activate`：**

这不是坏事，说明 AI-SDLC 只是在保护你，不让你跳过 adapter 认可步骤。直接回到上一步，再执行一遍：

```bash
python -m ai_sdlc adapter activate
python -m ai_sdlc run --dry-run
```

**如果你第一次空项目执行 `run --dry-run` 就提示缺少 `spec.md`：**

不要自己手工建 `spec.md`。
先直接复制下面这三条：

```bash
python -m ai_sdlc init .
python -m ai_sdlc status
python -m ai_sdlc adapter activate
python -m ai_sdlc run --dry-run
```

如果仍然报旧状态相关错误，再执行：

```bash
python -m ai_sdlc recover --reconcile
python -m ai_sdlc adapter activate
python -m ai_sdlc run --dry-run
```

### 第 9 步：到这里，才切换到 IDE 聊天输入框

**这一步在哪执行：**

- Cursor / Codex / Claude Code 的聊天输入框
- 不在终端执行

到这一步，你已经完成了：

- 安装
- 验证
- 初始化
- adapter 认可
- 预演启动

现在你可以开始需求沟通、需求扩展、拆解和设计。

**如果你只是打一段一句话需求，直接复制下面这段到 IDE 聊天输入框：**

```text
我已经在这个项目根目录执行过：
1. python -m ai_sdlc init .
2. python -m ai_sdlc adapter activate
3. python -m ai_sdlc run --dry-run

现在我要开始一个新需求。
需求是：我想开发一个全自动的UI测试平台。

请按 AI-SDLC 流程，先帮我做需求澄清、扩展、拆解和设计，不要直接写代码。
```

**如果你已经有 PRD，要上传 PRD，也是在这一步做。**

你可以在 IDE 聊天输入框直接复制：

```text
我已经在这个项目根目录执行过：
1. python -m ai_sdlc init .
2. python -m ai_sdlc adapter activate
3. python -m ai_sdlc run --dry-run

我现在会上传一份 PRD。
请先基于这份 PRD 做需求澄清、范围确认和设计，不要直接开始写代码。
```

**到这里，这个空项目的全流程就跑通了。**

你应该已经清楚：

- 安装命令在终端执行
- 初始化命令在终端执行
- `adapter activate` 在终端执行
- `run --dry-run` 在终端执行
- 至少要把 `init`、`adapter activate`、`run --dry-run` 做完以后，才进入 IDE 聊天输入框说需求

## 第二章：已有项目完整演练

下面用这个增量需求做完整示范：

```text
我想新增一个E2E的UI测试场景覆盖。
```

### 第 1 步：先用你的 IDE 打开这个已有项目一次

这一小步不执行命令，只做一个动作：

- 用 Cursor / Codex / Claude Code 打开现有项目文件夹

这样做的目的还是一样：

- 让 AI-SDLC 更容易识别你现在到底在用哪个 IDE

### 第 2 步：在终端里进入这个已有项目根目录

**这一步在哪执行：**

- 终端

**Windows 直接复制：**

```powershell
# D:\work\my-existing-project 是示例路径；请替换成你自己已有项目的真实路径
cd D:\work\my-existing-project
```

**macOS 直接复制：**

```bash
# ~/work/my-existing-project 是示例路径；请替换成你自己已有项目的真实路径
cd ~/work/my-existing-project
```

**Linux 直接复制：**

```bash
# ~/work/my-existing-project 是示例路径；请替换成你自己已有项目的真实路径
cd ~/work/my-existing-project
```

**执行成功以后，你应该看到：**

- 当前终端已经位于你的已有项目根目录

### 第 3 步：检查 Python 版本

**这一步在哪执行：**

- 终端

**Windows 直接复制：**

```powershell
py -3.11 --version
```

**macOS 直接复制：**

```bash
python3 --version
```

**Linux 直接复制：**

```bash
python3 --version
```

**执行成功以后，你应该看到：**

- Windows / macOS / Linux 至少显示 `Python 3.11.x`

**如果报错：**

- Windows 如果提示找不到 `py` 或没有 3.11，直接复制：

```powershell
winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
winget install -e --id Python.Launcher --accept-package-agreements --accept-source-agreements
py -3.11 --version
```

- macOS 如果版本低于 3.11，直接复制：

如果你的 Mac 还没装 Homebrew，先复制：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

然后继续复制：

```bash
if [ -x /opt/homebrew/bin/brew ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -x /usr/local/bin/brew ]; then
  eval "$(/usr/local/bin/brew shellenv)"
fi
brew install python@3.11
export PATH="$(brew --prefix python@3.11)/libexec/bin:$PATH"
python3 --version
```

- Linux 如果版本低于 3.11，直接复制：

下面这组命令按 Ubuntu / Debian 写法准备；如果你用的是其他发行版，思路不变，但安装系统依赖的命令要换成你自己的包管理器。

```bash
sudo apt-get update
sudo apt-get install -y build-essential procps curl file git
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
brew install python@3.11
export PATH="$(brew --prefix python@3.11)/libexec/bin:$PATH"
python3 --version
```

- Python 没准备好之前，不要继续

### 第 4 步：在这个已有项目里安装 AI-SDLC

**这一步在哪执行：**

- 终端

**Windows 直接复制：**

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install "https://github.com/sinclairpan-git/Ai_AutoSDLC/archive/refs/tags/v0.6.0.zip"
```

**macOS 直接复制：**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install "https://github.com/sinclairpan-git/Ai_AutoSDLC/archive/refs/tags/v0.6.0.tar.gz"
```

**Linux 直接复制：**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install "https://github.com/sinclairpan-git/Ai_AutoSDLC/archive/refs/tags/v0.6.0.tar.gz"
```

**执行成功以后，你应该看到：**

- 项目根目录里出现 `.venv`
- `pip install` 完成，没有报错

**如果你已经装过旧版本，想直接升级：**

前提：

- 当前项目目录里已经有 `.venv`
- 下面命令是在项目根目录执行

**Windows 升级直接复制：**

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install --upgrade --force-reinstall "https://github.com/sinclairpan-git/Ai_AutoSDLC/archive/refs/tags/v0.6.0.zip"
```

**Linux 升级直接复制：**

```bash
source .venv/bin/activate
python -m pip install -U pip
pip install --upgrade --force-reinstall "https://github.com/sinclairpan-git/Ai_AutoSDLC/archive/refs/tags/v0.6.0.tar.gz"
```

**macOS 升级直接复制：**

```bash
source .venv/bin/activate
python -m pip install -U pip
pip install --upgrade --force-reinstall "https://github.com/sinclairpan-git/Ai_AutoSDLC/archive/refs/tags/v0.6.0.tar.gz"
```

### 第 5 步：验证安装成功

**这一步在哪执行：**

- 终端

**Windows / macOS / Linux 都直接复制：**

```bash
python -m ai_sdlc --help
python -m ai_sdlc doctor
```

**执行成功以后，你应该看到：**

- `python -m ai_sdlc --help` 能打印命令帮助
- `python -m ai_sdlc doctor` 能正常执行
- 没有出现 `No module named ai_sdlc`

**如果报错：**

- 先重新激活虚拟环境，再重试

Windows：

```powershell
.\.venv\Scripts\Activate.ps1
python -m ai_sdlc --help
```

macOS：

```bash
source .venv/bin/activate
python -m ai_sdlc --help
```

Linux：

```bash
source .venv/bin/activate
python -m ai_sdlc --help
```

### 第 6 步：初始化这个已有项目

**这一步在哪执行：**

- 终端
- 不在 IDE 聊天输入框执行

**Windows / macOS / Linux 都直接复制：**

```bash
python -m ai_sdlc init .
```

如果当前终端是交互式 TTY，`init` 会先给你一个五项 selector，自动识别只负责默认聚焦，不会替你自动确认。

如果你非常确定自己真正聊天的工具是谁，也可以第一次就直接指定。例如你是在 VS Code 里用 Codex 聊天，可以直接执行：

```bash
python -m ai_sdlc init . --agent-target codex
```

**执行成功以后，你应该看到：**

- 输出里出现 `Initialized AI-SDLC project`
- 项目根目录里出现 `.ai-sdlc`
- 由于这是已有项目，输出里可能会出现 existing project / deep scan / baseline 之类的信息

你可以把结果大致对照成下面这样：

```text
╭─ ai-sdlc init ─────────────────────────────╮
│ Detected existing project                  │
│ Initialized AI-SDLC project                │
│   Path: .../my-existing-project/.ai-sdlc   │
│                                            │
│ Next step:                                 │
│   Acknowledge adapter:                     │
│     ai-sdlc adapter activate               │
│   Start framework in safe mode:            │
│     ai-sdlc run --dry-run                  │
╰────────────────────────────────────────────╯
```

### 第 7 步：看一下当前状态

**这一步在哪执行：**

- 终端

**Windows / macOS / Linux 都直接复制：**

```bash
python -m ai_sdlc status
```

**执行成功以后，你应该看到：**

- 一张项目状态表
- 说明 AI-SDLC 已经认到这个已有项目了
- 如果你刚才是先 `init`、后打开 IDE，这一步也可能顺手补装 adapter 文件；补装完以后，下一步仍然要执行 `adapter activate`

你可以把结果大致对照成下面这样：

```text
AI-SDLC Status
Project        my-existing-project
Status         initialized
Pipeline Stage init
```

### 第 8 步：先确认 adapter 已被宿主认可

**这一步在哪执行：**

- 终端
- 不在 IDE 聊天输入框执行

**Windows / macOS / Linux 都直接复制：**

```bash
python -m ai_sdlc adapter activate
```

**执行成功以后，你应该看到：**

- 输出里出现 `Adapter acknowledged`
- 行尾会看到类似 `(acknowledged)` 的状态字样
- 这只表示你在 CLI 里人工确认了当前 adapter target
- 对目前的 Markdown / 文件型 adapter（`codex`、`cursor`、`claude_code`、`vscode`、`generic`），这还不是“宿主可验证激活”；治理侧仍按 `soft_prompt_only` 看待

你可以把结果大致对照成下面这样：

```text
IDE adapter (codex): installed 1 file(s)
Adapter acknowledged: codex (acknowledged)
```

**如果你怀疑它认错了工具：**

比如你实际在 VS Code 里用的是 Codex，而不是只想装 VS Code 工作区提示，那么不要硬着头皮往下走。先改成真正的聊天工具，再重新激活：

```bash
python -m ai_sdlc adapter select
python -m ai_sdlc adapter activate --agent-target codex
```

`adapter select` 会进入和 `init` 相同的五项列表；如果你在 CI 或非交互终端里操作，再改用 `--agent-target` 明确指定。

### 第 9 步：先在终端做一次预演启动

**这一步在哪执行：**

- 终端
- 不在 IDE 聊天输入框执行

**Windows / macOS / Linux 都直接复制：**

```bash
python -m ai_sdlc run --dry-run
```

**这一步的真实含义：**

- 这是“启动框架的预演”
- 不是在这里输入增量需求
- 不是让你在这里手工补 `spec.md`

**执行成功以后，你至少应该看到：**

- 命令执行结束，回到终端提示符
- 没有出现 `No module named ai_sdlc`
- 没有出现 `Not inside an AI-SDLC project`
- 如果是正常预演，最后一般会看到 `Pipeline completed.`

你可以把结果大致对照成下面这样：

```text
Pipeline completed. Stage: verify
```

**注意：**这只是示例输出，不代表治理已激活；以 `python -m ai_sdlc adapter status` 的 ingress truth 为准。

**如果报错说需要 `recover --reconcile`：**

直接复制：

```bash
python -m ai_sdlc recover --reconcile
python -m ai_sdlc status
python -m ai_sdlc adapter activate
python -m ai_sdlc run --dry-run
```

如果照做仍失败，不要继续第 10 步，先回到第 5～7 步检查安装与路径。

**如果它提示你先执行 `adapter activate`：**

```bash
python -m ai_sdlc adapter activate
python -m ai_sdlc run --dry-run
```

### 第 10 步：到这里，才切换到 IDE 聊天输入框

**这一步在哪执行：**

- Cursor / Codex / Claude Code 的聊天输入框
- 不在终端执行

你现在已经完成了：

- 安装
- 验证
- 初始化
- 状态检查
- adapter 认可
- 预演启动

现在可以开始在聊天输入框里说增量需求。

**直接复制下面这段到 IDE 聊天输入框：**

```text
我已经在这个已有项目根目录执行过：
1. python -m ai_sdlc init .
2. python -m ai_sdlc status
3. python -m ai_sdlc adapter activate
4. python -m ai_sdlc run --dry-run

现在我要做一个增量需求。
需求是：我想新增一个E2E的UI测试场景覆盖。

请按 AI-SDLC 流程，先帮我做需求澄清、影响分析、拆解和设计，不要直接写代码。
```

**如果你不是打一行文字，而是要上传 PRD 或已有需求说明，也是在这一步上传。**

你可以直接复制：

```text
我已经在这个已有项目根目录执行过：
1. python -m ai_sdlc init .
2. python -m ai_sdlc status
3. python -m ai_sdlc adapter activate
4. python -m ai_sdlc run --dry-run

我现在会上传一份已有需求说明或 PRD。
请先基于它做增量需求分析、影响分析、拆解和设计，不要直接写代码。
```

**到这里，这个已有项目的全流程也跑通了。**

你应该已经清楚：

- 命令还是在终端执行
- 初始化还是在终端执行
- `adapter activate` 还是在终端执行
- `run --dry-run` 还是在终端执行
- 真正开始需求沟通，是在 IDE 聊天输入框里执行自然语言对话

## Telemetry 运维边界（status/doctor）

### 1) 原始 trace 与治理产物的区别

- 原始 trace（运行证据）在 `.ai-sdlc/local/telemetry/`，包含 manifest、event/evidence 流和 indexes（如果已存在）。
- 治理产物（面向运维阅读）在 `.ai-sdlc/project/reports/telemetry/`。

### 2) 手工记录 telemetry 的命令

在仓库根目录终端执行：

```bash
python -m ai_sdlc telemetry open-session
python -m ai_sdlc telemetry record-event --scope session --goal-session-id <gs_id>
python -m ai_sdlc telemetry record-evidence --scope session --goal-session-id <gs_id> --locator <locator>
python -m ai_sdlc telemetry record-evaluation --scope session --goal-session-id <gs_id> --result warning --status waived
python -m ai_sdlc telemetry record-violation --scope session --goal-session-id <gs_id> --status triaged --risk-level high
python -m ai_sdlc telemetry close-session --goal-session-id <gs_id> --status succeeded
```

这里的 `record-evaluation` 对应 telemetry 治理对象里的“评估结论”；CLI 沿用内部 `evaluation` 命名，而不是额外引入 `assessment` 别名。

### 2.5) provenance read-only 审计面

在仓库根目录终端执行：

```bash
python -m ai_sdlc provenance summary --subject-ref <provenance_ref>
python -m ai_sdlc provenance explain --subject-ref <provenance_ref>
python -m ai_sdlc provenance gaps --subject-ref <provenance_ref>
python -m ai_sdlc provenance summary --subject-ref <provenance_ref> --json
```

这一组命令的定位是：

- `summary`：日常快速看 provenance 链路概况。
- `explain`：展开 assessment，确认总体链状态、最高置信来源和关键缺口。
- `gaps`：只看当前阻止更高置信结论的 provenance 缺口。

Phase 1 的边界要记住：

- 这是 **只读** 审计面，不会 graph rewrite、repair、implicit rebuild 或初始化 provenance 根目录。
- 它不会把 provenance candidate 自动提升成 `verify / close-check / release` 的默认 blocker。
- 当前没有 host-native full coverage；缺失链路可能表现为 `unknown / unobserved / unsupported`。
- `manual injection` 仍只是测试 / 诊断 / 回放入口，不是日常业务入口；日常面就是 `summary / explain / gaps`。

### 3) `accepted` 的含义

- `accepted` 表示“风险被接受/债务被接受”，不是“问题已解决”。
- 在治理汇总里，`accepted` 仍属于 open debt，不会计入 resolved。

### 4) `status --json` 与 `doctor` 的边界

- `python -m ai_sdlc status --json` 只输出 bounded read surface：包含 telemetry 摘要，以及当前 active work item 的 bounded branch lifecycle summary。
- telemetry 缺失时会返回 `not_initialized`，并且不会创建 `.ai-sdlc/local/telemetry/`。
- `python -m ai_sdlc doctor` 的 telemetry readiness 仅做只读诊断：root 可写性、manifest 状态、registry 可解析性、writer path 有效性、resolver 健康、`status --json` surface 可用性，以及 branch lifecycle readiness。
- `doctor` 不会深度扫描 trace，不会隐式 rebuild indexes，也不会隐式初始化 telemetry 根目录。
- `python -m ai_sdlc host-runtime plan --json` 只输出当前宿主的只读 `host_runtime_plan`：会暴露 `bootstrap acquisition` / `mainline remediation fragment` / `will_not_touch` 等 machine truth，但不会下载、安装、升级或回滚任何宿主依赖。

### 5) `scan` 的边界

- `python -m ai_sdlc scan <path>` 是 operator/analysis 命令，用于做深度代码扫描并把摘要输出到终端。
- `scan` 可以深度读取仓库内容，但不会隐式初始化 `.ai-sdlc/`、不会触发 IDE adapter 写入，也不会替代 `run` / `stage run` 这类执行面。
- 如果你要生成或刷新工程知识基线，应该使用 `init`（已有项目初始化）或 `refresh`，而不是把 `scan` 当作写路径。

### 6) Operator surface 读写矩阵

先看一个总规则：

- 在已初始化项目里，除 `adapter`、`init`、`doctor`、`status`、`scan`、`verify` 外，CLI 默认会先尝试一次 **IDE adapter 幂等 apply**。
- 这意味着某些本来以“查看/规划”为主的命令，仍可能写入 `.cursor/`、`.vscode/`、`.codex/`、`.claude/` 或 `.ai-sdlc/project/config/project-config.yaml` 里的 adapter 元数据。

| Surface | 典型命令 | 主定位 | 仓库/本地状态影响 |
|---|---|---|---|
| bounded telemetry status | `python -m ai_sdlc status --json` | 只读 telemetry + branch lifecycle 摘要 | **只读**：不初始化 telemetry root，不 rebuild indexes，不触发 adapter |
| host runtime plan | `python -m ai_sdlc host-runtime plan --json` | 当前宿主 readiness / bootstrap / remediation 只读规划 | **只读**：不触发 adapter，不下载/安装/升级任何 Python、Node、package manager 或 Playwright 浏览器；只输出 bounded `host_runtime_plan` |
| adapter status | `python -m ai_sdlc adapter status` | 查看当前选中的 adapter target 与 activation state | **只读**：读取 project config；不触发 adapter apply |
| adapter select | `python -m ai_sdlc adapter select` | 手工改正当前真正聊天的 AI 入口 | **会写 adapter config**：TTY 下进入与 `init` 相同的五项 selector；非交互时可配合 `--agent-target` 显式指定，并把 activation state 重置为 `installed` |
| adapter activate | `python -m ai_sdlc adapter activate` | 把当前 adapter 明确记为“已人工确认” | **会写 adapter config**：必要时补装 adapter 文件，并把 activation state 推进到 `acknowledged`；对当前 Markdown / 文件型 adapter，这仍只是 `soft_prompt_only`，不是可验证治理激活 |
| provenance inspection | `python -m ai_sdlc provenance summary` / `explain` / `gaps` | provenance read-only 审计 | **只读**：不触发 adapter，不 repair graph，不把 candidate 提升成默认 blocker |
| doctor | `python -m ai_sdlc doctor` | 只读诊断 | **只读**：不 deep scan trace，不触发 adapter；会显示 branch lifecycle readiness |
| scan | `python -m ai_sdlc scan <path>` | operator / analysis | **analysis-only**：深度读取代码库并打印摘要；不初始化 `.ai-sdlc/`，不触发 adapter |
| verify constraints | `python -m ai_sdlc verify constraints` | 仓库级规则 / 治理只读校验 | **只读**：不触发 adapter；当前会额外暴露 active work item 的 branch lifecycle governance，但不替代代码变更场景下的 `pytest` / `ruff` |
| stage show / status | `python -m ai_sdlc stage show <stage>` / `stage status` | 阶段查看 | **可能写 adapter**：命令主体只读，但在已初始化项目中可能先触发一次 IDE adapter 幂等 apply |
| stage run --dry-run | `python -m ai_sdlc stage run <stage> --dry-run` | 阶段预演 | **可能写 adapter**：命令本身只展示清单，不执行阶段步骤；但仍可能先触发 adapter apply |
| stage run | `python -m ai_sdlc stage run <stage>` | 阶段调度入口 | **可能写 adapter**：命令本身输出清单与引导，不自动替你执行步骤；但仍可能先触发 adapter apply |
| program validate / status / plan | `python -m ai_sdlc program ...` | Program 级校验与规划 | **可能写 adapter**：program service 自身以读和规划为主，但 CLI 入口仍可能先触发 adapter apply |
| program solution-confirm --dry-run | `python -m ai_sdlc program solution-confirm --dry-run` | 技术方案确认预演 | **可能写 adapter**：命令主体会展示 recommendation / wizard / final preflight；若带 `--report` 会额外写 report 文件 |
| program solution-confirm --execute --yes | `python -m ai_sdlc program solution-confirm --execute --yes` | 技术方案确认落盘 | **可能写 adapter**；确认后会写 `.ai-sdlc/memory/frontend-solution-confirmation/` snapshot artifacts，并可选写 report 文件 |
| program page-ui-schema-handoff | `python -m ai_sdlc program page-ui-schema-handoff` | 查看 `147` 的 provider/kernel handoff surface | **可能写 adapter**：命令主体只读；依赖既有 `.ai-sdlc/memory/frontend-solution-confirmation/latest.yaml`，若缺失会返回 blocker |
| program integrate --dry-run | `python -m ai_sdlc program integrate --dry-run` | guarded integration runbook 预览 | **可能写 adapter**；若带 `--report`，还会写 report 文件 |
| program integrate --execute --yes | `python -m ai_sdlc program integrate --execute --yes` | guarded execute gate | **可能写 adapter**；当前会做 gate 校验与可选 report 写入，不会直接替你修改各 spec 内容 |
| rules materialize-frontend-page-ui-schema | `python -m ai_sdlc rules materialize-frontend-page-ui-schema` | materialize `147` 的 canonical page/ui schema artifacts | **可能写 adapter**：命令本身会把 artifact 写到 `kernel/frontend/page-ui-schema/`；CLI 入口仍可能先触发 adapter apply |
| manual telemetry | `python -m ai_sdlc telemetry open-session`、`record-*`、`close-session` | operator evidence write | **会写 telemetry**：落到 `.ai-sdlc/local/telemetry/` 与派生 indexes；CLI 入口本身也可能先触发 adapter apply |
| workitem init | `python -m ai_sdlc workitem init --title "新 capability 标题"` | direct-formal 初始化 formal work item | **会写 formal docs**：仅适用于已完成 `ai-sdlc init .` 的项目；直接创建 `specs/<WI>/spec.md`、`plan.md`、`tasks.md`；不会要求先写 `docs/superpowers/*` |
| workitem truth-check | `python -m ai_sdlc workitem truth-check --wi specs/<WI>/ --rev <branch|commit>` | work item 指定 revision 的阶段真值核验 | **命令主体只读，但可能写 adapter**：绑定用户指定 branch/commit 后，回答该 WI 在目标 revision 上是 `formal_freeze_only`、`branch_only_implemented` 还是 `mainline_merged`，并显式披露 HEAD/revision mismatch |
| workitem branch-check | `python -m ai_sdlc workitem branch-check --wi specs/<WI>/` | work item 关联 branch/worktree 只读盘点 | **命令主体只读，但可能写 adapter**：回答当前 WI 尚有哪些未处置 branch/worktree，以及它们相对 `main` 的 divergence 与 disposition |
| workitem close-check | `python -m ai_sdlc workitem close-check --wi specs/<WI>/` | work item 收口真值核验 | **命令主体只读，但可能写 adapter**：会核对 tasks / planned batch / traceability / execution-log / fresh verification / git closure / branch lifecycle disposition truth；若关联 scratch/worktree 分支仍未处置且相对 `main` 存在漂移，会返回 `BLOCKER` |
| offline build | `./packaging/offline/build_offline_bundle.sh` | 分发打包 | **会写本地构建产物**：写 `dist/`、`dist-offline/` 和 bundle archives，不修改业务仓源码 |
| offline install | `./install_offline.sh` / `install_offline.ps1` / `install_offline.bat` | bundle 本地安装 | **会写 bundle 目录**：创建 `.venv/` 并安装 wheel；不会替目标业务仓初始化 AI-SDLC |

判断一个命令是否“真的只读”，要同时看两层：

- 命令主体是否会写业务状态、telemetry 或离线产物
- 该命令是否处在会触发 IDE adapter 幂等 apply 的 CLI 入口上

### 7) `program solution-confirm` 的最小使用面

`program solution-confirm` 是 `073` 引入的结构化技术方案确认入口，用来把“推荐方案 / requested truth / effective truth / preflight 结果”从自由文本说明提升为可审计 snapshot。

- 简单模式预览：
  - `python -m ai_sdlc program solution-confirm --dry-run`
  - 默认输出单套主推荐，不落盘 artifact。
- 高级模式预览：
  - `python -m ai_sdlc program solution-confirm --mode advanced --dry-run`
  - 输出 7 步向导式摘要，并在最终确认区显式展示 `requested_*`、`effective_*`、`preflight_status`、`will_change_on_confirm`、`fallback_required`。
- 最终确认并落盘：
  - `python -m ai_sdlc program solution-confirm --mode advanced --execute --yes`
  - 会把确认后的 snapshot 落到 `.ai-sdlc/memory/frontend-solution-confirmation/`。

这里有三个边界需要明确：

- `will_change_on_confirm` 只属于确认前的派生展示字段，不会写入最终 snapshot artifact。
- 如果请求的 enterprise 方案不可用，但存在允许的退路，CLI 会保留 `requested_*`，并把 fallback 结果写到 `effective_*`。
- 如果预检结果是 `blocked`，命令会停止在确认 gate，不应把它理解为“已自动完成技术选型”。

### 7.1) `page-ui-schema` 的最小使用面

`147` 引入的 page/UI schema runtime baseline 有两个最小入口：

- materialize canonical artifacts：
  - `python -m ai_sdlc rules materialize-frontend-page-ui-schema`
  - 会把 schema manifest、versioning、page schemas、ui schemas 写到 `kernel/frontend/page-ui-schema/`。
- 查看 provider/kernel handoff：
  - `python -m ai_sdlc program page-ui-schema-handoff`
  - 会读取当前 `.ai-sdlc/memory/frontend-solution-confirmation/latest.yaml`，把 `147` 的 schema truth 和当前 provider/style truth 拼成可读 handoff。

这里也有两个边界需要明确：

- `page-ui-schema-handoff` 是只读 surfaced diagnostics，不会替你自动 materialize solution snapshot，也不会推进 Track B/C/D。
- 如果 solution snapshot 缺失或损坏，命令会诚实返回 `blocked`，而不是静默回退到内置默认值。

## 交付完成（DoD）与计划 / 任务状态

如果你是在 **AI-SDLC 仓库里开发 AI-SDLC 自身**，这一节主要看 `verify constraints`、`workitem close-check`、`branch-check` 和 `truth-check` 这几类收口命令怎么配合使用。

<a id="user-guide-dod-plan-sync"></a>

### 框架仓库里的 verify / close 收口

如果你是在 **AI-SDLC 仓库里开发 AI-SDLC 自身**，`verify` 和 `close` 最容易被混淆的地方是：

- `uv run ai-sdlc workitem init --title "<新的 framework capability 标题>"`
  - 这是**新 framework capability 的 direct-formal 入口**。
  - 它会直接在 `specs/<WI>/` 下创建 canonical `spec.md / plan.md / tasks.md`。
  - 如果根目录已有 `program-manifest.yaml`，它还会尝试补入对应 `specs[]` entry，并明确提示下一条 global truth 动作。
  - 如果你手头已有 `docs/superpowers/*` 设计稿，它们最多只应作为 `related_doc / related_plan` 被引用，不应再复制成第二套 canonical 文档。
- `uv run ai-sdlc verify constraints`
  - 这是**仓库级规则 / 治理只读校验**。
  - 它负责检查 verification profile、PR checklist、bounded surface / telemetry governance 等规则面是否一致。
  - 它不会替代代码改动场景下的 `uv run pytest -q` 和 `uv run ruff check src tests`。
- `uv run ai-sdlc workitem close-check --wi specs/<WI>/`
  - 这是**work item 级收口真值核验**。
  - 它看的不是“你是不是写了几段 execution log”，而是该 work item 的 tasks 完成度、planned batch coverage、FR / SC traceability、latest batch 的 fresh verification、`related_plan` 对账、branch disposition truth，以及最终 `git closure`。
  - 当仓库已启用根级 global truth 时，它还会区分 `manifest_unmapped`、`truth_snapshot_stale`、`capability_blocked`，并给出下一条 required truth action。
  - 如果 latest batch 还没完成最终 `git commit`，或者仓库工作树仍 dirty，`close-check` 返回 `BLOCKER` 是符合预期的。
- `python -m ai_sdlc program truth sync --dry-run`
  - 这是**truth-only / manifest-only 变更的最小 fresh verification**。
  - 它只做只读预演，不会偷写 snapshot；真正恢复 `fresh` 仍要显式执行 `python -m ai_sdlc program truth sync --execute --yes`。
- `python -m ai_sdlc program truth audit`
  - 这是**根级 truth freshness / capability blocker 诊断面**。
  - 当 `program status` 或 `close-check` 指出 `capability_blocked` 时，优先先看这个面，而不是盲目重复 sync。
- `uv run ai-sdlc workitem branch-check --wi specs/<WI>/`
  - 这是**work item 级 branch/worktree 只读盘点面**。
  - 它回答“这个 work item 当前还有哪些未处置 branch/worktree”，并显示它们相对 `main` 的 ahead/behind、worktree 绑定与 disposition。
  - `branch-check` 不会自动 merge / delete / prune / archive；它只是把 disposition 真值显式化。
- `uv run ai-sdlc workitem truth-check --wi specs/<WI>/ --rev <branch|commit>`
  - 这是**work item 级 revision-scoped 阶段真值面**。
  - 它回答“指定的 branch/commit 上，这个 WI 只是 formal freeze、已经在分支实现，还是已进 `main`”，并显式披露当前 HEAD 是否与目标 revision 一致。
  - 当你在 `main` 上审查另一个分支或历史提交时，优先先跑 `truth-check`，不要把当前 checkout 的 execution evidence 直接外推到目标 revision。
- `uv run ai-sdlc workitem close-check --wi specs/<WI>/ --all-docs`
  - 默认只扫 `specs/<WI>/*.md`，以及 `docs/pull-request-checklist.zh.md`、`USER_GUIDE.zh-CN.md`。
  - 只有当你需要做全仓 `docs/**/*.md` wording drift 复核时，才加 `--all-docs`。

框架仓库里做 telemetry smoke 或仓库级回归时，最常用的一组 fresh verification 是：

```bash
uv run pytest -q
uv run ruff check src tests
uv run ai-sdlc verify constraints
python -m ai_sdlc program truth sync --dry-run
uv run ai-sdlc workitem truth-check --wi specs/<WI> --rev <branch-or-commit>
uv run ai-sdlc workitem branch-check --wi specs/<WI>
git status --short
```

这里的 `git status --short` 不是装饰动作：

- 它用于确认 telemetry smoke、CLI smoke、或其他真实运行命令没有把工作树弄脏。
- `.ai-sdlc/local/` 应继续被视为本地运行态目录并保持忽略；如果 smoke 后工作树不干净，先处理漂移，再声称收口。
- 如果本轮还改了 close 阶段文档、`related_plan` 或 `task-execution-log.md`，应在**完成最终 git 提交后**再补跑一次 `workitem close-check`。

如果这轮工作是“创建新的 framework capability”，常见的 direct-formal 起手顺序是：

```bash
uv run ai-sdlc init .
uv run ai-sdlc workitem init --title "<新的 framework capability 标题>"
python -m ai_sdlc program truth sync --execute --yes
uv run ai-sdlc verify constraints
uv run ai-sdlc workitem branch-check --wi specs/<WI>
```

这条路径的重点是：

- `workitem init` 的前提是当前仓库已经完成 formal bootstrap；如果仓库只有历史 `.ai-sdlc` 痕迹但缺 `project-state.yaml`，应先执行 `uv run ai-sdlc init .`
- 先把 canonical spec/plan/tasks 直接写进 `specs/<WI>/`
- 再围绕这套 formal docs 做 review / verify / execute
- 不再要求“先写 `docs/superpowers/*`，再 formalize 一遍”

## 框架自身开发补充

如果你不是在“业务项目里使用 AI-SDLC”，而是在 **AI-SDLC 仓库里开发 AI-SDLC 自身**，应改看这份文档：

- [框架自迭代开发与发布约定](./框架自迭代开发与发布约定.md)

这份补充文档专门解释：

- 为什么框架仓库内应优先使用 `uv run ai-sdlc ...`
- commit / push / PR / merge / pull / release 各自改变的是什么
- 为什么“刚 push 完”通常不需要再 pull
- 如何把 telemetry trace、约束违约、backlog、根因分析和回归验证串成自优化闭环
