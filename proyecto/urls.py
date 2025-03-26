"""
 Configuración de URL para el proyecto.

La lista `urlpatterns` enruta URLs a vistas. Para más información consulte:
 https://docs.djangoproject.com/en/4.2/topics/http/urls/
Ejemplos:
Función views
 1. Añade una importación: from my_app import views
 2. Añade una URL a urlpatterns: path('') views.home.
 Añadir una URL a urlpatterns: path('', views.home, name='home')Vistas basadas en clases
 1. Añadir una importación: from other_app.views import Home
 2. Añadir una URL a urlpatterns: path('', views.home, name='home')
 Añade una URL a urlpatterns: path('', Home.as_view(), name='home')Incluyendo otra URLconf
 1. Importa la función include(): from django.urls import include, path
 2. Añade una URL a urlpatterns: path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # Panel de administración
    path('admin/', admin.site.urls),
    # Incluye las rutas de tu aplicación
    path('api/', include('apps.api.urls')),

    # URLs de autenticación
    path('users/register/', views.register,
         name='register'),  # Registro de usuarios
    path('users/login/', views.user_login, name='login'),  # Inicio de sesión
    path('users/logout/', auth_views.LogoutView.as_view(next_page='login'),
         name='logout'),

    #  Recuperación de contraseña

    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt',
             success_url='/password-reset/done/'
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='/reset/done/'
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # Página de inicio
    path('', views.home, name="home"),

    # Incluir las URLs de otras aplicaciones
    path('tasks/', include('apps.tasks.urls')),
    path('api/v1.0/', include('apps.api.urls')),

]
