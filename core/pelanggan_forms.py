# core/pelanggan_forms.py

from django import forms
from .models import Pelanggan # Asumsi models.py berada di direktori yang sama
from django.contrib.auth.hashers import make_password, check_password

# ==================== REGISTRASI PELANGGAN ====================

class PelangganRegistrationForm(forms.ModelForm):
    # Field tambahan untuk konfirmasi password
    password2 = forms.CharField(
        label='Konfirmasi Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ulangi Password Anda'})
    )

    class Meta:
        model = Pelanggan
        fields = ['nama_pelanggan', 'alamat', 'tanggal_lahir', 'no_hp', 'username', 'email', 'password']
        widgets = {
            'nama_pelanggan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Lengkap'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Alamat Lengkap', 'rows': 3}),
            'tanggal_lahir': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'no_hp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor HP Aktif'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username unik'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Alamat Email'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        }

    def clean(self):
        # Panggil clean() dari parent untuk validasi dasar
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise forms.ValidationError("Password tidak cocok.")
        
        return cleaned_data

    def save(self, commit=True):
        # Ambil instance Pelanggan
        pelanggan = super().save(commit=False)
        # Hash password sebelum menyimpan
        pelanggan.password = make_password(self.cleaned_data["password"])
        
        if commit:
            pelanggan.save()
        return pelanggan

# ==================== LOGIN PELANGGAN ====================

class PelangganLoginForm(forms.Form):
    # Menggunakan username atau email
    username_or_email = forms.CharField(
        label='Username atau Email',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username atau Email Anda'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    
    # Tidak perlu clean() di sini, validasi dilakukan di view
    
    
# core/pelanggan_forms.py (Tambahan dan Modifikasi)

from django import forms
from .models import Pelanggan
from django.contrib.auth.hashers import check_password # Untuk verifikasi password lama

class PelangganUpdateForm(forms.ModelForm):
    # Field yang bisa diubah oleh pelanggan
    class Meta:
        model = Pelanggan
        fields = ['nama_pelanggan', 'alamat', 'tanggal_lahir', 'no_hp']
        widgets = {
            'tanggal_lahir': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'alamat': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'nama_pelanggan': forms.TextInput(attrs={'class': 'form-control'}),
            'no_hp': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nama_pelanggan': 'Nama Lengkap',
            'no_hp': 'Nomor Handphone',
        }

# Form khusus untuk ganti password (lebih aman)
class PelangganPasswordForm(forms.Form):
    password_lama = forms.CharField(label='Password Lama', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_baru = forms.CharField(label='Password Baru', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    konfirmasi_password_baru = forms.CharField(label='Konfirmasi Password Baru', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        # Ambil instance pelanggan jika ada
        self.pelanggan = kwargs.pop('pelanggan', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        password_lama = cleaned_data.get("password_lama")
        password_baru = cleaned_data.get("password_baru")
        konfirmasi_password_baru = cleaned_data.get("konfirmasi_password_baru")

        # 1. Verifikasi Password Lama
        if self.pelanggan and password_lama:
            # Menggunakan check_password dari Django untuk verifikasi hash
            if not check_password(password_lama, self.pelanggan.password):
                self.add_error('password_lama', 'Password lama yang dimasukkan salah.')
        
        # 2. Verifikasi Konfirmasi Password Baru
        if password_baru and konfirmasi_password_baru and password_baru != konfirmasi_password_baru:
            self.add_error('konfirmasi_password_baru', "Konfirmasi password baru tidak cocok.")

        return cleaned_data