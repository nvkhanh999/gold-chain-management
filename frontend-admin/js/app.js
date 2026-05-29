const API_BASE = "/api";
const ADMIN_BASE = "/api/admin";
let token = localStorage.getItem("admin_token");

const loginPage = document.getElementById("loginPage");
const appPage = document.getElementById("appPage");

const pageTitles = {
  dashboard: "Dashboard tổng hợp",
  branches: "Quản lý chi nhánh",
  users: "Quản lý tài khoản",
  prices: "Quản lý giá vàng",
  reports: "Báo cáo toàn chuỗi",
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
    } else if (["branchID"].includes(key)) {
      obj[key] = Number(value);
    } else if (["buyPricePerChi", "sellPricePerChi"].includes(key)) {
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

function fillBranchSelect(id, branches, placeholder, nullable = true) {
  const select = document.getElementById(id);
  if (!select) return;
  select.innerHTML = "";
  const first = document.createElement("option");
  first.value = "";
  first.textContent = placeholder;
  select.appendChild(first);

  branches.forEach(b => {
    const option = document.createElement("option");
    option.value = b.branchID;
    option.textContent = `${b.code} - ${b.name}`;
    select.appendChild(option);
  });
}

async function loadMe() {
  const me = await api(`${API_BASE}/auth/me`);
  document.getElementById("userInfo").textContent = `${me.fullName} - ${me.role}`;
}

async function loadDashboard() {
  const data = await api(`${ADMIN_BASE}/dashboard`);
  document.getElementById("statBranches").textContent = data.totalBranches;
  document.getElementById("statProducts").textContent = data.totalProducts;
  document.getElementById("statSale").textContent = money(data.totalSaleAmount);
  document.getElementById("statWeight").textContent = gram(data.stockWeightGram);

  renderTable("branchStatsTable", [
    { key: "code", label: "Mã CN" },
    { key: "name", label: "Chi nhánh" },
    { key: "saleAmount", label: "Tổng bán", render: r => money(r.saleAmount) },
    { key: "purchaseAmount", label: "Tổng mua vào", render: r => money(r.purchaseAmount) },
    { key: "stockWeightGram", label: "Tồn kho", render: r => gram(r.stockWeightGram) },
  ], data.branchStats || []);
}

async function loadBranches() {
  const rows = await api(`${ADMIN_BASE}/branches`);
  renderTable("branchTable", [
    { key: "branchID", label: "ID" },
    { key: "code", label: "Mã" },
    { key: "name", label: "Tên chi nhánh" },
    { key: "phoneNumber", label: "SĐT" },
    { key: "address", label: "Địa chỉ" },
    { key: "active", label: "Trạng thái", render: r => r.active ? "Hoạt động" : "Ngừng" },
  ], rows);
  fillBranchSelect("userBranchSelect", rows, "Không gán chi nhánh", true);
  fillBranchSelect("priceBranchSelect", rows, "Giá toàn hệ thống", true);
}

async function loadUsers() {
  const rows = await api(`${ADMIN_BASE}/users`);
  renderTable("userTable", [
    { key: "userID", label: "ID" },
    { key: "fullName", label: "Họ tên" },
    { key: "email", label: "Email" },
    { key: "role", label: "Vai trò", render: r => `<span class="badge badge-info badge-role">${r.role}</span>` },
    { key: "branchID", label: "Chi nhánh" },
    { key: "active", label: "Trạng thái", render: r => r.active ? "Hoạt động" : "Khóa" },
  ], rows);
}

async function loadPrices() {
  const rows = await api(`${ADMIN_BASE}/gold-prices`);
  renderTable("priceTable", [
    { key: "priceID", label: "ID" },
    { key: "branchID", label: "Chi nhánh", render: r => r.branchID || "Toàn hệ thống" },
    { key: "goldType", label: "Loại vàng" },
    { key: "buyPricePerChi", label: "Mua/chỉ", render: r => money(r.buyPricePerChi) },
    { key: "sellPricePerChi", label: "Bán/chỉ", render: r => money(r.sellPricePerChi) },
    { key: "effectiveFrom", label: "Thời điểm", render: r => new Date(r.effectiveFrom).toLocaleString("vi-VN") },
  ], rows);
}

async function loadReport(type = "products") {
  if (type === "products") {
    const rows = await api(`${ADMIN_BASE}/products`);
    renderTable("reportTable", [
      { key: "productID", label: "ID" },
      { key: "branchID", label: "CN" },
      { key: "sku", label: "SKU" },
      { key: "name", label: "Tên" },
      { key: "goldType", label: "Loại vàng" },
      { key: "weightGram", label: "Gram", render: r => gram(r.weightGram) },
      { key: "quantity", label: "SL" },
      { key: "status", label: "Trạng thái" },
    ], rows);
  }

  if (type === "sales") {
    const rows = await api(`${ADMIN_BASE}/sales`);
    renderTable("reportTable", [
      { key: "code", label: "Mã HĐ" },
      { key: "branchID", label: "CN" },
      { key: "productID", label: "SP" },
      { key: "goldType", label: "Loại vàng" },
      { key: "weightGram", label: "Gram", render: r => gram(r.weightGram) },
      { key: "totalAmount", label: "Tổng tiền", render: r => money(r.totalAmount) },
      { key: "createdAt", label: "Ngày", render: r => new Date(r.createdAt).toLocaleString("vi-VN") },
    ], rows);
  }

  if (type === "purchases") {
    const rows = await api(`${ADMIN_BASE}/purchases`);
    renderTable("reportTable", [
      { key: "code", label: "Mã phiếu" },
      { key: "branchID", label: "CN" },
      { key: "customerID", label: "KH" },
      { key: "goldType", label: "Loại vàng" },
      { key: "weightGram", label: "Gram", render: r => gram(r.weightGram) },
      { key: "totalAmount", label: "Tổng tiền", render: r => money(r.totalAmount) },
      { key: "createdAt", label: "Ngày", render: r => new Date(r.createdAt).toLocaleString("vi-VN") },
    ], rows);
  }

  if (type === "inventory") {
    const rows = await api(`${ADMIN_BASE}/inventory`);
    renderTable("reportTable", [
      { key: "movementID", label: "ID" },
      { key: "branchID", label: "CN" },
      { key: "productID", label: "SP" },
      { key: "movementType", label: "Loại" },
      { key: "quantity", label: "SL" },
      { key: "weightGram", label: "Gram", render: r => gram(r.weightGram) },
      { key: "note", label: "Ghi chú" },
      { key: "createdAt", label: "Ngày", render: r => new Date(r.createdAt).toLocaleString("vi-VN") },
    ], rows);
  }

  if (type === "onlineOrders") {
    const rows = await api(`${ADMIN_BASE}/online-orders`);
    renderTable("reportTable", [
      { key: "onlineOrderID", label: "Mã đơn", render: r => `#${r.onlineOrderID}` },
      { key: "branchID", label: "CN" },
      { key: "customerName", label: "Khách hàng" },
      { key: "phoneNumber", label: "SĐT" },
      { key: "address", label: "Địa chỉ" },
      { key: "status", label: "Trạng thái" },
      { key: "totalAmount", label: "Tổng tiền", render: r => money(r.totalAmount) },
      { key: "createdAt", label: "Ngày", render: r => new Date(r.createdAt).toLocaleString("vi-VN") },
    ], rows);
  }
}

async function refreshAll() {
  await loadMe();
  await loadDashboard();
  await loadBranches();
  await loadUsers();
  await loadPrices();
  await loadReport("products");
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
    localStorage.setItem("admin_token", token);
    loginPage.classList.add("d-none");
    appPage.classList.remove("d-none");
    await refreshAll();
  } catch (error) {
    document.getElementById("loginError").textContent = error.message;
  }
});

document.getElementById("logoutBtn").addEventListener("click", () => {
  localStorage.removeItem("admin_token");
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

document.querySelectorAll(".report-btn").forEach(button => {
  button.addEventListener("click", () => loadReport(button.dataset.report));
});

bindForm("branchForm", `${ADMIN_BASE}/branches`, async () => loadBranches());
bindForm("userForm", `${ADMIN_BASE}/users`, async () => loadUsers());
bindForm("priceForm", `${ADMIN_BASE}/gold-prices`, async () => loadPrices());

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
    localStorage.removeItem("admin_token");
    token = null;
    loginPage.classList.remove("d-none");
    appPage.classList.add("d-none");
    document.getElementById("loginError").textContent = error.message;
  }
}

boot();
