// Web Portal JavaScript

// Enable Bootstrap tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Cart quantity adjustment
document.addEventListener('DOMContentLoaded', function() {
    // Handle quantity increase/decrease in product detail
    const qtyInputs = document.querySelectorAll('#jumlah');
    qtyInputs.forEach(function(input) {
        const decreaseBtn = input.parentElement.querySelector('#decreaseQty');
        const increaseBtn = input.parentElement.querySelector('#increaseQty');
        
        if (decreaseBtn && increaseBtn) {
            decreaseBtn.addEventListener('click', function() {
                let value = parseInt(input.value);
                if (value > 1) {
                    input.value = value - 1;
                }
            });
            
            increaseBtn.addEventListener('click', function() {
                let value = parseInt(input.value);
                let max = parseInt(input.max);
                if (value < max) {
                    input.value = value + 1;
                }
            });
        }
    });
    
    // Handle quantity increase/decrease in cart
    const cartQtyGroups = document.querySelectorAll('.input-group');
    cartQtyGroups.forEach(function(group) {
        const decreaseBtn = group.querySelector('.btn:first-child');
        const increaseBtn = group.querySelector('.btn:last-child');
        const input = group.querySelector('input');
        
        if (decreaseBtn && increaseBtn && input) {
            decreaseBtn.addEventListener('click', function() {
                let value = parseInt(input.value);
                if (value > 1) {
                    input.value = value - 1;
                }
            });
            
            increaseBtn.addEventListener('click', function() {
                let value = parseInt(input.value);
                // In a real implementation, you would check stock availability
                input.value = value + 1;
            });
        }
    });
    
    // Handle add to cart button
    const addToCartBtn = document.getElementById('addToCart');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', function() {
            const qty = document.getElementById('jumlah').value;
            const productName = document.querySelector('h1').textContent;
            
            // Show confirmation message
            alert(`Berhasil menambahkan ${qty} ${productName} ke keranjang!`);
            
            // In a real implementation, you would update the cart badge
            const cartBadge = document.querySelector('.navbar .badge');
            if (cartBadge) {
                let currentCount = parseInt(cartBadge.textContent) || 0;
                cartBadge.textContent = currentCount + parseInt(qty);
            }
        });
    }
    
    // Handle remove from cart buttons
    const removeButtons = document.querySelectorAll('.btn-danger');
    removeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            if (confirm('Apakah Anda yakin ingin menghapus item ini dari keranjang?')) {
                const row = button.closest('tr');
                if (row) {
                    row.remove();
                    // In a real implementation, you would update the total
                }
            }
        });
    });
});

// Smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                window.scrollTo({
                    top: target.offsetTop - 70,
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Navbar scroll effect
document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('shadow');
            } else {
                navbar.classList.remove('shadow');
            }
        });
    }
});