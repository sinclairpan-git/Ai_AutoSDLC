"""Jinja2 template generator for AI-SDLC files."""

from __future__ import annotations

import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

logger = logging.getLogger(__name__)


class TemplateGeneratorError(Exception):
    """Raised when template generation fails."""


class TemplateGenerator:
    """Generate files from Jinja2 templates."""

    def __init__(self, template_dir: Path | None = None) -> None:
        if template_dir is None:
            template_dir = Path(__file__).parent.parent / "templates"
        self._env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, template_name: str, context: dict[str, object]) -> str:
        """Render a template to string.

        Args:
            template_name: Template filename (e.g. "project-state.yaml.j2").
            context: Template variables.

        Returns:
            Rendered string.

        Raises:
            TemplateGeneratorError: If template not found or render fails.
        """
        try:
            tmpl = self._env.get_template(template_name)
            return tmpl.render(**context)
        except TemplateNotFound as exc:
            raise TemplateGeneratorError(
                f"Template not found: {template_name}"
            ) from exc
        except Exception as exc:
            raise TemplateGeneratorError(
                f"Failed to render {template_name}: {exc}"
            ) from exc

    def render_to_file(
        self,
        template_name: str,
        context: dict[str, object],
        output_path: Path,
    ) -> None:
        """Render a template and write to a file.

        Creates parent directories if needed.
        """
        content = self.render(template_name, context)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
