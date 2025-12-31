from pathlib import Path
from datetime import timedelta

# ------------------------------------------------
# Base Directory
# ------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------
# Security
# ------------------------------------------------
SECRET_KEY = 'your-secret-key-here'   # ⚠️ Replace in production
DEBUG = False
ALLOWED_HOSTS = ['*']

# ------------------------------------------------
# Installed Apps
# ------------------------------------------------
INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',

    # Local apps
    'api',
]

# ------------------------------------------------
# Middleware
# ------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    # CORS — Must stay at top
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ------------------------------------------------
# URLs & Templates
# ------------------------------------------------
# ⚠️ IMPORTANT — update "project" to your actual project folder name
# Example: if your folder is backend/sri_vari_mahal/, use 'sri_vari_mahal.urls'
ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ⚠️ Update this with your project folder name
WSGI_APPLICATION = 'project.wsgi.application'

# ------------------------------------------------
# Database (SQLite for Development)
# ------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ------------------------------------------------
# Static & Media
# ------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / "media"

# ------------------------------------------------
# CORS — Allow Frontend
# ------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True
    

CORS_ALLOW_CREDENTIALS = True

# ------------------------------------------------
# Django REST Framework + JWT Auth
# ------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    )
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=90),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=2),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ------------------------------------------------
# EMAIL SETTINGS (for Gmail SMTP)
# ------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "srivarimahal2025kpm@gmail.com"
EMAIL_HOST_PASSWORD = "eepw ibge bxej atwk"
DEFAULT_FROM_EMAIL = "srivarimahal2025kpm@gmail.com"

# ------------------------------------------------
# PAYMENT SETTINGS (Razorpay Placeholder)
# ------------------------------------------------
# RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_xxxxxxxxx")
# RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "xxxxxxxxxxxxxxx")

# ------------------------------------------------
# Internationalization
# ------------------------------------------------
# LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'Asia/Kolkata'
# USE_I18N = True
# USE_TZ = True

# ------------------------------------------------
# Default Primary Key
# ------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ------------------------------------------------
# NOTIFICATION SETTINGS (Email + SMS)
# ------------------------------------------------

# Email subjects used by backend views
# BOOKING_CONFIRMATION_SUBJECT = "Your Booking is Confirmed – Sri Vari Mahal"
# BOOKING_PENDING_SUBJECT = "Your Booking is Pending – Sri Vari Mahal"
# BOOKING_PAYMENT_RECEIVED_SUBJECT = "Payment Received – Sri Vari Mahal"
# BOOKING_PAYMENT_REQUIRED_SUBJECT = "Advance Payment Required – Sri Vari Mahal"

# SMS Notifications (Using Twilio or any provider)
# SMS_ENABLED = True

# TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
# TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
# TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

# Message templates
# SMS_TEMPLATE_BOOKING_CONFIRMED = (
#     "Your booking is confirmed at Sri Vari Mahal. Thank you!"
# )

# SMS_TEMPLATE_ADVANCE_REQUIRED = (
#     "Your booking requires an advance payment to confirm. Please complete payment."
# )

# SMS_TEMPLATE_PAYMENT_SUCCESS = (
#     "Payment received successfully for your booking at Sri Vari Mahal."
# )