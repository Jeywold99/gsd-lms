from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    # Auth
    path("login/", views.GSDLoginView.as_view(), name="login"),
    path("login/verify/", views.verify_2fa, name="verify_2fa"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("invite/", views.invite_signup, name="invite_signup"),
    path("account/security/", views.security, name="security"),
    path("account/security/2fa/enable/", views.enable_2fa, name="enable_2fa"),
    path("account/security/2fa/disable/", views.disable_2fa, name="disable_2fa"),
    # Password reset
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(template_name="auth/password_reset.html"),
        name="password_reset",
    ),
    path(
        "password-reset/sent/",
        auth_views.PasswordResetDoneView.as_view(template_name="auth/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="auth/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(template_name="auth/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    # Courses
    path("courses/<slug:course_slug>/", views.course_detail, name="course_detail"),
    path("courses/<slug:course_slug>/<slug:lesson_slug>/", views.lesson_detail, name="lesson_detail"),
    path(
        "courses/<slug:course_slug>/<slug:lesson_slug>/worksheet/",
        views.worksheet_download,
        name="worksheet_download",
    ),
    path("submissions/<int:pk>/file/", views.submission_download, name="submission_download"),
]
