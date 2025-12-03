# contact/views.py

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import ContactMessage
from .serializers import (
    ContactMessageSerializer,
    ContactMessageCreateSerializer,
    ContactMessageAdminSerializer
)


class ContactMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les messages de contact
    POST: Public (créer un message)
    GET/PUT/PATCH/DELETE: Admin uniquement
    """
    queryset = ContactMessage.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_read']
    search_fields = ['first_name', 'last_name', 'email', 'subject', 'message']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ContactMessageCreateSerializer
        elif self.request.user.is_authenticated:
            return ContactMessageAdminSerializer
        return ContactMessageSerializer
    
    def get_queryset(self):
        queryset = ContactMessage.objects.all()
        
        # Filtre par statut de lecture
        unread_only = self.request.query_params.get('unread_only')
        if unread_only and unread_only.lower() == 'true':
            queryset = queryset.filter(is_read=False)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Créer un message de contact et notifier l'admin
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        
        # Envoyer une notification à l'admin
        try:
            self._send_admin_notification(message)
        except Exception as e:
            print(f"Erreur envoi email admin: {e}")
        
        # Envoyer une confirmation au client
        try:
            self._send_confirmation_to_customer(message)
        except Exception as e:
            print(f"Erreur envoi email client: {e}")
        
        return Response({
            'message': 'Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.',
            'data': ContactMessageSerializer(message).data
        }, status=status.HTTP_201_CREATED)
    
    def _send_admin_notification(self, message):
        """
        Notifier l'admin d'un nouveau message
        """
        admin_emails = getattr(settings, 'ADMIN_NOTIFICATION_EMAILS', ['admin@bookstore.com'])
        
        subject = f'Nouveau message de contact - {message.subject or "Sans sujet"}'
        body = f"""
        Nouveau message de contact reçu :
        
        De: {message.full_name} ({message.email})
        Sujet: {message.subject or "Sans sujet"}
        
        Message:
        {message.message}
        
        ---
        Connectez-vous au backoffice pour répondre.
        """
        
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            fail_silently=False,
        )
    
    def _send_confirmation_to_customer(self, message):
        """
        Envoyer une confirmation au client
        """
        subject = 'Nous avons bien reçu votre message'
        body = f"""
        Bonjour {message.first_name},
        
        Nous avons bien reçu votre message concernant : {message.subject or "votre demande"}.
        
        Notre équipe vous répondra dans les plus brefs délais.
        
        Merci de nous avoir contactés !
        
        L'équipe Bookstore
        """
        
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[message.email],
            fail_silently=False,
        )
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Marquer un message comme lu
        """
        message = self.get_object()
        message.is_read = True
        message.save()
        
        return Response({
            'message': 'Message marqué comme lu',
            'data': ContactMessageAdminSerializer(message).data
        })
    
    @action(detail=True, methods=['post'])
    def mark_as_unread(self, request, pk=None):
        """
        Marquer un message comme non lu
        """
        message = self.get_object()
        message.is_read = False
        message.save()
        
        return Response({
            'message': 'Message marqué comme non lu',
            'data': ContactMessageAdminSerializer(message).data
        })
    
    @action(detail=True, methods=['post'])
    def mark_as_replied(self, request, pk=None):
        """
        Marquer un message comme ayant reçu une réponse
        """
        message = self.get_object()
        message.replied_at = timezone.now()
        message.is_read = True
        
        # Optionnel : ajouter des notes admin
        admin_notes = request.data.get('admin_notes', '')
        if admin_notes:
            message.admin_notes = admin_notes
        
        message.save()
        
        return Response({
            'message': 'Message marqué comme répondu',
            'data': ContactMessageAdminSerializer(message).data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Statistiques des messages de contact
        """
        total_messages = ContactMessage.objects.count()
        unread_messages = ContactMessage.objects.filter(is_read=False).count()
        replied_messages = ContactMessage.objects.filter(replied_at__isnull=False).count()
        
        return Response({
            'total_messages': total_messages,
            'unread_messages': unread_messages,
            'replied_messages': replied_messages,
            'pending_messages': total_messages - replied_messages,
        })
    
    @action(detail=False, methods=['post'])
    def bulk_mark_as_read(self, request):
        """
        Marquer plusieurs messages comme lus
        """
        message_ids = request.data.get('message_ids', [])
        
        if not message_ids:
            return Response({
                'error': 'message_ids requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        updated_count = ContactMessage.objects.filter(
            id__in=message_ids
        ).update(is_read=True)
        
        return Response({
            'message': f'{updated_count} message(s) marqué(s) comme lu(s)',
            'updated_count': updated_count
        })