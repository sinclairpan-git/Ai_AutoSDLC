"""Brownfield task adoption for existing project progress sources."""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any


class AdoptionSourceKind(str, Enum):
    """Supported external progress source kinds."""

    JSON = "json"
    MARKDOWN = "markdown"
    GIT_COMMIT = "git_commit"
    GIT_BRANCH = "git_branch"
    GIT_DIFF = "git_diff"
    TEST = "test"
    PROJECT_STRUCTURE = "project_structure"


class AdoptionTaskStatus(str, Enum):
    """Normalized task statuses used by the adoption map."""

    TODO = "todo"
    DOING = "doing"
    DONE = "done"
    BLOCKED = "blocked"
    NEEDS_REVIEW = "needs-review"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class AdoptionBudget:
    """Bounded scan budget for brownfield adoption."""

    max_candidate_files: int = 80
    max_file_bytes: int = 65_536
    max_recent_commits: int = 20
    max_visited_dirs: int = 400
    max_visited_files: int = 2_000


@dataclass(frozen=True, slots=True)
class AdoptionSource:
    """One external source considered for adoption."""

    kind: AdoptionSourceKind
    label: str
    rel_path: str
    confidence: float
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AdoptedTask:
    """One task inferred from an external source."""

    external_id: str
    ai_sdlc_task_id: str
    title: str
    description: str
    status: AdoptionTaskStatus
    source: str
    confidence: float
    path_refs: tuple[str, ...] = ()
    updated_at: str = ""
    owner: str = ""
    blockers: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AdoptionContinuePoint:
    """Recommended task to resume from."""

    task_id: str
    title: str
    confidence: float
    reason: str
    needs_review: bool


@dataclass(frozen=True, slots=True)
class AdoptionMap:
    """Bridge between external task state and AI-SDLC continuation."""

    generated_at: str
    root: str
    sources: tuple[AdoptionSource, ...]
    tasks: tuple[AdoptedTask, ...]
    continue_point: AdoptionContinuePoint
    checkpoint_candidate: dict[str, Any]
    warnings: tuple[str, ...] = ()


IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".ai-sdlc",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "target",
    ".next",
    ".nuxt",
    "coverage",
    "__pycache__",
}
TASK_FILE_TOKENS = (
    "task",
    "todo",
    "issue",
    "progress",
    "roadmap",
    "backlog",
    "plan",
    "readme",
    "任务",
    "需求",
    "计划",
    "待办",
    "进度",
    "问题",
    "路线图",
)
TASK_SUFFIXES = {".json", ".md", ".markdown"}
ID_KEYS = ("id", "task_id", "key", "number", "issue", "uuid")
TITLE_KEYS = ("title", "name", "summary", "task", "text")
DESCRIPTION_KEYS = ("description", "desc", "details", "body", "notes")
STATUS_KEYS = ("status", "state", "phase")
PROGRESS_KEYS = ("progress", "percent", "completion")
CHILDREN_KEYS = ("children", "subtasks", "items", "tasks")
DEPENDENCY_KEYS = ("depends", "dependencies", "blocked_by")
FILE_KEYS = ("files", "paths", "path", "file")
OWNER_KEYS = ("owner", "assignee", "developer")
BLOCKER_KEYS = ("blockers", "blocked_reason", "risk")
UPDATED_KEYS = (
    "updated",
    "updated_at",
    "modified",
    "modified_at",
    "last_modified",
    "lastModified",
    "created_at",
    "created",
)


def build_adoption_map(
    root: Path,
    *,
    target: Path | None = None,
    prefer_text: str = "",
    budget: AdoptionBudget | None = None,
) -> AdoptionMap:
    """Build an adoption map from existing progress sources without overwriting them."""
    resolved_root = root.resolve()
    scan_target = (target or root).resolve()
    active_budget = budget or AdoptionBudget()
    warnings: list[str] = []
    sources = list(
        discover_adoption_sources(
            resolved_root,
            target=scan_target,
            budget=active_budget,
        )
    )
    tasks: list[AdoptedTask] = []
    for source in sources:
        if source.kind is AdoptionSourceKind.JSON:
            tasks.extend(_tasks_from_json_source(resolved_root / source.rel_path, source))
        elif source.kind is AdoptionSourceKind.MARKDOWN:
            tasks.extend(_tasks_from_markdown_source(resolved_root / source.rel_path, source))
        elif source.kind is AdoptionSourceKind.GIT_COMMIT:
            tasks.extend(_tasks_from_git_source(source))
        elif source.kind in {
            AdoptionSourceKind.GIT_BRANCH,
            AdoptionSourceKind.GIT_DIFF,
            AdoptionSourceKind.TEST,
        }:
            tasks.extend(_tasks_from_evidence_source(source))

    if not _is_git_repo(resolved_root):
        warnings.append("未检测到 Git 历史，已改用任务文件和项目结构继续接入，无需处理。")
    if not tasks:
        tasks.append(_fallback_task_from_structure(resolved_root, scan_target))
        warnings.append("未识别到结构化任务源，已生成临时继续点。")

    continue_point = recommend_continue_point(tuple(tasks), prefer_text=prefer_text)
    return AdoptionMap(
        generated_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        root=resolved_root.as_posix(),
        sources=tuple(sources),
        tasks=tuple(tasks),
        continue_point=continue_point,
        checkpoint_candidate=_build_checkpoint_candidate(continue_point, tuple(tasks)),
        warnings=tuple(warnings),
    )


def discover_adoption_sources(
    root: Path,
    *,
    target: Path,
    budget: AdoptionBudget,
) -> tuple[AdoptionSource, ...]:
    """Discover bounded task/progress sources from files, project structure, and git."""
    sources: list[AdoptionSource] = []
    for path in _iter_candidate_files(root, target=target, budget=budget):
        rel = _rel_path(path, root)
        suffix = path.suffix.lower()
        if suffix == ".json":
            sources.append(
                AdoptionSource(
                    AdoptionSourceKind.JSON,
                    path.name,
                    rel,
                    0.75,
                    ("json candidate",),
                )
            )
        elif suffix in {".md", ".markdown"}:
            sources.append(
                AdoptionSource(
                    AdoptionSourceKind.MARKDOWN,
                    path.name,
                    rel,
                    0.55,
                    ("markdown candidate",),
                )
            )

    sources.extend(_discover_git_sources(root, budget=budget))
    sources.extend(_discover_test_sources(root))
    if not sources:
        sources.append(
            AdoptionSource(
                AdoptionSourceKind.PROJECT_STRUCTURE,
                "project structure",
                ".",
                0.2,
                ("fallback source",),
            )
        )
    return tuple(sources)


def recommend_continue_point(
    tasks: tuple[AdoptedTask, ...],
    *,
    prefer_text: str = "",
) -> AdoptionContinuePoint:
    """Recommend the task to resume, using status, confidence, and user correction text."""
    if not tasks:
        return AdoptionContinuePoint(
            "adopted-temp-001",
            "接入已有项目",
            0.2,
            "未识别到任务源，先生成临时继续点",
            True,
        )

    preferred = prefer_text.strip().lower()

    def score(task: AdoptedTask) -> tuple[float, str]:
        value = task.confidence
        reason = f"置信度={task.confidence:.2f}"
        if task.status is AdoptionTaskStatus.DOING:
            value += 0.25
            reason += ", 状态=进行中"
        elif task.status is AdoptionTaskStatus.TODO:
            value += 0.12
            reason += ", 状态=待办"
        elif task.status is AdoptionTaskStatus.BLOCKED:
            value -= 0.12
            reason += ", 状态=阻塞"
        elif task.status is AdoptionTaskStatus.DONE:
            value -= 0.35
            reason += ", 状态=已完成"
        if preferred:
            haystack = f"{task.title} {task.description} {' '.join(task.path_refs)}".lower()
            if preferred in haystack:
                value += 0.35
                reason += ", 匹配用户纠偏"
        if task.path_refs:
            value += 0.05
            reason += ", 文件证据"
        if task.updated_at:
            value += 0.03
            reason += ", 更新时间证据"
        if task.dependencies:
            value -= 0.08
            reason += ", 依赖待确认"
        if task.blockers:
            value -= 0.18
            reason += ", 存在阻塞"
        return value, reason

    ranked = sorted(tasks, key=lambda task: score(task)[0], reverse=True)
    selected = ranked[0]
    selected_score, reason = score(selected)
    confidence = max(0.0, min(selected_score, 1.0))
    return AdoptionContinuePoint(
        selected.external_id,
        selected.title,
        confidence,
        reason,
        confidence < 0.75,
    )


def write_adoption_artifacts(
    root: Path,
    adoption_map: AdoptionMap,
    *,
    output_dir: Path | None = None,
) -> tuple[Path, Path, Path]:
    """Write bridge artifacts under .ai-sdlc without modifying original sources."""
    target_dir = output_dir or root / ".ai-sdlc" / "adoption"
    target_dir.mkdir(parents=True, exist_ok=True)
    map_path = target_dir / "adoption-map.json"
    bridge_path = target_dir / "bridge.md"
    checkpoint_path = target_dir / "checkpoint-candidate.json"
    map_path.write_text(
        json.dumps(_adoption_map_to_dict(adoption_map), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    bridge_path.write_text(_render_bridge_markdown(adoption_map), encoding="utf-8")
    checkpoint_path.write_text(
        json.dumps(adoption_map.checkpoint_candidate, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return map_path, bridge_path, checkpoint_path


def _iter_candidate_files(
    root: Path,
    *,
    target: Path,
    budget: AdoptionBudget,
) -> tuple[Path, ...]:
    files: list[Path] = []
    if not target.exists():
        return ()
    visited_dirs = 0
    visited_files = 0
    for dirpath, dirnames, filenames in os.walk(target):
        visited_dirs += 1
        if visited_dirs > budget.max_visited_dirs:
            dirnames[:] = []
            break
        dirnames[:] = [name for name in dirnames if name not in IGNORED_DIRS]
        for filename in filenames:
            if len(files) >= budget.max_candidate_files:
                break
            visited_files += 1
            if visited_files > budget.max_visited_files:
                break
            path = Path(dirpath) / filename
            if not path.is_file() or path.suffix.lower() not in TASK_SUFFIXES:
                continue
            try:
                if path.stat().st_size > budget.max_file_bytes:
                    continue
            except OSError:
                continue
            if _is_task_candidate_file(path):
                files.append(path)
        if len(files) >= budget.max_candidate_files or visited_files > budget.max_visited_files:
            break
    return tuple(files)


def _is_task_candidate_file(path: Path) -> bool:
    lower_name = path.name.lower()
    if any(token in lower_name for token in TASK_FILE_TOKENS):
        return True
    try:
        sample = path.read_text(encoding="utf-8", errors="replace")[:4096]
    except OSError:
        return False
    if path.suffix.lower() == ".json":
        lowered = sample.lower()
        return any(
            key in lowered
            for key in TITLE_KEYS + STATUS_KEYS + PROGRESS_KEYS + CHILDREN_KEYS
        )
    return any(
        marker in sample for marker in ("- [ ]", "- [x]", "- [X]", "TODO:", "待办", "任务", "进度")
    )


def _discover_git_sources(root: Path, *, budget: AdoptionBudget) -> tuple[AdoptionSource, ...]:
    if not _is_git_repo(root):
        return ()
    sources: list[AdoptionSource] = []
    branch = _git_output(root, ["git", "branch", "--show-current"])
    if branch:
        sources.append(
            AdoptionSource(
                AdoptionSourceKind.GIT_BRANCH,
                branch,
                ".git",
                0.3,
                ("current branch",),
            )
        )
    status = _git_output(root, ["git", "status", "--short"])
    if status:
        changed_paths = tuple(line[3:].strip() for line in status.splitlines() if len(line) > 3)
        sources.append(
            AdoptionSource(
                AdoptionSourceKind.GIT_DIFF,
                "working tree diff",
                ".git",
                0.45,
                changed_paths[:20],
            )
        )
    log = _git_output(
        root,
        ["git", "log", f"--max-count={budget.max_recent_commits}", "--pretty=%h %s"],
    )
    for line in log.splitlines():
        normalized = line.strip()
        if not normalized:
            continue
        sources.append(
            AdoptionSource(
                AdoptionSourceKind.GIT_COMMIT,
                normalized,
                ".git",
                0.35,
                ("recent commit",),
            )
        )
    return tuple(sources)


def _discover_test_sources(root: Path) -> tuple[AdoptionSource, ...]:
    evidence: list[str] = []
    for candidate in (root / "tests", root / "test", root / "src" / "test"):
        if candidate.is_dir():
            evidence.append(_rel_path(candidate, root))
    if not evidence:
        return ()
    return (
        AdoptionSource(
            AdoptionSourceKind.TEST,
            "test structure",
            evidence[0],
            0.3,
            tuple(evidence),
        ),
    )


def _tasks_from_json_source(path: Path, source: AdoptionSource) -> tuple[AdoptedTask, ...]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return ()
    raw_tasks = list(_extract_task_objects(payload))
    tasks: list[AdoptedTask] = []
    for index, raw in enumerate(raw_tasks, start=1):
        task = _task_from_mapping(raw, source=source, index=index)
        if task is not None:
            tasks.append(task)
    return tuple(tasks)


def _tasks_from_markdown_source(path: Path, source: AdoptionSource) -> tuple[AdoptedTask, ...]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return ()
    tasks: list[AdoptedTask] = []
    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("- [ ]") or stripped.startswith("* [ ]"):
            title = stripped[5:].strip()
            status = AdoptionTaskStatus.TODO
        elif (
            stripped.startswith("- [x]")
            or stripped.startswith("* [x]")
            or stripped.startswith("- [X]")
            or stripped.startswith("* [X]")
        ):
            title = stripped[5:].strip()
            status = AdoptionTaskStatus.DONE
        elif stripped.startswith("TODO:"):
            title = stripped.removeprefix("TODO:").strip()
            status = AdoptionTaskStatus.TODO
        elif stripped.startswith(("待办：", "待办:")):
            title = stripped.split(":", maxsplit=1)[-1].strip()
            if title == stripped:
                title = stripped.split("：", maxsplit=1)[-1].strip()
            status = AdoptionTaskStatus.TODO
        elif stripped.startswith(("任务：", "任务:")):
            title = stripped.split(":", maxsplit=1)[-1].strip()
            if title == stripped:
                title = stripped.split("：", maxsplit=1)[-1].strip()
            status = AdoptionTaskStatus.UNKNOWN
        elif stripped.startswith(("进行中：", "进行中:")):
            title = stripped.split(":", maxsplit=1)[-1].strip()
            if title == stripped:
                title = stripped.split("：", maxsplit=1)[-1].strip()
            status = AdoptionTaskStatus.DOING
        else:
            continue
        if not title:
            continue
        tasks.append(
            AdoptedTask(
                external_id=f"{source.rel_path}:{index}",
                ai_sdlc_task_id=f"ADOPT-{index:03d}",
                title=title,
                description="",
                status=status,
                source=source.rel_path,
                confidence=0.58,
            )
        )
    return tuple(tasks)


def _tasks_from_git_source(source: AdoptionSource) -> tuple[AdoptedTask, ...]:
    title = source.label
    lowered = title.lower()
    if not any(token in lowered for token in ("fix", "feat", "task", "todo", "wip")):
        return ()
    return (
        AdoptedTask(
            external_id=source.label.split(maxsplit=1)[0],
            ai_sdlc_task_id="ADOPT-GIT-001",
            title=title,
            description="recent commit evidence",
            status=AdoptionTaskStatus.UNKNOWN,
            source="git log",
            confidence=0.35,
        ),
    )


def _tasks_from_evidence_source(source: AdoptionSource) -> tuple[AdoptedTask, ...]:
    if source.kind is AdoptionSourceKind.GIT_BRANCH:
        title = f"继续当前分支：{source.label}"
        status = AdoptionTaskStatus.DOING
    elif source.kind is AdoptionSourceKind.GIT_DIFF:
        title = "继续当前未提交改动"
        status = AdoptionTaskStatus.DOING
    else:
        title = "保留并复用现有测试结构"
        status = AdoptionTaskStatus.UNKNOWN
    return (
        AdoptedTask(
            external_id=source.label,
            ai_sdlc_task_id=f"ADOPT-{source.kind.value.upper().replace('_', '-')}",
            title=title,
            description="evidence source",
            status=status,
            source=source.rel_path,
            confidence=source.confidence,
            path_refs=source.evidence,
        ),
    )


def _extract_task_objects(payload: Any) -> tuple[dict[str, Any], ...]:
    found: list[dict[str, Any]] = []
    if isinstance(payload, list):
        for item in payload:
            found.extend(_extract_task_objects(item))
    elif isinstance(payload, dict):
        if _looks_like_task(payload):
            found.append(payload)
        for key in CHILDREN_KEYS:
            child = payload.get(key)
            if isinstance(child, (list, dict)):
                found.extend(_extract_task_objects(child))
        for key, value in payload.items():
            if key in CHILDREN_KEYS:
                continue
            if isinstance(value, list) and any(isinstance(item, dict) for item in value):
                found.extend(_extract_task_objects(value))
    return tuple(found)


def _looks_like_task(value: dict[str, Any]) -> bool:
    keys = {str(key).lower() for key in value}
    return bool(keys & set(TITLE_KEYS)) and bool(
        keys & (set(ID_KEYS) | set(STATUS_KEYS) | set(PROGRESS_KEYS) | set(CHILDREN_KEYS))
    )


def _task_from_mapping(
    raw: dict[str, Any],
    *,
    source: AdoptionSource,
    index: int,
) -> AdoptedTask | None:
    title = _first_text(raw, TITLE_KEYS)
    if not title:
        return None
    external_id = _first_text(raw, ID_KEYS) or f"{source.rel_path}:{index}"
    status = _normalize_status(_first_text(raw, STATUS_KEYS), _first_present(raw, PROGRESS_KEYS))
    path_refs = _string_tuple_from_value(_first_present(raw, FILE_KEYS))
    blockers = _string_tuple_from_value(_first_present(raw, BLOCKER_KEYS))
    dependencies = _string_tuple_from_value(_first_present(raw, DEPENDENCY_KEYS))
    updated_at = _first_text(raw, UPDATED_KEYS)
    confidence = _score_json_task(
        raw,
        status=status,
        path_refs=path_refs,
        updated_at=updated_at,
    )
    return AdoptedTask(
        external_id=external_id,
        ai_sdlc_task_id=f"ADOPT-{index:03d}",
        title=title,
        description=_first_text(raw, DESCRIPTION_KEYS),
        status=status,
        source=source.rel_path,
        confidence=confidence,
        path_refs=path_refs,
        updated_at=updated_at,
        owner=_first_text(raw, OWNER_KEYS),
        blockers=blockers,
        dependencies=dependencies,
    )


def _score_json_task(
    raw: dict[str, Any],
    *,
    status: AdoptionTaskStatus,
    path_refs: tuple[str, ...],
    updated_at: str,
) -> float:
    score = 0.35
    keys = {str(key).lower() for key in raw}
    if keys & set(ID_KEYS):
        score += 0.1
    if keys & set(TITLE_KEYS):
        score += 0.15
    if keys & set(DESCRIPTION_KEYS):
        score += 0.08
    if status is not AdoptionTaskStatus.UNKNOWN:
        score += 0.16
    if path_refs:
        score += 0.08
    if keys & set(OWNER_KEYS):
        score += 0.04
    if keys & set(BLOCKER_KEYS):
        score += 0.04
    if updated_at:
        score += 0.05
    return min(score, 0.95)


def _normalize_status(raw_status: str, progress: object = None) -> AdoptionTaskStatus:
    value = raw_status.strip().lower()
    if value in {"todo", "open", "new", "pending", "backlog"}:
        return AdoptionTaskStatus.TODO
    if value in {"doing", "in_progress", "in-progress", "active", "wip"}:
        return AdoptionTaskStatus.DOING
    if value in {"done", "closed", "complete", "completed", "merged"}:
        return AdoptionTaskStatus.DONE
    if value in {"blocked", "stuck", "waiting"}:
        return AdoptionTaskStatus.BLOCKED
    if value in {"review", "needs-review", "needs_review", "qa"}:
        return AdoptionTaskStatus.NEEDS_REVIEW
    if isinstance(progress, int | float):
        if progress >= 100:
            return AdoptionTaskStatus.DONE
        if progress > 0:
            return AdoptionTaskStatus.DOING
    return AdoptionTaskStatus.UNKNOWN


def _fallback_task_from_structure(root: Path, target: Path) -> AdoptedTask:
    rel_target = _rel_path(target, root)
    return AdoptedTask(
        external_id="adopted-temp-001",
        ai_sdlc_task_id="ADOPT-TEMP-001",
        title="接入已有项目",
        description="未识别到现有任务文件，基于项目结构生成临时继续点。",
        status=AdoptionTaskStatus.NEEDS_REVIEW,
        source=rel_target,
        confidence=0.2,
        path_refs=(rel_target,),
    )


def _build_checkpoint_candidate(
    continue_point: AdoptionContinuePoint,
    tasks: tuple[AdoptedTask, ...],
) -> dict[str, Any]:
    return {
        "current_stage": "execute" if not continue_point.needs_review else "decompose",
        "active_task": continue_point.task_id,
        "active_title": continue_point.title,
        "needs_review": continue_point.needs_review,
        "adopted_task_count": len(tasks),
        "next_action": (
            "确认推荐继续点后进入实现"
            if continue_point.needs_review
            else "继续当前进行中任务"
        ),
    }


def _first_text(raw: dict[str, Any], keys: tuple[str, ...]) -> str:
    value = _first_present(raw, keys)
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, int | float):
        return str(value)
    return ""


def _first_present(raw: dict[str, Any], keys: tuple[str, ...]) -> object:
    lowered = {str(key).lower(): key for key in raw}
    for key in keys:
        original = lowered.get(key)
        if original is not None:
            return raw[original]
    return None


def _string_tuple_from_value(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value.strip(),) if value.strip() else ()
    if isinstance(value, list | tuple):
        return tuple(str(item).strip() for item in value if str(item).strip())
    return (str(value).strip(),) if str(value).strip() else ()


def _is_git_repo(root: Path) -> bool:
    return (root / ".git").exists()


def _git_output(root: Path, args: list[str]) -> str:
    try:
        result = subprocess.run(
            args,
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _rel_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _adoption_map_to_dict(adoption_map: AdoptionMap) -> dict[str, Any]:
    payload = asdict(adoption_map)
    payload["sources"] = [
        {**source, "kind": source["kind"].value if hasattr(source["kind"], "value") else source["kind"]}
        for source in payload["sources"]
    ]
    payload["tasks"] = [
        {
            **task,
            "status": task["status"].value
            if hasattr(task["status"], "value")
            else task["status"],
        }
        for task in payload["tasks"]
    ]
    return payload


def _render_bridge_markdown(adoption_map: AdoptionMap) -> str:
    cp = adoption_map.continue_point
    lines = [
        "# 接入已有项目桥接结果",
        "",
        "## 当前结果",
        "",
        f"- 推荐继续点：{cp.title}",
        f"- 外部任务 ID：`{cp.task_id}`",
        f"- 置信度：{cp.confidence:.2f}",
        f"- 需要人工确认：{'是' if cp.needs_review else '否'}",
        f"- 原因：{cp.reason}",
        "",
        "## 已识别任务",
        "",
    ]
    for task in adoption_map.tasks[:20]:
        lines.append(
            f"- `{task.external_id}` {task.title} "
            f"({task.status.value}, 置信度={task.confidence:.2f}, 来源={task.source})"
        )
    lines.extend(
        [
            "",
            "## 说明",
            "",
            "- 原任务文件不会被修改。",
            "- 如推荐不准确，可用自然语言纠偏，例如：`ai-sdlc adopt . --prefer \"支付回调\"`。",
            "- checkpoint 候选已写入 `.ai-sdlc/adoption/checkpoint-candidate.json`。",
            "- 后续可基于本桥接结果补齐 AI-SDLC 的 spec / plan / tasks。",
            "",
        ]
    )
    return "\n".join(lines)
