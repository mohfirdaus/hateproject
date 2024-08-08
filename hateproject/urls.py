"""
URL configuration for hateproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from hateapp import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.berita, name='berita'),
    path('detail_berita/<int:berita_id>/', views.detail_berita, name='detail_berita'),
    path('predict_comments/<int:berita_id>/', views.predict_comments, name='predict_comments'),
    path('list_berita/', views.list_berita, name="list_berita"),
    path('delete_berita/<int:berita_id>/', views.delete_berita, name='delete_berita'),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name='logout'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)