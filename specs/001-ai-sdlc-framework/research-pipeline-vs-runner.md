# Pipeline 规则 vs Runner 行为对照（Task 6.6）

**工作项**：001-ai-sdlc-framework  
**目的**：将 [`src/ai_sdlc/rules/pipeline.md`](../../src/ai_sdlc/rules/pipeline.md) 中与 **阶段跳跃 / 已有产物** 相关的条文，与 [`src/ai_sdlc/core/runner.py`](../../src/ai_sdlc/core/runner.py) 及门禁实现 **逐条对齐**，标出缺口与建议（**仅文档**，本文件不修改产品代码）。

**关联**：`tasks.md` Task **6.6**；计划侧 todo `gap-pipeline-rule-vs-code`。

---

## 对照表

| 规则条文（摘要） | 代码 / 模块行为 | 缺口 | 建议 |
|------------------|-----------------|------|------|
| **阶段顺序** `init → … → close`，禁止跳阶段（`pipeline.md` §阶段执行顺序） | `SDLCRunner` 使用固定 `PIPELINE_STAGES` 顺序；`run()` 从 `checkpoint.current_stage` 对应下标起向后迭代各阶段 | 无（顺序由枚举锁死） | 保持；断点恢复须保证 `checkpoint.yml` 与真实进度一致 |
| **唯一例外**：`specs/NNN/` 若已有某阶段产物，**可从下一阶段开始**，但须先验证该产物满足门禁（`pipeline.md` §阶段执行顺序 末段） | Runner **不扫描** `specs/` 推断「应处于哪一阶段」；起点仅为 `Checkpoint.current_stage`。各阶段仍执行对应 `Gate` | **规则描述的「从下一阶段开始」在 Runner 内不自动发生**；须通过 `init` / `recover` / 人工或上层工具更新 `current_stage`，再 `run` | **reconcile（文档）**：在 `pipeline.md` 或用户指南中写明——「已有产物」例外体现为 **checkpoint 阶段字段与门禁通过**，而非 Runner 自动发现文件后跳步；若未来要自动化，应经 ADR 在 `stage`/`recover` 路径实现 |
| **配置优先于硬编码**（`pipeline.md` §强制行为 4） | `Runner._build_context` 从 `Checkpoint` 与磁盘路径拼装 `ctx`；阶段注册在 `Runner._build_registry` | 部分 policy 仍可能来自默认 `pipeline.yml`（由其他模块读取，非本表逐行核对范围） | 扩展对照时单列 `pipeline.yml` 消费点 |
| **PRD 引导须完成** 后方可进入 Stage 0（`pipeline.md` §强制行为 8） | `SDLCRunner.run` **不调用** `prd-guidance`；由 Agent / 操作者在外部保证 | Agent 侧流程与 Runner 解耦 | **仅文档**：保持「引导在流水线入口前」的约定；CLI `init`/`run` 文档已述职责边界则足够 |
| **`dry_run`**（`Runner.run(..., dry_run=True)`） | `dry_run` 为真时不写入 `completed_stages`、不 `save_checkpoint` 于通过路径（见 `runner.py` `_apply_result`） | 与「归档先于继续」联用时，dry-run 不产真实归档 | 文档已隐含；培训材料注明 dry-run 不替代批次归档 |

---

## 结论

- **当前真值**：阶段推进以 **`checkpoint.yml` + 门禁结果** 为准；**非**「仅因 `spec.md` 存在即自动等价于完成 design」。
- **与 Task 6.6 AC 关系**：本表满足「表格列：规则条文、代码行为、缺口、建议」；审阅通过后 Task **6.6** 可视为关闭（以 `tasks.md` 收口登记为准）。

---

## 变更登记

- **2026-03-25**：首版，服务 Task **6.6** 收口。
