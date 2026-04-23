import { access, mkdir, readFile, stat, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
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

function lookupRoots(payload) {
  const roots = [];
  const managedTarget = String(payload.managed_frontend_target || "").trim();
  if (managedTarget && !managedTarget.includes("://")) {
    roots.push(path.resolve(process.cwd(), managedTarget));
  }

  const browserEntry = String(payload.browser_entry_ref || "").trim();
  if (browserEntry && !browserEntry.includes("://") && !browserEntry.startsWith("file://")) {
    const browserEntryPath = path.resolve(process.cwd(), browserEntry);
    roots.push(path.extname(browserEntryPath) ? path.dirname(browserEntryPath) : browserEntryPath);
  }

  roots.push(process.cwd());
  return [...new Set(roots)];
}

async function loadPlaywright(payload) {
  const require = createRequire(import.meta.url);
  for (const root of lookupRoots(payload)) {
    let resolved;
    try {
      resolved = require.resolve("playwright", { paths: [root] });
    } catch {
      continue;
    }

    try {
      const loaded = require(resolved);
      return loaded.default || loaded;
    } catch (error) {
      if (error && error.code !== "ERR_REQUIRE_ESM") {
        throw error;
      }
      const imported = await import(pathToFileURL(resolved).href);
      return imported.default || imported;
    }
  }
  throw new Error("playwright_runtime_unavailable");
}

async function loadRuntimeModule(payload, moduleName) {
  const require = createRequire(import.meta.url);
  for (const root of lookupRoots(payload)) {
    let resolved;
    try {
      resolved = require.resolve(moduleName, { paths: [root] });
    } catch {
      continue;
    }

    try {
      const loaded = require(resolved);
      return loaded.default || loaded;
    } catch (error) {
      if (error && error.code !== "ERR_REQUIRE_ESM") {
        throw error;
      }
      const imported = await import(pathToFileURL(resolved).href);
      return imported.default || imported;
    }
  }
  throw new Error(`${moduleName}_unavailable`);
}

function resolveViewportSize(viewportId) {
  switch (viewportId) {
    case "desktop-1440":
      return { width: 1440, height: 900 };
    case "tablet-834":
      return { width: 834, height: 1112 };
    case "mobile-390":
      return { width: 390, height: 844 };
    default:
      return { width: 1280, height: 720 };
  }
}

function resolveVisualRegressionPaths(payload) {
  const matrixId = String(payload.visual_regression_matrix_id || "").trim();
  if (!matrixId) {
    return null;
  }
  const baselineRoot = path.resolve(
    process.cwd(),
    "governance",
    "frontend",
    "quality-platform",
    "evidence",
    "visual-regression",
    "baselines",
    matrixId,
  );
  return {
    matrixId,
    baselineRoot,
    baselineImagePath: path.join(baselineRoot, "baseline.png"),
    baselineMetadataPath: path.join(baselineRoot, "baseline.yaml"),
  };
}

function parseBaselineYamlScalar(value) {
  const trimmed = value.trim();
  if (!trimmed) {
    return "";
  }
  if (trimmed === "true") {
    return true;
  }
  if (trimmed === "false") {
    return false;
  }
  if (trimmed === "null" || trimmed === "~") {
    return null;
  }
  if (
    (trimmed.startsWith('"') && trimmed.endsWith('"')) ||
    (trimmed.startsWith("'") && trimmed.endsWith("'"))
  ) {
    return trimmed.slice(1, -1);
  }
  const numeric = Number(trimmed);
  if (Number.isFinite(numeric)) {
    return numeric;
  }
  if (
    (trimmed.startsWith("[") && !trimmed.endsWith("]")) ||
    (trimmed.startsWith("{") && !trimmed.endsWith("}"))
  ) {
    throw new Error("invalid_yaml_scalar");
  }
  return trimmed;
}

function parseBaselineMetadata(raw) {
  const trimmed = raw.trim();
  if (!trimmed) {
    return {};
  }
  try {
    return JSON.parse(trimmed);
  } catch {
    // JSON is a YAML subset, but committed metadata may be plain YAML.
  }

  const metadata = {};
  let topLevelKeyCount = 0;
  for (const rawLine of raw.split(/\r?\n/)) {
    const line = rawLine.replace(/\s+#.*$/, "").trimEnd();
    if (!line.trim() || line.trimStart().startsWith("#")) {
      continue;
    }
    if (/^\s/.test(rawLine)) {
      continue;
    }
    if (line.startsWith("- ")) {
      throw new Error("invalid_yaml_top_level_sequence");
    }
    const match = line.match(/^([A-Za-z0-9_-]+):(?:\s*(.*))?$/);
    if (!match) {
      throw new Error("invalid_yaml_mapping");
    }
    const value = match[2] ?? "";
    metadata[match[1]] = value.trim() ? parseBaselineYamlScalar(value) : {};
    topLevelKeyCount += 1;
  }
  if (topLevelKeyCount === 0) {
    throw new Error("invalid_yaml_empty_mapping");
  }
  return metadata;
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

  const viewportSize = resolveViewportSize(
    String(payload.visual_regression_viewport_id || "").trim(),
  );
  const browser = await playwright.chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: viewportSize,
    deviceScaleFactor: 1,
    colorScheme: "light",
  });
  let traceStarted = false;
  await context.tracing.start({ screenshots: true, snapshots: true });
  traceStarted = true;
  const page = await context.newPage();
  const consoleErrorMessages = [];
  const pageErrorMessages = [];
  if (typeof page.on === "function") {
    page.on("console", (message) => {
      if (message.type() !== "error") {
        return;
      }
      const text = String(message.text?.() || "").trim();
      if (text) {
        consoleErrorMessages.push(text);
      }
    });
    page.on("pageerror", (error) => {
      const text =
        error instanceof Error
          ? String(error.stack || error.message || error.name || "").trim()
          : String(error || "").trim();
      if (text) {
        pageErrorMessages.push(text);
      }
    });
  }
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
    const visualRegressionCapture = await compareVisualRegression({
      artifactRoot,
      artifactRootRef,
      payload,
      screenshotPath,
    });

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
    const qualityCapture = await page.evaluate(() => {
      const normalizeText = (value) => String(value || "").replace(/\s+/g, " ").trim();
      const textFromReferences = (value) => {
        const ids = normalizeText(value).split(/\s+/).filter(Boolean);
        if (ids.length === 0) {
          return "";
        }
        return normalizeText(
          ids
            .map((id) => document.getElementById(id)?.textContent || "")
            .filter(Boolean)
            .join(" "),
        );
      };
      const elementText = (element) => {
        if (!(element instanceof HTMLElement)) {
          return "";
        }
        return normalizeText(
          element.getAttribute("aria-label") ||
            textFromReferences(element.getAttribute("aria-labelledby")) ||
            ("labels" in element && Array.isArray(Array.from(element.labels || []))
              ? Array.from(element.labels || [])
                  .map((label) => label.textContent || "")
                  .join(" ")
              : "") ||
            element.getAttribute("title") ||
            ("value" in element ? element.value : "") ||
            element.innerText ||
            element.textContent ||
            "",
        );
      };
      const hasAccessibleName = (element) => elementText(element).length > 0;
      const interactiveElements = Array.from(
        document.querySelectorAll(
          [
            "button",
            "[role='button']",
            "a[href]",
            "input:not([type='hidden'])",
            "select",
            "textarea",
            "[tabindex]:not([tabindex='-1'])",
          ].join(","),
        ),
      ).filter((element) => element instanceof HTMLElement);
      const buttonLikeElements = interactiveElements.filter((element) =>
        element.matches(
          [
            "button",
            "[role='button']",
            "a[href]",
            "input[type='button']",
            "input[type='submit']",
            "input[type='reset']",
          ].join(","),
        ),
      );
      const labeledFormControls = Array.from(
        document.querySelectorAll(
          "input:not([type='hidden']):not([type='button']):not([type='submit']):not([type='reset']), select, textarea",
        ),
      ).filter((element) => element instanceof HTMLElement);
      const landmarkSelectors = [
        "main",
        "header",
        "nav",
        "footer",
        "aside",
        "[role='main']",
        "[role='banner']",
        "[role='navigation']",
        "[role='contentinfo']",
        "[role='complementary']",
        "[role='search']",
        "[role='region']",
      ];
      const parseCssColor = (value) => {
        const normalized = String(value || "").trim().toLowerCase();
        if (!normalized || normalized === "transparent") {
          return null;
        }
        const rgbaMatch = normalized.match(/^rgba?\(([^)]+)\)$/);
        if (!rgbaMatch) {
          return null;
        }
        const parts = rgbaMatch[1].split(",").map((part) => part.trim());
        if (parts.length < 3) {
          return null;
        }
        const red = Number.parseFloat(parts[0]);
        const green = Number.parseFloat(parts[1]);
        const blue = Number.parseFloat(parts[2]);
        const alpha = parts.length >= 4 ? Number.parseFloat(parts[3]) : 1;
        if ([red, green, blue, alpha].some((value) => Number.isNaN(value))) {
          return null;
        }
        return { r: red, g: green, b: blue, a: alpha };
      };
      const isVisibleElement = (element) => {
        if (!(element instanceof HTMLElement)) {
          return false;
        }
        const style = window.getComputedStyle(element);
        if (
          style.display === "none" ||
          style.visibility === "hidden" ||
          Number.parseFloat(style.opacity || "1") === 0
        ) {
          return false;
        }
        const rect = element.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0 && element.getClientRects().length > 0;
      };
      const relativeLuminance = (color) => {
        const transform = (channel) => {
          const normalized = channel / 255;
          return normalized <= 0.03928
            ? normalized / 12.92
            : ((normalized + 0.055) / 1.055) ** 2.4;
        };
        return 0.2126 * transform(color.r) + 0.7152 * transform(color.g) + 0.0722 * transform(color.b);
      };
      const contrastRatio = (foreground, background) => {
        const foregroundLuminance = relativeLuminance(foreground);
        const backgroundLuminance = relativeLuminance(background);
        const lighter = Math.max(foregroundLuminance, backgroundLuminance);
        const darker = Math.min(foregroundLuminance, backgroundLuminance);
        return (lighter + 0.05) / (darker + 0.05);
      };
      const getEffectiveBackgroundColor = (element) => {
        let current = element instanceof HTMLElement ? element : null;
        while (current) {
          const background = parseCssColor(window.getComputedStyle(current).backgroundColor);
          if (background && background.a > 0) {
            return background;
          }
          current = current.parentElement;
        }
        const bodyBackground = parseCssColor(
          window.getComputedStyle(document.body || document.documentElement).backgroundColor,
        );
        if (bodyBackground && bodyBackground.a > 0) {
          return bodyBackground;
        }
        const rootBackground = parseCssColor(
          window.getComputedStyle(document.documentElement).backgroundColor,
        );
        if (rootBackground && rootBackground.a > 0) {
          return rootBackground;
        }
        return { r: 255, g: 255, b: 255, a: 1 };
      };
      const hasVisibleFocusIndicator = (element) => {
        if (!(element instanceof HTMLElement)) {
          return false;
        }
        const style = window.getComputedStyle(element);
        const outlineWidth = Number.parseFloat(style.outlineWidth || "0") || 0;
        const outlineVisible = style.outlineStyle !== "none" && outlineWidth > 0;
        const shadowVisible = String(style.boxShadow || "").trim().toLowerCase() !== "none";
        const pseudoVisible =
          typeof element.matches === "function" ? element.matches(":focus-visible") : false;
        return outlineVisible || shadowVisible || pseudoVisible;
      };
      const focusableCandidates = Array.from(
        document.querySelectorAll(
          [
            "button",
            "[role='button']",
            "a[href]",
            "input:not([type='hidden'])",
            "select",
            "textarea",
            "[tabindex]:not([tabindex='-1'])",
          ].join(","),
        ),
      ).filter(
        (element) =>
          element instanceof HTMLElement &&
          !element.hasAttribute("disabled") &&
          element.getAttribute("aria-hidden") !== "true" &&
          isVisibleElement(element),
      );
      const textSamples = Array.from(document.querySelectorAll("body *")).filter((element) => {
        if (!(element instanceof HTMLElement)) {
          return false;
        }
        if (!isVisibleElement(element)) {
          return false;
        }
        if (element.childElementCount !== 0) {
          return false;
        }
        const tagName = String(element.tagName || "").toUpperCase();
        if (["SCRIPT", "STYLE", "NOSCRIPT", "TEMPLATE"].includes(tagName)) {
          return false;
        }
        return normalizeText(element.textContent || "").length > 0;
      });
      let lowContrastTextCount = 0;
      for (const element of textSamples) {
        const style = window.getComputedStyle(element);
        const foreground = parseCssColor(style.color);
        if (!foreground) {
          continue;
        }
        const background = getEffectiveBackgroundColor(element);
        const ratio = contrastRatio(foreground, background);
        const fontSize = Number.parseFloat(style.fontSize || "0") || 0;
        const fontWeight = String(style.fontWeight || "").toLowerCase();
        const numericWeight = Number.parseFloat(fontWeight);
        const isBold =
          fontWeight.includes("bold") || (Number.isFinite(numericWeight) && numericWeight >= 700);
        const isLargeText = fontSize >= 24 || (isBold && fontSize >= 18.66);
        const minimumContrast = isLargeText ? 3 : 4.5;
        if (ratio < minimumContrast) {
          lowContrastTextCount += 1;
        }
      }
      let focusableWithoutVisibleFocusCount = 0;
      for (const element of focusableCandidates) {
        try {
          element.focus({ preventScroll: true });
        } catch {
          element.focus();
        }
        if (!hasVisibleFocusIndicator(element)) {
          focusableWithoutVisibleFocusCount += 1;
        }
      }
      if (document.activeElement instanceof HTMLElement && document.activeElement !== document.body) {
        document.activeElement.blur();
      }
      const viewportWidth = window.innerWidth || document.documentElement.clientWidth || 0;
      const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0;
      const documentScrollWidth = document.documentElement.scrollWidth || 0;
      const documentScrollHeight = document.documentElement.scrollHeight || 0;
      const horizontalOverflowCount = Array.from(
        document.querySelectorAll("body *"),
      ).filter((element) => {
        if (!(element instanceof HTMLElement)) {
          return false;
        }
        const rect = element.getBoundingClientRect();
        return rect.right > viewportWidth + 1 || rect.left < -1;
      }).length;
      return {
        body_text_char_count: normalizeText(document.body?.innerText || "").length,
        heading_count: document.querySelectorAll("h1, h2, h3, h4, h5, h6, [role='heading']").length,
        landmark_count: document.querySelectorAll(landmarkSelectors.join(",")).length,
        interactive_count: interactiveElements.length,
        unlabeled_button_count: buttonLikeElements.filter((element) => !hasAccessibleName(element))
          .length,
        unlabeled_input_count: labeledFormControls.filter((element) => !hasAccessibleName(element))
          .length,
        image_missing_alt_count: Array.from(document.querySelectorAll("img")).filter((image) => {
          const altText = normalizeText(image.getAttribute("alt"));
          return !image.hasAttribute("alt") || altText.length === 0;
        }).length,
        viewport_width: viewportWidth,
        viewport_height: viewportHeight,
        document_scroll_width: documentScrollWidth,
        document_scroll_height: documentScrollHeight,
        horizontal_overflow_count: horizontalOverflowCount,
        low_contrast_text_count: lowContrastTextCount,
        focusable_count: focusableCandidates.length,
        focusable_without_visible_focus_count: focusableWithoutVisibleFocusCount,
      };
    });
    const normalizedQualityCapture = {
      body_text_char_count: Number(qualityCapture?.body_text_char_count || 0),
      heading_count: Number(qualityCapture?.heading_count || 0),
      landmark_count: Number(qualityCapture?.landmark_count || 0),
      interactive_count: Number(qualityCapture?.interactive_count || 0),
      unlabeled_button_count: Number(qualityCapture?.unlabeled_button_count || 0),
      unlabeled_input_count: Number(qualityCapture?.unlabeled_input_count || 0),
      image_missing_alt_count: Number(qualityCapture?.image_missing_alt_count || 0),
      viewport_width: Number(qualityCapture?.viewport_width || 0),
      viewport_height: Number(qualityCapture?.viewport_height || 0),
      document_scroll_width: Number(qualityCapture?.document_scroll_width || 0),
      document_scroll_height: Number(qualityCapture?.document_scroll_height || 0),
      horizontal_overflow_count: Number(qualityCapture?.horizontal_overflow_count || 0),
      low_contrast_text_count: Number(qualityCapture?.low_contrast_text_count || 0),
      focusable_count: Number(qualityCapture?.focusable_count || 0),
      focusable_without_visible_focus_count: Number(
        qualityCapture?.focusable_without_visible_focus_count || 0,
      ),
    };
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
          provider_runtime_adapter_carrier_mode: String(
            payload.provider_runtime_adapter_carrier_mode || "",
          ).trim(),
          provider_runtime_adapter_delivery_state: String(
            payload.provider_runtime_adapter_delivery_state || "",
          ).trim(),
          provider_runtime_adapter_evidence_state: String(
            payload.provider_runtime_adapter_evidence_state || "",
          ).trim(),
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
      quality_capture: {
        gate_run_id: payload.gate_run_id,
        page_title: pageTitle,
        final_url: finalUrl,
        screenshot_ref: `${artifactRootRef}/shared-runtime/navigation-screenshot.png`,
        body_text_char_count: normalizedQualityCapture.body_text_char_count,
        heading_count: normalizedQualityCapture.heading_count,
        landmark_count: normalizedQualityCapture.landmark_count,
        interactive_count: normalizedQualityCapture.interactive_count,
        unlabeled_button_count: normalizedQualityCapture.unlabeled_button_count,
        unlabeled_input_count: normalizedQualityCapture.unlabeled_input_count,
        image_missing_alt_count: normalizedQualityCapture.image_missing_alt_count,
        viewport_width: normalizedQualityCapture.viewport_width,
        viewport_height: normalizedQualityCapture.viewport_height,
        document_scroll_width: normalizedQualityCapture.document_scroll_width,
        document_scroll_height: normalizedQualityCapture.document_scroll_height,
        horizontal_overflow_count: normalizedQualityCapture.horizontal_overflow_count,
        low_contrast_text_count: normalizedQualityCapture.low_contrast_text_count,
        focusable_count: normalizedQualityCapture.focusable_count,
        focusable_without_visible_focus_count:
          normalizedQualityCapture.focusable_without_visible_focus_count,
        console_error_messages: consoleErrorMessages,
        page_error_messages: pageErrorMessages,
      },
      visual_regression_capture: visualRegressionCapture,
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

async function compareVisualRegression({
  artifactRoot,
  artifactRootRef,
  payload,
  screenshotPath,
}) {
  const matrixPaths = resolveVisualRegressionPaths(payload);
  const screenshotRef = `${artifactRootRef}/shared-runtime/navigation-screenshot.png`;
  if (matrixPaths === null) {
    return {
      matrix_id: "",
      gate_run_id: payload.gate_run_id,
      capture_status: "missing",
      screenshot_ref: screenshotRef,
      baseline_ref: "",
      baseline_metadata_ref: "",
      diff_image_ref: "",
      diff_ratio: 1,
      threshold: 0.03,
      region_summaries: [],
      change_summary: "visual-regression-matrix-unavailable",
      capture_protocol_ref: "",
      bootstrap_ref: "",
      verdict: "evidence_missing",
    };
  }

  const baselineExists = await pathExists(matrixPaths.baselineImagePath);
  const metadataExists = await pathExists(matrixPaths.baselineMetadataPath);
  const baselineRef = `artifact:${path.relative(process.cwd(), matrixPaths.baselineImagePath)}`;
  const baselineMetadataRef = `artifact:${path.relative(
    process.cwd(),
    matrixPaths.baselineMetadataPath,
  )}`;
  const bootstrapPath = path.join(
    artifactRoot,
    "bootstrap",
    "bootstrap-receipt.yaml",
  );
  const bootstrapRef = `artifact:${path.relative(process.cwd(), bootstrapPath)}`;
  await mkdir(path.dirname(bootstrapPath), { recursive: true });

  if (!baselineExists || !metadataExists) {
    await writeFile(
      bootstrapPath,
      JSON.stringify(
        {
          schema_version: "frontend-visual-regression-bootstrap/v1",
          gate_run_id: payload.gate_run_id,
          matrix_id: matrixPaths.matrixId,
          managed_frontend_target: String(payload.managed_frontend_target || "").trim(),
          package_manager: "npm",
          dependency_refs: ["pixelmatch", "pngjs"],
          lockfile_ref: "managed/frontend/package-lock.json",
          status: "ready",
          failure_reason: "",
        },
        null,
        2,
      ),
      "utf8",
    );
    return {
      matrix_id: matrixPaths.matrixId,
      gate_run_id: payload.gate_run_id,
      capture_status: "missing",
      screenshot_ref: screenshotRef,
      baseline_ref: baselineRef,
      baseline_metadata_ref: baselineMetadataRef,
      diff_image_ref: "",
      diff_ratio: 1,
      threshold: 0.03,
      region_summaries: [],
      change_summary: "baseline-missing",
      capture_protocol_ref: `matrix:${matrixPaths.matrixId}`,
      bootstrap_ref: bootstrapRef,
      verdict: "evidence_missing",
    };
  }

  let baselineMetadata;
  try {
    baselineMetadata = parseBaselineMetadata(
      await readFile(matrixPaths.baselineMetadataPath, "utf8"),
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    await writeFile(
      bootstrapPath,
      JSON.stringify(
        {
          schema_version: "frontend-visual-regression-bootstrap/v1",
          gate_run_id: payload.gate_run_id,
          matrix_id: matrixPaths.matrixId,
          managed_frontend_target: String(payload.managed_frontend_target || "").trim(),
          package_manager: "npm",
          dependency_refs: ["pixelmatch", "pngjs"],
          lockfile_ref: "managed/frontend/package-lock.json",
          status: "failed",
          failure_reason: `baseline-metadata-invalid:${message}`,
        },
        null,
        2,
      ),
      "utf8",
    );
    return {
      matrix_id: matrixPaths.matrixId,
      gate_run_id: payload.gate_run_id,
      capture_status: "capture_failed",
      screenshot_ref: screenshotRef,
      baseline_ref: baselineRef,
      baseline_metadata_ref: baselineMetadataRef,
      diff_image_ref: "",
      diff_ratio: 1,
      threshold: 0.03,
      region_summaries: [],
      change_summary: "baseline-metadata-invalid",
      capture_protocol_ref: `matrix:${matrixPaths.matrixId}`,
      bootstrap_ref: bootstrapRef,
      verdict: "recheck",
    };
  }
  const threshold = Number(baselineMetadata.threshold ?? 0.03);
  if (!Number.isFinite(threshold) || threshold < 0 || threshold > 1) {
    await writeFile(
      bootstrapPath,
      JSON.stringify(
        {
          schema_version: "frontend-visual-regression-bootstrap/v1",
          gate_run_id: payload.gate_run_id,
          matrix_id: matrixPaths.matrixId,
          managed_frontend_target: String(payload.managed_frontend_target || "").trim(),
          package_manager: "npm",
          dependency_refs: ["pixelmatch", "pngjs"],
          lockfile_ref: "managed/frontend/package-lock.json",
          status: "failed",
          failure_reason: "baseline-threshold-invalid",
        },
        null,
        2,
      ),
      "utf8",
    );
    return {
      matrix_id: matrixPaths.matrixId,
      gate_run_id: payload.gate_run_id,
      capture_status: "capture_failed",
      screenshot_ref: screenshotRef,
      baseline_ref: baselineRef,
      baseline_metadata_ref: baselineMetadataRef,
      diff_image_ref: "",
      diff_ratio: 1,
      threshold: 0.03,
      region_summaries: [],
      change_summary: "baseline-threshold-invalid",
      capture_protocol_ref: `matrix:${matrixPaths.matrixId}`,
      bootstrap_ref: bootstrapRef,
      verdict: "recheck",
    };
  }

  let pngjs;
  let pixelmatch;
  try {
    pngjs = await loadRuntimeModule(payload, "pngjs");
    pixelmatch = await loadRuntimeModule(payload, "pixelmatch");
  } catch {
    await writeFile(
      bootstrapPath,
      JSON.stringify(
        {
          schema_version: "frontend-visual-regression-bootstrap/v1",
          gate_run_id: payload.gate_run_id,
          matrix_id: matrixPaths.matrixId,
          managed_frontend_target: String(payload.managed_frontend_target || "").trim(),
          package_manager: "npm",
          dependency_refs: ["pixelmatch", "pngjs"],
          lockfile_ref: "managed/frontend/package-lock.json",
          status: "failed",
          failure_reason: "visual-regression-dependencies-unavailable",
        },
        null,
        2,
      ),
      "utf8",
    );
    return {
      matrix_id: matrixPaths.matrixId,
      gate_run_id: payload.gate_run_id,
      capture_status: "capture_failed",
      screenshot_ref: screenshotRef,
      baseline_ref: baselineRef,
      baseline_metadata_ref: baselineMetadataRef,
      diff_image_ref: "",
      diff_ratio: 1,
      threshold,
      region_summaries: [],
      change_summary: "visual-regression-dependencies-unavailable",
      capture_protocol_ref: `matrix:${matrixPaths.matrixId}`,
      bootstrap_ref: bootstrapRef,
      verdict: "transient_run_failure",
    };
  }

  const currentPng = pngjs.PNG.sync.read(await readFile(screenshotPath));
  const baselinePng = pngjs.PNG.sync.read(await readFile(matrixPaths.baselineImagePath));
  if (
    currentPng.width !== baselinePng.width ||
    currentPng.height !== baselinePng.height
  ) {
    await writeFile(
      bootstrapPath,
      JSON.stringify(
        {
          schema_version: "frontend-visual-regression-bootstrap/v1",
          gate_run_id: payload.gate_run_id,
          matrix_id: matrixPaths.matrixId,
          managed_frontend_target: String(payload.managed_frontend_target || "").trim(),
          package_manager: "npm",
          dependency_refs: ["pixelmatch", "pngjs"],
          lockfile_ref: "managed/frontend/package-lock.json",
          status: "ready",
          failure_reason: "",
        },
        null,
        2,
      ),
      "utf8",
    );
    return {
      matrix_id: matrixPaths.matrixId,
      gate_run_id: payload.gate_run_id,
      capture_status: "capture_failed",
      screenshot_ref: screenshotRef,
      baseline_ref: baselineRef,
      baseline_metadata_ref: baselineMetadataRef,
      diff_image_ref: "",
      diff_ratio: 1,
      threshold,
      region_summaries: [],
      change_summary: "dimension-mismatch",
      capture_protocol_ref: `matrix:${matrixPaths.matrixId}`,
      bootstrap_ref: bootstrapRef,
      verdict: "actual_quality_blocker",
    };
  }

  const diffPng = new pngjs.PNG({ width: baselinePng.width, height: baselinePng.height });
  const diffPixels = pixelmatch(
    currentPng.data,
    baselinePng.data,
    diffPng.data,
    baselinePng.width,
    baselinePng.height,
    { threshold: 0.1, includeAA: true },
  );
  const diffRatio = diffPixels / (baselinePng.width * baselinePng.height);
  const diffPath = path.join(artifactRoot, "visual-regression", "diff.png");
  await mkdir(path.dirname(diffPath), { recursive: true });
  await writeFile(diffPath, pngjs.PNG.sync.write(diffPng));
  await writeFile(
    bootstrapPath,
    JSON.stringify(
      {
        schema_version: "frontend-visual-regression-bootstrap/v1",
        gate_run_id: payload.gate_run_id,
        matrix_id: matrixPaths.matrixId,
        managed_frontend_target: String(payload.managed_frontend_target || "").trim(),
        package_manager: "npm",
        dependency_refs: ["pixelmatch", "pngjs"],
        lockfile_ref: "managed/frontend/package-lock.json",
        status: "ready",
        failure_reason: "",
      },
      null,
      2,
    ),
    "utf8",
  );

  const verdict = diffRatio > threshold ? "actual_quality_blocker" : "pass";
  return {
    matrix_id: matrixPaths.matrixId,
    gate_run_id: payload.gate_run_id,
    capture_status: "captured",
    screenshot_ref: screenshotRef,
    baseline_ref: baselineRef,
    baseline_metadata_ref: baselineMetadataRef,
    diff_image_ref: `artifact:${path.relative(process.cwd(), diffPath)}`,
    diff_ratio: diffRatio,
    threshold,
    region_summaries: [
      {
        region_id: "overall",
        diff_ratio: diffRatio,
        threshold,
        verdict,
      },
    ],
    change_summary:
      diffRatio > threshold
        ? "visual-regression-diff-over-threshold"
        : "visual-regression-within-threshold",
    capture_protocol_ref: `matrix:${matrixPaths.matrixId}`,
    bootstrap_ref: bootstrapRef,
    verdict,
  };
}

async function main() {
  const raw = await readStdin();
  const payload = JSON.parse(raw || "{}");
  let playwright;
  try {
    playwright = await loadPlaywright(payload);
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
