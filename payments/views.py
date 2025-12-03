# payments/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives
import stripe
import json
import logging

logger = logging.getLogger(__name__)

from .models import StripePayment
from orders.models import Order
from .serializers import StripePaymentSerializer, StripeWebhookSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour consultation des paiements (admin uniquement)
    """
    queryset = StripePayment.objects.all()
    serializer_class = StripePaymentSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([AllowAny])
def create_checkout_session(request):
    """
    Créer une session Stripe Checkout pour une commande
    """
    try:
        order_id = request.data.get('order_id')
        
        if not order_id:
            return Response({
                'error': 'order_id requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({
                'error': 'Commande introuvable'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifier que la commande n'a pas déjà été payée
        if order.stripe_payment_intent_id:
            return Response({
                'error': 'Commande déjà payée'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Préparer les line items pour Stripe
        line_items = []
        for item in order.items.all():
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': item.book_title,
                    },
                    'unit_amount': item.unit_price,  # En centimes
                },
                'quantity': item.quantity,
            })
        
        # Ajouter les frais de port
        if order.shipping_cost > 0:
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': 'Frais de port',
                    },
                    'unit_amount': order.shipping_cost,
                },
                'quantity': 1,
            })
        
        # Créer la session Checkout
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=settings.STRIPE_SUCCESS_URL + f'?order_id={order.id}',
            cancel_url=settings.STRIPE_CANCEL_URL + f'?order_id={order.id}',
            customer_email=order.email,
            metadata={
                'order_id': order.id,
            },
            payment_intent_data={
                'metadata': {
                    'order_id': order.id,
                }
            }
        )
        
        # Sauvegarder la session ID
        order.stripe_checkout_session_id = checkout_session.id
        order.save()
        
        return Response({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id,
        }, status=status.HTTP_200_OK)
        
    except stripe.error.StripeError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Erreur lors de la création de la session',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_webhook(request):
    """
    Webhook Stripe pour gérer les événements de paiement
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Gérer les différents types d'événements
    if event['type'] == 'checkout.session.completed':
        handle_checkout_session_completed(event['data']['object'])
    
    elif event['type'] == 'payment_intent.succeeded':
        handle_payment_intent_succeeded(event['data']['object'])
    
    elif event['type'] == 'payment_intent.payment_failed':
        handle_payment_intent_failed(event['data']['object'])
    
    return HttpResponse(status=200)


def handle_checkout_session_completed(session):
    """
    Gérer la complétion d'une session checkout
    """
    order_id = session['metadata'].get('order_id')
    
    if not order_id:
        logger.warning("Pas d'order_id dans la session checkout")
        return
    
    try:
        order = Order.objects.get(id=order_id)
        
        # Mettre à jour la commande
        order.stripe_payment_intent_id = session['payment_intent']
        order.stripe_checkout_session_id = session['id']
        order.save()
        
        # Créer l'enregistrement du paiement
        StripePayment.objects.create(
            order=order,
            payment_intent_id=session['payment_intent'],
            checkout_session_id=session['id'],
            amount=session['amount_total'],
            currency=session['currency'],
            status='succeeded',
            metadata=session.get('metadata', {}),
            webhook_received=True,
            webhook_data=dict(session),
            webhook_received_at=timezone.now()
        )
        logger.info(f"StripePayment créé pour order {order_id}")
        
        # Envoyer la facture par email
        try:
            _send_invoice_email(order)
        except Exception as e:
            logger.error(f"Erreur envoi facture pour order {order_id}: {str(e)}", exc_info=True)
        
    except Order.DoesNotExist:
        logger.error(f"Commande {order_id} introuvable pour webhook")
    except Exception as e:
        logger.error(f"Erreur création StripePayment pour order {order_id}: {str(e)}", exc_info=True)


def handle_payment_intent_succeeded(payment_intent):
    """
    Gérer le succès d'un paiement
    """
    order_id = payment_intent['metadata'].get('order_id')
    
    if not order_id:
        logger.warning("Pas d'order_id dans le payment_intent")
        return
    
    try:
        order = Order.objects.get(id=order_id)
        
        # Mettre à jour ou créer le paiement
        payment, created = StripePayment.objects.get_or_create(
            payment_intent_id=payment_intent['id'],
            defaults={
                'order': order,
                'amount': payment_intent['amount'],
                'currency': payment_intent['currency'],
                'status': 'succeeded',
                'metadata': payment_intent.get('metadata', {}),
                'webhook_received': True,
                'webhook_data': dict(payment_intent),
                'webhook_received_at': timezone.now()
            }
        )
        
        if not created:
            payment.status = 'succeeded'
            payment.webhook_received = True
            payment.webhook_data = dict(payment_intent)
            payment.webhook_received_at = timezone.now()
            payment.save()
        
        logger.info(f"Payment intent {payment_intent['id']} traité pour order {order_id}")
        
    except Order.DoesNotExist:
        logger.error(f"Commande {order_id} introuvable pour webhook")
    except Exception as e:
        logger.error(f"Erreur traitement payment_intent pour order {order_id}: {str(e)}", exc_info=True)


def _send_invoice_email(order):
    """
    Envoyer la facture PDF par email
    """
    from orders.utils import generate_invoice_pdf
    
    invoice_pdf = generate_invoice_pdf(order)
    
    email = EmailMultiAlternatives(
        subject=f'Facture de votre commande #{order.id}',
        body=f'Veuillez trouver ci-joint la facture de votre commande #{order.id}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email]
    )
    
    email.attach(f'facture_{order.id}.pdf', invoice_pdf, 'application/pdf')
    email.send(fail_silently=False)
    
    logger.info(f"Facture envoyée par email pour order {order.id}")


def handle_payment_intent_failed(payment_intent):
    """
    Gérer l'échec d'un paiement
    """
    order_id = payment_intent['metadata'].get('order_id')
    
    if not order_id:
        return
    
    try:
        order = Order.objects.get(id=order_id)
        
        # Créer ou mettre à jour le paiement
        payment, created = StripePayment.objects.get_or_create(
            payment_intent_id=payment_intent['id'],
            defaults={
                'order': order,
                'amount': payment_intent['amount'],
                'currency': payment_intent['currency'],
                'status': 'failed',
                'metadata': payment_intent.get('metadata', {}),
                'webhook_received': True,
                'webhook_data': dict(payment_intent),
                'webhook_received_at': timezone.now()
            }
        )
        
        if not created:
            payment.status = 'failed'
            payment.webhook_received = True
            payment.webhook_data = dict(payment_intent)
            payment.webhook_received_at = timezone.now()
            payment.save()
        
        # TODO: Notifier l'admin et le client
        
    except Order.DoesNotExist:
        print(f"Commande {order_id} introuvable pour webhook")


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_payment(request):
    """
    Vérifier le statut d'un paiement
    """
    order_id = request.query_params.get('order_id')
    
    if not order_id:
        return Response({
            'error': 'order_id requis'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        order = Order.objects.get(id=order_id)
        
        if not order.stripe_payment_intent_id:
            return Response({
                'paid': False,
                'message': 'Paiement non initié'
            })
        
        # Vérifier auprès de Stripe
        payment_intent = stripe.PaymentIntent.retrieve(order.stripe_payment_intent_id)
        
        is_paid = payment_intent.status == 'succeeded'
        
        return Response({
            'paid': is_paid,
            'status': payment_intent.status,
            'order': {
                'id': order.id,
                'email': order.email,
                'total': order.total / 100,
            }
        })
        
    except Order.DoesNotExist:
        return Response({
            'error': 'Commande introuvable'
        }, status=status.HTTP_404_NOT_FOUND)
    except stripe.error.StripeError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)