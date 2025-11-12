from django.urls import path
from . import views
from . import pelanggan_views 
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
    path('pelanggan/login/', pelanggan_views.login_pelanggan, name='login_pelanggan'),
    path('pelanggan/register/', pelanggan_views.register_pelanggan, name='register_pelanggan'),
    path('pelanggan/logout/', pelanggan_views.logout_pelanggan, name='logout_pelanggan'),
    path('pelanggan/', pelanggan_views.pelanggan_home, name='home_pelanggan'),
    
    
    path('web/', pelanggan_views.beranda_pelanggan, name='home_web'), # Alias untuk beranda
    path('web/produk/', pelanggan_views.daftar_produk, name='daftar_produk_web'),
    path('web/produk/<int:id>/', pelanggan_views.detail_produk, name='detail_produk_web'),
    path('web/keranjang/', pelanggan_views.keranjang_web, name='keranjang_web'),
    
    path('web/keranjang/add/<int:id>/', pelanggan_views.add_to_cart, name='add_to_cart'),
    path('web/keranjang/update/<int:id>/', pelanggan_views.update_cart, name='update_cart'),
    path('web/keranjang/remove/<int:id>/', pelanggan_views.remove_from_cart, name='remove_from_cart'),
    path('web/checkout/', pelanggan_views.checkout_web, name='checkout_web'),
    
    path('web/pesanan/', pelanggan_views.daftar_pesanan_pelanggan, name='daftar_pesanan_pelanggan'),
    path('web/pesanan/<int:pk>/', pelanggan_views.detail_pesanan_pelanggan, name='detail_pesanan_pelanggan'),
    
    path('web/akun/', pelanggan_views.akun_saya, name='akun_saya'),
]