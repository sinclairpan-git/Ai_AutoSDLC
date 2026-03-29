# AI-SDLC 小白实操手册

这份文档只有两章。
第一章用一个空项目，从 0 开始，完整跑到“可以开始在 IDE 聊天窗里说需求”。
第二章用一个已有项目，从安装一直跑到“可以开始在 IDE 聊天窗里说增量需求”。

**先记住一条铁规则：**

- `python -m ai_sdlc ...` 这类命令，永远在**终端**执行。
- Cursor / Codex / Claude Code 的**聊天输入框**，永远只发自然语言，不发 shell 命令。

如果你问“最合适在哪里执行命令”，我的答案是：

- 最合适：先用 Cursor / Codex / Claude Code 打开项目文件夹一次，然后在这个 IDE 自带的 Terminal 里执行本文命令。
- 也可以：Windows 用 PowerShell，macOS 用 Terminal。
- 但是不管你用哪种终端，**都不要把 `python -m ai_sdlc init .` 这种命令粘贴到 IDE 聊天输入框里。**

如果你问“PowerShell 怎么识别 IDE”，答案是：

- 不是 PowerShell 识别 IDE。
- AI-SDLC 识别的是项目里的 IDE 标记目录，例如 `.cursor`、`.codex`、`.claude`、`.vscode`。
- 所以最稳的做法是：**先用你的 IDE 打开项目文件夹一次，再去终端跑 `init`。**
- 如果你先在 PowerShell 跑了 `init`，后面才打开 IDE，也没关系。打开 IDE 以后，再在终端执行一次 `python -m ai_sdlc status`，AI-SDLC 仍然可以补装 IDE 适配文件。

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

**Windows 直接复制：**

```powershell
cd D:\work
mkdir ui-test-platform
cd ui-test-platform
```

**macOS 直接复制：**

```bash
cd ~/work
mkdir ui-test-platform
cd ui-test-platform
```

**执行成功以后，你应该看到：**

- 终端当前目录已经进入 `ui-test-platform`
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

**执行成功以后，你应该看到：**

- Windows 至少显示 `Python 3.11.x`
- macOS 至少显示 `Python 3.11.x`

**如果报错：**

- Windows 如果提示找不到 `py` 或没有 3.11，请先安装 Python 3.11+
- macOS 如果版本低于 3.11，请先安装 Python 3.11+
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
pip install "https://github.com/sinclairpan-git/Ai_AutoSDLC/archive/refs/tags/v0.2.5.zip"
```

**macOS 直接复制：**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install "https://github.com/sinclairpan-git/Ai_AutoSDLC/archive/refs/tags/v0.2.5.zip"
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

### 第 5 步：验证 AI-SDLC 安装成功

**这一步在哪执行：**

- 终端

**Windows / macOS 都直接复制：**

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

- 如果重新激活后还是不行，回到上一步重新安装，不要继续往下走

### 第 6 步：初始化这个空项目

**这一步在哪执行：**

- 终端
- 不在 IDE 聊天输入框执行

**Windows / macOS 都直接复制：**

```bash
python -m ai_sdlc init .
```

**执行成功以后，你应该看到：**

- 输出里出现 `Initialized AI-SDLC project`
- 当前项目目录里出现 `.ai-sdlc`
- 如果你前面已经用 Cursor / Codex / Claude Code 打开过这个项目，输出里还可能出现 `IDE 适配`

**如果你前面忘了先打开 IDE：**

没关系。现在先去用你的 IDE 打开这个项目文件夹一次，然后回到终端执行：

```bash
python -m ai_sdlc status
```

执行成功以后，你应该看到：

- `status` 正常输出项目状态
- IDE 适配文件有机会在这一步补装

### 第 7 步：现在不要聊天，先在终端里做一次预演启动

**这一步在哪执行：**

- 终端
- 不在 IDE 聊天输入框执行

**Windows / macOS 都直接复制：**

```bash
python -m ai_sdlc run --dry-run
```

**这一步的真实含义：**

- 这是“启动框架的预演”
- 不是在这里输入需求
- 不是在这里手工写 `spec.md`
- 按当前框架设计，**第一次空项目 `init` 之后，不要求你先手工创建 `spec.md` 再执行这条命令**

**执行成功以后，你至少应该看到：**

- 命令执行结束，回到终端提示符
- 没有出现 `No module named ai_sdlc`
- 没有出现 `Not inside an AI-SDLC project`

**如果报错说需要 `recover --reconcile`：**

直接复制下面三条：

```bash
python -m ai_sdlc recover --reconcile
python -m ai_sdlc status
python -m ai_sdlc run --dry-run
```

**如果你第一次空项目执行 `run --dry-run` 就提示缺少 `spec.md`：**

不要自己手工建 `spec.md`。
先直接复制下面这三条：

```bash
python -m ai_sdlc init .
python -m ai_sdlc status
python -m ai_sdlc run --dry-run
```

如果仍然报旧状态相关错误，再执行：

```bash
python -m ai_sdlc recover --reconcile
python -m ai_sdlc run --dry-run
```

### 第 8 步：到这里，才切换到 IDE 聊天输入框

**这一步在哪执行：**

- Cursor / Codex / Claude Code 的聊天输入框
- 不在终端执行

到这一步，你已经完成了：

- 安装
- 验证
- 初始化
- 预演启动

现在你可以开始需求沟通、需求扩展、拆解和设计。

**如果你只是打一段一句话需求，直接复制下面这段到 IDE 聊天输入框：**

```text
我已经在这个项目根目录执行过：
1. python -m ai_sdlc init .
2. python -m ai_sdlc run --dry-run

现在我要开始一个新需求。
需求是：我想开发一个全自动的UI测试平台。

请按 AI-SDLC 流程，先帮我做需求澄清、扩展、拆解和设计，不要直接写代码。
```

**如果你已经有 PRD，要上传 PRD，也是在这一步做。**

你可以在 IDE 聊天输入框直接复制：

```text
我已经在这个项目根目录执行过：
1. python -m ai_sdlc init .
2. python -m ai_sdlc run --dry-run

我现在会上传一份 PRD。
请先基于这份 PRD 做需求澄清、范围确认和设计，不要直接开始写代码。
```

**到这里，这个空项目的全流程就跑通了。**

你应该已经清楚：

- 安装命令在终端执行
- 初始化命令在终端执行
- `run --dry-run` 在终端执行
- 只有 `init` 和 `run --dry-run` 做完以后，才进入 IDE 聊天输入框说需求

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
cd D:\work\my-existing-project
```

**macOS 直接复制：**

```bash
cd ~/work/my-existing-project
```

**执行成功以后，你应该看到：**

- 当前终端已经位于已有项目的根目录

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

**执行成功以后，你应该看到：**

- Python 版本至少是 `3.11.x`

**如果报错：**

- 先安装 Python 3.11+
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
pip install "https://github.com/sinclairpan-git/Ai_AutoSDLC/archive/refs/tags/v0.2.5.zip"
```

**macOS 直接复制：**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install "https://github.com/sinclairpan-git/Ai_AutoSDLC/archive/refs/tags/v0.2.5.zip"
```

**执行成功以后，你应该看到：**

- 项目根目录里出现 `.venv`
- `pip install` 完成，没有报错

### 第 5 步：验证安装成功

**这一步在哪执行：**

- 终端

**Windows / macOS 都直接复制：**

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

### 第 6 步：初始化这个已有项目

**这一步在哪执行：**

- 终端
- 不在 IDE 聊天输入框执行

**Windows / macOS 都直接复制：**

```bash
python -m ai_sdlc init .
```

**执行成功以后，你应该看到：**

- 输出里出现 `Initialized AI-SDLC project`
- 项目根目录里出现 `.ai-sdlc`
- 由于这是已有项目，输出里可能会出现 existing project / deep scan / baseline 之类的信息

### 第 7 步：看一下当前状态

**这一步在哪执行：**

- 终端

**Windows / macOS 都直接复制：**

```bash
python -m ai_sdlc status
```

**执行成功以后，你应该看到：**

- 一张项目状态表
- 说明 AI-SDLC 已经认到这个已有项目了

### 第 8 步：先在终端做一次预演启动

**这一步在哪执行：**

- 终端
- 不在 IDE 聊天输入框执行

**Windows / macOS 都直接复制：**

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

**如果报错说需要 `recover --reconcile`：**

直接复制：

```bash
python -m ai_sdlc recover --reconcile
python -m ai_sdlc status
python -m ai_sdlc run --dry-run
```

### 第 9 步：到这里，才切换到 IDE 聊天输入框

**这一步在哪执行：**

- Cursor / Codex / Claude Code 的聊天输入框
- 不在终端执行

你现在已经完成了：

- 安装
- 验证
- 初始化
- 状态检查
- 预演启动

现在可以开始在聊天输入框里说增量需求。

**直接复制下面这段到 IDE 聊天输入框：**

```text
我已经在这个已有项目根目录执行过：
1. python -m ai_sdlc init .
2. python -m ai_sdlc status
3. python -m ai_sdlc run --dry-run

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
3. python -m ai_sdlc run --dry-run

我现在会上传一份已有需求说明或 PRD。
请先基于它做增量需求分析、影响分析、拆解和设计，不要直接写代码。
```

**到这里，这个已有项目的全流程也跑通了。**

你应该已经清楚：

- 命令还是在终端执行
- 初始化还是在终端执行
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

### 3) `accepted` 的含义

- `accepted` 表示“风险被接受/债务被接受”，不是“问题已解决”。
- 在治理汇总里，`accepted` 仍属于 open debt，不会计入 resolved。

### 4) `status --json` 与 `doctor` 的边界

- `python -m ai_sdlc status --json` 只输出 bounded telemetry surface：只读 manifest + latest index summaries。
- telemetry 缺失时会返回 `not_initialized`，并且不会创建 `.ai-sdlc/local/telemetry/`。
- `python -m ai_sdlc doctor` 的 telemetry readiness 仅做只读诊断：root 可写性、manifest 状态、registry 可解析性、writer path 有效性、resolver 健康、`status --json` surface 可用性。
- `doctor` 不会深度扫描 trace，不会隐式 rebuild indexes，也不会隐式初始化 telemetry 根目录。

### 5) `scan` 的边界

- `python -m ai_sdlc scan <path>` 是 operator/analysis 命令，用于做深度代码扫描并把摘要输出到终端。
- `scan` 可以深度读取仓库内容，但不会隐式初始化 `.ai-sdlc/`、不会触发 IDE adapter 写入，也不会替代 `run` / `stage run` 这类执行面。
- 如果你要生成或刷新工程知识基线，应该使用 `init`（已有项目初始化）或 `refresh`，而不是把 `scan` 当作写路径。

### 6) Operator surface 读写矩阵

先看一个总规则：

- 在已初始化项目里，除 `init`、`doctor`、`status`、`scan`、`verify` 外，CLI 默认会先尝试一次 **IDE adapter 幂等 apply**。
- 这意味着某些本来以“查看/规划”为主的命令，仍可能写入 `.cursor/`、`.vscode/`、`.codex/`、`.claude/` 或 `.ai-sdlc/project/config/project-config.yaml` 里的 adapter 元数据。

| Surface | 典型命令 | 主定位 | 仓库/本地状态影响 |
|---|---|---|---|
| bounded telemetry status | `python -m ai_sdlc status --json` | 只读 telemetry 摘要 | **只读**：不初始化 telemetry root，不 rebuild indexes，不触发 adapter |
| doctor | `python -m ai_sdlc doctor` | 只读诊断 | **只读**：不 deep scan trace，不触发 adapter |
| scan | `python -m ai_sdlc scan <path>` | operator / analysis | **analysis-only**：深度读取代码库并打印摘要；不初始化 `.ai-sdlc/`，不触发 adapter |
| stage show / status | `python -m ai_sdlc stage show <stage>` / `stage status` | 阶段查看 | **可能写 adapter**：命令主体只读，但在已初始化项目中可能先触发一次 IDE adapter 幂等 apply |
| stage run --dry-run | `python -m ai_sdlc stage run <stage> --dry-run` | 阶段预演 | **可能写 adapter**：命令本身只展示清单，不执行阶段步骤；但仍可能先触发 adapter apply |
| stage run | `python -m ai_sdlc stage run <stage>` | 阶段调度入口 | **可能写 adapter**：命令本身输出清单与引导，不自动替你执行步骤；但仍可能先触发 adapter apply |
| program validate / status / plan | `python -m ai_sdlc program ...` | Program 级校验与规划 | **可能写 adapter**：program service 自身以读和规划为主，但 CLI 入口仍可能先触发 adapter apply |
| program integrate --dry-run | `python -m ai_sdlc program integrate --dry-run` | guarded integration runbook 预览 | **可能写 adapter**；若带 `--report`，还会写 report 文件 |
| program integrate --execute --yes | `python -m ai_sdlc program integrate --execute --yes` | guarded execute gate | **可能写 adapter**；当前会做 gate 校验与可选 report 写入，不会直接替你修改各 spec 内容 |
| manual telemetry | `python -m ai_sdlc telemetry open-session`、`record-*`、`close-session` | operator evidence write | **会写 telemetry**：落到 `.ai-sdlc/local/telemetry/` 与派生 indexes；CLI 入口本身也可能先触发 adapter apply |
| offline build | `./packaging/offline/build_offline_bundle.sh` | 分发打包 | **会写本地构建产物**：写 `dist/`、`dist-offline/` 和 bundle archives，不修改业务仓源码 |
| offline install | `./install_offline.sh` / `install_offline.ps1` / `install_offline.bat` | bundle 本地安装 | **会写 bundle 目录**：创建 `.venv/` 并安装 wheel；不会替目标业务仓初始化 AI-SDLC |

判断一个命令是否“真的只读”，要同时看两层：

- 命令主体是否会写业务状态、telemetry 或离线产物
- 该命令是否处在会触发 IDE adapter 幂等 apply 的 CLI 入口上

## 框架自身开发补充

如果你不是在“业务项目里使用 AI-SDLC”，而是在 **AI-SDLC 仓库里开发 AI-SDLC 自身**，应改看这份文档：

- [框架自迭代开发与发布约定](./框架自迭代开发与发布约定.md)

这份补充文档专门解释：

- 为什么框架仓库内应优先使用 `uv run ai-sdlc ...`
- commit / push / PR / merge / pull / release 各自改变的是什么
- 为什么“刚 push 完”通常不需要再 pull
- 如何把 telemetry trace、约束违约、backlog、根因分析和回归验证串成自优化闭环
