# ============================================
# 5. APP PAYMENTS - Serializers Paiements
# ============================================

from rest_framework import serializers
from .models import StripePayment


class StripePaymentSerializer(serializers.ModelSerializer):
    """Serializer pour paiements Stripe"""
    
    amount_euros = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    order_email = serializers.EmailField(source='order.email', read_only=True)
    
    class Meta:
        model = StripePayment
        fields = [
            'id', 'order', 'order_id', 'order_email',
            'payment_intent_id', 'checkout_session_id',
            'amount', 'amount_euros', 'currency', 'status',
            'metadata', 'webhook_received', 'webhook_data',
            'webhook_received_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_id', 'order_email', 'amount_euros',
            'created_at', 'updated_at'
        ]


class StripeWebhookSerializer(serializers.Serializer):
    """Serializer pour validation des webhooks Stripe"""
    
    type = serializers.CharField()
    data = serializers.JSONField()
    
    def validate_type(self, value):
        """Valide le type d'événement"""
        valid_types = [
            'checkout.session.completed',
            'payment_intent.succeeded',
            'payment_intent.payment_failed'
        ]
        if value not in valid_types:
            raise serializers.ValidationError(f"Type d'événement non supporté: {value}")
        return value
