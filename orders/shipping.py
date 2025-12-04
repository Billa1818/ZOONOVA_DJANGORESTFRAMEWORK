# ============================================
# ORDERS - Calcul des frais de port
# ============================================

# Tarifs de port par nombre de livres (en euros)
FRANCE_SHIPPING_RATES = {
    1: 4.71,
    2: 4.71,
    3: 6.77,
    4: 5.13,
    5: 8.94,
    6: 8.40,
    7: 8.42,
    8: 8.42,
}

EUROPE_SHIPPING_RATES = {
    1: 10.48,
    2: 10.48,
    3: 15.24,
    4: 15.24,
    5: 28.62,
    6: 28.62,
    7: 28.62,
    8: 28.62,
}


def calculate_shipping_cost(country_name, book_count):
    """
    Calcule les frais de port basés sur le pays et le nombre de livres.
    
    Args:
        country_name (str): "France" ou "Europe"
        book_count (int): Nombre total de livres commandés
    
    Returns:
        int: Frais de port en centimes
    """
    
    if country_name == "France":
        # Pour 8+ livres, utiliser le tarif de 8
        quantity = min(book_count, 8) if book_count >= 8 else book_count
        rate = FRANCE_SHIPPING_RATES.get(quantity, FRANCE_SHIPPING_RATES[8])
        return int(rate * 100)  # Convertir en centimes
    
    elif country_name == "Europe":
        # Pour 8+ livres, utiliser le tarif de 8
        quantity = min(book_count, 8) if book_count >= 8 else book_count
        rate = EUROPE_SHIPPING_RATES.get(quantity, EUROPE_SHIPPING_RATES[8])
        return int(rate * 100)  # Convertir en centimes
    
    else:
        # Pays non supporté
        return 0


def count_total_books(order_items):
    """
    Compte le nombre total de livres dans la commande.
    
    Args:
        order_items (list): Liste des items avec leurs quantités
        
    Returns:
        int: Nombre total de livres
    """
    return sum(item['quantity'] for item in order_items)
