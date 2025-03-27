# 1. Importaciones estándar de Python
from smtplib import SMTPException
import mimetypes
import os


# 2. Importaciones de terceros (Django y otras librerías externas)
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.http import FileResponse, Http404

# 3. Importaciones locales (tu aplicación)
from .models import Task
from .forms import TaskForm, EmailConfigForm

User = get_user_model()


@login_required
def task_list(request):
    """
    Muestra una lista de tareas pendientes y resueltas con paginación independiente.
    """
    # Filtra las tareas pendientes y resueltas
    tareas_pendientes = Task.objects.filter(user=request.user, resuelto=False).order_by(   # pylint: disable=no-member
        'fecha_asignacion')
    tareas_resueltas = Task.objects.filter(user=request.user, resuelto=True).order_by(   # pylint: disable=no-member
        'fecha_asignacion')

    # Configura los paginadores
    pendientes_paginator = Paginator(tareas_pendientes, 5)
    resueltas_paginator = Paginator(tareas_resueltas, 5)

    # Obtén el número de página de cada lista desde los parámetros de la solicitud
    pendientes_page_number = request.GET.get('pendientes_page', 1)
    resueltas_page_number = request.GET.get('resueltas_page', 1)

    # Obtén las páginas paginadas
    tareas_pendientes_paginated = pendientes_paginator.get_page(
        pendientes_page_number)
    tareas_resueltas_paginated = resueltas_paginator.get_page(
        resueltas_page_number)

    # Renderiza la plantilla con las tareas
    return render(request, 'tasks/task_list.html', {
        'tareas_pendientes': tareas_pendientes_paginated,
        'tareas_resueltas': tareas_resueltas_paginated
    })


@login_required
def task_create(request):
    """
    Maneja la creación de una nueva tarea.
    """
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Tarea creada exitosamente.')
            return redirect('task_list')
        else:
            messages.error(
                request, 'Error al crear la tarea. Verifica los datos.')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})


@login_required
def task_update(request, pk):
    """
    Maneja la actualización de una tarea existente.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarea actualizada exitosamente.')
            return redirect('task_list')
        else:
            messages.error(request, 'Error al actualizar la tarea.')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_update.html', {'form': form})


@login_required
def task_delete(request,  pk):
    """
    Gestiona la eliminación de una tarea.
    """
    task = get_object_or_404(Task,  pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Tarea eliminada exitosamente.')
        return redirect('task_list')
    return render(request, 'tasks/task_delete.html', {'task': task})


@login_required
@require_POST
def check_resolve(request, pk):
    """
    Marca una tarea como resuelta y devuelve una respuesta JSON.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if task.resuelto:
        messages.error(request, 'La tarea ya está resuelta')
        return JsonResponse({
            'status': 'error',
            'message': 'La tarea ya está resuelta',
            'alert': {
                'icon': 'error',
                'title': 'La tarea ya está resuelta'
            }
        }, status=400)

    task.resuelto = True
    task.save()
    messages.success(request, 'Tarea marcada como resuelta')

    return JsonResponse({
        'status': 'success',
        'message': 'Tarea marcada como resuelta',
        'task_id': task.id,
        'alert': {
            'icon': 'success',
            'title': 'Tarea marcada como resuelta'
        }
    })


@login_required
def task_file_download(request, pk):
    """
    Descarga o visualiza un archivo adjunto a una tarea.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if not task.archivo:  # Verifica si hay un archivo adjunto
        raise Http404("Esta tarea no tiene archivo adjunto")

    file_path = task.archivo.path
    if not os.path.exists(file_path):
        raise Http404("El archivo no existe")

    # Determina el tipo MIME del archivo
    content_type, _ = mimetypes.guess_type(file_path)

    # Si no se puede determinar el tipo MIME, usa un valor por defecto
    if content_type is None:
        content_type = 'application/octet-stream'

    # Para visualización en el navegador (si es compatible)
    if request.GET.get('preview'):
        return FileResponse(
            open(file_path, 'rb'),
            content_type=content_type
        )

    # Para descarga
    return FileResponse(
        open(file_path, 'rb'),
        as_attachment=True,
        filename=os.path.basename(file_path),
        content_type=content_type
    )


def configure_email(request):
    """
    Configura los detalles del servidor de correo y los almacena en la sesión.
    """
    if request.method == 'POST':
        form = EmailConfigForm(request.POST)
        if form.is_valid():
            email_config = {
                'email_host': form.cleaned_data['email_host'],
                'email_port': form.cleaned_data['email_port'],
                'email_use_tls': form.cleaned_data['email_use_tls'],
                'email_host_user': form.cleaned_data['email_host_user'],
                'email_host_password': form.cleaned_data['email_host_password'],
            }
            request.session['email_config'] = email_config
            messages.success(
                request, 'Configuración de correo guardada exitosamente.')
            return redirect('send_email')
    else:
        form = EmailConfigForm()
    return render(request, 'email_config.html', {'form': form})


def send_email(request):
    """
    Envía un correo electrónico utilizando la configuración de correo almacenada en la sesión.
    """
    email_config = request.session.get('email_config', {})

    try:
        send_mail(
            subject="Prueba de MailHog",
            message="¡Este es un correo de prueba enviado desde Django usando MailHog!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["usuario@ejemplo.com"],
            fail_silently=False,
            auth_user=email_config.get('email_host_user', ''),
            auth_password=email_config.get('email_host_password', ''),
            connection=None,  # Usar la configuración de settings.py
        )
        return JsonResponse({"mensaje": "Correo enviado correctamente"})

    except SMTPException as e:
        messages.error(request, f'Error al enviar el correo: {str(e)}')
        return render(request, 'email_error.html', {'error': str(e)})
