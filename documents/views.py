from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView, ListView

from .models import Category, NursingDocument, visible_documents_for


class DocumentListView(LoginRequiredMixin, ListView):
    model = NursingDocument
    template_name = "documents/list.html"
    context_object_name = "documents"

    def get_queryset(self):
        queryset = visible_documents_for(self.request.user)
        search_query = self.request.GET.get("q", "").strip()
        category_slug = self.request.GET.get("category", "").strip()

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
        visible_documents = visible_documents_for(self.request.user)
        context["categories"] = Category.objects.filter(
            documents__in=visible_documents
        ).distinct()
        context["search_query"] = self.request.GET.get("q", "").strip()
        context["selected_category"] = self.request.GET.get("category", "").strip()
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
        else:
            document.bookmarks.add(request.user)
        return redirect("documents:detail", pk=document.pk)
