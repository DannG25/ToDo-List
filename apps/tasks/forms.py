"""
Módulo forms.py

Este módulo define los formularios utilizados en la aplicación, incluyendo:
- Formularios para la creación y actualización de tareas (TaskForm).
- Formularios para la configuración del servidor de correo electrónico (EmailConfigForm).
- Formularios personalizados de autenticación (EmailAuthenticationForm).
- Formularios para la creación y actualización de usuarios 
(CustomUserCreationForm, UserEditForm, UserUpdateForm).
- Formularios para la actualización del perfil de usuario (ProfileUpdateForm).
"""

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.conf import settings
from .models import Task


class TaskForm(forms.ModelForm):
    """
    Formulario para crear o actualizar una tarea.
    Incluye campos para el título, nota, fecha de vencimiento y archivo adjunto.
    """
    class Meta:
        model = Task
        fields = ['title', 'nota', 'fecha_vencimiento', 'archivo', 'priority']
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mensaje de ayuda para el campo archivo
        self.fields['archivo'].help_text = f'Tamaño máximo permitido: {settings.MAX_UPLOAD_SIZE/1024/1024}MB'

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')

        # Validación solo si hay archivo (campo opcional)
        if archivo:
            # Validación de tamaño
            if archivo.size > settings.MAX_UPLOAD_SIZE:
                raise forms.ValidationError(
                    f'El archivo es demasiado grande. Tamaño máximo permitido: {settings.MAX_UPLOAD_SIZE/1024/1024}MB'
                )

            # Validación de tipo de archivo (opcional)
            valid_extensions = ['.pdf', '.doc', '.docx',
                                '.jpg', '.png', '.xls', '.xlsx']
            if not any(archivo.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError(
                    'Tipo de archivo no permitido. Formatos aceptados: PDF, DOC, DOCX, JPG, PNG, XLS, XLSX'
                )

        return archivo


class EmailConfigForm(forms.Form):
    """
    Formulario para configurar los detalles del servidor de correo electrónico.
    Incluye campos para el servidor SMTP, puerto, TLS, correo electrónico y contraseña.
    """
    email_host = forms.CharField(label="Servidor SMTP", max_length=100)
    email_port = forms.IntegerField(label="Puerto SMTP")
    email_use_tls = forms.BooleanField(label="Usar TLS", required=False)
    email_host_user = forms.EmailField(label="Correo electrónico")
    email_host_password = forms.CharField(
        label="Contraseña", widget=forms.PasswordInput)


class EmailAuthenticationForm(AuthenticationForm):
    """
    Formulario de autenticación personalizado que permite el inicio de sesión
    con un correo electrónico o nombre de usuario.
    """
    username = forms.CharField(label="Correo electrónico o nombre de usuario")


class CustomUserCreationForm(UserCreationForm):
    """
    Formulario personalizado para la creación de usuarios.
    Incluye campos para el nombre de usuario, correo electrónico y contraseñas.
    """
    email = forms.EmailField(required=True, label="Correo electrónico")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
