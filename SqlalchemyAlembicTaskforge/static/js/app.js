const API = Object.freeze({ users: "/users", tags: "/tags", tasks: "/tasks" });
const state = { users: [], tags: [], tasks: [] };

async function request(url, options = {}) {
  const response = await fetch(url, options);
  const payload = response.status === 204 ? null : await response.json();
  if (!response.ok) {
    const detail = Array.isArray(payload?.detail)
      ? payload.detail
          .map((item) => `${item.loc.slice(1).join(".")}: ${item.msg}`)
          .join(" · ")
      : payload?.detail;
    throw new Error(detail || `HTTP ${response.status}`);
  }
  return payload;
}

function jsonOptions(payload, method = "POST") {
  return {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  };
}

function showResult(message, type = "success") {
  const target = document.querySelector("#action-result");
  target.textContent = message;
  target.className = `result-panel ${type}`;
}

function populateSelects() {
  const owner = document.querySelector("#owner-select");
  const tags = document.querySelector("#tag-select");
  const selectedOwner = owner.value;
  const selectedTags = new Set(
    Array.from(tags.selectedOptions, (option) => option.value),
  );
  owner.replaceChildren(
    new Option("Choose a saved musician", ""),
    ...state.users.map((user) => new Option(user.username, user.id)),
  );
  owner.value = state.users.some((user) => String(user.id) === selectedOwner)
    ? selectedOwner
    : "";
  tags.replaceChildren(
    ...state.tags.map((tag) => new Option(tag.name, tag.id)),
  );
  for (const option of tags.options)
    option.selected = selectedTags.has(option.value);
  document.querySelector('#task-form button[type="submit"]').disabled =
    state.users.length === 0;
  renderSavedItems(
    "#musician-roster",
    state.users.map((user) => user.username),
    "No musicians yet — register one to assign tasks",
  );
  renderSavedItems(
    "#available-tags",
    state.tags.map((tag) => tag.name),
    "No tags yet — add one or apply the seed migration",
  );
}

function renderSavedItems(selector, values, emptyMessage) {
  const target = document.querySelector(selector);
  target.replaceChildren();
  for (const value of values) {
    const label = document.createElement("span");
    label.textContent = value;
    target.append(label);
  }
  if (!values.length) target.textContent = emptyMessage;
}

function nextStatus(status) {
  return { todo: "in_progress", in_progress: "done", done: "todo" }[status];
}

function renderBoard() {
  for (const status of ["todo", "in_progress", "done"]) {
    const lane = document.querySelector(`[data-status="${status}"] .task-list`);
    lane.replaceChildren();
    const tasks = state.tasks.filter((task) => task.status === status);
    const countId =
      status === "in_progress" ? "progress-count" : `${status}-count`;
    document.querySelector(`#${countId}`).textContent = tasks.length;
    if (!tasks.length) {
      const empty = document.createElement("p");
      empty.className = "field-help";
      empty.textContent = "No production tasks in this stage";
      lane.append(empty);
    }
    for (const task of tasks) {
      const card = document.createElement("article");
      card.className = "task-card";
      card.innerHTML =
        '<h3></h3><p></p><div class="tags"></div><footer><small></small><button type="button" class="move-task">Move →</button><button type="button" class="delete-task">Delete</button></footer>';
      for (const tag of task.tags) {
        const label = document.createElement("span");
        label.textContent = tag.name;
        card.querySelector(".tags").append(label);
      }
      card.querySelector("h3").textContent = task.title;
      card.querySelector("p").textContent =
        task.description || "No production note";
      card.querySelector("small").textContent =
        `${task.owner.username} · P${task.priority}${task.due_date ? ` · Due ${task.due_date}` : ""}`;
      card.querySelector(".move-task").addEventListener("click", (event) =>
        runAction(event.currentTarget, async () => {
          await request(
            `${API.tasks}/${task.id}`,
            jsonOptions({ status: nextStatus(task.status) }, "PATCH"),
          );
          return `Moved “${task.title}” to ${nextStatus(task.status).replaceAll("_", " ")}`;
        }),
      );
      card.querySelector(".delete-task").addEventListener("click", (event) =>
        runAction(event.currentTarget, async () => {
          await request(`${API.tasks}/${task.id}`, { method: "DELETE" });
          return `Deleted production task “${task.title}”`;
        }),
      );
      lane.append(card);
    }
  }
}

async function loadSession() {
  const query = new URLSearchParams(
    new FormData(document.querySelector("#board-filter")),
  );
  if (!query.get("status")) query.delete("status");
  [state.users, state.tags, state.tasks] = await Promise.all([
    request(API.users),
    request(API.tags),
    request(`${API.tasks}?${query}`),
  ]);
  populateSelects();
  renderBoard();
}

async function runAction(button, action) {
  if (button.disabled) return;
  button.disabled = true;
  try {
    const message = await action();
    try {
      await loadSession();
      showResult(message);
    } catch (error) {
      showResult(
        `${message} — saved, but the board could not refresh: ${error.message}`,
        "error",
      );
    }
  } catch (error) {
    showResult(error.message, "error");
  } finally {
    button.disabled =
      button.closest("#task-form") !== null && state.users.length === 0;
  }
}

function bindForm(selector, action) {
  document.querySelector(selector).addEventListener("submit", (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    runAction(form.querySelector('button[type="submit"]'), () =>
      action(new FormData(form)),
    );
  });
}

bindForm("#user-form", async (data) => {
  const user = await request(API.users, jsonOptions(Object.fromEntries(data)));
  return `Musician ${user.username} joined the session — choose this handle in Owner`;
});

bindForm("#tag-form", async (data) => {
  const tag = await request(API.tags, jsonOptions(Object.fromEntries(data)));
  return `Tag “${tag.name}” is ready — select it when scheduling production work`;
});

bindForm("#task-form", async (data) => {
  const payload = {
    title: data.get("title"),
    description: data.get("description") || null,
    priority: Number(data.get("priority")),
    due_date: data.get("due_date") || null,
    owner_id: Number(data.get("owner_id")),
    tag_ids: data.getAll("tag_ids").map(Number),
  };
  const task = await request(API.tasks, jsonOptions(payload));
  return `Production task “${task.title}” entered To do — use Move to advance its stage`;
});

async function refreshSession() {
  try {
    await loadSession();
    showResult(
      "Session loaded from your database — register a musician or schedule production work",
    );
  } catch (error) {
    showResult(error.message, "error");
  }
}

const revisions = Array.from(document.querySelectorAll("[data-revision]"));
let selectedRevision = revisions.at(-1);

function renderMigration() {
  for (const revision of revisions)
    revision.setAttribute(
      "aria-pressed",
      String(revision === selectedRevision),
    );
  document.querySelector("#revision-title").textContent =
    `${selectedRevision.dataset.revision} · ${selectedRevision.querySelector("strong").textContent}`;
  document.querySelector("#revision-upgrade").textContent =
    selectedRevision.dataset.upgrade;
  document.querySelector("#revision-downgrade").textContent =
    selectedRevision.dataset.downgrade;
  const action = document.querySelector("#migration-action").value;
  document.querySelector("#migration-command").textContent =
    action === "upgrade"
      ? `alembic upgrade ${selectedRevision.dataset.revision}`
      : `alembic ${action === "history" ? "history --verbose" : action}`;
  document.querySelector("#copy-result").textContent = "";
}

for (const revision of revisions)
  revision.addEventListener("click", () => {
    selectedRevision = revision;
    renderMigration();
  });
document
  .querySelector("#migration-action")
  .addEventListener("change", renderMigration);
document
  .querySelector("#copy-migration")
  .addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(
        document.querySelector("#migration-command").textContent,
      );
      document.querySelector("#copy-result").textContent =
        "Command copied — paste it into your project terminal";
    } catch {
      document.querySelector("#copy-result").textContent =
        "Clipboard unavailable — select and copy the displayed command manually";
    }
  });
document
  .querySelector("#refresh-board")
  .addEventListener("click", refreshSession);
document.querySelector("#board-filter").addEventListener("submit", (event) => {
  event.preventDefault();
  refreshSession();
});
renderMigration();
refreshSession();
