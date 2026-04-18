# 功能规格：Agent Adapter Canonical Consumption Proof Carrier Baseline

**功能编号**：`162-agent-adapter-canonical-consumption-proof-carrier-baseline`
**创建日期**：2026-04-18
**状态**：进行中
**输入**：Current program truth is blocked only by adapter_canonical_consumption:unverified. Work items 159-161 already implemented runtime proof fields, release/program gate consumption, and dry-run/live close parity; the remaining gap is a real Codex canonical proof carrier that can machine-verifiably provide AI_SDLC_ADAPTER_CANONICAL_SHA256 and optional AI_SDLC_ADAPTER_CANONICAL_PATH without relying on operator inference or manual shell spoofing.

## 问题定义

`159` 已定义 canonical consumption proof 字段与环境变量协议，`160` 已把它接入 release/program truth，`161` 又把 dry-run/live close 的 close-check 语义拉齐。当前剩余 blocker 已收敛为：

- `adapter_canonical_consumption:unverified`
- `capability_closure_audit:partial`

这说明治理闭环已经能正确消费 proof，但仓库内仍缺少一个正式 carrier 去稳定地产生并传递 proof。现状只有两种路径：

1. 不提供 proof，release/program truth 持续 blocked
2. 由操作者手工导出 `AI_SDLC_ADAPTER_CANONICAL_SHA256` / `AI_SDLC_ADAPTER_CANONICAL_PATH`

第二种虽然能让既有协议转绿，但它仍依赖人工拷贝和人工绑定，既不利于重复执行，也容易把“本仓库计算出的 digest”退化成“操作者声称的 digest”。`162` 的目标不是放宽 gate，也不是伪造宿主原生消费事实，而是增加一个仓库支持的 proof carrier：它从当前 canonical 文件计算 proof，带着这个 proof 启动子命令，让下游 `adapter status` / `run` / `program truth` 在同一进程树内消费到一致的 canonical proof。

## 范围

- **覆盖**：
  - 新增一个显式 CLI carrier，用当前 canonical 文件生成 `AI_SDLC_ADAPTER_CANONICAL_SHA256` 与 `AI_SDLC_ADAPTER_CANONICAL_PATH`
  - carrier 以 `-- <command>` 形式执行子命令，并把 proof 注入子进程环境
  - 缺失 canonical 文件、target 不支持、proof 绑定不合法时 fail closed
  - 用单测和 CLI 集成测试锁定 carrier 的 red/green 路径
  - 回填 `162` formal docs、执行日志与 manifest handoff evidence
- **不覆盖**：
  - 不把“通过 carrier 启动命令”叙述成宿主原生消费证明
  - 不修改 `159/160/161` 已上线的 canonical proof gate 语义
  - 不自动把当前父 shell 或项目配置直接标记为 canonical consumption verified
  - 不要求 OpenAI Codex 宿主在仓库外额外提供新协议

## 用户故事与验收

### US-162-1 — Maintainer 需要一个正式 proof carrier 来启动受治理命令

作为 **maintainer**，我希望框架提供一个正式 carrier 命令，在启动子命令前自动计算并注入 canonical proof，这样我不必再手工复制 digest/path，也不会把 proof 生产过程留给人工操作。

**验收**：

1. **Given** 当前项目已 materialize `AGENTS.md` 且 target 为 Codex，**When** 执行 `python -m ai_sdlc adapter exec -- python -m ai_sdlc adapter status --json`，**Then** 子命令看到的 `adapter_canonical_consumption_result` 必须为 `verified`
2. **Given** 同一 carrier 启动 `python -m ai_sdlc run --dry-run`，**When** close gate 评估 program truth，**Then** canonical consumption 不再因为 proof 缺失而成为 blocker

### US-162-2 — Reviewer 需要 carrier 只负责传递 proof，不负责自证

作为 **reviewer**，我希望 carrier 只把当前 canonical proof 传给子命令，而不是直接改项目状态或跳过校验，这样 verified 仍然由既有 proof 消费链路得出。

**验收**：

1. **Given** 未通过 carrier 直接运行 `python -m ai_sdlc adapter status --json`，**When** 当前环境没有显式 proof，**Then** `adapter_canonical_consumption_result` 仍保持 `unverified`
2. **Given** carrier 启动的子命令不执行任何持久化动作，**When** 父进程随后重新运行普通 `adapter status`，**Then** 项目不会因为之前的 carrier 调用而自动变成 verified

### US-162-3 — Operator 需要 fail-closed 的 carrier 边界

作为 **operator**，我希望 carrier 在 canonical 文件缺失、target 不支持或命令为空时直接失败退出，这样不会把一个不完整的 proof 环境静默传下去。

**验收**：

1. **Given** canonical 文件不存在，**When** 执行 `adapter exec -- ...`，**Then** carrier 必须返回非零退出码且不执行子命令
2. **Given** `--` 后没有命令，**When** 执行 `adapter exec`，**Then** CLI 必须明确报错并退出

## 功能需求

- **FR-162-001**：系统必须在 `adapter` CLI 下提供一个显式 canonical proof carrier 子命令，命令形式为 `ai-sdlc adapter exec -- <command ...>`
- **FR-162-002**：carrier 在执行子命令前必须读取当前 target 的 canonical 文件，并基于文件真实内容计算 `sha256:` 摘要
- **FR-162-003**：carrier 必须向子命令注入 `AI_SDLC_ADAPTER_CANONICAL_SHA256=<当前 digest>` 与 `AI_SDLC_ADAPTER_CANONICAL_PATH=<当前 canonical path>`
- **FR-162-004**：当 canonical 文件不存在、target 为 generic、或 `--` 后没有命令时，carrier 必须 fail closed 并返回非零退出码
- **FR-162-005**：carrier 不得直接写入 `adapter_canonical_consumption_result=verified`；verified 仍必须由既有 `ide_adapter` proof 消费逻辑在子命令中判断
- **FR-162-006**：carrier 执行子命令时必须保留原有环境变量，并只覆盖 canonical proof 相关键
- **FR-162-007**：CLI 集成测试必须证明“普通运行仍是 unverified，carrier 运行可见 verified”，避免把 proof 语义错误折叠成常驻配置

## 成功标准

- **SC-162-001**：新增聚焦单测覆盖命令为空、canonical 文件缺失、generic target、proof payload 注入四类分支，并全部通过
- **SC-162-002**：新增 CLI 集成测试覆盖 `adapter exec -- python -m ai_sdlc adapter status --json` 绿灯路径，并证明普通路径仍保持 `unverified`
- **SC-162-003**：在当前仓库使用 carrier 运行 `python -m ai_sdlc adapter status --json` 时，可观测到 `adapter_canonical_consumption_result=verified`
