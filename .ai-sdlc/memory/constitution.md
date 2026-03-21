# AI-SDLC 项目宪章

**生成来源**：PRD v1.1 自动推导  
**生成时间**：2026-03-21  
**状态**：已冻结（仅允许在 Stage 0 创建，后续不可修改）

---

## 核心原则

### MUST-1：MVP 优先，范围严控

只实现 PRD 中 P0 标记的能力。任何超出 P0 范围的功能、优化或"顺手加上"的改进，必须被拒绝或记录为 P1 backlog。宁可功能少但闭环完整，不可功能多但没跑通。

### MUST-2：关键路径必须可验证

每个模块、每个 gate、每条业务规则（BR-xxx）必须有对应的自动化测试。不允许存在"看起来对但没测过"的代码路径。声称完成前必须有新鲜的测试证据。

### MUST-3：每次改动声明范围、验证与回退

任何代码变更必须：
1. 明确声明影响的文件和模块范围
2. 有对应的测试验证
3. 可通过 git revert 独立回退

禁止"大泥球"提交（一次 commit 混合多个不相关变更）。

### MUST-4：状态落盘，上下文外化

所有运行时状态必须持久化到 `.ai-sdlc/` 目录下的文件中。不允许依赖聊天窗口、内存变量或其他临时状态。中断后必须能从文件系统完整恢复。

### MUST-5：产品代码与开发框架严格隔离

产品源代码（Python 包 + 规则文件模板）放在专用的产品代码目录中。开发过程使用的框架约束文件（工作区根目录的 `autopilot.md`、`rules/`、`templates/` 等）不与产品代码混用。两套文件各自独立演进。

---

## 技术硬约束

### 语言与运行时

- Python >= 3.11，不兼容 3.10 及以下
- 类型注解覆盖所有函数签名（参数 + 返回值），mypy strict 模式通过
- 使用 Ruff 做 lint + format，行宽 88
- 使用 pytest 做测试，pytest-cov 做覆盖率

### 代码规范

- 命名：模块 snake_case，类 UpperCamelCase，函数/变量 snake_case，常量 UPPER_SNAKE_CASE
- 引号：双引号（Ruff 默认）
- Docstring：Google style
- 单文件不超过 400 行，单函数不超过 50 行
- 禁止裸 except，至少 except Exception
- 使用 logging 模块，禁止 print 调试
- 使用 Enum 代替魔法字符串
- 配置通过 YAML 文件 + pydantic 模型管理，禁止硬编码

### 依赖管理

- 使用 uv 做依赖管理（pyproject.toml）
- 运行时依赖尽量少：PyYAML、Click/Typer、Pydantic、Jinja2
- 不引入数据库、Web 框架、ORM 等非必要依赖

### 项目结构

```
src/ai_sdlc/           产品源代码（Python 包）
  __init__.py
  cli/                  CLI 命令入口
  core/                 核心引擎（状态机、Runner）
  routers/              路由器（Bootstrap、Work Intake）
  studios/              Studios（PRD、Incident、Change、Maintenance）
  gates/                质量门禁
  context/              Context Control Plane
  branch/               分支管理
  generators/           模板与索引生成器
  models/               数据模型（Pydantic）
  utils/                工具函数
src/ai_sdlc/rules/     产品内置规则文件（Markdown）
src/ai_sdlc/templates/ 产品内置模板文件
tests/                  测试
  unit/
  flow/
  integration/
```

### Git 纪律

- 每个逻辑变更一个 commit
- commit message 使用 conventional commits 格式
- 分支策略遵循 docs/dev 双分支模型

---

## 交付门禁

任何产出物（代码、配置、文档）在声称完成前，必须回答以下 5 个问题：

1. **这个变更的 PRD 依据是什么？** — 必须指向 PRD 的具体章节或 BR/AC 编号
2. **影响范围是什么？** — 列出所有受影响的文件和模块
3. **如何验证？** — 必须有可运行的测试或可执行的验证步骤
4. **如果出错如何回退？** — 必须可通过 git revert 独立回退
5. **是否引入了范围蔓延？** — 如果做了 PRD 未要求的事情，必须标注并说明理由

---

## 治理规则

1. 宪章一旦冻结不可修改
2. 所有设计产物必须在 docs 分支上完成
3. 所有代码实现必须在 dev 分支上完成
4. 门禁检查不可绕过，失败时先自修复再阻断
5. AI 自主决策累计超过 15 次必须暂停审查
6. 单个文件超过 400 行必须建议拆分
