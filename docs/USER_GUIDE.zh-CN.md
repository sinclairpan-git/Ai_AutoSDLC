# AI-SDLC 实战用户手册（中文版）

> **阅读顺序**：使用本工具前，请先完成 **[§3 安装与环境（第一步）](#user-guide-s3-install)**（含安装后验证）。再执行 `init`、流水线与日常命令。

## 1. 这套框架是什么

`AI-SDLC` 是一套 AI-Native 软件研发流程自动化框架，核心形态是一个 Python CLI（`ai-sdlc`）。

它把“需求 -> 设计 -> 分解 -> 验证 -> 执行 -> 收尾”串成可运行、可检查、可恢复的流水线，并通过规则与上下文文件让 LLM/Agent 在每个阶段都按统一标准执行。

---

## 2. 解决什么问题

- 把“靠人记流程”变成“命令驱动 + 状态可追踪”的工程流程
- 给 LLM 明确的阶段上下文和检查清单，减少跑偏
- 支持中断恢复（checkpoint），避免一次会话失败就丢进度
- 支持 IDE 自动适配（Cursor/VSCode/Codex/Claude Code），复制目录后开箱即用

---

<a id="user-guide-s3-install"></a>

## 3. 安装与环境（第一步）

**所有使用场景都请先完成：安装 → [安装验证](#user-guide-install-verify) → 再 `init`。**  
下面按常见路径组织；若某一步报错「找不到 `ai-sdlc`」，优先看 **[§3.7 Windows 与 PATH](#user-guide-win-path)**（macOS/Linux 同理：需激活 venv 或改用 `python -m ai_sdlc`）。

### 3.1 环境准备

- Python **`>=3.11`**
- 包管理：普通用户用 **`pip`** 即可；已安装 **`uv`** 时可用 `uv sync` / `uv run`（见 §3.5）

### 3.2 安装方式怎么选

| 你的情况 | 推荐小节 |
|----------|----------|
| 有公网，只要在本机用 CLI，不参与本仓库开发 | **[§3.3 在线安装（pip）](#user-guide-install-online)** |
| 无外网 / 内网 / 不能访问 PyPI、GitHub | **[§3.4 离线安装](#user-guide-install-offline)**，细节另见 **[§12](#user-guide-offline-chapter)** 与仓库 [`packaging/offline/README.md`](../packaging/offline/README.md) |
| 已克隆 `Ai_AutoSDLC` 仓库，想快速跑 CLI | **[§3.5 使用 uv（本仓库）](#user-guide-install-uv)** |
| 在本仓库里改框架代码 | **[§3.6 开发模式（可编辑安装）](#user-guide-install-dev)** |

<a id="user-guide-install-online"></a>

### 3.3 在线安装（pip，普通用户推荐）

> 适用：不在本仓库内开发，只想在本机安装并使用 `ai-sdlc`。

Windows / macOS / Linux（通用；**推荐不依赖本机 Git**，用 zip 源）：

```bash
python -m venv .venv
# Windows (PowerShell): .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -U pip
pip install "https://github.com/sinclairpan-git/Ai_AutoSDLC/archive/refs/tags/v0.2.3.zip"
```

安装完成后**务必**做 [§3.8 安装验证](#user-guide-install-verify)（`ai-sdlc --help` 或 `python -m ai_sdlc --help`）。Windows 若未激活 venv，可先使用：

```powershell
& .\.venv\Scripts\ai-sdlc.exe --help
```

若本机已安装 Git，也可改用（将标签换成当前发布版本，例如 `v0.2.3`）：

```bash
pip install "git+https://github.com/sinclairpan-git/Ai_AutoSDLC.git@v0.2.3"
```

<a id="user-guide-install-offline"></a>

### 3.4 离线安装（无外网）

适用：目标机无法访问 PyPI / GitHub，或使用内网镜像仍不可用。

1. **打包**（在联网机器、且尽量与目标机 **同一操作系统与 CPU 架构** 上执行）：仓库根目录执行 `./packaging/offline/build_offline_bundle.sh`，产物与目录说明见 [`packaging/offline/README.md`](../packaging/offline/README.md) 与下文 **[§12](#user-guide-offline-chapter)**。
2. **安装**：将离线包拷到目标机解压后，运行 `install_offline.sh`（Linux/macOS）或 `install_offline.ps1` / `install_offline.bat`（Windows）。**禁止**把在 macOS 上打好的 `wheels` 目录直接用于 Windows（反之亦然），否则会出现缺依赖或无法安装。
3. **验证**：与 [§3.8](#user-guide-install-verify) 相同；脚本结束时的提示也会给出 `Activate.ps1`、全路径 `ai-sdlc.exe` 与 `python -m ai_sdlc` 等写法。

维护者发布离线包前的检查清单见 [`packaging/offline/README.md`](../packaging/offline/README.md) 第五节。

<a id="user-guide-install-uv"></a>

### 3.5 使用 uv（本仓库）

> 适用：已克隆 `Ai_AutoSDLC` 仓库，且本机已安装 [uv](https://github.com/astral-sh/uv)。

```bash
cd /path/to/Ai_AutoSDLC
uv sync              # 参与框架开发可加: uv sync --dev
uv run ai-sdlc --help
```

`uv run` 会在项目环境中执行 CLI，不依赖全局 PATH 上的 `ai-sdlc`。

<a id="user-guide-install-dev"></a>

### 3.6 开发模式（可编辑安装）

> 适用：在本仓库内修改 `ai-sdlc` 源码并即时生效。

```bash
# 方式 A：uv
uv sync --dev
uv run ai-sdlc --help

# 方式 B：pip editable
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e ".[dev]"
ai-sdlc --help
```

<a id="user-guide-win-path"></a>

### 3.7 Windows：虚拟环境、PATH 与「找不到 ai-sdlc」

`ai-sdlc` 的可执行文件默认安装在虚拟环境的 `Scripts` 目录（例如 `.venv\Scripts\ai-sdlc.exe`）。**未激活 venv** 或 **未把 `Scripts` 加入 PATH** 时，直接在终端输入 `ai-sdlc` 会提示找不到命令，这是环境配置问题，不是 CLI 未安装。

建议顺序：

1. 创建并激活 venv（PowerShell）。若提示无法加载 `Activate.ps1`，仅当前进程放宽执行策略：

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

2. 确认能解析到命令：

   ```powershell
   Get-Command ai-sdlc
   ai-sdlc --help
   ```

3. 若仍失败，使用完整路径（venv 目录名按你实际为准）：

   ```powershell
   & .\.venv\Scripts\ai-sdlc.exe --help
   ```

4. 若已激活 venv 但习惯用解释器调用，可使用 `python -m ai_sdlc`（子命令与 `ai-sdlc` 相同），例如 `python -m ai_sdlc run --dry-run`。

**说明**：本框架**不会**替你修改 Windows 全局 PATH；在 Cursor / VS Code / Codex 等内置终端中，仍需使用已激活 venv 的终端，或上述全路径 / `python -m` 写法。

<a id="user-guide-install-verify"></a>

### 3.8 安装验证与故障自检

安装完成后，在**安装时所使用的同一虚拟环境**下执行（任选其一成功即可）：

```bash
ai-sdlc --help
```

若提示找不到 `ai-sdlc`，改用：

```bash
python -m ai_sdlc --help
```

需要查看当前 Python、`ai-sdlc` 是否在 PATH、典型 shim 路径时：

```bash
ai-sdlc doctor
# 或（不依赖 PATH 上的 ai-sdlc）
python -m ai_sdlc doctor
```

### 3.9 初始化项目

**在确认 §3.8 通过后**，在你的工程目录执行：

```bash
ai-sdlc init .
```

（若仅用 `python -m`，则：`python -m ai_sdlc init .`。后文示例默认已激活 venv。）

初始化后会生成 `.ai-sdlc/`，并自动进行 IDE 适配落地。

### 3.10 启动工程框架（强制入口）

> 关键说明：输入需求本身不会自动执行流水线。完成 `init` 后，需显式执行启动命令。

推荐入口（安全）：

```bash
ai-sdlc run --dry-run
```

通过后再执行：

```bash
ai-sdlc run
```

如果你偏好分阶段执行，可使用：

```bash
ai-sdlc stage run init --dry-run
```

---

## 4. 开箱即用 IDE 自动适配

### 4.1 生效时机

- 执行 `ai-sdlc init` 时自动生效
- 已初始化项目中，首次执行主要命令（如 `status/run/stage/...`）时自动校验并补齐

### 4.2 自动识别规则

优先看项目目录标记：

- `.cursor/` -> Cursor
- `.vscode/` -> VSCode
- `.codex/` -> Codex
- `.claude/` -> Claude Code

若都没有，走 `generic` 降级，不阻断主流程。

### 4.3 适配文件落地目标

- Cursor: `.cursor/rules/ai-sdlc.md`
- VSCode: `.vscode/AI-SDLC.md`
- Codex: `.codex/AI-SDLC.md`
- Claude Code: `.claude/AI-SDLC.md`
- Generic: `.ai-sdlc/memory/ide-adapter-hint.md`

### 4.4 幂等与安全策略

- 已存在且内容一致：跳过
- 已存在但用户改过：不覆盖（保护用户自定义）

---

## 5. 日常使用路径（实战）

### 5.1 最小流程

```bash
ai-sdlc init .
ai-sdlc status
ai-sdlc run --dry-run
ai-sdlc run
```

### 5.2 分阶段流程（更适合 LLM 协作）

```bash
ai-sdlc stage show init
ai-sdlc stage run init --dry-run
ai-sdlc stage status
```

可用阶段：

- `init`
- `refine`
- `design`
- `decompose`
- `verify`
- `execute`
- `close`

---

## 6. 命令清单（常用）

- `ai-sdlc init <path>`：初始化项目与基线
- `ai-sdlc status`：查看流程状态
- `ai-sdlc run [--dry-run] [--mode auto|confirm]`：执行主流水线
- `ai-sdlc stage show <name>`：查看阶段清单
- `ai-sdlc stage run <name> [--dry-run]`：执行单阶段
- `ai-sdlc stage status`：查看阶段状态
- `ai-sdlc scan`：深度扫描
- `ai-sdlc refresh`：知识刷新
- `ai-sdlc recover`：从 checkpoint 恢复

---

## 7. 框架结构、功能、和关键文件价值

以下是“你最需要理解”的结构，不是逐文件字典，而是按价值分层。

### 7.1 核心目录结构

- `src/ai_sdlc/cli/`：CLI 入口与命令编排层
- `src/ai_sdlc/routers/`：初始化与流程路由
- `src/ai_sdlc/core/`：运行器、配置、分发等核心机制
- `src/ai_sdlc/gates/`：质量门禁与规则检查
- `src/ai_sdlc/stages/`：阶段清单定义（YAML）
- `src/ai_sdlc/integrations/`：外部集成（如 IDE 适配）
- `src/ai_sdlc/adapters/`：IDE 适配模板资源
- `src/ai_sdlc/models/`：统一数据模型
- `tests/`：单元、集成、流程测试

### 7.2 关键文件价值（高频关注）

- `src/ai_sdlc/cli/main.py`
  - 价值：统一 CLI 总入口，注册子命令与全局钩子
  - 什么时候看：想知道命令生命周期先后顺序时

- `src/ai_sdlc/cli/commands.py`
  - 价值：`init/status/scan/refresh/...` 等主命令实现
  - 什么时候看：新增命令或改交互输出时

- `src/ai_sdlc/cli/run_cmd.py`
  - 价值：整条 SDLC 流水线命令入口（`run`）
  - 什么时候看：调整运行模式、确认点逻辑时

- `src/ai_sdlc/cli/stage_cmd.py`
  - 价值：单阶段执行接口（`stage show/run/status`）
  - 什么时候看：你想让 LLM 按阶段执行而非一次性全跑

- `src/ai_sdlc/routers/bootstrap.py`
  - 价值：项目初始化主逻辑（目录、状态文件、初始元数据）
  - 什么时候看：改初始化行为、首装体验时

- `src/ai_sdlc/core/runner.py`
  - 价值：全流程编排器，串联阶段、门禁、checkpoint
  - 什么时候看：流程推进、暂停恢复、失败重试策略

- `src/ai_sdlc/core/config.py`
  - 价值：项目 YAML 配置/状态读写，持久化核心
  - 什么时候看：新增配置字段、迁移配置结构

- `src/ai_sdlc/integrations/ide_adapter.py`
  - 价值：IDE 检测 + 适配文件幂等落地 + 配置记录
  - 什么时候看：扩展新 IDE、调整识别优先级

- `src/ai_sdlc/models/project.py`
  - 价值：项目配置/状态模型定义（包括 IDE 适配元信息）
  - 什么时候看：扩展配置 schema、保证向后兼容

- `src/ai_sdlc/adapters/*`
  - 价值：各 IDE 的最小模板资源
  - 什么时候看：调整提示词、规则文件内容

- `tests/unit/test_ide_adapter.py`
  - 价值：IDE 识别、幂等、降级策略的核心回归测试
  - 什么时候看：改自动适配逻辑之后

- `tests/integration/test_cli_*`
  - 价值：从命令层面验证端到端行为
  - 什么时候看：改 CLI 钩子、入口行为之后

---

## 8. `.ai-sdlc/` 目录里有什么

初始化后你会看到：

- `.ai-sdlc/project/config/project-state.yaml`：项目状态（是否初始化、时间戳等）
- `.ai-sdlc/project/config/project-config.yaml`：项目配置（含 IDE 识别/适配记录）。字段 `document_locale` 默认 `zh-CN`，表示框架生成的**面向人阅读的 Markdown**（扫描基线、脚手架等）以简体中文为主；流水线产物语言约定另见 `rules/pipeline.md`「产出语言」。
- `.ai-sdlc/memory/`：记忆与上下文沉淀（含 generic 适配 hint）

这部分是框架的“持久化大脑”，建议提交到版本库（除非你的团队有其他策略）。

---

## 9. 开发者工作流建议

```bash
uv run pytest
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv build
```

提交前至少保证：测试 + lint + build 全绿。

---

## 10. 常见问题（FAQ）

### Q1：为什么没有自动生成我期望的 IDE 文件？

- 先看项目里是否有对应标记目录（如 `.vscode/`）
- 确认已执行 `init` 或执行过主要命令
- 查看 `.ai-sdlc/project/config/project-config.yaml` 中 `detected_ide`

### Q2：会覆盖我已有的 IDE 配置吗？

不会。默认对已存在且用户改动过的目标文件不覆盖。

### Q3：未知 IDE 会不会影响流程？

不会。会自动降级到 `generic`，主流程继续执行。

---

## 11. 10 分钟实战 Demo（最后一章）

这一节给你一条可直接复制执行的最小闭环，目标是：

- 初始化一个项目
- 自动完成 IDE 适配
- 跑通状态查看与阶段命令
- 跑一次主流程 dry-run

### 11.1 准备一个演示项目目录

```bash
mkdir -p /tmp/ai-sdlc-demo/.vscode
cd /tmp/ai-sdlc-demo
```

> 这里提前建 `.vscode/`，是为了演示“自动识别 VSCode 并落地适配文件”。

### 11.2 初始化并验证自动适配

```bash
ai-sdlc init .
```

执行后预期：

- 生成 `.ai-sdlc/` 目录
- 自动生成 `.vscode/AI-SDLC.md`
- `project-config.yaml` 内可看到 `detected_ide: vscode`（或你的当前 IDE）

可选检查：

```bash
ls -la .vscode
ls -la .ai-sdlc/project/config
```

### 11.3 查看当前状态与可用命令

```bash
ai-sdlc --help
ai-sdlc status
ai-sdlc stage --help
```

### 11.4 运行阶段命令（LLM 友好）

```bash
ai-sdlc stage show init
ai-sdlc stage run init --dry-run
ai-sdlc stage status
```

### 11.5 运行主流程（先 dry-run）

```bash
ai-sdlc run --dry-run
```

如果 dry-run 结果符合预期，再执行：

```bash
ai-sdlc run
```

### 11.6 中断恢复演示（可选）

当你需要恢复流程时：

```bash
ai-sdlc recover
```

### 11.7 Demo 完成判定

满足以下条件即表示你已经跑通了一个最小实战闭环：

- `init` 成功，且 `.ai-sdlc/` 存在
- IDE 适配文件自动落地（如 `.vscode/AI-SDLC.md`）
- `status`、`stage`、`run --dry-run` 都可正常执行

到这里你就可以把这套流程迁移到真实项目中，开始按阶段协作开发。

---

<a id="user-guide-offline-chapter"></a>

## 12. 完全离线环境：一键打包 + 一键安装（含 Windows）

> **与 §3 的关系**：离线安装是 **[§3.4](#user-guide-install-offline)** 的展开版；通用安装顺序、验证命令与 Windows PATH 说明以 **[§3](#user-guide-s3-install)** 为准。

适用场景：他人电脑、服务器、内网、无 GitHub、无公网 PyPI。

### 12.1 联网机器打包

```bash
cd /path/to/Ai_AutoSDLC
./packaging/offline/build_offline_bundle.sh
```

产物：

- `dist-offline/ai-sdlc-offline-<version>.tar.gz`（Linux/macOS 推荐）
- `dist-offline/ai-sdlc-offline-<version>.zip`（Windows 推荐）

### 12.2 目标机离线安装

Linux/macOS（将 `0.2.3` 换成你手中离线包的实际版本目录名）：

```bash
tar xzf ai-sdlc-offline-0.2.3.tar.gz
cd ai-sdlc-offline-0.2.3
chmod +x install_offline.sh
./install_offline.sh
```

Windows（PowerShell）：

```powershell
powershell -ExecutionPolicy Bypass -File .\install_offline.ps1
```

Windows（批处理）：

```bat
install_offline.bat
```

> 注意：离线包依赖 wheel 与平台相关。Windows 用户请下载 Windows 包，macOS 用户请下载 macOS 包，不可混用。

安装后请先完成 **[§3.8 安装验证](#user-guide-install-verify)**，再进入业务项目目录。示例：

```bash
# 已激活 venv 时
ai-sdlc --help
ai-sdlc init .
```

Windows 若尚未激活 venv，可先验证：

```powershell
& .\.venv\Scripts\ai-sdlc.exe --help
# 或
& .\.venv\Scripts\python.exe -m ai_sdlc --help
```

---

## 13. 多 SPEC Program 命令（分阶段上线）

当你的 PRD 需要拆成多个 `specs/NNN-*` 时，使用 Program 命令进行程序级校验与计划：

```bash
ai-sdlc program validate --manifest program-manifest.yaml
ai-sdlc program status --manifest program-manifest.yaml
ai-sdlc program plan --manifest program-manifest.yaml
ai-sdlc program integrate --dry-run --manifest program-manifest.yaml
ai-sdlc program integrate --execute --yes --manifest program-manifest.yaml
```

命令语义（当前阶段）：

- `validate`：检查 manifest 格式、依赖引用、环依赖、路径有效性。
- `status`：查看各 spec 的阶段提示、任务完成度和阻塞依赖。
- `plan`：输出拓扑顺序和并行 tiers（可并行分组）。
- `integrate --dry-run`：输出程序级收口预演步骤（合并顺序、验证矩阵、归档检查），不执行 merge/push。
- `integrate --execute --yes`：执行受保护收口门禁（仅在门禁通过时返回成功），支持 `--allow-dirty` 临时放宽工作区干净检查。

拆分规则与收口规范见：`docs/SPEC_SPLIT_AND_PROGRAM.zh-CN.md`。

---

## 14. 如何开启“需求开发”与“Bug 修复”

### 14.1 新需求开发（Feature SOP）

适用：新增能力、需求迭代、模块扩展。

```bash
# 1) 进入项目并初始化（首次）
ai-sdlc init .

# 2) 先看当前状态
ai-sdlc status

# 3) 先 dry-run，再正式执行
ai-sdlc run --dry-run
ai-sdlc run
```

若你希望人工把关更细，使用阶段式：

```bash
ai-sdlc stage show init
ai-sdlc stage run init --dry-run
ai-sdlc stage run refine --dry-run
ai-sdlc stage run design --dry-run
ai-sdlc stage run decompose --dry-run
ai-sdlc stage run verify --dry-run
ai-sdlc stage run execute --dry-run
ai-sdlc stage run close --dry-run
```

多 SPEC 场景（Program）建议顺序：

```bash
ai-sdlc program validate --manifest program-manifest.yaml
ai-sdlc program status --manifest program-manifest.yaml
ai-sdlc program plan --manifest program-manifest.yaml
ai-sdlc program integrate --dry-run --manifest program-manifest.yaml
ai-sdlc program integrate --execute --yes --manifest program-manifest.yaml
```

### 14.2 Bug 修复（Bugfix SOP）

适用：线上问题修复、回归缺陷、兼容性问题。

```bash
# 1) 先确认当前状态与上下文
ai-sdlc status

# 2) 用阶段方式先做定位与验证准备（建议 dry-run）
ai-sdlc stage run refine --dry-run
ai-sdlc stage run design --dry-run
ai-sdlc stage run decompose --dry-run

# 3) 修复前后执行验证
ai-sdlc stage run verify --dry-run
ai-sdlc stage run execute --dry-run
ai-sdlc stage run close --dry-run
```

最小原则：

- 先复现、后修改；先验证、后收口。
- 优先最小改动面，避免“顺手大改”。
- 收口前确保测试、lint、关键流程检查通过。

---

## 15. 代码评审、测试评审与归档收口模板

### 15.1 代码评审（提交前）

建议按 `rules/code-review.md` 六维度执行：

- 宪章对齐（Critical）
- 需求规格对齐（Critical）
- 技术规范一致性
- 代码质量
- 测试质量
- Spec 偏移检测

### 15.2 测试评审（完成声明前）

最小验证命令（示例）：

```bash
uv run pytest -q
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

在任何“已完成”声明前，必须有新鲜命令输出证据（见 `rules/verification.md`）。

### 15.3 归档收口（Close）

收口时至少确认：

- `tasks.md` 中任务状态与实际一致
- `task-execution-log.md` 记录完整
- `development-summary.md` 已更新
- 最终测试/构建结果可追溯
- Git 提交与发布说明已同步

