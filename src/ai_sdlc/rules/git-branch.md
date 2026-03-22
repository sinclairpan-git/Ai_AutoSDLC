# Git 分支策略

> 本规则在整个流水线生命周期内生效，定义分支创建、切换、合并的强制行为。

## 核心原则

```
设计产物和开发代码分属不同分支。
切换分支前必须 commit。
切换分支后必须校验基线。
```

## 分支结构

每个 Feature 使用两条分支，分阶段递进：

```
main (或 develop)
  │
  ├─ design/NNN-short-name      ← Stage 1-4 的设计产物（spec、plan、tasks 等）
  │    │
  │    └─ feature/NNN-short-name ← Stage 5 EXECUTE 的代码实现（从 design 分支创建）
  │         │
  │         └─ 开发完成后合并回 main
  │
  └─ (下一个 Feature 重复上述结构)
```

| 分支 | 创建时机 | 内容 | 合并时机 |
|------|---------|------|---------|
| `design/NNN-short-name` | Stage 1 REFINE 开始前 | spec.md, plan.md, research.md, data-model.md, contracts/, tasks.md, quickstart.md | Stage 4 VERIFY 通过后合并到 main |
| `feature/NNN-short-name` | Stage 5 EXECUTE 开始前 | 全部代码、测试、execution-log、development-summary | Stage 6 CLOSE 完成后合并到 main |

## 分支生命周期

### Stage 0 INIT（在 main 上执行）

```
宪章、技术栈、预决策 → 在 main 分支上 commit
原因：这些是项目级配置，不属于某个 Feature
```

### Stage 1 REFINE 开始前：创建设计分支

```
1. 确认 main 分支上无未 commit 的变更
2. git checkout -b design/NNN-short-name
3. 开始 Stage 1 工作
```

### Stage 1-4（在 design 分支上执行）

```
每个阶段完成后在 design 分支上 commit：
  Stage 1: git commit -m "docs(NNN): add spec.md"
  Stage 2: git commit -m "docs(NNN): add plan, research, data-model, contracts"
  Stage 3: git commit -m "docs(NNN): add tasks.md"
  Stage 4: git commit -m "docs(NNN): verify consistency - all passed"
```

### Stage 4 → Stage 5 过渡：合并设计、创建开发分支

```
Stage 4 VERIFY 通过后：
  1. 确认 design 分支上所有变更已 commit
  2. 合并设计分支到 main：
     git checkout main
     git merge design/NNN-short-name --no-ff -m "docs(NNN): merge design artifacts"
  3. 从 main 创建开发分支：
     git checkout -b feature/NNN-short-name
  4. 开始 Stage 5 EXECUTE

为什么从 main 而不是从 design 分支创建 feature 分支？
  → 保证 feature 分支的基线包含最新的 main 代码
  → 如果有其他 feature 已合并，feature 分支也能包含
```

### Stage 5-6（在 feature 分支上执行）

```
每个批次在 feature 分支上 commit
Stage 6 完成后，feature 分支可合并到 main
```

### Stage 6 完成后：合并开发分支

```
1. 确认 feature 分支上所有变更已 commit
2. 合并到 main：
   git checkout main
   git merge feature/NNN-short-name --no-ff -m "feat(NNN): complete implementation"
3. 删除已合并的分支（可选）：
   git branch -d design/NNN-short-name
   git branch -d feature/NNN-short-name
```

## 铁律一：切换前必须 commit

**任何分支切换之前，必须保证当前分支的工作区干净。**

```
切换前检查协议：
  1. git status → 检查是否有未 staged 或未 commit 的变更
  2. 如果有变更：
     a. 变更属于当前阶段的正常产出 → git add + git commit
     b. 变更是临时/未完成的工作 → git stash（恢复后 git stash pop）
     c. 变更是误操作 → git checkout -- [文件] 撤销
  3. 再次 git status → 确认工作区干净
  4. 执行 git checkout [目标分支]

违反后果：
  切换分支丢失未 commit 的工作 → 不可恢复
  → 流水线必须阻断并提示用户
```

## 铁律二：切换后必须校验基线

**切换到新分支后，必须验证基线完整性才能开始工作。**

```
切换后基线校验协议：

场景 A：切换到 design 分支开始工作
  1. 确认宪章存在且可读：.ai-sdlc/memory/constitution.md
  2. 确认技术栈存在：.ai-sdlc/profiles/tech-stack.yml
  3. 确认 PRD 可访问
  4. 如果是从断点恢复 → 确认 checkpoint.yml 中的 feature.spec_dir 目录存在

场景 B：从 design 分支切换到 feature 分支（Stage 4 → 5 过渡）
  1. 确认 design 分支已合并到 main（git log --oneline main | grep NNN）
  2. 确认设计产物在 feature 分支上可访问：
     □ specs/NNN/spec.md 存在
     □ specs/NNN/plan.md 存在
     □ specs/NNN/tasks.md 存在
     □ specs/NNN/data-model.md 存在（如适用）
  3. 确认 tasks.md 内容与 design 分支上的一致（无丢失）
  4. 确认测试框架可运行（如已有测试配置）

场景 C：断点恢复后切换分支
  1. 读取 checkpoint.yml → 确定目标分支
  2. git checkout [目标分支]
  3. 执行场景 A 或 B 的校验
  4. 校验通过 → 继续恢复流程

基线校验失败处理：
  任何一项缺失 → 阻断流水线
  输出缺失清单
  提示可能原因（分支未合并、文件被删、checkout 错误）
```

## 增量 Feature（已初始化项目的新需求）

```
当项目已初始化（宪章存在），处理新 Feature 时：
  1. 确认在 main 分支上
  2. git pull（如有远程仓库）
  3. 创建 design/NNN-short-name（同上流程）
  4. 后续流程同标准流程
```

## 并行 Feature

```
当同时开发多个 Feature 时：
  main
   ├─ design/001-xxx → feature/001-xxx
   └─ design/002-yyy → feature/002-yyy

规则：
  - 每个 Feature 有独立的分支对
  - design 分支合并到 main 时需检查冲突
  - feature 分支合并到 main 时需做全量回归
  - 如果两个 Feature 修改同一个文件 → 后合并的需要解决冲突
```

## 与 checkpoint.yml 的集成

checkpoint 中记录当前分支信息：

```yaml
feature:
  id: "001-employee-signup"
  spec_dir: "specs/001-employee-signup-core"
  design_branch: "design/001-employee-signup-core"
  feature_branch: "feature/001-employee-signup-core"
  current_branch: "design/001-employee-signup-core"  # 当前活跃分支
```

恢复时，根据 `current_branch` 自动切换到正确的分支。

## Commit Message 规范（分支相关）

```
design 分支上的 commit：
  docs(NNN): add spec.md
  docs(NNN): add plan, research, data-model
  docs(NNN): add tasks.md
  docs(NNN): verify consistency passed

feature 分支上的 commit：
  feat(NNN): scaffold project structure
  feat(NNN): implement [US 描述]
  test(NNN): add [测试范围] coverage
  docs(NNN): add development summary

合并 commit：
  docs(NNN): merge design artifacts
  feat(NNN): complete implementation
```

## 异常处理

```
异常 1：切换分支时发现 main 上有未拉取的远程变更
  → 先 git pull，解决冲突后再创建分支

异常 2：design 分支合并到 main 时有冲突
  → 在 design 分支上 rebase main，解决冲突，再合并

异常 3：feature 分支合并到 main 时有冲突
  → 在 feature 分支上 rebase main，解决冲突，运行全量回归，再合并

异常 4：切换分支后发现产物缺失
  → 阻断流水线，输出缺失清单
  → 检查是否合并遗漏，或分支创建基点错误

异常 5：误在错误分支上工作（如在 main 上写了 spec）
  → git stash → git checkout 正确分支 → git stash pop → git add + commit
```
