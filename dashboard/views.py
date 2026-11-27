from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView
from accounts.models import CustomUser
from accounts.views import AdminRoleRequiredMixin
from documents.models import visible_documents_for

class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_admin_role():
            return redirect('dashboard:admin_panel')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["documents"] = visible_documents_for(self.request.user)[:4]
        return context


class AdminPanelView(AdminRoleRequiredMixin, ListView):
    model = CustomUser
    template_name = 'dashboard/admin_panel.html'
    context_object_name = 'users'

    def get_queryset(self):
        return CustomUser.objects.filter(role=CustomUser.Role.STUDENT)