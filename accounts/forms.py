from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


def _clean_unique_email(form):
    email = form.cleaned_data.get('email', '').strip().lower()
    if not email:
        return email
    existing_users = CustomUser.objects.filter(email__iexact=email)
    if form.instance.pk:
        existing_users = existing_users.exclude(pk=form.instance.pk)
    if existing_users.exists():
        raise forms.ValidationError("An account with this email already exists.")
    return email


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'specialization')

    def clean_email(self):
        return _clean_unique_email(self)


class CustomUserChangeForm(UserChangeForm):
    password = None
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'specialization')

    def clean_email(self):
        return _clean_unique_email(self)


class AdminUserChangeForm(CustomUserChangeForm):
    role = forms.ChoiceField(
        choices=CustomUser.Role.choices,
        widget=forms.Select(attrs={
            'class': 'w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-nurseon/40 focus:border-nurseon transition',
        }),
    )

    class Meta(CustomUserChangeForm.Meta):
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'specialization',
            'role',
        )
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-nurseon/40 focus:border-nurseon transition',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-nurseon/40 focus:border-nurseon transition',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-nurseon/40 focus:border-nurseon transition',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-nurseon/40 focus:border-nurseon transition',
            }),
            'specialization': forms.TextInput(attrs={
                'class': 'w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-nurseon/40 focus:border-nurseon transition',
            }),
        }

    def __init__(self, *args, requesting_user=None, **kwargs):
        self.requesting_user = requesting_user
        super().__init__(*args, **kwargs)

    def clean_role(self):
        new_role = self.cleaned_data.get('role')
        if self.instance.pk and self.instance.role == CustomUser.Role.ADMIN and new_role != CustomUser.Role.ADMIN:
            can_demote, reason = self.instance.can_be_demoted_by(self.requesting_user)
            if not can_demote:
                raise forms.ValidationError(reason)
        return new_role


AdminStudentChangeForm = AdminUserChangeForm


class AdminSetUserPasswordForm(forms.Form):
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-nurseon/40 focus:border-nurseon transition',
            'placeholder': 'Enter new password',
        }),
    )
    confirm_password = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-nurseon/40 focus:border-nurseon transition',
            'placeholder': 'Confirm new password',
        }),
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password")
        p2 = cleaned_data.get("confirm_password")
        if p1 and p2:
            if p1 != p2:
                raise forms.ValidationError("Passwords do not match.")
            try:
                password_validation.validate_password(p1, self.user)
            except forms.ValidationError as exc:
                self.add_error("new_password", exc)
        return cleaned_data

    def save(self):
        if self.user:
            self.user.set_password(self.cleaned_data['new_password'])
            self.user.save()
            return self.user
