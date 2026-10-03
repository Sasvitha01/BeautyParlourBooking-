# GlowNest Beauty Studio

> **Where Beauty Meets Confidence**

A full-featured, production-ready **Beauty Parlour & Salon Appointment Booking System** built with **Django 5.1**, **Django REST Framework**, and **Vanilla CSS**. Designed for real-world deployment on Render + PostgreSQL (Supabase).

- **GitHub Repository**: [https://github.com/Sasvitha01/BeautyParlourBooking-](https://github.com/Sasvitha01/BeautyParlourBooking-)
- **Live Render URL**: [https://glownest-beauty-studio.onrender.com](https://glownest-beauty-studio.onrender.com)

---

## Features

### Customer-Facing Website
- **Elegant Homepage** — hero image, featured services, testimonials, opening hours, location, and booking CTAs
- **Services Catalog** — browse and filter across 6 categories with real images and clear pricing
- **Service Details** — full description, duration, price, related services, and direct booking
- **Online Appointment Booking**:
  - Live available time slot checking per selected date
  - Double-booking prevention at both form-validation and database constraint levels
  - Unique booking reference per appointment (`GNS-YYYY-XXXXX` format)
  - Printable booking confirmation receipt
- **Booking Status Lookup** — enter booking reference + phone to check appointment status
- **Studio Pages** — About Us, Contact Us, Privacy Policy, Terms & Booking Policy
- **Responsive Design** — mobile, tablet, and desktop optimised with hamburger nav and accessible layout
- **WhatsApp Integration** — floating WhatsApp chat button and in-page WhatsApp CTAs

### Admin Dashboard (`/admin-dashboard/`)
- **Staff Authentication** — separate login portal with `is_staff` permission check
- **Dashboard Overview** — today's appointments, pending/confirmed/completed/cancelled counts, upcoming schedule
- **Appointment Management**:
  - Search by booking ID, customer name, phone, or email
  - Filter by status, date, and service
  - One-click Confirm, Complete, Cancel, and Delete actions
  - Detailed appointment view with admin notes
- **Service Management** — add, edit, deactivate, or delete services; upload service images
- **Service Category Management** — manage display order, icons, and activation
- **Customer Directory** — list all customers with appointment counts and contact links
- **Django Admin** — also available at `/django-admin/` for superusers

### REST API
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/services/` | List all active services |
| GET | `/api/services/<slug>/` | Service detail |
| GET | `/api/categories/` | List service categories |
| GET | `/api/appointments/available-slots/?date=YYYY-MM-DD` | Available time slots |
| POST | `/api/appointments/` | Create appointment |
| GET | `/api/appointments/lookup/?booking_id=...` | Lookup booking |

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12+, Django 5.1+, Django REST Framework 3.15+ |
| Database | SQLite (Development), PostgreSQL (Production via `dj-database-url`) |
| Static Files | WhiteNoise, Vanilla CSS design system |
| Frontend | Django Templates, Vanilla JavaScript |
| Deployment | Render (Web Service + PostgreSQL) |
| Security | CSRF, environment-variable secrets, production security headers |

---

## Project Structure

```
BeautyParlourBooking/
├── glownest/               # Django project config
│   ├── settings.py         # Environment-driven settings
│   ├── urls.py             # Root URL configuration
│   ├── context_processors.py  # Global template context
│   └── views.py            # Custom 404 handler
├── appointments/           # Booking flow app
│   ├── models.py           # Customer, Appointment models
│   ├── forms.py            # Booking, lookup, contact forms
│   ├── views.py            # Public views (home, book, confirm, check, etc.)
│   └── urls.py             # Public URL routes
├── services/               # Service catalog app
│   ├── models.py           # ServiceCategory, Service models
│   ├── views.py            # Service list, service detail
│   └── urls.py             # Service URL routes
├── dashboard/              # Admin dashboard app
│   ├── views.py            # Admin-authenticated management views
│   └── urls.py             # Dashboard URL routes
├── api/                    # REST API app
│   ├── serializers.py      # DRF serializers
│   ├── views.py            # API views
│   └── urls.py             # API URL routes
├── templates/              # HTML templates
│   ├── base.html           # Site-wide base (header, footer, nav)
│   ├── public/             # Customer-facing pages
│   ├── dashboard/          # Admin dashboard pages
│   └── errors/             # Custom 404, 500 error pages
├── static/
│   ├── css/style.css       # Full design system (variables, components)
│   ├── js/main.js          # Navigation, form interactions, animations
│   └── images/             # Local service and hero images
├── media/                  # Uploaded service images (runtime)
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment configuration
├── .env.example            # Environment variables template
└── manage.py
```

---

## Local Development Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd BeautyParlourBooking
```

### 2. Create & Activate Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
copy .env.example .env    # Windows
# cp .env.example .env    # Linux/macOS
```

Edit `.env` with your values:
```ini
SECRET_KEY=your-secure-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
WHATSAPP_NUMBER=+911234567890
```

### 5. Apply Database Migrations
```bash
python manage.py migrate
```

### 6. Create Admin Superuser
```bash
python manage.py createsuperuser
```

### 7. Run the Development Server
```bash
python manage.py runserver
```
Visit: `http://127.0.0.1:8000/`

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes (production) | insecure fallback | Django secret key |
| `DEBUG` | No | `False` | Enable debug mode |
| `ALLOWED_HOSTS` | Yes (production) | `localhost,127.0.0.1` | Comma-separated allowed hosts |
| `DATABASE_URL` | No | SQLite | PostgreSQL connection URL |
| `WHATSAPP_NUMBER` | No | `+911234567890` | WhatsApp business number |
| `RENDER_EXTERNAL_HOSTNAME` | No | — | Auto-set by Render for ALLOWED_HOSTS |
| `CORS_ALLOWED_ORIGINS` | No | localhost origins | Comma-separated CORS allowed origins |

---

## Admin Access

| Portal | URL |
|--------|-----|
| Custom Admin Dashboard | `/admin-dashboard/` |
| Admin Login | `/admin-dashboard/login/` |
| Django Admin | `/django-admin/` |

> **Note:** The custom dashboard requires `is_staff = True`. The Django Admin at `/django-admin/` requires a superuser account.

---

## Database Setup

### Local (SQLite — default)
No configuration needed. SQLite is used automatically when `DATABASE_URL` is not set.

### Production (PostgreSQL)
Set `DATABASE_URL` in your environment:
```
DATABASE_URL=postgres://username:password@host:5432/dbname
```
Supabase PostgreSQL connection strings work directly.

Run migrations after configuring the database:
```bash
python manage.py migrate
```

---

## Running Tests

The test suite covers booking flows, double-booking prevention, admin workflows, service catalog, and REST APIs:

```bash
python manage.py test
```

Run system check:
```bash
python manage.py check
```

Check for pending migrations:
```bash
python manage.py makemigrations --check
```

---

## Render Deployment

- **Live Web Service URL**: `https://glownest-beauty-studio.onrender.com`
- **GitHub Repository**: `https://github.com/Sasvitha01/BeautyParlourBooking-.git`

### Deploy with render.yaml (Recommended)
1. Connect your GitHub repository (`Sasvitha01/BeautyParlourBooking-`) to Render
2. Render detects `render.yaml` automatically
3. Configure environment variables in the Render dashboard:
   - `SECRET_KEY` — (auto-generated or set via `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
   - `DEBUG` — `False`
   - `DATABASE_URL` — Supabase or Render PostgreSQL connection string
   - `WHATSAPP_NUMBER` — Business WhatsApp number with country code (e.g. `+919876543210`)
4. Trigger manual or automatic deploy.

### Manual Web Service Configuration on Render
1. Create a new **Web Service** pointing to `Sasvitha01/BeautyParlourBooking-`
2. **Environment**: `Python 3`
3. **Build Command**: `./build.sh` (or `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate --no-input && python manage.py loaddata services/fixtures/initial_data.json`)
4. **Start Command**: `gunicorn glownest.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
5. **Environment Variables**:
   - `SECRET_KEY`: `<your-random-secret-key>`
   - `DEBUG`: `False`
   - `DATABASE_URL`: `<postgres-connection-string>`
   - `ALLOWED_HOSTS`: `glownest-beauty-studio.onrender.com`
   - `RENDER_EXTERNAL_HOSTNAME`: `glownest-beauty-studio.onrender.com`
   - `CSRF_TRUSTED_ORIGINS`: `https://glownest-beauty-studio.onrender.com,https://*.onrender.com`
   - `WHATSAPP_NUMBER`: `+919876543210`

### Supabase PostgreSQL Setup (Recommended)
Set `DATABASE_URL` in Render environment variables to your permanent Supabase connection string:
```
DATABASE_URL=postgres://postgres.[project-ref]:[password]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require
```

---

## Security Features

- Secrets loaded exclusively from environment variables (never hardcoded)
- `.env` excluded from Git via `.gitignore`
- CSRF protection enabled and enforced
- Production security headers: HSTS, XSS filter, content-type sniffing prevention, X-Frame-Options
- Secure session and CSRF cookies in production
- SSL redirect enforced in production
- Admin dashboard protected by `is_staff` check
- Double-booking prevention via database unique constraint + form validation
- CORS restricted to configured origins

---

## Service Categories

| Category | Image Used |
|----------|-----------|
| Hair Care | `hair.jpg` |
| Skin Care & Facials | `skin.jpg` |
| Makeup & Styling | `makeup.jpg` |
| Bridal Studio | `bridal.jpg` |
| Spa & Wellness | `spa.jpg` |
| Nail Bar | `nails.jpg` |

Images auto-selected by category slug. Individual service images can be uploaded via the admin dashboard.

---

## Business Hours

| Day | Hours |
|-----|-------|
| Monday – Friday | 9:00 AM – 7:00 PM |
| Saturday | 9:00 AM – 8:00 PM |
| Sunday | 10:00 AM – 5:00 PM |
| Lunch Break | 1:00 PM – 2:00 PM (unavailable for booking) |

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.
