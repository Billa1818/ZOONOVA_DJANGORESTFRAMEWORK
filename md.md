# ============================================
# 1. APP ACCOUNTS - Gestion Admin Uniquement
# ============================================

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone

class AdminManager(BaseUserManager):
    """Manager pour les comptes administrateurs"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email requis')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class Admin(AbstractBaseUser, PermissionsMixin):
    """Compte administrateur uniquement - Pas de compte client"""
    
    email = models.EmailField(unique=True, db_index=True, verbose_name="Email")
    first_name = models.CharField(max_length=150, blank=True, verbose_name="Prénom")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Nom")
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="Date d'inscription")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="Dernière connexion")
    
    objects = AdminManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'admins'
        verbose_name = 'Administrateur'
        verbose_name_plural = 'Administrateurs'
    
    def __str__(self):
        return self.email


# ============================================
# 2. APP BOOKS - Catalogue Livres Complet
# ============================================

from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator

class Book(models.Model):
    """Livre du catalogue avec toutes les informations détaillées"""
    
    # Informations de base
    titre = models.CharField(max_length=255, db_index=True, verbose_name="Titre")
    nom = models.CharField(max_length=255, verbose_name="Nom/Auteur")
    description = models.TextField(verbose_name="Description")
    legende = models.CharField(max_length=500, blank=True, verbose_name="Légende/Sous-titre")
    
    # Prix en centimes (ex: 2500 = 25.00€)
    prix = models.PositiveIntegerField(
        help_text="Prix en centimes (ex: 2500 = 25€)",
        validators=[MinValueValidator(0)],
        verbose_name="Prix"
    )
    
    # Caractéristiques physiques du livre
    code_bare = models.CharField(
        max_length=13, 
        unique=True, 
        null=True, 
        blank=True,
        verbose_name="Code-barres ISBN"
    )
    nombre_pages = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre de pages"
    )
    largeur_cm = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Largeur (cm)"
    )
    hauteur_cm = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Hauteur (cm)"
    )
    epaisseur_cm = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Épaisseur (cm)"
    )
    poids_grammes = models.PositiveIntegerField(
        null=True, 
        blank=True,
        verbose_name="Poids (grammes)"
    )
    
    # Informations éditoriales
    date_publication = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Date de publication"
    )
    editeur = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name="Éditeur"
    )
    langue = models.CharField(
        max_length=50, 
        default='Français',
        verbose_name="Langue"
    )
    
    # Stock et disponibilité
    quantites = models.PositiveIntegerField(
        default=0, 
        help_text="Stock disponible",
        verbose_name="Quantité en stock"
    )
    
    # SEO et URL
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    seo_title = models.CharField(max_length=255, blank=True, verbose_name="Titre SEO")
    seo_description = models.CharField(max_length=500, blank=True, verbose_name="Description SEO")
    
    # Statistiques
    views_count = models.PositiveIntegerField(default=0, verbose_name="Vues")
    sales_count = models.PositiveIntegerField(default=0, verbose_name="Ventes")
    
    # Gestion
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    is_featured = models.BooleanField(default=False, verbose_name="Mise en avant")
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        db_table = 'books'
        ordering = ['-created_at']
        verbose_name = 'Livre'
        verbose_name_plural = 'Livres'
    
    def __str__(self):
        return self.titre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)
    
    @property
    def prix_euros(self):
        """Retourne le prix en euros"""
        return self.prix / 100
    
    @property
    def in_stock(self):
        """Vérifie si le livre est en stock"""
        return self.quantites > 0
    
    @property
    def dimensions(self):
        """Retourne les dimensions formatées"""
        if self.largeur_cm and self.hauteur_cm and self.epaisseur_cm:
            return f"{self.largeur_cm} × {self.hauteur_cm} × {self.epaisseur_cm} cm"
        return "Non renseignées"


# ============================================
# 3. APP MEDIA - Images du Livre
# ============================================

from django.db import models

def book_image_upload_path(instance, filename):
    """Chemin de stockage des images"""
    return f'books/{instance.book.slug}/images/{filename}'


class BookImage(models.Model):
    """Images d'un livre (couverture, pages, aperçus)"""
    
    IMAGE_TYPES = [
        ('cover_front', 'Couverture (1ère page)'),
        ('cover_back', 'Quatrième de couverture (dernière page)'),
        ('content', 'Aperçu contenu'),
        ('other', 'Autre'),
    ]
    
    book = models.ForeignKey(
        'books.Book', 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name="Livre"
    )
    
    image = models.ImageField(
        upload_to=book_image_upload_path,
        verbose_name="Image"
    )
    
    type = models.CharField(
        max_length=50, 
        choices=IMAGE_TYPES, 
        default='other',
        verbose_name="Type d'image"
    )
    
    is_main_cover = models.BooleanField(
        default=False,
        verbose_name="Image de couverture principale"
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )
    
    alt_text = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name="Texte alternatif"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        db_table = 'book_images'
        ordering = ['order', 'created_at']
        verbose_name = 'Image de livre'
        verbose_name_plural = 'Images de livres'
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.book.titre}"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'une seule image soit la couverture principale
        if self.is_main_cover:
            BookImage.objects.filter(
                book=self.book, 
                is_main_cover=True
            ).update(is_main_cover=False)
        super().save(*args, **kwargs)


class BookVideo(models.Model):
    """Vidéos associées à un livre"""
    
    book = models.ForeignKey(
        'books.Book', 
        on_delete=models.CASCADE, 
        related_name='videos',
        verbose_name="Livre"
    )
    
    video_url = models.URLField(
        max_length=500,
        verbose_name="URL de la vidéo"
    )
    
    title = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name="Titre"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        db_table = 'book_videos'
        ordering = ['order', 'created_at']
        verbose_name = 'Vidéo de livre'
        verbose_name_plural = 'Vidéos de livres'
    
    def __str__(self):
        return f"Vidéo - {self.book.titre}"


# ============================================
# 4. APP ORDERS - Commandes Simplifiées
# ============================================

from django.db import models
from django.core.validators import EmailValidator

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
        blank=True,
        unique=True,
        verbose_name="Stripe Payment Intent ID"
    )
    stripe_checkout_session_id = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name="Stripe Checkout Session ID"
    )
    
    # Montants en centimes
    subtotal = models.PositiveIntegerField(verbose_name="Sous-total")
    shipping_cost = models.PositiveIntegerField(default=0, verbose_name="Frais de port")
    total = models.PositiveIntegerField(verbose_name="Total")
    
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
    
    @property
    def subtotal(self):
        return self.unit_price * self.quantity
    
    @property
    def subtotal_euros(self):
        return self.subtotal / 100


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


# ============================================
# 6. APP CONTACT - Messages de Contact
# ============================================

from django.db import models

class ContactMessage(models.Model):
    """Message de contact du site"""
    
    first_name = models.CharField(max_length=255, verbose_name="Prénom")
    last_name = models.CharField(max_length=255, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    subject = models.CharField(max_length=255, blank=True, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    
    # Gestion admin
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    replied_at = models.DateTimeField(null=True, blank=True, verbose_name="Répondu le")
    admin_notes = models.TextField(blank=True, verbose_name="Notes admin")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        db_table = 'contact_messages'
        ordering = ['-created_at']
        verbose_name = 'Message de contact'
        verbose_name_plural = 'Messages de contact'
    
    def __str__(self):
        return f"Message de {self.email} - {self.subject or 'Sans sujet'}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"