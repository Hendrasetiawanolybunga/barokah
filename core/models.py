from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import os
from datetime import date


class Admin(AbstractUser):
    nama_lengkap = models.CharField(max_length=100)

    def __str__(self):
        return self.nama_lengkap


class Pelanggan(models.Model):
    nama_pelanggan = models.CharField(max_length=100)
    alamat = models.TextField()
    tanggal_lahir = models.DateField()
    no_hp = models.CharField(max_length=15)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama_pelanggan


class Kategori(models.Model):
    nama_kategori = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nama_kategori

    class Meta:
        verbose_name_plural = "Kategori"


class Produk(models.Model):
    nama_produk = models.CharField(max_length=100)
    deskripsi_produk = models.TextField()
    foto_produk = models.ImageField(upload_to='produk/', blank=True, null=True)
    stok_produk = models.IntegerField(default=0)
    harga_produk = models.DecimalField(max_digits=10, decimal_places=2)
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE)

    def __str__(self):
        return self.nama_produk


class Transaksi(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('dibayar', 'Dibayar'),
        ('dikirim', 'Dikirim'),
        ('selesai', 'Selesai'),
        ('dibatalkan', 'Dibatalkan'),
    ]

    tanggal = models.DateTimeField(default=date.today)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    ongkir = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status_transaksi = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    bukti_bayar = models.FileField(upload_to='bukti_bayar/', blank=True, null=True)
    pelanggan = models.ForeignKey(Pelanggan, on_delete=models.CASCADE)
    alamat_pengiriman = models.TextField()
    feedback = models.TextField(blank=True, null=True)
    fotofeedback = models.ImageField(upload_to='feedback/', blank=True, null=True)
    waktu_checkout = models.DateTimeField(auto_now_add=True)
    batas_waktu_bayar = models.DateTimeField()
    total_diskon = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    keterangan_diskon = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Transaksi {self.id} - {self.pelanggan.nama_pelanggan}"


class DetailTransaksi(models.Model):
    transaksi = models.ForeignKey(Transaksi, on_delete=models.CASCADE)
    produk = models.ForeignKey(Produk, on_delete=models.CASCADE)
    jumlah_produk = models.IntegerField()
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detail {self.transaksi.id} - {self.produk.nama_produk}"


class DiskonPelanggan(models.Model):
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('tidak_aktif', 'Tidak Aktif'),
    ]

    pelanggan = models.ForeignKey(Pelanggan, on_delete=models.CASCADE)
    produk = models.ForeignKey(Produk, on_delete=models.CASCADE, null=True, blank=True)
    persen_diskon = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')
    pesan = models.TextField()
    tanggal_dibuat = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()

    def __str__(self):
        return f"Diskon untuk {self.pelanggan.nama_pelanggan}"


class Notifikasi(models.Model):
    pelanggan = models.ForeignKey(Pelanggan, on_delete=models.CASCADE)
    tipe_pesan = models.CharField(max_length=50)
    isi_pesan = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notifikasi untuk {self.pelanggan.nama_pelanggan}"

    class Meta:
        verbose_name_plural = "Notifikasi"
