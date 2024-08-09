from django.contrib import admin
from django.urls import path
from hateapp import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.berita, name='berita'),
    path('detail_berita/<str:berita_id>/', views.detail_berita, name='detail_berita'),
    path('predict_comments/<str:berita_id>/', views.predict_comments, name='predict_comments'),
    path('list_berita/', views.list_berita, name="list_berita"),
    path('delete_berita/<str:berita_id>/', views.delete_berita, name='delete_berita'),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name='logout'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
