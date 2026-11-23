import re
from django import forms
from django.core.exceptions import ValidationError

from .models import Category, NursingDocument


class DocumentFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        max_length=100,
        strip=True,
        error_messages={
            "max_length": "Search query cannot exceed 100 characters.",
        },
    )
    category = forms.SlugField(
        required=False,
        max_length=120,
        error_messages={
            "invalid": "Invalid category filter selected.",
        },
    )

    def __init__(self, *args, valid_categories=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.valid_categories = valid_categories

    def clean_q(self):
        value = self.cleaned_data.get("q", "").strip()
        # Collapse repeated whitespace
        return re.sub(r"\s+", " ", value)

    def clean_category(self):
        slug = self.cleaned_data.get("category", "").strip()
        if not slug:
            return ""
        qs = self.valid_categories if self.valid_categories is not None else Category.objects.all()
        if not qs.filter(slug=slug).exists():
            raise ValidationError("Selected category does not exist.")
        return slug


class NursingDocumentAdminForm(forms.ModelForm):
    class Meta:
        model = NursingDocument
        fields = "__all__"

    def clean_title(self):
        title = (self.cleaned_data.get("title") or "").strip()
        if len(title) < 3:
            raise ValidationError("Document title must be at least 3 characters long.")
        return title

    def clean_description(self):
        description = (self.cleaned_data.get("description") or "").strip()
        if len(description) < 10:
            raise ValidationError("Description must be at least 10 characters long.")
        return description

    def clean_read_time(self):
        read_time = (self.cleaned_data.get("read_time") or "").strip()
        if not re.search(r"\d+", read_time):
            raise ValidationError("Estimated read time must include a numeric duration (e.g., '10 mins (estimated)').")
        return read_time