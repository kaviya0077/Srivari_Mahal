import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User

# Your existing credentials
USERNAME = os.environ.get('SUPERUSER_USERNAME', 'kaviya')
EMAIL = os.environ.get('SUPERUSER_EMAIL', 'kaviyavpcs@gmail.com')
PASSWORD = os.environ.get('SUPERUSER_PASSWORD', 'KJVL@77vitai')

if not User.objects.filter(username=USERNAME).exists():
    User.objects.create_superuser(
        username=USERNAME,
        email=EMAIL,
        password=PASSWORD
    )
    print(f'✅ Superuser "{USERNAME}" created')
else:
    print(f'ℹ️ Superuser "{USERNAME}" already exists')
