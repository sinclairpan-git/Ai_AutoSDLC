# 功能规格：YAML quoted-scalar comment-policy 精确识别

**功能编号**：`209-yaml-quoted-scalar-comment-policy`
**父项**：`196-ai-sdlc-lean-code-self-reduction-governance` / GAP-14 / T57
**基线**：`main@85bdedaca6a34563ccc2b8626a7e0adb188f1d4e`
**创建日期**：2026-07-17
**状态**：formal ready；Round 5 同一身份双对抗 PASS，formal PR/Codex/checks/merge 未完成

## 1. 问题与目标

`collect_removed_comment_findings()` 当前只对 unified diff 行执行 `_is_comment_line()`。当 `.yaml` / `.yml`
中的 single-quoted 或 double-quoted 多行标量续行以 `#139...` 开头时，该内容被误判为已删除注释，
`verify constraints` 因而产生假 BLOCKER。

基线只读复现对 single/double quoted scalar 均得到 1 个 finding；PyYAML scanner 同时证明对应 token
真实跨越第 1～3 行。本项只消除这一个误报，并确保真实注释检测不变。

## 2. 范围

### 2.1 范围内

- 在 `src/ai_sdlc/core/comment_policy.py` 内让 removed/added diff 行具备 YAML old/new 路径、行号和语法上下文。
- 复用现有 PyYAML scanner 的 `ScalarToken`，只识别 style 为 `'` 或 `"` 的跨行标量内容。
- 对旧侧删除行和新侧新增行对称处理，避免 quoted 内容被算作“替代注释”。
- 用 `tests/unit/test_comment_policy.py` 固定 RED/GREEN、token/path/hunk 和真实 Git diff 行为；用
  `tests/integration/test_cli_verify_constraints.py` 固定 CLI exit/text。

### 2.2 明确非目标

- 不全局关闭 YAML comment detection，也不豁免所有以 `#` 开头的 YAML 行。
- 不豁免 plain、literal (`|`) 或 folded (`>`) scalar；本项边界仅为 quoted scalar。
- 不编写完整 YAML diff parser，不扩大 diff context，不新增 parser/strategy/factory 公共抽象。
- 不修改 `verify_constraints.py`、adapter、resume reconstruction、telemetry、CLI、artifact/schema 或规则文案。
- 不作为减重成果计入 RC-08，也不夹带 WP-03～WP-07 的结构减重。

## 3. 用户故事与验收场景

### US-209-01 合法 quoted 内容不阻断（P0）

作为框架维护者，我希望删除或修改 quoted multiline scalar 中以 `#` 开头的内容时不产生注释删除
BLOCKER，从而让合法治理文档/YAML 变更通过真实约束检查。

1. **Given** `.yaml` / `.yml` 的旧侧 single/double quoted scalar 跨行内容，**When** 删除以 `#` 开头的
   续行，**Then** 不产生 removed-comment finding。
2. **Given** 新侧 quoted scalar 新增以 `#` 开头的续行，**When** 同一 hunk 还删除真实注释，**Then**
   新增内容不得抵消真实注释 finding。

### US-209-02 真实注释保护不退化（P0）

作为框架使用者，我希望修复误报后，Python、Markdown 和 YAML 的真实注释删除仍按原合同阻断。

1. **Given** YAML 真实 `# comment`，**When** 删除且无同 hunk 替代注释，**Then** blocker 文本和退出语义不变。
2. **Given** 非 YAML 文件出现相同 quoted 文本形态，**When** 删除 `#` 行，**Then** 仍按既有规则报告。
3. **Given** literal/folded/plain 或无法确认语法的 YAML 行，**When** 删除 `#` 行，**Then** 保守报告。

### US-209-03 失败时保持 fail-closed（P1）

1. **Given** old 侧 HEAD blob 缺失、YAML 扫描失败或行号不可信，**When** 删除 `#` 行，**Then**
   不应用豁免并继续报告。
2. **Given** added YAML 侧工作树内容缺失、扫描失败或行号不可信，**When** 新增 `#` 行，**Then**
   该行不得作为 replacement；非 YAML added comment 继续沿用既有配对行为。
3. **Given** 同一文件多 hunk，**When** old/new 行号分别推进，**Then** 每个行号只按对应侧源码判断。

## 4. 功能需求

- **FR-209-01**：现有 `--unified=0` 必须保留；不得用全文件 diff context 换取语法状态。
- **FR-209-02**：必须解析 `---` / `+++` 的独立 old/new path 与 hunk old/new 起始行；context 同时推进两侧，removed 只推进 old，added 只推进 new。
- **FR-209-03**：路径解析必须覆盖 rename、create/delete `/dev/null`、Git C-quoted 的空格/非 ASCII 路径和 traversal；无法安全解码或 containment 失败时仍保留 fail-closed finding，不得因 path 为空丢失。
- **FR-209-04**：只对 old/new 各自后缀（大小写不敏感）为 `.yaml` / `.yml` 的路径读取 `HEAD:<old_path>` / 工作树 `<new_path>`；工作树读取前必须逐组件 `lstat`，拒绝 symlink、Windows reparse/junction、特殊文件和 root 外解析结果；每侧每路径最多读取/扫描一次。
- **FR-209-05**：只有 PyYAML `ScalarToken.style` 为 `'` 或 `"`，且目标行严格晚于 token 起始行并不晚于结束行时，才可能是 quoted 内容。结束行从当前 token 的 `end_mark.column` 后扫描：忽略后续所有 quoted token 的列区间后，任一处于行首或前一字符为空白的 `#` 都是真实 YAML comment，整行不得豁免。
- **FR-209-06**：removed 与 added 行必须使用各自版本的 token span；可确认的 quoted added 内容不得增加 `added_comments`。
- **FR-209-07**：old YAML 侧缺失/解码失败/scanner 异常/非法行号时继续把候选 removed 行报告；new 侧 path/source/语法/行号任一不可信时，候选 added 行不得作为 replacement。只有确认是非 YAML 的两侧才保持既有判断。
- **FR-209-08**：hunk parser 必须覆盖省略 count、`-0,0/+0,0`、section suffix 和 `\ No newline at end of file`；非法 header 必须清空 old/new 位置，不能复用上一 hunk 状态。
- **FR-209-09**：真实 comment 的同 hunk 配对、finding 顺序、展示路径和 blocker 文本必须保持不变。
- **FR-209-10**：公共调用保持兼容；若纯函数增加上下文参数，该参数必须可选且不新增公共类型或跨模块抽象。
- **FR-209-11**：实现不得写文件、修改 Git 状态或访问网络；`verify constraints` 继续是只读检查。
- **FR-209-12**：formal 与 implementation 必须使用不同分支/PR；implementation 从 formal merge 后的新 `main` 创建。

## 5. 边界矩阵

| 路径/语法 | removed `#` | added `#` 可作 replacement | 预期 |
|---|---:|---:|---|
| `.yaml/.yml` single quoted continuation | 忽略 | 否 | 无假 finding；closing/flow tokens 后真实 comment 仍报告 |
| `.yaml/.yml` double quoted continuation | 忽略 | 否 | 同上，覆盖 escape/end column/后续 quoted token |
| YAML 真实 comment | 报告 | 是 | 既有行为不变 |
| YAML plain/literal/folded scalar | 报告 | 是 | 保守边界，不扩权 |
| malformed/不可读 YAML old 侧 | 报告 | 不适用 | removed fail-closed |
| malformed/不可读 YAML new 侧 | 不适用 | 否 | 不得掩盖真实 removed comment |
| new path 为 symlink/junction/特殊文件/越界 | 不适用 | 否 | 不跟随、不读取、不得作 replacement |
| Python/Markdown/其他后缀 | 报告 | 是 | 路径隔离 |

## 6. NC 与兼容影响

- **NC-01 基线**：上述 revision；`comment_policy.py=256` 行，`test_comment_policy.py=134` 行，`test_cli_verify_constraints.py=1799` 行（两测试合计 1933）；single/double 复现均为 1 finding。
- **NC-02 影响面**：产品只允许 `comment_policy.py`；测试只允许 `test_comment_policy.py` 与 `test_cli_verify_constraints.py`。受影响契约为 CC-02（blocker/exit）、CC-03（文本/顺序）、CC-05（只读副作用）、CC-07（Git/PyYAML 跨平台）。
- **NC-03 预算**：手写产品净新增最多 130 行，两个测试文件合计净新增最多 200 行；新增产品/测试文件均为 0；新增公共抽象为 0；新增 private helper 最多 5 个，单函数不超过 50 行。
- **NC-04 验证**：先提交至少一个 single/double quoted RED；GREEN 后运行 comment-policy focused、受影响 verify constraints、全量、Ruff、跨平台 CI 和 fresh-main。
- **NC-05 回退**：revert WI209 implementation commit/PR；无 schema、artifact 或数据迁移。回退后原假 blocker 恢复，真实注释保护不受损。
- **NC-06 隔离**：本项是验证可靠性缺陷修复，不计 Reduction Contract 收益，不混入结构重写。

## 7. 停止条件

出现任一情况即停止实现并回到 formal：需要全局 YAML 豁免、需要修改 PyYAML 依赖版本、需要完整 diff
重写器、无法对 added/removed 两侧对称判定、真实注释合同改变、预算超限或跨平台行为不一致。

## 8. 成功标准

- **SC-209-01**：矩阵中 quoted 两类不再误报，其余类别保持 finding/blocker。
- **SC-209-02**：quoted 或不可确认的 YAML added 内容不能抵消真实 removed comment；closing/flow suffix comment 保留；mixed-extension rename/quoted path、no-follow containment 和标准 hunk 边界准确。
- **SC-209-03**：产品/测试改动满足 NC-03，Ruff normalized 预算同样通过，无新公共抽象。
- **SC-209-04**：unit + real CLI exit/text、full/constraints/validate/truth/manifest/diff-check 全绿；真实 comment blocker 文本零变化。
- **SC-209-05**：两位对抗 reviewer 对同一 formal 哈希和同一 final implementation 身份均 PASS。
- **SC-209-06**：PR current-head Codex clean、required checks 全绿、合并后 fresh detached main 复验通过，才关闭 GAP-14/T57。
