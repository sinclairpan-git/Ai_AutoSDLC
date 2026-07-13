# 实施计划：AI-SDLC 精简代码治理与框架自身减重计划

**编号**：`196-ai-sdlc-lean-code-self-reduction-governance`  
**日期**：2026-07-12  
**规格**：`specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md`  
**计划性质**：治理总项路线图；本分支不执行产品代码减重。

## 1. 总体方案

采用“兼容契约先行、观测先行、低风险先行、双跑切换、延迟删除”的渐进式方案。Work Item 196 只冻结原则、基线、工作包和门禁；每个实现工作包必须在独立 work item、独立分支和独立 PR 中完成。

不采用以下方案：

- **单分支重写**：变更面过大，无法将行为差异定位到一个责任边界。
- **仅增加 LOC 限制**：会误伤必要的安全、兼容和测试代码，也无法处理结构复制。
- **先拆巨型文件再补保护**：文件移动不能证明行为等价，且会扩大 merge/review 噪音。

## 2. 技术背景

- **语言/运行时**：Python 3.11+。
- **主要依赖**：Typer、Pydantic、PyYAML、Jinja2、Rich。
- **测试**：pytest、现有集成/flow/unit 测试、后续 Characterization/Differential Tests。
- **质量工具**：Ruff、mypy、AI-SDLC constraints、git diff checks；复杂度/重复工具必须先通过依赖评估再引入。
- **目标平台**：macOS、Linux、Windows 离线发布链。
- **核心约束**：公共 CLI、artifact、状态迁移、授权边界和发布行为保持兼容。

## 3. 宪章检查

| 宪章门禁 | 计划响应 |
|---|---|
| MVP 优先、范围严控 | 196 只做治理文档；实现拆为独立工作包 |
| 关键路径可验证 | 先建立 Characterization、Golden Master 和差异测试 |
| 声明范围、验证和回退 | 每个工作包强制独立范围、验证矩阵和 revert/fallback |
| 状态落盘 | 基线、差异、豁免、review 和 handoff 均落盘 |
| 产品与开发框架隔离 | 196 不写产品代码；子工作项分别管理 |
| 单文件/单函数约束 | 先作为现状基线和增量门禁，不一次性阻断历史债务 |

## 4. 文档结构

```text
specs/196-ai-sdlc-lean-code-self-reduction-governance/
├── spec.md                 # 原则、兼容契约、需求、成功标准
├── plan.md                 # 分阶段路线图、风险和验证策略
├── tasks.md                # 本治理分支任务与后续工作包定义
└── task-execution-log.md   # 命令、证据、决策和评审归档
```

本工作项不创建第二套 canonical design/plan 文档，避免与 `specs/<wi>/` 四件套形成双轨真值。

## 5. 治理架构

```text
Work Item 196 治理总项
  ├─ Lean 原则与兼容冻结
  ├─ 当前基线与度量定义
  ├─ 风险/豁免/停止/回退规则
  └─ Reduction Work Package 路线图
       ├─ WP-01 兼容观测与 Golden Master
       ├─ WP-02 Lean Gate report-only
       ├─ WP-03 低风险 helper 与测试去重
       ├─ WP-04 Loop Store 收敛
       ├─ WP-05 静态 baseline 配置化
       ├─ WP-06 ProgramService 分域
       ├─ WP-07 Program Stage Engine 双跑收敛
       └─ WP-08 增量门禁强化与旧实现删除
```

每个 WP 只表示路线图中的工作包名称，不占用正式 work item 编号。正式编号在用户批准启动时分配。

## 6. 基线与度量模型

### 6.1 基线维度

1. **规模**：产品 LOC、测试 LOC、文件数、新增/删除/复用 LOC。
2. **结构**：超限文件、超长函数、顶层类/方法数、模块 fan-out/fan-in。
3. **复杂度**：圈复杂度或等价分支复杂度、嵌套深度。
4. **重复**：完全重复 helper、结构重复 DTO/CLI/test、重复规则常量。
5. **行为**：CLI surface、退出码、artifact、状态迁移、副作用边界。
6. **效率**：CLI 启动、`verify constraints`、关键 workflow 运行耗时。
7. **质量**：全量测试、Ruff、mypy、release smoke 和独立 review。

### 6.2 评价规则

- LOC 下降但复杂度、耦合或行为差异上升：FAIL。
- LOC 不明显下降但职责边界、依赖方向和可测试性显著改善：允许作为结构准备批次，但必须说明后续删除路径。
- 测试 LOC 下降只在场景数、断言强度和平台覆盖不下降时成立。
- 生成/fixture/vendored 代码单独统计，不参与手写产品代码预算。

## 7. 工作包路线图

### WP-01：兼容观测与 Golden Master（L1/L2）

**目标**：建立后续减重的行为保险，不改现有实现。

**产物**：

- CLI surface manifest。
- 代表性命令 fixture 和退出码基线。
- artifact 规范化器与 Golden Snapshot。
- 状态迁移、dry-run 无写入和幂等重放测试。
- 代表性兄弟项目 smoke 清单。

**进入条件**：196 通过用户评审。  
**完成条件**：同一 revision 重复采样零非语义漂移。  
**回退**：删除新增观测代码和 fixture，不影响产品路径。

### WP-02：Lean Code Gate report-only（L1/L2）

**目标**：机器化采集规模、复杂度、重复和增量预算，但不阻断历史债务。

**产物**：结构化报告、changed-code 分类、waiver schema、CLI/verify 接入的报告模式。

**完成条件**：在本仓库稳定报告且无误把生成资产计入手写产品代码。  
**回退**：关闭 gate profile 或移除 report-only 接入。

### WP-03：低风险 helper 与测试去重（L1）

**目标**：处理完全相同 dedupe、路径、YAML/JSON helper，并参数化纯镜像测试。

**限制**：不改变公共模型、异常文本和 artifact。  
**验证**：定向测试、Golden diff、全量测试。  
**回退**：按重复族逐 commit revert。

### WP-04：Loop Store 收敛（L2）

**目标**：复用 loop ID、路径、pointer、JSON/Pydantic 读取等稳定公共逻辑。

**限制**：不同 loop 的错误语义和 close 规则保持独立。  
**验证**：旧/新 store 差异测试、恢复和损坏输入测试。  
**回退**：保留原 store adapter，按 loop 逐个切回。

### WP-05：静态 baseline 配置化（L2）

**目标**：将大段静态 Python baseline 迁移为版本化 YAML/JSON，并由 Pydantic 校验。

**限制**：字段、顺序语义、默认值和 provider 行为不变。  
**验证**：序列化快照、provider/frontend targeted tests。  
**回退**：loader 回到原 Python builder。

### WP-06：ProgramService 分域（L3）

**目标**：将 manifest、solution、delivery、browser、governance、archive 职责拆为内聚服务；`ProgramService` 暂保留 facade。

**限制**：不删除 facade，不改变调用方。  
**验证**：每移动一个领域运行 Golden diff、全量测试和依赖图比较。  
**回退**：facade 重新指向原方法。

### WP-07：Program Stage Engine 双跑收敛（L3）

**目标**：将经过证明的镜像治理阶段收敛为数据驱动 stage spec、通用 executor 和 renderer。

**限制**：所有现有 33 个 `program` 命令继续存在；新引擎先 shadow，不负责用户结果。

**切换顺序**：

1. dry-run 结果双跑。
2. artifact 生成双跑。
3. 单个低风险命令切换。
4. 每次只切换一个 stage family。
5. 稳定发布后才允许删除旧实现。

### WP-08：增量门禁强化与旧实现删除（L2/L3）

**目标**：将 report-only 升级为 changed-code warning/blocking，并删除已稳定替换的旧实现。

**进入条件**：相关新实现至少经过一个稳定发布周期，无未批准差异和兄弟项目回归。  
**回退**：恢复兼容 adapter，并将门禁降级为 warning。

## 8. Lean Gate 渐进策略

### 阶段 A：Report Only

- 记录全仓债务和 changed-code 指标。
- 永不因历史债务阻断。
- 校准生成代码、fixture 和 vendored 排除规则。

### 阶段 B：Changed-Code Warning

- 新文件、显著增长文件、新增长函数和新抽象触发 warning。
- 每条 warning 必须处理或形成有期限 waiver。

### 阶段 C：Changed-Code Blocking

- 无豁免的新超限文件、超长函数、重复实现和超预算扩展触发 BLOCKER。
- 旧文件只有被显著修改的区域进入硬门禁。
- 阈值必须按语言和任务类型配置，不使用全语言统一绝对 LOC。

## 9. 验证矩阵

| 验证层 | L1 | L2 | L3 |
|---|---:|---:|---:|
| 定向单元测试 | 必须 | 必须 | 必须 |
| CLI/Artifact Golden diff | 按影响 | 必须 | 必须 |
| 旧/新差异双跑 | 可选 | 按影响 | 必须 |
| 全量 pytest | 必须 | 必须 | 必须 |
| Ruff / constraints / diff-check | 必须 | 必须 | 必须 |
| mypy 基线不得恶化 | 必须 | 必须 | 必须 |
| 本地独立只读 review | 建议 | 必须 | 必须 |
| 跨平台 release smoke | 按影响 | 按影响 | 必须 |
| 兄弟项目 smoke | 按影响 | 按影响 | 必须 |

## 10. 停止条件

任一条件成立时，当前工作包必须停止，不得用修测试掩盖差异：

1. 公共命令、参数、默认值或退出码发生未批准变化。
2. artifact schema、路径或状态迁移出现未批准差异。
3. `--dry-run` 出现新写入或授权边界弱化。
4. 测试场景、平台覆盖或关键断言下降。
5. 新实现无法通过开关或 facade 快速回退。
6. 全量测试、release smoke 或代表性兄弟项目 smoke 失败。
7. 为减少 LOC 引入更高耦合、更深继承或更难理解的泛型抽象。
8. 工作包需要同时修改两个以上独立领域且无法拆分。

## 11. 提交与 PR 策略

- 196 只提交治理文档、manifest/project-state/handoff 等合法治理状态。
- 每个后续 WP 使用独立正式 work item、独立分支和独立 PR。
- 减重 PR 不混入新功能、发布 bump 或无关格式化。
- 每批提交包含代码、测试、before/after 指标和 execution log，能够单独 revert。
- L3 PR 必须经过本地专职只读 reviewer；进入 mainline 时继续遵守仓库 PR review、checks、heartbeat 和 merge 协议。

## 12. 当前工作项完成标准

1. `spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md` 内容完整且互相一致。
2. 无占位符、无开放设计决策。
3. `program-manifest.yaml` 和 project state 正确登记 Work Item 196。
4. 全量测试基线、constraints、文档检查和 diff-check 有新鲜证据。
5. 用户审核本工作项后，再决定是否启动 WP-01。

## 13. 开放问题

无。本治理总项不预先冻结具体语言阈值；阈值校准属于 WP-02，必须根据 report-only 数据决定。
