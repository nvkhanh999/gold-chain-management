const SHOP_BASE = "/api/shop";
let branches = [];
let products = [];
let cart = [];

function money(value) {
  return Number(value || 0).toLocaleString("vi-VN") + " đ";
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    let message = "Có lỗi xảy ra";
    try {
      const data = await response.json();
      message = data.detail || message;
    } catch (_) { }
    throw new Error(message);
  }

  return response.json();
}

async function loadBranches() {
  branches = await api(`${SHOP_BASE}/branches`);
  const select = document.getElementById("branchSelect");
  select.innerHTML = branches.map(b => `<option value="${b.branchID}">${b.code} - ${b.name}</option>`).join("");
}

async function loadProducts() {
  const branchID = document.getElementById("branchSelect").value;
  const keyword = document.getElementById("keywordInput").value.trim();
  const goldType = document.getElementById("goldTypeSelect").value;

  const params = new URLSearchParams();
  if (branchID) params.append("branchID", branchID);
  if (keyword) params.append("keyword", keyword);
  if (goldType) params.append("goldType", goldType);

  products = await api(`${SHOP_BASE}/products?${params.toString()}`);
  renderProducts();
}
function productImage(p) {
  return `/static-shop/img/${p.sku}.jpg`;
}
function renderProducts() {
  const grid = document.getElementById("productGrid");

  if (!products.length) {
    grid.innerHTML = `<div class="col-12"><div class="alert alert-warning">Không có sản phẩm phù hợp.</div></div>`;
    return;
  }

  grid.innerHTML = products.map(p => `
    <div class="col-md-6 mb-4">
      <div class="card product-card">
        <div class="product-img">
  <img src="${productImage(p)}" 
       alt="${p.name}" 
       onerror="this.style.display='none'; this.parentElement.innerHTML='<i class=&quot;fas fa-gem&quot;></i>'">
</div>
        <div class="card-body">
          <div class="mb-2">
            <span class="badge badge-gold">${p.goldType}</span>
            <span class="badge badge-light">${p.category || "Trang sức"}</span>
          </div>
          <h5 class="card-title">${p.name}</h5>
          <p class="card-text text-muted">
            SKU: ${p.sku}<br>
            Trọng lượng: ${p.weightGram}g<br>
            Hàm lượng: ${p.purity || "-"}<br>
            Còn: ${p.quantity}
          </p>
          <div class="price mb-3">${money(p.estimatedPrice)}</div>
          <button class="btn btn-gold btn-block" onclick="addToCart(${p.productID})">
            <i class="fas fa-cart-plus"></i> Thêm vào giỏ
          </button>
        </div>
      </div>
    </div>
  `).join("");
}

function addToCart(productID) {
  const product = products.find(p => p.productID === productID);
  if (!product) return;

  const existing = cart.find(item => item.productID === productID);
  if (existing) {
    const productStock = product.quantity;
    if (existing.cartQuantity >= productStock) {
      alert("Số lượng trong giỏ đã bằng số lượng tồn kho");
      return;
    }
    existing.cartQuantity += 1;
  } else {
    cart.push({ ...product, cartQuantity: 1 });
  }

  renderCart();
}

function removeFromCart(productID) {
  cart = cart.filter(item => item.productID !== productID);
  renderCart();
}

function changeQuantity(productID, quantity) {
  const item = cart.find(i => i.productID === productID);
  if (!item) return;

  const nextQuantity = Number(quantity);

  if (nextQuantity <= 0) {
    removeFromCart(productID);
    return;
  }

  if (nextQuantity > item.quantity) {
    alert("Số lượng vượt quá tồn kho");
    return;
  }

  item.cartQuantity = nextQuantity;
  renderCart();
}

function renderCart() {
  const cartItems = document.getElementById("cartItems");
  const cartTotal = document.getElementById("cartTotal");

  if (!cart.length) {
    cartItems.innerHTML = "Chưa có sản phẩm";
    cartTotal.textContent = money(0);
    return;
  }

  cartItems.innerHTML = cart.map(item => `
    <div class="border-bottom py-2">
      <strong>${item.name}</strong>
      <div class="small text-muted">${item.sku} - ${money(item.estimatedPrice)}</div>
      <div class="d-flex align-items-center mt-1">
        <input type="number" class="form-control form-control-sm mr-2" style="width: 80px"
          min="1" max="${item.quantity}" value="${item.cartQuantity}"
          onchange="changeQuantity(${item.productID}, this.value)">
        <button class="btn btn-sm btn-outline-danger" onclick="removeFromCart(${item.productID})">Xóa</button>
      </div>
    </div>
  `).join("");

  const total = cart.reduce((sum, item) => sum + item.estimatedPrice * item.cartQuantity, 0);
  cartTotal.textContent = money(total);
}

document.getElementById("filterBtn").addEventListener("click", loadProducts);
document.getElementById("branchSelect").addEventListener("change", () => {
  cart = [];
  renderCart();
  loadProducts();
});

document.getElementById("orderForm").addEventListener("submit", async event => {
  event.preventDefault();

  const message = document.getElementById("orderMessage");
  message.innerHTML = "";

  if (!cart.length) {
    message.innerHTML = `<div class="alert alert-warning">Vui lòng chọn ít nhất một sản phẩm.</div>`;
    return;
  }

  const form = new FormData(event.target);
  const payload = {
    branchID: Number(document.getElementById("branchSelect").value),
    customerName: form.get("customerName"),
    phoneNumber: form.get("phoneNumber"),
    address: form.get("address") || null,
    note: form.get("note") || null,
    items: cart.map(item => ({
      productID: item.productID,
      quantity: item.cartQuantity,
    })),
  };

  try {
    const result = await api(`${SHOP_BASE}/orders`, {
      method: "POST",
      body: JSON.stringify(payload),
    });

    message.innerHTML = `
      <div class="alert alert-success">
        ${result.message}<br>
        Mã đơn: <strong>#${result.onlineOrderID}</strong><br>
        Tổng tiền dự kiến: <strong>${money(result.totalAmount)}</strong>
      </div>
    `;

    cart = [];
    renderCart();
    event.target.reset();
    await loadProducts();
  } catch (error) {
    message.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
  }
});

async function boot() {
  await loadBranches();
  await loadProducts();
}

boot();
