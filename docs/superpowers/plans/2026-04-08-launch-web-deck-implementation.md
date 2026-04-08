# Launch Web Deck Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild `.deliverables/launch-web` from a long-scroll launch page into a single-screen, keyboard-driven presentation deck that matches the approved AI-SDLC Chinese slide structure.

**Architecture:** Replace the existing section-anchor page with a slide-state deck shell. Keep the deliverable self-contained inside `.deliverables/launch-web/`, move navigation truth into `app.js`, express the stage/chrome/slide system in `styles.css`, and update the contract test so it validates deck behavior and content instead of scroll-page markers.

**Tech Stack:** Static HTML, CSS, vanilla JavaScript, pytest, local `python3 -m http.server`, Playwright screenshot verification

---

## Planned File Structure

- `/.deliverables/launch-web/site/index.html`: deck shell, slide markup, desktop chrome, narrow-screen pager, slide metadata hooks.
- `/.deliverables/launch-web/site/styles.css`: stage layout, Spine Led chrome, slide visual system, desktop/narrow-screen responsive branch, motion and reduced-motion handling.
- `/.deliverables/launch-web/site/app.js`: slide state, keyboard navigation, `?slide=` sync, resize/orientation responsive mode switch, narrow-screen pager wiring.
- `/.deliverables/launch-web/tests/test_launch_web_contract.py`: contract tests for deck shell, Chinese slide copy, navigation model, responsive control branch, and style markers.
- `/.deliverables/launch-web/README.md`: preview/test commands and QA checklist updated from long page to deck walkthrough.

## Execution Order And Boundaries

- Critical path:
  1. Freeze the new deck contract in tests and README.
  2. Rebuild `index.html` into slide-based structure.
  3. Rebuild `styles.css` around stage/chrome/slide layout.
  4. Replace `app.js` scroll logic with slide-state logic and run full verification.
- Guardrails:
  - Do not preserve anchor-scroll navigation as a fallback desktop path.
  - Do not introduce frameworks, bundlers, or external dependencies.
  - Do not expose visible previous/next buttons above `900px`.
  - Keep all changes inside `.deliverables/launch-web/` plus plan/spec docs already written.

## Task 1: Freeze The New Deck Contract

**Files:**
- Modify: `/.deliverables/launch-web/tests/test_launch_web_contract.py`
- Modify: `/.deliverables/launch-web/README.md`
- Test: `/.deliverables/launch-web/tests/test_launch_web_contract.py`

- [ ] **Step 1: Write the failing deck-shell contract tests**

Add focused tests that assert the new baseline:

```python
def test_launch_web_uses_slide_deck_shell():
    html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    assert 'class="deck-app"' in html
    assert 'data-slide="1"' in html
    assert "deck-chrome" in html


def test_launch_web_documents_deck_preview():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "ArrowLeft / ArrowRight" in readme
    assert "PageUp / PageDown / Space / Home / End" in readme
    assert "<= 900px" in readme
```

Also remove or replace assertions that lock the old anchor-section model (`id="hero"`, `IntersectionObserver`, `.site-nav`, `.comparison-matrix`, etc.) when those markers are no longer valid for the approved deck design.

- [ ] **Step 2: Run the focused contract tests and confirm they fail**

Run: `uv run pytest .deliverables/launch-web/tests/test_launch_web_contract.py -k "deck_shell or documents_deck_preview" -v`

Expected: FAIL because current deliverable still uses the long-scroll section model and old README wording.

- [ ] **Step 3: Update the README and minimal contract expectations**

Implement the smallest non-visual contract/document changes needed for the new baseline:

- rewrite README preview/QA language around slide deck behavior
- document the full keyboard set `ArrowLeft / ArrowRight / PageUp / PageDown / Space / Home / End`
- document `?slide=1` deep link and narrow-screen pager branch
- keep preview and test commands intact

Do not rebuild the full page yet; only make the contract/document layer reflect the approved design.

- [ ] **Step 4: Re-run the focused contract tests**

Run: `uv run pytest .deliverables/launch-web/tests/test_launch_web_contract.py -k "documents_deck_preview" -v`

Expected: PASS for README/documentation-focused assertions, while HTML deck-shell assertions still remain red until Task 2.

- [ ] **Step 5: Commit**

```bash
git add .deliverables/launch-web/tests/test_launch_web_contract.py .deliverables/launch-web/README.md
git commit -m "test: freeze launch web deck contract"
```

## Task 2: Rebuild The HTML Into An 8-Slide Deck

**Files:**
- Modify: `/.deliverables/launch-web/site/index.html`
- Modify: `/.deliverables/launch-web/tests/test_launch_web_contract.py`
- Test: `/.deliverables/launch-web/tests/test_launch_web_contract.py`

- [ ] **Step 1: Write the failing slide-structure and copy tests**

Add focused assertions for:

```python
def test_launch_web_contains_eight_slides_in_order():
    html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    markers = [
        'data-slide="1"',
        'data-slide="2"',
        'data-slide="3"',
        'data-slide="4"',
        'data-slide="5"',
        'data-slide="6"',
        'data-slide="7"',
        'data-slide="8"',
    ]
    offsets = [html.index(marker) for marker in markers]
    assert offsets == sorted(offsets)
    assert html.count('class="deck-slide"') == 8


def test_launch_web_contains_approved_slide_titles():
    html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    approved_pairs = [
        ("AI-SDLC 是把任务、产物、校验、回退绑在一起的交付框架", "我们要改的不是聊天框，而是交付链路本身。"),
        ("模型够用了，交付还在人工兜底", "今天卡住效率的，不是生成能力，而是任务分解、上下文续接和完成确认。"),
        ("问题不在模型聪不聪明，而在偏差有没有被关住", "一旦没有状态和校验，AI 的不确定性就会变成“看起来完成”。"),
        ("AI-SDLC 的三件事：阶段、状态、校验", "它不是把任务排顺序，而是让每一步都有输入、产物、判定和回退。"),
        ("这不是普通工作流编排", "普通 workflow 只管下一步，AI-SDLC 还要管完成定义、失败处理和默认约束。"),
        ("执行完成不算完成，验证通过才算", "每个任务都必须留下可检查的证据，没有通过验证就不能算交付。"),
        ("失败不只是修补，要回写成规则", "一次失败只有进入归因、更新规则和工具之后，才算真正被系统吸收。"),
        ("把 AI 从助手变成研发底座", "真正的差别不是有没有 AI，而是结果能不能被验证、被继承、被持续复用。"),
    ]
    for title, lede in approved_pairs:
        assert title in html
        assert lede in html
```

Also add assertions for:

- desktop chrome markers such as `deck-chrome`, `deck-progress`, `spine-meta`
- narrow-screen pager markup such as `deck-pager`
- current slide semantics via `aria-hidden`, `data-active`, or equivalent stable hooks
- legacy section markers such as `id="hero"` and `id="problem"` no longer appearing in the final HTML

- [ ] **Step 2: Run the focused HTML tests and confirm they fail**

Run: `uv run pytest .deliverables/launch-web/tests/test_launch_web_contract.py -k "eight_slides or approved_slide_titles" -v`

Expected: FAIL because `index.html` still contains long-scroll sections and old copy.

- [ ] **Step 3: Replace the long page markup with the deck shell and approved 8-slide content**

Implement in `index.html`:

- one outer `.deck-app` / `.deck-stage`
- one desktop `.deck-chrome` with brand, current chapter, current title, page count, and progress
- one slide rail/container holding exactly 8 slides
- approved Chinese titles and main statements from the frozen spec
- desktop-hidden / narrow-screen-visible pager shell for `<=900px`

Keep HTML responsibilities clear:

- slide order and content live in the DOM
- state hooks are declarative (`data-slide`, `data-chapter`, `data-title`)
- no anchor-nav leftovers or section-scroll affordances remain

- [ ] **Step 4: Re-run the focused HTML tests**

Run: `uv run pytest .deliverables/launch-web/tests/test_launch_web_contract.py -k "eight_slides or approved_slide_titles or deck_shell" -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add .deliverables/launch-web/site/index.html .deliverables/launch-web/tests/test_launch_web_contract.py
git commit -m "feat: rebuild launch web markup as slide deck"
```

## Task 3: Rebuild The Visual System For Stage, Spine, And Responsive Pager

**Files:**
- Modify: `/.deliverables/launch-web/site/styles.css`
- Modify: `/.deliverables/launch-web/tests/test_launch_web_contract.py`
- Test: `/.deliverables/launch-web/tests/test_launch_web_contract.py`

- [ ] **Step 1: Write the failing CSS contract tests**

Replace old scroll-page selectors with deck-specific expectations:

```python
def test_launch_web_css_contains_deck_stage_markers():
    css = (ROOT / "site" / "styles.css").read_text(encoding="utf-8")
    required = [
        ".deck-app",
        ".deck-stage",
        ".deck-chrome",
        ".deck-progress",
        ".deck-slide",
        ".deck-pager",
        "@media (max-width: 900px)",
    ]
    for marker in required:
        assert marker in css
```

Add focused assertions for:

- desktop stage locking (`height: 100vh` or equivalent)
- hidden desktop pager / visible narrow-screen pager
- slide transition markers
- preserved visual tokens such as `--bg`, `--surface`, `--accent`
- reduced text sprawl markers such as balance/wrap handling on slide headings and body copy

- [ ] **Step 2: Run the focused CSS tests and confirm they fail**

Run: `uv run pytest .deliverables/launch-web/tests/test_launch_web_contract.py -k "css_contains_deck_stage_markers" -v`

Expected: FAIL because `styles.css` still styles `.site-nav`, `.hero`, and scroll sections.

- [ ] **Step 3: Rewrite `styles.css` around the approved deck layout**

Implement:

- stage-level layout and viewport lock
- Spine Led chrome with desktop-only presence
- slide card/layout variants for cover, problem, architecture, innovation, and closing slides
- `>900px` desktop branch that hides explicit prev/next controls
- `<=900px` branch that shows the pager and compresses the spine into a top bar
- meaningful but restrained horizontal slide motion, plus `prefers-reduced-motion` fallback

Preserve the approved pale technical atmosphere instead of reverting to generic white cards or dark-stage styling.

- [ ] **Step 4: Re-run the focused CSS tests**

Run: `uv run pytest .deliverables/launch-web/tests/test_launch_web_contract.py -k "css_contains_deck_stage_markers" -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add .deliverables/launch-web/site/styles.css .deliverables/launch-web/tests/test_launch_web_contract.py
git commit -m "feat: restyle launch web as presentation deck"
```

## Task 4: Replace Scroll Logic With Slide State And Run Full Verification

**Files:**
- Modify: `/.deliverables/launch-web/site/app.js`
- Modify: `/.deliverables/launch-web/tests/test_launch_web_contract.py`
- Test: `/.deliverables/launch-web/tests/test_launch_web_contract.py`
- Verify: `/.deliverables/launch-web/site/index.html`
- Verify: `/.deliverables/launch-web/site/styles.css`
- Verify: `/.deliverables/launch-web/site/app.js`

- [ ] **Step 1: Write the failing JS/navigation tests**

Add focused assertions for:

```python
def test_launch_web_js_uses_slide_state_navigation():
    js = (ROOT / "site" / "app.js").read_text(encoding="utf-8")
    assert "URLSearchParams" in js
    assert "ArrowRight" in js
    assert "ArrowLeft" in js
    assert "PageDown" in js
    assert "PageUp" in js
    assert "Space" in js
    assert "Home" in js
    assert "End" in js
    assert "matchMedia" in js
    assert "resize" in js
```

Also assert the new logic covers:

- `?slide` 1-based parsing and invalid-value fallback
- no-op behavior at first/last slide boundaries
- `ArrowLeft / ArrowRight / PageUp / PageDown / Space / Home / End` all mapping to the approved deck actions
- `>900px` desktop path with hidden pager
- `<=900px` pager binding and resize/orientation recalculation
- `prefers-reduced-motion` fallback

- [ ] **Step 2: Run the focused JS tests and confirm they fail**

Run: `uv run pytest .deliverables/launch-web/tests/test_launch_web_contract.py -k "js_uses_slide_state_navigation" -v`

Expected: FAIL because `app.js` still uses `IntersectionObserver` and anchor scroll syncing.

- [ ] **Step 3: Replace `app.js` with deck state management**

Implement:

- slide index parsing from `?slide`
- slide activation/render sync for chrome, progress, and active slide
- desktop keyboard navigation
- narrow-screen pager click handling
- resize/orientation branch recalculation
- reduced-motion-aware transitions

Remove:

- `IntersectionObserver` section tracking
- anchor smooth-scroll code
- `aria-current` nav syncing tied to old header links

- [ ] **Step 4: Run the full contract suite and browser verification**

Run: `uv run pytest .deliverables/launch-web/tests/test_launch_web_contract.py -v`

Expected: PASS

Then verify the rendered deck:

1. Start preview: `python3 -m http.server 4180 --directory .deliverables/launch-web/site`
2. Capture desktop proof with keyboard flow at `1728x1117`
3. Capture narrow-screen proof with visible pager at `390x844`
4. Confirm:
   - desktop has no visible prev/next buttons
   - `?slide=5` deep-links to slide 5
   - `<=900px` shows the pager
   - slide 5 clearly reads as “这不是普通工作流编排”
   - pressing `Space` and `PageDown` on desktop changes slides without reintroducing vertical page scrolling

- [ ] **Step 5: Commit**

```bash
git add .deliverables/launch-web/site/app.js .deliverables/launch-web/tests/test_launch_web_contract.py .deliverables/launch-web/site/index.html .deliverables/launch-web/site/styles.css .deliverables/launch-web/README.md
git commit -m "feat: finish launch web deck navigation"
```

## Final Verification Checklist

- [ ] `uv run pytest .deliverables/launch-web/tests/test_launch_web_contract.py -v`
- [ ] `python3 -m http.server 4180 --directory .deliverables/launch-web/site`
- [ ] Desktop screenshot captured around `1728x1117`
- [ ] Narrow-screen screenshot captured around `390x844`
- [ ] `?slide=1`, `?slide=5`, and invalid `?slide=999` behavior checked
- [ ] Desktop hides visible pager; narrow-screen shows pager
- [ ] Desktop `Space` / `PageDown` navigation does not trigger vertical scrolling
- [ ] Final slide title remains `把 AI 从助手变成研发底座`
