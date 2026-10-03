const elements = {
  conceptGrid: document.querySelector("#concept-grid"),
  mroType: document.querySelector("#mro-type"),
  mroTrack: document.querySelector("#mro-track"),
  greetingResult: document.querySelector("#greeting-result"),
  vehicleType: document.querySelector("#vehicle-type"),
  engineResult: document.querySelector("#engine-result"),
  exportForm: document.querySelector("#export-form"),
  exportName: document.querySelector("#export-name"),
  exportFamily: document.querySelector("#export-family"),
  exportPrice: document.querySelector("#export-price"),
  exportFormat: document.querySelector("#export-format"),
  exportResult: document.querySelector("#export-result"),
};

const pageData = {
  mro: null,
  vehicles: [],
};

function mroNodes(classNames) {
  const nodes = [];
  classNames.forEach((className, index) => {
    const node = document.createElement("span");
    node.className = "mro-node";
    node.textContent = className;
    nodes.push(node);
    if (index < classNames.length - 1) {
      const arrow = document.createElement("span");
      arrow.className = "mro-arrow";
      arrow.textContent = "→";
      nodes.push(arrow);
    }
  });
  return nodes;
}

async function loadPage() {
  const [concepts, mro, vehicles, formats, perfumes] = await Promise.all([
    PerfumeLab.requestJson("/api/contracts/overview"),
    PerfumeLab.requestJson("/api/contracts/mro"),
    PerfumeLab.requestJson("/api/contracts/polymorphism"),
    PerfumeLab.requestJson("/api/contracts/formats"),
    PerfumeLab.requestJson("/api/catalog/perfumes"),
  ]);
  pageData.mro = mro;
  pageData.vehicles = vehicles;
  elements.conceptGrid.replaceChildren(...concepts.map(PerfumeLab.conceptCard));
  elements.vehicleType.replaceChildren(
    ...vehicles.map((vehicle) => {
      const option = document.createElement("option");
      option.value = vehicle.type;
      option.textContent = vehicle.type;
      return option;
    }),
  );
  elements.exportFormat.replaceChildren(
    ...formats.map((format) => {
      const option = document.createElement("option");
      option.value = format;
      option.textContent = format.toUpperCase();
      return option;
    }),
  );
  const defaultPerfume = perfumes[0];
  if (defaultPerfume) {
    elements.exportName.value = defaultPerfume.name;
    elements.exportFamily.value = defaultPerfume.family;
    elements.exportPrice.value = defaultPerfume.price;
  }
}

function traceMro() {
  if (!pageData.mro) {
    return;
  }
  const selected = elements.mroType.value;
  elements.mroTrack.replaceChildren(...mroNodes(pageData.mro[selected]));
  elements.greetingResult.textContent =
    selected === "diamond"
      ? `Lookup order: ${pageData.mro.diamond.join(" → ")}\nCall result: ${pageData.mro.greeting}\nMeaning: every super() continues with the next class in this order`
      : `Lookup order: ${pageData.mro.vehicles.join(" → ")}\nMeaning: Python searches each class from left to right until it finds the requested method`;
}

function startEngine() {
  const selected = pageData.vehicles.find(
    (vehicle) => vehicle.type === elements.vehicleType.value,
  );
  elements.engineResult.textContent = selected
    ? `Same call: start_engine()\nRuntime type: ${selected.type}\nSelected implementation: ${selected.result}\nMeaning: the object type controls the behavior`
    : "No runtime type selected";
}

async function exportFormula(event) {
  event.preventDefault();
  try {
    const result = await PerfumeLab.requestJson("/api/contracts/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: elements.exportName.value,
        family: elements.exportFamily.value,
        price: Number(elements.exportPrice.value),
        format: elements.exportFormat.value,
      }),
    });
    elements.exportResult.textContent = `Selected plugin: ${result.format.toUpperCase()}Exporter\nContract method: export(data)\n\n${result.result}`;
  } catch (error) {
    elements.exportResult.textContent = error.message;
  }
}

elements.exportForm.addEventListener("submit", exportFormula);
document.querySelector("#trace-mro").addEventListener("click", traceMro);
document.querySelector("#start-engine").addEventListener("click", startEngine);

loadPage().catch((error) => {
  elements.conceptGrid.textContent = error.message;
});
