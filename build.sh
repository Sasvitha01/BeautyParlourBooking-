#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input

# Load services and categories fixture
python manage.py loaddata services/fixtures/initial_data.json || true

# Ensure service images are assigned
python assign_service_images.py || true

# Ensure admin superuser exists
python ensure_admin.py || true

# Update the Django Site record to use the actual deployment domain
# so that /sitemap.xml emits correct absolute URLs.
python manage.py shell -c "
from django.contrib.sites.models import Site
import os
hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'beautyparlourbooking-2.onrender.com')
site = Site.objects.get_or_create(id=1)[0]
site.domain = hostname
site.name = 'GlowNest Beauty Studio'
site.save()
print(f'[GlowNest] Site domain set to: {hostname}')
" || true
