# ============================================
# 4. APP ORDERS - Commandes Simplifiées
# ============================================

from django.db import models
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

class Country(models.Model):
    """Pays de livraison"""
    
    name = models.CharField(max_length=255, verbose_name="Nom")
    code = models.CharField(max_length=2, unique=True, verbose_name="Code ISO")
    shipping_cost = models.PositiveIntegerField(
        default=0, 
        help_text="Frais de port en centimes",
        verbose_name="Frais de port"
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        db_table = 'countries'
        ordering = ['name']
        verbose_name = 'Pays'
        verbose_name_plural = 'Pays'
    
    def __str__(self):
        return self.name
    
    @property
    def shipping_cost_euros(self):
        return self.shipping_cost / 100


class Order(models.Model):
    """Commande client (sans authentification)"""
    
    STATUS_CHOICES = [
        ('pending', 'En attente de livraison'),
        ('delivered', 'Livrée'),
    ]
    
    # Informations client (pas de User lié)
    email = models.EmailField(
        validators=[EmailValidator()],
        verbose_name="Email"
    )
    first_name = models.CharField(max_length=255, verbose_name="Prénom")
    last_name = models.CharField(max_length=255, verbose_name="Nom")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    
    # Adresse de livraison
    voie = models.CharField(max_length=255, verbose_name="Rue")
    numero_voie = models.CharField(max_length=20, verbose_name="Numéro")
    complement_adresse = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name="Complément d'adresse"
    )
    code_postal = models.CharField(max_length=20, verbose_name="Code postal")
    ville = models.CharField(max_length=255, verbose_name="Ville")
    country = models.ForeignKey(
        Country, 
        on_delete=models.PROTECT,
        verbose_name="Pays"
    )
    
    # Paiement Stripe uniquement
    stripe_payment_intent_id = models.CharField(
        max_length=255, 
        null=True,
        blank=True,
        unique=True,
        verbose_name="Stripe Payment Intent ID"
    )
    stripe_checkout_session_id = models.CharField(
        max_length=255, 
        null=True,
        blank=True,
        verbose_name="Stripe Checkout Session ID"
    )
    
    # Montants en centimes
    subtotal = models.PositiveIntegerField(default=0, verbose_name="Sous-total")
    shipping_cost = models.PositiveIntegerField(default=0, verbose_name="Frais de port")
    total = models.PositiveIntegerField(default=0, verbose_name="Total")
    
    # Statut simplifié
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending', 
        db_index=True,
        verbose_name="Statut"
    )
    
    # Informations de livraison
    tracking_number = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name="Numéro de suivi"
    )
    delivered_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Livré le"
    )
    
    # Notes admin
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
    
    def __str__(self):
        return f"Commande #{self.id} - {self.email}"
    
    @property
    def total_euros(self):
        return self.total / 100
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_address(self):
        address = f"{self.numero_voie} {self.voie}"
        if self.complement_adresse:
            address += f", {self.complement_adresse}"
        address += f", {self.code_postal} {self.ville}, {self.country.name}"
        return address


class OrderItem(models.Model):
    """Article d'une commande"""
    
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name="Commande"
    )
    
    book = models.ForeignKey(
        'books.Book', 
        on_delete=models.PROTECT, 
        related_name='order_items',
        verbose_name="Livre"
    )
    
    # Snapshot des informations au moment de la commande
    book_title = models.CharField(max_length=255, verbose_name="Titre du livre")
    unit_price = models.PositiveIntegerField(verbose_name="Prix unitaire")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantité")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'Article de commande'
        verbose_name_plural = 'Articles de commandes'
    
    def __str__(self):
        return f"{self.quantity}x {self.book_title}"
    
    def clean(self):
        """Valide que un livre est sélectionné et que la quantité est > 0"""
        if not self.book:
            raise ValidationError("Vous devez sélectionner un livre.")
        if self.quantity <= 0:
            raise ValidationError("La quantité doit être supérieure à 0.")
    
    def save(self, *args, **kwargs):
        """Remplir automatiquement les infos du livre avant de sauvegarder"""
        if self.book:
            self.book_title = self.book.titre
            if not self.unit_price:
                self.unit_price = self.book.prix
        super().save(*args, **kwargs)
    
    @property
    def subtotal(self):
        return self.unit_price * self.quantity
    
    @property
    def subtotal_euros(self):
        return self.subtotal / 100

