# ============================================
# 4. APP ORDERS - Serializers Commandes
# ============================================

from rest_framework import serializers
from .models import Order, OrderItem, Country


class CountrySerializer(serializers.ModelSerializer):
    """Serializer pour pays"""
    
    shipping_cost_euros = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Country
        fields = [
            'id', 'name', 'code',
            'shipping_cost', 'shipping_cost_euros',
            'is_active'
        ]
        read_only_fields = ['id', 'shipping_cost_euros']


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer pour articles de commande"""
    
    subtotal_euros = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    book_slug = serializers.CharField(source='book.slug', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'book', 'book_slug',
            'book_title', 'unit_price', 'quantity',
            'subtotal', 'subtotal_euros',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'subtotal', 'subtotal_euros',
            'created_at', 'updated_at'
        ]


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer pour liste de commandes"""
    
    total_euros = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    full_name = serializers.CharField(read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    items_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = Order
        fields = [
            'id', 'email', 'full_name', 'first_name', 'last_name',
            'country_name', 'total', 'total_euros',
            'status', 'status_display', 'items_count',
            'tracking_number', 'created_at'
        ]
    
    def get_items_count(self, obj):
        """Nombre d'articles dans la commande"""
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour une commande"""
    
    total_euros = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    full_name = serializers.CharField(read_only=True)
    full_address = serializers.CharField(read_only=True)
    country = CountrySerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = Order
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'voie', 'numero_voie', 'complement_adresse',
            'code_postal', 'ville', 'country', 'full_address',
            'stripe_payment_intent_id', 'stripe_checkout_session_id',
            'subtotal', 'shipping_cost', 'total', 'total_euros',
            'status', 'status_display', 'tracking_number',
            'delivered_at', 'notes', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'full_name', 'full_address', 'total_euros',
            'created_at', 'updated_at'
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer pour création de commande"""
    
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    
    class Meta:
        model = Order
        fields = [
            'email', 'first_name', 'last_name', 'phone',
            'voie', 'numero_voie', 'complement_adresse',
            'code_postal', 'ville', 'country',
            'items'
        ]
    
    def validate_items(self, value):
        """Valide les articles de la commande"""
        if not value:
            raise serializers.ValidationError("La commande doit contenir au moins un article")
        
        from books.models import Book
        
        for item in value:
            if 'book_id' not in item or 'quantity' not in item:
                raise serializers.ValidationError(
                    "Chaque article doit avoir book_id et quantity"
                )
            
            try:
                book = Book.objects.get(id=item['book_id'])
                if item['quantity'] > book.quantites:
                    raise serializers.ValidationError(
                        f"Stock insuffisant pour {book.titre}"
                    )
            except Book.DoesNotExist:
                raise serializers.ValidationError(
                    f"Livre {item['book_id']} introuvable"
                )
        
        return value
    
    def create(self, validated_data):
        """Crée la commande avec ses articles"""
        from books.models import Book
        
        items_data = validated_data.pop('items')
        country = validated_data['country']
        
        # Calculer les montants
        subtotal = 0
        order_items = []
        
        for item_data in items_data:
            book = Book.objects.get(id=item_data['book_id'])
            quantity = item_data['quantity']
            unit_price = book.prix
            subtotal += unit_price * quantity
            
            order_items.append({
                'book': book,
                'book_title': book.titre,
                'unit_price': unit_price,
                'quantity': quantity
            })
        
        shipping_cost = country.shipping_cost
        total = subtotal + shipping_cost
        
        # Créer la commande
        order = Order.objects.create(
            **validated_data,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            total=total
        )
        
        # Créer les articles
        for item_data in order_items:
            OrderItem.objects.create(order=order, **item_data)
        
        # Décrémenter le stock
        for item_data in order_items:
            book = item_data['book']
            book.quantites -= item_data['quantity']
            book.sales_count += item_data['quantity']
            book.save()
        
        return order


class OrderUpdateStatusSerializer(serializers.ModelSerializer):
    """Serializer pour mise à jour du statut"""
    
    class Meta:
        model = Order
        fields = ['status', 'tracking_number', 'delivered_at', 'notes']
    
    def validate_status(self, value):
        """Valide le changement de statut"""
        return value
