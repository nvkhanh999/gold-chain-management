const API_BASE = "/api";
const CENTER_BASE = "/api/center";
let token = localStorage.getItem("center_token");

const loginPage = document.getElementById("loginPage");
const appPage = document.getElementById("appPage");

const pageTitles = {
  dashboard: "Dashboard cửa hàng",
  customers: "Khách hàng",
  products: "Sản phẩm vàng",
  prices: "Bảng giá vàng",
  sales: "Bán vàng",
  purchases: "Mua vàng từ khách",
  inventory: "Biến động kho",
  onlineOrders: "Đơn hàng online",
};

function money(value) {
  return Number(value || 0).toLocaleString("vi-VN") + " đ";
}

function gram(value) {
  return Number(value || 0).toLocaleString("vi-VN", { maximumFractionDigits: 3 }) + " g";
}

async function api(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(path, { ...options, headers });

  if (!response.ok) {
    let message = "Có lỗi xảy ra";
    try {
      const data = await response.json();
      message = data.detail || message;
    } catch (_) {}
    throw new Error(message);
  }
  return response.json();
}

function formToObject(form) {
  const data = new FormData(form);
  const obj = {};
  for (const [key, value] of data.entries()) {
    if (value === "") {
      obj[key] = null;
    } else if (["customerID", "productID", "quantity"].includes(key)) {
      obj[key] = Number(value);
    } else if (["weightGram", "makingFee", "stoneFee", "costPrice", "discount"].includes(key)) {
      obj[key] = Number(value);
    } else {
      obj[key] = value;
    }
  }
  return obj;
}

function renderTable(tableId, columns, rows) {
  const table = document.getElementById(tableId);
  table.innerHTML = `
    <thead><tr>${columns.map(c => `<th>${c.label}</th>`).join("")}</tr></thead>
    <tbody>
      ${rows.map(row => `<tr>${columns.map(c => `<td>${c.render ? c.render(row) : (row[c.key] ?? "")}</td>`).join("")}</tr>`).join("")}
    </tbody>
  `;
}

function fillSelect(id, rows, placeholder, nullable = true) {
  const select = document.getElementById(id);
  if (!select) return;
  select.innerHTML = "";

  const first = document.createElement("option");
  first.value = "";
  first.textContent = placeholder;
  select.appendChild(first);

  rows.forEach(row => {
    const option = document.createElement("option");
    option.value = row.id;
    option.textContent = row.name;
    select.appendChild(option);
  });
}

async function loadMe() {
  const me = await api(`${API_BASE}/auth/me`);
  document.getElementById("userInfo").textContent = `${me.fullName} - ${me.role}`;
}

async function loadDashboard() {
  const data = await api(`${CENTER_BASE}/dashboard`);
  document.getElementById("branchName").textContent = data.branchName;
  document.getElementById("statCustomers").textContent = data.totalCustomers;
  document.getElementById("statProducts").textContent = data.totalProducts;
  document.getElementById("statSale").textContent = money(data.totalSaleAmount);
  document.getElementById("statWeight").textContent = gram(data.stockWeightGram);
}

async function loadCustomers() {
  const rows = await api(`${CENTER_BASE}/customers`);
  renderTable("customerTable", [
    { key: "customerID", label: "ID" },
    { key: "fullName", label: "Họ tên" },
    { key: "phoneNumber", label: "SĐT" },
    { key: "identityNumber", label: "CCCD/CMND" },
    { key: "address", label: "Địa chỉ" },
  ], rows);

  const options = rows.map(c => ({ id: c.customerID, name: `${c.fullName} - ${c.phoneNumber || ""}` }));
  fillSelect("saleCustomerSelect", options, "Khách lẻ", true);
  fillSelect("purchaseCustomerSelect", options, "Khách lẻ", true);
}

async function loadProducts() {
  const rows = await api(`${CENTER_BASE}/products`);
  renderTable("productTable", [
    { key: "productID", label: "ID" },
    { key: "sku", label: "SKU" },
    { key: "name", label: "Tên" },
    { key: "category", label: "Danh mục" },
    { key: "goldType", label: "Loại vàng" },
    { key: "weightGram", label: "Gram", render: r => gram(r.weightGram) },
    { key: "quantity", label: "SL" },
    { key: "makingFee", label: "Tiền công", render: r => money(r.makingFee) },
    { key: "status", label: "Trạng thái" },
  ], rows);

  const options = rows
    .filter(p => p.status === "IN_STOCK" && p.quantity > 0)
    .map(p => ({ id: p.productID, name: `${p.sku} - ${p.name} (${p.goldType}, ${p.weightGram}g)` }));
  fillSelect("saleProductSelect", options, "Chọn sản phẩm", false);
}

async function loadPrices() {
  const rows = await api(`${CENTER_BASE}/gold-prices`);
  renderTable("priceTable", [
    { key: "priceID", label: "ID" },
    { key: "branchID", label: "Phạm vi", render: r => r.branchID || "Toàn hệ thống" },
    { key: "goldType", label: "Loại vàng" },
    { key: "buyPricePerChi", label: "Mua/chỉ", render: r => money(r.buyPricePerChi) },
    { key: "sellPricePerChi", label: "Bán/chỉ", render: r => money(r.sellPricePerChi) },
    { key: "effectiveFrom", label: "Thời điểm", render: r => new Date(r.effectiveFrom).toLocaleString("vi-VN") },
  ], rows);
}

async function loadSales() {
  const rows = await api(`${CENTER_BASE}/sales`);
  renderTable("saleTable", [
    { key: "code", label: "Mã HĐ" },
    { key: "customerID", label: "KH" },
    { key: "productID", label: "SP" },
    { key: "goldType", label: "Loại vàng" },
    { key: "weightGram", label: "Gram", render: r => gram(r.weightGram) },
    { key: "totalAmount", label: "Tổng tiền", render: r => money(r.totalAmount) },
    { key: "paymentMethod", label: "Thanh toán" },
    { key: "createdAt", label: "Ngày", render: r => new Date(r.createdAt).toLocaleString("vi-VN") },
  ], rows);
}

async function loadPurchases() {
  const rows = await api(`${CENTER_BASE}/purchases`);
  renderTable("purchaseTable", [
    { key: "code", label: "Mã phiếu" },
    { key: "customerID", label: "KH" },
    { key: "goldType", label: "Loại vàng" },
    { key: "weightGram", label: "Gram", render: r => gram(r.weightGram) },
    { key: "totalAmount", label: "Tổng tiền", render: r => money(r.totalAmount) },
    { key: "paymentMethod", label: "Thanh toán" },
    { key: "createdAt", label: "Ngày", render: r => new Date(r.createdAt).toLocaleString("vi-VN") },
  ], rows);
}


async function loadOnlineOrders() {
  const rows = await api(`${CENTER_BASE}/online-orders`);
  renderTable("onlineOrderTable", [
    { key: "onlineOrderID", label: "Mã đơn", render: r => `#${r.onlineOrderID}` },
    { key: "customerName", label: "Khách hàng" },
    { key: "phoneNumber", label: "SĐT" },
    { key: "address", label: "Địa chỉ" },
    { key: "totalAmount", label: "Tổng tiền", render: r => money(r.totalAmount) },
    { key: "status", label: "Trạng thái", render: r => `<span class="badge badge-${statusColor(r.status)}">${r.status}</span>` },
    { key: "items", label: "Sản phẩm", render: r => r.items.map(i => `${i.sku} x${i.quantity}`).join("<br>") },
    { key: "createdAt", label: "Ngày", render: r => new Date(r.createdAt).toLocaleString("vi-VN") },
    { key: "actions", label: "Thao tác", render: r => renderOrderActions(r) },
  ], rows);
}

function statusColor(status) {
  if (status === "PENDING") return "warning";
  if (status === "CONFIRMED") return "info";
  if (status === "COMPLETED") return "success";
  if (status === "CANCELLED") return "danger";
  return "secondary";
}

function renderOrderActions(order) {
  if (order.status === "COMPLETED" || order.status === "CANCELLED") {
    return "-";
  }

  return `
    <div class="btn-group btn-group-sm">
      <button class="btn btn-info" onclick="updateOnlineOrderStatus(${order.onlineOrderID}, 'CONFIRMED')">Xác nhận</button>
      <button class="btn btn-success" onclick="updateOnlineOrderStatus(${order.onlineOrderID}, 'COMPLETED')">Hoàn tất</button>
      <button class="btn btn-danger" onclick="updateOnlineOrderStatus(${order.onlineOrderID}, 'CANCELLED')">Hủy</button>
    </div>
  `;
}

async function updateOnlineOrderStatus(orderID, status) {
  if (!confirm(`Cập nhật đơn #${orderID} sang trạng thái ${status}?`)) return;

  try {
    await api(`${CENTER_BASE}/online-orders/${orderID}/status`, {
      method: "PUT",
      body: JSON.stringify({ status }),
    });
    await loadOnlineOrders();
    await loadProducts();
    await loadInventory();
    await loadDashboard();
    alert("Cập nhật đơn hàng thành công");
  } catch (error) {
    alert(error.message);
  }
}


async function loadInventory() {
  const rows = await api(`${CENTER_BASE}/inventory`);
  renderTable("inventoryTable", [
    { key: "movementID", label: "ID" },
    { key: "productID", label: "SP" },
    { key: "movementType", label: "Loại" },
    { key: "quantity", label: "SL" },
    { key: "weightGram", label: "Gram", render: r => gram(r.weightGram) },
    { key: "referenceType", label: "Nguồn" },
    { key: "note", label: "Ghi chú" },
    { key: "createdAt", label: "Ngày", render: r => new Date(r.createdAt).toLocaleString("vi-VN") },
  ], rows);
}

async function refreshAll() {
  await loadMe();
  await loadDashboard();
  await loadCustomers();
  await loadProducts();
  await loadPrices();
  await loadSales();
  await loadPurchases();
  await loadOnlineOrders();
  await loadInventory();
}

function showPage(page) {
  document.querySelectorAll(".page").forEach(item => item.classList.add("d-none"));
  document.getElementById(page).classList.remove("d-none");
  document.querySelectorAll(".nav-link").forEach(item => item.classList.remove("active"));
  document.querySelectorAll(`.nav-route[data-page="${page}"]`).forEach(item => item.classList.add("active"));
  document.getElementById("pageTitle").textContent = pageTitles[page] || "";
}

function bindForm(formId, path, afterSubmit) {
  document.getElementById(formId).addEventListener("submit", async event => {
    event.preventDefault();
    try {
      const payload = formToObject(event.target);
      await api(path, { method: "POST", body: JSON.stringify(payload) });
      event.target.reset();
      await afterSubmit();
      await loadDashboard();
      alert("Thao tác thành công");
    } catch (error) {
      alert(error.message);
    }
  });
}

document.getElementById("loginForm").addEventListener("submit", async event => {
  event.preventDefault();
  document.getElementById("loginError").textContent = "";
  try {
    const data = await api(`${API_BASE}/auth/login`, {
      method: "POST",
      body: JSON.stringify({
        email: document.getElementById("email").value,
        password: document.getElementById("password").value,
      }),
    });
    token = data.access_token;
    localStorage.setItem("center_token", token);
    loginPage.classList.add("d-none");
    appPage.classList.remove("d-none");
    await refreshAll();
  } catch (error) {
    document.getElementById("loginError").textContent = error.message;
  }
});

document.getElementById("logoutBtn").addEventListener("click", () => {
  localStorage.removeItem("center_token");
  token = null;
  appPage.classList.add("d-none");
  loginPage.classList.remove("d-none");
});

document.querySelectorAll(".nav-route").forEach(item => {
  item.addEventListener("click", event => {
    event.preventDefault();
    showPage(item.dataset.page);
  });
});

bindForm("customerForm", `${CENTER_BASE}/customers`, async () => loadCustomers());
bindForm("productForm", `${CENTER_BASE}/products`, async () => {
  await loadProducts();
  await loadInventory();
});
bindForm("saleForm", `${CENTER_BASE}/sales`, async () => {
  await loadProducts();
  await loadSales();
  await loadInventory();
});
bindForm("purchaseForm", `${CENTER_BASE}/purchases`, async () => {
  await loadPurchases();
  await loadOnlineOrders();
  await loadInventory();
});

async function boot() {
  if (!token) {
    loginPage.classList.remove("d-none");
    appPage.classList.add("d-none");
    return;
  }

  try {
    loginPage.classList.add("d-none");
    appPage.classList.remove("d-none");
    await refreshAll();
  } catch (error) {
    localStorage.removeItem("center_token");
    token = null;
    loginPage.classList.remove("d-none");
    appPage.classList.add("d-none");
    document.getElementById("loginError").textContent = error.message;
  }
}

boot();
