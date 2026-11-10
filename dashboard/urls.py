from django.urls import path
from .views import DashboardHomeView, AdminPanelView

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardHomeView.as_view(), name='home'),
    path('admin-panel/', AdminPanelView.as_view(), name='admin_panel'),
]