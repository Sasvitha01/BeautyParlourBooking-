/**
 * GlowNest Beauty Studio — Dashboard JavaScript
 * Handles sidebar toggle, confirmation modals, and dashboard interactions.
 */
document.addEventListener('DOMContentLoaded', () => {

    // ---- Sidebar Toggle (Mobile) ----
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.dashboard-sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });

        // Close sidebar on outside click
        document.addEventListener('click', (e) => {
            if (sidebar.classList.contains('active') &&
                !sidebar.contains(e.target) &&
                !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('active');
            }
        });
    }

    // ---- Confirm before destructive actions ----
    document.querySelectorAll('[data-confirm]').forEach(el => {
        el.addEventListener('click', (e) => {
            const message = el.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // ---- Auto-submit filter forms ----
    document.querySelectorAll('.filter-group select').forEach(select => {
        select.addEventListener('change', () => {
            select.closest('form').submit();
        });
    });

    // ---- Active sidebar link ----
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-nav a').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath.startsWith(href) && href !== '/admin-dashboard/')) {
            link.classList.add('active');
        } else if (href === '/admin-dashboard/' && currentPath === '/admin-dashboard/') {
            link.classList.add('active');
        }
    });

    // ---- Auto-dismiss messages ----
    const messages = document.querySelectorAll('.message');
    messages.forEach(msg => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.3s, transform 0.3s';
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-10px)';
            setTimeout(() => msg.remove(), 300);
        }, 5000);
    });
});
