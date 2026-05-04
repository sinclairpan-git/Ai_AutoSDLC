# AI-SDLC 小白实操手册

## 升级兼容提示（2026-04）

- 这份手册现在默认以**当前仓库源码版 / 当前发布版 `v0.7.5`** 为准。如果你正在验证当前仓库里的新能力，优先在目标项目的虚拟环境里执行 `pip install -e <Ai_AutoSDLC 本地源码目录>`；如果你只想安装当前已发布版，再使用下文的 `v0.7.5` tag 安装命令。
- adapter 的 canonical path 已切换到厂商默认入口：
  - Codex -> `AGENTS.md`
  - Cursor -> `.cursor/rules/ai-sdlc.mdc`
  - VS Code -> `.github/copilot-instructions.md`
  - Claude Code -> `.claude/CLAUDE.md`
- 旧路径（`.vscode/AI-SDLC.md` / `.claude/AI-SDLC.md` / `.codex/AI-SDLC.md` / `.cursor/rules/ai-sdlc.md`）只作为迁移输入；新版会把内容迁到 canonical path，但不会覆盖你在新路径上的自定义修改。
- 普通用户不需要先读懂 `adapter status`；`adapter activate` 只保留为兼容/调试入口，不是开始聊天前的必经步骤。
- 示例输出（`Adapter acknowledged` / `Pipeline completed`）不代表 verified_loaded；只有调试机器真值时，才看 `adapter status --json`。
- `v0.7.5` 开始，默认 `init` 会在你完成 AI 代理入口和 shell 选择后自动做安全预演。正常时输出会直接告诉你“初始化完成，切换到 AI 对话输入需求”；异常时只给一个明确的下一步命令。
- 如果你只是使用 CLI，不需要先理解 `verified_loaded`、`governance_activation`、digest 这类内部状态；需要机器真值时再看 `adapter status --json`。
- `close-check` 只在 `execute_progress` 缺失时作为可信补证，仍要求 tasks.md / execution-log / fresh verification，不能替代正常 execute 收口。
- `workitem init` 如果发现根目录还没有 `program-manifest.yaml`，现在会先自动创建最小 manifest，再把当前 work item 写进去。
- `program managed-delivery-apply --execute --yes` 现在不只是写 apply artifact；它会把组件库包真正安装到目标项目的 `managed/frontend/`，并在需要时自动安装 Playwright browser runtime。
- `program browser-gate-baseline --execute --yes` 是新增正式入口，用来把最近一次 browser gate 的 visual-regression bootstrap capture 提升成 baseline。
- 如果异常排查时 `status` 仍显示 `materialized only` 或 `unsupported`，请在 IDE 自带终端重新运行 `python -m ai_sdlc adapter select`，或按提示设置宿主环境变量后再跑 `status`。

## 目录

- 使用前先记住
- 第零章：先选一种安装方式
  - 方案 A：用 GitHub tag 在线安装当前发布版
  - 方案 B：用 0.7.5 Release 离线包安装
  - 方案 C：用本地源码安装最新开发版
  - 已安装用户：检查更新与显式升级
- 第零点五章：从安装到首次使用的命令卡片
  - 命令卡 1：安装或更新 AI-SDLC
  - 命令卡 2：进入业务项目目录
  - 命令卡 3：初始化项目
  - 命令卡 4：进入 IDE 聊天
  - 常见错误怎么处理
- 第一章：空项目完整演练
  - 第 1 步：先用 IDE 打开你准备放项目的目录一次
  - 第 2 步：在终端里创建一个空项目文件夹
  - 第 3 步：安装 AI-SDLC
  - 第 4 步：确认 CLI 可用
  - 第 5 步：记住下一条业务项目命令
  - 第 6 步：初始化这个空项目
  - 第 7 步：切换到 IDE 聊天输入框
- 第二章：已有项目完整演练
  - 第 1 步：先用你的 IDE 打开这个已有项目一次
  - 第 2 步：在终端里进入这个已有项目根目录
  - 第 3 步：安装或确认 AI-SDLC
  - 第 4 步：确认 CLI 可用
  - 第 5 步：确认你仍在已有项目根目录
  - 第 6 步：初始化这个已有项目
  - 第 7 步：切换到 IDE 聊天输入框
- Telemetry 运维边界（status/doctor）
- 交付完成（DoD）与计划 / 任务状态
- 框架自身开发补充

## 使用前先记住

这份文档按“先选安装方式，再照步骤演练”的方式写。

- 第零章：帮你先选安装方式。
- 第零点五章：给你一条最小成功路径，每一步都有命令、成功判据、下一步和报错处理。
- 第一章：用一个空项目，从 0 开始，完整跑到“可以开始在 IDE 聊天窗里说需求”。
- 第二章：用一个已有项目，从安装一直跑到“可以开始在 IDE 聊天窗里说增量需求”。

**先记住一条铁规则：**

- `python -m ai_sdlc ...` 这类命令，永远在**终端**执行。
- Cursor / Codex / Claude Code 的**聊天输入框**，永远只发自然语言，不发 shell 命令。

如果你问“最合适在哪里执行命令”，我的答案是：

- 最合适：先用 Cursor / Codex / Claude Code 打开项目文件夹一次，然后在这个 IDE 自带的 Terminal 里执行本文命令。
- 也可以：Windows 用 PowerShell，macOS / Linux 用 Terminal。
- 但是不管你用哪种终端，**都不要把 `python -m ai_sdlc init .` 这种命令粘贴到 IDE 聊天输入框里。**

如果你问“shell 入口要不要选”，答案是：

- 新项目执行 `init` 时，AI-SDLC 会写入一个推荐 shell。
- 如果你后续实际执行命令的终端不是这个推荐值，就要运行 `python -m ai_sdlc adapter shell-select` 改掉。
- 这个选择会写进项目配置，并刷新 `AGENTS.md` / adapter instructions，让 AI 后续给命令时按 PowerShell、bash、zsh 或 cmd 的语法来写。
- 它不是 AI 代理入口选择。AI 代理入口用 `adapter select`；命令 shell 入口用 `adapter shell-select`。

如果你问“PowerShell 怎么识别 IDE”，答案是：

- 不是 PowerShell 识别 IDE。
- AI-SDLC 识别的是项目里的 IDE 标记目录，例如 `.cursor`、`.codex`、`.claude`、`.vscode`。
- 所以最稳的做法是：**先用你的 IDE 打开项目文件夹一次，再去终端跑 `init`。**
- 如果你先在 PowerShell 跑了 `init`，后面才打开 IDE，也没关系。打开 IDE 以后，再在终端执行一次 `python -m ai_sdlc adapter status`，AI-SDLC 仍然可以补装 IDE 适配文件；如果 target 识别错了，再执行 `python -m ai_sdlc adapter select --agent-target <真实聊天入口>`。

如果你问“AI-SDLC 到底应该认哪个工具”，答案是：

- 认的是你**真正用来聊天输入需求的 AI 入口**，不是最外层编辑器壳。
- 例如你在 VS Code 里用 Codex 聊天，AI-SDLC 应该认 `codex`，不是只认 `vscode`。
- 例如你在 VS Code 里用 Claude Code 聊天，AI-SDLC 应该认 `claude_code`。
- 如果自动识别错了，也不用怕。交互式 `init` 会先给你一个五项列表；如果后面还想改，可以直接运行 `python -m ai_sdlc adapter select` 进入同一个列表，`--agent-target` 只作为非交互 override。

## 第零章：先选一种安装方式

如果你只是想把 AI-SDLC 用起来，优先按下面顺序选：

1. 普通用户、公司统一分发、或不想手动管 Python/venv：选 **方案 B**。
2. 你已经有 Python 3.11+，并且明确想从 GitHub tag 用 pip 安装：选 **方案 A**。
3. 你正在开发 AI-SDLC 框架本身，或要验证尚未发布的新改动：选 **方案 C**。

### 方案 A：用 GitHub tag 在线安装当前发布版

这不是小白首选路径，只适合你已经有 Python 3.11+、知道自己在使用哪个虚拟环境，并且明确想用 pip 从 GitHub tag 安装。普通用户优先看方案 B。

**Windows：**

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install "https://github.com/sinclairpan-git/Ai_AutoSDLC/archive/refs/tags/v0.7.5.zip"
python -m ai_sdlc --help
```

**macOS / Linux：**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install "https://github.com/sinclairpan-git/Ai_AutoSDLC/archive/refs/tags/v0.7.5.tar.gz"
python -m ai_sdlc --help
```

看到 help 输出，就说明 CLI 已安装成功。下一步去第一章或第二章继续做 `init`。

### 方案 B：用 0.7.5 Release 离线包安装

这是普通用户最推荐的方式。先让管理员或你自己从 GitHub Release 下载与你机器匹配的包，再拷贝或放到目标机器。安装脚本会自己检测运行时；除非脚本明确报错，否则不要先手动安装 Python、pip 或其他依赖。

当前 `v0.7.5` 正式发布资产：

- Windows x64：`ai-sdlc-offline-0.7.5-windows-amd64.zip`
- macOS Apple Silicon：`ai-sdlc-offline-0.7.5-macos-arm64.tar.gz`
- Linux x64：`ai-sdlc-offline-0.7.5-linux-amd64.tar.gz`

下载入口：

```text
https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/tag/v0.7.5
```

**Windows：**

```powershell
Expand-Archive -LiteralPath .\ai-sdlc-offline-0.7.5-windows-amd64.zip -DestinationPath .
cd .\ai-sdlc-offline-0.7.5-windows-amd64
powershell -ExecutionPolicy Bypass -File .\install_offline.ps1
.\.venv\Scripts\python.exe -m ai_sdlc --help
```

**macOS Apple Silicon：**

```bash
tar xzf ai-sdlc-offline-0.7.5-macos-arm64.tar.gz
cd ai-sdlc-offline-0.7.5-macos-arm64
chmod +x install_offline.sh
./install_offline.sh
./.venv/bin/python -m ai_sdlc --help
```

**Linux x64：**

```bash
tar xzf ai-sdlc-offline-0.7.5-linux-amd64.tar.gz
cd ai-sdlc-offline-0.7.5-linux-amd64
chmod +x install_offline.sh
./install_offline.sh
./.venv/bin/python -m ai_sdlc --help
```

如果安装脚本提示平台不匹配，说明这个包不是给当前机器用的。不要强行改脚本，请换对应系统和 CPU 的包，或让管理员重新打包。

离线包只负责把 AI-SDLC CLI 安装好；真正让业务项目接入 AI-SDLC，仍然要进入业务项目根目录，再按第一章或第二章执行 `python -m ai_sdlc init .`。

### 方案 C：用本地源码安装最新开发版

只有在你本机已经有一份 `Ai_AutoSDLC` 源码目录时才选这个方式。

**Windows 示例：**

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e D:\work\Ai_AutoSDLC
python -m ai_sdlc --help
```

**macOS / Linux 示例：**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e ~/work/Ai_AutoSDLC
python -m ai_sdlc --help
```

如果你不是框架开发者，通常不需要选这个方案。

### 已安装用户：检查更新与显式升级

`v0.7.5` 开始，已安装的 CLI 可以做非阻断更新提醒。检测到可升级版本时，CLI 会给出一条自动更新命令。

在已经激活 `.venv` 的终端里执行：

```bash
ai-sdlc self-update check
```

如果你是从 GitHub Release 离线包安装的，执行下面这一条命令即可自动下载、安装并校验版本：

```bash
ai-sdlc self-update install --version 0.7.5
```

如果公司内网不允许访问 GitHub，或你希望完全关闭更新检查，可以在终端环境里设置：

**Windows：**

```powershell
$env:AI_SDLC_DISABLE_UPDATE_CHECK = "1"
```

**macOS / Linux：**

```bash
export AI_SDLC_DISABLE_UPDATE_CHECK=1
```

记住：更新检查只是帮助你发现新版本；是否升级，仍然由你或公司的工具管理员明确执行。

## 第零点五章：从安装到首次使用的命令卡片

这一章是最短可执行路径。目标是让完全不懂技术的用户只照着 CLI 输出走，不再手动翻译内部状态。

**重要：预期结果不要逐字硬比对。**

AI-SDLC 的输出可能因为终端宽度、操作系统、IDE、路径不同而换行不同。判断成功时，只看本章写出的“关键字”。如果关键字一致，就继续下一步；如果命令退出码失败或出现本章列出的错误，再按故障分支处理。

### 命令卡 1：安装或更新 AI-SDLC

如果你是第一次安装，优先使用第零章的 Release 离线包或公司管理员给你的安装包。安装脚本会自己检测可用运行时；除非脚本明确报错，否则不要先手动安装 Python、pip 或其他依赖。

如果你已经安装过旧版本，执行一条更新命令即可：

```bash
ai-sdlc self-update install --version 0.7.5
```

**成功后你应该看到：**

- `更新完成 / Update completed`
- `Installed version: 0.7.5`
- 没有要求你继续手动执行 `curl`、`tar`、`install_offline` 之类命令

**下一步执行：**

- 进入你真正要接入 AI-SDLC 的业务项目目录，继续命令卡 2。

**如果失败：**

- CLI 会给出一条重试命令；只执行那一条。
- 如果公司网络不能访问 GitHub，改用第零章的 Release 离线包，不要自己拼下载命令。
- 如果 `ai-sdlc` 命令找不到，但安装目录里的 Python 可用，按安装脚本输出的提示使用 `python -m ai_sdlc ...`。

### 命令卡 2：进入业务项目目录

这一步不是进入 AI-SDLC 安装包目录，而是进入你要开发的项目根目录。

**macOS / Linux 示例：**

```bash
cd ~/project/my-app
```

**Windows PowerShell 示例：**

```powershell
cd D:\project\my-app
```

如果你还没有项目目录，先创建一个空目录，再进入它。

**成功后你应该看到：**

- 终端提示符所在路径就是业务项目目录。
- 这个目录将会出现 `.ai-sdlc/` 和对应 AI 工具的规则文件。

**下一步执行：**

```bash
ai-sdlc init .
```

如果当前终端找不到 `ai-sdlc`，使用模块入口：

```bash
python -m ai_sdlc init .
```

### 命令卡 3：初始化项目

**在业务项目根目录执行：**

```bash
python -m ai_sdlc init .
```

如果你想避免交互选择，可以显式指定你真正使用的 AI 入口：

```bash
python -m ai_sdlc init . --agent-target codex
```

你也可以同时指定 shell，避免交互选择：

```bash
python -m ai_sdlc init . --agent-target codex --shell zsh
```

可选值按你的真实聊天入口和终端选择。AI 入口常见值：`codex`、`cursor`、`vscode`、`claude_code`。shell 常见值：`powershell`、`cmd`、`zsh`、`bash`、`auto`。

**成功后你应该看到：**

- 输出里包含 `Initialized AI-SDLC project`
- 输出里包含 `当前结果 / Result`
- 输出里包含 `下一步 / Next`
- `当前结果 / Result` 告诉你初始化完成，并说明安全预演已自动执行
- `下一步 / Next` 告诉你切换到 AI 对话输入需求
- 项目目录里出现 `.ai-sdlc/`
- 对 Codex，项目根目录里出现或更新 `AGENTS.md`

真实输出会接近下面这样：

```text
AI 代理入口: Codex (explicit override)
Project shell: zsh (explicit override)
╭──────────────── ai-sdlc init ────────────────╮
│ Initialized AI-SDLC project                  │
│   Agent Target: codex                        │
│                                               │
│ 当前结果 / Result                            │
│   初始化完成。正常：codex 规则已安装到       │
│ AGENTS.md。安全预演已自动执行；当前仍有开放 │
│ 门禁。新项目或未完成需求出现这个结果是正常的│
│ 。                                            │
│                                               │
│ 下一步 / Next                                │
│   不用再手动执行初始化命令；现在切换到       │
│ Codex/AI 对话中输入你的需求即可。            │
╰───────────────────────────────────────────────╯
```

正常情况下不用继续执行 `adapter status`、`run --dry-run` 或其他初始化相关命令；切换到 AI 对话里输入需求即可。

**如果失败：**

- 只执行 CLI 输出里的 `下一步 / Next` 那一条命令。
- 提示不清楚 agent target：重新执行并加上 `--agent-target`。
- 提示 shell 不清楚：重新执行并加上 `--shell`。
- 初始化到了错误目录：先 `pwd`（macOS / Linux）或 `Get-Location`（Windows）确认当前目录，再进入业务项目根目录重跑。
- 你在 IDE 聊天框里粘贴了命令：停下来，改到终端执行。

### 命令卡 4：进入 IDE 聊天

**这一步不要在终端执行。**

切换到 Codex / Cursor / Claude Code / VS Code Copilot 的聊天输入框，输入自然语言。

空项目可以复制：

```text
我已经在项目根目录执行过：
1. python -m ai_sdlc init .

现在我要从零开始做一个新项目。
需求是：我想开发一个全自动的UI测试平台。

请按 AI-SDLC 流程，先帮我做需求澄清、影响分析、拆解和设计，不要直接写代码。
```

已有项目可以复制：

```text
我已经在这个已有项目根目录执行过：
1. python -m ai_sdlc init .

现在我要做一个增量需求。
需求是：我想新增一个E2E的UI测试场景覆盖。

请按 AI-SDLC 流程，先帮我做需求澄清、影响分析、拆解和设计，不要直接写代码。
```

### 常见错误怎么处理

| 你看到的现象 | 先执行什么检查 | 怎么处理 |
|---|---|---|
| `python: No module named ai_sdlc` | `python -m pip show ai-sdlc` | 当前环境没装，回到第零章重新安装 |
| `ai-sdlc: command not found` | `python -m ai_sdlc --help` | 如果模块入口成功，就继续使用 `python -m ai_sdlc ...` |
| Windows 无法激活 `.venv` | `Get-ExecutionPolicy -Scope Process` | 执行 `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` 后再激活 |
| `pip install` 下载失败 | `python -m pip --version` | 通常是网络或公司代理问题；改用离线包，或让管理员配置代理 |
| 离线包提示平台不匹配 | 查看 `bundle-manifest.json` | 换对应 Windows/macOS/Linux 和 CPU 的包，不要强行安装 |
| AI 给出的命令总是 PowerShell/bash 风格不对 | `python -m ai_sdlc adapter status` | 查看 `preferred_shell`；不对就运行 `python -m ai_sdlc adapter shell-select --shell <shell>` |
| `preferred_shell_configured` 是 `False` | `python -m ai_sdlc adapter status` | 执行 `python -m ai_sdlc adapter shell-select`，然后重新看 status |
| `init` 输出提示 adapter 未验证 | 看 `下一步 / Next` | 只执行 CLI 给出的那一条命令；普通终端无法证明 AI 宿主加载规则是常见情况 |
| `init` 输出提示 open gates | 看 `说明 / Notes` | 新项目或未完成需求通常正常；如果 `下一步 / Next` 让你切聊天，就直接切聊天 |
| 更新检查显示 `editable_runtime` | `python -m ai_sdlc self-update check` | 你在源码/开发安装路径里，更新提醒会安静退出；正式安装用户才需要按提醒更新 |

后面第一章和第二章里的输出片段是帮助你理解流程的示例；真正判断是否能继续，以 CLI 输出里的 `当前结果 / Result` 和 `下一步 / Next` 为准。

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

### 第 3 步：安装 AI-SDLC

普通用户不要先手动检查 Python、创建 venv、安装 pip 依赖。优先使用第零章的 Release 安装包，或公司管理员给你的安装包。安装脚本会自己检测可用运行时；不符合时会给出明确错误。

如果你已经拿到与你机器匹配的 Release 包，按包内 `README_BUNDLE.txt` 或安装脚本输出执行。安装成功后，输出会包含：

- `当前结果 / Result`
- `下一步 / Next`
- 下一步通常会让你进入业务项目目录并执行 `ai-sdlc init .`

如果你是已安装用户，直接执行一条自动更新命令即可：

```bash
ai-sdlc self-update install --version 0.7.5
```

成功时你应该看到：

- `更新完成 / Update completed`
- `Installed version: 0.7.5`

如果公司内网不能访问 GitHub，使用离线包，不要自己拼 `curl`、`tar` 或 `pip` 命令。

### 第 4 步：确认 CLI 可用

安装完成后，安装脚本会告诉你是否需要激活 `.venv`，或是否应该使用 `python -m ai_sdlc`。优先照安装脚本输出执行。

如果你的终端已经能识别 `ai-sdlc`，执行：

```bash
ai-sdlc --help
```

如果提示 `ai-sdlc` 找不到，执行模块入口：

```bash
python -m ai_sdlc --help
```

成功时你应该看到：

- 输出顶部包含 `Usage`
- 命令列表里包含 `init`、`adapter`、`run`、`self-update`

### 第 5 步：记住下一条业务项目命令

安装包目录只是安装位置，不是业务项目。下一步必须回到你刚创建的 `ui-test-platform` 项目目录。

在业务项目根目录执行：

```bash
ai-sdlc init .
```

如果 `ai-sdlc` 不在 PATH，就执行：

```bash
python -m ai_sdlc init .
```

### 第 6 步：初始化这个空项目

**这一步在哪执行：**

- 终端
- 不在 IDE 聊天输入框执行

**Windows / macOS / Linux 都直接复制：**

```bash
python -m ai_sdlc init .
```

如果当前终端是交互式 TTY，`init` 会先让你选择两件必要信息：

- 当前实际用于聊天开发的 AI 代理入口，例如 Codex、Cursor、Claude Code、VS Code。
- 当前项目默认使用的命令 Shell，例如 PowerShell、zsh、bash、cmd。

这两个选择是必要的，其他检查会由 CLI 自动继续。

如果你非常确定自己真正聊天的工具和 shell，也可以第一次就直接指定。例如你是在 VS Code 里用 Codex 聊天，终端是 zsh，可以直接执行：

```bash
python -m ai_sdlc init . --agent-target codex --shell zsh
```

**执行成功以后，你应该看到：**

- 输出里出现 `Initialized AI-SDLC project`
- 当前项目目录里出现 `.ai-sdlc`
- 对应宿主的 canonical adapter 文件已经落盘，例如 `AGENTS.md`、`.cursor/rules/ai-sdlc.mdc`、`.github/copilot-instructions.md` 或 `.claude/CLAUDE.md`
- 输出里出现 `当前结果 / Result`
- 输出里出现 `下一步 / Next`
- `下一步 / Next` 告诉你切换到 AI 对话输入需求

你可以把结果大致对照成下面这样：

```text
╭──────────────── ai-sdlc init ────────────────╮
│ Initialized AI-SDLC project                  │
│   Name: ui-test-platform                     │
│   Agent Target: codex                        │
│                                               │
│ 当前结果 / Result                            │
│   初始化完成。正常：codex 规则已安装到       │
│ AGENTS.md。安全预演已自动执行；当前仍有开放 │
│ 门禁。新项目或未完成需求出现这个结果是正常的│
│ 。                                            │
│                                               │
│ 下一步 / Next                                │
│   不用再手动执行初始化命令；现在切换到       │
│ Codex/AI 对话中输入你的需求即可。            │
╰───────────────────────────────────────────────╯
```

**如果你前面忘了先打开 IDE：**

没关系。现在先去用你的 IDE 打开这个项目文件夹一次，然后重新执行一次 `init`。如果 CLI 输出的 `下一步 / Next` 仍然让你切换到 AI 对话，就不用再补跑其他命令。

**如果 CLI 输出异常或报错：**

- 只执行 `下一步 / Next` 里给出的那一条命令。
- 如果提示 agent target 选错，重新执行：

```bash
python -m ai_sdlc init . --agent-target codex
```

- 如果提示 shell 选错，重新执行：

```bash
python -m ai_sdlc init . --shell zsh
```

### 第 7 步：切换到 IDE 聊天输入框

**这一步在哪执行：**

- Cursor / Codex / Claude Code 的聊天输入框
- 不在终端执行

到这一步，你已经完成了：

- 安装
- 验证
- 初始化
- CLI 自动安全预演

现在你可以开始需求沟通、需求扩展、拆解和设计。

**如果你只是打一段一句话需求，直接复制下面这段到 IDE 聊天输入框：**

```text
我已经在这个项目根目录执行过：
1. python -m ai_sdlc init .

现在我要开始一个新需求。
需求是：我想开发一个全自动的UI测试平台。

请按 AI-SDLC 流程，先帮我做需求澄清、扩展、拆解和设计，不要直接写代码。
```

**如果你已经有 PRD，要上传 PRD，也是在这一步做。**

你可以在 IDE 聊天输入框直接复制：

```text
我已经在这个项目根目录执行过：
1. python -m ai_sdlc init .

我现在会上传一份 PRD。
请先基于这份 PRD 做需求澄清、范围确认和设计，不要直接开始写代码。
```

**到这里，这个空项目的全流程就跑通了。**

你应该已经清楚：

- 安装命令在终端执行
- 初始化命令在终端执行
- 真正开始需求沟通，是在 IDE 聊天输入框里执行自然语言对话
- 只有当 CLI 明确报错或 `下一步 / Next` 要求时，才执行额外排查命令

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

### 第 3 步：安装或确认 AI-SDLC

已有项目也不要求普通用户先手动检查 Python、创建 venv 或安装依赖。优先使用第零章的 Release 安装包，或公司管理员给你的安装包。安装脚本会自己检测可用运行时。

如果你已经安装过旧版本，执行一条自动更新命令：

```bash
ai-sdlc self-update install --version 0.7.5
```

成功时你应该看到：

- `更新完成 / Update completed`
- `Installed version: 0.7.5`

如果你还没有安装，先回到第零章选择 Release 安装包。安装完成后，回到这个已有项目根目录继续。

### 第 4 步：确认 CLI 可用

优先照安装脚本输出使用 `ai-sdlc` 或 `python -m ai_sdlc`。

```bash
ai-sdlc --help
```

如果 `ai-sdlc` 找不到：

```bash
python -m ai_sdlc --help
```

成功时你应该看到命令帮助，且命令列表里包含 `init`。

### 第 5 步：确认你仍在已有项目根目录

安装或更新完成后，终端可能还停在安装包目录。继续前先回到已有项目根目录。

macOS / Linux：

```bash
pwd
```

Windows PowerShell：

```powershell
Get-Location
```

确认路径是你的业务项目后，继续下一步。

### 第 6 步：初始化这个已有项目

**这一步在哪执行：**

- 终端
- 不在 IDE 聊天输入框执行

**Windows / macOS / Linux 都直接复制：**

```bash
python -m ai_sdlc init .
```

如果当前终端是交互式 TTY，`init` 会先让你选择 AI 代理入口和项目 shell。选择完成后，CLI 会自动继续做必要检查和安全预演。

如果你非常确定自己真正聊天的工具和 shell，也可以第一次就直接指定。例如你是在 VS Code 里用 Codex 聊天，终端是 PowerShell，可以直接执行：

```bash
python -m ai_sdlc init . --agent-target codex --shell powershell
```

**执行成功以后，你应该看到：**

- 输出里出现 `Initialized AI-SDLC project`
- 项目根目录里出现 `.ai-sdlc`
- 由于这是已有项目，输出里可能会出现 existing project / deep scan / baseline 之类的信息
- 输出里出现 `当前结果 / Result`
- 输出里出现 `下一步 / Next`
- `下一步 / Next` 告诉你切换到 AI 对话输入增量需求

你可以把结果大致对照成下面这样：

```text
╭──────────────── ai-sdlc init ────────────────╮
│ Detected existing project                    │
│ Initialized AI-SDLC project                  │
│   Path: .../my-existing-project/.ai-sdlc     │
│                                               │
│ 当前结果 / Result                            │
│   初始化完成。安全预演已自动执行；如果仍有   │
│ 开放门禁，已有项目或未完成需求出现这个结果   │
│ 是正常的。                                    │
│                                               │
│ 下一步 / Next                                │
│   不用再手动执行初始化命令；现在切换到       │
│ Codex/AI 对话中输入你的需求即可。            │
╰───────────────────────────────────────────────╯
```

### 第 7 步：切换到 IDE 聊天输入框

**这一步在哪执行：**

- Cursor / Codex / Claude Code 的聊天输入框
- 不在终端执行

你现在已经完成了：

- 安装
- 验证
- 初始化
- CLI 自动安全预演

现在可以开始在聊天输入框里说增量需求。

**直接复制下面这段到 IDE 聊天输入框：**

```text
我已经在这个已有项目根目录执行过：
1. python -m ai_sdlc init .

现在我要做一个增量需求。
需求是：我想新增一个E2E的UI测试场景覆盖。

请按 AI-SDLC 流程，先帮我做需求澄清、影响分析、拆解和设计，不要直接写代码。
```

**如果你不是打一行文字，而是要上传 PRD 或已有需求说明，也是在这一步上传。**

你可以直接复制：

```text
我已经在这个已有项目根目录执行过：
1. python -m ai_sdlc init .

我现在会上传一份已有需求说明或 PRD。
请先基于它做增量需求分析、影响分析、拆解和设计，不要直接写代码。
```

**到这里，这个已有项目的全流程也跑通了。**

你应该已经清楚：

- 命令还是在终端执行
- 初始化还是在终端执行
- 真正开始需求沟通，是在 IDE 聊天输入框里执行自然语言对话
- 只有当 CLI 明确报错或 `下一步 / Next` 要求时，才执行额外排查命令

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
| program solution-confirm --execute --continue --yes | `python -m ai_sdlc program solution-confirm --execute --continue --yes` | 确认后继续进入 managed delivery apply | **可能写 adapter**；会先写 solution snapshot，再进入 apply；若 `requested_* != effective_*`，还需额外提供 `--ack-effective-change` |
| program managed-delivery-apply --dry-run | `python -m ai_sdlc program managed-delivery-apply --dry-run` | managed delivery apply 预览 | **可能写 adapter**；若省略 `--request`，会从 current truth 物化 request，并显示 guard / blocker / next step |
| program managed-delivery-apply --execute --yes | `python -m ai_sdlc program managed-delivery-apply --execute --yes` | 执行 managed delivery apply | **可能写 adapter**；若省略 `--request` 且 `requested_* != effective_*`，还需额外提供 `--ack-effective-change`；会把组件库包真正安装到 `managed/frontend/`，更新 lockfile，并在需要时安装 Playwright browser runtime |
| program browser-gate-probe --dry-run | `python -m ai_sdlc program browser-gate-probe --dry-run` | browser gate 预演 | **可能写 adapter**：命令主体只读；会显示 managed frontend target、delivery entry、component packages 与 overall gate status preview |
| program browser-gate-probe --execute | `python -m ai_sdlc program browser-gate-probe --execute` | 执行 browser gate probe | **可能写 adapter**：会写 `.ai-sdlc/memory/frontend-browser-gate/latest.yaml`，并显式显示 delivery entry、component packages、gate status 与下一条命令；如果 visual bootstrap 已经可用，下一条通常会指向 `program browser-gate-baseline --execute --yes` |
| program browser-gate-baseline --dry-run | `python -m ai_sdlc program browser-gate-baseline --dry-run` | 查看当前 visual bootstrap 是否已满足 baseline 提升条件 | **可能写 adapter**：命令主体只读；会显示当前 artifact、gate run、matrix id、baseline state 与 blocker |
| program browser-gate-baseline --execute --yes | `python -m ai_sdlc program browser-gate-baseline --execute --yes` | 正式提升 browser gate 的 visual bootstrap baseline | **可能写 adapter**：会把 visual-regression bootstrap capture 复制到 `governance/frontend/quality-platform/evidence/visual-regression/baselines/<matrix-id>/baseline.png` 并写 `baseline.yaml` |
| program page-ui-schema-handoff | `python -m ai_sdlc program page-ui-schema-handoff` | 查看 `147` 的 provider/kernel handoff surface | **可能写 adapter**：命令主体只读；依赖既有 `.ai-sdlc/memory/frontend-solution-confirmation/latest.yaml`，若缺失会返回 blocker |
| program delivery-registry-handoff | `python -m ai_sdlc program delivery-registry-handoff` | 查看当前技术栈选择命中的官方 delivery entry、组件库包集合与 prerequisite | **可能写 adapter**：命令主体只读；会显示 install strategy、component packages、provider manifest/style-support 引用与当前 prerequisite gap |
| program generation-constraints-handoff | `python -m ai_sdlc program generation-constraints-handoff` | 查看后续代码生成默认继承的组件库上下文与 generation constraints | **可能写 adapter**：命令主体只读；会显示 delivery entry、component packages、page schema ids、allowed recipes 与 whitelist components |
| program theme-token-governance-handoff | `python -m ai_sdlc program theme-token-governance-handoff` | 查看默认继承 generation truth 的 theme governance handoff、requested/effective theme 与 override diagnostics | **可能写 adapter**：命令主体只读；依赖既有 solution snapshot、generation truth 与 provider style-support truth，若缺失会返回 blocker |
| program quality-platform-handoff | `python -m ai_sdlc program quality-platform-handoff` | 查看默认继承 generation/theme truth 的质量矩阵、组件库上下文与 evidence contracts | **可能写 adapter**：命令主体只读；会显示 delivery entry、component packages、page schema ids、quality diagnostics 与 evidence contracts |
| program cross-provider-consistency-handoff | `python -m ai_sdlc program cross-provider-consistency-handoff` | 查看默认继承 generation/theme/quality truth 的跨组件库一致性 pair diagnostics | **可能写 adapter**：命令主体只读；会显示 page schema ids、pair counts、pair diagnostics 与 blocker/warning |
| program provider-expansion-handoff | `python -m ai_sdlc program provider-expansion-handoff` | 查看 provider expansion 的公开选择面、roster admission 与 React 暴露边界 | **可能写 adapter**：命令主体只读；会显示 requested/effective frontend stack、provider diagnostics、react visibility 与 blocker/warning |
| program provider-runtime-adapter-handoff | `python -m ai_sdlc program provider-runtime-adapter-handoff` | 查看 runtime adapter 的 scaffold / runtime delivery / evidence return truth | **可能写 adapter**：命令主体只读；会显示 carrier mode、runtime delivery state、evidence return state 与 provider diagnostics |
| program integrate --dry-run | `python -m ai_sdlc program integrate --dry-run` | guarded integration runbook 预览 | **可能写 adapter**；若带 `--report`，还会写 report 文件 |
| program integrate --execute --yes | `python -m ai_sdlc program integrate --execute --yes` | guarded execute gate | **可能写 adapter**；当前会做 gate 校验与可选 report 写入，不会直接替你修改各 spec 内容 |
| rules materialize-frontend-page-ui-schema | `python -m ai_sdlc rules materialize-frontend-page-ui-schema` | materialize `147` 的 canonical page/ui schema artifacts | **可能写 adapter**：命令本身会把 artifact 写到 `kernel/frontend/page-ui-schema/`；CLI 入口仍可能先触发 adapter apply |
| rules materialize-frontend-mvp | `python -m ai_sdlc rules materialize-frontend-mvp` | materialize frontend governance artifacts，并优先绑定当前项目的 generation delivery context | **可能写 adapter**：命令本身会把 artifact 写到 `governance/frontend/gates/` 与 `governance/frontend/generation/`；若当前项目已有 solution snapshot，会把 delivery entry、component packages、page schema ids 一并写入 `generation.manifest.yaml` |
| rules materialize-frontend-theme-token-governance | `python -m ai_sdlc rules materialize-frontend-theme-token-governance` | materialize `148` 的 canonical theme governance artifacts，并消费当前 generation truth | **可能写 adapter**：命令本身会把 artifact 写到 `governance/frontend/theme-token-governance/`；若当前项目已有 solution snapshot，会继承 delivery entry、component packages、page schema ids 与 requested/effective theme |
| rules materialize-frontend-quality-platform | `python -m ai_sdlc rules materialize-frontend-quality-platform` | materialize `149` 的 canonical quality platform artifacts，并消费当前 generation/theme truth | **可能写 adapter**：命令本身会把 artifact 写到 `governance/frontend/quality-platform/`；会继承 delivery entry、component packages、page schema ids、theme governance 与 evidence contracts |
| rules materialize-frontend-cross-provider-consistency | `python -m ai_sdlc rules materialize-frontend-cross-provider-consistency` | materialize `150` 的 canonical cross-provider consistency artifacts，并消费当前 theme/quality truth | **可能写 adapter**：命令本身会把 artifact 写到 `governance/frontend/cross-provider-consistency/`；会继承 page schema ids、pair certification truth 与 upstream quality evidence refs |
| rules materialize-frontend-provider-expansion | `python -m ai_sdlc rules materialize-frontend-provider-expansion` | materialize `151` 的 canonical provider expansion artifacts | **可能写 adapter**：命令本身会把 artifact 写到 `governance/frontend/provider-expansion/`；会落 choice surface、react exposure boundary 与各 provider 的 roster/certification aggregate |
| rules materialize-frontend-provider-runtime-adapter | `python -m ai_sdlc rules materialize-frontend-provider-runtime-adapter` | materialize `153` 的 canonical provider runtime adapter artifacts | **可能写 adapter**：命令本身会把 artifact 写到 `governance/frontend/provider-runtime-adapter/`；会落 adapter targets、runtime boundary receipt 与各 provider 的 scaffold contract |
| manual telemetry | `python -m ai_sdlc telemetry open-session`、`record-*`、`close-session` | operator evidence write | **会写 telemetry**：落到 `.ai-sdlc/local/telemetry/` 与派生 indexes；CLI 入口本身也可能先触发 adapter apply |
| workitem init | `python -m ai_sdlc workitem init --title "新 capability 标题"` | direct-formal 初始化 formal work item | **会写 formal docs**：仅适用于已完成 `ai-sdlc init .` 的项目；直接创建 `specs/<WI>/spec.md`、`plan.md`、`tasks.md`；如果根目录尚无 `program-manifest.yaml`，现在会先自动创建最小 manifest 并写入当前 spec entry；不会要求先写 `docs/superpowers/*` |
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
- 确认后继续进入 apply：
  - `python -m ai_sdlc program solution-confirm --execute --continue --yes`
  - 会先写 `.ai-sdlc/memory/frontend-solution-confirmation/latest.yaml`，再进入 managed delivery apply。
  - 如果 `requested_* != effective_*`，必须额外带上 `--ack-effective-change`。

这里有三个边界需要明确：

- `will_change_on_confirm` 只属于确认前的派生展示字段，不会写入最终 snapshot artifact。
- 如果请求的 enterprise 方案不可用，但存在允许的退路，CLI 会保留 `requested_*`，并把 fallback 结果写到 `effective_*`。
- 如果预检结果是 `blocked`，命令会停止在确认 gate，不应把它理解为“已自动完成技术选型”。

### 7.0.1) `program managed-delivery-apply` 的最小使用面

`program managed-delivery-apply` 是当前 managed delivery request / execute / artifact 的独立入口。

- request 预览：
  - `python -m ai_sdlc program managed-delivery-apply --dry-run`
  - 若省略 `--request`，CLI 会从 current truth 自动物化 request，并展示 selected actions、blockers 与 next steps。
- 执行显式 request：
  - `python -m ai_sdlc program managed-delivery-apply --request <path> --execute --yes`
  - 会执行该 request 对应的 narrow apply runtime，并写 `.ai-sdlc/memory/frontend-managed-delivery-apply/latest.yaml`。
- 执行 truth-derived request：
  - `python -m ai_sdlc program managed-delivery-apply --execute --yes`
  - 若省略 `--request` 且 current truth 中存在 `requested_* != effective_*`，必须额外带上 `--ack-effective-change`，否则命令会 fail-closed。
  - 当前 truth-derived path 默认会在 `managed/frontend/` 下写出最小受控前端产物，包括 `index.html`、`src/generated/frontend-delivery-context.ts` 与 `src/App.vue`。

这里也有两个边界：

- `--ack-effective-change` 只约束“从 current truth 自动物化 request”的路径，不额外注入到显式 `--request` 回放路径。
- `Managed Delivery Apply Result` 不是最终交付完成态；`apply_succeeded_pending_browser_gate` 仍表示 browser gate 尚未运行。

### 7.0.2) `program browser-gate-probe` 的最小使用面

`program browser-gate-probe` 是当前 browser gate 执行面。

- 预演：
  - `python -m ai_sdlc program browser-gate-probe --dry-run`
  - 会读取最新的 managed delivery apply artifact，显示当前 `managed frontend target`、`delivery entry`、`provider theme adapter`、`component packages`、`page schema ids` 与 preview gate status。
- 执行：
  - `python -m ai_sdlc program browser-gate-probe --execute`
  - 会写 `.ai-sdlc/memory/frontend-browser-gate/latest.yaml`，并把当前 delivery context 一并带进 `execution_context` 与 `bundle_input`。
  - 默认会优先消费 `managed/frontend/index.html` 作为最小 browser entry。
  - 当前基线会校验页面已渲染内容是否覆盖当前 `delivery entry`、`component packages` 与 `page schema ids`；不一致时会诚实返回 blocker。

这里也有两个边界：

- 这一步只表示 browser gate 执行面已继承当前组件库选择，不代表 provider-specific 质量探针已经全部实现。
- 如果 Playwright runner 或运行时不可用，artifact 会诚实返回 `recheck_required` / `incomplete`，而不是把当前组件库误报成已验收通过。

### 7.0.3) `program browser-gate-baseline` 的最小使用面

`program browser-gate-baseline` 是当前 visual-regression baseline promotion 的正式入口。

- 预演：
  - `python -m ai_sdlc program browser-gate-baseline --dry-run`
  - 会读取最近一次 browser gate artifact，显示当前 `gate run`、`matrix id`、`baseline state`、`bootstrap artifact`、`baseline image path` 与 `baseline metadata path`。
- 执行：
  - `python -m ai_sdlc program browser-gate-baseline --execute --yes`
  - 会把最近一次 browser gate 中的 `visual_regression_bootstrap` capture 提升成正式 baseline，写到 `governance/frontend/quality-platform/evidence/visual-regression/baselines/<matrix-id>/baseline.png` 和 `baseline.yaml`。
- 执行完以后：
  - 下一步应该重新执行 `python -m ai_sdlc program browser-gate-probe --execute`
  - 用新 baseline 再跑一轮 gate，确认最终状态是不是已经变成 `passed`

这里有三个边界：

- baseline 来源是 `visual_regression_bootstrap`，不是 smoke 的 `navigation_screenshot`。
- 这个命令本身不重新跑浏览器，只负责把最近一次 gate 产出的 bootstrap capture 提升成正式 baseline。
- 如果最近一次 browser gate 还没有生成 bootstrap capture，这个命令会 fail-closed，并诚实返回 blocker。

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

### 7.2) `theme-token-governance` 的最小使用面

`148` 引入的 theme/token governance runtime baseline 也有两个最小入口：

- materialize canonical artifacts：
  - `python -m ai_sdlc rules materialize-frontend-theme-token-governance`
  - 会把 theme governance manifest、token mapping、override policy、style editor boundary 写到 `governance/frontend/theme-token-governance/`。
- 查看 theme governance handoff：
  - `python -m ai_sdlc program theme-token-governance-handoff`
  - 会读取当前 `.ai-sdlc/memory/frontend-solution-confirmation/latest.yaml` 与 provider style-support truth，把 `148` 的 requested/effective theme、page-schema coverage、override diagnostics 拼成可读 handoff。

这里同样有三个边界需要明确：

- `theme-token-governance-handoff` 是只读 surfaced diagnostics，不会自动替你执行 override；Track C/D 的 runtime truth 由 `quality-platform-handoff` / `cross-provider-consistency-handoff` 与对应 materialize 命令继续承接。
- `149/150` 现在已经接进当前项目的 upstream truth：quality platform 会继承 generation/theme truth，cross-provider consistency 会继承 theme/quality truth；provider expansion 仍是独立后续承接项。
- 如果 solution snapshot、provider style-support 或 theme governance artifacts 缺失 / 损坏，命令与 `verify constraints` 都会诚实返回 `blocked` / `RETRY`，而不会静默回退为默认值。

### 7.3) `quality-platform` / `cross-provider-consistency` 的最小使用面

现在 Track C/D 也已经接到当前项目的 upstream truth，最小入口各有两条：

- materialize `149` quality platform artifacts：
  - `python -m ai_sdlc rules materialize-frontend-quality-platform`
  - 会把 quality platform manifest、coverage matrix、evidence platform、interaction quality、truth surfacing 写到 `governance/frontend/quality-platform/`。
- 查看 `149` quality platform handoff：
  - `python -m ai_sdlc program quality-platform-handoff`
  - 会读取当前 solution snapshot、resolved theme governance 与 quality platform truth，把 delivery entry、component packages、page schema coverage、quality diagnostics 与 evidence contracts 拼成可读 handoff。
- materialize `150` cross-provider consistency artifacts：
  - `python -m ai_sdlc rules materialize-frontend-cross-provider-consistency`
  - 会把 consistency manifest、readiness gate、truth surfacing，以及每个 provider pair 的 diff/certification/evidence index 写到 `governance/frontend/cross-provider-consistency/`。
- 查看 `150` cross-provider consistency handoff：
  - `python -m ai_sdlc program cross-provider-consistency-handoff`
  - 会读取当前 generation/theme/quality upstream truth，把 page schema ids、pair counts、pair diagnostics、blockers/warnings 拼成可读 handoff。

这里也有三个边界需要明确：

- 这两个 handoff 都是只读 surfaced diagnostics，不会替你自动执行安装、切换 provider 或补齐证据。
- `verify constraints` 现在会把 upstream theme/quality artifacts 漂移当成显式 gate，而不是静默忽略。
- provider expansion、runtime adapter 与真实组件库交付仍是独立后续能力，不等同于 `149/150` 已经替业务项目自动落地这些动作。

### 7.4) `provider-expansion` / `provider-runtime-adapter` 的最小使用面

Track E/F 现在也各有一条只读 handoff 和一条 canonical materialize 入口：

- materialize `151` provider expansion artifacts：
  - `python -m ai_sdlc rules materialize-frontend-provider-expansion`
  - 会把 provider expansion manifest、truth surfacing、choice surface policy、react exposure boundary，以及每个 provider 的 admission / roster-state / certification aggregate 写到 `governance/frontend/provider-expansion/`。
- 查看 `151` provider expansion handoff：
  - `python -m ai_sdlc program provider-expansion-handoff`
  - 会读取当前 solution snapshot 与 provider expansion truth，把 requested/effective frontend stack、公开选择面、react visibility 与 provider diagnostics 拼成可读 handoff。
- materialize `153` provider runtime adapter artifacts：
  - `python -m ai_sdlc rules materialize-frontend-provider-runtime-adapter`
  - 会把 runtime adapter manifest、adapter targets，以及每个 provider 的 scaffold contract / runtime boundary receipt 写到 `governance/frontend/provider-runtime-adapter/`。
- 查看 `153` provider runtime adapter handoff：
  - `python -m ai_sdlc program provider-runtime-adapter-handoff`
  - 会读取当前 solution snapshot 与 runtime adapter truth，把 carrier mode、runtime delivery state、evidence return state 与 provider diagnostics 拼成可读 handoff。

这里也有三个边界需要明确：

- `151` 解决的是“哪些 provider 可以公开出现在选择面上，以及 React 能否暴露”，不是自动把它们装进目标项目。
- `153` 解决的是“target project adapter scaffold 与 runtime boundary receipt 是否存在”，不是自动替你完成真实组件库安装、注册或业务接线。
- 如果 solution snapshot 缺失，`provider-expansion-handoff` / `provider-runtime-adapter-handoff` 会诚实返回 `blocked`；若只有 scaffold 存在但 runtime delivery/evidence 仍未完成，也会如实显示 `scaffolded` / `missing`，不会伪装成已可用。

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
