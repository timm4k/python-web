function conceptExplanation(label, text) {
  const section = document.createElement("div");
  section.className = "concept-explanation";
  const heading = document.createElement("strong");
  heading.textContent = label;
  const content = document.createElement("p");
  content.textContent =
    text || "Restart the Python server to load this updated explanation";
  section.append(heading, content);
  return section;
}

window.PerfumeLab = {
  async requestJson(url, options) {
    const response = await fetch(url, options);
    const payload = await response.json();
    if (!response.ok) {
      const detail =
        typeof payload.detail === "string" ? payload.detail : "Request failed";
      throw new Error(detail);
    }
    return payload;
  },

  conceptCard(concept) {
    const card = document.createElement("details");
    card.className = "concept-card";
    const summary = document.createElement("summary");
    const number = document.createElement("span");
    number.className = "concept-number";
    number.textContent = concept.index;
    const module = document.createElement("span");
    module.className = "module-name";
    module.textContent = concept.module;
    const title = document.createElement("h3");
    title.textContent = concept.title;
    const hint = document.createElement("span");
    hint.className = "concept-hint";
    hint.textContent = "More details";
    const details = document.createElement("div");
    details.className = "concept-details";
    summary.append(number, title, module, hint);
    details.append(
      conceptExplanation("What it covers", concept.focus),
      conceptExplanation("What the file demonstrates", concept.demonstration),
      conceptExplanation("Why it matters", concept.meaning),
      conceptExplanation("Run separately", concept.command),
    );
    card.append(summary, details);
    return card;
  },

  formatMegabytes(bytes) {
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  },
};
