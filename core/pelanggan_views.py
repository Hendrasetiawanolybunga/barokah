# core/pelanggan_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from .models import Pelanggan, Produk
from .pelanggan_forms import PelangganRegistrationForm, PelangganLoginForm, PelangganUpdateForm, PelangganPasswordForm
from django.http import HttpResponse

# ==================== AUTHENTIKASI PELANGGAN ====================

def pelanggan_home(request):
    """
    View placeholder untuk Beranda Pelanggan (target redirect setelah login)
    """
    if 'pelanggan_id' in request.session:
        pesan = f"Selamat datang kembali, {request.session.get('nama_pelanggan')}!"
    else:
        pesan = "Selamat datang di Portal Pelanggan UD Barokah Jaya Beton."

    return render(request, 'pelanggan/beranda_placeholder.html', {'pesan': pesan})

def register_pelanggan(request):
    if request.method == 'POST':
        form = PelangganRegistrationForm(request.POST)
        if form.is_valid():
            # Simpan user baru (password sudah di-hash di form.save())
            form.save()
            messages.success(request, 'Registrasi berhasil! Silakan masuk.')
            return redirect(reverse('login_pelanggan'))
    else:
        form = PelangganRegistrationForm()
        
    context = {'form': form}
    # Layout minimal, tanpa basis_web penuh
    return render(request, 'pelanggan/register_pelanggan.html', context)


def login_pelanggan(request):
    if request.method == 'POST':
        form = PelangganLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email']
            password = form.cleaned_data['password']

            try:
                # Cari Pelanggan berdasarkan username ATAU email
                pelanggan = Pelanggan.objects.get(
                    # Menggunakan Q object untuk OR query jika model tidak memiliki manager khusus
                    # Karena kita hanya menggunakan Django murni, kita gunakan try-except berantai
                    username=username_or_email
                )
            except Pelanggan.DoesNotExist:
                try:
                    pelanggan = Pelanggan.objects.get(email=username_or_email)
                except Pelanggan.DoesNotExist:
                    # User tidak ditemukan
                    pelanggan = None

            if pelanggan and check_password(password, pelanggan.password):
                # Password cocok, set data ke SESSION
                request.session['pelanggan_id'] = pelanggan.id
                request.session['nama_pelanggan'] = pelanggan.nama_pelanggan
                messages.success(request, f"Login berhasil! Selamat datang, {pelanggan.nama_pelanggan}.")
                # Redirect ke Beranda Pelanggan
                return redirect(reverse('home_web'))
            else:
                messages.error(request, "Username/Email atau Password salah.")

    else:
        form = PelangganLoginForm()

    context = {'form': form}
    return render(request, 'pelanggan/login_pelanggan.html', context)


def logout_pelanggan(request):

    if 'pelanggan_id' in request.session:
        # Hapus semua kunci sesi yang terkait dengan otentikasi pelanggan
        request.session.pop('pelanggan_id', None)
        request.session.pop('nama_pelanggan', None)
        
        # Hapus sesi keranjang jika ada (best practice)
        if 'cart' in request.session:
             request.session.pop('cart', None)
             
        messages.success(request, "Anda telah keluar.")
    
    # Redirect ke halaman login atau beranda
    return redirect(reverse('login_pelanggan'))



# Helper function untuk mendapatkan data keranjang (tetap diperlukan)
def get_cart_data(session):
    # Menginisialisasi keranjang jika belum ada (aman)
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session.get('cart', {})
    cart_items = []
    total_price = 0
    
    # Ambil detail produk dari DB
    for product_id, quantity in cart.items():
        try:
            produk = Produk.objects.get(id=int(product_id))
            subtotal = produk.harga_produk * quantity
            total_price += subtotal
            
            cart_items.append({
                'id': produk.id,
                'nama': produk.nama_produk,
                'harga': produk.harga_produk,
                'kuantitas': quantity,
                'subtotal': subtotal,
                'gambar': produk.foto_produk.url if produk.foto_produk else '/static/images/default.png'
            })
        except Produk.DoesNotExist:
            # Hapus item dari sesi jika produk tidak ditemukan (data usang)
            del session['cart'][product_id]
            session.modified = True
            
    return {'cart_items': cart_items, 'total_price': total_price, 'cart_count': len(cart)}


def beranda_pelanggan(request):
    # 1. Pastikan inisialisasi sesi keranjang (best practice)
    if 'cart' not in request.session:
        request.session['cart'] = {}
        
    # 2. Query Produk Unggulan/Terbaru (max 4 item, stok > 0)
    try:
        featured_products = Produk.objects.filter(stok_produk__gt=0).order_by('-id')[:4]
    except Exception:
        featured_products = [] # Handle jika tabel Produk belum ada atau error query
        
    # 3. Ambil data keranjang untuk Navbar
    cart_data = get_cart_data(request.session)

    context = {
        'featured_products': featured_products,
        'cart_count': cart_data['cart_count'],
        'is_logged_in': 'pelanggan_id' in request.session,
    }
    return render(request, 'web/beranda.html', context)


def daftar_produk(request):
    # Query semua produk yang memiliki stok > 0
    produk_list = Produk.objects.filter(stok_produk__gt=0).order_by('nama_produk')
    cart_data = get_cart_data(request.session)

    context = {
        'produk_list': produk_list,
        'cart_count': cart_data['cart_count'],
        'is_logged_in': 'pelanggan_id' in request.session,
    }
    return render(request, 'web/list_produk.html', context)


def detail_produk(request, id):
    # Menggunakan ID produk
    produk = get_object_or_404(Produk, id=id, stok_produk__gt=0)
    cart_data = get_cart_data(request.session)

    context = {
        'produk': produk,
        'cart_count': cart_data['cart_count'],
        'is_logged_in': 'pelanggan_id' in request.session,
    }
    return render(request, 'web/detail_produk.html', context)

# Tambahkan view keranjang (walaupun Modul 3, diperlukan untuk Navbar)
def keranjang_web(request):
    cart_data = get_cart_data(request.session)
    
    context = {
        'cart_data': cart_data,
        'cart_count': cart_data['cart_count'],
        'is_logged_in': 'pelanggan_id' in request.session,
    }
    return render(request, 'web/keranjang.html', context)




# core/pelanggan_views.py (Tambahan dan Modifikasi)

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db import transaction, models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import Pelanggan, Produk, Transaksi, DetailTransaksi # Import model baru
from .pelanggan_forms import PelangganRegistrationForm, PelangganLoginForm

# Helper function get_cart_data (sudah ada, pastikan menggunakan Decimal)
def get_cart_data(session):
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session.get('cart', {})
    cart_items = []
    total_price = Decimal(0.00)
    
    # Ambil detail produk dari DB
    for product_id, quantity in cart.items():
        try:
            produk = Produk.objects.get(id=int(product_id), stok_produk__gt=0)
            
            # Pastikan kuantitas di sesi tidak melebihi stok yang ada
            if quantity > produk.stok_produk:
                quantity = produk.stok_produk
                session['cart'][product_id] = quantity
                session.modified = True
            
            subtotal = produk.harga_produk * quantity
            total_price += subtotal
            
            cart_items.append({
                'id': produk.id,
                'nama': produk.nama_produk,
                'harga': produk.harga_produk,
                'kuantitas': quantity,
                'subtotal': subtotal,
                'gambar': produk.foto_produk.url if produk.foto_produk else '/static/images/default.png',
                'stok_tersedia': produk.stok_produk,
            })
        except Produk.DoesNotExist:
            del session['cart'][product_id]
            session.modified = True
            
    # Hitung ulang jumlah item (cart_count)
    cart_count = sum(item['kuantitas'] for item in cart_items)
    
    return {'cart_items': cart_items, 'total_price': total_price, 'cart_count': cart_count}

# ==================== VIEWS KERANJANG (POST MURNI) ====================

# 1. ADD TO CART
def add_to_cart(request, id):
    # Pastikan ini adalah POST request
    if request.method != 'POST':
        return redirect(reverse('detail_produk_web', args=[id]))

    produk = get_object_or_404(Produk, id=id)
    
    try:
        # Ambil kuantitas dari form, default ke 1
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            raise ValueError()
    except ValueError:
        messages.error(request, "Kuantitas tidak valid.")
        return redirect(reverse('detail_produk_web', args=[id]))

    # Inisialisasi/ambil keranjang sesi
    cart = request.session.get('cart', {})
    product_id_str = str(id)
    
    # Hitung kuantitas total yang diminta
    current_quantity = cart.get(product_id_str, 0)
    new_total_quantity = current_quantity + quantity
    
    if new_total_quantity > produk.stok_produk:
        messages.error(request, f"Stok produk ({produk.nama_produk}) tidak cukup. Maksimal: {produk.stok_produk}")
    else:
        cart[product_id_str] = new_total_quantity
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, f"{quantity} unit {produk.nama_produk} berhasil ditambahkan ke keranjang.")
    
    # Selalu redirect kembali ke halaman detail setelah aksi
    return redirect(reverse('detail_produk_web', args=[id]))


# 2. UPDATE CART (di halaman keranjang)
def update_cart(request, id):
    if request.method != 'POST':
        return redirect(reverse('keranjang_web'))
        
    produk = get_object_or_404(Produk, id=id)
    cart = request.session.get('cart', {})
    product_id_str = str(id)

    try:
        new_quantity = int(request.POST.get('quantity', 0))
        if new_quantity < 0:
            raise ValueError()
    except ValueError:
        messages.error(request, "Kuantitas tidak valid.")
        return redirect(reverse('keranjang_web'))

    if new_quantity == 0:
        # Jika kuantitas 0, hapus item
        if product_id_str in cart:
            del cart[product_id_str]
            messages.success(request, f"Produk {produk.nama_produk} berhasil dihapus dari keranjang.")
    elif new_quantity > produk.stok_produk:
        messages.error(request, f"Stok ({produk.nama_produk}) tidak cukup. Maksimal: {produk.stok_produk}")
        # Biarkan kuantitas lama
    else:
        cart[product_id_str] = new_quantity
        messages.success(request, f"Kuantitas {produk.nama_produk} berhasil diperbarui menjadi {new_quantity}.")

    request.session['cart'] = cart
    request.session.modified = True
    return redirect(reverse('keranjang_web'))


# 3. REMOVE FROM CART (di halaman keranjang)
def remove_from_cart(request, id):
    if request.method != 'POST':
        return redirect(reverse('keranjang_web'))
        
    cart = request.session.get('cart', {})
    product_id_str = str(id)
    
    if product_id_str in cart:
        produk = get_object_or_404(Produk, id=id)
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, f"Produk {produk.nama_produk} berhasil dihapus dari keranjang.")
    
    return redirect(reverse('keranjang_web'))


# 4. CHECKOUT (Perlu Login)
def checkout_web(request):
    if 'pelanggan_id' not in request.session:
        messages.warning(request, "Anda harus login untuk melanjutkan proses Checkout.")
        return redirect(reverse('login_pelanggan') + f"?next={reverse('checkout_web')}")
        
    cart_data = get_cart_data(request.session)
    
    if not cart_data['cart_count'] > 0:
        messages.error(request, "Keranjang Anda kosong.")
        return redirect(reverse('keranjang_web'))

    pelanggan = get_object_or_404(Pelanggan, id=request.session['pelanggan_id'])
    
    # REVISI KRITIS: Ongkir diatur menjadi 0.00 dan akan diinput manual oleh Admin.
    ongkir = Decimal(0.00) 
    
    # REVISI KRITIS: Total akhir hanya subtotal produk
    final_total = cart_data['total_price'] + ongkir # Sekarang sama dengan total_price
    
    if request.method == 'POST':
        # Logika pemrosesan final: Simpan Transaksi dan DetailTransaksi
        alamat_pengiriman = request.POST.get('alamat_pengiriman', pelanggan.alamat)
        
        try:
            with transaction.atomic():
                batas_waktu_bayar = timezone.now() + timedelta(hours=24)
                
                # 1. Buat instance Transaksi
                transaksi = Transaksi.objects.create(
                    pelanggan=pelanggan,
                    tanggal=timezone.now().date(),
                    # Total diisi dengan subtotal produk, Admin yang akan update total akhir setelah input ongkir
                    total=final_total, 
                    # Ongkir diset 0.00
                    ongkir=ongkir, 
                    status_transaksi='pending',
                    alamat_pengiriman=alamat_pengiriman,
                    batas_waktu_bayar=batas_waktu_bayar,
                    total_diskon=Decimal(0.00),
                )
                
                # 2. Iterasi Keranjang untuk Detail Transaksi dan Update Stok
                # ... (Logika DetailTransaksi dan Update Stok sama seperti sebelumnya) ...
                for item in cart_data['cart_items']:
                    produk = Produk.objects.get(id=item['id'])
                    DetailTransaksi.objects.create(
                        transaksi=transaksi,
                        produk=produk,
                        jumlah_produk=item['kuantitas'],
                        sub_total=item['subtotal']
                    )
                    produk.stok_produk -= item['kuantitas']
                    produk.save()
                    
                # 3. Hapus Keranjang Sesi
                del request.session['cart']
                request.session.modified = True
                
                messages.success(request, f"Checkout berhasil! Pesanan Anda ({transaksi.id}) telah dibuat. Biaya pengiriman akan dihitung Admin. Selesaikan pembayaran sebelum {batas_waktu_bayar.strftime('%d %b %Y %H:%M')}")
                # Redirect ke halaman detail transaksi (placeholder)
                return redirect(reverse('home_web')) 
                
        except Exception as e:
            messages.error(request, f"Terjadi kesalahan sistem: {e}")
            return redirect(reverse('checkout_web'))


    # GET request untuk menampilkan form checkout
    context = {
        'cart_data': cart_data,
        'ongkir': ongkir, # Tetap 0.00
        'final_total': final_total, # Sekarang hanya total produk
        'pelanggan': pelanggan,
        'cart_count': cart_data['cart_count'],
        'is_logged_in': True,
    }
    return render(request, 'web/checkout.html', context)


# core/pelanggan_views.py (Tambahan Views)

from django.db.models import Sum # Import untuk aggregasi

# Fungsi helper (Pastikan sudah ada atau tambahkan)
def login_required_web(view_func):
    """Decorator sederhana untuk memastikan pelanggan sudah login."""
    def wrapper(request, *args, **kwargs):
        if 'pelanggan_id' not in request.session:
            messages.warning(request, "Anda harus login untuk mengakses halaman ini.")
            # Redirect ke login dengan parameter next
            current_path = request.path
            return redirect(reverse('login_pelanggan') + f"?next={current_path}")
        return view_func(request, *args, **kwargs)
    return wrapper


# ==================== VIEWS RIWAYAT PESANAN (MODUL 4) ====================

@login_required_web
def daftar_pesanan_pelanggan(request):
    pelanggan_id = request.session['pelanggan_id']
    
    # Ambil semua transaksi milik pelanggan, diurutkan dari yang terbaru
    pesanan_list = Transaksi.objects.filter(
        pelanggan_id=pelanggan_id
    ).order_by('-waktu_checkout')
    
    # Ambil data keranjang untuk navbar
    cart_data = get_cart_data(request.session)

    context = {
        'pesanan_list': pesanan_list,
        'cart_count': cart_data['cart_count'],
        'is_logged_in': True,
    }
    return render(request, 'web/riwayat_pesanan.html', context)


@login_required_web
def detail_pesanan_pelanggan(request, pk):
    pelanggan_id = request.session['pelanggan_id']
    
    # Ambil transaksi berdasarkan PK, pastikan milik pelanggan yang sedang login
    transaksi = get_object_or_404(
        Transaksi, 
        pk=pk, 
        pelanggan_id=pelanggan_id
    )
    
    # Ambil detail transaksi (item-item)
    detail_items = DetailTransaksi.objects.filter(transaksi=transaksi)
    
    # Ambil data keranjang untuk navbar
    cart_data = get_cart_data(request.session)

    context = {
        'transaksi': transaksi,
        'detail_items': detail_items,
        'cart_count': cart_data['cart_count'],
        'is_logged_in': True,
    }
    return render(request, 'web/detail_pesanan.html', context)


# core/pelanggan_views.py (Tambahan Views)

from django.contrib.auth.hashers import make_password # Untuk menyimpan password baru

# ... (Definisi login_required_web di atas) ...
# ... (Import PelangganUpdateForm, PelangganPasswordForm) ...


# ==================== VIEWS AKUN SAYA (MODUL 5) ====================

@login_required_web
def akun_saya(request):
    pelanggan_id = request.session['pelanggan_id']
    pelanggan = get_object_or_404(Pelanggan, id=pelanggan_id)
    cart_data = get_cart_data(request.session)

    # 1. Form Update Profil
    if request.method == 'POST' and 'update_profil' in request.POST:
        profile_form = PelangganUpdateForm(request.POST, instance=pelanggan)
        if profile_form.is_valid():
            profile_form.save()
            # Update nama di sesi jika nama_pelanggan berubah
            request.session['nama_pelanggan'] = profile_form.cleaned_data['nama_pelanggan']
            request.session.modified = True
            messages.success(request, 'Data profil Anda berhasil diperbarui.')
            return redirect(reverse('akun_saya'))
    else:
        profile_form = PelangganUpdateForm(instance=pelanggan)
    
    # 2. Form Ganti Password
    if request.method == 'POST' and 'update_password' in request.POST:
        password_form = PelangganPasswordForm(request.POST, pelanggan=pelanggan)
        if password_form.is_valid():
            new_password = password_form.cleaned_data['password_baru']
            # Hash dan Simpan Password Baru
            pelanggan.password = make_password(new_password)
            pelanggan.save()
            messages.success(request, 'Password Anda berhasil diubah. Silakan login ulang.')
            # Logout user untuk memaksa login dengan password baru
            return redirect(reverse('logout_pelanggan')) 
    else:
        password_form = PelangganPasswordForm(pelanggan=pelanggan)

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'pelanggan': pelanggan,
        'cart_count': cart_data['cart_count'],
        'is_logged_in': True,
    }
    return render(request, 'web/akun_saya.html', context)