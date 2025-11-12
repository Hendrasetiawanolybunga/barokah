from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Sum, F
from django.db.models.functions import TruncMonth
from .models import Admin, Pelanggan, Kategori, Produk, Transaksi, DetailTransaksi, DiskonPelanggan, Notifikasi
from .forms import AdminLoginForm, PelangganForm, KategoriForm, ProdukForm, TransaksiForm, DiskonPelangganForm, NotifikasiForm
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime
from django.db.models import Q
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from io import BytesIO
import calendar

# Halaman login admin
def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Selamat datang kembali, {user.nama_lengkap}!')
                return redirect('dashboard_utama')
            else:
                messages.error(request, 'Nama pengguna atau kata sandi salah.')
        else:
            messages.error(request, 'Form tidak valid. Silakan periksa kembali.')
    else:
        form = AdminLoginForm()
    
    return render(request, 'core/login_admin.html', {'form': form})


# Logout admin
@login_required
def admin_logout(request):
    logout(request)
    messages.info(request, 'Anda telah berhasil keluar.')
    return redirect('admin_login')


# Dashboard utama
@login_required
def dashboard_utama(request):
    # Statistik dashboard
    total_pelanggan = Pelanggan.objects.count()
    total_produk = Produk.objects.count()
    total_kategori = Kategori.objects.count()
    total_transaksi = Transaksi.objects.count()
    
    # Pendapatan total
    pendapatan_total = Transaksi.objects.filter(status_transaksi='selesai').aggregate(
        total=Sum('total')
    )['total'] or 0
    
    # Transaksi terbaru
    transaksi_terbaru = Transaksi.objects.select_related('pelanggan').order_by('-waktu_checkout')[:5]
    
    # Kategori dengan produk terbanyak
    kategori_produk = Kategori.objects.annotate(jumlah_produk=Count('produk')).order_by('-jumlah_produk')[:5]
    
    # Data untuk grafik pendapatan bulanan (6 bulan terakhir)
    from django.utils import timezone
    from datetime import timedelta
    
    # Menghitung 6 bulan terakhir
    sekarang = timezone.now()
    data_bulan = []
    data_pendapatan = []
    
    for i in range(5, -1, -1):  # 6 bulan terakhir (0-5)
        tanggal_awal = sekarang.replace(day=1) - timedelta(days=30 * i)
        tanggal_akhir = (tanggal_awal.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
        # Format nama bulan dalam bahasa Indonesia
        nama_bulan = tanggal_awal.strftime("%b")
        if nama_bulan == "Jan":
            nama_bulan = "Jan"
        elif nama_bulan == "Feb":
            nama_bulan = "Feb"
        elif nama_bulan == "Mar":
            nama_bulan = "Mar"
        elif nama_bulan == "Apr":
            nama_bulan = "Apr"
        elif nama_bulan == "May":
            nama_bulan = "Mei"
        elif nama_bulan == "Jun":
            nama_bulan = "Jun"
        elif nama_bulan == "Jul":
            nama_bulan = "Jul"
        elif nama_bulan == "Aug":
            nama_bulan = "Agu"
        elif nama_bulan == "Sep":
            nama_bulan = "Sep"
        elif nama_bulan == "Oct":
            nama_bulan = "Okt"
        elif nama_bulan == "Nov":
            nama_bulan = "Nov"
        elif nama_bulan == "Dec":
            nama_bulan = "Des"
        
        # Hitung total pendapatan untuk bulan ini
        total_bulan = Transaksi.objects.filter(
            status_transaksi='selesai',
            tanggal__gte=tanggal_awal,
            tanggal__lte=tanggal_akhir
        ).aggregate(total=Sum('total'))['total'] or 0
        
        data_bulan.append(nama_bulan)
        data_pendapatan.append(float(total_bulan))
    
    context = {
        'total_pelanggan': total_pelanggan,
        'total_produk': total_produk,
        'total_kategori': total_kategori,
        'total_transaksi': total_transaksi,
        'pendapatan_total': pendapatan_total,
        'transaksi_terbaru': transaksi_terbaru,
        'kategori_produk': kategori_produk,
        'data_bulan': data_bulan,
        'data_pendapatan': data_pendapatan,
    }
    
    return render(request, 'core/dashboard_utama.html', context)


# ==================== LAPORAN ====================
@login_required
def laporan_utama(request):
    # Filter options
    bulan_filter = request.GET.get('bulan')
    tahun_filter = request.GET.get('tahun')
    status_filter = request.GET.get('status')
    
    # Laporan transaksi
    transaksi_queryset = Transaksi.objects.select_related('pelanggan')
    
    # KOREKSI FILTER: Pastikan hanya transaksi dengan tanggal yang valid
    transaksi_queryset = transaksi_queryset.exclude(tanggal__isnull=True)
    
    if bulan_filter and tahun_filter and bulan_filter != 'None' and tahun_filter != 'None':
        transaksi_queryset = transaksi_queryset.filter(
            tanggal__year=tahun_filter,
            tanggal__month=bulan_filter
        )
    
    if status_filter and status_filter != 'None':
        transaksi_queryset = transaksi_queryset.filter(status_transaksi=status_filter)
    
    # Laporan pelanggan loyal (pelanggan dengan total pembelian >= 5.000.000 dan status selesai)
    pelanggan_loyal = Pelanggan.objects.annotate(
        jumlah_transaksi=Count('transaksi', filter=Q(transaksi__status_transaksi='selesai')),
        total_pembelian=Sum('transaksi__total', filter=Q(transaksi__status_transaksi='selesai'))
    ).filter(
        jumlah_transaksi__gt=0,
        total_pembelian__gte=5000000
    ).order_by('-total_pembelian')
    
    # Statistik bulanan
    transaksi_bulanan = Transaksi.objects.annotate(
        bulan=TruncMonth('tanggal')
    ).values('bulan').annotate(
        total=Sum('total'),
        jumlah=Count('id')
    ).order_by('bulan')
    
    # KOREKSI: Ambil daftar tahun yang unik dan terurut dari transaksi
    list_tahun = Transaksi.objects.exclude(tanggal__isnull=True).dates('tanggal', 'year').order_by('tanggal__year').values_list('tanggal__year', flat=True).distinct()
    
    context = {
        'transaksi_list': transaksi_queryset,
        'pelanggan_loyal': pelanggan_loyal,
        'transaksi_bulanan': transaksi_bulanan,
        'bulan_filter': bulan_filter,
        'tahun_filter': tahun_filter,
        'status_filter': status_filter,
        'status_choices': Transaksi.STATUS_CHOICES,
        'list_tahun': list_tahun,  # Tambahkan daftar tahun yang unik dan terurut
    }
    
    return render(request, 'core/laporan_utama.html', context)


# ==================== TAMBAH TRANSAKSI BARU ====================
@login_required
def tambah_transaksi_baru(request):
    if request.method == 'POST':
        form = TransaksiBaruForm(request.POST)
        if form.is_valid():
            # Simpan transaksi dasar
            transaksi = form.save(commit=False)
            
            # Set nilai otomatis
            transaksi.total = 0
            transaksi.ongkir = 0
            transaksi.total_diskon = 0
            transaksi.tanggal = timezone.now().date()
            transaksi.batas_waktu_bayar = timezone.now() + timezone.timedelta(days=1)
            transaksi.save()
            
            # Proses detail transaksi
            produk_items = []
            for key in request.POST.keys():
                # Cari key yang dimulai dengan 'produk_' (e.g., produk_0, produk_1)
                if key.startswith('produk_'):
                    index = key.split('_')[1]
                    produk_id = request.POST.get(key)
                    jumlah = request.POST.get(f'jumlah_produk_{index}')
                    
                    if produk_id and jumlah:
                        produk_items.append({
                            'produk_id': produk_id,
                            'jumlah': jumlah
                        })
            
            if not produk_items:
                messages.error(request, 'Transaksi gagal dibuat: Detail produk kosong.')
                transaksi.delete()  # Hapus transaksi yang gagal
                return redirect('tambah_transaksi_baru')
                
            total_transaksi = 0
            detail_transaksi_objects = []
            for item in produk_items:
                produk = get_object_or_404(Produk, id=item['produk_id'])
                jumlah = int(item['jumlah'])
                sub_total = produk.harga_produk * jumlah
                
                # Create detail transaksi object
                detail_transaksi = DetailTransaksi(
                    transaksi=transaksi,
                    produk=produk,
                    jumlah_produk=jumlah,
                    sub_total=sub_total
                )
                detail_transaksi_objects.append(detail_transaksi)
                
                total_transaksi += sub_total
            
            # Bulk create detail transaksi
            DetailTransaksi.objects.bulk_create(detail_transaksi_objects)
            
            # Update total transaksi
            transaksi.total = total_transaksi
            transaksi.save()
            
            # Kurangi stok produk
            for item in produk_items:
                produk = get_object_or_404(Produk, id=item['produk_id'])
                jumlah = int(item['jumlah'])
                # Kurangi stok produk menggunakan F() expression untuk keamanan
                Produk.objects.filter(id=produk.id).update(stok_produk=F('stok_produk') - jumlah)
            
            messages.success(request, 'Transaksi baru berhasil ditambahkan.')
            return redirect('daftar_transaksi')
    else:
        form = TransaksiBaruForm()
    
    # GET request - tampilkan form
    pelanggan_list = Pelanggan.objects.all()
    produk_list = Produk.objects.all()
    
    context = {
        'form': form,
        'pelanggan_list': pelanggan_list,
        'produk_list': produk_list,
    }
    
    return render(request, 'core/transaksi/form_transaksi_baru.html', context)


# ==================== EDIT TRANSAKSI ====================
@login_required
def edit_transaksi(request, pk):
    transaksi = get_object_or_404(Transaksi, pk=pk)
    detail_transaksi_list = DetailTransaksi.objects.filter(transaksi=transaksi)
    
    if request.method == 'POST':
        # Ambil status transaksi lama
        old_status = Transaksi.objects.get(pk=pk).status_transaksi
        form = TransaksiForm(request.POST, request.FILES, instance=transaksi)
        if form.is_valid():
            # Simpan transaksi
            transaksi = form.save()
            
            # Ambil status transaksi baru
            new_status = form.cleaned_data['status_transaksi']
            
            # Implementasi logika kompleks untuk stok
            # Jika old_status != 'dibatalkan' DAN new_status == 'dibatalkan': Kembalikan Stok
            if old_status != 'dibatalkan' and new_status == 'dibatalkan':
                # Kembalikan stok untuk semua produk dalam transaksi ini
                detail_transaksi_items = DetailTransaksi.objects.filter(transaksi=transaksi)
                for detail in detail_transaksi_items:
                    Produk.objects.filter(id=detail.produk.id).update(stok_produk=F('stok_produk') + detail.jumlah_produk)
            
            # Jika old_status == 'dibatalkan' DAN new_status != 'dibatalkan': Kurangi Stok
            elif old_status == 'dibatalkan' and new_status != 'dibatalkan':
                # Kurangi stok untuk semua produk dalam transaksi ini
                detail_transaksi_items = DetailTransaksi.objects.filter(transaksi=transaksi)
                for detail in detail_transaksi_items:
                    Produk.objects.filter(id=detail.produk.id).update(stok_produk=F('stok_produk') - detail.jumlah_produk)
            
            # Proses detail transaksi
            # Hapus detail yang ada
            DetailTransaksi.objects.filter(transaksi=transaksi).delete()
            
            # Tambahkan detail baru
            produk_keys = [key for key in request.POST.keys() if key.startswith('produk_')]
            total_transaksi = 0
            detail_transaksi_objects = []
            
            for key in produk_keys:
                detail_id = key.split('_')[1]
                produk_id = request.POST.get(key)
                jumlah = request.POST.get(f'jumlah_{detail_id}')
                
                if produk_id and jumlah:
                    produk = get_object_or_404(Produk, id=produk_id)
                    jumlah = int(jumlah)
                    sub_total = produk.harga_produk * jumlah
                    
                    # Create detail transaksi object
                    detail_transaksi = DetailTransaksi(
                        transaksi=transaksi,
                        produk=produk,
                        jumlah_produk=jumlah,
                        sub_total=sub_total
                    )
                    detail_transaksi_objects.append(detail_transaksi)
                    
                    total_transaksi += sub_total
            
            # Bulk create detail transaksi
            DetailTransaksi.objects.bulk_create(detail_transaksi_objects)
            
            # Update total transaksi
            transaksi.total = total_transaksi
            transaksi.save()
            
            messages.success(request, 'Data transaksi berhasil diperbarui.')
            return redirect('daftar_transaksi')
    else:
        form = TransaksiForm(instance=transaksi)
    
    # GET request - tampilkan form
    pelanggan_list = Pelanggan.objects.all()
    produk_list = Produk.objects.all()
    
    context = {
        'form': form,
        'title': 'Edit Transaksi',
        'transaksi': transaksi,
        'detail_transaksi_list': detail_transaksi_list,
        'pelanggan_list': pelanggan_list,
        'produk_list': produk_list,
    }
    
    return render(request, 'core/transaksi/form_transaksi.html', context)


# ==================== CRUD PELANGGAN ====================
@login_required
def daftar_pelanggan(request):
    pelanggan_list = Pelanggan.objects.all().order_by('-created_at')
    paginator = Paginator(pelanggan_list, 10)  # Tampilkan 10 item per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/pelanggan/daftar_pelanggan.html', {'page_obj': page_obj})


@login_required
def tambah_pelanggan(request):
    if request.method == 'POST':
        form = PelangganForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pelanggan berhasil ditambahkan.')
            return redirect('daftar_pelanggan')
    else:
        form = PelangganForm()
    
    return render(request, 'core/pelanggan/form_pelanggan.html', {'form': form, 'title': 'Tambah Pelanggan'})


@login_required
def edit_pelanggan(request, pk):
    pelanggan = get_object_or_404(Pelanggan, pk=pk)
    if request.method == 'POST':
        form = PelangganForm(request.POST, instance=pelanggan)
        if form.is_valid():
            # Save the form but preserve the password if not provided
            pelanggan_form = form.save(commit=False)
            # If password is not provided in the form, keep the existing one
            if not form.cleaned_data.get('password'):
                # Get the existing password from the database
                existing_pelanggan = Pelanggan.objects.get(pk=pk)
                pelanggan_form.password = existing_pelanggan.password
            pelanggan_form.save()
            messages.success(request, 'Data pelanggan berhasil diperbarui.')
            return redirect('daftar_pelanggan')
    else:
        form = PelangganForm(instance=pelanggan)
        # Clear the password field for security reasons
        form.fields['password'].initial = ''
    
    return render(request, 'core/pelanggan/form_pelanggan.html', {
        'form': form, 
        'title': 'Edit Pelanggan',
        'pelanggan': pelanggan
    })


@login_required
def detail_pelanggan(request, pk):
    pelanggan = get_object_or_404(Pelanggan, pk=pk)
    return render(request, 'core/pelanggan/detail_pelanggan.html', {'pelanggan': pelanggan})


@login_required
def hapus_pelanggan(request, pk):
    pelanggan = get_object_or_404(Pelanggan, pk=pk)
    if request.method == 'POST':
        pelanggan.delete()
        messages.success(request, 'Pelanggan berhasil dihapus.')
        return redirect('daftar_pelanggan')
    
    return render(request, 'core/pelanggan/hapus_pelanggan.html', {'pelanggan': pelanggan})


# ==================== CRUD PRODUK ====================
@login_required
def daftar_produk(request):
    produk_list = Produk.objects.select_related('kategori').all().order_by('-id')
    paginator = Paginator(produk_list, 10)  # Tampilkan 10 item per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/produk/daftar_produk.html', {'page_obj': page_obj})


@login_required
def tambah_produk(request):
    if request.method == 'POST':
        form = ProdukForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produk berhasil ditambahkan.')
            return redirect('daftar_produk')
    else:
        form = ProdukForm()
    
    return render(request, 'core/produk/form_produk.html', {'form': form, 'title': 'Tambah Produk'})


@login_required
def edit_produk(request, pk):
    produk = get_object_or_404(Produk, pk=pk)
    if request.method == 'POST':
        form = ProdukForm(request.POST, request.FILES, instance=produk)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data produk berhasil diperbarui.')
            return redirect('daftar_produk')
    else:
        form = ProdukForm(instance=produk)
    
    return render(request, 'core/produk/form_produk.html', {
        'form': form, 
        'title': 'Edit Produk',
        'produk': produk
    })


@login_required
def detail_produk(request, pk):
    produk = get_object_or_404(Produk, pk=pk)
    return render(request, 'core/produk/detail_produk.html', {'produk': produk})


@login_required
def hapus_produk(request, pk):
    produk = get_object_or_404(Produk, pk=pk)
    if request.method == 'POST':
        produk.delete()
        messages.success(request, 'Produk berhasil dihapus.')
        return redirect('daftar_produk')
    
    return render(request, 'core/produk/hapus_produk.html', {'produk': produk})


# ==================== CRUD KATEGORI ====================
@login_required
def daftar_kategori(request):
    kategori_list = Kategori.objects.all().order_by('nama_kategori')
    paginator = Paginator(kategori_list, 10)  # Tampilkan 10 item per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/kategori/daftar_kategori.html', {'page_obj': page_obj})


@login_required
def tambah_kategori(request):
    if request.method == 'POST':
        form = KategoriForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori berhasil ditambahkan.')
            return redirect('daftar_kategori')
    else:
        form = KategoriForm()
    
    return render(request, 'core/kategori/form_kategori.html', {'form': form, 'title': 'Tambah Kategori'})


@login_required
def edit_kategori(request, pk):
    kategori = get_object_or_404(Kategori, pk=pk)
    if request.method == 'POST':
        form = KategoriForm(request.POST, instance=kategori)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data kategori berhasil diperbarui.')
            return redirect('daftar_kategori')
    else:
        form = KategoriForm(instance=kategori)
    
    return render(request, 'core/kategori/form_kategori.html', {
        'form': form, 
        'title': 'Edit Kategori',
        'kategori': kategori
    })


@login_required
def hapus_kategori(request, pk):
    kategori = get_object_or_404(Kategori, pk=pk)
    if request.method == 'POST':
        kategori.delete()
        messages.success(request, 'Kategori berhasil dihapus.')
        return redirect('daftar_kategori')
    
    return render(request, 'core/kategori/hapus_kategori.html', {'kategori': kategori})


# ==================== CRUD TRANSAKSI ====================
@login_required
def daftar_transaksi(request):
    transaksi_list = Transaksi.objects.select_related('pelanggan').order_by('-id')
    paginator = Paginator(transaksi_list, 10)  # Tampilkan 10 item per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/transaksi/daftar_transaksi.html', {'page_obj': page_obj})


@login_required
def detail_transaksi(request, pk):
    transaksi = get_object_or_404(Transaksi, pk=pk)
    detail_transaksi = DetailTransaksi.objects.filter(transaksi=transaksi).select_related('produk')
    return render(request, 'core/transaksi/detail_transaksi.html', {
        'transaksi': transaksi,
        'detail_transaksi': detail_transaksi
    })


@login_required
def hapus_transaksi(request, pk):
    transaksi = get_object_or_404(Transaksi, pk=pk)
    if request.method == 'POST':
        transaksi.delete()
        messages.success(request, 'Transaksi berhasil dihapus.')
        return redirect('daftar_transaksi')
    
    return render(request, 'core/transaksi/hapus_transaksi.html', {'transaksi': transaksi})


# ==================== CRUD DISKON ====================
@login_required
def daftar_diskon(request):
    diskon_list = DiskonPelanggan.objects.select_related('pelanggan', 'produk').all().order_by('-tanggal_dibuat')
    paginator = Paginator(diskon_list, 10)  # Tampilkan 10 item per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/diskon/daftar_diskon.html', {'page_obj': page_obj})


@login_required
def tambah_diskon(request):
    if request.method == 'POST':
        form = DiskonPelangganForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Diskon berhasil ditambahkan.')
            return redirect('daftar_diskon')
    else:
        form = DiskonPelangganForm()
    
    return render(request, 'core/diskon/form_diskon.html', {'form': form, 'title': 'Tambah Diskon'})


@login_required
def edit_diskon(request, pk):
    diskon = get_object_or_404(DiskonPelanggan, pk=pk)
    if request.method == 'POST':
        form = DiskonPelangganForm(request.POST, instance=diskon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data diskon berhasil diperbarui.')
            return redirect('daftar_diskon')
    else:
        form = DiskonPelangganForm(instance=diskon)
    
    return render(request, 'core/diskon/form_diskon.html', {
        'form': form, 
        'title': 'Edit Diskon',
        'diskon': diskon
    })


@login_required
def hapus_diskon(request, pk):
    diskon = get_object_or_404(DiskonPelanggan, pk=pk)
    if request.method == 'POST':
        diskon.delete()
        messages.success(request, 'Diskon berhasil dihapus.')
        return redirect('daftar_diskon')
    
    return render(request, 'core/diskon/hapus_diskon.html', {'diskon': diskon})


# ==================== CRUD NOTIFIKASI ====================
@login_required
def daftar_notifikasi(request):
    notifikasi_list = Notifikasi.objects.select_related('pelanggan').all().order_by('-created_at')
    paginator = Paginator(notifikasi_list, 10)  # Tampilkan 10 item per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/notifikasi/daftar_notifikasi.html', {'page_obj': page_obj})


@login_required
def tambah_notifikasi(request):
    if request.method == 'POST':
        form = NotifikasiForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notifikasi berhasil ditambahkan.')
            return redirect('daftar_notifikasi')
    else:
        form = NotifikasiForm()
    
    return render(request, 'core/notifikasi/form_notifikasi.html', {'form': form, 'title': 'Tambah Notifikasi'})


@login_required
def edit_notifikasi(request, pk):
    notifikasi = get_object_or_404(Notifikasi, pk=pk)
    if request.method == 'POST':
        form = NotifikasiForm(request.POST, instance=notifikasi)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data notifikasi berhasil diperbarui.')
            return redirect('daftar_notifikasi')
    else:
        form = NotifikasiForm(instance=notifikasi)
    
    return render(request, 'core/notifikasi/form_notifikasi.html', {
        'form': form, 
        'title': 'Edit Notifikasi',
        'notifikasi': notifikasi
    })


@login_required
def hapus_notifikasi(request, pk):
    notifikasi = get_object_or_404(Notifikasi, pk=pk)
    if request.method == 'POST':
        notifikasi.delete()
        messages.success(request, 'Notifikasi berhasil dihapus.')
        return redirect('daftar_notifikasi')
    
    return render(request, 'core/notifikasi/hapus_notifikasi.html', {'notifikasi': notifikasi})


# ==================== CETAK LAPORAN PDF ====================
@login_required
def cetak_laporan_transaksi_pdf(request):
    # Get filter parameters
    bulan_filter = request.GET.get('bulan')
    tahun_filter = request.GET.get('tahun')
    status_filter = request.GET.get('status')
    
    # Filter transactions
    transaksi_queryset = Transaksi.objects.select_related('pelanggan')
    
    # KOREKSI ERROR 500: PASTIKAN FILTER BERISI DATA NUMERIK YANG VALID
    if bulan_filter and tahun_filter and bulan_filter != 'None' and tahun_filter != 'None' and bulan_filter.isdigit() and tahun_filter.isdigit():
        transaksi_queryset = transaksi_queryset.filter(
            tanggal__year=int(tahun_filter),
            tanggal__month=int(bulan_filter)
        )
    
    # KOREKSI ERROR 500: PASTIKAN STATUS FILTER VALID
    if status_filter and status_filter != 'None':
        transaksi_queryset = transaksi_queryset.filter(status_transaksi=status_filter)
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Title
    title = Paragraph("Laporan Transaksi UD Barokah Jaya Beton", title_style)
    elements.append(title)
    
    # Filter information (KOREKSI: Penanganan `bulan_filter` yang mungkin 'None')
    if bulan_filter and tahun_filter and bulan_filter != 'None' and tahun_filter != 'None' and bulan_filter.isdigit() and tahun_filter.isdigit():
        try:
            bulan_nama = calendar.month_name[int(bulan_filter)]  # Konversi aman di sini
            filter_info = Paragraph(f"Periode: {bulan_nama} {tahun_filter}", styles['Normal'])
            elements.append(filter_info)
        except (ValueError, IndexError):
            # Handle invalid month numbers
            filter_info = Paragraph(f"Periode: {bulan_filter}/{tahun_filter}", styles['Normal'])
            elements.append(filter_info)
    
    # KOREKSI ERROR 500: PASTIKAN STATUS FILTER VALID
    if status_filter and status_filter != 'None':
        status_label = dict(Transaksi.STATUS_CHOICES)[status_filter]
        status_info = Paragraph(f"Status: {status_label}", styles['Normal'])
        elements.append(status_info)
    
    elements.append(Spacer(1, 20))
    
    # Transaction table
    data = [['No.', 'ID Transaksi', 'Pelanggan', 'Tanggal', 'Total', 'Status']]
    
    for i, transaksi in enumerate(transaksi_queryset, 1):
        status_label = dict(Transaksi.STATUS_CHOICES)[transaksi.status_transaksi]
        data.append([
            str(i),
            str(transaksi.id),
            transaksi.pelanggan.nama_pelanggan,
            transaksi.tanggal.strftime("%d/%m/%Y"),
            f"Rp {transaksi.total:,.2f}",
            status_label
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Latar belakang putih
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    
    # Return PDF
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="laporan_transaksi.pdf"'
    return response


@login_required
def cetak_laporan_loyal_pdf(request):
    # Get loyal customers
    pelanggan_loyal = Pelanggan.objects.annotate(
        jumlah_transaksi=Count('transaksi', filter=Q(transaksi__status_transaksi='selesai')),
        total_pembelian=Sum('transaksi__total', filter=Q(transaksi__status_transaksi='selesai'))
    ).filter(
        jumlah_transaksi__gt=0,
        total_pembelian__gte=5000000
    ).order_by('-total_pembelian')
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Title
    title = Paragraph("Laporan Pelanggan Loyal UD Barokah Jaya Beton", title_style)
    elements.append(title)
    
    # Description
    description = Paragraph(
        "Pelanggan dengan total pembelian minimal Rp 5.000.000", 
        styles['Normal']
    )
    elements.append(description)
    elements.append(Spacer(1, 20))
    
    # Loyal customers table
    data = [['No.', 'Nama Pelanggan', 'Jumlah Transaksi', 'Total Pembelian']]
    
    for i, pelanggan in enumerate(pelanggan_loyal, 1):
        data.append([
            str(i),
            pelanggan.nama_pelanggan,
            str(pelanggan.jumlah_transaksi),
            f"Rp {pelanggan.total_pembelian:,.2f}"
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Latar belakang putih
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    
    # Return PDF
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="laporan_pelanggan_loyal.pdf"'
    return response


