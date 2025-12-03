# ============================================
# 3. APP MEDIA - Images du Livre
# ============================================

from django.db import models

def book_image_upload_path(instance, filename):
    """Chemin de stockage des images"""
    return f'books/{instance.book.slug}/images/{filename}'

def book_video_upload_path(instance, filename):
    """Chemin de stockage des vidéos"""
    return f'books/{instance.book.slug}/videos/{filename}'


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
    
    video_file = models.FileField(
        upload_to=book_video_upload_path,
        verbose_name="Fichier vidéo",
        blank=True,
        null=True
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

