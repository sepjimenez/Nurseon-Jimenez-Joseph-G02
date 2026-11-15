from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .forms import (
    AdminSetUserPasswordForm,
    AdminStudentChangeForm,
    AdminUserChangeForm,
    CustomUserChangeForm,
    CustomUserCreationForm,
)
from .models import CustomUser


class AdminRoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin_role()

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Access restricted to administrators.")
        return redirect('dashboard:home')


class SignUpView(SuccessMessageMixin, CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
    success_message = "Account created successfully. You can now sign in."

    def form_valid(self, form):
        form.instance.role = CustomUser.Role.STUDENT
        return super().form_valid(form)


class RoleDashboardRedirectView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.is_admin_role():
            return redirect('dashboard:admin_panel')
        return redirect('dashboard:home')


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')
    success_message = "Your profile details have been saved."

    def get_object(self):
        return self.request.user


class AdminUserUpdateView(AdminRoleRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CustomUser
    form_class = AdminUserChangeForm
    template_name = 'dashboard/student_form.html'
    pk_url_kwarg = 'user_id'
    success_url = reverse_lazy('dashboard:admin_panel')
    success_message = "User profile details updated successfully."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['requesting_user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['target_user'] = self.object
        return context


AdminStudentUpdateView = AdminUserUpdateView


class AdminUserPasswordView(AdminRoleRequiredMixin, View):
    template_name = 'dashboard/user_password_form.html'

    def get(self, request, user_id):
        target_user = get_object_or_404(CustomUser, pk=user_id)
        form = AdminSetUserPasswordForm(user=target_user)
        return render(request, self.template_name, {
            'form': form,
            'target_user': target_user,
        })

    def post(self, request, user_id):
        target_user = get_object_or_404(CustomUser, pk=user_id)
        form = AdminSetUserPasswordForm(request.POST, user=target_user)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Password for {target_user.username} was updated successfully."
            )
            return redirect('dashboard:admin_panel')
        return render(request, self.template_name, {
            'form': form,
            'target_user': target_user,
        })


class AdminToggleUserRoleView(AdminRoleRequiredMixin, View):
    def post(self, request, user_id):
        target_user = get_object_or_404(CustomUser, pk=user_id)
        if target_user.role == CustomUser.Role.STUDENT:
            target_user.role = CustomUser.Role.ADMIN
            target_user.save()
            messages.success(request, f"User '{target_user.username}' was promoted to Administrator.")
        else:
            can_demote, reason = target_user.can_be_demoted_by(request.user)
            if not can_demote:
                messages.error(request, reason)
            else:
                target_user.role = CustomUser.Role.STUDENT
                target_user.save()
                messages.success(request, f"User '{target_user.username}' was changed to Student.")
        return redirect('dashboard:admin_panel')


class AdminUserDeleteView(AdminRoleRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'dashboard/student_confirm_delete.html'
    pk_url_kwarg = 'user_id'
    success_url = reverse_lazy('dashboard:admin_panel')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        can_delete, reason = self.object.can_be_deleted_by(request.user)
        if not can_delete:
            messages.error(request, reason)
            return redirect('dashboard:admin_panel')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        target = self.get_object()
        can_delete, reason = target.can_be_deleted_by(self.request.user)
        if not can_delete:
            messages.error(self.request, reason)
            return redirect('dashboard:admin_panel')
        username = target.username
        response = super().form_valid(form)
        messages.success(self.request, f"User account '{username}' was deleted.")
        return response


class AdminStudentDeleteView(AdminUserDeleteView):
    pk_url_kwarg = 'student_id'
