from django import forms
from .models import Admin, Pelanggan, Kategori, Produk, Transaksi, DetailTransaksi, DiskonPelanggan, Notifikasi
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm

from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password

class AdminLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nama Pengguna Admin'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kata Sandi'
        })
    )


class PelangganForm(forms.ModelForm):
    # Make password optional
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    
    class Meta:
        model = Pelanggan
        fields = ['nama_pelanggan', 'alamat', 'tanggal_lahir', 'no_hp', 'username', 'password', 'email']
        widgets = {
            'nama_pelanggan': forms.TextInput(attrs={'class': 'form-control'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tanggal_lahir': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'no_hp': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If this is an edit form, make password optional
        if self.instance and self.instance.pk:
            self.fields['password'].required = False

    def save(self, commit=True):
        pelanggan = super().save(commit=False)
        # Only update password if it's provided
        if self.cleaned_data.get('password'):
            # Since Pelanggan is not a Django User model, we store password as plain text
            # In a production environment, you should implement proper password hashing
            pelanggan.password = self.cleaned_data['password']
        if commit:
            pelanggan.save()
        return pelanggan


class KategoriForm(forms.ModelForm):
    class Meta:
        model = Kategori
        fields = ['nama_kategori']
        widgets = {
            'nama_kategori': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProdukForm(forms.ModelForm):
    class Meta:
        model = Produk
        fields = ['nama_produk', 'deskripsi_produk', 'foto_produk', 'stok_produk', 'harga_produk', 'kategori']
        widgets = {
            'nama_produk': forms.TextInput(attrs={'class': 'form-control'}),
            'deskripsi_produk': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'foto_produk': forms.FileInput(attrs={'class': 'form-control'}),
            'stok_produk': forms.NumberInput(attrs={'class': 'form-control'}),
            'harga_produk': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'kategori': forms.Select(attrs={'class': 'form-control'}),
        }


class TransaksiForm(forms.ModelForm):
    class Meta:
        model = Transaksi
        fields = [
            'tanggal', 'total', 'ongkir', 'status_transaksi', 'bukti_bayar',
            'pelanggan', 'alamat_pengiriman', 'batas_waktu_bayar', 'total_diskon', 'keterangan_diskon'
        ]
        widgets = {
            'tanggal': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ongkir': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status_transaksi': forms.Select(attrs={'class': 'form-control'}),
            'bukti_bayar': forms.FileInput(attrs={'class': 'form-control'}),
            'pelanggan': forms.Select(attrs={'class': 'form-control'}),
            'alamat_pengiriman': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'batas_waktu_bayar': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'total_diskon': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'keterangan_diskon': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TransaksiBaruForm(forms.ModelForm):
    class Meta:
        model = Transaksi
        fields = ['pelanggan', 'alamat_pengiriman', 'status_transaksi'] 
        widgets = {
            'pelanggan': forms.Select(attrs={'class': 'form-control'}),
            'alamat_pengiriman': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status_transaksi': forms.Select(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default status
        self.fields['status_transaksi'].initial = 'pending'


class DiskonPelangganForm(forms.ModelForm):
    class Meta:
        model = DiskonPelanggan
        fields = ['pelanggan', 'produk', 'persen_diskon', 'status', 'pesan', 'end_time']
        widgets = {
            'pelanggan': forms.Select(attrs={'class': 'form-control'}),
            'produk': forms.Select(attrs={'class': 'form-control'}),
            'persen_diskon': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'pesan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class NotifikasiForm(forms.ModelForm):
    class Meta:
        model = Notifikasi
        fields = ['pelanggan', 'tipe_pesan', 'isi_pesan', 'is_read']
        widgets = {
            'pelanggan': forms.Select(attrs={'class': 'form-control'}),
            'tipe_pesan': forms.TextInput(attrs={'class': 'form-control'}),
            'isi_pesan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_read': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Konfirmasi Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Pelanggan
        fields = ['nama_pelanggan', 'alamat', 'tanggal_lahir', 'no_hp', 'username', 'email']
        widgets = {
            'nama_pelanggan': forms.TextInput(attrs={'class': 'form-control'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tanggal_lahir': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'no_hp': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords tidak cocok")
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = self.cleaned_data["password1"]
        if commit:
            user.save()
        return user
