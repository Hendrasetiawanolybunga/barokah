// core/static/core/js/web.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('Web portal scripts loaded.');
    
    // 1. Script untuk menghilangkan pesan Bootstrap secara otomatis
    const messageContainer = document.querySelector('.container-fluid .alert');
    if (messageContainer) {
        setTimeout(() => {
            messageContainer.style.display = 'none';
        }, 5000); // Pesan hilang setelah 5 detik
    }

    // 2. Script sederhana untuk tombol quantity di Detail Produk (Optional)
    // Jika Anda ingin tombol +/- berfungsi tanpa AJAX, Anda perlu membuat fungsi ini.
    // Saat ini, kita biarkan input field default.

});