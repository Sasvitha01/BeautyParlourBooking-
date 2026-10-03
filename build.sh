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
