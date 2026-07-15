from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path

# Route the admin's own login page through the site login (which enforces the
# optional TOTP second factor) instead of Django's unprotected admin login.
admin.site.login = login_required(admin.site.login)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]
