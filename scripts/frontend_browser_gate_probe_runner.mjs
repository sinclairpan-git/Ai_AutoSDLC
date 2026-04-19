import { access, mkdir, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) {
    chunks.push(chunk);
  }
  return Buffer.concat(chunks).toString("utf8");
}

function transientResult(payload, diagnosticCode, warning) {
  const artifactRootRef = String(payload.artifact_root_ref || "").trim();
  return {
    runtime_status: "failed_transient",
    shared_capture: {
      gate_run_id: payload.gate_run_id,
      trace_artifact_ref: `${artifactRootRef}/shared-runtime/playwright-trace.zip`,
      navigation_screenshot_ref: `${artifactRootRef}/shared-runtime/navigation-screenshot.png`,
      capture_status: "capture_failed",
      final_url: "",
      anchor_refs: [],
      diagnostic_codes: [diagnosticCode],
    },
    interaction_capture: {
      gate_run_id: payload.gate_run_id,
      interaction_probe_id: "primary-action",
      artifact_refs: [`${artifactRootRef}/interaction/interaction-snapshot.json`],
      capture_status: "capture_failed",
      classification_candidate: "transient_run_failure",
      blocking_reason_codes: [diagnosticCode],
      anchor_refs: [],
    },
    diagnostic_codes: [diagnosticCode],
    warnings: [warning],
  };
}

async function pathExists(targetPath) {
  try {
    await access(targetPath);
    return true;
  } catch {
    return false;
  }
}

async function resolveBrowserEntry(payload) {
  const raw = String(payload.browser_entry_ref || "").trim();
  if (!raw) {
    throw new Error("browser_entry_unavailable");
  }
  if (raw.startsWith("http://") || raw.startsWith("https://")) {
    return raw;
  }
  if (raw.startsWith("file://")) {
    return raw;
  }
  if (raw.includes("://")) {
    throw new Error("browser_entry_unavailable");
  }

  let absolutePath = path.resolve(process.cwd(), raw);
  if (!(await pathExists(absolutePath)) && !path.extname(absolutePath)) {
    absolutePath = path.join(absolutePath, "index.html");
  }
  if (!(await pathExists(absolutePath))) {
    throw new Error("browser_entry_unavailable");
  }
  const targetStat = await stat(absolutePath);
  if (targetStat.isDirectory()) {
    absolutePath = path.join(absolutePath, "index.html");
    if (!(await pathExists(absolutePath))) {
      throw new Error("browser_entry_unavailable");
    }
  }
  return pathToFileURL(absolutePath).href;
}

async function captureProbe(playwright, payload) {
  const artifactRoot = path.resolve(String(payload.artifact_root || ""));
  const artifactRootRef = String(payload.artifact_root_ref || "").trim();
  const sharedRuntimeDir = path.join(artifactRoot, "shared-runtime");
  const interactionDir = path.join(artifactRoot, "interaction");
  await mkdir(sharedRuntimeDir, { recursive: true });
  await mkdir(interactionDir, { recursive: true });

  const tracePath = path.join(sharedRuntimeDir, "playwright-trace.zip");
  const screenshotPath = path.join(sharedRuntimeDir, "navigation-screenshot.png");
  const interactionPath = path.join(interactionDir, "interaction-snapshot.json");

  const browser = await playwright.chromium.launch({ headless: true });
  const context = await browser.newContext();
  let traceStarted = false;
  await context.tracing.start({ screenshots: true, snapshots: true });
  traceStarted = true;
  const page = await context.newPage();
  let finalUrl = "";
  try {
    const targetUrl = await resolveBrowserEntry(payload);
    try {
      await page.goto(targetUrl, { waitUntil: "domcontentloaded", timeout: 10000 });
    } catch {
      throw new Error("navigation_failed");
    }
    finalUrl = page.url();
    await page.screenshot({ path: screenshotPath, fullPage: true });

    const pageIntegrity = await page.evaluate(() => ({
      bodyText: document.body?.innerText?.trim() || "",
      elementCount: document.body?.querySelectorAll("*").length || 0,
    }));
    if (!pageIntegrity.bodyText && pageIntegrity.elementCount === 0) {
      throw new Error("browser_entry_unavailable");
    }

    const interactionSnapshot = await page.evaluate(async (probePayload) => {
      const deliveryContextScript = document.querySelector("#frontend-delivery-context");
      let embeddedDeliveryContext = null;
      if (
        deliveryContextScript instanceof HTMLScriptElement &&
        deliveryContextScript.textContent
      ) {
        try {
          embeddedDeliveryContext = JSON.parse(deliveryContextScript.textContent);
        } catch {
          embeddedDeliveryContext = null;
        }
      }

      const renderedDeliveryEntryId =
        document.querySelector(".entry-eyebrow")?.textContent?.trim() ||
        String(embeddedDeliveryContext?.deliveryEntryId || "").trim();
      const renderedPackages = Array.from(
        document.querySelectorAll(".package-item"),
        (node) => node.textContent?.trim() || "",
      ).filter(Boolean);
      const renderedPageSchemaIds = Array.from(
        document.querySelectorAll(".page-item"),
        (node) => node.textContent?.trim() || "",
      ).filter(Boolean);

      const blockingReasonCodes = [];
      const expectedDeliveryEntryId = String(probePayload.delivery_entry_id || "").trim();
      if (
        expectedDeliveryEntryId &&
        renderedDeliveryEntryId !== expectedDeliveryEntryId
      ) {
        blockingReasonCodes.push("delivery_entry_render_mismatch");
      }

      const expectedPackages = Array.isArray(probePayload.component_library_packages)
        ? probePayload.component_library_packages
            .map((item) => String(item).trim())
            .filter(Boolean)
        : [];
      if (expectedPackages.some((pkg) => !renderedPackages.includes(pkg))) {
        blockingReasonCodes.push("component_library_package_render_mismatch");
      }

      const expectedPageSchemaIds = Array.isArray(probePayload.page_schema_ids)
        ? probePayload.page_schema_ids
            .map((item) => String(item).trim())
            .filter(Boolean)
        : [];
      if (expectedPageSchemaIds.some((schemaId) => !renderedPageSchemaIds.includes(schemaId))) {
        blockingReasonCodes.push("page_schema_render_mismatch");
      }

      if (blockingReasonCodes.length > 0) {
        return {
          interaction_probe_id: "primary-action",
          anchor_refs: ["interaction:delivery-context"],
          classification_candidate: "actual_quality_blocker",
          blocking_reason_codes: blockingReasonCodes,
          rendered_delivery_entry_id: renderedDeliveryEntryId,
          rendered_component_library_packages: renderedPackages,
          rendered_page_schema_ids: renderedPageSchemaIds,
          delivery_context_validation_status: "failed",
          detail: "delivery-context-render-mismatch",
        };
      }

      const selectors = [
        "button",
        "[role='button']",
        "a[href]",
        "input[type='submit']",
      ];
      const candidate = document.querySelector(selectors.join(","));
      if (!candidate) {
        return {
          interaction_probe_id: "primary-action",
          anchor_refs: [],
          classification_candidate: "evidence_missing",
          blocking_reason_codes: ["interaction_target_missing"],
          rendered_delivery_entry_id: renderedDeliveryEntryId,
          rendered_component_library_packages: renderedPackages,
          rendered_page_schema_ids: renderedPageSchemaIds,
          delivery_context_validation_status: "passed",
          detail: "no-interactive-target",
        };
      }
      const html = candidate instanceof HTMLElement ? candidate.outerHTML.slice(0, 200) : "";
      if (candidate instanceof HTMLElement) {
        candidate.click();
        await new Promise((resolve) => setTimeout(resolve, 50));
      }
        return {
          interaction_probe_id: "primary-action",
          anchor_refs: [html ? `interaction:${html}` : "interaction:primary-action"],
          classification_candidate: "pass",
          blocking_reason_codes: [],
          rendered_delivery_entry_id: renderedDeliveryEntryId,
          rendered_component_library_packages: renderedPackages,
          rendered_page_schema_ids: renderedPageSchemaIds,
          delivery_context_validation_status: "passed",
          detail: "clicked-primary-candidate",
        };
    }, payload);

    const pageTitle = await page.title();
    await writeFile(
      interactionPath,
      JSON.stringify(
        {
          gate_run_id: payload.gate_run_id,
          generated_at: payload.generated_at,
          final_url: finalUrl,
          page_title: pageTitle,
          delivery_entry_id: String(payload.delivery_entry_id || "").trim(),
          component_library_packages: Array.isArray(payload.component_library_packages)
            ? payload.component_library_packages.map((item) => String(item))
            : [],
          provider_theme_adapter_id: String(payload.provider_theme_adapter_id || "").trim(),
          page_schema_ids: Array.isArray(payload.page_schema_ids)
            ? payload.page_schema_ids.map((item) => String(item))
            : [],
          effective_provider: String(payload.effective_provider || "").trim(),
          effective_style_pack: String(payload.effective_style_pack || "").trim(),
          ...interactionSnapshot,
        },
        null,
        2,
      ),
      "utf8",
    );
    await context.tracing.stop({ path: tracePath });
    traceStarted = false;

    return {
      runtime_status: "completed",
      shared_capture: {
        gate_run_id: payload.gate_run_id,
        trace_artifact_ref: `${artifactRootRef}/shared-runtime/playwright-trace.zip`,
        navigation_screenshot_ref: `${artifactRootRef}/shared-runtime/navigation-screenshot.png`,
        capture_status: "captured",
        final_url: finalUrl,
        anchor_refs: finalUrl ? [finalUrl] : [],
        diagnostic_codes: [],
      },
      interaction_capture: {
        gate_run_id: payload.gate_run_id,
        interaction_probe_id: "primary-action",
        artifact_refs: [`${artifactRootRef}/interaction/interaction-snapshot.json`],
        capture_status: "captured",
        classification_candidate: interactionSnapshot.classification_candidate || "pass",
        blocking_reason_codes: interactionSnapshot.blocking_reason_codes || [],
        anchor_refs: interactionSnapshot.anchor_refs || [],
      },
      diagnostic_codes: [],
      warnings: [],
    };
  } finally {
    await page.close().catch(() => {});
    if (traceStarted) {
      await context.tracing.stop({ path: tracePath }).catch(() => {});
    }
    await context.close().catch(() => {});
    await browser.close().catch(() => {});
  }
}

async function main() {
  const raw = await readStdin();
  const payload = JSON.parse(raw || "{}");
  let playwright;
  try {
    playwright = await import("playwright");
  } catch {
    process.stdout.write(
      `${JSON.stringify(
        transientResult(
          payload,
          "playwright_runtime_unavailable",
          "Playwright runtime is not available on this host. Install Playwright and its browsers for this frontend host, then re-run `uv run ai-sdlc program browser-gate-probe --execute`.",
        ),
      )}\n`,
    );
    return;
  }

  try {
    const result = await captureProbe(playwright, payload);
    process.stdout.write(`${JSON.stringify(result)}\n`);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    const diagnosticCode =
      message === "browser_entry_unavailable"
        ? "browser_entry_unavailable"
        : message === "navigation_failed"
          ? "navigation_failed"
          : "browser_launch_failed";
    process.stdout.write(
      `${JSON.stringify(
        transientResult(
          payload,
          diagnosticCode,
          diagnosticCode === "browser_entry_unavailable"
            ? "The managed frontend target did not resolve to a loadable browser entry. Materialize a browser entry such as `index.html`, or point the apply artifact at a navigable URL, then re-run `uv run ai-sdlc program browser-gate-probe --execute`."
            : diagnosticCode === "navigation_failed"
            ? "Browser navigation failed before the probe could complete. Confirm the browser entry exists and is loadable, then re-run `uv run ai-sdlc program browser-gate-probe --execute`."
            : "Browser launch failed before the probe could complete. Restore the frontend browser runtime, then re-run `uv run ai-sdlc program browser-gate-probe --execute`.",
        ),
      )}\n`,
    );
  }
}

await main();
