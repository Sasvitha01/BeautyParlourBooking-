/**
 * GlowNest Beauty Studio — Main JavaScript
 * Handles navigation, booking form interactions, and UI enhancements.
 */
document.addEventListener('DOMContentLoaded', () => {

    // ---- Header scroll effect ----
    const header = document.querySelector('.header');
    if (header) {
        window.addEventListener('scroll', () => {
            header.classList.toggle('scrolled', window.scrollY > 20);
        });
    }

    // ---- Mobile Navigation Toggle ----
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('active');
            document.body.style.overflow = navLinks.classList.contains('active') ? 'hidden' : '';
        });

        // Close nav on link click
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
                document.body.style.overflow = '';
            });
        });
    }

    // ---- Booking Form: Date & Time Slot Logic ----
    const dateInput = document.getElementById('id_appointment_date');
    const timeSelect = document.getElementById('id_appointment_time');

    if (dateInput && timeSelect) {
        // Set min date to today
        const today = new Date();
        const todayStr = today.toISOString().split('T')[0];
        dateInput.setAttribute('min', todayStr);

        // Set max date to 90 days from now
        const maxDate = new Date(today);
        maxDate.setDate(maxDate.getDate() + 90);
        dateInput.setAttribute('max', maxDate.toISOString().split('T')[0]);

        // Fetch available slots when date changes
        dateInput.addEventListener('change', () => {
            const selectedDate = dateInput.value;
            if (!selectedDate) return;

            // Clear existing options
            timeSelect.innerHTML = '<option value="">Loading slots...</option>';
            timeSelect.disabled = true;

            fetch(`/available-slots/?date=${selectedDate}`)
                .then(response => response.json())
                .then(data => {
                    timeSelect.innerHTML = '<option value="">Select a time slot...</option>';
                    if (data.slots && data.slots.length > 0) {
                        data.slots.forEach(slot => {
                            const option = document.createElement('option');
                            option.value = slot.value;
                            option.textContent = slot.label;
                            timeSelect.appendChild(option);
                        });
                    } else {
                        timeSelect.innerHTML = '<option value="">No slots available for this date</option>';
                    }
                    timeSelect.disabled = false;
                })
                .catch(() => {
                    timeSelect.innerHTML = '<option value="">Error loading slots. Try again.</option>';
                    timeSelect.disabled = false;
                });
        });
    }

    // ---- Service selector: show price/duration ----
    const serviceSelect = document.getElementById('id_service');
    if (serviceSelect) {
        serviceSelect.addEventListener('change', () => {
            // The selected option text includes price info which Django renders
        });
    }

    // ---- Print booking confirmation ----
    const printBtn = document.getElementById('print-confirmation');
    if (printBtn) {
        printBtn.addEventListener('click', (e) => {
            e.preventDefault();
            window.print();
        });
    }

    // ---- Auto-dismiss messages after 5 seconds ----
    const messages = document.querySelectorAll('.message');
    messages.forEach(msg => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.3s, transform 0.3s';
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-10px)';
            setTimeout(() => msg.remove(), 300);
        }, 5000);
    });

    // ---- Smooth scroll for anchor links ----
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // ---- Active nav link highlight ----
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-links a').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        }
    });

    // ---- Form validation visual feedback ----
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('.form-input');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                if (input.value.trim() && input.checkValidity()) {
                    input.style.borderColor = 'var(--color-success)';
                } else if (input.value.trim() && !input.checkValidity()) {
                    input.style.borderColor = 'var(--color-danger)';
                } else {
                    input.style.borderColor = '';
                }
            });

            input.addEventListener('focus', () => {
                input.style.borderColor = '';
            });
        });
    });

    // ---- Intersection Observer for fade-in animations ----
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.card, .feature-card, .testimonial-card, .info-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});
