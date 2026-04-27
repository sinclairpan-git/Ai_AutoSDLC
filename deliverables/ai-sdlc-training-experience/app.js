const chapters = [
  { id: "sense", title: "认知建立", audience: "认知视角" },
  { id: "start", title: "第一次上手", audience: "实践视角" },
  { id: "system", title: "系统骨架", audience: "工程视角" },
  { id: "govern", title: "治理闭环", audience: "治理视角" },
  { id: "close", title: "收束", audience: "总结视角" },
];

const slides = [
  {
    chapter: "sense",
    title: "AI-SDLC：把 AI 编码，升级成可证明的交付系统",
    lead: "它解决的不是“模型会不会写”，而是需求会不会漂、结果能不能验、失败会不会留下来，团队能不能稳定接住 AI 的速度。",
    note: "开场先钉住一句话定义：AI-SDLC 的对象不是提示词，而是交付闭环。",
    visual: "hero",
    cards: [
      ["失控点", "需求、执行、验证和发布不再靠聊天记忆串起来。"],
      ["控制面", "入口、真值、门禁、状态、调度、证据一起决定能否继续。"],
      ["结果", "交付变成可追溯、可恢复、可复核、可回写的系统行为。"],
    ],
  },
  {
    chapter: "sense",
    title: "没有框架时，AI 交付最常见的 4 种失控",
    lead: "真正拖慢团队的不是模型偶尔写错，而是需求漂移、上下文断裂、假完成和失败经验不会进入下一次默认约束。",
    note: "这一页用具体失控场景建认知，不上来讲组件名词。",
    visual: "failures",
  },
  {
    chapter: "sense",
    title: "三条路径的差异，不在“谁更聪明”，而在“谁更能闭环”",
    lead: "比较要落在同一组维度上：探索速度、需求是否固定、执行是否受约束、验证是否要过门、失败是否能进入下一次默认规则，而不是泛泛说哪套方法更强。",
    note: "把比较维度钉死，避免只靠话术抬高 AI-SDLC。",
    visual: "compare",
    compare: [
      ["随手试做", ["探索很快，适合试方向", "需求与实现常混在聊天里", "正式交付边界不固定", "验收多靠肉眼和临时补测", "失败经验不自动进入下一次默认约束"]],
      ["spec-kit+superpowers", ["规格和方法更完整", "能指导流程，但关键门禁仍要靠操作者盯住", "状态、证据和协作事实分散在多个表面", "多任务协作缺统一程序真值", "失败不一定沉淀成受保护约束"]],
      ["AI-SDLC", ["先冻结工作项，再进入正式执行", "正式产物、执行授权和门禁串成闭环", "最新验证证据决定是否前进", "程序级集成与失败回写进入系统", "更适合持续交付与多人协作"], true],
    ],
  },
  {
    chapter: "start",
    title: "第一次进入这套系统，只需要分清两个入口",
    lead: "终端负责触发流程和查看真值，聊天框负责表达业务需求。把入口分离，才能区分是输入问题、运行问题还是治理问题。",
    note: "先把入口说清楚，再谈命令和工作项。",
    visual: "onboarding",
  },
  {
    chapter: "start",
    title: "第一次上手路径：先看真值，再做安全预演，再提交需求",
    lead: "先看 `adapter status`，再跑 `run --dry-run` 做安全预演，然后回到聊天框提交需求。预演通过，只说明启动路径与门禁预演通过，不构成治理激活证明。",
    note: "这里必须把安全预演的边界说准，不能讲成已经完全接入。",
    visual: "terminal",
  },
  {
    chapter: "start",
    title: "系统会接住你什么：不是多一个命令，而是多一层交付保障",
    lead: "第一次使用最直接的变化，是工作项、产物、验证、总结和失败回写开始进入统一链路，而不是散在聊天记录、本地文件和个人记忆里。",
    note: "收益页不按能力标签分人群，而按角色职责分收益。",
    visual: "benefits",
    cards: [
      ["首次接触者", "更容易知道下一步做什么，失败时也知道卡在哪里。"],
      ["工程实践者", "正式产物、任务边界和最新验证证据让实现更可控。"],
      ["负责人", "能看到真值、门禁和证据，而不是只听“已经完成”。"],
      ["团队协作", "状态与产物沉淀到统一路径，中断和换人都更可恢复。"],
      ["质量保障", "浏览器质量门、收口门和发布约束把假完成挡在前面。"],
      ["系统进化", "失败会回写成规则、工具、评测和缺陷池，而不是消失。"],
    ],
  },
  {
    chapter: "start",
    title: "为什么这些体验背后，必须是一套控制系统",
    lead: "如果没有接入真值、状态机、执行授权、质量门和证据链，前面承诺的“可追溯、可恢复、可治理”都会重新退化成靠人盯、靠人记、靠人补。",
    note: "这是前半段到后半段的桥接页，要让观众自然过渡到系统内部。",
    visual: "bridge",
  },
  {
    chapter: "system",
    title: "系统骨架：谁负责触发，谁负责判定，谁负责阻断，谁负责回写",
    lead: "顺序可以压成 6 步：入口触发，真值暴露，状态保存，门禁阻断，调度分工，证据回闭环。",
    note: "这页不罗列名词，而是明确顺序与因果。",
    visual: "control-flow",
  },
  {
    chapter: "system",
    title: "阶段契约：阶段不是步骤表，而是输入、产物、结论的契约",
    lead: "每个阶段只回答三件事：输入是什么、产物落到哪里、谁给出可执行结论。真正推动状态前进的是通过、重试或停止。",
    note: "把阶段口径和结论口径改回工程上可执行的表达。",
    visual: "pipeline",
  },
  {
    chapter: "system",
    title: "组件地图与调度方式：哪些可以并行，哪些必须先被约束住",
    lead: "先看组件边界，再看并行边界。框架不是为了复杂，而是为了让系统知道什么能并行、什么必须先被约束住。",
    note: "把组件边界和调度边界合并讲，减少并列主题的平铺。",
    visual: "system-stack",
  },
  {
    chapter: "system",
    title: "硬约束：真正不能绕过的，是正式产物、执行授权和最新验证证据",
    lead: "宪章、规范落点、执行授权、质量门和收口门都在表达同一件事：没有被系统接纳的产物，不算正式交付。",
    note: "这一页把约束从“流程规定”讲成“交付定义”。",
    visual: "constraints",
  },
  {
    chapter: "govern",
    title: "观测面：不是多打日志，而是把证据边界诚实暴露给操作者",
    lead: "治理真正关心的是：谁做了什么、当前真值是什么、证据链闭合到哪一步、哪里仍然是未知、部分闭合或尚未观测。能看到缺口，比假装自动化更重要。",
    note: "观测页必须强调边界，而不是把运行观测讲成万能答案。",
    visual: "observability",
  },
  {
    chapter: "govern",
    title: "自迭代优化：失败不是一次性的修补，而是框架能力的输入",
    lead: "一条真实失败链路，应该进入缺陷池、规则、工具、评测和发布约束，直到同类错误在下一次默认被拦住。这才叫框架在变硬，而不是团队在变累。",
    note: "让听众看见失败如何回写为能力，而不是只做总结。",
    visual: "iteration",
  },
  {
    chapter: "govern",
    title: "前端治理案例：先看同一条受控链路，再逐张看证据渲染",
    lead: "这段案例按同一条受控前端链路展开：先看 recommendation 与 effective override，再看只读 handoff 真值面、执行 apply 结果和浏览器质量门 receipts。每张图都来自受控输出的 presentation rendering，而不是原始终端截图墙。",
    note: "先把 recommendation versus effective truth 讲清楚，再进入逐张证据页。",
    visual: "frontend-evidence",
  },
  {
    chapter: "govern",
    title: "证据一：物化 effective truth",
    lead: "`solution-confirm --execute --yes` 会把 recommendation 与 effective truth 一起物化。这里要同时讲清 recommended provider: enterprise-vue2 与 effective provider: public-primevue，后面的 apply 和 gate 才会显得是同一条链。",
    note: "第一张证据页必须把 recommendation versus effective override 讲透。",
    visual: "execution-detail",
    evidence: {
      kicker: "受控输出渲染图",
      title: "python -m ai_sdlc program solution-confirm --execute --yes",
      summary: "先展示 recommendation，再把 requested/effective truth 物化成后续 apply 与 gate 共用的方案快照。",
      image: "./assets/execution-stack.png",
      tags: [
        "recommended: enterprise-vue2",
        "effective: public-primevue",
        "style: modern-saas",
        "preflight: ready",
      ],
    },
  },
  {
    chapter: "govern",
    title: "证据二：只读 handoff 真值面",
    lead: "`page-ui-schema-handoff` 是只读 handoff 真值面，不是 execute surface。它把 effective provider、style pack、theme adapter 和 page schema 交给后续生成与测试链路。",
    note: "第二张证据页要把 read-only handoff boundary 说清楚。",
    visual: "execution-detail",
    evidence: {
      kicker: "只读 handoff 真值面",
      title: "python -m ai_sdlc program page-ui-schema-handoff",
      summary: "这一步不落盘执行，只交接 provider、style pack、组件包与 page/ui schema 的只读真值。",
      image: "./assets/execution-style.png",
      tags: [
        "surface: read-only",
        "provider: public-primevue",
        "style: modern-saas",
        "schema: dashboard/search/wizard",
      ],
    },
  },
  {
    chapter: "govern",
    title: "证据三：execute apply 真正落盘",
    lead: "`managed-delivery-apply --execute` 才是真正的窄执行面。它会执行依赖接入、骨架生成和工作区绑定，同时明确告诉你交付仍未完成，因为浏览器质量门还没跑。",
    note: "第三张证据图要让人一眼看见真实落地文件和 pending browser gate。",
    visual: "execution-detail",
    evidence: {
      kicker: "执行结果渲染图",
      title: "python -m ai_sdlc program managed-delivery-apply --execute --yes --ack-effective-change",
      summary: "这里已经不只是计划，而是实际把 managed frontend 和运行时回执落到了工作区。",
      image: "./assets/execution-apply.png",
      tags: ["apply: pending_browser_gate", "target: managed/frontend", "files: index.html + App.vue", "gate: pending"],
    },
  },
  {
    chapter: "govern",
    title: "证据四：gate receipts passed",
    lead: "当前归档展示的是一次通过的 `browser-gate-probe --execute` receipts。重点不是“跑过浏览器”这句话，而是 smoke、visual、a11y 和 interaction checks 都留下了最新可追溯证据，系统才允许继续声称完成。",
    note: "第四张证据页要强调 latest receipts 和 overall gate verdict。",
    visual: "execution-detail",
    evidence: {
      kicker: "浏览器 gate receipts 渲染图",
      title: "python -m ai_sdlc program browser-gate-probe --execute",
      summary: "质量门 receipts 先落地，再给出 overall gate status；这里展示的是 passed，而不是缺证据时的阻断态。",
      image: "./assets/execution-gate.png",
      tags: ["overall: passed", "smoke: pass", "visual: pass", "a11y/interaction: pass"],
    },
  },
  {
    chapter: "close",
    title: "最后只记住 4 件事：入口、真值、证据、回写",
    lead: "第一次使用，记住入口分离；进入工程阶段，盯住真值和门禁；验收时看证据，不看表述；真实失败要回写成规则与工具。AI-SDLC 不是让 AI 更自由，而是让 AI 在工程轨道上高强度运行。",
    note: "把行动原则和全篇结论合到最后一页，收成一个可复述的结尾。",
    visual: "checklist",
  },
];

const slideRoot = document.querySelector("#slideRoot");
const progressBar = document.querySelector("#progressBar");
const frameCount = document.querySelector("#frameCount");
const speakerNote = document.querySelector("#speakerNote");
const modeChip = document.querySelector("#modeChip");
const chapterChip = document.querySelector("#chapterChip");
const chapterNav = document.querySelector("#chapterNav");
const miniMap = document.querySelector("#miniMap");
const sectionMeter = document.querySelector("#sectionMeter");
const prevButton = document.querySelector("#prevButton");
const nextButton = document.querySelector("#nextButton");
const shell = document.querySelector(".deck-shell");

let current = getInitialSlide();

function getInitialSlide() {
  const param = new URLSearchParams(window.location.search).get("slide");
  const parsed = Number.parseInt(param || "1", 10);
  if (Number.isNaN(parsed) || parsed < 1 || parsed > slides.length) return 0;
  return parsed - 1;
}

function chapterFor(slide) {
  return chapters.find((chapter) => chapter.id === slide.chapter) || chapters[0];
}

function setSlide(next, push = true) {
  const bounded = Math.max(0, Math.min(slides.length - 1, next));
  if (bounded === current && shell.dataset.ready === "true") return;
  current = bounded;
  renderSlide();
  if (push) {
    const url = new URL(window.location.href);
    url.searchParams.set("slide", String(current + 1));
    window.history.replaceState({}, "", url);
  }
}

function renderSlide() {
  const slide = slides[current];
  const chapter = chapterFor(slide);
  slideRoot.classList.add("is-changing");
  slideRoot.scrollTo({ top: 0, left: 0 });
  window.setTimeout(() => {
    slideRoot.innerHTML = buildSlide(slide, chapter);
    slideRoot.scrollTo({ top: 0, left: 0 });
    slideRoot.classList.remove("is-changing");
  }, 80);

  progressBar.style.width = `${((current + 1) / slides.length) * 100}%`;
  frameCount.textContent = `${pad(current + 1)} / ${slides.length}`;
  if (speakerNote) speakerNote.textContent = slide.note;
  modeChip.textContent = chapter.audience;
  chapterChip.textContent = chapter.title;
  prevButton.disabled = current === 0;
  nextButton.disabled = current === slides.length - 1;
  renderNavigation();
  shell.dataset.ready = "true";
}

function pad(value) {
  return String(value).padStart(2, "0");
}

function buildSlide(slide, chapter) {
  const visual = buildVisual(slide);
  const single = [
    "compare",
    "pipeline",
    "constraints",
    "checklist",
    "failures",
    "bridge",
    "control-flow",
    "system-stack",
    "observability",
    "frontend-evidence",
    "execution-detail",
  ].includes(
    slide.visual,
  );
  return `
    <div class="slide-grid ${single ? "single" : ""} visual-${slide.visual}">
      <section>
        <span class="chapter-label">${chapter.audience} · ${chapter.title}</span>
        ${current === 0 ? `<h1>${slide.title}</h1>` : `<h2>${slide.title}</h2>`}
        <p class="lead">${slide.lead}</p>
        ${slide.cards ? buildCards(slide.cards) : ""}
      </section>
      ${visual}
    </div>
  `;
}

function buildCards(cards) {
  const normalized = cards.map((card) => {
    if (card.length === 3) {
      return `<div class="value-card"><small>${card[0]}</small><strong>${card[1]}</strong><p>${card[2]}</p></div>`;
    }
    return `<div class="value-card"><strong>${card[0]}</strong><p>${card[1]}</p></div>`;
  });
  return `<div class="grid-cards">${normalized.join("")}</div>`;
}

function buildVisual(slide) {
  if (slide.visual === "hero") {
    return `<aside class="asset-stage hero-asset">
      <img src="./assets/hero-control-room.png" alt="AI-SDLC 控制室式交付管线主视觉" />
      <div class="asset-overlay">
        <span>需求入口</span>
        <span>受控流水线</span>
        <span>验证证据</span>
      </div>
    </aside>`;
  }

  if (slide.visual === "failures") {
    const failures = [
      ["需求漂移", "需求在聊天里不断变形，最后没人能说清当前到底交付哪一版。"],
      ["上下文断裂", "换窗口、换人、隔天继续时，只能重新解释背景，效率被大量消耗。"],
      ["假完成", "模型说完成了，但测试、浏览器验证、发布门和交付总结可能根本没闭环。"],
      ["失败不复用", "问题散在聊天和个人经验里，下次仍会以同样方式重演。"],
    ];
    return `<section class="failure-grid">
      ${failures
        .map(
          ([title, text], index) => `<div class="failure-card">
            <small>0${index + 1}</small><strong>${title}</strong><p>${text}</p>
          </div>`,
        )
        .join("")}
      <div class="failure-beam">
        <span>没有统一框架时，问题不是单点错误，而是整条交付链持续失去真值。</span>
      </div>
    </section>`;
  }

  if (slide.visual === "compare") {
    return `<section class="compare-grid">${slide.compare
      .map(
        ([title, items, primary]) => `<div class="compare-card ${primary ? "is-primary" : ""}">
          <h3>${title}</h3>
          <ul>${items.map((item) => `<li>${item}</li>`).join("")}</ul>
        </div>`,
      )
      .join("")}</section>`;
  }

  if (slide.visual === "terminal") {
    return `<aside class="terminal-card">
      <div class="terminal-top"><span></span><span></span><span></span></div>
      <pre><code># 先看接入真值
ai-sdlc adapter status
  状态: 已物化 / 已验证加载 / 降级运行 / 当前不支持

# 安全预演入口
ai-sdlc run --dry-run
  收口阶段: 通过

# 这不构成治理激活证明
# 它只说明启动路径与门禁预演通过

# 裸命令不可用时，用 Python 模块入口
python -m ai_sdlc run --dry-run

# 然后回到聊天框提交业务需求
“我想把客服工单转成可追踪的交付流水线...”</code></pre>
    </aside>`;
  }

  if (slide.visual === "onboarding") {
    const steps = [
      ["终端", "触发 `adapter status`、`run --dry-run`、`stage show` 等流程命令。"],
      ["聊天框", "表达业务意图、约束、验收预期，不夹带终端控制命令。"],
      ["系统", "把需求接成工作项、任务、产物、验证与总结链路。"],
    ];
    return `<section class="entry-split">
      <div class="entry-panel">
        <small>命令入口</small><strong>终端入口</strong><p>负责触发流程、查看真值、执行安全预演和调取阶段信息。</p>
      </div>
      <div class="entry-divider">→</div>
      <div class="entry-panel accent">
        <small>需求入口</small><strong>需求入口</strong><p>负责表达业务需求、范围边界、验收口径和上下文补充。</p>
      </div>
      <div class="entry-strip">
        ${steps
          .map(
            ([name, text]) => `<div class="entry-step"><strong>${name}</strong><p>${text}</p></div>`,
          )
          .join("")}
      </div>
    </section>`;
  }

  if (slide.visual === "ladder") {
    const steps = [
      ["01", "确认入口文件", "AGENTS.md 是 Codex adapter 的标准入口文件。"],
      ["02", "检查接入真值", "adapter status 会区分已物化、已验证加载、降级运行、当前不支持。"],
      ["03", "安全预演", "run --dry-run 只证明命令链路预演成功，不证明治理激活。"],
      ["04", "回到聊天框", "用自然语言说需求，不把终端命令粘进聊天框。"],
      ["05", "生成工作项", "需求落成规格、计划、任务和执行记录。"],
      ["06", "进入交付流程", "后续由阶段契约、门禁和证据链继续约束。"],
    ];
    return `<aside class="image-with-steps">
      <div class="asset-stage compact">
        <img src="./assets/delivery-assembly-line.png" alt="AI-SDLC 从需求到验证证据的交付流水线视觉" />
      </div>
      <div class="ladder">${steps
        .map(
          ([num, name, text]) => `<div class="ladder-step"><span>${num}</span><div><strong>${name}</strong><p>${text}</p></div></div>`,
        )
        .join("")}</div>
    </aside>`;
  }

  if (slide.visual === "benefits") {
    const benefits = [
      ["01 / 首次接触者", "第一次接触这套系统的人，会更快分清入口、工作项和阶段真值。"],
      ["02 / 工程实践者", "工程实践者能把正式产物、任务边界和最新验证证据接成闭环。"],
      ["03 / 负责人", "负责人看到的是门禁和证据，而不是只听一段完成描述。"],
    ];
    return `<aside class="holo-panel benefits-panel">
      <div class="benefits-hud" aria-hidden="true">
        <span>ENTRY TRUTH</span>
        <span>WORK ITEM</span>
        <span>FRESH EVIDENCE</span>
      </div>
      <div class="benefits-grid">
        ${benefits
          .map(
            ([label, text]) => `<div class="benefit-card">
              <small>${label}</small>
              <p>${text}</p>
            </div>`,
          )
          .join("")}
      </div>
    </aside>`;
  }

  if (slide.visual === "bridge") {
    return `<section class="bridge-stage">
      <div class="bridge-copy">
        <small>为什么必须有这套系统</small>
        <strong>前半段承诺的是体验，后半段兜底的是控制系统</strong>
        <p>没有入口真值、工作项冻结、执行授权、质量门和失败回写，所谓“更稳的交付”仍会退化回人工补位。</p>
      </div>
      <div class="bridge-alert">
        <strong>桥接判断</strong>
        <p>这一页不是重复收益，而是把“体验为什么能被兜住”明确转译成可执行的控制面。</p>
      </div>
      <div class="bridge-grid">
        <article class="bridge-lane">
          <small>入口层</small>
          <strong>先分清谁在表达需求，谁在触发流程</strong>
          <p>聊天框只负责业务意图，终端只负责真值与入口命令，避免输入面和运行面混写。</p>
        </article>
        <article class="bridge-lane">
          <small>执行层</small>
          <strong>把“可以继续”改写成状态、授权与门禁</strong>
          <p>不是模型说能做就能做，而是工作项、任务边界和执行面一起决定是否允许进入正式实现。</p>
        </article>
        <article class="bridge-lane">
          <small>闭环层</small>
          <strong>把“已经完成”改写成最新证据与失败回写</strong>
          <p>没有最新验证证据就不能收口；真实失败还要继续回写成规则、工具和评测。</p>
        </article>
      </div>
      <div class="bridge-flow">
        <span>入口真值</span>
        <span>工作项冻结</span>
        <span>执行授权</span>
        <span>质量门</span>
        <span>最新证据</span>
        <span>失败回写</span>
      </div>
    </section>`;
  }

  if (slide.visual === "control-flow") {
    const flow = [
      ["入口", "命令入口", "触发 run、stage、adapter、verify 等流程命令。"],
      ["真值", "接入真值", "报告当前是已物化、已验证加载、降级运行还是当前不支持。"],
      ["状态", "状态机", "保存阶段位置、产物路径和可恢复的推进真值。"],
      ["阻断", "门禁与约束", "执行授权、质量门、发布门决定是否允许继续。"],
      ["调度", "调度器", "决定串行、批内并行还是 Agent 级并行。"],
      ["闭环", "证据与回写", "收集最新验证证据，并把失败回写为规则和评测。"],
    ];
    return `<section class="control-flow">
      <div class="control-rail" aria-hidden="true"></div>
      ${flow
        .map(
          ([tag, title, text]) => `<div class="flow-card">
            <small>${tag}</small><strong>${title}</strong><p>${text}</p>
          </div>`,
        )
        .join("")}
    </section>`;
  }

  if (slide.visual === "pipeline") {
    const stages = [
      ["01", "初始化", "输入：仓库与入口文件", "产物：配置与接入状态", "门禁 / 结论：入口真值可解释"],
      ["02", "澄清", "输入：自然语言需求", "产物：问题边界与验收口径", "门禁 / 结论：是否进入设计"],
      ["03", "设计", "输入：冻结需求", "产物：方案与架构取舍", "门禁 / 结论：风险是否显式"],
      ["04", "拆解", "输入：设计方案", "产物：任务、依赖、文件边界", "门禁 / 结论：是否可授权执行"],
      ["05", "验证", "输入：计划与约束", "产物：验证策略与预检结果", "门禁 / 结论：是否允许进入执行"],
      ["06", "执行", "输入：已授权任务", "产物：代码、日志、正式产物、最新验证证据", "门禁 / 结论：通过 / 重试 / 停止"],
      ["07", "收口", "输入：通过的交付链", "产物：总结、归档、失败回写", "门禁 / 结论：收口门是否允许声明完成"],
    ];
    return `<section>
      <div class="contract-grid">${stages
        .map(
          ([num, name, input, output, gate]) => `<div class="contract-card">
            <span>${num}</span><strong>${name}</strong><p>${input}</p><p>${output}</p><p>${gate}</p>
          </div>`,
        )
        .join("")}</div>
      <div class="spec-strip">
        <span class="spec-tag">阶段契约 = 输入 + 产物 + 结论</span>
        <span class="spec-tag">结论必须来自真实门禁，而不是主观感觉</span>
        <span class="spec-tag">最新验证证据决定是否推进</span>
        <span class="spec-tag">收口门之前不能声称完成</span>
      </div>
    </section>`;
  }

  if (slide.visual === "system-stack") {
    const cards = [
      ["规则与模板", "规定规格、计划、任务、执行记录与总结的结构。"],
      ["正式产物", "把正式产物固定到规范落点，而不是散在聊天与桌面。"],
      ["执行授权", "没有授权任务，不进入正式实现阶段。"],
      ["程序级集成", "总集成负责最后收口，不能替代单个任务的执行真值。"],
      ["前端语义内核", "把页面、组件、状态、交互和验收点变成治理对象。"],
      ["反馈回写", "把失败沉淀为规则、工具、评测和发布约束。"],
    ];
    return `<section class="system-grid">
      <div class="system-band">
        <span>组件边界先回答“系统由哪些约束面构成”</span>
        <span>调度方式再回答“在什么条件下才允许并行”</span>
      </div>
      ${cards
        .map(
          ([title, text]) => `<div class="system-card"><strong>${title}</strong><p>${text}</p></div>`,
        )
        .join("")}
      <div class="timeline dispatch-lane">
        <div class="timeline-step"><span>串行</span><div><strong>默认路径</strong><p>共享文件多、依赖强时，用单 Agent 串行保证可控。</p></div></div>
        <div class="timeline-step"><span>批内</span><div><strong>同主控拆分</strong><p>仍在单执行流内推进，只把内部步骤拆成可并行的小批次。</p></div></div>
        <div class="timeline-step"><span>多 Agent</span><div><strong>四重隔离后并行</strong><p>文件、接口、数据、测试隔离成立，才允许 Agent 级并行。</p></div></div>
      </div>
    </section>`;
  }

  if (slide.visual === "constraints") {
    const cards = [
      ["宪章至上", "生成产物前必须符合宪章里的强制规则。"],
      ["阶段门禁", "不能跳阶段，失败必须先修复或阻断。"],
      ["验证铁律", "没有新鲜验证证据，不能声称完成。"],
      ["目标落点", "正式规格、计划、任务必须写入规范工作项路径。"],
      ["执行授权", "规格和计划冻结不等于允许执行，缺任务不能开做。"],
      ["分支与归档", "执行日志和收口总结是交付事实的一部分。"],
    ];
    return `<section class="constraint-grid">${cards
      .map(([title, text]) => `<div class="constraint-card"><small>硬约束</small><strong>${title}</strong><p>${text}</p></div>`)
      .join("")}</section>`;
  }

  if (slide.visual === "observability") {
    return `<section class="observability-grid">
      <div class="proof-card" data-index="真"><strong>当前真值</strong><p>先分清已物化、已验证加载、降级运行、当前不支持，再决定后续动作。</p></div>
      <div class="proof-card" data-index="证"><strong>证据闭合</strong><p>证据不是“有日志”，而是能解释状态、产物和验证之间的来源关系。</p></div>
      <div class="proof-card" data-index="边"><strong>边界暴露</strong><p>未知、部分闭合、尚未观测都要被诚实展示，不能假装已经闭环。</p></div>
      <div class="proof-card" data-index="操"><strong>操作者视角</strong><p>观测面要帮助人判断下一步，而不是制造更多需要人工解读的噪声。</p></div>
      <div class="observability-board">
        <span>运行观测</span>
        <span>状态表面</span>
        <span>操作者报告</span>
        <span>证据闭合</span>
      </div>
    </section>`;
  }

  if (slide.visual === "iteration") {
    return `<section class="timeline">
      <div class="timeline-step"><span>观察</span><div><strong>门禁或用户发现问题</strong><p>例如假完成、错误落点、跳过执行授权。</p></div></div>
      <div class="timeline-step"><span>记录</span><div><strong>写入框架缺陷池</strong><p>记录现象、根因、风险、证据、可验证成功标准。</p></div></div>
      <div class="timeline-step"><span>加固</span><div><strong>沉淀为规则、流程、工具、评测</strong><p>把一次纠偏变成下次默认拦截。</p></div></div>
      <div class="timeline-step"><span>发布</span><div><strong>进入版本和文档收口</strong><p>说明文档、发布说明、离线包、用户手册必须一致。</p></div></div>
    </section>`;
  }

  if (slide.visual === "frontend-evidence") {
    const steps = [
      [
        "01",
        "技术栈推荐",
        "先跑 solution-confirm，冻结推荐栈、provider、style pack，并给出是否回退的预检结论。",
      ],
      [
        "02",
        "组件库与风格冻结",
        "再跑 page-ui-schema-handoff，把组件包、主题桥接和页面 schema 交接给生成链路。",
      ],
      [
        "03",
        "组件接入与工程落地",
        "managed-delivery-apply --execute 真正接入依赖、生成骨架、绑定工作区。",
      ],
      [
        "04",
        "浏览器质量门",
        "browser-gate-probe --execute 决定是否允许继续往下收口，而不是事后补截图。",
      ],
    ];
    return `<section class="route-grid">${steps
      .map(
        ([index, title, text]) => `<div class="route-card">
          <small>步骤 ${index}</small>
          <strong>${title}</strong>
          <p>${text}</p>
        </div>`,
      )
      .join("")}</section>`;
  }

  if (slide.visual === "execution-detail") {
    return `<figure class="execution-detail-figure">
      <div class="execution-detail-top">
        <small>${slide.evidence.kicker}</small>
        <strong>${slide.evidence.title}</strong>
        <p>${slide.evidence.summary}</p>
      </div>
      <img src="${slide.evidence.image}" alt="${slide.title}" />
      <figcaption>
        <div class="execution-detail-tags">${slide.evidence.tags
          .map((tag) => `<span>${tag}</span>`)
          .join("")}</div>
      </figcaption>
    </figure>`;
  }

  if (slide.visual === "checklist") {
    const cards = [
      ["入门使用者", "记住：终端跑命令，聊天框说需求；`run --dry-run` 是启动预演，不构成治理激活证明。"],
      ["工程实践者", "记住：所有实现都要落到工作项、任务边界、验证证据。"],
      ["架构", "记住：扩展组件时优先补模型、门禁、模板和测试。"],
      ["负责人", "记住：看门禁和证据，不只看 Agent 的完成描述。"],
    ];
    return `<section>
      <div class="close-statement">
        <small>压轴结论</small>
        <strong>先过真值、授权与证据，再允许自己说“完成”。</strong>
        <p>AI-SDLC 不是把 AI 包装得更会说，而是把交付链变成可验证、可阻断、可回写的系统行为。</p>
      </div>
      <div class="check-grid">${cards
        .map(([title, text]) => `<div class="check-card"><small>角色</small><strong>${title}</strong><p>${text}</p></div>`)
        .join("")}</div>
    </section>`;
  }

  return `<aside class="holo-panel">
    <div class="proof-stack">
      <div class="proof-card" data-index="1"><strong>约束不是刹车</strong><p>它让 AI 的速度不会变成返工。</p></div>
      <div class="proof-card" data-index="2"><strong>证据不是文档癖</strong><p>它让团队能判断完成到底是真是假。</p></div>
      <div class="proof-card" data-index="3"><strong>失败不是浪费</strong><p>它是下一次自动变好的原材料。</p></div>
    </div>
  </aside>`;
}

function renderNavigation() {
  chapterNav.innerHTML = chapters
    .map((chapter, index) => {
      const firstIndex = slides.findIndex((slide) => slide.chapter === chapter.id);
      const active = chapter.id === slides[current].chapter;
      return `<button class="chapter-button ${active ? "is-active" : ""}" type="button" data-slide="${firstIndex}">
        <span>${pad(index + 1)}</span><strong>${chapter.title}</strong>
      </button>`;
    })
    .join("");

  if (miniMap) {
    miniMap.innerHTML = slides
      .map(
        (_, index) =>
          `<button type="button" class="${index === current ? "is-active" : ""}" data-slide="${index}" aria-label="跳到第 ${index + 1} 页"></button>`,
      )
      .join("");
  }

  sectionMeter.innerHTML = slides
    .map((_, index) => `<span class="${index === current ? "is-active" : ""}"></span>`)
    .join("");

  document.querySelectorAll("[data-slide]").forEach((button) => {
    button.addEventListener("click", () => setSlide(Number(button.dataset.slide)));
  });
}

prevButton.addEventListener("click", () => setSlide(current - 1));
nextButton.addEventListener("click", () => setSlide(current + 1));

window.addEventListener("keydown", (event) => {
  const keys = ["ArrowRight", "PageDown", " ", "ArrowLeft", "PageUp", "Home", "End"];
  if (!keys.includes(event.key)) return;
  event.preventDefault();
  if (event.key === "ArrowRight" || event.key === "PageDown" || event.key === " ") setSlide(current + 1);
  if (event.key === "ArrowLeft" || event.key === "PageUp") setSlide(current - 1);
  if (event.key === "Home") setSlide(0);
  if (event.key === "End") setSlide(slides.length - 1);
});

function startCanvas() {
  const canvas = document.querySelector("#signalCanvas");
  const context = canvas.getContext("2d");
  let width = 0;
  let height = 0;
  let points = [];

  function resize() {
    width = canvas.width = window.innerWidth * window.devicePixelRatio;
    height = canvas.height = window.innerHeight * window.devicePixelRatio;
    canvas.style.width = `${window.innerWidth}px`;
    canvas.style.height = `${window.innerHeight}px`;
    points = Array.from({ length: Math.min(70, Math.floor(window.innerWidth / 18)) }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.32 * window.devicePixelRatio,
      vy: (Math.random() - 0.5) * 0.32 * window.devicePixelRatio,
    }));
  }

  function tick() {
    context.clearRect(0, 0, width, height);
    context.lineWidth = window.devicePixelRatio;
    points.forEach((point, index) => {
      point.x += point.vx;
      point.y += point.vy;
      if (point.x < 0 || point.x > width) point.vx *= -1;
      if (point.y < 0 || point.y > height) point.vy *= -1;

      context.fillStyle = "rgba(77, 233, 255, 0.42)";
      context.beginPath();
      context.arc(point.x, point.y, 1.6 * window.devicePixelRatio, 0, Math.PI * 2);
      context.fill();

      for (let next = index + 1; next < points.length; next += 1) {
        const other = points[next];
        const distance = Math.hypot(point.x - other.x, point.y - other.y);
        if (distance < 170 * window.devicePixelRatio) {
          context.strokeStyle = `rgba(77, 233, 255, ${0.12 * (1 - distance / (170 * window.devicePixelRatio))})`;
          context.beginPath();
          context.moveTo(point.x, point.y);
          context.lineTo(other.x, other.y);
          context.stroke();
        }
      }
    });
    window.requestAnimationFrame(tick);
  }

  resize();
  window.addEventListener("resize", resize);
  tick();
}

startCanvas();
setSlide(current, false);
