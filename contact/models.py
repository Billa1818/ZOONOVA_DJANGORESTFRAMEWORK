


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