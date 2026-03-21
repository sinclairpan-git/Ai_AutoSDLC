# 技术研究：AI-SDLC 框架 P0

**编号**：`001-ai-sdlc-framework` | **日期**：2026-03-21 | **状态**：已冻结

---

## 1. CLI 框架选型

**决策**：Typer（AD-001 已冻结）

| 方案 | 优势 | 劣势 |
|------|------|------|
| **Typer** ✅ | 类型注解自动推导参数；Rich 集成；社区活跃 | 较 Click 多一层抽象 |
| Click | 成熟稳定、文档丰富 | 参数定义繁琐、无类型推导 |
| argparse | 标准库无依赖 | API 冗长、无自动补全 |

Typer 底层仍是 Click，兼容 Click 生态（中间件、测试工具），且与项目强制类型注解规范一致。

---

## 2. 状态机实现

**决策**：基于字典映射的轻量状态机，不引入第三方状态机库。

理由：
- 状态转换数量有限（12 个，见 PRD §9.3），不需要复杂的状态机框架
- transitions 库功能过重，且引入额外依赖
- 自实现可完全控制持久化逻辑（每次转换写 YAML）

实现方案：
```python
class StateMachine:
    TRANSITIONS: dict[tuple[str, str], Callable] = {
        ("created", "intake_classified"): _on_classify,
        ("intake_classified", "governance_frozen"): _on_freeze,
        ...
    }

    def transition(self, from_state: str, to_state: str) -> None:
        guard = self.TRANSITIONS.get((from_state, to_state))
        if guard is None:
            raise InvalidTransitionError(...)
        guard(self)
        self._persist(to_state)
```

---

## 3. YAML 读写策略

**决策**：PyYAML + Pydantic v2 双层（AD-002、AD-020 已冻结）

- 读取层：`yaml.safe_load()` → Python dict
- 校验层：Pydantic BaseModel 做 schema 验证 + 默认值填充
- 写出层：model → dict → `yaml.dump()`
- 封装为统一 `YamlStore` 类，所有文件读写通过此类，不散落 `yaml.load()` 调用

缺失 key 处理：Pydantic model 定义 `Optional` + 默认值，缺失字段静默填充，不抛异常。

---

## 4. Git 操作封装

**决策**：subprocess 调用 git CLI（AD-005 已冻结）

封装 `GitClient` 类：
- `status()` → 返回工作区状态
- `checkout(branch)` → 切换分支（前置检查 uncommitted changes）
- `create_branch(name)` → 创建分支
- `commit(message)` → add + commit
- `merge(source, target, message)` → merge --no-ff
- `diff_stat(base, head)` → 返回变更文件列表

所有 git 命令失败时抛出 `GitError`，包含 stderr 输出。

---

## 5. 模板引擎

**决策**：Jinja2

用途：
- 生成 spec、plan、tasks 等文档骨架
- 生成 project-state.yaml 等初始配置
- 生成状态面板输出（Rich 格式化 + Jinja2 模板）

模板存放位置：`src/ai_sdlc/templates/`，随产品分发。

---

## 6. 项目打包与分发

**决策**：src layout + pyproject.toml + uv（AD-003、AD-004 已冻结）

```toml
[project]
name = "ai-sdlc"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "typer>=0.9",
    "pyyaml>=6.0",
    "pydantic>=2.0",
    "jinja2>=3.1",
    "rich>=13.0",
]

[project.scripts]
ai-sdlc = "ai_sdlc.cli.main:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

P0 交付方式：拷贝源码到项目。未来可发布到 PyPI。

---

## 7. 测试策略

| 层 | 框架 | 覆盖范围 |
|----|------|---------|
| 单元测试 | pytest + pytest-mock | 每个模块的核心函数 |
| 流程测试 | pytest + tmp_path | 端到端流程（init → classify → execute） |
| 集成测试 | pytest + 真实 git repo | CLI 命令 + git 操作 |

关键测试基础设施：
- `tmp_path` fixture 创建临时项目目录
- `git_repo` fixture 初始化临时 git 仓库
- `mock_project` fixture 创建包含 `.ai-sdlc/` 的模拟项目

覆盖率目标：核心模块 ≥ 80%，gate 模块 = 100%。

---

## 8. Work Intake Router 分类策略

**决策**：关键词匹配 + 规则引擎（P0 不使用 LLM）

P0 采用确定性规则分类：
1. 扫描输入文本的关键词
2. 按优先级匹配规则：production_issue > change_request > maintenance_task > new_requirement
3. 无匹配或多匹配 → uncertain

关键词表：
- `production_issue`：生产、线上、P0、故障、告警、宕机、502、OOM、回滚、紧急、incident
- `change_request`：需求变了、范围变更、推翻、不做了、改为
- `maintenance_task`：升级、迁移、清理、优化、重构、依赖更新
- `new_requirement`：新功能、新需求、从零、MVP、PRD（兜底）

置信度计算：匹配关键词数 / 总关键词数 → high (≥ 0.6) / medium (0.3-0.6) / low (< 0.3)

---

## 9. 开放问题

| 问题 | 状态 | 备注 |
|------|------|------|
| P1 的 LLM 集成分类是否需要预留接口？ | 已决策 | 是，WorkIntakeRouter 定义 Protocol，P0 实现关键词版，P1 可替换为 LLM 版 |
| 产品内置规则文件是否与开发框架规则共用？ | 已决策 | 否，产品的规则文件在 `src/ai_sdlc/rules/` 下独立维护，内容可参考但不引用开发框架 |
| Rich 面板在非终端环境（如 CI）如何降级？ | 待定 | P0 先实现 Rich 输出，CI 环境检测到 `NO_COLOR` 或非 TTY 时输出纯文本 |
