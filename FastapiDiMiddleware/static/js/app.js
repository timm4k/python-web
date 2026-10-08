const API = Object.freeze({
  products: "/products",
  orders: "/api/v1/orders",
  notes: "/api/v1/notes",
  shorten: "/shorten",
});

const state = {
  allProducts: [],
  apiKey: "energy_remi_123",
};

async function request(url, options = {}) {
  const response = await fetch(url, options);
  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : null;
  if (!response.ok) {
    const fieldErrors = Object.values(payload?.errors ?? {}).join(" · ");
    const error = new Error(
      payload?.detail ??
        payload?.message ??
        (fieldErrors || null) ??
        `HTTP ${response.status}`,
    );
    error.status = response.status;
    error.payload = payload;
    throw error;
  }
  return { payload, response };
}

function setBusy(button, busy) {
  button.disabled = busy;
  button.dataset.originalLabel ??= button.textContent;
  button.textContent = busy ? "Processing…" : button.dataset.originalLabel;
}

function renderError(target, error) {
  target.innerHTML = "";
  const title = document.createElement("strong");
  title.className = "error";
  title.textContent = `HTTP ${error.status ?? "ERROR"}`;
  const message = document.createElement("p");
  message.textContent = error.message;
  target.append(title, message);
}

function renderDefinitionList(target, entries) {
  const list = document.createElement("dl");
  for (const [term, value, className] of entries) {
    const key = document.createElement("dt");
    const description = document.createElement("dd");
    key.textContent = term;
    description.textContent = value;
    if (className) description.className = className;
    list.append(key, description);
  }
  target.replaceChildren(list);
}

function renderProducts(products) {
  const grid = document.querySelector("#product-grid");
  if (!products.length) {
    grid.innerHTML = '<p class="placeholder">No cans match this query</p>';
    return;
  }
  grid.innerHTML = "";
  for (const product of products) {
    const card = document.createElement("article");
    card.className = "product-card";
    card.dataset.category = product.category;
    const category = document.createElement("small");
    category.textContent = `${product.category} · ${product.sugar_free ? "zero sugar" : "original sugar"}`;
    const title = document.createElement("h3");
    title.textContent = product.name;
    const profile = document.createElement("p");
    profile.textContent = product.flavor_profile;
    const footer = document.createElement("footer");
    const price = document.createElement("strong");
    price.textContent = `${product.price.toFixed(2)} UAH`;
    const stock = document.createElement("span");
    stock.textContent = product.stock
      ? `${product.stock} cans`
      : "out of stock";
    if (!product.stock) stock.className = "stock-out";
    footer.append(price, stock);
    card.append(category, title, profile, footer);
    grid.append(card);
  }
}

function populateOrderProducts(products) {
  const select = document.querySelector("#order-product");
  select.innerHTML = "";
  for (const product of products.filter((item) => item.stock > 0)) {
    const option = document.createElement("option");
    option.value = product.id;
    option.textContent = `${product.name} · ${product.price.toFixed(2)} UAH`;
    select.append(option);
  }
}

document
  .querySelector("#catalog-form")
  .addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const button = form.querySelector("button");
    const data = new FormData(form);
    const params = new URLSearchParams({ skip: "0", limit: "50" });
    for (const field of ["category", "price_min", "price_max"]) {
      const value = data.get(field);
      if (value) params.set(field, value);
    }
    if (data.get("in_stock")) params.set("in_stock", "true");
    const url = `${API.products}?${params}`;
    document.querySelector("#catalog-request").textContent = url;
    setBusy(button, true);
    try {
      const { payload } = await request(url);
      renderProducts(payload);
    } catch (error) {
      renderError(document.querySelector("#product-grid"), error);
    } finally {
      setBusy(button, false);
    }
  });

document
  .querySelector("#order-form")
  .addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const button = form.querySelector("button");
    const data = new FormData(form);
    const product = state.allProducts.find(
      (item) => item.id === Number(data.get("product_name")),
    );
    const target = document.querySelector("#order-result");
    if (!product) {
      renderError(
        target,
        new Error("Run the catalog query and select an available can"),
      );
      return;
    }
    const payload = {
      customer_name: data.get("customer_name"),
      customer_phone: data.get("customer_phone"),
      delivery_address: data.get("delivery_address"),
      items: [
        {
          product_name: product.name,
          quantity: Number(data.get("quantity")),
          price: product.price,
        },
      ],
      promo_code: data.get("promo_code") || null,
    };
    setBusy(button, true);
    try {
      const result = await request(API.orders, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      renderDefinitionList(target, [
        ["Schema", "OrderRead", "ok"],
        ["Order ID", String(result.payload.id)],
        ["Status", result.payload.status],
        ["Computed total", `${result.payload.total_price.toFixed(2)} UAH`],
        ["Server timestamp", result.payload.created_at],
      ]);
    } catch (error) {
      renderError(target, error);
    } finally {
      setBusy(button, false);
    }
  });

for (const button of document.querySelectorAll("[data-api-key]")) {
  button.addEventListener("click", () => {
    state.apiKey = button.dataset.apiKey;
    document
      .querySelectorAll("[data-api-key]")
      .forEach((item) => item.classList.remove("selected"));
    button.classList.add("selected");
  });
}

document
  .querySelector("#note-form")
  .addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const button = form.querySelector("button");
    const data = new FormData(form);
    const target = document.querySelector("#note-result");
    setBusy(button, true);
    try {
      const result = await request(API.notes, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": state.apiKey,
        },
        body: JSON.stringify({
          title: data.get("title"),
          content: data.get("content"),
        }),
      });
      renderDefinitionList(target, [
        ["Resolved author", result.payload.author, "ok"],
        ["Owner ID", result.payload.owner_id],
        ["Stored note", result.payload.title],
        [
          "Dependency lifecycle",
          "authentication → audit yield → endpoint → audit finally",
        ],
      ]);
    } catch (error) {
      renderError(target, error);
    } finally {
      setBusy(button, false);
    }
  });

document
  .querySelector("#link-form")
  .addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const button = form.querySelector("button");
    const data = new FormData(form);
    const target = document.querySelector("#link-result");
    setBusy(button, true);
    try {
      const result = await request(API.shorten, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Request-ID": crypto.randomUUID(),
        },
        body: JSON.stringify({
          original_url: data.get("original_url"),
          custom_alias: data.get("custom_alias") || null,
        }),
      });
      renderDefinitionList(target, [
        ["Status", "201 Created", "ok"],
        ["Short route", `/${result.payload.short_code}`],
        ["X-Request-ID", result.response.headers.get("X-Request-ID")],
        ["X-Process-Time", result.response.headers.get("X-Process-Time")],
        ["Clicks", String(result.payload.clicks)],
      ]);
    } catch (error) {
      renderError(target, error);
    } finally {
      setBusy(button, false);
    }
  });

async function initializeCatalog() {
  const target = document.querySelector("#product-grid");
  try {
    const { payload } = await request(`${API.products}?skip=0&limit=50`);
    state.allProducts = payload;
    renderProducts(payload);
    populateOrderProducts(payload);
  } catch (error) {
    renderError(target, error);
  }
}

initializeCatalog();
