from django.contrib import admin
from .models import Admin, Pelanggan, Kategori, Produk, Transaksi, DetailTransaksi, DiskonPelanggan, Notifikasi

# Register your models here.
admin.site.register(Admin)
admin.site.register(Pelanggan)
admin.site.register(Kategori)
admin.site.register(Produk)
admin.site.register(Transaksi)
admin.site.register(DetailTransaksi)
admin.site.register(DiskonPelanggan)
admin.site.register(Notifikasi)