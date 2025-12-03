# orders/views.py

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count, Sum
from datetime import datetime, timedelta

from .models import Order, OrderItem, Country
from .serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    OrderCreateSerializer,
    OrderUpdateStatusSerializer,
    CountrySerializer
)
from .utils import generate_invoice_pdf


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les pays (lecture seule pour public)
    """
    queryset = Country.objects.filter(is_active=True)
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des commandes
    """
    queryset = Order.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'country']
    search_fields = ['email', 'first_name', 'last_name', 'tracking_number']
    ordering_fields = ['created_at', 'total']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action in ['create', 'invoice']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action == 'list':
            return OrderListSerializer
        elif self.action == 'update_status':
            return OrderUpdateStatusSerializer
        return OrderDetailSerializer
    
    def get_queryset(self):
        queryset = Order.objects.all().select_related('country').prefetch_related('items__book')
        
        # Filtres de date
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Créer une commande et envoyer les emails
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        # Envoyer les emails
        try:
            self._send_order_emails(order)
        except Exception as e:
            print(f"Erreur envoi email: {e}")
        
        return Response({
            'message': 'Commande créée avec succès',
            'order': OrderDetailSerializer(order, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    def _send_order_emails(self, order):
        """
        Envoyer les emails de confirmation de commande
        """
        # Générer la facture PDF
        invoice_pdf = generate_invoice_pdf(order)
        
        # Email au client
        self._send_customer_email(order, invoice_pdf)
        
        # Email à l'admin
        self._send_admin_notification(order)
    
    def _send_customer_email(self, order, invoice_pdf):
        """
        Envoyer l'email de confirmation au client
        """
        context = {
            'order': order,
            'items': order.items.all(),
        }
        
        html_content = render_to_string('emails/order_confirmation.html', context)
        text_content = f"""
        Bonjour {order.full_name},
        
        Votre commande #{order.id} a été confirmée !
        
        Récapitulatif :
        - Sous-total: {order.subtotal / 100}€
        - Frais de port: {order.shipping_cost / 100}€
        - Total: {order.total / 100}€
        
        Articles commandés:
        """
        
        for item in order.items.all():
            text_content += f"\n- {item.book_title} x{item.quantity} = {item.subtotal / 100}€"
        
        text_content += f"""
        
        Adresse de livraison:
        {order.full_address}
        
        Vous recevrez un email avec le numéro de suivi dès l'expédition de votre commande.
        
        Merci pour votre confiance !
        L'équipe zoonova
        """
        
        email = EmailMultiAlternatives(
            subject=f'Confirmation de commande #{order.id}',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Joindre la facture PDF
        email.attach(f'facture_{order.id}.pdf', invoice_pdf, 'application/pdf')
        
        email.send(fail_silently=False)
    
    def _send_admin_notification(self, order):
        """
        Envoyer une notification à l'admin
        """
        admin_emails = settings.ADMIN_NOTIFICATION_EMAILS if hasattr(settings, 'ADMIN_NOTIFICATION_EMAILS') else ['admin@zoonova.com']
        
        context = {
            'order': order,
            'items': order.items.all(),
        }
        
        html_content = render_to_string('emails/admin_new_order.html', context)
        text_content = f"""
        Nouvelle commande reçue !
        
        Commande #{order.id}
        Client: {order.full_name} ({order.email})
        Montant total: {order.total / 100}€
        
        Articles:
        """
        
        for item in order.items.all():
            text_content += f"\n- {item.book_title} x{item.quantity}"
        
        text_content += f"""
        
        Adresse de livraison:
        {order.full_address}
        
        Consultez le backoffice pour plus de détails.
        """
        
        email = EmailMultiAlternatives(
            subject=f'Nouvelle commande #{order.id}',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=admin_emails
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Mettre à jour le statut de la commande
        """
        order = self.get_object()
        old_status = order.status
        
        serializer = OrderUpdateStatusSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Si passage à "delivered", définir la date
        if serializer.validated_data.get('status') == 'delivered' and old_status != 'delivered':
            serializer.validated_data['delivered_at'] = timezone.now()
        
        order = serializer.save()
        
        # Envoyer un email si le statut change ou si un tracking est ajouté
        if old_status != order.status or ('tracking_number' in request.data and request.data['tracking_number']):
            try:
                self._send_status_update_email(order)
            except Exception as e:
                print(f"Erreur envoi email: {e}")
        
        return Response({
            'message': 'Statut mis à jour',
            'order': OrderDetailSerializer(order, context={'request': request}).data
        })
    
    def _send_status_update_email(self, order):
        """
        Envoyer un email de mise à jour du statut
        """
        if order.status == 'delivered':
            subject = f'Votre commande #{order.id} a été livrée'
            message = f"""
            Bonjour {order.full_name},
            
            Votre commande #{order.id} a été livrée !
            
            Nous espérons que vous êtes satisfait de votre achat.
            
            Merci pour votre confiance !
            L'équipe zoonova
            """
        elif order.tracking_number:
            subject = f'Votre commande #{order.id} a été expédiée'
            message = f"""
            Bonjour {order.full_name},
            
            Votre commande #{order.id} a été expédiée !
            
            Numéro de suivi: {order.tracking_number}
            
            Vous pouvez suivre votre colis en utilisant ce numéro.
            
            Merci pour votre confiance !
            L'équipe zoonova
            """
        else:
            return
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False,
        )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Statistiques des commandes (admin uniquement)
        """
        # Total des commandes
        total_orders = Order.objects.count()
        
        # Revenus totaux
        total_revenue = Order.objects.aggregate(
            total=Sum('total')
        )['total'] or 0
        
        # Commandes par statut
        orders_by_status = Order.objects.values('status').annotate(
            count=Count('id')
        )
        
        # Commandes du mois
        current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_orders = Order.objects.filter(
            created_at__gte=current_month
        ).count()
        
        monthly_revenue = Order.objects.filter(
            created_at__gte=current_month
        ).aggregate(total=Sum('total'))['total'] or 0
        
        return Response({
            'total_orders': total_orders,
            'total_revenue': total_revenue / 100,
            'orders_by_status': orders_by_status,
            'monthly_orders': monthly_orders,
            'monthly_revenue': monthly_revenue / 100,
        })
    
    @action(detail=True, methods=['get'])
    def invoice(self, request, pk=None):
        """
        Télécharger la facture PDF
        """
        order = self.get_object()
        invoice_pdf = generate_invoice_pdf(order)
        
        from django.http import HttpResponse
        response = HttpResponse(invoice_pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="facture_{order.id}.pdf"'
        return response