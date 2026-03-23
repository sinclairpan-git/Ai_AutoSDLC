"""Per-pipeline stage manifests (YAML) for stage-based dispatch.

Each file defines one stage: prerequisites, must-read paths, rule references,
checklist steps, and expected outputs. Loaded by ``StageDispatcher`` and
``ai-sdlc stage`` CLI.
"""
