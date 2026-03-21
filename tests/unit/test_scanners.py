"""Tests for project scanners."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.scanners.api_scanner import scan_apis
from ai_sdlc.scanners.ast_scanner import scan_symbols
from ai_sdlc.scanners.dependency_scanner import scan_dependencies
from ai_sdlc.scanners.file_scanner import FileInfo, scan_files
from ai_sdlc.scanners.risk_scanner import scan_risks
from ai_sdlc.scanners.test_scanner import scan_tests


class TestFileScanner:
    def test_empty_dir(self, tmp_path: Path) -> None:
        result = scan_files(tmp_path)
        assert result == []

    def test_python_file_detection(self, tmp_path: Path) -> None:
        (tmp_path / "main.py").write_text("print('hello')\n")
        result = scan_files(tmp_path)
        assert len(result) == 1
        assert result[0].language == "python"
        assert result[0].line_count == 1
        assert result[0].is_entry_point is True

    def test_ignores_git_dir(self, tmp_path: Path) -> None:
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("core")
        (tmp_path / "app.py").write_text("pass")
        result = scan_files(tmp_path)
        assert len(result) == 1
        assert result[0].path == "app.py"

    def test_ignores_node_modules(self, tmp_path: Path) -> None:
        nm = tmp_path / "node_modules" / "lodash"
        nm.mkdir(parents=True)
        (nm / "index.js").write_text("module.exports = {}")
        src = tmp_path / "src"
        src.mkdir()
        (src / "app.js").write_text("console.log('hi')")
        result = scan_files(tmp_path)
        assert all("node_modules" not in f.path for f in result)
        assert any(f.path == "src/app.js" for f in result)

    def test_multi_language_project(self, tmp_path: Path) -> None:
        (tmp_path / "main.py").write_text("pass")
        (tmp_path / "index.ts").write_text("export default {}")
        (tmp_path / "App.java").write_text("class App {}")
        result = scan_files(tmp_path)
        languages = {f.language for f in result}
        assert "python" in languages
        assert "typescript" in languages
        assert "java" in languages

    def test_test_file_detection(self, tmp_path: Path) -> None:
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("def test_foo(): pass")
        result = scan_files(tmp_path)
        test_files = [f for f in result if f.is_test]
        assert len(test_files) == 1

    def test_config_file_detection(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("[tool.ruff]")
        (tmp_path / "Dockerfile").write_text("FROM python:3.11")
        result = scan_files(tmp_path)
        config_files = [f for f in result if f.is_config]
        assert len(config_files) >= 1

    def test_line_counting(self, tmp_path: Path) -> None:
        (tmp_path / "module.py").write_text("a = 1\nb = 2\nc = 3\n")
        result = scan_files(tmp_path)
        assert result[0].line_count == 3


class TestDependencyScanner:
    def test_no_manifests(self, tmp_path: Path) -> None:
        result = scan_dependencies(tmp_path)
        assert result == []

    def test_package_json(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").write_text("""{
            "dependencies": {"react": "^18.0.0", "next": "14.0.0"},
            "devDependencies": {"jest": "^29.0.0"}
        }""")
        result = scan_dependencies(tmp_path)
        assert len(result) == 3
        react = next(d for d in result if d.name == "react")
        assert react.ecosystem == "npm"
        assert react.is_dev is False
        jest = next(d for d in result if d.name == "jest")
        assert jest.is_dev is True

    def test_requirements_txt(self, tmp_path: Path) -> None:
        (tmp_path / "requirements.txt").write_text(
            "flask>=2.0\nrequests==2.28.0\n# comment\n-r other.txt\n"
        )
        result = scan_dependencies(tmp_path)
        assert len(result) == 2
        assert result[0].name == "flask"
        assert result[0].ecosystem == "pypi"

    def test_go_mod(self, tmp_path: Path) -> None:
        (tmp_path / "go.mod").write_text(
            "module github.com/example/app\n\ngo 1.21\n\n"
            "require (\n\tgithub.com/gin-gonic/gin v1.9.1\n)\n"
        )
        result = scan_dependencies(tmp_path)
        assert len(result) == 1
        assert result[0].name == "github.com/gin-gonic/gin"
        assert result[0].ecosystem == "go"

    def test_cargo_toml(self, tmp_path: Path) -> None:
        (tmp_path / "Cargo.toml").write_text(
            '[package]\nname = "myapp"\n\n[dependencies]\n'
            'serde = "1.0"\ntokio = "1.28"\n\n[dev-dependencies]\n'
            'criterion = "0.5"\n'
        )
        result = scan_dependencies(tmp_path)
        assert len(result) == 3
        dev_deps = [d for d in result if d.is_dev]
        assert len(dev_deps) == 1
        assert dev_deps[0].name == "criterion"

    def test_corrupt_package_json(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").write_text("{broken json")
        result = scan_dependencies(tmp_path)
        assert result == []

    def test_multiple_manifests(self, tmp_path: Path) -> None:
        (tmp_path / "requirements.txt").write_text("flask>=2.0\n")
        (tmp_path / "package.json").write_text('{"dependencies": {"express": "4.0"}}')
        result = scan_dependencies(tmp_path)
        ecosystems = {d.ecosystem for d in result}
        assert "pypi" in ecosystems
        assert "npm" in ecosystems


class TestAstScanner:
    def test_python_class_and_function(self, tmp_path: Path) -> None:
        (tmp_path / "module.py").write_text(
            'class UserService:\n    """Manages users."""\n    pass\n\n'
            'def create_user():\n    """Create a user."""\n    pass\n\n'
            'MAX_RETRIES = 3\n'
        )
        files = [FileInfo(path="module.py", language="python", category="source")]
        symbols = scan_symbols(tmp_path, files)
        names = {s.name for s in symbols}
        assert "UserService" in names
        assert "create_user" in names
        assert "MAX_RETRIES" in names
        cls = next(s for s in symbols if s.name == "UserService")
        assert cls.kind == "class"
        assert cls.docstring == "Manages users."

    def test_python_private_symbols(self, tmp_path: Path) -> None:
        (tmp_path / "mod.py").write_text("def _helper(): pass\nclass _Internal: pass\n")
        files = [FileInfo(path="mod.py", language="python", category="source")]
        symbols = scan_symbols(tmp_path, files)
        assert all(not s.is_public for s in symbols)

    def test_python_decorators(self, tmp_path: Path) -> None:
        (tmp_path / "api.py").write_text(
            "from fastapi import FastAPI\napp = FastAPI()\n\n"
            "@app.get\ndef index(): pass\n"
        )
        files = [FileInfo(path="api.py", language="python", category="source")]
        symbols = scan_symbols(tmp_path, files)
        func = next((s for s in symbols if s.name == "index"), None)
        assert func is not None
        assert "app.get" in func.decorators

    def test_js_export_detection(self, tmp_path: Path) -> None:
        (tmp_path / "service.ts").write_text(
            "export class AuthService {\n}\n\n"
            "export function login() {}\n\n"
            "export const API_URL = 'http://example.com';\n"
        )
        files = [FileInfo(path="service.ts", language="typescript", category="source")]
        symbols = scan_symbols(tmp_path, files)
        names = {s.name for s in symbols}
        assert "AuthService" in names
        assert "login" in names
        assert "API_URL" in names

    def test_java_class_detection(self, tmp_path: Path) -> None:
        (tmp_path / "User.java").write_text(
            "public class UserController {\n"
            "    public void getUser() {}\n"
            "}\n"
        )
        files = [FileInfo(path="User.java", language="java", category="source")]
        symbols = scan_symbols(tmp_path, files)
        names = {s.name for s in symbols}
        assert "UserController" in names

    def test_go_exported_types(self, tmp_path: Path) -> None:
        (tmp_path / "main.go").write_text(
            "package main\n\n"
            "type UserService struct {\n\tName string\n}\n\n"
            "func NewUserService() *UserService { return nil }\n"
        )
        files = [FileInfo(path="main.go", language="go", category="source")]
        symbols = scan_symbols(tmp_path, files)
        names = {s.name for s in symbols}
        assert "UserService" in names
        assert "NewUserService" in names

    def test_syntax_error_handled(self, tmp_path: Path) -> None:
        (tmp_path / "broken.py").write_text("def broken(:\n")
        files = [FileInfo(path="broken.py", language="python", category="source")]
        symbols = scan_symbols(tmp_path, files)
        assert symbols == []

    def test_skips_non_source(self, tmp_path: Path) -> None:
        (tmp_path / "readme.md").write_text("# Docs")
        files = [FileInfo(path="readme.md", language="markdown", category="doc")]
        symbols = scan_symbols(tmp_path, files)
        assert symbols == []


class TestApiScanner:
    def test_fastapi_routes(self, tmp_path: Path) -> None:
        (tmp_path / "api.py").write_text(
            "from fastapi import FastAPI\napp = FastAPI()\n\n"
            '@app.get("/users")\ndef list_users(): pass\n\n'
            '@app.post("/users")\ndef create_user(): pass\n'
        )
        files = [FileInfo(path="api.py", language="python", category="source")]
        endpoints = scan_apis(tmp_path, files)
        assert len(endpoints) == 2
        methods = {e.method for e in endpoints}
        assert "GET" in methods
        assert "POST" in methods
        assert endpoints[0].path == "/users"

    def test_flask_routes(self, tmp_path: Path) -> None:
        (tmp_path / "app.py").write_text(
            'from flask import Flask\napp = Flask(__name__)\n\n'
            '@app.route("/health")\ndef health(): return "ok"\n'
        )
        files = [FileInfo(path="app.py", language="python", category="source")]
        endpoints = scan_apis(tmp_path, files)
        assert len(endpoints) == 1
        assert endpoints[0].path == "/health"

    def test_express_routes(self, tmp_path: Path) -> None:
        (tmp_path / "routes.js").write_text(
            "const router = require('express').Router();\n"
            "router.get('/api/items', getItems);\n"
            "router.post('/api/items', createItem);\n"
        )
        files = [FileInfo(path="routes.js", language="javascript", category="source")]
        endpoints = scan_apis(tmp_path, files)
        assert len(endpoints) == 2
        assert endpoints[0].framework == "express"

    def test_no_apis_in_non_source(self, tmp_path: Path) -> None:
        (tmp_path / "config.json").write_text('{"get": "/foo"}')
        files = [FileInfo(path="config.json", language="json", category="config")]
        endpoints = scan_apis(tmp_path, files)
        assert endpoints == []


class TestTestScanner:
    def test_python_test_detection(self, tmp_path: Path) -> None:
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_auth.py").write_text(
            "def test_login(): pass\ndef test_logout(): pass\ndef helper(): pass\n"
        )
        files = [FileInfo(path="tests/test_auth.py", language="python", is_test=True, category="test")]
        result = scan_tests(tmp_path, files)
        assert len(result) == 1
        assert result[0].test_count == 2
        assert result[0].framework == "pytest"
        assert "test_login" in result[0].test_names

    def test_js_test_detection(self, tmp_path: Path) -> None:
        (tmp_path / "auth.test.js").write_text(
            "describe('auth', () => {\n"
            "  it('should login', () => {});\n"
            "  test('should logout', () => {});\n"
            "});\n"
        )
        files = [FileInfo(path="auth.test.js", language="javascript", is_test=True, category="test")]
        result = scan_tests(tmp_path, files)
        assert len(result) == 1
        assert result[0].test_count == 2

    def test_go_test_detection(self, tmp_path: Path) -> None:
        (tmp_path / "main_test.go").write_text(
            "package main\n\nimport \"testing\"\n\n"
            "func TestAdd(t *testing.T) {}\nfunc TestSub(t *testing.T) {}\n"
        )
        files = [FileInfo(path="main_test.go", language="go", is_test=True, category="test")]
        result = scan_tests(tmp_path, files)
        assert len(result) == 1
        assert result[0].test_count == 2
        assert result[0].framework == "go_test"

    def test_skips_non_test_files(self, tmp_path: Path) -> None:
        (tmp_path / "main.py").write_text("def main(): pass")
        files = [FileInfo(path="main.py", language="python", is_test=False, category="source")]
        result = scan_tests(tmp_path, files)
        assert result == []


class TestRiskScanner:
    def test_large_file_detection(self, tmp_path: Path) -> None:
        content = "\n".join([f"line_{i} = {i}" for i in range(600)])
        (tmp_path / "big.py").write_text(content)
        files = [FileInfo(path="big.py", language="python", line_count=600, category="source")]
        risks = scan_risks(tmp_path, files)
        large = [r for r in risks if r.category == "large_file"]
        assert len(large) == 1
        assert large[0].metric_value == 600.0

    def test_todo_density(self, tmp_path: Path) -> None:
        content = "\n".join([f"# TODO: fix item {i}" for i in range(8)] + ["code = 1"])
        (tmp_path / "messy.py").write_text(content)
        files = [FileInfo(path="messy.py", language="python", line_count=9, category="source")]
        risks = scan_risks(tmp_path, files)
        todos = [r for r in risks if r.category == "todo_density"]
        assert len(todos) == 1
        assert todos[0].metric_value == 8.0

    def test_no_risks_in_clean_project(self, tmp_path: Path) -> None:
        (tmp_path / "clean.py").write_text("x = 1\n")
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_clean.py").write_text("def test_x(): pass\n")
        files = [
            FileInfo(path="clean.py", language="python", line_count=1, category="source"),
            FileInfo(path="tests/test_clean.py", language="python", line_count=1, category="test", is_test=True),
        ]
        risks = scan_risks(tmp_path, files)
        large_or_todo = [r for r in risks if r.category in ("large_file", "todo_density")]
        assert large_or_todo == []
