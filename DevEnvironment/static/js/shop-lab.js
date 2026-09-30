const elements = {
  taskGrid: document.querySelector("#task-grid"),
  vatPrice: document.querySelector("#vat-price"),
  vatResult: document.querySelector("#vat-result"),
  productGrid: document.querySelector("#product-grid"),
  productSelect: document.querySelector("#product-select"),
  customerName: document.querySelector("#customer-name"),
  orderResult: document.querySelector("#order-result"),
  ordersList: document.querySelector("#orders-list"),
  simulationSummary: document.querySelector("#simulation-summary"),
  ordersCreated: document.querySelector("#orders-created"),
  manifestValue: document.querySelector("#manifest-value"),
  downloadOrders: document.querySelector("#download-orders"),
};

let currentOrders = [];

function taskCard(task) {
  const card = document.createElement("article");
  card.className = "task-card";
  const number = document.createElement("span");
  number.className = "task-number";
  number.textContent = task.number;
  const title = document.createElement("h3");
  title.textContent = task.title;
  const concept = document.createElement("p");
  concept.textContent = task.concept;
  const command = document.createElement("code");
  command.textContent = task.command;
  card.append(number, title, concept, command);
  return card;
}

function productCard(product) {
  const card = document.createElement("article");
  card.className = "product-card";
  const title = document.createElement("strong");
  title.textContent = product.name;
  const price = document.createElement("span");
  price.textContent = `${product.price.toFixed(2)} UAH`;
  card.append(title, price);
  return card;
}

function productOption(product) {
  const option = document.createElement("option");
  option.value = product.id;
  option.textContent = `${product.name} · ${product.price.toFixed(2)} UAH`;
  return option;
}

function orderItem(order) {
  const item = document.createElement("article");
  item.className = "order-item";
  const number = document.createElement("b");
  number.textContent = order.id;
  const details = document.createElement("div");
  details.className = "order-meta";
  const product = document.createElement("strong");
  product.textContent = order.product;
  const customer = document.createElement("small");
  const createdAt = new Intl.DateTimeFormat("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date(order.timestamp));
  customer.textContent = `${order.customer} · ${createdAt}`;
  details.append(product, customer);
  const price = document.createElement("span");
  price.className = "order-price";
  price.textContent = `${order.price.toFixed(2)} UAH`;
  item.append(number, details, price);
  return item;
}

async function requestJson(url, options) {
  const response = await fetch(url, options);
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail ?? "Request failed");
  return payload;
}

async function loadPage() {
  const [tasks, products] = await Promise.all([
    requestJson("/api/shop-lab/overview"),
    requestJson("/api/shop-lab/products"),
  ]);
  elements.taskGrid.replaceChildren(...tasks.map(taskCard));
  elements.productGrid.replaceChildren(...products.map(productCard));
  elements.productSelect.replaceChildren(...products.map(productOption));
}

async function calculateVat() {
  const price = elements.vatPrice.value.trim();
  if (!price) {
    elements.vatResult.textContent = "Enter a product price";
    return;
  }
  try {
    const result = await requestJson(
      `/api/shop-lab/vat?price=${encodeURIComponent(price)}`,
    );
    elements.vatResult.textContent = `VAT ${result.formattedVat} · Total ${result.formattedTotal}`;
  } catch (error) {
    elements.vatResult.textContent = error.message;
  }
}

async function createOrder() {
  try {
    const result = await requestJson("/api/shop-lab/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        customer_name: elements.customerName.value,
        product_id: Number(elements.productSelect.value),
      }),
    });
    elements.orderResult.textContent = result.message;
  } catch (error) {
    elements.orderResult.textContent = error.message;
  }
}

function renderManifest(orders) {
  const total = orders.reduce((sum, order) => sum + order.price, 0);
  elements.ordersCreated.textContent = orders.length;
  elements.manifestValue.textContent = `${total.toFixed(2)} UAH`;
  elements.simulationSummary.hidden = false;
  elements.downloadOrders.hidden = false;
  elements.ordersList.replaceChildren(...orders.map(orderItem));
}

async function simulateOrders() {
  elements.ordersList.textContent = "Building manifest";
  try {
    currentOrders = await requestJson("/api/shop-lab/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ count: 5 }),
    });
    renderManifest(currentOrders);
  } catch (error) {
    elements.ordersList.textContent = error.message;
  }
}

function downloadOrders() {
  const blob = new Blob([JSON.stringify(currentOrders, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "orders.json";
  link.click();
  URL.revokeObjectURL(url);
}

document
  .querySelector("#calculate-vat")
  .addEventListener("click", calculateVat);
document.querySelector("#create-order").addEventListener("click", createOrder);
document
  .querySelector("#simulate-orders")
  .addEventListener("click", simulateOrders);
elements.downloadOrders.addEventListener("click", downloadOrders);
elements.vatPrice.addEventListener("keydown", (event) => {
  if (event.key === "Enter") calculateVat();
});

loadPage().catch((error) => {
  elements.taskGrid.textContent = error.message;
});
