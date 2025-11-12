from django.urls import path
from . import views

urlpatterns = [
    # Autentikasi Admin
    path('masuk/', views.admin_login, name='admin_login'),
    path('keluar/', views.admin_logout, name='admin_logout'),
    
    # Dashboard Utama
    path('', views.dashboard_utama, name='dashboard_utama'),
    
    # Laporan
    path('laporan/', views.laporan_utama, name='laporan_utama'),
    path('laporan/transaksi/pdf/', views.cetak_laporan_transaksi_pdf, name='cetak_laporan_transaksi_pdf'),
    path('laporan/loyal/pdf/', views.cetak_laporan_loyal_pdf, name='cetak_laporan_loyal_pdf'),
    
    # Tambah Transaksi Baru
    path('transaksi/tambah/', views.tambah_transaksi_baru, name='tambah_transaksi_baru'),
    
    # Edit Transaksi
    path('transaksi/<int:pk>/edit/', views.edit_transaksi, name='edit_transaksi'),
    
    # CRUD Pelanggan
    path('pelanggan/', views.daftar_pelanggan, name='daftar_pelanggan'),
    path('pelanggan/tambah/', views.tambah_pelanggan, name='tambah_pelanggan'),
    path('pelanggan/<int:pk>/edit/', views.edit_pelanggan, name='edit_pelanggan'),
    path('pelanggan/<int:pk>/', views.detail_pelanggan, name='detail_pelanggan'),
    path('pelanggan/<int:pk>/hapus/', views.hapus_pelanggan, name='hapus_pelanggan'),
    
    # CRUD Produk
    path('produk/', views.daftar_produk, name='daftar_produk'),
    path('produk/tambah/', views.tambah_produk, name='tambah_produk'),
    path('produk/<int:pk>/edit/', views.edit_produk, name='edit_produk'),
    path('produk/<int:pk>/', views.detail_produk, name='detail_produk'),
    path('produk/<int:pk>/hapus/', views.hapus_produk, name='hapus_produk'),
    
    # CRUD Kategori
    path('kategori/', views.daftar_kategori, name='daftar_kategori'),
    path('kategori/tambah/', views.tambah_kategori, name='tambah_kategori'),
    path('kategori/<int:pk>/edit/', views.edit_kategori, name='edit_kategori'),
    path('kategori/<int:pk>/hapus/', views.hapus_kategori, name='hapus_kategori'),
    
    # CRUD Transaksi
    path('transaksi/', views.daftar_transaksi, name='daftar_transaksi'),
    path('transaksi/<int:pk>/', views.detail_transaksi, name='detail_transaksi'),
    path('transaksi/<int:pk>/hapus/', views.hapus_transaksi, name='hapus_transaksi'),
    
    # CRUD Diskon
    path('diskon/', views.daftar_diskon, name='daftar_diskon'),
    path('diskon/tambah/', views.tambah_diskon, name='tambah_diskon'),
    path('diskon/<int:pk>/edit/', views.edit_diskon, name='edit_diskon'),
    path('diskon/<int:pk>/hapus/', views.hapus_diskon, name='hapus_diskon'),
    
    # CRUD Notifikasi
    path('notifikasi/', views.daftar_notifikasi, name='daftar_notifikasi'),
    path('notifikasi/tambah/', views.tambah_notifikasi, name='tambah_notifikasi'),
    path('notifikasi/<int:pk>/edit/', views.edit_notifikasi, name='edit_notifikasi'),
    path('notifikasi/<int:pk>/hapus/', views.hapus_notifikasi, name='hapus_notifikasi'),
    
    # ==================== PORTAL PELANGGAN ====================
    # Web Portal URLs
    path('web/', views.beranda_pelanggan, name='beranda_pelanggan'),
    path('web/produk/', views.daftar_produk_web, name='daftar_produk_web'),
    path('web/produk/<int:id>/', views.detail_produk_web, name='detail_produk_web'),
    path('web/keranjang/', views.keranjang_web, name='keranjang_web'),
    
    # Web Portal Authentication
    path('web/login/', views.login_web, name='login_web'),
    path('web/register/', views.register_web, name='register_web'),
    path('web/logout/', views.logout_web, name='logout_web'),
    path('web/akun/', views.akun_saya_web, name='akun_saya_web'),
    
    # Cart AJAX endpoints
    path('web/add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
]