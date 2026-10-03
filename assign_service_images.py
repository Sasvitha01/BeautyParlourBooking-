"""
Script to assign service images via DB image field.
Each service gets a unique image from static/images/.
Run: python assign_service_images.py
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glownest.settings')

import django
django.setup()

from services.models import Service
from django.core.files import File

# Mapping: service slug -> image filename in static/images/
SERVICE_IMAGE_MAP = {
    # Hair Care
    'deluxe-hair-spa': 'svc-deluxe-hair-spa.jpg',
    'keratin-smoothing': 'svc-keratin-smoothing.jpg',
    'layered-cut-blowout': 'svc-layered-cut.jpg',
    # Skin Care
    'glow-radiance-gold-facial': 'svc-gold-facial.jpg',
    'oxygen-infusion-cleanup': 'svc-oxygen-cleanup.jpg',
    'anti-aging-collagen': 'svc-collagen-rejuv.jpg',
    # Makeup - use existing makeup.jpg (we can't generate more now)
    'glam-party-hd-makeup': 'makeup.jpg',
    'soft-glam-daytime': 'makeup.jpg',
    # Bridal
    'royal-bridal-makeover': 'bridal.jpg',
    'pre-bridal-radiance': 'bridal.jpg',
    # Spa
    'swedish-aromatherapy': 'spa.jpg',
    'deep-tissue-herbal': 'spa.jpg',
    # Nails
    'rose-gel-pedicure': 'nails.jpg',
    'sculpted-gel-extensions': 'nails.jpg',
}

STATIC_IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'static', 'images')

assigned = []
skipped = []

for slug, img_filename in SERVICE_IMAGE_MAP.items():
    try:
        service = Service.objects.get(slug=slug)
        img_path = os.path.join(STATIC_IMAGES_DIR, img_filename)
        if os.path.exists(img_path):
            with open(img_path, 'rb') as f:
                # Save as media/services/<filename>
                dest_name = f'services/{slug}.jpg'
                service.image.save(dest_name, File(f), save=True)
            assigned.append(f'{slug} -> {img_filename}')
        else:
            skipped.append(f'{slug}: image file not found: {img_path}')
    except Service.DoesNotExist:
        skipped.append(f'{slug}: service not found in DB')

print('=== ASSIGNED ===')
for a in assigned:
    print(a)
print()
print('=== SKIPPED ===')
for s in skipped:
    print(s)
print()
print(f'Done: {len(assigned)} assigned, {len(skipped)} skipped')
