
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
        return f"{self.titre} - {self.nom} ({self.prix_euros:.2f}€) - Stock: {self.quantites}"
    
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

