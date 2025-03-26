from smtplib import SMTPException, SMTPConnectError, SMTPRecipientsRefused

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings
from django.core.mail import send_mail
from apps.tasks.models import Task, EmailConfig
from apps.api.serializers import TaskSerializer, EmailConfigSerializer


class HelloWorldAPIView(APIView):
    def get(self, request):
        print(request)
        return Response({"message": "Hello, World!"})


class HelloWorldViewSet(viewsets.ViewSet):
    def list(self, request):
        """
        Retorna un mensaje de saludo.
        """
        _ = request
        return Response({"message": "Hello, World!"})


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar las operaciones CRUD de las tareas.
    """
    queryset = Task.objects.all()  # pylint: disable=no-member
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtra las tareas para que solo el usuario autenticado pueda ver las suyas.
        """
        return Task.objects.filter(user=self.request.user)  # pylint: disable=no-member

    def perform_create(self, serializer):
        """
        Asigna el usuario autenticado como el propietario de la tarea al crearla.
        """
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_resolved(self, request, pk=None):
        """
        Marca una tarea como resuelta.
        """
        task = self.get_object()
        if task.resuelto:
            return Response(
                {'status': 'La tarea ya estaba resuelta', 'id': task.id},
                status=status.HTTP_200_OK
            )
        task.resuelto = True
        task.save()
        return Response(
            {'status': 'Tarea marcada como resuelta'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def tareas_pendientes(self, request):
        """
        Lista las tareas pendientes del usuario.
        """
        tareas_pendientes = self.get_queryset().filter(resuelto=False)
        serializer = self.get_serializer(tareas_pendientes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def tareas_resueltas(self, request):
        """
        Lista las tareas resueltas del usuario.
        """
        tareas_resueltas = self.get_queryset().filter(resuelto=True)
        serializer = self.get_serializer(tareas_resueltas, many=True)
        return Response(serializer.data)


class EmailConfigViewSet(viewsets.ViewSet):
    """
    ViewSet para manejar la configuración y envío de correos electrónicos.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def configure_email(self, request):
        """
        Configura los detalles del servidor de correo y los almacena en la base de datos.
        """
        user = request.user
        email_config, created = EmailConfig.objects.get_or_create(   # pylint: disable=no-member
            user=user)  # pylint: disable=no-member
        serializer = EmailConfigSerializer(email_config, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Configuración de correo guardada exitosamente.'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def send_email(self, request):
        
        """
        Envía un correo electrónico utilizando MailHog.
        """
        recipient = request.data.get('recipient', 'noreply@example.com')
        message = request.data.get(
            'message', 'Este es un correo predeterminado.')
        try:
            send_mail(
                subject=request.data.get('subject', 'Asunto predeterminado'),
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            return Response(
                {'message': f'Correo enviado a {recipient} exitosamente.'},
                status=status.HTTP_200_OK
            )
        except SMTPException as e:
            return Response(
                {'error': f'Error al enviar el correo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
