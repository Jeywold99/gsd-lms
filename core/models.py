import secrets

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


class User(AbstractUser):
    """
    Two roles:
      - Student: a regular account (is_staff=False), created by an admin or via
        a one-time invite code. Sees only the courses they're enrolled in.
      - Admin: is_staff=True (use a superuser for full access). Manages
        everything through the Django admin.
    """

    @property
    def is_admin_role(self):
        return self.is_staff

    def __str__(self):
        full = self.get_full_name()
        return f"{self.username} ({full})" if full else self.username


class Course(models.Model):
    class Status(models.TextChoices):
        LIVE = "live", "Live"
        DRAFT = "draft", "Draft / Coming soon"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    tagline = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    order = models.PositiveIntegerField(default=0, help_text="Display order on the dashboard.")

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    @property
    def is_live(self):
        return self.status == self.Status.LIVE

    def get_absolute_url(self):
        return reverse("course_detail", args=[self.slug])


def worksheet_upload_path(instance, filename):
    return f"worksheets/{instance.course.slug}/{filename}"


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    order = models.PositiveIntegerField(help_text="1-based position inside the course.")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    objectives = models.TextField(blank=True, help_text="One objective per line.")
    content = models.TextField(blank=True, help_text="Lesson body (HTML allowed).")
    video_url = models.URLField(
        blank=True,
        help_text="Embed URL for the lesson video (YouTube / Vimeo / Bunny). "
        "Paste the normal watch URL — it is converted for embedding automatically.",
    )
    worksheet_file = models.FileField(
        upload_to=worksheet_upload_path, blank=True,
        help_text="The downloadable worksheet (PDF) students must complete.",
    )
    prerequisite = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="unlocks",
        help_text="Lesson whose approved submission unlocks this one. "
        "Usually the previous lesson in the course.",
    )
    release_date = models.DateTimeField(
        null=True, blank=True,
        help_text="Optional drip date — the lesson stays locked until this moment even "
        "if the prerequisite is approved.",
    )

    class Meta:
        ordering = ["course", "order"]
        constraints = [
            models.UniqueConstraint(fields=["course", "order"], name="unique_lesson_order"),
            models.UniqueConstraint(fields=["course", "slug"], name="unique_lesson_slug"),
        ]

    def __str__(self):
        return f"{self.course.title} · {self.order:02d} {self.title}"

    def clean(self):
        if self.prerequisite:
            if self.prerequisite_id == self.id:
                raise ValidationError("A lesson can't be its own prerequisite.")
            if self.prerequisite.course_id != self.course_id:
                raise ValidationError("Prerequisite must belong to the same course.")

    def get_absolute_url(self):
        return reverse("lesson_detail", args=[self.course.slug, self.slug])

    @property
    def objective_list(self):
        return [line.strip() for line in self.objectives.splitlines() if line.strip()]

    @property
    def is_released(self):
        return self.release_date is None or self.release_date <= timezone.now()

    def embed_url(self):
        """Best-effort conversion of common watch URLs into embeddable ones."""
        url = self.video_url.strip()
        if not url:
            return ""
        if "youtube.com/watch" in url:
            from urllib.parse import parse_qs, urlparse
            video_id = parse_qs(urlparse(url).query).get("v", [""])[0]
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"
        if "youtu.be/" in url:
            video_id = url.rstrip("/").rsplit("/", 1)[-1].split("?")[0]
            return f"https://www.youtube.com/embed/{video_id}"
        if "vimeo.com" in url and "/video/" not in url:
            video_id = url.rstrip("/").rsplit("/", 1)[-1].split("?")[0]
            if video_id.isdigit():
                return f"https://player.vimeo.com/video/{video_id}"
        return url

    # ------------------------------------------------------------------ gating
    def status_for(self, user):
        """
        The gating rule. Returns one of:
          locked      – prerequisite not approved, or release date in the future
          unlocked    – accessible, nothing submitted yet (or resubmission needed)
          in_progress – worksheet submitted, waiting for admin review
          completed   – submission approved
        """
        latest = (
            Submission.objects.filter(user=user, lesson=self)
            .order_by("-submitted_at")
            .first()
        )
        if Submission.objects.filter(
            user=user, lesson=self, status=Submission.Status.APPROVED
        ).exists():
            return "completed"
        if not self.is_unlocked_for(user):
            return "locked"
        if latest and latest.status == Submission.Status.SUBMITTED:
            return "in_progress"
        return "unlocked"

    def is_unlocked_for(self, user):
        if not self.is_released:
            return False
        if self.prerequisite_id is None:
            return True
        return Submission.objects.filter(
            user=user,
            lesson_id=self.prerequisite_id,
            status=Submission.Status.APPROVED,
        ).exists()


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "course"], name="unique_enrollment"),
        ]

    def __str__(self):
        return f"{self.user.username} → {self.course.title}"


def submission_upload_path(instance, filename):
    return f"submissions/user_{instance.user_id}/lesson_{instance.lesson_id}/{filename}"


class Submission(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted — awaiting review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected — resubmit"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="submissions")
    uploaded_file = models.FileField(upload_to=submission_upload_path)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SUBMITTED)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="reviewed_submissions",
    )
    feedback = models.TextField(blank=True, help_text="Shown to the student (especially on rejection).")

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.user.username} · {self.lesson} · {self.get_status_display()}"

    def mark(self, status, reviewer, feedback=None):
        self.status = status
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        if feedback is not None:
            self.feedback = feedback
        self.save()


def generate_invite_code():
    # Human-friendly: GSD-XXXX-XXXX (no ambiguous chars).
    alphabet = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
    chunk = lambda: "".join(secrets.choice(alphabet) for _ in range(4))
    return f"GSD-{chunk()}-{chunk()}"


class InviteCode(models.Model):
    """
    One-time signup code. The admin generates a code tied to one or more
    courses; whoever redeems it gets a student account already enrolled in
    those courses. Payments happen entirely outside the LMS.
    """

    code = models.CharField(max_length=20, unique=True, default=generate_invite_code)
    courses = models.ManyToManyField(Course, related_name="invite_codes")
    note = models.CharField(max_length=200, blank=True, help_text="Who this code is for (internal).")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="invite_codes_created",
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    used_by = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="invite_code_used",
    )
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.code

    @property
    def is_used(self):
        return self.used_by_id is not None

    def is_valid(self):
        if self.is_used:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

    def redeem(self, user):
        self.used_by = user
        self.used_at = timezone.now()
        self.save()
        for course in self.courses.all():
            Enrollment.objects.get_or_create(user=user, course=course)
