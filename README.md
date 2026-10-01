# ✨ GlowNest Beauty Studio — Appointment Booking System

A full-featured, responsive Beauty Parlour & Salon Appointment Booking platform built with **Django 5.1**, **Django REST Framework**, and **Vanilla CSS**.

---

## 🌟 Key Features

### 👤 Customer Experience
- **Elegant Homepage**: Hero showcase, featured treatments, stylist experience counters, opening hours, and client testimonials.
- **Service Catalog**: Filter treatments across Hair Care, Skin Care & Facials, Makeup & Styling, Bridal Studio, Spa & Wellness, and Nail Bar.
- **Service Details**: Full description, duration, pricing, and related recommendations.
- **Online Booking**:
  - Live available time slots per date.
  - Multi-layer prevention against double bookings (form validation & database partial unique constraint).
  - Instant booking confirmation with a unique booking reference (`GNS-YYYY-XXXXX`).
  - Print confirmation receipt option.
- **Booking Status Lookup**: Track appointment status in real-time with Booking Reference ID and phone number.
- **Studio Pages**: About Us, Contact Us with working inquiry form, Privacy Policy, and Terms & Booking Policy.
- **Responsive Mobile First**: Polished layout, accessible navigation, glassmorphism accents, and WhatsApp chat button.

### 🛡️ Admin Dashboard
- **Authentication**: Staff login portal (`/admin-dashboard/login/`).
- **Dashboard Overview**: Live statistics (Today's, Pending, Confirmed, Completed appointments), today's schedule, and upcoming sessions.
- **Appointment Management**: Search and filter by client, status, date, or service.
  - One-click Confirm, Complete, and Cancel actions.
  - Detailed view with client notes, WhatsApp shortcut, and deletion capability.
- **Service & Catalog Management**: Add, edit, or deactivate services and service categories.
- **Client Directory**: Customer list with booking history and contact links.
- **Django Admin Integration**: Full Django Admin access at `/django-admin/`.

### ⚡ REST API Endpoints
- `GET /api/services/` — List active beauty services.
- `GET /api/services/<slug>/` — Retrieve service details.
- `GET /api/categories/` — List service categories.
- `GET /api/appointments/available-slots/?date=YYYY-MM-DD` — Real-time available slot checking.
- `POST /api/appointments/` — Create new appointments with validation.
- `GET /api/appointments/lookup/?booking_id=...` — Query booking status by ID.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12+, Django 5.1+, Django REST Framework 3.15+
- **Database**: SQLite (Local Development) / PostgreSQL (Production via `dj_database_url`)
- **Static Assets**: WhiteNoise storage, Vanilla CSS design system, Vanilla JavaScript
- **Security**: Environment-driven settings, CSRF protection, secure cookie flags in production

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone <repository-url>
cd BeautyParlourBooking
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure your `.env` contains:
```ini
SECRET_KEY=your-secure-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
WHATSAPP_NUMBER=+911234567890
```

### 5. Apply Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser (Admin Access)
```bash
python manage.py createsuperuser
```

### 7. Run the Development Server
```bash
python manage.py runserver
```
Visit the application at `http://127.0.0.1:8000/`.

---

## 🧪 Running Tests

The test suite covers customer booking, double-booking prevention, admin workflows, catalog operations, and REST APIs:

```bash
python manage.py test
```

---

## 🔐 Default Admin Portal

- **Admin Dashboard**: `http://127.0.0.1:8000/admin-dashboard/`
- **Django Admin**: `http://127.0.0.1:8000/django-admin/`

---

## 📄 License
This project is licensed under the MIT License.
