"""Unit tests for ExecutionLogger."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.execution_logger import ExecutionLogger


class TestExecutionLogger:
    """ExecutionLogger append-only Markdown logging."""

    def test_creates_file_if_not_exists(self, tmp_path: Path) -> None:
        log_path = tmp_path / "subdir" / "execution-log.md"
        ExecutionLogger(log_path)
        assert log_path.exists()
        content = log_path.read_text(encoding="utf-8")
        assert content.startswith("# Execution Log")

    def test_log_task_appends_entry(self, tmp_path: Path) -> None:
        log_path = tmp_path / "log.md"
        elog = ExecutionLogger(log_path)

        ts = elog.log_task("T001", "completed")

        content = log_path.read_text(encoding="utf-8")
        assert "**T001**: completed" in content
        assert ts in content

    def test_log_task_with_details(self, tmp_path: Path) -> None:
        log_path = tmp_path / "log.md"
        elog = ExecutionLogger(log_path)

        elog.log_task("T002", "failed", details="assertion error on line 42")

        content = log_path.read_text(encoding="utf-8")
        assert "assertion error on line 42" in content

    def test_log_batch_appends_summary(self, tmp_path: Path) -> None:
        log_path = tmp_path / "log.md"
        elog = ExecutionLogger(log_path)

        ts = elog.log_batch(1, "All 3 tasks passed.")

        content = log_path.read_text(encoding="utf-8")
        assert "### Batch 1" in content
        assert "All 3 tasks passed." in content
        assert ts != ""

    def test_get_last_log_timestamp(self, tmp_path: Path) -> None:
        log_path = tmp_path / "log.md"
        elog = ExecutionLogger(log_path)
        assert elog.get_last_log_timestamp() == ""

        ts1 = elog.log_task("T1", "completed")
        assert elog.get_last_log_timestamp() == ts1

        ts2 = elog.log_batch(1, "done")
        assert elog.get_last_log_timestamp() == ts2
        assert ts2 >= ts1

    def test_multiple_logs_accumulate(self, tmp_path: Path) -> None:
        log_path = tmp_path / "log.md"
        elog = ExecutionLogger(log_path)

        elog.log_task("T1", "completed")
        elog.log_task("T2", "failed")
        elog.log_task("T3", "completed")

        content = log_path.read_text(encoding="utf-8")
        assert content.count("**T") == 3

    def test_existing_file_not_overwritten(self, tmp_path: Path) -> None:
        log_path = tmp_path / "log.md"
        log_path.write_text("# Existing Log\n\nOld content.\n", encoding="utf-8")

        elog = ExecutionLogger(log_path)
        elog.log_task("T1", "completed")

        content = log_path.read_text(encoding="utf-8")
        assert "Old content." in content
        assert "**T1**: completed" in content
