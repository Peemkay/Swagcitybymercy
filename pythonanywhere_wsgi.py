"""
PythonAnywhere WSGI configuration for Swagcitybymercy.

HOW TO USE:
  1. On PythonAnywhere, open the "Web" tab -> click the WSGI configuration
     file link (e.g. /var/www/swagcitybymercy_pythonanywhere_com_wsgi.py).
  2. Delete everything in it and paste the contents of THIS file.
  3. Edit the two paths + the env vars below to match your account.
  4. Save, then click the green "Reload" button on the Web tab.

Do NOT commit real secrets to git — they live only in this server-side file.
"""

import os
import sys

# --- 1. Point to your project folder -----------------------------------------
project_home = "/home/Swagcity/swagcity_project"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# --- 2. Production environment variables -------------------------------------
# Generate a fresh key locally with:
#   python manage.py shell -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
os.environ["DJANGO_SECRET_KEY"] = "PASTE-YOUR-50-CHAR-RANDOM-KEY-HERE"
os.environ["DJANGO_DEBUG"] = "False"
os.environ["DJANGO_ALLOWED_HOSTS"] = "swagcity.pythonanywhere.com"
os.environ["DJANGO_CSRF_TRUSTED_ORIGINS"] = "https://swagcity.pythonanywhere.com"
os.environ["DJANGO_SECURE_SSL_REDIRECT"] = "True"
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

# --- 3. Start Django ----------------------------------------------------------
from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
