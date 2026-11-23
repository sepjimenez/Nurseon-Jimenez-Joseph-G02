from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView, ListView

from .forms import DocumentFilterForm
from .models import Category, NursingDocument, visible_documents_for


class DocumentListView(LoginRequiredMixin, ListView):
    model = NursingDocument
    template_name = "documents/list.html"
    context_object_name = "documents"

    def _get_visible_categories(self):
        visible_documents = visible_documents_for(self.request.user)
        return Category.objects.filter(documents__in=visible_documents).distinct()

    def get_filter_form(self):
        if not hasattr(self, "_filter_form"):
            self._filter_form = DocumentFilterForm(
                self.request.GET or None,
                valid_categories=self._get_visible_categories(),
            )
        return self._filter_form

    def get_queryset(self):
        queryset = visible_documents_for(self.request.user)
        form = self.get_filter_form()

        if self.request.GET and not form.is_valid():
            for field_errors in form.errors.values():
                for err in field_errors:
                    messages.error(self.request, err)
            return queryset

        search_query = form.cleaned_data.get("q", "") if form.is_bound else ""
        category_slug = form.cleaned_data.get("category", "") if form.is_bound else ""

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(doc_id__icontains=search_query)
                | Q(tags__name__icontains=search_query)
            ).distinct()
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.get_filter_form()
        context["categories"] = self._get_visible_categories()
        context["filter_form"] = form
        context["search_query"] = (
            form.cleaned_data.get("q", "")
            if form.is_bound and form.is_valid()
            else self.request.GET.get("q", "").strip()
        )
        context["selected_category"] = (
            form.cleaned_data.get("category", "")
            if form.is_bound and form.is_valid()
            else ""
        )
        return context


class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = NursingDocument
    template_name = "documents/detail.html"
    context_object_name = "document"

    def get_queryset(self):
        return visible_documents_for(self.request.user).prefetch_related(
            "content_sections",
            "sources",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_bookmarked"] = self.object.bookmarks.filter(
            pk=self.request.user.pk
        ).exists()
        return context


class DocumentBookmarkView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk):
        document = get_object_or_404(visible_documents_for(request.user), pk=pk)
        if document.bookmarks.filter(pk=request.user.pk).exists():
            document.bookmarks.remove(request.user)
            messages.info(request, f'Removed "{document.title}" from your bookmarks.')
        else:
            document.bookmarks.add(request.user)
            messages.success(request, f'Bookmarked "{document.title}".')
        return redirect("documents:detail", pk=document.pk)