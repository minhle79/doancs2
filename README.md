# ComputerStore (Django)

Website bán máy tính đơn giản với Django + SQLite.

## Tính năng
- Danh sách sản phẩm, tìm kiếm, lọc theo danh mục/hãng/giá
- Chi tiết sản phẩm (ảnh, thông số, mô tả, giá, tồn kho)
- Giỏ hàng (session) thêm/xóa/sửa số lượng với kiểm tra tồn kho
- Thanh toán đơn giản, tạo đơn hàng và giảm tồn kho
- Đăng ký / đăng nhập người dùng (Django Auth)
- Trang quản trị (Django Admin) thêm/sửa/xóa sản phẩm
- API JSON: `/api/products/`, `/api/suggest/`
- Kiểm tra tồn kho khi thêm vào giỏ và đặt hàng

## Cài đặt và chạy

1) Tạo môi trường ảo và cài phụ thuộc
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2) (Tuỳ chọn) Cấu hình biến môi trường
```bash
# Copy file .env.example thành .env và chỉnh sửa theo nhu cầu
copy .env.example .env
```

3) Tạo migrations cho app và migrate, sau đó tạo tài khoản admin
```bash
python manage.py makemigrations store
python manage.py migrate
python manage.py createsuperuser
```

4) Nạp dữ liệu mẫu (tuỳ chọn)
```bash
python manage.py loaddata store/fixtures/sample_data.json
```

5) Chạy server
```bash
python manage.py runserver
```

- Trang chủ: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## Cấu trúc chính
- `computer_store/` cấu hình dự án (settings, urls, wsgi)
- `store/` logic cửa hàng: models, views, urls, forms, cart
- `templates/` giao diện HTML (home, detail, cart, checkout, auth)
- `static/` CSS, ảnh placeholder

## Ghi chú mở rộng
- File `store/cart.py` dùng session (`CART_SESSION_KEY = "cart"`).
- Có thể thêm upload ảnh cho `Product.image` (cấu hình MEDIA_* đã bật khi DEBUG).
- Để triển khai production: đặt `DEBUG=False`, cấu hình `ALLOWED_HOSTS`, staticfiles, và SECRET_KEY qua biến môi trường.

