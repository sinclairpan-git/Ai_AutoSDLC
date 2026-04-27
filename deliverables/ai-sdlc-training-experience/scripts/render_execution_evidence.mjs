import fs from "node:fs/promises";
import path from "node:path";
import playwright from "../node_modules/playwright/index.js";

const { chromium } = playwright;

const previewPath = path.resolve(
  new URL("../assets/execution-browser-preview.png", import.meta.url).pathname,
);

const cards = [
  {
    id: "stack",
    windowTitle: "solution-confirm",
    command: "python -m ai_sdlc program solution-confirm --execute --yes",
    body: `Program Frontend Solution Confirm Simple

Recommended Solution
  - recommended_frontend_stack: vue2
  - recommended_provider_id: enterprise-vue2
  - recommended_style_pack_id: enterprise-default
  - recommendation_reason_text: Enterprise baseline is available and preferred.

Final Preflight
  - requested_frontend_stack: vue3
  - requested_provider_id: public-primevue
  - requested_style_pack_id: modern-saas
  - effective_frontend_stack: vue3
  - effective_provider_id: public-primevue
  - effective_style_pack_id: modern-saas
  - preflight_status: ready
  - user_overrode_recommendation: true`,
  },
  {
    id: "style",
    windowTitle: "page-ui-schema-handoff",
    command: "python -m ai_sdlc program page-ui-schema-handoff",
    body: `Frontend Page/UI Schema Handoff
  - state: ready
  - provider: public-primevue
  - style pack: modern-saas
  - delivery entry: vue3-public-primevue
  - provider theme adapter: public-primevue-theme-bridge
  - component package: primevue
  - component package: @primeuix/themes
  - page schema: dashboard-workspace | recipe: DashboardPage
  - page schema: search-list-workspace | recipe: SearchListPage
  - page schema: wizard-workspace | recipe: WizardPage`,
  },
  {
    id: "apply",
    windowTitle: "managed-delivery-apply",
    command: "python -m ai_sdlc program managed-delivery-apply --execute --yes --ack-effective-change",
    body: `Program Managed Delivery Apply Execute

Managed Delivery Apply Guard
  - apply state: ready_to_execute
  - selected action types: managed_target_prepare, dependency_install
    artifact_generate, workspace_integration
  - managed target path: managed/frontend
  - delivery remains incomplete until browser gate and downstream closure finish

Managed Delivery Apply Result
  - status: apply_succeeded_pending_browser_gate
  - delivery complete: false
  - browser gate required: true
  - browser gate state: pending
  - executed actions: managed-target-prepare, dependency-install
    visual-regression-runtime-install, artifact-generate, workspace-integration

Artifacts
  - managed/frontend/index.html: present
  - managed/frontend/package.json: present
  - managed/frontend/src/App.vue: present
  - runtime-boundary-receipt.yaml: present`,
  },
  {
    id: "gate",
    windowTitle: "browser-gate-probe",
    command: "python -m ai_sdlc program browser-gate-probe --execute",
    body: `Program Browser Gate Probe Execute

Browser Gate Probe Guard
  - probe state: ready_to_execute
  - managed frontend target: managed/frontend
  - delivery entry: vue3-public-primevue
  - component package: primevue
  - component package: @primeuix/themes
  - browser entry ref: managed/frontend/index.html

Browser Gate Probe Result
  - probe runtime state: completed
  - smoke verdict: pass
  - visual verdict: pass
  - a11y verdict: pass
  - interaction anti-pattern verdict: pass
  - overall gate status: passed
  - artifact root: .ai-sdlc/artifacts/frontend-browser-gate/gate-run-2026-04-23t02-15-45z`,
    preview: true,
  },
];

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderCard(card, previewDataUrl = "") {
  const preview = card.preview
    ? `<div class="browser-panel">
        <div class="panel-top browser-top"><span></span><span></span><span></span><strong>被校验页面预览</strong></div>
        <img src="${previewDataUrl}" alt="managed frontend preview" />
      </div>`
    : "";
  const splitClass = card.preview ? "screen-shell split" : "screen-shell";
  return `<!doctype html>
  <html lang="zh-CN">
    <head>
      <meta charset="utf-8" />
      <style>
        :root {
          color-scheme: dark;
          --bg: #06101b;
          --panel: #0d1726;
          --line: rgba(81, 223, 255, 0.28);
          --line-strong: rgba(81, 223, 255, 0.42);
          --text: #edf5ff;
          --muted: #a9b9cc;
          --cyan: #4de9ff;
          --green: #65f2b3;
          --amber: #ffd166;
          --shadow: 0 28px 64px rgba(0, 0, 0, 0.34);
        }
        * { box-sizing: border-box; }
        body {
          margin: 0;
          background:
            radial-gradient(circle at top left, rgba(77, 233, 255, 0.14), transparent 30%),
            radial-gradient(circle at top right, rgba(101, 242, 179, 0.12), transparent 28%),
            #040913;
          font-family: "SF Pro Display", "PingFang SC", "Microsoft YaHei", sans-serif;
          color: var(--text);
        }
        .frame {
          width: 1600px;
          min-height: 980px;
          padding: 12px;
        }
        .screen-shell {
          display: grid;
          gap: 12px;
          padding: 10px;
          border: 1px solid var(--line);
          border-radius: 22px;
          background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)), var(--bg);
          box-shadow: var(--shadow);
        }
        .screen-shell.split {
          grid-template-columns: minmax(0, 1.3fr) minmax(380px, 0.7fr);
          align-items: stretch;
        }
        .terminal-panel, .browser-panel {
          min-width: 0;
          border: 1px solid var(--line-strong);
          border-radius: 18px;
          overflow: hidden;
          background: #08110f;
        }
        .panel-top {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 14px 18px;
          border-bottom: 1px solid rgba(81, 223, 255, 0.16);
          background: rgba(255,255,255,0.04);
        }
        .panel-top span {
          width: 11px;
          height: 11px;
          border-radius: 50%;
          background: var(--green);
          box-shadow: 0 0 12px rgba(101, 242, 179, 0.28);
        }
        .panel-top strong {
          margin-left: 8px;
          font-size: 16px;
          color: #d6faff;
          font-weight: 650;
        }
        .command {
          margin: 0;
          padding: 16px 18px 0;
          color: var(--amber);
          font-family: "SFMono-Regular", Consolas, monospace;
          font-size: 24px;
          line-height: 1.35;
          white-space: pre-wrap;
        }
        pre {
          margin: 0;
          padding: 16px 18px 20px;
          color: #c3ffe0;
          font-family: "SFMono-Regular", Consolas, monospace;
          font-size: 30px;
          line-height: 1.42;
          white-space: pre-wrap;
          overflow-wrap: anywhere;
        }
        .browser-panel img {
          display: block;
          width: 100%;
          height: 100%;
          min-height: 820px;
          object-fit: contain;
          object-position: top center;
          background: #f4f7fb;
        }
      </style>
    </head>
    <body>
      <main class="frame">
        <section class="${splitClass}">
          <div class="terminal-panel">
            <div class="panel-top"><span></span><span></span><span></span><strong>${escapeHtml(card.windowTitle)}</strong></div>
            <p class="command">$ ${escapeHtml(card.command)}</p>
            <pre>${escapeHtml(card.body)}</pre>
          </div>
          ${preview}
        </section>
      </main>
    </body>
  </html>`;
}

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1700, height: 1080 }, deviceScaleFactor: 1 });
const previewDataUrl = await fs
  .readFile(previewPath)
  .then((buffer) => `data:image/png;base64,${buffer.toString("base64")}`);

for (const card of cards) {
  const html = renderCard(card, previewDataUrl);
  await page.setContent(html, { waitUntil: "load" });
  const outPath = path.resolve(
    new URL(`../assets/execution-${card.id}.png`, import.meta.url).pathname,
  );
  const target = card.preview ? ".screen-shell" : ".terminal-panel";
  await page.locator(target).screenshot({ path: outPath });
}

await browser.close();
console.log(cards.map((card) => `execution-${card.id}.png`).join("\n"));
