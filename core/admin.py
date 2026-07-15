from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import Course, Enrollment, InviteCode, Lesson, Submission, User

admin.site.site_header = "GSD HQ · Mission Control"
admin.site.site_title = "GSD HQ Admin"
admin.site.index_title = "Manage students, courses & submissions"


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    autocomplete_fields = ["course"]


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    inlines = [EnrollmentInline]
    list_display = ["username", "first_name", "last_name", "email", "role", "is_active", "date_joined"]
    list_filter = ["is_staff", "is_active", "enrollments__course"]
    search_fields = ["username", "first_name", "last_name", "email"]

    @admin.display(description="Role", boolean=False)
    def role(self, obj):
        return "Admin" if obj.is_staff else "Student"


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ["order", "title", "slug", "video_url", "worksheet_file", "prerequisite", "release_date"]
    prepopulated_fields = {"slug": ["title"]}
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "order", "lesson_count", "student_count"]
    list_filter = ["status"]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ["title"]}
    inlines = [LessonInline]

    @admin.display(description="Lessons")
    def lesson_count(self, obj):
        return obj.lessons.count()

    @admin.display(description="Students")
    def student_count(self, obj):
        return obj.enrollments.count()


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["__str__", "course", "order", "has_video", "has_worksheet", "release_date"]
    list_filter = ["course"]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ["title"]}
    ordering = ["course", "order"]

    @admin.display(description="Video", boolean=True)
    def has_video(self, obj):
        return bool(obj.video_url)

    @admin.display(description="Worksheet", boolean=True)
    def has_worksheet(self, obj):
        return bool(obj.worksheet_file)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ["user", "course", "enrolled_at"]
    list_filter = ["course"]
    search_fields = ["user__username", "user__email"]
    autocomplete_fields = ["user", "course"]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ["user", "lesson", "status", "submitted_at", "reviewed_by", "file_link"]
    list_filter = ["status", "lesson__course"]
    search_fields = ["user__username", "user__email", "lesson__title"]
    readonly_fields = ["user", "lesson", "uploaded_file", "submitted_at", "file_link"]
    fields = ["user", "lesson", "file_link", "submitted_at", "status", "feedback", "reviewed_by", "reviewed_at"]
    actions = ["approve_submissions", "reject_submissions"]
    date_hierarchy = "submitted_at"

    def has_add_permission(self, request):
        return False  # submissions only come from student uploads

    @admin.display(description="File")
    def file_link(self, obj):
        if not obj.pk or not obj.uploaded_file:
            return "—"
        return format_html('<a href="{}">Download</a>', reverse("submission_download", args=[obj.pk]))

    @admin.action(description="Approve selected submissions (unlocks the next lesson)")
    def approve_submissions(self, request, queryset):
        updated = queryset.update(
            status=Submission.Status.APPROVED,
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )
        self.message_user(request, f"{updated} submission(s) approved.")

    @admin.action(description="Reject selected submissions (student must resubmit)")
    def reject_submissions(self, request, queryset):
        updated = queryset.update(
            status=Submission.Status.REJECTED,
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )
        self.message_user(request, f"{updated} submission(s) rejected.")

    def save_model(self, request, obj, form, change):
        if "status" in form.changed_data:
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(InviteCode)
class InviteCodeAdmin(admin.ModelAdmin):
    list_display = ["code", "note", "course_list", "created_at", "expires_at", "status"]
    list_filter = ["courses"]
    search_fields = ["code", "note", "used_by__username"]
    filter_horizontal = ["courses"]
    readonly_fields = ["code", "created_at", "created_by", "used_by", "used_at"]

    @admin.display(description="Courses")
    def course_list(self, obj):
        return ", ".join(obj.courses.values_list("title", flat=True)) or "—"

    @admin.display(description="Status")
    def status(self, obj):
        if obj.is_used:
            return format_html("Used by <b>{}</b>", obj.used_by)
        return "Valid" if obj.is_valid() else "Expired"

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
