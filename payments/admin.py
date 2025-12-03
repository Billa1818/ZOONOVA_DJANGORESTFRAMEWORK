# payments/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import StripePayment

@admin.register(StripePayment)
class StripePaymentAdmin(admin.ModelAdmin):
    # 1. Colonnes affichées dans la liste
    list_display = (
        'payment_intent_id',
        'order',
        'display_amount_euros', # Montant formaté
        'status',
        'webhook_received',
        'created_at',
    )

    list_display_links = ('payment_intent_id',)

    # 2. Filtres (très utiles pour le débogage et l'audit)
    list_filter = ('status', 'webhook_received', 'currency', 'created_at')

    # 3. Barre de recherche (utile pour trouver une transaction spécifique)
    search_fields = (
        'payment_intent_id',
        'checkout_session_id',
        'order__id',
        'order__email'
    )

    # 4. Organisation du formulaire d'édition
    fieldsets = (
        ('Informations Clés de la Transaction', {
            'fields': (
                'order',
                ('payment_intent_id', 'checkout_session_id'),
                ('amount', 'display_amount_hint', 'currency'),
                'status',
                'created_at',
            )
        }),
        ('Données Techniques (Stripe & Webhook)', {
            'fields': (
                'metadata',
                ('webhook_received', 'webhook_received_at'),
                'webhook_data',
                'updated_at',
            ),
            'classes': ('collapse',), # Masque ces données techniques par défaut
        }),
    )

    # 5. Champs en lecture seule (CRUCIAL pour l'intégrité financière)
    # L'administrateur ne devrait jamais modifier manuellement une transaction confirmée.
    readonly_fields = [
        'order', 
        'payment_intent_id', 
        'checkout_session_id', 
        'amount', 
        'currency', 
        'status',
        'metadata', 
        'webhook_received', 
        'webhook_received_at', 
        'webhook_data',
        'created_at', 
        'updated_at',
        'display_amount_hint',
    ]

    # --- Méthodes Personnalisées ---

    @admin.display(description="Montant (€)")
    def display_amount_euros(self, obj):
        """Affiche le montant formaté en Euros dans la liste et dans le formulaire."""
        return f"{obj.amount_euros:.2f} €"

    @admin.display(description="Aperçu montant")
    def display_amount_hint(self, obj):
        """Aide visuelle dans le formulaire."""
        return f"Soit {obj.amount_euros:.2f} {obj.currency}"