from pathlib import Path
from datetime import timedelta
import os

# ------------------------------------------------
# Base Directory
# ------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------
# Security
# ------------------------------------------------
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')  # Uses env var in production, fallback in dev
DEBUG = os.getenv('DEBUG', 'True') == 'True'  # True in dev, False in production

ALLOWED_HOSTS = [    
    'localhost',
    '127.0.0.1',
    'srivari-mahal.onrender.com',  # Removed https://
    '.netlify.app',  
    # 'your-custom-domain.com',
]

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
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ------------------------------------------------
# URLs & Templates
# ------------------------------------------------
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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

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
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # Fixed path join

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / "media"

# ------------------------------------------------
# CORS — Allow Frontend
# ------------------------------------------------
# For development: allow all origins
# For production: specific origins only
CORS_ALLOW_ALL_ORIGINS = DEBUG  # True in dev, False in production

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://srivarimahalac.netlify.app",
]
    
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CSRF_TRUSTED_ORIGINS = [
    "https://srivarimahalac.netlify.app",
    "https://srivari-mahal.onrender.com",
]

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
# EMAIL SETTINGS (Handles both Dev & Production)
# ------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Uses environment variables in production, fallback values in development
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "srivarimahal2025kpm@gmail.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "gvpdmrdmtoaypwgw")
DEFAULT_FROM_EMAIL = os.getenv("EMAIL_HOST_USER", "srivarimahal2025kpm@gmail.com")

# Debug logging (only shows in development when DEBUG=True)
if DEBUG:
    print(f"📧 Email configured: {EMAIL_HOST_USER}")
    print(f"📧 Password length: {len(EMAIL_HOST_PASSWORD)}")

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