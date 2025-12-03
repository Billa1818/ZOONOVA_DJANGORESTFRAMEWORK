
# ============================================
# 5. APP PAYMENTS - Paiements Stripe
# ============================================

from django.db import models

class StripePayment(models.Model):
    """Historique des paiements Stripe"""
    
    order = models.ForeignKey(
        'orders.Order', 
        on_delete=models.CASCADE, 
        related_name='stripe_payments',
        verbose_name="Commande"
    )
    
    payment_intent_id = models.CharField(
        max_length=255, 
        unique=True,
        verbose_name="Payment Intent ID"
    )
    
    checkout_session_id = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name="Checkout Session ID"
    )
    
    amount = models.PositiveIntegerField(verbose_name="Montant")
    currency = models.CharField(max_length=3, default='EUR', verbose_name="Devise")
    
    status = models.CharField(max_length=50, verbose_name="Statut")
    
    # Métadonnées Stripe
    metadata = models.JSONField(default=dict, blank=True)
    
    # Webhook
    webhook_received = models.BooleanField(default=False, verbose_name="Webhook reçu")
    webhook_data = models.JSONField(default=dict, blank=True)
    webhook_received_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        db_table = 'stripe_payments'
        ordering = ['-created_at']
        verbose_name = 'Paiement Stripe'
        verbose_name_plural = 'Paiements Stripe'
    
    def __str__(self):
        return f"Paiement {self.payment_intent_id} - {self.amount/100}€"
    
    @property
    def amount_euros(self):
        return self.amount / 100

