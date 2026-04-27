# 功能规格：跨平台 Shell 偏好持久化与迁移基线

**功能编号**：`180-shell-preference-persistence-and-migration-baseline`  
**状态**：草案（待评审）  
**创建日期**：2026-04-27  
**输入**：Persist a project-level preferred shell across Windows/macOS/Linux, materialize the preference into adapter instructions, prompt upgraded legacy projects to choose a shell, surface the missing configuration in status/doctor, and provide a standalone command to reselect the shell after init.

> 口径：本 work item 负责把“项目首选 shell”升级为正式、可持久化、可迁移、可重配的项目级配置能力。它必须同时覆盖新项目初始化、老项目升级提示、adapter 文档落地、CLI 状态面展示和独立重选命令，避免 Windows/macOS/Linux 宿主环境下的 shell 猜测与错误命令回退。

## 问题定义

当前框架只在 adapter 文档中给出通用“终端约定”，但没有把宿主 shell 真值建模为结构化配置。结果是：

1. Windows + Codex 场景下，agent 经常先生成 POSIX 命令（如 `ls`、`grep`、`export`），失败后再回退到 PowerShell，造成时间和 token 浪费
2. 新项目初始化时无法显式确认“本项目默认 shell 是什么”
3. 已初始化项目升级到新版本后，没有单独命令可补录 shell 偏好
4. `status` / `doctor` 无法提示老项目当前缺失 shell 配置，也无法给出推荐值和下一步命令
5. adapter 物料（尤其 `AGENTS.md`）不能稳定把“应使用哪类命令语法”传达给 agent

这不是单纯文档优化问题，而是项目级宿主执行上下文缺失。缺失这个上下文会直接影响命令生成正确率、治理日志质量和 AI agent 的执行效率。

## 范围

### 覆盖

- 在 `.ai-sdlc/project/config/project-config.yaml` 中持久化项目级 shell 偏好
- 定义跨平台 shell 取值：`powershell`、`bash`、`zsh`、`cmd`、`auto`
- `init` 时允许用户选择 shell，并按宿主 OS 给出推荐值
- 为已初始化项目提供独立命令，允许后续重新选择 shell
- 让 `status` / `doctor` / 必要的启动提示对“未配置 shell”的老项目给出升级指引
- 让 adapter 模板物化 shell 偏好，明确约束 agent 应生成何种命令语法
- 为老项目定义无阻断迁移策略：缺失配置时先提示，不直接阻断运行

### 不覆盖

- 不在本 work item 中改变 host runtime、provider 安装器或 browser gate 的执行引擎
- 不在本 work item 中做 shell 命令自动转换器或多 shell fallback 执行器
- 不改变 adapter verified ingress / canonical consumption 的治理协议
- 不把 shell 偏好与 OS 强绑定；Windows 上仍允许显式选择 `bash`，macOS/Linux 仍允许显式选择 `powershell` 或 `cmd`

## 用户故事

### US-180-001：Windows 用户希望 agent 默认生成 PowerShell 命令

作为 Windows 用户，我希望项目初始化后明确记录首选 shell 为 `powershell`，并写入 `AGENTS.md`，以便 agent 不再先尝试 Unix 命令再回退。

### US-180-002：macOS/Linux 用户希望项目默认使用熟悉的 shell

作为 macOS 或 Linux 用户，我希望初始化时看到与宿主平台匹配的 shell 推荐值，并能选择 `zsh`、`bash` 或其他兼容选项，以便 agent 命令风格与团队实际终端一致。

### US-180-003：升级用户希望不重跑 init 也能补录 shell 偏好

作为已经初始化过项目的老用户，我希望升级新版本后可以执行单独的 shell 选择命令完成持久化，而不是被迫重新初始化项目。

### US-180-004：维护者希望从状态面看到迁移缺口

作为框架维护者，我希望 `status` 和 `doctor` 能明确告诉我当前项目是否缺少 shell 偏好配置、推荐值是什么、下一步应该执行哪个命令，以便我能快速完成迁移。

## 功能需求

| ID | 需求 |
|----|------|
| FR-180-001 | 系统必须在 `ProjectConfig` 中新增项目级 shell 偏好字段，并持久化到 `.ai-sdlc/project/config/project-config.yaml` |
| FR-180-002 | shell 偏好允许值必须至少包含 `powershell`、`bash`、`zsh`、`cmd`、`auto` |
| FR-180-003 | `init` 在交互式场景下必须允许用户选择 shell，并按宿主 OS 提供推荐值：Windows=`powershell`，macOS=`zsh`，Linux=`bash` |
| FR-180-004 | 系统必须提供独立重选命令，允许已初始化项目在不重新 `init` 的情况下更新 shell 偏好 |
| FR-180-005 | 独立重选命令更新 shell 偏好后，必须重新物化 adapter 文档，使 `AGENTS.md` / 其他 canonical adapter 文件同步反映最新配置 |
| FR-180-006 | Codex adapter 模板必须显式写出“当前项目 shell 是什么，以及 agent 应优先生成哪类命令语法” |
| FR-180-007 | 其他 adapter 模板若存在终端约定段落，也必须消费同一 shell 偏好配置，避免各 adapter 文案漂移 |
| FR-180-008 | 对缺少 shell 偏好的已初始化老项目，`status` 和 `doctor` 必须给出非阻断迁移提示、推荐值和下一步命令 |
| FR-180-009 | 对缺少 shell 偏好的已初始化老项目，系统不得把运行直接判为失败；默认行为应是提示迁移，而不是阻断 |
| FR-180-010 | shell 偏好读取优先级必须清晰：显式 CLI 参数（如未来提供）优先于已持久化项目配置；项目配置优先于宿主推断推荐值 |
| FR-180-011 | 当 shell 偏好为 `auto` 时，状态面必须明确表明这是兜底模式，而不是强约束命令语法 |
| FR-180-012 | 文档和测试必须覆盖 Windows、macOS、Linux 三类宿主推荐路径，以及老项目迁移和重选命令路径 |

## 成功标准

| ID | 标准 |
|----|------|
| SC-180-001 | 新项目在交互式初始化后，`project-config.yaml` 中存在 shell 偏好字段，且值与用户选择一致 |
| SC-180-002 | 已初始化老项目执行独立重选命令后，shell 偏好写入配置且 adapter 文档同步更新 |
| SC-180-003 | Codex adapter 物料明确包含 shell 类型和命令语法约束，不再只写通用“终端约定” |
| SC-180-004 | `status` / `doctor` 在老项目缺少 shell 偏好时输出推荐值和可复制的下一步命令 |
| SC-180-005 | Windows/macOS/Linux 的推荐值逻辑均有自动化测试，且不会把 shell 与 OS 硬绑定为唯一值 |
| SC-180-006 | 老项目缺少 shell 偏好时不会阻断 `run --dry-run`，但会提示迁移 |
| SC-180-007 | 重选命令的回归测试证明：更新 shell 后 adapter 文案跟随变化，且配置写入是幂等的 |

## 依赖和追踪

- 相关能力：`010` agent adapter activation contract、`121/122/159/162/163` adapter ingress / canonical consumption、`179` Windows/source-checkout/terminal 体验补齐
- 主要实现文件预计见 `plan.md` 和 `tasks.md`

---
related_doc:
  - "AGENTS.md"
frontend_evidence_class: "framework_capability"
---
