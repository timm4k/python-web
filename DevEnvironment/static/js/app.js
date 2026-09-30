const accentColors = {
  violet: "#9b6dff",
  pink: "#ff7ad9",
  blue: "#72d7ff",
  lime: "#c8f76f",
  orange: "#ffb86b",
};

const elements = {
  environmentGrid: document.querySelector("#environment-grid"),
  factsGrid: document.querySelector("#facts-grid"),
  conceptsGrid: document.querySelector("#concepts-grid"),
  factKeyword: document.querySelector("#fact-keyword"),
  factCategory: document.querySelector("#fact-category"),
  factSort: document.querySelector("#fact-sort"),
  factSummary: document.querySelector("#fact-summary"),
  converterForm: document.querySelector("#converter-form"),
  numberValue: document.querySelector("#number-value"),
  fromBase: document.querySelector("#from-base"),
  toBase: document.querySelector("#to-base"),
  conversionResult: document.querySelector("#conversion-result"),
};

function environmentCard(label, value) {
  const card = document.createElement("article");
  card.className = "environment-card";
  const caption = document.createElement("span");
  caption.textContent = label;
  const content = document.createElement("strong");
  content.textContent = value;
  card.append(caption, content);
  return card;
}

function factCard(fact) {
  const card = document.createElement("article");
  card.className = "fact-card";
  card.style.setProperty(
    "--card-accent",
    accentColors[fact.accent] ?? accentColors.violet,
  );
  const category = document.createElement("span");
  category.textContent = fact.category;
  const title = document.createElement("h3");
  title.textContent = fact.title;
  const copy = document.createElement("p");
  copy.textContent = fact.fact;
  card.append(category, title, copy);
  return card;
}

function conceptCard(concept) {
  const card = document.createElement("article");
  card.className = "concept-card";
  const title = document.createElement("h3");
  title.textContent = concept.name;
  const expression = document.createElement("code");
  expression.textContent = concept.expression;
  const result = document.createElement("p");
  result.textContent = `Result: ${concept.result}`;
  card.append(title, expression, result);
  return card;
}

async function loadDashboard() {
  const [environmentResponse, conceptsResponse] = await Promise.all([
    fetch("/api/environment"),
    fetch("/api/concepts"),
  ]);
  if (!environmentResponse.ok || !conceptsResponse.ok) {
    throw new Error("The Python lab could not be loaded");
  }
  const environment = await environmentResponse.json();
  const concepts = await conceptsResponse.json();
  elements.environmentGrid.replaceChildren(
    environmentCard("Python", environment.pythonVersion),
    environmentCard("Operating system", environment.operatingSystem),
    environmentCard("Architecture", environment.architecture),
    environmentCard(
      "Virtual environment",
      environment.virtualEnvironment ? "Active" : "Inactive",
    ),
  );
  elements.conceptsGrid.replaceChildren(...concepts.map(conceptCard));
  await loadFacts();
}

async function loadFacts() {
  const parameters = new URLSearchParams();
  const keyword = elements.factKeyword.value.trim();
  if (keyword) parameters.set("keyword", keyword);
  if (elements.factCategory.value)
    parameters.set("category", elements.factCategory.value);
  if (elements.factSort.checked) parameters.set("sort_by_title", "true");
  const query = parameters.toString();
  const response = await fetch(`/api/cats${query ? `?${query}` : ""}`);
  if (!response.ok) throw new Error("Cat facts could not be filtered");
  const facts = await response.json();
  if (facts.length === 0) {
    const emptyState = document.createElement("p");
    emptyState.className = "empty-state";
    emptyState.textContent =
      "No facts match these filters. Try another word or clear the filters";
    elements.factsGrid.replaceChildren(emptyState);
  } else {
    elements.factsGrid.replaceChildren(...facts.map(factCard));
  }
  elements.factSummary.textContent = `Showing ${facts.length} ${facts.length === 1 ? "matching fact" : "matching facts"}`;
}

function filterFacts() {
  elements.factSummary.textContent = "Filtering facts";
  loadFacts().catch((error) => {
    elements.factSummary.textContent = error.message;
  });
}

async function convertNumber(event) {
  event.preventDefault();
  const response = await fetch("/api/convert", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      value: elements.numberValue.value,
      from_base: Number(elements.fromBase.value),
      to_base: Number(elements.toBase.value),
    }),
  });
  const payload = await response.json();
  const result = elements.conversionResult.querySelector("strong");
  elements.conversionResult.classList.toggle("error", !response.ok);
  result.textContent = response.ok
    ? payload.result
    : (payload.detail ?? "Conversion failed");
}

function swapBases() {
  const currentFrom = elements.fromBase.value;
  elements.fromBase.value = elements.toBase.value;
  elements.toBase.value = currentFrom;
}

document.querySelector("#apply-filters").addEventListener("click", filterFacts);
elements.factKeyword.addEventListener("keydown", (event) => {
  if (event.key === "Enter") filterFacts();
});
document.querySelector("#clear-filters").addEventListener("click", () => {
  elements.factKeyword.value = "";
  elements.factCategory.value = "";
  elements.factSort.checked = false;
  filterFacts();
});
document.querySelector("#swap-bases").addEventListener("click", swapBases);
elements.converterForm.addEventListener("submit", convertNumber);

loadDashboard().catch((error) => {
  elements.environmentGrid.textContent = error.message;
});
