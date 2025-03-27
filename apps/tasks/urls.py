from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
# from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views

urlpatterns = [

    # Incluye las URLs de la API
    path('', views.task_list, name='task_list'),
    path('create/', views.task_create, name='task_create'),
    path('update/<int:pk>/', views.task_update, name='task_update'),
    path('delete/<int:pk>/', views.task_delete, name='task_delete'),
    path('check_resolve/<int:pk>/', views.check_resolve, name='check_resolve'),
    path('task/<int:pk>/file/', views.task_file_download,
         name='task_file_download'),

    # URLs para la configuración y envío de correo
    path('configure_email/', views.configure_email, name='configure_email'),
    path('send_email/', views.send_email, name='send_email'),
    path('configure-email/', views.configure_email, name='configure_email'),


    path('', RedirectView.as_view(url='login/')),

]  # Solo en desarrollo: servir archivos multimedia
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
