import base64
import io

import qrcode
import qrcode.image.svg
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django_otp import login as otp_login
from django_otp.plugins.otp_totp.models import TOTPDevice

from .forms import InviteSignupForm, SubmissionForm, TOTPTokenForm
from .models import Course, Enrollment, Lesson, Submission

User = get_user_model()


def _confirmed_device(user):
    return TOTPDevice.objects.devices_for_user(user, confirmed=True).first()


# ---------------------------------------------------------------------------
# Auth: login with optional second factor
# ---------------------------------------------------------------------------
class GSDLoginView(LoginView):
    template_name = "auth/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        device = _confirmed_device(user)
        if device:
            # Defer the actual login until the TOTP token checks out.
            self.request.session["pre_2fa_user_id"] = user.pk
            self.request.session["pre_2fa_next"] = self.get_success_url()
            return redirect("verify_2fa")
        return super().form_valid(form)


def verify_2fa(request):
    user_id = request.session.get("pre_2fa_user_id")
    if not user_id:
        return redirect("login")
    user = get_object_or_404(User, pk=user_id)
    device = _confirmed_device(user)
    if device is None:
        return redirect("login")

    form = TOTPTokenForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if device.verify_token(form.cleaned_data["token"]):
            next_url = request.session.pop("pre_2fa_next", None)
            del request.session["pre_2fa_user_id"]
            auth_login(request, user)
            otp_login(request, device)
            return redirect(next_url or "dashboard")
        form.add_error("token", "That code didn't match. Try again.")
    return render(request, "auth/verify_2fa.html", {"form": form})


def invite_signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    initial = {"code": request.GET.get("code", "")}
    form = InviteSignupForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        auth_login(request, user)
        messages.success(request, "Welcome to the crew. Your courses are ready — get moving.")
        return redirect("dashboard")
    return render(request, "auth/invite_signup.html", {"form": form})


# ---------------------------------------------------------------------------
# Optional 2FA management (per-account)
# ---------------------------------------------------------------------------
@login_required
def security(request):
    device = _confirmed_device(request.user)
    pending = TOTPDevice.objects.filter(user=request.user, confirmed=False).first()
    return render(request, "auth/security.html", {"device": device, "pending": pending})


@login_required
def enable_2fa(request):
    if _confirmed_device(request.user):
        return redirect("security")
    device, _ = TOTPDevice.objects.get_or_create(
        user=request.user, confirmed=False, defaults={"name": "Authenticator app"}
    )
    form = TOTPTokenForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if device.verify_token(form.cleaned_data["token"]):
            device.confirmed = True
            device.save()
            otp_login(request, device)
            messages.success(request, "Two-factor authentication is on.")
            return redirect("security")
        form.add_error("token", "That code didn't match. Scan the QR again and retry.")

    img = qrcode.make(device.config_url, image_factory=qrcode.image.svg.SvgPathImage)
    buf = io.BytesIO()
    img.save(buf)
    qr_svg = base64.b64encode(buf.getvalue()).decode()
    return render(request, "auth/enable_2fa.html", {"form": form, "qr_svg": qr_svg, "device": device})


@login_required
@require_POST
def disable_2fa(request):
    TOTPDevice.objects.filter(user=request.user).delete()
    messages.info(request, "Two-factor authentication is off.")
    return redirect("security")


# ---------------------------------------------------------------------------
# Student pages
# ---------------------------------------------------------------------------
def _enrollment_or_404(user, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    if not Enrollment.objects.filter(user=user, course=course).exists():
        raise Http404  # don't reveal courses the student didn't buy
    return course


def course_progress(user, course):
    """Every lesson of a course with its gating status for this student."""
    rows = []
    for lesson in course.lessons.all():
        rows.append(
            {
                "lesson": lesson,
                "status": lesson.status_for(user),
                "submission": lesson.submissions.filter(user=user).first(),
            }
        )
    return rows


@login_required
def dashboard(request):
    cards = []
    enrollments = (
        Enrollment.objects.filter(user=request.user)
        .select_related("course")
        .order_by("course__order")
    )
    for enrollment in enrollments:
        course = enrollment.course
        total = course.lessons.count()
        done = Submission.objects.filter(
            user=request.user,
            lesson__course=course,
            status=Submission.Status.APPROVED,
        ).values("lesson").distinct().count()
        cards.append(
            {
                "course": course,
                "total": total,
                "done": done,
                "percent": int(done / total * 100) if total else 0,
            }
        )
    return render(request, "dashboard.html", {"cards": cards})


@login_required
def course_detail(request, course_slug):
    course = _enrollment_or_404(request.user, course_slug)
    if not course.is_live:
        return render(request, "course_coming_soon.html", {"course": course})
    rows = course_progress(request.user, course)
    done = sum(1 for r in rows if r["status"] == "completed")
    percent = int(done / len(rows) * 100) if rows else 0
    next_row = next((r for r in rows if r["status"] in ("unlocked", "in_progress")), None)
    return render(
        request,
        "course_detail.html",
        {"course": course, "rows": rows, "done": done, "percent": percent, "next_row": next_row},
    )


@login_required
def lesson_detail(request, course_slug, lesson_slug):
    course = _enrollment_or_404(request.user, course_slug)
    if not course.is_live:
        raise Http404
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)
    status = lesson.status_for(request.user)
    if status == "locked":
        messages.warning(request, "That lesson is still locked. Finish the one before it first.")
        return redirect(course.get_absolute_url())

    submission = lesson.submissions.filter(user=request.user).first()
    form = SubmissionForm()
    if request.method == "POST":
        can_submit = status in ("unlocked", "in_progress") and (
            submission is None or submission.status == Submission.Status.REJECTED
        )
        if not can_submit:
            messages.info(request, "Your worksheet is already in — hang tight for the review.")
            return redirect(lesson.get_absolute_url())
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            new_submission = form.save(commit=False)
            new_submission.user = request.user
            new_submission.lesson = lesson
            new_submission.save()
            messages.success(
                request,
                "Worksheet in. We'll review it shortly — the next lesson unlocks on approval.",
            )
            return redirect(lesson.get_absolute_url())

    rows = course_progress(request.user, course)
    index = next(i for i, r in enumerate(rows) if r["lesson"].pk == lesson.pk)
    next_lesson = rows[index + 1]["lesson"] if index + 1 < len(rows) else None
    prev_lesson = rows[index - 1]["lesson"] if index > 0 else None
    return render(
        request,
        "lesson_detail.html",
        {
            "max_mb": settings.SUBMISSION_MAX_MB,
            "course": course,
            "lesson": lesson,
            "status": lesson.status_for(request.user),
            "submission": lesson.submissions.filter(user=request.user).first(),
            "form": form,
            "rows": rows,
            "next_lesson": next_lesson,
            "prev_lesson": prev_lesson,
        },
    )


# ---------------------------------------------------------------------------
# Protected file downloads (media is never served publicly)
# ---------------------------------------------------------------------------
@login_required
def worksheet_download(request, course_slug, lesson_slug):
    if request.user.is_staff:
        course = get_object_or_404(Course, slug=course_slug)
    else:
        course = _enrollment_or_404(request.user, course_slug)
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)
    if not lesson.worksheet_file:
        raise Http404
    if not request.user.is_staff and lesson.status_for(request.user) == "locked":
        raise Http404
    return FileResponse(lesson.worksheet_file.open("rb"), as_attachment=True)


@login_required
def submission_download(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    if submission.user_id != request.user.pk and not request.user.is_staff:
        raise Http404
    return FileResponse(submission.uploaded_file.open("rb"), as_attachment=True)
