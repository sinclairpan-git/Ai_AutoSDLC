# 快速启动手册：AI-SDLC 框架 P0

**编号**：`001-ai-sdlc-framework` | **日期**：2026-03-21

---

## 1. 开发环境搭建

### 前置条件

- Python >= 3.11
- Git >= 2.30
- uv（Python 包管理器）

### 安装 uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 初始化项目

```bash
cd /path/to/Ai_AutoSDLC

# 创建虚拟环境并安装依赖
uv sync

# 验证安装
uv run ai-sdlc --help
```

### 开发依赖

```bash
# 安装开发依赖（测试、lint、类型检查）
uv sync --dev
```

---

## 2. 运行测试

```bash
# 全量测试
uv run pytest

# 仅单元测试
uv run pytest tests/unit/

# 仅流程测试
uv run pytest tests/flow/

# 仅集成测试
uv run pytest tests/integration/

# 带覆盖率
uv run pytest --cov=ai_sdlc --cov-report=term-missing

# 特定测试文件
uv run pytest tests/unit/test_bootstrap_router.py -v
```

---

## 3. 代码质量检查

```bash
# Lint
uv run ruff check src/ tests/

# 自动修复
uv run ruff check --fix src/ tests/

# 格式化
uv run ruff format src/ tests/

# 类型检查
uv run mypy src/ai_sdlc/
```

---

## 4. 使用 CLI

```bash
# 在目标项目中初始化 AI-SDLC
cd /path/to/your-project
ai-sdlc init

# 查看当前状态
ai-sdlc status

# 从中断恢复
ai-sdlc recover

# 重建索引
ai-sdlc index

# 手动运行门禁
ai-sdlc gate init
ai-sdlc gate refine
```

---

## 5. 项目目录约定

```
Ai_AutoSDLC/                  ← 工作区根目录
├── autopilot.md              ← 开发框架约束（不动）
├── rules/                    ← 开发框架约束（不动）
├── templates/                ← 开发框架约束（不动）
├── presets/                  ← 开发框架约束（不动）
├── config/                   ← 开发框架约束（不动）
├── .ai-sdlc/                 ← 开发流水线状态（自动管理）
├── specs/                    ← 设计产物（自动管理）
├── src/ai_sdlc/              ← 产品源代码（开发产物）
├── tests/                    ← 测试代码（开发产物）
└── pyproject.toml            ← 项目配置（开发产物）
```

---

## 6. 回退手册

### 回退某个 Phase

```bash
# 查看 commit 历史
git log --oneline

# 回退最近一个 commit
git revert HEAD

# 回退特定 commit
git revert <commit-hash>
```

### 重置流水线状态

```bash
# 删除流水线状态（保留产品代码）
rm -rf .ai-sdlc/state/checkpoint.yml

# 完全重置（删除所有 .ai-sdlc 状态）
rm -rf .ai-sdlc/
```

### 分支回退

```bash
# 放弃当前 feature 分支
git checkout main
git branch -D feature/001-ai-sdlc-framework

# 放弃当前 design 分支
git checkout main
git branch -D design/001-ai-sdlc-framework
```

---

## 7. 常见问题

| 问题 | 解决方案 |
|------|---------|
| `ai-sdlc: command not found` | 确认已运行 `uv sync` 且在 venv 中 |
| `ModuleNotFoundError: ai_sdlc` | 确认使用 `uv run` 前缀或激活了 venv |
| `git not found` | 安装 Git：`brew install git` (macOS) |
| `Python < 3.11` | 直接按下方“Python < 3.11 时直接复制”执行 |
| YAML 解析错误 | 检查文件编码（必须 UTF-8）和缩进（空格，非 Tab） |

### Python < 3.11 时直接复制

**Windows（PowerShell）**

```powershell
winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
winget install -e --id Python.Launcher --accept-package-agreements --accept-source-agreements
py -3.11 --version
```

**macOS（Terminal）**

如果你的 Mac 还没装 Homebrew，先执行：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

然后执行：

```bash
if [ -x /opt/homebrew/bin/brew ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -x /usr/local/bin/brew ]; then
  eval "$(/usr/local/bin/brew shellenv)"
fi
brew install python@3.11
export PATH="$(brew --prefix python@3.11)/libexec/bin:$PATH"
python3 --version
```

**Linux（Ubuntu / Debian）**

```bash
sudo apt-get update
sudo apt-get install -y build-essential procps curl file git
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
brew install python@3.11
export PATH="$(brew --prefix python@3.11)/libexec/bin:$PATH"
python3 --version
```

如果你用的是其他 Linux 发行版，把系统依赖安装命令替换成你自己的包管理器；装好以后，再回到第 1 节继续执行 `uv sync`。
