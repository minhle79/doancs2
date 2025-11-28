# ComputerStore - Django E-commerce

Website bán máy tính với Django + SQLite, bao gồm trang quản trị (admin) chuyên nghiệp với dark mode.

## ✨ Tính năng

### Frontend (Khách hàng)
- 🛍️ Danh sách sản phẩm với tìm kiếm, lọc theo danh mục/hãng/giá
- 📱 Chi tiết sản phẩm (ảnh, thông số, mô tả, giá, tồn kho)
- 🛒 Giỏ hàng (session-based) với kiểm tra tồn kho real-time
- 💳 Thanh toán đơn giản, tạo đơn hàng tự động
- 👤 Đăng ký / đăng nhập người dùng
- 📊 Lịch sử đơn hàng và quản lý profile
- 🔍 API JSON: `/api/products/`, `/api/suggest/`

### Admin Panel (Quản trị)
- 🎨 Giao diện dark mode chuyên nghiệp
- 📊 Dashboard với thống kê và biểu đồ (Chart.js)
- 📦 Quản lý sản phẩm, danh mục, thương hiệu
- 🛒 Quản lý đơn hàng và khách hàng
- 🎯 Custom widgets cho thông số sản phẩm
- ⚡ Quick actions và keyboard shortcuts
- 📈 Theo dõi tồn kho và cảnh báo sắp hết hàng

## 🚀 Cài đặt và chạy

### 1. Clone và setup môi trường
```bash
# Tạo môi trường ảo
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### 2. Cấu hình (Tuỳ chọn)
```bash
# Copy file .env.example thành .env
copy .env.example .env  # Windows
# hoặc
cp .env.example .env    # Linux/Mac

# Chỉnh sửa .env theo nhu cầu
```

### 3. Database setup
```bash
# Tạo migrations và migrate
python manage.py makemigrations store
python manage.py migrate

# Tạo tài khoản admin
python manage.py createsuperuser

# (Tuỳ chọn) Nạp dữ liệu mẫu
python manage.py loaddata store/fixtures/sample_data.json
```

### 4. Chạy server
```bash
python manage.py runserver
```

- 🏠 Trang chủ: http://127.0.0.1:8000/
- ⚙️ Admin: http://127.0.0.1:8000/admin/

## 📁 Cấu trúc dự án

```
doancs2/
├── computer_store/         # Django project settings
│   ├── settings.py        # Cấu hình chính
│   ├── urls.py           # URL routing chính
│   └── wsgi.py           # WSGI config
├── store/                 # App chính
│   ├── models.py         # Models: Product, Order, Category, Brand
│   ├── views.py          # Views xử lý requests
│   ├── urls.py           # URL patterns của app
│   ├── admin.py          # Admin customization
│   ├── admin_site.py     # Custom admin site
│   ├── cart.py           # Cart logic (session-based)
│   ├── forms.py          # Forms
│   ├── fixtures/         # Dữ liệu mẫu
│   ├── migrations/       # Database migrations
│   └── templates/        # Templates của app
├── templates/            # Templates global
│   ├── admin/           # Admin templates
│   │   ├── index.html   # Dashboard
│   │   └── base_site.html
│   ├── registration/    # Auth templates
│   └── store/          # Store templates
├── static/              # Static files
│   ├── admin/          # Admin static files
│   │   ├── css/       # Custom admin CSS
│   │   └── js/        # Custom admin JS
│   ├── css/           # Frontend CSS
│   ├── js/            # Frontend JS
│   └── img/           # Images
├── media/              # User uploads
│   └── products/      # Product images
├── .env               # Environment variables
├── .gitignore        # Git ignore rules
├── clean.py          # Cleanup script
├── manage.py         # Django management
└── requirements.txt  # Python dependencies
```

## 🧹 Maintenance

### Làm sạch dự án
```bash
# Xóa cache và __pycache__
python clean.py

# Hoặc thủ công
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
```

### Tạo migrations mới
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collect static files (production)
```bash
python manage.py collectstatic
```

## 🛠️ Tech Stack

- **Backend**: Django 5.0.6
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Charts**: Chart.js 4.4.0
- **Authentication**: Django Auth
- **Session**: Django Sessions

## 📝 License

This project is for educational purposes.

- `computer_store/` cấu hình dự án (settings, urls, wsgi)
- `store/` logic cửa hàng: models, views, urls, forms, cart
- `templates/` giao diện HTML (home, detail, cart, checkout, auth)
- `static/` CSS, ảnh placeholder

## Ghi chú mở rộng
- File `store/cart.py` dùng session (`CART_SESSION_KEY = "cart"`).
- Có thể thêm upload ảnh cho `Product.image` (cấu hình MEDIA_* đã bật khi DEBUG).
- Để triển khai production: đặt `DEBUG=False`, cấu hình `ALLOWED_HOSTS`, staticfiles, và SECRET_KEY qua biến môi trường.

## Nạp dữ liệu vào dữ liệu mẫu
```bash
python manage.py dumpdata store > store/fixtures/sample_data.json
```