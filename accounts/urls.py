from django.urls import path, include
from .views import SignUpView, ProfileUpdateView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('', include('django.contrib.auth.urls')),
]
