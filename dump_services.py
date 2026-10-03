import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glownest.settings')
import django
django.setup()
from services.models import ServiceCategory, Service
print('CATEGORIES')
for c in ServiceCategory.objects.all():
    print(f'{c.id}: {c.name} | slug: {c.slug} | icon: {c.icon}')
print()
print('SERVICES')
for s in Service.objects.all():
    print(f'{s.id}: [{s.category.name}] {s.name} | slug: {s.slug} | price: {s.price} | duration: {s.duration_minutes}min | has_image: {bool(s.image)}')
