const byId = (id) => document.getElementById(id);
const API = Object.freeze({
  overview: "/api/overview",
  movieProtocols: "/api/movie-protocols",
  collection: "/api/collection",
  factory: "/api/factory",
  retry: "/api/retry",
  session: "/api/session",
});

async function request(url, options = {}) {
  const response = await fetch(url, options);
  const payload = await response.json();
  if (!response.ok)
    throw new Error(payload.detail || "The experiment could not run");
  return payload;
}

function post(url, body) {
  return request(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

function escapeHtml(value) {
  const element = document.createElement("div");
  element.textContent = String(value);
  return element.innerHTML;
}

function renderError(target, error) {
  target.classList.remove("empty");
  target.innerHTML = `<div class="event failure">${escapeHtml(error.message)}</div>`;
}

async function loadGuides() {
  const { guides } = await request(API.overview);
  byId("guide-grid").innerHTML = guides
    .map(
      (guide, index) => `
    <article class="guide-card">
      <button type="button" aria-expanded="false">
        <span class="number">0${index + 1}</span>
        <h3>${escapeHtml(guide.label)}</h3>
        <span class="file">${escapeHtml(guide.file)}</span>
        <span class="open-label">Open explanation +</span>
      </button>
      <div class="guide-details">
        <strong>Methods involved</strong>
        <div class="method-pills">${guide.methods.map((method) => `<code>${escapeHtml(method)}</code>`).join("")}</div>
        <strong>What happens</strong><p>${escapeHtml(guide.meaning)}</p>
        <strong>Why it matters</strong><p>${escapeHtml(guide.outcome)}</p>
      </div>
    </article>`,
    )
    .join("");
  document.querySelectorAll(".guide-card button").forEach((button) => {
    button.addEventListener("click", () => {
      const card = button.closest(".guide-card");
      const expanded = card.classList.toggle("expanded");
      button.setAttribute("aria-expanded", String(expanded));
      card.querySelector(".open-label").textContent = expanded
        ? "Close explanation −"
        : "Open explanation +";
    });
  });
}

byId("inspect-movie").addEventListener("click", async () => {
  const target = byId("movie-output");
  try {
    const data = await request(API.movieProtocols);
    target.classList.remove("empty");
    target.innerHTML = `
      <div class="result-card"><span>repr(movie) → __repr__</span><code>${escapeHtml(data.selected.repr)}</code></div>
      <div class="result-card"><span>str(movie) → __str__</span><strong>${escapeHtml(data.selected.str)}</strong></div>
      <div class="result-card wide"><span>sorted(movies) → __lt__ + total_ordering</span><ol class="result-list">${data.sorted.map((movie) => `<li>${escapeHtml(movie)}</li>`).join("")}</ol></div>
      <div class="result-card"><span>set(movies) → __hash__ + __eq__</span><strong>${data.sourceCount} inputs → ${data.setCount} unique</strong><small> identity: ${escapeHtml(data.identityRule)}</small></div>
      <div class="result-card"><span>ratings[movie] → __hash__</span><strong>${data.dictionaryLookup}</strong></div>`;
  } catch (error) {
    renderError(target, error);
  }
});

byId("run-collection").addEventListener("click", async () => {
  const target = byId("collection-output");
  try {
    const data = await post(API.collection, {
      operation: byId("collection-operation").value,
    });
    const result = Array.isArray(data.result)
      ? `<ol class="result-list">${data.result.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ol>`
      : `<strong>${escapeHtml(data.result)}</strong>`;
    target.classList.remove("empty");
    target.innerHTML = `<div class="dispatch"><div class="dispatch-box"><span>Python syntax</span><code>${escapeHtml(data.expression)}</code></div><b class="dispatch-arrow">→</b><div class="dispatch-box"><span>Dispatches to</span><code>${escapeHtml(data.method)}</code></div><b class="dispatch-arrow">→</b><div class="dispatch-box"><span>Returned value</span>${result}</div></div>`;
  } catch (error) {
    renderError(target, error);
  }
});

byId("factory-source").addEventListener("change", ({ target }) => {
  byId("factory-data").value =
    target.value === "csv"
      ? "Arrival,2016,Denis Villeneuve,Science fiction,7.9"
      : "Arrival | 2016 | Denis Villeneuve | Science fiction | 7.9";
});

byId("run-factory").addEventListener("click", async () => {
  const target = byId("factory-output");
  const source = byId("factory-source").value;
  const raw = byId("factory-data").value;
  const values = raw.split("|").map((value) => value.trim());
  const payload =
    source === "csv"
      ? { source, premium: byId("factory-premium").checked, csv_line: raw }
      : {
          source,
          premium: byId("factory-premium").checked,
          title: values[0],
          year: Number(values[1]),
          director: values[2],
          genre: values[3],
          rating: Number(values[4]),
        };
  try {
    const data = await post(API.factory, payload);
    target.classList.remove("empty");
    target.innerHTML = `<div class="dispatch"><div class="dispatch-box"><span>Factory call</span><code>${escapeHtml(data.constructor)}(...)</code></div><b class="dispatch-arrow">→</b><div class="dispatch-box"><span>cls resolves to</span><strong>${escapeHtml(data.type)}</strong></div><b class="dispatch-arrow">→</b><div class="dispatch-box"><span>Created object</span><strong>${escapeHtml(data.display)}</strong></div></div><details class="repr-details"><summary>Show full developer representation</summary><code>${escapeHtml(data.repr)}</code></details>`;
  } catch (error) {
    renderError(target, error);
  }
});

for (const [inputId, outputId] of [
  ["failure-count", "failure-value"],
  ["attempt-count", "attempt-value"],
]) {
  byId(inputId).addEventListener("input", ({ target }) => {
    byId(outputId).value = target.value;
  });
}

byId("run-retry").addEventListener("click", async () => {
  const target = byId("retry-output");
  const failures = Number(byId("failure-count").value);
  const attempts = Number(byId("attempt-count").value);
  try {
    const data = await post(API.retry, {
      failures_before_success: failures,
      max_attempts: attempts,
    });
    const events = data.events
      .map((event) => `<div class="event">${escapeHtml(event)}</div>`)
      .join("");
    const outcomeClass = data.status === "completed" ? "success" : "failure";
    const successfulAttempt = failures + 1;
    const reason =
      attempts >= successfulAttempt
        ? `The function is configured to fail ${failures} time${failures === 1 ? "" : "s"}. Attempt ${successfulAttempt} reaches the success branch, so the retry budget of ${attempts} is enough`
        : `Success would require attempt ${successfulAttempt}, but @retry stops after attempt ${attempts}. Every allowed call failed, so it raises RuntimeError`;
    target.classList.remove("empty");
    target.innerHTML = `<div class="retry-reason"><strong>Why this result</strong><br>${escapeHtml(reason)}</div>${events}<div class="event ${outcomeClass}">${escapeHtml(data.status)}: ${escapeHtml(data.result)}</div><div class="event">@timed measured the complete retry cycle in ${escapeHtml(data.elapsedMilliseconds)} ms</div><div class="event">@wraps kept __name__ = ${escapeHtml(data.functionName)} and __doc__ = ${escapeHtml(data.documentation)}</div>`;
  } catch (error) {
    renderError(target, error);
  }
});

byId("run-session").addEventListener("click", async () => {
  const target = byId("session-output");
  const movieIndexes = [
    ...document.querySelectorAll('[name="session-movie"]:checked'),
  ].map((input) => Number(input.value));
  try {
    const data = await post(API.session, { movie_indexes: movieIndexes });
    target.classList.remove("empty");
    target.innerHTML = `${data.events.map((event, index) => `<div class="timeline-item"><span>${index === 0 ? "__enter__" : index === data.events.length - 1 ? "__exit__" : "session.add"}</span>${escapeHtml(event)}</div>`).join("")}<div class="singleton-result"><code>MovieCache() is MovieCache()</code><br><strong>${data.sameCache}</strong> · ${data.cachedCount} cached movies</div>`;
  } catch (error) {
    renderError(target, error);
  }
});

loadGuides().catch((error) => renderError(byId("guide-grid"), error));
