from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Arabic
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('report/', views.report, name='report'),
    path('scams/', views.scams, name='scams'),
    path('scam/<int:pk>/', views.scam_detail, name='scam_detail'),
    path('ar/simulator/', views.simulator_view, name='simulator_ar'),
    path('ar/login/', views.login_view, name='login_ar'),
    path('ar/register/', views.register_view, name='register_ar'),
    path('ar/logout/', views.logout_view, name='logout_ar'),
    path('ar/profile/', views.profile_view, name='profile_ar'),
    path('ar/leaderboard/', views.leaderboard_view, name='leaderboard_ar'),
    path('ar/scenarios/', views.phishing_list_view, name='phishing_list_ar'),
    path('ar/scenarios/<int:pk>/', views.phishing_detail_view, name='phishing_detail_ar'),
    path('ar/my-reports/', views.my_reports_view, name='my_reports_ar'),

    # English
    path('en/', views.home_en, name='home_en'),
    path('en/about/', views.about_en, name='about_en'),
    path('en/report/', views.report_en, name='report_en'),
    path('en/scams/', views.scams_en, name='scams_en'),
    path('en/scam/<int:pk>/', views.scam_detail_en, name='scam_detail_en'),
    path('en/simulator/', views.simulator_view, name='simulator_en'),
    path('en/login/', views.login_view, name='login_en'),
    path('en/register/', views.register_view, name='register_en'),
    path('en/logout/', views.logout_view, name='logout_en'),
    path('en/profile/', views.profile_view, name='profile_en'),
    path('en/leaderboard/', views.leaderboard_view, name='leaderboard_en'),
    path('en/scenarios/', views.phishing_list_view, name='phishing_list_en'),
    path('en/scenarios/<int:pk>/', views.phishing_detail_view, name='phishing_detail_en'),
    path('en/my-reports/', views.my_reports_view, name='my_reports_en'),

    # API
    path('api/submit-answer/', views.submit_answer, name='submit_answer'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
