from django.contrib import admin
from django.db import transaction

from .forms import NursingDocumentAdminForm
from .models import Category, DocumentSection, DocumentSource, NursingDocument, Tag


class DocumentSectionInline(admin.TabularInline):
    model = DocumentSection
    extra = 1


class DocumentSourceInline(admin.TabularInline):
    model = DocumentSource
    extra = 1


@admin.register(NursingDocument)
class NursingDocumentAdmin(admin.ModelAdmin):
    form = NursingDocumentAdminForm
    list_display = ("title", "category", "is_published", "publish_date", "created_by")
    list_filter = ("is_published", "category", "publish_date")
    search_fields = ("title", "description", "doc_id")
    filter_horizontal = ("tags",)
    readonly_fields = ("created_by", "doc_id")
    inlines = (DocumentSectionInline, DocumentSourceInline)

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            if not change:
                obj.created_by = request.user
            super().save_model(request, obj, form, change)


admin.site.register(Category)
admin.site.register(Tag)