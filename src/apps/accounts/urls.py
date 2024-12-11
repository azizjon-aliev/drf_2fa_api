from django.urls import path
from .views import OTPConfirmView, UserLoginView, UserRegisterView

urlpatterns = [
	path('register/', UserRegisterView.as_view(), name='user-register'),
	path('login/', UserLoginView.as_view(), name='user-login'),
	path('confirm-otp/', OTPConfirmView.as_view(), name='confirm-otp'),
]
