from django.urls import path, include
from .views import SignIn, SignOut, save_telegram_id, send_notification, save_firebase_token, settings_view, get_latest_notification
urlpatterns = [
    path('login/', SignIn, name='login'),
    path('logout/', SignOut, name='logout'),
    path('save/fcm/token/', save_firebase_token, name='save_user_token'),
    path('settings/', settings_view, name='settings'),
    path('save-session/', save_telegram_id, name='save_session'),
    path('notify/<str:role>/', send_notification, name='notify_users'),
    path('get_last_notification/', get_latest_notification, name="get_notification")
]