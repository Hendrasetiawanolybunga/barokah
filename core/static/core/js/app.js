// Custom JavaScript for Barokah Admin Dashboard

// Enable Bootstrap tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Confirm before deleting
function confirmDelete(message) {
    return confirm(message || 'Apakah Anda yakin ingin menghapus item ini?');
}

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Dynamic delete modal
document.addEventListener('DOMContentLoaded', function() {
    var deleteModal = document.getElementById('deleteModal');
    deleteModal.addEventListener('show.bs.modal', function(event) {
        var button = event.relatedTarget;
        var itemName = button.getAttribute('data-item-name');
        var deleteUrl = button.getAttribute('data-delete-url');
        
        var modal = this;
        modal.querySelector('#delete-item-name').textContent = itemName;
        modal.querySelector('#delete-form').action = deleteUrl;
    });
});

// Sidebar toggle functionality - Clean and simple
document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mobileToggle = document.getElementById('mobileToggle');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    
    // Desktop toggle
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            content.classList.toggle('sidebar-collapsed');
        });
    }
    
    // Mobile toggle
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        const isClickInsideSidebar = sidebar.contains(event.target);
        const isClickOnToggle = event.target.closest('#mobileToggle');
        
        if (!isClickInsideSidebar && !isClickOnToggle && window.innerWidth < 768) {
            sidebar.classList.remove('active');
        }
    });
});