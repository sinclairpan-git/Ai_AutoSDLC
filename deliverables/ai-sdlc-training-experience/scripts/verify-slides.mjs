import playwright from "../node_modules/playwright/index.js";

const { chromium } = playwright;

const VIEWPORT = { width: 1366, height: 768 };
const BASE_URL = process.env.SLIDE_VERIFY_BASE_URL || "http://127.0.0.1:4317";
const SLIDE_COUNT = 19;
const failures = [];

function record(slide, reason, detail) {
  failures.push({ slide, reason, detail });
}

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: VIEWPORT, deviceScaleFactor: 1 });

for (let slide = 1; slide <= SLIDE_COUNT; slide += 1) {
  await page.goto(`${BASE_URL}/index.html?slide=${slide}`, { waitUntil: "networkidle", timeout: 10000 });
  await page.waitForTimeout(120);
  const metrics = await page.evaluate(() => {
    const slideRoot = document.querySelector("#slideRoot");
    const terminal = document.querySelector(".terminal-card pre");
    const bridgePill = document.querySelector(".bridge-flow span");
    const bridgeLaneCount = document.querySelectorAll(".bridge-lane").length;
    const bridgeFlowLineStats = Array.from(document.querySelectorAll(".bridge-flow span")).map((node) => {
      const textNode = Array.from(node.childNodes).find(
        (child) => child.nodeType === Node.TEXT_NODE && child.textContent?.trim(),
      );
      const rawText = textNode?.textContent || "";
      const lineLengths = [];
      const lineTops = [];

      if (textNode) {
        for (let index = 0; index < rawText.length; index += 1) {
          if (!rawText[index].trim()) continue;
          const range = document.createRange();
          range.setStart(textNode, index);
          range.setEnd(textNode, index + 1);
          const rect = range.getBoundingClientRect();
          const top = Math.round(rect.top);
          let lineIndex = lineTops.findIndex((value) => Math.abs(value - top) <= 2);
          if (lineIndex === -1) {
            lineTops.push(top);
            lineLengths.push(0);
            lineIndex = lineLengths.length - 1;
          }
          lineLengths[lineIndex] += 1;
        }
      }

      return {
        text: node.textContent?.trim() || "",
        lineLengths,
      };
    });
    const lead = document.querySelector(".lead");
    const holoPanel = document.querySelector(".holo-panel");
    const slideRect = slideRoot?.getBoundingClientRect();
    const routeCardText = Array.from(document.querySelectorAll(".route-card p")).map((node) => node.textContent?.trim() || "");
    const routeCardCount = document.querySelectorAll(".route-card").length;
    const executionCardBottoms = Array.from(document.querySelectorAll(".execution-card")).map((node) => {
      const rect = node.getBoundingClientRect();
      return {
        bottom: rect.bottom,
        slideBottom: slideRect?.bottom ?? 0,
      };
    });
    const executionDetailFigures = Array.from(document.querySelectorAll(".execution-detail-figure")).map((node) => {
      const rect = node.getBoundingClientRect();
      const image = node.querySelector("img");
      return {
        bottom: rect.bottom,
        slideBottom: slideRect?.bottom ?? 0,
        imageHeight: image?.getBoundingClientRect().height ?? 0,
      };
    });
    const holoPanelStyles = holoPanel
      ? {
          overflow: getComputedStyle(holoPanel).overflow,
          borderRadius: getComputedStyle(holoPanel).borderRadius,
          isolation: getComputedStyle(holoPanel).isolation,
          afterBorderRadius: getComputedStyle(holoPanel, "::after").borderRadius,
          afterFilter: getComputedStyle(holoPanel, "::after").filter,
        }
      : null;

    return {
      title: document.querySelector("#slideRoot h1, #slideRoot h2")?.textContent?.trim() || "",
      slideText: slideRoot?.innerText || "",
      executionKickerText: document.querySelector(".execution-detail-top small")?.textContent?.trim() || "",
      executionCommandText: document.querySelector(".execution-detail-top strong")?.textContent?.trim() || "",
      bodyOverflowX: document.body.scrollWidth - document.body.clientWidth,
      bodyOverflowY: document.body.scrollHeight - document.body.clientHeight,
      docOverflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      docOverflowY: document.documentElement.scrollHeight - document.documentElement.clientHeight,
      slideOverflowX: slideRoot ? slideRoot.scrollWidth - slideRoot.clientWidth : 0,
      slideOverflowY: slideRoot ? slideRoot.scrollHeight - slideRoot.clientHeight : 0,
      terminalOverflowX: terminal ? terminal.scrollWidth - terminal.clientWidth : 0,
      bridgeWhiteSpace: bridgePill ? getComputedStyle(bridgePill).whiteSpace : "",
      bridgeLaneCount,
      bridgeFlowLineStats,
      leadWordBreak: lead ? getComputedStyle(lead).wordBreak : "",
      leadOverflowWrap: lead ? getComputedStyle(lead).overflowWrap : "",
      routeCardText,
      routeCardCount,
      executionCardCount: document.querySelectorAll(".execution-card").length,
      executionCardBottoms,
      executionDetailFigures,
      holoPanelStyles,
    };
  });

  if (metrics.bodyOverflowX > 0 || metrics.docOverflowX > 0 || metrics.slideOverflowX > 0) {
    record(slide, "horizontal-overflow", metrics);
  }
  if (metrics.bodyOverflowY > 0 || metrics.docOverflowY > 0 || metrics.slideOverflowY > 0) {
    record(slide, "vertical-overflow", metrics);
  }
  if (metrics.terminalOverflowX > 0) {
    record(slide, "terminal-overflow", metrics);
  }
  if (slide === 7 && metrics.bridgeWhiteSpace === "nowrap") {
    record(slide, "bridge-pill-still-locked-to-nowrap", { whiteSpace: metrics.bridgeWhiteSpace });
  }
  if (
    slide === 7 &&
    metrics.bridgeFlowLineStats.some((item) => item.lineLengths.length > 1 && item.lineLengths.includes(1))
  ) {
    record(slide, "bridge-pill-single-character-wrap", metrics.bridgeFlowLineStats);
  }
  if (slide === 7 && metrics.bridgeLaneCount < 3) {
    record(slide, "bridge-structure-still-too-thin", { bridgeLaneCount: metrics.bridgeLaneCount });
  }
  if (metrics.leadWordBreak === "keep-all") {
    record(slide, "long-copy-locked-to-keep-all", {
      title: metrics.title,
      wordBreak: metrics.leadWordBreak,
      overflowWrap: metrics.leadOverflowWrap,
    });
  }
  if (slide === 14 && metrics.routeCardCount !== 4) {
    record(slide, "frontend-overview-step-count-mismatch", {
      routeCardCount: metrics.routeCardCount,
    });
  }
  if ([15, 16, 17, 18].includes(slide) && metrics.executionDetailFigures.length !== 1) {
    record(slide, "execution-detail-figure-count-mismatch", metrics.executionDetailFigures);
  }
  if (
    [15, 16, 17, 18].includes(slide) &&
    metrics.executionDetailFigures.some((figure) => figure.bottom > figure.slideBottom + 1 || figure.imageHeight < 340)
  ) {
    record(slide, "execution-detail-figure-clipped-or-too-small", metrics.executionDetailFigures);
  }
  if ([15, 16, 17, 18].includes(slide) && /真实/.test(metrics.executionKickerText)) {
    record(slide, "execution-detail-still-claims-raw-screenshot", {
      kicker: metrics.executionKickerText,
    });
  }
  if (slide === 15 && !/--execute --yes/.test(metrics.executionCommandText)) {
    record(slide, "solution-confirm-still-shown-as-non-execute-surface", {
      command: metrics.executionCommandText,
    });
  }
  if (
    slide === 15 &&
    (!/effective provider: public-primevue/i.test(metrics.slideText) ||
      !/recommended provider: enterprise-vue2/i.test(metrics.slideText))
  ) {
    record(slide, "solution-confirm-no-longer-explains-recommendation-vs-effective-truth", {
      slideText: metrics.slideText,
    });
  }
  if (slide === 16 && !/只读/.test(metrics.slideText)) {
    record(slide, "page-ui-schema-handoff-boundary-still-unclear", {
      slideText: metrics.slideText,
    });
  }
  if ([5, 19].includes(slide) && /命令演练/.test(metrics.slideText)) {
    record(slide, "dry-run-still-described-as-command-drill", {
      slideText: metrics.slideText,
    });
  }
  if ([5, 19].includes(slide) && !/治理激活证明/.test(metrics.slideText)) {
    record(slide, "dry-run-governance-boundary-missing", {
      slideText: metrics.slideText,
    });
  }
  if (slide === 14 && metrics.routeCardText.some((text) => /Agent|CLI|Stage Contract|PASS|RETRY|HALT/.test(text))) {
    record(slide, "frontend-copy-keeps-unneeded-english", metrics.routeCardText);
  }
  if (
    metrics.holoPanelStyles &&
    (metrics.holoPanelStyles.overflow !== "hidden" ||
      metrics.holoPanelStyles.isolation !== "isolate" ||
      metrics.holoPanelStyles.afterFilter === "none")
  ) {
    record(slide, "holo-panel-rotating-highlight-can-leak-corners", metrics.holoPanelStyles);
  }
}

await browser.close();

if (failures.length) {
  console.error(JSON.stringify(failures, null, 2));
  process.exit(1);
}

console.log(`Verified ${SLIDE_COUNT} slides at ${VIEWPORT.width}x${VIEWPORT.height}.`);
