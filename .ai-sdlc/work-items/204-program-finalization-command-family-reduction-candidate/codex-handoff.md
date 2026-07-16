# Continuity Handoff

- Updated: 2026-07-16T01:31:41+00:00
- Reason: Record the close-check receipt correction before regenerating the terminal snapshot
- Goal: Resolve Program Truth merge-topology self-staleness while preserving the WI-204 RC-09 No-Go
- State: Implementation payload 6d4a7965ed179aca2247f1f5a9312bce269f7f68 plus the terminal receipt define the root-cause repair and required close markers; the v2 snapshot is generated only from their clean head, and final acceptance is read-only on fresh main
- Stage: close
- Work Item: 204-program-finalization-command-family-reduction-candidate
- Branch: codex/program-truth-merge-stability

## Changed Files
- M .ai-sdlc/state/codex-handoff.md
- M .ai-sdlc/state/resume-pack.yaml
- M .ai-sdlc/work-items/204-program-finalization-command-family-reduction-candidate/codex-handoff.md
- M .ai-sdlc/work-items/204-program-finalization-command-family-reduction-candidate/resume-pack.yaml
- M .ai-sdlc/work-items/204-program-finalization-command-family-reduction-candidate/working-set.yaml
- M docs/framework-defect-backlog.zh-CN.md
- M program-manifest.yaml
- M specs/204-program-finalization-command-family-reduction-candidate/task-execution-log.md
- M src/ai_sdlc/core/program_service.py
- M tests/unit/test_program_service.py

## Key Decisions
- Normalize only branch_only_implemented and mainline_merged inside the snapshot source-hash projection
- Keep raw truth-check API, capability gate, RC-09 revocation, claim=0, and all candidate handlers unchanged
- The terminal receipt must include code-change constraints plus deleted/removed lifecycle markers; no checkpoint or runtime mutation

## Commands / Tests
- RED: 2 failed on projection and real Git branch-to-main topology; GREEN: targeted 2, ProgramService 406, Program CLI plus close-check 300, Ruff and constraints PASS
- First exact close-check correctly rejected the receipt until constraints and deleted/removed lifecycle markers were explicit

## Blockers / Risks
- Risk control: regenerate the v2 snapshot from the corrected clean receipt head and prove feature, projected-main, and real main freshness

## Local PR Review
- none

## Exact Next Steps
- Terminal protocol: commit corrected receipt and continuity, regenerate the v2 snapshot from that clean head, run exact-head dual review and CI, then perform read-only fresh-main acceptance without another continuity write
