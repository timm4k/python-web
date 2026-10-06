const API = Object.freeze({
  eventLoop: "/api/v1/experiments/event-loop",
  grouping: "/api/v1/experiments/task-grouping",
  race: "/api/v1/experiments/race-condition",
  semaphore: "/api/v1/experiments/semaphore",
  config: "/api/v1/experiments/validate-config",
  books: "/api/v1/books",
  ioSync: "/api/v1/benchmark/io-bound-sync",
  ioAsync: "/api/v1/benchmark/io-bound-async",
});

const DEMO_DATA = Object.freeze({
  config: {
    service_name: "vitamin-analysis-service",
    environment: "production",
    debug_mode: false,
    database: {
      host: "192.168.1.100",
      port: 5432,
      database_name: "vitamin_results",
      credentials: { username: "lab_admin", password: "strong-password" },
    },
    redis: { connection_url: "redis://localhost:6379", ttl_seconds: 3600 },
    admin_emails: ["quality@vitalab.example", "support@vitalab.example"],
    secret_key: "local-demonstration-secret-key-123456789",
  },
  book: {
    title: "Clinical Biochemistry Handbook",
    author: "VitaTrace Reference Team",
    isbn: "978-0-1234-5678-9",
    year: 2025,
    available_copies: 3,
  },
  benchmarkRequestCount: 10,
});

async function request(url, options) {
  const response = await fetch(url, options);
  const payload = response.status === 204 ? null : await response.json();
  if (!response.ok) {
    const detail = payload?.detail ?? `Request failed with ${response.status}`;
    const error = new Error(
      typeof detail === "string" ? detail : JSON.stringify(detail, null, 2),
    );
    error.status = response.status;
    throw error;
  }
  return payload;
}

function renderMetrics(target, items, note) {
  const row = document.createElement("div");
  row.className = "metric-row";
  for (const [label, value] of items) {
    const metric = document.createElement("span");
    const number = document.createElement("b");
    number.textContent = value;
    metric.append(number, label);
    row.append(metric);
  }
  const explanation = document.createElement("small");
  explanation.className = "result-note";
  explanation.textContent = note;
  target.replaceChildren(row, explanation);
}

function bindButton(buttonSelector, targetSelector, operation, render) {
  const button = document.querySelector(buttonSelector);
  const target = document.querySelector(targetSelector);
  button.addEventListener("click", async () => {
    button.disabled = true;
    try {
      render(target, await operation());
    } catch (error) {
      target.textContent = `HTTP ${error.status ?? "error"} · ${error.message}`;
    } finally {
      button.disabled = false;
    }
  });
}

async function measureBatch(endpoint, count) {
  const started = performance.now();
  await Promise.all(Array.from({ length: count }, () => request(endpoint)));
  return (performance.now() - started) / 1000;
}

bindButton(
  "#run-event-loop",
  "#event-loop-result",
  () => request(API.eventLoop),
  (target, data) =>
    renderMetrics(
      target,
      [
        ["sequential", `${data.sequential_seconds}s`],
        ["concurrent", `${data.concurrent_seconds}s`],
        ["speed-up", `${data.speedup}×`],
      ],
      data.explanation,
    ),
);

bindButton(
  "#run-race",
  "#race-result",
  () => request(API.race),
  (target, data) =>
    renderMetrics(
      target,
      [
        ["without lock", `${data.unsafe_balance} µL`],
        ["with lock", `${data.safe_balance} µL`],
        ["approved", data.approved_with_lock],
      ],
      data.explanation,
    ),
);

bindButton(
  "#run-semaphore",
  "#semaphore-result",
  () => request(API.semaphore),
  (target, data) =>
    renderMetrics(
      target,
      [
        ["unlimited peak", data.unlimited_peak],
        ["limited peak", data.limited_peak],
        ["limited time", `${data.limited_seconds}s`],
      ],
      data.explanation,
    ),
);

document
  .querySelector("#grouping-form")
  .addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = event.currentTarget.querySelector("button");
    const target = document.querySelector("#grouping-result");
    const strategy = new FormData(event.currentTarget).get("strategy");
    button.disabled = true;
    try {
      const data = await request(
        `${API.grouping}?strategy=${encodeURIComponent(strategy)}`,
      );
      renderMetrics(
        target,
        [
          ["completed", data.completed],
          ["errors", data.errors],
          ["cancelled", data.cancelled],
        ],
        data.behavior,
      );
    } catch (error) {
      target.textContent = `HTTP ${error.status ?? "error"} · ${error.message}`;
    } finally {
      button.disabled = false;
    }
  });

function configForScenario(scenario) {
  const payload = structuredClone(DEMO_DATA.config);
  if (scenario === "debug") payload.debug_mode = true;
  if (scenario === "invalid") {
    payload.admin_emails = ["not-an-email"];
    payload.secret_key = "short";
  }
  return payload;
}

function selectedConfig() {
  const selected = new FormData(document.querySelector("#config-form")).get(
    "scenario",
  );
  return configForScenario(selected);
}

function showConfigInput() {
  document.querySelector("#config-input").textContent = JSON.stringify(
    selectedConfig(),
    null,
    2,
  );
}

document
  .querySelector("#config-form")
  .addEventListener("change", showConfigInput);
showConfigInput();

document
  .querySelector("#config-form")
  .addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = event.currentTarget.querySelector("button");
    const target = document.querySelector("#config-result");
    button.disabled = true;
    try {
      const data = await request(API.config, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(selectedConfig()),
      });
      target.textContent = `HTTP 200\n${JSON.stringify(data, null, 2)}`;
    } catch (error) {
      target.textContent = `HTTP ${error.status ?? "error"}\n${error.message}`;
    } finally {
      button.disabled = false;
    }
  });

bindButton(
  "#create-book",
  "#book-result",
  () =>
    request(API.books, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(DEMO_DATA.book),
    }),
  (target, data) => {
    target.textContent = `201 · Book ${data.id}: ${data.title}`;
  },
);

bindButton(
  "#filter-books",
  "#filter-result",
  () => request(`${API.books}?available_only=true&limit=10`),
  (target, data) => {
    target.textContent = `200 · ${data.length} available book${data.length === 1 ? "" : "s"}`;
  },
);

bindButton(
  "#run-benchmark",
  "#benchmark-result",
  async () => ({
    syncSeconds: await measureBatch(
      API.ioSync,
      DEMO_DATA.benchmarkRequestCount,
    ),
    asyncSeconds: await measureBatch(
      API.ioAsync,
      DEMO_DATA.benchmarkRequestCount,
    ),
  }),
  (target, data) =>
    renderMetrics(
      target,
      [
        ["sync batch", `${data.syncSeconds.toFixed(2)}s`],
        ["async batch", `${data.asyncSeconds.toFixed(2)}s`],
        ["requests each", DEMO_DATA.benchmarkRequestCount],
      ],
      "Both approaches keep the event loop responsive: sync uses worker threads, async yields directly",
    ),
);
