# Barokah Admin Dashboard

Custom Django administration dashboard for the Barokah e-commerce system.

## Features

- Custom admin authentication system
- Full CRUD operations for all models:
  - Pelanggan (Customers)
  - Produk (Products)
  - Kategori (Categories)
  - Transaksi (Transactions)
  - Diskon (Discounts)
  - Notifikasi (Notifications)
- Dashboard with statistics and summaries
- Responsive design using Bootstrap 5
- Modal confirmations for delete operations
- Pagination for list views
- Flash messages for user feedback

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv myenv
   ```
3. Activate the virtual environment:
   - On Windows: `myenv\Scripts\activate`
   - On macOS/Linux: `source myenv/bin/activate`
4. Install dependencies:
   ```
   pip install django
   ```
5. Run migrations:
   ```
   python manage.py migrate
   ```
6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
7. Start the development server:
   ```
   python manage.py runserver
   ```

## Usage

1. Access the admin dashboard at: http://127.0.0.1:8000/admin-panel/masuk/
2. Login with your superuser credentials
3. Navigate through the sidebar menu to manage different entities

## Models

### Admin
Custom user model for administrators with nama_lengkap field.

### Pelanggan (Customer)
- nama_pelanggan: Customer name
- alamat: Address
- tanggal_lahir: Date of birth
- no_hp: Phone number
- username: Unique username
- password: Password (hashed)
- email: Unique email
- created_at: Registration timestamp

### Kategori (Category)
- nama_kategori: Unique category name

### Produk (Product)
- nama_produk: Product name
- deskripsi_produk: Product description
- foto_produk: Product image (optional)
- stok_produk: Stock quantity
- harga_produk: Price
- kategori: Foreign key to Kategori

### Transaksi (Transaction)
- tanggal: Transaction date
- total: Total amount
- ongkir: Shipping cost
- status_transaksi: Transaction status (pending, dibayar, dikirim, selesai, dibatalkan)
- bukti_bayar: Payment proof (optional)
- pelanggan: Foreign key to Pelanggan
- alamat_pengiriman: Shipping address
- feedback: Customer feedback (optional)
- fotofeedback: Feedback image (optional)
- waktu_checkout: Checkout timestamp
- batas_waktu_bayar: Payment deadline
- total_diskon: Total discount
- keterangan_diskon: Discount description (optional)

### DetailTransaksi (Transaction Detail)
- transaksi: Foreign key to Transaksi
- produk: Foreign key to Produk
- jumlah_produk: Quantity
- sub_total: Subtotal amount

### DiskonPelanggan (Customer Discount)
- pelanggan: Foreign key to Pelanggan
- produk: Foreign key to Produk (optional)
- persen_diskon: Discount percentage
- status: Discount status (aktif, tidak_aktif)
- pesan: Discount message
- tanggal_dibuat: Creation timestamp
- end_time: Expiration timestamp

### Notifikasi (Notification)
- pelanggan: Foreign key to Pelanggan
- tipe_pesan: Message type
- isi_pesan: Message content
- is_read: Read status
- created_at: Creation timestamp

## URLs

- `/admin-panel/masuk/` - Admin login
- `/admin-panel/keluar/` - Admin logout
- `/admin-panel/` - Dashboard
- `/admin-panel/pelanggan/` - Customer list
- `/admin-panel/pelanggan/tambah/` - Add customer
- `/admin-panel/pelanggan/<id>/` - Customer detail
- `/admin-panel/pelanggan/<id>/edit/` - Edit customer
- `/admin-panel/pelanggan/<id>/hapus/` - Delete customer
- `/admin-panel/produk/` - Product list
- `/admin-panel/produk/tambah/` - Add product
- `/admin-panel/produk/<id>/` - Product detail
- `/admin-panel/produk/<id>/edit/` - Edit product
- `/admin-panel/produk/<id>/hapus/` - Delete product
- And similar patterns for other models

## Templates

All templates are located in `core/templates/core/` with subdirectories for each model:
- `basis.html` - Base template with sidebar and navigation
- `login_admin.html` - Admin login page
- `dashboard_utama.html` - Main dashboard
- Model-specific templates in respective subdirectories

## Static Files

CSS and JavaScript files are located in `core/static/core/`:
- `css/app.css` - Custom styles
- `js/app.js` - Custom JavaScript

## Security

- All admin views are protected with `@login_required` decorator
- Passwords are hashed using Django's built-in authentication system
- CSRF protection is enabled for all forms