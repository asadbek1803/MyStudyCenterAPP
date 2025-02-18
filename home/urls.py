from django.urls import path
from .views import role_based_redirect, team, app_download, vacancy_view, home, dashboard, error_page, arxiv, about

urlpatterns = [
    path('', home, name='home'), 
    path('restart/', role_based_redirect, name='base_url'),
    path('vakansiyalar/', vacancy_view, name='vakansiyalar'),
    path('dashboard/', dashboard, name='dashboard'),  # Added new URL for dashboard
    path('error_page/', error_page, name='block_error_page'),
    path('etirof/', arxiv, name='etirof'), # Added new URL for
    path('about/', about, name='about'),
    path('app/free/download/', app_download, name='app_download'),
    path('team/', team, name='team')
    
]
