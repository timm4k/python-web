const elements = {
  conceptGrid: document.querySelector("#concept-grid"),
  priceForm: document.querySelector("#price-form"),
  productName: document.querySelector("#product-name"),
  currentPrice: document.querySelector("#current-price"),
  newPrice: document.querySelector("#new-price"),
  priceResult: document.querySelector("#price-result"),
  objectCount: document.querySelector("#object-count"),
  objectCountValue: document.querySelector("#object-count-value"),
  memoryResults: document.querySelector("#memory-results"),
  memoryBars: document.querySelector("#memory-bars"),
  regularBar: document.querySelector("#regular-bar"),
  slottedBar: document.querySelector("#slotted-bar"),
  regularMemory: document.querySelector("#regular-memory"),
  slottedMemory: document.querySelector("#slotted-memory"),
  savedMemory: document.querySelector("#saved-memory"),
  memoryStatus: document.querySelector("#memory-status"),
};

async function loadPage() {
  const [concepts, perfumes, memorySettings] = await Promise.all([
    PerfumeLab.requestJson("/api/object-model/overview"),
    PerfumeLab.requestJson("/api/catalog/perfumes"),
    PerfumeLab.requestJson("/api/object-model/memory-settings"),
  ]);
  elements.conceptGrid.replaceChildren(...concepts.map(PerfumeLab.conceptCard));
  const defaultPerfume = perfumes[0];
  if (defaultPerfume) {
    elements.productName.value = defaultPerfume.name;
    elements.currentPrice.value = defaultPerfume.price;
    elements.newPrice.value = defaultPerfume.price;
  }
  elements.objectCount.min = memorySettings.minimum;
  elements.objectCount.max = memorySettings.maximum;
  elements.objectCount.value = memorySettings.default;
  updateObjectCount();
}

function parsePriceValue(rawValue) {
  const numericValue = Number(rawValue);
  return rawValue.trim() !== "" && Number.isFinite(numericValue)
    ? numericValue
    : rawValue;
}

async function validatePrice(event) {
  event.preventDefault();
  try {
    const result = await PerfumeLab.requestJson("/api/object-model/price", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: elements.productName.value,
        current_price: Number(elements.currentPrice.value),
        new_price: parsePriceValue(elements.newPrice.value),
      }),
    });
    if (result.accepted) {
      elements.currentPrice.value = result.price;
      elements.priceResult.textContent = `Setter decision: accepted\nState change: _price is now ${result.formatted}\nMeaning: the value passed both validation rules`;
    } else {
      elements.priceResult.textContent = `Setter decision: rejected\nReason: ${result.message}\nState change: none · _price remains ${result.formatted}`;
    }
  } catch (error) {
    elements.priceResult.textContent = error.message;
  }
}

async function measureMemory() {
  elements.memoryStatus.textContent = "Allocating objects";
  try {
    const result = await PerfumeLab.requestJson(
      `/api/object-model/memory?count=${encodeURIComponent(elements.objectCount.value)}`,
    );
    elements.regularMemory.textContent = PerfumeLab.formatMegabytes(
      result.regularBytes,
    );
    elements.slottedMemory.textContent = PerfumeLab.formatMegabytes(
      result.slottedBytes,
    );
    elements.savedMemory.textContent = `${result.savedPercent}%`;
    elements.memoryResults.hidden = false;
    elements.memoryBars.hidden = false;
    elements.regularBar.style.width = "100%";
    elements.slottedBar.style.width = `${(result.slottedBytes / result.regularBytes) * 100}%`;
    elements.memoryStatus.textContent = `Measured: ${result.count.toLocaleString()} objects per class\nMeaning: __slots__ used ${result.savedPercent}% less peak memory in this run`;
  } catch (error) {
    elements.memoryStatus.textContent = error.message;
  }
}

function updateObjectCount() {
  elements.objectCountValue.textContent = Number(
    elements.objectCount.value,
  ).toLocaleString();
}

elements.priceForm.addEventListener("submit", validatePrice);
document
  .querySelector("#measure-memory")
  .addEventListener("click", measureMemory);
elements.objectCount.addEventListener("input", updateObjectCount);
document.querySelectorAll("[data-price-example]").forEach((button) => {
  button.addEventListener("click", () => {
    elements.newPrice.value = button.dataset.priceExample;
  });
});

loadPage().catch((error) => {
  elements.conceptGrid.textContent = error.message;
});
