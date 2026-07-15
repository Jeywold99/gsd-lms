from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import FileExtensionValidator

from .models import InviteCode, Submission, User


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["uploaded_file"]
        labels = {"uploaded_file": "Your completed worksheet"}

    uploaded_file = forms.FileField(
        label="Your completed worksheet",
        validators=[FileExtensionValidator(settings.SUBMISSION_ALLOWED_EXTENSIONS)],
        widget=forms.ClearableFileInput(attrs={"accept": ".pdf,.png,.jpg,.jpeg,.doc,.docx"}),
    )

    def clean_uploaded_file(self):
        f = self.cleaned_data["uploaded_file"]
        max_bytes = settings.SUBMISSION_MAX_MB * 1024 * 1024
        if f.size > max_bytes:
            raise forms.ValidationError(
                f"File is too big ({f.size / (1024 * 1024):.1f} MB). "
                f"Max is {settings.SUBMISSION_MAX_MB} MB."
            )
        return f


class InviteSignupForm(UserCreationForm):
    """Redeem a one-time invite code and create the student account in one go."""

    code = forms.CharField(label="Invite code", max_length=20)
    first_name = forms.CharField(label="First name", max_length=150)
    last_name = forms.CharField(label="Last name", max_length=150, required=False)
    email = forms.EmailField(label="Email")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def clean_code(self):
        raw = self.cleaned_data["code"].strip().upper()
        try:
            invite = InviteCode.objects.get(code=raw)
        except InviteCode.DoesNotExist:
            raise forms.ValidationError("That invite code doesn't exist. Check it and try again.")
        if not invite.is_valid():
            raise forms.ValidationError("That invite code has already been used or has expired.")
        self.invite = invite
        return raw

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            self.invite.redeem(user)
        return user


class TOTPTokenForm(forms.Form):
    token = forms.CharField(
        label="6-digit code",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "one-time-code", "autofocus": True}),
    )
