BEGIN;

DROP TABLE IF EXISTS online_order_items CASCADE;
DROP TABLE IF EXISTS online_orders CASCADE;
DROP TABLE IF EXISTS inventory_movements CASCADE;
DROP TABLE IF EXISTS purchase_orders CASCADE;
DROP TABLE IF EXISTS sale_orders CASCADE;
DROP TABLE IF EXISTS gold_price_histories CASCADE;
DROP TABLE IF EXISTS gold_products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS branches CASCADE;

CREATE TABLE branches (
    "branchID" SERIAL PRIMARY KEY,
    code VARCHAR NOT NULL UNIQUE,
    name VARCHAR NOT NULL,
    "phoneNumber" VARCHAR,
    address VARCHAR,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    "createdAt" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE users (
    "userID" SERIAL PRIMARY KEY,
    "branchID" INTEGER REFERENCES branches("branchID") ON DELETE SET NULL ON UPDATE CASCADE,
    "fullName" VARCHAR NOT NULL,
    email VARCHAR NOT NULL UNIQUE,
    password VARCHAR NOT NULL,
    role VARCHAR NOT NULL DEFAULT 'EMPLOYEE',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    "createdAt" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE customers (
    "customerID" SERIAL PRIMARY KEY,
    "branchID" INTEGER NOT NULL REFERENCES branches("branchID") ON DELETE CASCADE ON UPDATE CASCADE,
    "fullName" VARCHAR NOT NULL,
    "phoneNumber" VARCHAR,
    "identityNumber" VARCHAR,
    address VARCHAR,
    "createdAt" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE gold_products (
    "productID" SERIAL PRIMARY KEY,
    "branchID" INTEGER NOT NULL REFERENCES branches("branchID") ON DELETE CASCADE ON UPDATE CASCADE,
    sku VARCHAR NOT NULL UNIQUE,
    name VARCHAR NOT NULL,
    category VARCHAR,
    "goldType" VARCHAR NOT NULL,
    purity VARCHAR,
    "weightGram" NUMERIC(12, 3) NOT NULL DEFAULT 0,
    quantity INTEGER NOT NULL DEFAULT 1,
    "makingFee" NUMERIC(15, 2) NOT NULL DEFAULT 0,
    "stoneFee" NUMERIC(15, 2) NOT NULL DEFAULT 0,
    "costPrice" NUMERIC(15, 2) NOT NULL DEFAULT 0,
    status VARCHAR NOT NULL DEFAULT 'IN_STOCK',
    note TEXT,
    "createdAt" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE gold_price_histories (
    "priceID" SERIAL PRIMARY KEY,
    "branchID" INTEGER REFERENCES branches("branchID") ON DELETE CASCADE ON UPDATE CASCADE,
    "goldType" VARCHAR NOT NULL,
    "buyPricePerChi" NUMERIC(15, 2) NOT NULL,
    "sellPricePerChi" NUMERIC(15, 2) NOT NULL,
    "createdBy" INTEGER REFERENCES users("userID") ON DELETE SET NULL ON UPDATE CASCADE,
    "effectiveFrom" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE sale_orders (
    "saleID" SERIAL PRIMARY KEY,
    code VARCHAR NOT NULL UNIQUE,
    "branchID" INTEGER NOT NULL REFERENCES branches("branchID") ON DELETE CASCADE ON UPDATE CASCADE,
    "customerID" INTEGER REFERENCES customers("customerID") ON DELETE SET NULL ON UPDATE CASCADE,
    "productID" INTEGER NOT NULL REFERENCES gold_products("productID") ON DELETE CASCADE ON UPDATE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    "weightGram" NUMERIC(12, 3) NOT NULL,
    "goldType" VARCHAR NOT NULL,
    "sellPricePerChi" NUMERIC(15, 2) NOT NULL,
    "makingFee" NUMERIC(15, 2) NOT NULL DEFAULT 0,
    "stoneFee" NUMERIC(15, 2) NOT NULL DEFAULT 0,
    discount NUMERIC(15, 2) NOT NULL DEFAULT 0,
    "totalAmount" NUMERIC(15, 2) NOT NULL,
    "paymentMethod" VARCHAR NOT NULL DEFAULT 'CASH',
    "createdBy" INTEGER REFERENCES users("userID") ON DELETE SET NULL ON UPDATE CASCADE,
    "createdAt" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE purchase_orders (
    "purchaseID" SERIAL PRIMARY KEY,
    code VARCHAR NOT NULL UNIQUE,
    "branchID" INTEGER NOT NULL REFERENCES branches("branchID") ON DELETE CASCADE ON UPDATE CASCADE,
    "customerID" INTEGER REFERENCES customers("customerID") ON DELETE SET NULL ON UPDATE CASCADE,
    "goldType" VARCHAR NOT NULL,
    "weightGram" NUMERIC(12, 3) NOT NULL,
    "buyPricePerChi" NUMERIC(15, 2) NOT NULL,
    "totalAmount" NUMERIC(15, 2) NOT NULL,
    description TEXT,
    "paymentMethod" VARCHAR NOT NULL DEFAULT 'CASH',
    "createdBy" INTEGER REFERENCES users("userID") ON DELETE SET NULL ON UPDATE CASCADE,
    "createdAt" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);


CREATE TABLE online_orders (
    "onlineOrderID" SERIAL PRIMARY KEY,
    "branchID" INTEGER NOT NULL REFERENCES branches("branchID") ON DELETE CASCADE ON UPDATE CASCADE,
    "customerName" VARCHAR NOT NULL,
    "phoneNumber" VARCHAR NOT NULL,
    address VARCHAR,
    note TEXT,
    status VARCHAR NOT NULL DEFAULT 'PENDING',
    "totalAmount" NUMERIC(15, 2) NOT NULL DEFAULT 0,
    "createdAt" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE online_order_items (
    "onlineOrderItemID" SERIAL PRIMARY KEY,
    "onlineOrderID" INTEGER NOT NULL REFERENCES online_orders("onlineOrderID") ON DELETE CASCADE ON UPDATE CASCADE,
    "productID" INTEGER NOT NULL REFERENCES gold_products("productID") ON DELETE CASCADE ON UPDATE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    "unitPrice" NUMERIC(15, 2) NOT NULL,
    "makingFee" NUMERIC(15, 2) NOT NULL DEFAULT 0,
    "stoneFee" NUMERIC(15, 2) NOT NULL DEFAULT 0,
    "totalAmount" NUMERIC(15, 2) NOT NULL
);

CREATE TABLE inventory_movements (
    "movementID" SERIAL PRIMARY KEY,
    "branchID" INTEGER NOT NULL REFERENCES branches("branchID") ON DELETE CASCADE ON UPDATE CASCADE,
    "productID" INTEGER REFERENCES gold_products("productID") ON DELETE SET NULL ON UPDATE CASCADE,
    "movementType" VARCHAR NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    "weightGram" NUMERIC(12, 3) NOT NULL DEFAULT 0,
    "referenceType" VARCHAR,
    "referenceID" INTEGER,
    note TEXT,
    "createdBy" INTEGER REFERENCES users("userID") ON DELETE SET NULL ON UPDATE CASCADE,
    "createdAt" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_customers_branch ON customers("branchID");
CREATE INDEX idx_products_branch ON gold_products("branchID");
CREATE INDEX idx_products_sku ON gold_products(sku);
CREATE INDEX idx_prices_gold_type ON gold_price_histories("goldType");
CREATE INDEX idx_sales_branch ON sale_orders("branchID");
CREATE INDEX idx_purchases_branch ON purchase_orders("branchID");
CREATE INDEX idx_inventory_branch ON inventory_movements("branchID");
CREATE INDEX idx_online_orders_branch ON online_orders("branchID");
CREATE INDEX idx_online_orders_status ON online_orders(status);
CREATE INDEX idx_online_order_items_order ON online_order_items("onlineOrderID");
CREATE INDEX idx_online_order_items_product ON online_order_items("productID");

-- Password for all demo accounts is: 123456
-- Demo password for all accounts is stored as plain text: 123456
INSERT INTO branches ("branchID", code, name, "phoneNumber", address, active, "createdAt") VALUES
(1, 'HN001', 'Chi nhánh Hà Nội', '0900000001', 'Cầu Giấy, Hà Nội', TRUE, NOW()),
(2, 'HCM001', 'Chi nhánh Hồ Chí Minh', '0900000002', 'Quận 1, TP. Hồ Chí Minh', TRUE, NOW()),
(3, 'DN001', 'Chi nhánh Đà Nẵng', '0900000003', 'Hải Châu, Đà Nẵng', TRUE, NOW());

INSERT INTO users ("userID", "branchID", "fullName", email, password, role, active, "createdAt") VALUES
(1, NULL, 'Quản trị tổng chuỗi', 'admin@gold.local', '123456', 'ADMIN', TRUE, NOW()),
(2, NULL, 'Quản lý cấp cao', 'chain@gold.local', '123456', 'CHAIN_MANAGER', TRUE, NOW()),
(3, 1, 'Quản lý chi nhánh Hà Nội', 'manager.hn@gold.local', '123456', 'BRANCH_MANAGER', TRUE, NOW()),
(4, 1, 'Nhân viên bán hàng Hà Nội', 'employee.hn@gold.local', '123456', 'EMPLOYEE', TRUE, NOW()),
(5, 2, 'Quản lý chi nhánh Hồ Chí Minh', 'manager.hcm@gold.local', '123456', 'BRANCH_MANAGER', TRUE, NOW()),
(6, 3, 'Quản lý chi nhánh Đà Nẵng', 'manager.dn@gold.local', '123456', 'BRANCH_MANAGER', TRUE, NOW());

INSERT INTO customers ("customerID", "branchID", "fullName", "phoneNumber", "identityNumber", address, "createdAt") VALUES
(1, 1, 'Nguyễn Văn An', '0912345678', '001200000001', 'Hà Nội', NOW()),
(2, 1, 'Trần Thị Bình', '0987654321', '001200000002', 'Hà Nội', NOW()),
(3, 2, 'Lê Văn Cường', '0909123456', '079200000001', 'TP. Hồ Chí Minh', NOW()),
(4, 3, 'Phạm Thị Dung', '0933333333', '048200000001', 'Đà Nẵng', NOW());

INSERT INTO gold_price_histories ("priceID", "branchID", "goldType", "buyPricePerChi", "sellPricePerChi", "createdBy", "effectiveFrom") VALUES
(1, NULL, '9999', 8500000, 8650000, 1, NOW()),
(2, NULL, '24K', 8400000, 8600000, 1, NOW()),
(3, NULL, '18K', 5800000, 6100000, 1, NOW()),
(4, NULL, '14K', 4300000, 4700000, 1, NOW()),
(5, 1, '9999', 8520000, 8670000, 1, NOW()),
(6, 2, '9999', 8510000, 8660000, 1, NOW());

INSERT INTO gold_products (
    "productID", "branchID", sku, name, category, "goldType", purity, "weightGram",
    quantity, "makingFee", "stoneFee", "costPrice", status, note, "createdAt"
) VALUES
(1, 1, 'HN-NV9999-001', 'Nhẫn vàng 9999 trơn', 'Nhẫn', '9999', '99.99%', 3.750, 4, 300000, 0, 8400000, 'IN_STOCK', 'Dữ liệu ban đầu', NOW()),
(2, 1, 'HN-DC18K-001', 'Dây chuyền vàng 18K', 'Dây chuyền', '18K', '75%', 7.500, 2, 700000, 0, 11000000, 'IN_STOCK', 'Dữ liệu ban đầu', NOW()),
(3, 1, 'HN-BT14K-001', 'Bông tai vàng 14K', 'Bông tai', '14K', '58.5%', 2.250, 5, 250000, 150000, 3200000, 'IN_STOCK', 'Có đá trang trí', NOW()),
(4, 2, 'HCM-LT24K-001', 'Lắc tay vàng 24K', 'Lắc tay', '24K', '99.9%', 11.250, 2, 900000, 0, 25000000, 'IN_STOCK', 'Dữ liệu ban đầu', NOW()),
(5, 2, 'HCM-NV9999-002', 'Nhẫn cưới vàng 9999', 'Nhẫn cưới', '9999', '99.99%', 7.500, 2, 600000, 0, 16800000, 'IN_STOCK', 'Bộ nhẫn cưới', NOW()),
(6, 3, 'DN-MV9999-001', 'Vàng miếng 9999', 'Vàng miếng', '9999', '99.99%', 37.500, 3, 0, 0, 85000000, 'IN_STOCK', 'Vàng miếng 1 lượng', NOW()),
(7, 3, 'DN-DC18K-001', 'Dây chuyền vàng 18K nữ', 'Dây chuyền', '18K', '75%', 5.250, 3, 650000, 0, 8200000, 'IN_STOCK', 'Dữ liệu ban đầu', NOW());

INSERT INTO sale_orders (
    "saleID", code, "branchID", "customerID", "productID", quantity, "weightGram", "goldType",
    "sellPricePerChi", "makingFee", "stoneFee", discount, "totalAmount", "paymentMethod", "createdBy", "createdAt"
) VALUES
(1, 'BH202601010001', 1, 1, 1, 1, 3.750, '9999', 8670000, 300000, 0, 0, 8970000, 'CASH', 3, NOW()),
(2, 'BH202601010002', 2, 3, 4, 1, 11.250, '24K', 8600000, 900000, 0, 100000, 26600000, 'BANK_TRANSFER', 5, NOW());

INSERT INTO purchase_orders (
    "purchaseID", code, "branchID", "customerID", "goldType", "weightGram",
    "buyPricePerChi", "totalAmount", description, "paymentMethod", "createdBy", "createdAt"
) VALUES
(1, 'MV202601010001', 1, 2, '18K', 3.750, 5800000, 5800000, 'Mua lại nhẫn vàng 18K từ khách', 'CASH', 3, NOW()),
(2, 'MV202601010002', 3, 4, '9999', 7.500, 8500000, 17000000, 'Mua lại vàng 9999', 'BANK_TRANSFER', 6, NOW());


INSERT INTO online_orders (
    "onlineOrderID", "branchID", "customerName", "phoneNumber", address, note, status, "totalAmount", "createdAt", "updatedAt"
) VALUES
(1, 1, 'Khách online Hà Nội', '0911111111', 'Cầu Giấy, Hà Nội', 'Muốn giữ hàng đến cuối ngày', 'PENDING', 8970000, NOW(), NOW()),
(2, 2, 'Khách online Hồ Chí Minh', '0922222222', 'Quận 3, TP. Hồ Chí Minh', 'Liên hệ trước khi giao', 'CONFIRMED', 26400000, NOW(), NOW());

INSERT INTO online_order_items (
    "onlineOrderItemID", "onlineOrderID", "productID", quantity, "unitPrice", "makingFee", "stoneFee", "totalAmount"
) VALUES
(1, 1, 1, 1, 8970000, 300000, 0, 8970000),
(2, 2, 4, 1, 26400000, 900000, 0, 26400000);

INSERT INTO inventory_movements (
    "movementID", "branchID", "productID", "movementType", quantity, "weightGram",
    "referenceType", "referenceID", note, "createdBy", "createdAt"
) VALUES
(1, 1, 1, 'IMPORT', 4, 15.000, 'SQL_INIT', 1, 'Nhập dữ liệu ban đầu', 1, NOW()),
(2, 1, 2, 'IMPORT', 2, 15.000, 'SQL_INIT', 2, 'Nhập dữ liệu ban đầu', 1, NOW()),
(3, 1, 3, 'IMPORT', 5, 11.250, 'SQL_INIT', 3, 'Nhập dữ liệu ban đầu', 1, NOW()),
(4, 2, 4, 'IMPORT', 2, 22.500, 'SQL_INIT', 4, 'Nhập dữ liệu ban đầu', 1, NOW()),
(5, 2, 5, 'IMPORT', 2, 15.000, 'SQL_INIT', 5, 'Nhập dữ liệu ban đầu', 1, NOW()),
(6, 3, 6, 'IMPORT', 3, 112.500, 'SQL_INIT', 6, 'Nhập dữ liệu ban đầu', 1, NOW()),
(7, 3, 7, 'IMPORT', 3, 15.750, 'SQL_INIT', 7, 'Nhập dữ liệu ban đầu', 1, NOW()),
(8, 1, 1, 'SALE', -1, -3.750, 'SALE_ORDER', 1, 'Bán vàng BH202601010001', 3, NOW()),
(9, 2, 4, 'SALE', -1, -11.250, 'SALE_ORDER', 2, 'Bán vàng BH202601010002', 5, NOW()),
(10, 1, NULL, 'BUY_FROM_CUSTOMER', 1, 3.750, 'PURCHASE_ORDER', 1, 'Mua vàng từ khách MV202601010001', 3, NOW()),
(11, 3, NULL, 'BUY_FROM_CUSTOMER', 1, 7.500, 'PURCHASE_ORDER', 2, 'Mua vàng từ khách MV202601010002', 6, NOW());

-- Keep product quantities consistent with sale demo data.
UPDATE gold_products SET quantity = 3 WHERE "productID" = 1;
UPDATE gold_products SET quantity = 1 WHERE "productID" = 4;

SELECT setval(pg_get_serial_sequence('branches', 'branchID'), COALESCE((SELECT MAX("branchID") FROM branches), 1), true);
SELECT setval(pg_get_serial_sequence('users', 'userID'), COALESCE((SELECT MAX("userID") FROM users), 1), true);
SELECT setval(pg_get_serial_sequence('customers', 'customerID'), COALESCE((SELECT MAX("customerID") FROM customers), 1), true);
SELECT setval(pg_get_serial_sequence('gold_products', 'productID'), COALESCE((SELECT MAX("productID") FROM gold_products), 1), true);
SELECT setval(pg_get_serial_sequence('gold_price_histories', 'priceID'), COALESCE((SELECT MAX("priceID") FROM gold_price_histories), 1), true);
SELECT setval(pg_get_serial_sequence('sale_orders', 'saleID'), COALESCE((SELECT MAX("saleID") FROM sale_orders), 1), true);
SELECT setval(pg_get_serial_sequence('purchase_orders', 'purchaseID'), COALESCE((SELECT MAX("purchaseID") FROM purchase_orders), 1), true);
SELECT setval(pg_get_serial_sequence('inventory_movements', 'movementID'), COALESCE((SELECT MAX("movementID") FROM inventory_movements), 1), true);
SELECT setval(pg_get_serial_sequence('online_orders', 'onlineOrderID'), COALESCE((SELECT MAX("onlineOrderID") FROM online_orders), 1), true);
SELECT setval(pg_get_serial_sequence('online_order_items', 'onlineOrderItemID'), COALESCE((SELECT MAX("onlineOrderItemID") FROM online_order_items), 1), true);

COMMIT;
