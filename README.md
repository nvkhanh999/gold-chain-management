# Gold Chain Management

Dự án web quản lý giao dịch mua bán vàng cho chuỗi cửa hàng vàng bạc.

Hệ thống gồm backend FastAPI, database PostgreSQL, giao diện Admin quản lý toàn chuỗi, giao diện Center quản lý từng cửa hàng và giao diện Shop dành cho khách hàng mua hàng trực tuyến.

## Yêu cầu cài đặt

Máy cần cài Docker Desktop và Docker Compose.

Kiểm tra Docker bằng lệnh:

docker version

Nếu Docker chưa chạy, hãy mở Docker Desktop trước rồi mới chạy project.

## Cách chạy project

Mở terminal tại thư mục có file `docker-compose.yml`, sau đó chạy:

docker compose up --build

Nếu đã từng chạy bản cũ, nên reset database trước:

docker compose down -v --remove-orphans
docker compose up --build

Sau khi chạy thành công, mở trình duyệt và truy cập:

Admin:  http://localhost:8000/admin
Center: http://localhost:8000/center
Shop:   http://localhost:8000/shop
API:    http://localhost:8000/docs

## Tài khoản mẫu

Admin:
Email: admin@gold.local
Password: 123456

Quản lý cửa hàng:
Email: manager.hn@gold.local
Password: 123456

Nhân viên cửa hàng:
Email: employee.hn@gold.local
Password: 123456


## Nếu gặp lỗi trùng container:

container name "/gold_postgres" is already in use

Chạy:

docker rm -f gold_postgres
docker compose up --build


## Dừng project và xóa database cũ:

docker compose down -v
