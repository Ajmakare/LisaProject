from django.urls import include, path

from .views import *

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', index, name='index'),
    path("signup/", SignUpView.as_view(), name="signup"),
    path('logout/', pagelogout, name='logout'),
    path('profile/', profile, name='profile'),
    path('control_panel/', controlPanel, name='control_panel'),
    path('program/', program, name='program'),
    path('subscription/', subscription, name='subscription'),
    path('process_subscription/', process_subscription, name='process_subscription'),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('paypal-return/', PaypalSuccess.as_view(), name='paypal-return'),
    path('paypal-cancel/', PayPalCancel.as_view(), name='paypal-cancel'),
    path('user_info', controlPanel, name='user_info'),
    path('paypal_webhook/', paypal_webhook, name='paypal_webhook'),
    path('remove-group/<int:user_id>/', remove_group, name='remove_group'),
    path('reset_password', auth_views.PasswordResetView.as_view(), name="reset_password"),
    path('reset_password_sent', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('reset_password_complete', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

]