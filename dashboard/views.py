from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView
from accounts.models import CustomUser
from accounts.views import AdminRoleRequiredMixin

class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_admin_role():
            return redirect('dashboard:admin_panel')
        return super().dispatch(request, *args, **kwargs)


class AdminPanelView(AdminRoleRequiredMixin, TemplateView):
    template_name = 'dashboard/admin_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = CustomUser.objects.all().order_by('role', 'username')
        return context
