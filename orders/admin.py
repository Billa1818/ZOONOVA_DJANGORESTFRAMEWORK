# orders/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Sum
from django.core.exceptions import ValidationError
from .models import Order, OrderItem, Country

# --- INLINE : Articles de la commande ---
class OrderItemInline(admin.TabularInline):
    """Affiche les articles (livres) liés à une commande spécifique."""
    model = OrderItem
    extra = 1  # Affiche 1 ligne vide pour ajouter un nouvel article
    
    # Champs affichés dans l'inline
    fields = (
        'book', 
        'quantity', 
        'unit_price', 
        'display_subtotal_euros' # Total de la ligne
    )
    
    # Champs éditables (pas de raw_id_fields, utilise un dropdown)
    readonly_fields = ('book_title', 'unit_price', 'display_subtotal_euros')
    
    # Permissions
    can_delete = True  # Permet de supprimer des articles
    
    def has_add_permission(self, request, obj=None):
        """Permet d'ajouter des articles à la commande"""
        return True
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Limite les livres sélectionnables aux livres existants uniquement.
        Affiche le titre et le prix du livre dans le dropdown.
        """
        if db_field.name == 'book':
            # Ne montre que les livres actifs/disponibles
            Book = db_field.related_model
            kwargs['queryset'] = Book.objects.filter(is_active=True)
            
            # Affiche le titre, auteur et prix dans le dropdown
            kwargs['to_field_name'] = 'id'
        
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        
        if db_field.name == 'book':
            # Désactive tous les boutons d'ajout/modification
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
        
        return field
    
    @admin.display(description="Total Ligne (€)")
    def display_subtotal_euros(self, obj):
        if obj.pk:  # Vérifier que l'objet existe en base
            return f"{obj.subtotal_euros:.2f} €"
        return "0.00 €"
    
    @admin.display(description="Détails du Livre")
    def book_info(self, obj):
        """Affiche les informations du livre sélectionné"""
        if obj.book:
            return format_html(
                '<strong>{}</strong><br>'
                '<small>Auteur: {}</small><br>'
                '<small>Prix: {:.2f}€ | Stock: {}</small>',
                obj.book.titre,
                obj.book.nom,
                obj.book.prix / 100,
                obj.book.quantites
            )
        return "Aucun livre sélectionné"
    
    def has_add_permission(self, request, obj=None):
        return True  # Permet d'ajouter des articles
    
    def save_model(self, request, obj, form, change):
        """Valide et sauvegarde l'article de commande"""
        # Ne sauvegarder que si un livre est sélectionné
        if not obj.book:
            return  # Ignorer les lignes vides
        
        # Appeler clean() pour valider avant de sauvegarder
        try:
            obj.full_clean()
        except ValidationError:
            # Si validation échoue, on ignore l'article vide
            return
        
        super().save_model(request, obj, form, change)


# --- ADMIN : Modèle de Commande (Order) ---
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # 1. Colonnes affichées dans la liste
    list_display = (
        'id', 
        'full_name', 
        'email', 
        'display_total_euros', 
        'status', 
        'tracking_number', 
        'created_at'
    )
    
    list_display_links = ('id', 'full_name')
    
    # 2. Filtres
    list_filter = ('status', 'country', 'created_at')
    
    # 3. Barre de recherche (Nom, Email, Tracking)
    search_fields = (
        'first_name', 
        'last_name', 
        'email', 
        'code_postal', 
        'ville', 
        'tracking_number'
    )
    
    # 4. Inlines (Articles)
    # NOTE: Les inlines (articles) ne s'affichent QUE pour les commandes EXISTANTES
    # Ils sont DÉSACTIVÉS lors de la création d'une nouvelle commande
    inlines = [
        OrderItemInline,
    ]
    
    def get_inlines(self, request, obj):
        """
        Affiche les inlines (articles) SEULEMENT pour les commandes existantes.
        Désactive complètement lors de l'ajout d'une nouvelle commande.
        """
        if obj is None:  # Création de nouvelle commande (obj est None)
            return []
        return super().get_inlines(request, obj)  # Retour à la normale pour edit

    def get_readonly_fields(self, request, obj):
        """Rend country éditable seulement lors de l'ajout, sinon en lecture seule"""
        readonly = list(super().get_readonly_fields(request, obj))
        if obj is not None:  # Édition d'une commande existante
            readonly.append('country')
        return readonly

    # 5. Organisation du formulaire d'édition
    fieldsets = (
        ('⭐ OBLIGATOIRES', {
            'fields': (
                ('email', 'country'),
                ('first_name', 'last_name', 'phone'), 
            ),
            'description': format_html(
                '<p style="color:red; font-weight:bold;">⚠️ Tous ces champs sont OBLIGATOIRES !</p>'
            )
        }),
        ('Adresse de Livraison', {
            'fields': (
                ('numero_voie', 'voie'), 
                'complement_adresse',
                ('code_postal', 'ville'),
                'full_address_hint',
            )
        }),
        ('Informations Générales', {
            'fields': (
                ('status', 'tracking_number', 'delivered_at'),
                'notes',
                'created_at', 
                'updated_at'
            )
        }),
        ('Détails Financiers & Paiement', {
            'fields': (
                ('subtotal', 'shipping_cost', 'total'), 
                'stripe_payment_intent_id', 
                'stripe_checkout_session_id'
            ),
            'classes': ('collapse',),
        }),
    )

    # 6. Champs en lecture seule
    readonly_fields = [
        'first_name', 'last_name', 'email', 'phone', 
        'voie', 'numero_voie', 'complement_adresse', 
        'code_postal', 'ville',
        'subtotal', 'shipping_cost', 'total', 
        'stripe_payment_intent_id', 'stripe_checkout_session_id',
        'created_at', 'updated_at',
        'full_address_hint', # Custom field
    ]
    
    # 7. Actions de masse
    actions = ['mark_as_delivered']
    
    # 8. Organisation des onglets (si Django 3.2+)
    # (optionnel, pour une meilleure UX)

    # --- Méthodes Personnalisées ---
    
    def save_model(self, request, obj, form, change):
        """Sauvegarde la commande et recalcule les totaux si nécessaire"""
        super().save_model(request, obj, form, change)
        # Les totaux seront recalculés automatiquement si nécessaire
    
    def save_formset(self, request, form, formset, change):
        """Sauvegarde les articles et recalcule le total de la commande"""
        formset.save()
        
        # Recalculer le total si des articles ont été modifiés
        order = form.instance
        if order.pk:
            order.subtotal = order.items.aggregate(total=Sum('unit_price'))['total'] or 0
            # Recalculer à partir des articles
            total_items = sum(item.unit_price * item.quantity for item in order.items.all())
            order.subtotal = total_items
            order.total = order.subtotal + order.shipping_cost
            order.save()

    @admin.display(description="Total (€)")
    def display_total_euros(self, obj):
        """Affiche le total formaté en Euros dans la liste"""
        return f"{obj.total_euros:.2f} €"

    @admin.display(description="Adresse Complète")
    def full_address_hint(self, obj):
        """Affiche l'adresse complète pour vérification rapide sur la fiche d'édition"""
        if not obj.pk or not hasattr(obj, 'country') or not obj.country:
            return "Sélectionnez d'abord un pays"
        return format_html(
            '<strong>{}</strong>', 
            obj.full_address.replace(', ', '<br>')
        )

    # --- Actions personnalisées ---

    @admin.action(description='Marquer les commandes sélectionnées comme Livrées')
    def mark_as_delivered(self, request, queryset):
        # Filtre uniquement les commandes en attente
        updated_count = queryset.filter(status='pending').update(
            status='delivered', 
            delivered_at=timezone.now()
        )
        self.message_user(
            request, 
            f"{updated_count} commandes ont été marquées comme Livrées."
        )


# --- ADMIN : Modèle Pays (Country) ---
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    # 1. Colonnes
    list_display = (
        'name', 
        'code', 
        'display_shipping_cost_euros', 
        'is_active'
    )
    
    list_display_links = ('name', 'code')
    
    # 2. Filtres
    list_filter = ('is_active',)
    
    # 3. Barre de recherche
    search_fields = ('name', 'code')
    
    # 4. Champs affichés
    fields = ('name', 'code', 'shipping_cost', 'is_active', 'shipping_cost_hint')
    
    # 5. Lecture seule
    readonly_fields = ('shipping_cost_hint',)

    # --- Méthodes Personnalisées ---
    @admin.display(description="Frais de port (€)")
    def display_shipping_cost_euros(self, obj):
        """Affiche les frais de port formatés en Euros dans la liste"""
        return f"{obj.shipping_cost_euros:.2f} €"

    @admin.display(description="Aperçu frais de port")
    def shipping_cost_hint(self, obj):
        """Affiche le coût en euros à côté du champ en centimes dans le formulaire"""
        return f"Soit {obj.shipping_cost_euros:.2f} €"