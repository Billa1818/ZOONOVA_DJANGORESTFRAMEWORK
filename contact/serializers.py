# ============================================
# 6. APP CONTACT - Serializers Contact
# ============================================

from rest_framework import serializers
from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):
    """Serializer pour messages de contact"""
    
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'first_name', 'last_name', 'full_name',
            'email', 'subject', 'message',
            'is_read', 'replied_at', 'admin_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'full_name', 'is_read', 'replied_at',
            'admin_notes', 'created_at', 'updated_at'
        ]


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer pour création de message"""
    
    class Meta:
        model = ContactMessage
        fields = [
            'first_name', 'last_name', 'email',
            'subject', 'message'
        ]
    
    def validate_message(self, value):
        """Valide que le message a au moins 10 caractères"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Le message doit contenir au moins 10 caractères"
            )
        return value


class ContactMessageAdminSerializer(serializers.ModelSerializer):
    """Serializer admin pour gestion des messages"""
    
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'first_name', 'last_name', 'full_name',
            'email', 'subject', 'message',
            'is_read', 'replied_at', 'admin_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'full_name', 'created_at', 'updated_at']