# AI Agent Instructions for ComputerStore

## Project Overview
This is a Django-based e-commerce site for selling computers with core features like product listing, cart management, and checkout. The project uses SQLite for storage and Django's built-in authentication.

## Key Architecture Components

### Data Models (`store/models.py`)
- `Product`: Core product model with fields for name, price, stock, specs (JSON), and flags (is_featured, is_hot, is_deal)
- `Category` and `Brand`: Product categorization
- `Order` and `OrderItem`: Order management with customer details

### Cart System (`store/cart.py`)
- Session-based cart implementation (`CART_SESSION_KEY = "cart"`)
- Cart data structure: `Dict[str, dict]` where key is product_id
- Methods: add, remove, clear, total calculation
- Products prices always fetched from DB to reflect updates

### URL Structure (`store/urls.py`)
- Main pages: home, products list, product detail
- Cart operations: view, add, remove
- Checkout process
- API endpoints: `/api/products/`, `/api/suggest/`

## Development Workflows

### Setup Commands
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

### Loading Sample Data
```bash
python manage.py loaddata store/fixtures/sample_data.json
```

### Development Server
```bash
python manage.py runserver
```
Access at http://127.0.0.1:8000/ and admin at /admin/

## Project Conventions

### Media Handling
- Product images stored in `media/products/`
- Media configuration ready when `DEBUG=True`

### Database Protection
- Using `models.PROTECT` for foreign keys to prevent cascading deletes
- Careful stock management in checkout process

### Frontend Integration
- Template inheritance from base layout
- Cart interactions via modal (`templates/store/partials/cart_modal.html`)
- Static files in `static/` (css, js, img)

## Common Tasks

### Adding New Product Fields
1. Update `Product` model in `store/models.py`
2. Create and run migrations
3. Update admin if needed (`store/admin.py`)
4. Modify templates to display new fields

### Modifying Cart Behavior
- Cart logic centralized in `store/cart.py`
- Session handling via Django's session middleware
- Update related views in `store/views.py` for new cart features