# 实施计划：AI-SDLC 原 PRD 跨域旧债补充合同

**编号**：`003-cross-cutting-authoring-and-extension-contracts` | **日期**：2026-03-28 | **规格**：specs/003-cross-cutting-authoring-and-extension-contracts/spec.md

## 概述

本计划承接 `003` 的原 PRD 跨域旧债：一句话想法生成 PRD 草案、Human Reviewer 决策点、Native / Plugin Backend delegation / fallback、可测量 NFR 与 release gates。实现策略应坚持“合同先行”：先补 authoring / reviewer / backend / release 的对象与决策真值，再把它们挂进现有 Studio、BackendRegistry、verify/close-check surface。

## 技术背景

**语言/版本**：Python 3.11+  
**主要依赖**：Typer、Pydantic v2、PyYAML、Rich、pytest  
**存储**：spec/work-item 目录下的 Markdown / YAML 决策记录  
**测试**：unit + integration，重点覆盖合同与 fallback 决策  
**目标平台**：macOS + Linux；同时要求非交互路径行为一致  
**约束**：不把 `004` 的 operator / telemetry / program 扩展混入本计划

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 只交付原 PRD 旧债，不吸收 post-PRD operator 扩展 |
| MUST-2 关键路径可验证 | authoring、reviewer、backend routing、release gates 都要有 contract tests |
| MUST-3 范围声明与回退 | 按 authoring / reviewer / backend / release gate 四块切分提交 |
| MUST-4 状态落盘 | reviewer decision、draft/final 状态、backend choice、release evidence 都落盘 |
| MUST-5 产品代码隔离 | 只修改产品代码和 `specs/003-*` 计划文档 |

## 项目结构

### 文档结构

```text
specs/003-cross-cutting-authoring-and-extension-contracts/
├── spec.md
├── plan.md          ← 本文件
└── tasks.md         ← 本次补齐
```

### 源码结构

```text
src/ai_sdlc/
├── studios/
│   ├── prd_studio.py             # existing readiness review
│   └── router.py                 # Studio routing entry
├── models/work.py                # PRD / reviewer related models
├── backends/native.py            # Backend protocol + registry
├── core/
│   ├── close_check.py            # existing close/read-only gate
│   └── verify_constraints.py     # verification truth surface
├── cli/verify_cmd.py             # verify CLI
└── tests/
    ├── unit/test_prd_studio.py
    ├── unit/test_backends.py
    ├── unit/test_close_check.py
    └── integration/test_cli_verify_constraints.py
```

## 阶段计划

### Phase 0：跨域旧债 contract 模型冻结

**目标**：先定义 draft PRD、review checkpoint、review decision、backend selection、release gate evidence 的单一真值。  
**产物**：`models/work.py` 或相邻模块中的新对象与状态枚举。  
**验证方式**：对应 unit tests。  
**回退方式**：模型批次单独提交。

### Phase 1：一句话想法 -> draft PRD authoring

**目标**：让系统能生成显式占位的 draft PRD，而不是只有 readiness review。  
**产物**：扩展 `prd_studio` 或新增 authoring 模块；draft/final 状态切分。  
**验证方式**：`test_prd_studio.py` + 生成器单测。  
**回退方式**：保持现有 readiness review 入口兼容。

### Phase 2：Human Reviewer checkpoint 与决策记录

**目标**：把 approve / revise / block 从口头流程变成正式对象与日志。  
**产物**：review decision artifact、状态读取 surface、close / recover 可见性。  
**验证方式**：review journal unit tests + close-check assertions。  
**回退方式**：先做只读决策记录，再接强制 gate。

### Phase 3：Backend capability declaration 与 fallback 决策

**目标**：让 Native / Plugin 的选择有统一 capability 合同，并区分可安全回退与必须阻断。  
**产物**：backend routing / policy 层与 registry 扩展。  
**验证方式**：`test_backends.py`。  
**回退方式**：保持 native default 可用。

### Phase 4：NFR / Release Gate 可测量化

**目标**：把 recoverability / portability / multi-IDE / stability 变成 release gate 证据面。  
**产物**：release gate 只读检查、verify/close-check 集成、证据输出结构。  
**验证方式**：`test_close_check.py` + `test_cli_verify_constraints.py`。  
**回退方式**：先给 WARN，再提升到 BLOCK 条件。

## 工作流计划

### 工作流 A：PRD draft authoring

**范围**：一句话输入 -> draft PRD -> readiness-review 可消费元数据  
**影响范围**：`prd_studio`、可能的新 authoring 模块、`models/work.py`  
**验证方式**：生成结果必须显式标记未决假设  
**回退方式**：保留当前 path-based readiness review

### 工作流 B：Reviewer decision truth

**范围**：PRD freeze / docs baseline freeze / close 前 reviewer 决策  
**影响范围**：review artifact、status/recover/close-check surface  
**验证方式**：approve / revise / block 三种结果都可读  
**回退方式**：先落盘，再逐步接 gate

### 工作流 C：Backend / Release gating

**范围**：capability declaration -> backend selection -> fallback/block -> release gate evidence  
**影响范围**：`backends/native.py`、新 routing/policy 层、`close_check.py` / `verify_constraints.py`  
**验证方式**：unit + integration 证明决策原因和 blocker 可追溯  
**回退方式**：native default 永远保留

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| draft PRD 显式标记未决项 | `tests/unit/test_prd_studio.py` | close-check / downstream metadata consumer |
| reviewer decision 可追溯 | reviewer unit tests | status/recover surface 夹具 |
| backend 失败时区分 fallback / block | `tests/unit/test_backends.py` | verify / close-check 决策报告 |
| release gate 输出 PASS/WARN/BLOCK | `tests/unit/test_close_check.py` | `tests/integration/test_cli_verify_constraints.py` |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| draft PRD 入口挂在 PRD Studio 还是单独 authoring service | 待锁定 | Phase 1 |
| reviewer decision artifact 归档到 work-item 目录还是 spec 目录 | 待锁定 | Phase 2 |
| plugin backend 的 capability schema 放在 registry 还是独立 models 模块 | 待锁定 | Phase 3 |

## 实施顺序建议

1. 先冻结模型和状态，再做 authoring / reviewer / backend / release 行为。
2. Human Reviewer 决策日志先落盘，再接入阻断型 gate。
3. Backend fallback 与 release gate 最后接 CLI / close-check，避免过早扰动现有主链。
