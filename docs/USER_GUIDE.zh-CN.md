# AI-SDLC 实战用户手册（中文版）

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

## 3. 快速开始（5 分钟）

### 3.1 环境准备

- Python `>=3.11`
- 推荐使用 `uv`（也支持 `pip`）

### 3.2 安装（开发模式）

```bash
# 方式 A：uv
uv sync --dev

# 方式 B：pip editable
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

### 3.3 查看命令

```bash
ai-sdlc --help
```

### 3.4 初始化项目

在你的工程目录执行：

```bash
ai-sdlc init .
```

初始化后会生成 `.ai-sdlc/`，并自动进行 IDE 适配落地。

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
- `.ai-sdlc/project/config/project-config.yaml`：项目配置（含 IDE 识别/适配记录）
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

## 12. 完全离线环境：一键打包 + 一键安装（含 Windows）

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

Linux/macOS：

```bash
tar xzf ai-sdlc-offline-0.1.0.tar.gz
cd ai-sdlc-offline-0.1.0
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

安装后在你的项目目录执行：

```bash
ai-sdlc --help
ai-sdlc init .
```

---

## 13. 多 SPEC Program 命令（分阶段上线）

当你的 PRD 需要拆成多个 `specs/NNN-*` 时，使用 Program 命令进行程序级校验与计划：

```bash
ai-sdlc program validate --manifest program-manifest.yaml
ai-sdlc program status --manifest program-manifest.yaml
ai-sdlc program plan --manifest program-manifest.yaml
ai-sdlc program integrate --dry-run --manifest program-manifest.yaml
```

命令语义（当前阶段）：

- `validate`：检查 manifest 格式、依赖引用、环依赖、路径有效性。
- `status`：查看各 spec 的阶段提示、任务完成度和阻塞依赖。
- `plan`：输出拓扑顺序和并行 tiers（可并行分组）。
- `integrate --dry-run`：输出程序级收口预演步骤（合并顺序、验证矩阵、归档检查），不执行 merge/push。

拆分规则与收口规范见：`docs/SPEC_SPLIT_AND_PROGRAM.zh-CN.md`。

