# 场景路由与分支流程

> 在默认「PRD → 全流水线」之外，部分输入应走**短路径**或**范围变更路径**，避免用完整 SDLC 误伤效率，也避免在 EXECUTE 中静默改 spec。

## 何时读取本文件

- 用户入口消息看起来像**线上故障 / 热修复**，而非新产品需求
- 用户在 **EXECUTE 或 CLOSE 前后**声明**需求重大变更**
- 维护者做**场景自测**或审计流水线完整性

---

## 1. 标准路径（默认）

```
用户输入 → PRD 引导（prd-guidance.md）→ Stage 0–6
```

适用于：新功能、较大改造、从 0 到 1、增量 Feature（简化引导但仍产出 PRD）。

**存量代码库**（已有业务实现）：在 PRD 引导之后、进入 Stage 1 之前，须满足 `rules/brownfield-corpus.md`——先产出 `memory/engineering-corpus.md` 作为结构化工程索引。不得用通读全仓库代替（与热修复 §2 的精简流程要求不同）。

---

## 2. 生产环境 / 线上问题（热修复短路径）

### 2.1 触发特征（满足其一即可倾向本路径）

- 显式词：**生产**、**线上**、**P0/P1**、**故障**、**告警**、**宕机**、**502**、**OOM**、**数据不一致**、**回滚**
- 结构：现象 + 环境 +（可选）日志/栈 + 影响面，**无**产品愿景/用户故事扩展

### 2.2 与全流水线的关系

| 项 | 说明 |
|----|------|
| PRD 引导 | **可不按完整探索/结构化模式**；改为「事件单」：现象、影响、复现、验收（修复后怎样算好） |
| Stage 0–4 | **通常跳过**（不新建 `specs/NNN` 全量设计），除非团队要求每次热修也补文档 |
| 必须遵守 | `debugging.md`、`tdd.md`（代码变更时）、`code-review.md`、`verification.md`、`git-branch.md`（分支与 commit 纪律） |

### 2.3 推荐执行序列

```
1. 事件 intake：确认环境、版本、是否可复现、是否需先回滚
2. 根因：按 debugging.md 四阶段（禁止跳过根因）
3. 分支：从 main（或项目约定的 release 分支）创建 hotfix/NNN-xxx
4. 修复：最小变更 + TDD（先失败测试再改代码）
5. 验证：verification.md + Smoke（针对影响面）
6. 提交：review 通过后 commit；merge 策略按团队规范
7. 可选 backlog：若仓库已有 AI-SDLC 产物，建工单「补 spec / tasks 与实现一致」
```

### 2.4 禁止

- 以「先写一堆 spec 再修一行配置」为由延误 P0
- 无复现/无验收标准就声称修复完成（违反 verification.md）

---

## 3. 开发中需求大变更（范围变更路径）

### 3.1 触发特征

- 用户明确说：**需求变了**、**范围扩大/缩小**、**推翻之前方案**、**不做 US-x 改做 US-y**
- 或 EXECUTE 中发现：当前 tasks **无法**在不变更 spec/plan 的前提下完成（架构级矛盾）

### 3.2 阶段越早，成本越低

| 当前阶段 | 动作 |
|----------|------|
| PRD / REFINE / DESIGN / DECOMPOSE / VERIFY | 更新 PRD 与对应产物，**重新跑门禁**；必要时提高 `stage_overrides` 为 confirm |
| EXECUTE | **禁止**在 feature 分支上直接改 spec/plan 了事（违反 pipeline.md）；必须走下方「上升」流程 |

### 3.3 EXECUTE 中的上升流程（强制）

```
1. 在完成当前最小原子操作后 HALT（与 autopilot「暂停」协议一致）
2. 在 task-execution-log.md 记录：SCOPE_CHANGE、原因、影响范围、用户确认引语
3. 切回设计层：
   a. 若 design 分支仍存在：checkout design/NNN，更新 spec.md / plan.md / tasks.md（或增量文件）
   b. 若 design 已合并：从 main 拉分支 docs/hotfix-scope-NNN 或在原 design 命名规范下新建分支按 git-branch.md 处理
4. 重新跑 Stage 4 VERIFY（至少对变更部分做一致性校验）
5. 按 git-branch.md：commit → 合并策略 → checkout feature/NNN（或新建）→ **基线校验**
6. 从「首个受影响任务」继续 EXECUTE；已完成的批次保持归档，作废任务标记为 CANCELLED 并说明
```

### 3.4 与设计缺陷的关系

若在 EXECUTE 发现的是 **实现错误** → 用 debugging.md，**不**上升改 spec。  
若确认是 **设计/需求错误** → 走 3.3。

---

## 4. 路由决策表（入口）

| 用户意图（摘要） | 首选路径 |
|------------------|----------|
| 一句话想法 / MVP | PRD 探索模式 → 标准流水线 |
| 完整 PRD | PRD 审核模式 → 标准流水线 |
| 已有项目 + 新功能 | 增量 PRD → 若无 `engineering-corpus.md` 则先补（brownfield-corpus.md）→ 路径 5（autopilot） |
| 线上故障 / 紧急修复 | 本文件 §2 热修复短路径 |
| 开发中需求大变 | 本文件 §3 范围变更 |
| 断点恢复 | checkpoint → 跳过 PRD（autopilot） |

---

## 5. 与其他规则的一致性

- `pipeline.md` 禁止在 EXECUTE 私自改 spec/plan：范围变更必须通过 §3「上升」。
- `prd-guidance.md` 的增量 Feature 与 §3 互补：增量是**新增能力**，§3 是**推翻或重大调整已有范围**。
- `git-branch.md`：任何换分支、合并、恢复均先 commit 再校验基线。
