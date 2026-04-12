from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from django.conf import settings
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('report/', views.report, name='report'),
    path('scams/', views.scams, name='scams'),
    path('scam/<int:pk>/', views.scam_detail, name='scam_detail'),

path('ar/simulator/', views.simulator_view, name='simulator_ar'),
path('en/simulator/', views.simulator_view, name='simulator_en'),

    path('en/', views.home_en, name='home_en'),
    path('en/about/', views.about_en, name='about_en'),
    path('en/report/', views.report_en, name='report_en'),
    path('en/scams/', views.scams_en, name='scams_en'),
    path('en/scam/<int:pk>/', views.scam_detail_en, name='scam_detail_en'),
]
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
