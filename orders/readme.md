# 📦 API Commandes - Documentation

## Base URL
```
http://127.0.0.1:8000/api/v1/orders/
```

---

## 📚 Table des matières
1. [Endpoints Pays](#endpoints-pays)
2. [Endpoints Commandes](#endpoints-commandes)
3. [Actions Spéciales](#actions-spéciales)
4. [Permissions](#permissions)
5. [Statuts et Codes HTTP](#statuts-et-codes-http)
6. [Exemples cURL](#exemples-curl)

---

## 🌍 Endpoints Pays

### GET `/countries/`
**Lister tous les pays actifs**

Récupère la liste paginée de tous les pays de livraison actifs.

**Permissions:** Public (pas d'authentification requise)

**Query Parameters (optionnels):**
- `page` (integer): Numéro de page

**Réponse (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "France",
      "code": "FR",
      "shipping_cost": 500,
      "shipping_cost_euros": "5.00",
      "is_active": true
    },
    {
      "id": 2,
      "name": "Belgique",
      "code": "BE",
      "shipping_cost": 750,
      "shipping_cost_euros": "7.50",
      "is_active": true
    }
  ]
}
```

---

### GET `/countries/{id}/`
**Récupérer un pays**

Obtient les détails d'un pays spécifique.

**Permissions:** Public

**Réponse (200 OK):**
```json
{
  "id": 1,
  "name": "France",
  "code": "FR",
  "shipping_cost": 500,
  "shipping_cost_euros": "5.00",
  "is_active": true
}
```

---

## 📋 Endpoints Commandes

### GET `/`
**Lister les commandes**

Récupère la liste paginée de toutes les commandes.

**Permissions:** Authentifié (Token requis)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Query Parameters (optionnels):**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `page` | integer | Numéro de page |
| `status` | string | Filtrer par statut (`pending`, `delivered`) |
| `country` | integer | Filtrer par ID de pays |
| `start_date` | date | Date de début (format: YYYY-MM-DD) |
| `end_date` | date | Date de fin (format: YYYY-MM-DD) |
| `search` | string | Recherche dans email, prénom, nom, numéro de suivi |
| `ordering` | string | Tri: `-created_at` (défaut), `created_at`, `total`, `-total` |

**Exemples de requêtes:**
```
GET /?status=pending
GET /?country=1&ordering=-created_at
GET /?search=dupont
GET /?start_date=2025-01-01&end_date=2025-01-31
GET /?status=delivered&ordering=total
```

**Réponse (200 OK):**
```json
{
  "count": 25,
  "next": "http://127.0.0.1:8000/api/v1/orders/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "email": "client@example.com",
      "first_name": "Jean",
      "last_name": "Dupont",
      "full_name": "Jean Dupont",
      "phone": "+33612345678",
      "voie": "Rue de la Paix",
      "numero_voie": "10",
      "complement_adresse": "Appartement 5",
      "code_postal": "75001",
      "ville": "Paris",
      "country_id": 1,
      "country_name": "France",
      "full_address": "10 Rue de la Paix, Appartement 5, 75001 Paris, France",
      "subtotal": 2000,
      "subtotal_euros": "20.00",
      "shipping_cost": 500,
      "shipping_cost_euros": "5.00",
      "total": 2500,
      "total_euros": "25.00",
      "status": "pending",
      "status_display": "En attente de livraison",
      "items_count": 2,
      "tracking_number": "",
      "delivered_at": null,
      "notes": "",
      "created_at": "2025-11-29T10:30:00Z",
      "updated_at": "2025-11-29T10:30:00Z"
    }
  ]
}
```

---

### POST `/`
**Créer une commande**

Crée une nouvelle commande (publique, sans authentification).

**Permissions:** Public (pas d'authentification requise)

**Headers:**
```
Content-Type: application/json
```

**Payload:**
```json
{
  "email": "client@example.com",
  "first_name": "Jean",
  "last_name": "Dupont",
  "phone": "+33612345678",
  "voie": "Rue de la Paix",
  "numero_voie": "10",
  "complement_adresse": "Appartement 5",
  "code_postal": "75001",
  "ville": "Paris",
  "country": 1,
  "items": [
    {
      "book_id": 1,
      "quantity": 2
    },
    {
      "book_id": 3,
      "quantity": 1
    }
  ]
}
```

**Validations:**
- `email`: requis, format email valide
- `first_name`: requis, max 255 caractères
- `last_name`: requis, max 255 caractères
- `phone`: optionnel, max 20 caractères
- `voie`: requis
- `numero_voie`: requis
- `complement_adresse`: optionnel
- `code_postal`: requis
- `ville`: requis
- `country`: requis (ID du pays actif)
- `items`: requis (min 1 article)
  - Chaque article: `book_id` et `quantity` requis
  - Le stock doit être suffisant

**Réponse (201 CREATED):**
```json
{
  "message": "Commande créée avec succès",
  "order": {
    "id": 1,
    "email": "client@example.com",
    "first_name": "Jean",
    "last_name": "Dupont",
    "full_name": "Jean Dupont",
    "phone": "+33612345678",
    "voie": "Rue de la Paix",
    "numero_voie": "10",
    "complement_adresse": "Appartement 5",
    "code_postal": "75001",
    "ville": "Paris",
    "country_id": 1,
    "country_name": "France",
    "full_address": "10 Rue de la Paix, Appartement 5, 75001 Paris, France",
    "stripe_payment_intent_id": "",
    "stripe_checkout_session_id": "",
    "subtotal": 2000,
    "subtotal_euros": "20.00",
    "shipping_cost": 500,
    "shipping_cost_euros": "5.00",
    "total": 2500,
    "total_euros": "25.00",
    "status": "pending",
    "status_display": "En attente de livraison",
    "tracking_number": "",
    "delivered_at": null,
    "notes": "",
    "items": [
      {
        "id": 1,
        "order": 1,
        "book": 1,
        "book_title": "Python pour les débutants",
        "unit_price": 1000,
        "unit_price_euros": "10.00",
        "quantity": 2,
        "subtotal": 2000,
        "subtotal_euros": "20.00",
        "created_at": "2025-11-29T10:30:00Z",
        "updated_at": "2025-11-29T10:30:00Z"
      }
    ],
    "created_at": "2025-11-29T10:30:00Z",
    "updated_at": "2025-11-29T10:30:00Z"
  }
}
```

**Erreurs possibles:**

Erreur 400 - Stock insuffisant:
```json
{
  "items": ["Stock insuffisant pour Python pour les débutants"]
}
```

Erreur 400 - Livre inexistant:
```json
{
  "items": ["Livre 999 introuvable"]
}
```

**Actions automatiques:**
- ✉️ Email de confirmation envoyé au client avec facture PDF
- ✉️ Email de notification envoyé à l'admin
- 📊 Stock des livres décrémenté
- 📊 Compteur de ventes incrémenté

---

### GET `/{id}/`
**Récupérer une commande**

Obtient les détails complets d'une commande.

**Permissions:** Authentifié (Token requis)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Réponse (200 OK):**
Même format que POST `/` (création)

---

### PUT `/{id}/`
**Mettre à jour complètement une commande**

Met à jour l'ensemble des champs d'une commande.

**Permissions:** Authentifié (Token requis)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Payload:**
```json
{
  "email": "newemail@example.com",
  "first_name": "Jean",
  "last_name": "Dupont",
  "phone": "+33612345678",
  "voie": "Rue de la Paix",
  "numero_voie": "10",
  "complement_adresse": "Appartement 5",
  "code_postal": "75001",
  "ville": "Paris",
  "country": 1,
  "status": "pending",
  "tracking_number": "",
  "notes": "",
  "stripe_payment_intent_id": "",
  "stripe_checkout_session_id": ""
}
```

**Réponse (200 OK):**
Même format que GET `/{id}/`

---

### PATCH `/{id}/`
**Mettre à jour partiellement une commande**

Met à jour certains champs seulement.

**Permissions:** Authentifié (Token requis)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Payload (exemple):**
```json
{
  "notes": "Commande confirmée par téléphone",
  "phone": "+33712345678"
}
```

**Réponse (200 OK):**
Même format que GET `/{id}/`

---

### DELETE `/{id}/`
**Supprimer une commande**

Supprime complètement une commande.

**Permissions:** Authentifié (Token requis)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Réponse (204 NO CONTENT):** Pas de contenu

---

## 📊 Actions Spéciales

### GET `/statistics/`
**Obtenir les statistiques**

Récupère les statistiques globales des commandes.

**Permissions:** Authentifié (Token requis)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Réponse (200 OK):**
```json
{
  "total_orders": 150,
  "total_revenue": 15000.00,
  "orders_by_status": [
    {
      "status": "pending",
      "count": 45
    },
    {
      "status": "delivered",
      "count": 105
    }
  ],
  "monthly_orders": 23,
  "monthly_revenue": 2300.00
}
```

**Description des champs:**
- `total_orders`: Nombre total de commandes
- `total_revenue`: Revenus totaux en euros
- `orders_by_status`: Répartition par statut
- `monthly_orders`: Commandes du mois courant
- `monthly_revenue`: Revenus du mois courant en euros

---

### PATCH `/{id}/update_status/`
**Mettre à jour le statut de la commande**

Endpoint dédié pour mettre à jour le statut avec logique métier.

**Permissions:** Authentifié (Token requis)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Payload:**
```json
{
  "status": "delivered",
  "tracking_number": "FR123456789",
  "notes": "Livraison effectuée avec signature"
}
```

**Validations:**
- Pour passer à `delivered`, un `tracking_number` est requis

**Réponse (200 OK):**
```json
{
  "message": "Statut mis à jour",
  "order": {
    "id": 1,
    "email": "client@example.com",
    "full_name": "Jean Dupont",
    "status": "delivered",
    "status_display": "Livrée",
    "tracking_number": "FR123456789",
    "delivered_at": "2025-11-29T14:30:00Z",
    "notes": "Livraison effectuée avec signature",
    "total_euros": "25.00",
    ...
  }
}
```

**Erreur 400 - Tracking manquant pour livraison:**
```json
{
  "status": ["Un numéro de suivi est requis pour marquer comme livrée"]
}
```

**Actions automatiques:**
- 📅 `delivered_at` mis à jour si statut = "delivered"
- ✉️ Email au client avec numéro de suivi (si ajout)
- ✉️ Email de confirmation de livraison

---

### GET `/{id}/invoice/`
**Télécharger la facture PDF**

Génère et retourne la facture PDF d'une commande.

**Permissions:** Authentifié (Token requis)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="facture_{id}.pdf"`

**Contenu du PDF:**
- Numéro et date de la commande
- Informations client (nom, email)
- Adresse de livraison
- Articles commandés
- Sous-total, frais de port, total en euros
- Statut et numéro de suivi (si disponible)

---

## 🔐 Permissions

| Endpoint | Méthode | Permission | Détails |
|----------|---------|------------|---------|
| `/countries/` | GET | Public ✅ | Lister les pays |
| `/countries/{id}/` | GET | Public ✅ | Détails d'un pays |
| `/` | GET | Auth ✅ | Lister les commandes |
| `/` | POST | Public ✅ | Créer une commande |
| `/{id}/` | GET | Auth ✅ | Récupérer une commande |
| `/{id}/` | PUT | Auth ✅ | Mettre à jour complètement |
| `/{id}/` | PATCH | Auth ✅ | Mettre à jour partiellement |
| `/{id}/` | DELETE | Auth ✅ | Supprimer une commande |
| `/statistics/` | GET | Auth ✅ | Statistiques |
| `/{id}/update_status/` | PATCH | Auth ✅ | Mettre à jour le statut |
| `/{id}/invoice/` | GET | Auth ✅ | Télécharger la facture PDF |

---

## 📌 Statuts de Commande

| Code | Affichage | Description |
|------|-----------|-------------|
| `pending` | En attente de livraison | Commande confirmée, en traitement |
| `delivered` | Livrée | Commande livrée au client |

---

## 🔧 Codes de Statut HTTP

| Code | Description |
|------|-------------|
| 200 | Requête réussie |
| 201 | Commande créée |
| 204 | Suppression réussie |
| 400 | Validation échouée (données invalides) |
| 401 | Non authentifié (token manquant/invalide) |
| 403 | Authentifié mais permissions insuffisantes |
| 404 | Ressource non trouvée |
| 500 | Erreur serveur |

---

## 💡 Exemples cURL

### Lister les pays
```bash
curl -X GET http://127.0.0.1:8000/api/v1/orders/countries/ \
  -H "Content-Type: application/json"
```

### Créer une commande
```bash
curl -X POST http://127.0.0.1:8000/api/v1/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@example.com",
    "first_name": "Jean",
    "last_name": "Dupont",
    "phone": "+33612345678",
    "voie": "Rue de la Paix",
    "numero_voie": "10",
    "complement_adresse": "Appartement 5",
    "code_postal": "75001",
    "ville": "Paris",
    "country": 1,
    "items": [
      {
        "book_id": 1,
        "quantity": 2
      },
      {
        "book_id": 3,
        "quantity": 1
      }
    ]
  }'
```

### Lister les commandes en attente (authentifié)
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/orders/?status=pending&ordering=-created_at" \
  -H "Authorization: Bearer <access_token>"
```

### Lister les commandes livrées en France
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/orders/?status=delivered&country=1" \
  -H "Authorization: Bearer <access_token>"
```

### Rechercher par email
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/orders/?search=client@example.com" \
  -H "Authorization: Bearer <access_token>"
```

### Récupérer une commande
```bash
curl -X GET http://127.0.0.1:8000/api/v1/orders/1/ \
  -H "Authorization: Bearer <access_token>"
```

### Mettre à jour partiellement une commande
```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/orders/1/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Commande confirmée par téléphone",
    "phone": "+33712345678"
  }'
```

### Mettre à jour le statut avec numéro de suivi
```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/orders/1/update_status/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "delivered",
    "tracking_number": "FR123456789",
    "notes": "Livraison effectuée avec signature"
  }'
```

### Obtenir les statistiques
```bash
curl -X GET http://127.0.0.1:8000/api/v1/orders/statistics/ \
  -H "Authorization: Bearer <access_token>"
```

### Télécharger la facture PDF
```bash
curl -X GET http://127.0.0.1:8000/api/v1/orders/1/invoice/ \
  -H "Authorization: Bearer <access_token>" \
  -o facture_1.pdf
```

### Lister les commandes par plage de dates
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/orders/?start_date=2025-01-01&end_date=2025-01-31" \
  -H "Authorization: Bearer <access_token>"
```

---

## 📧 Notifications Email

### Email Client - Confirmation de Commande
- **Déclenché:** Création d'une commande
- **Destinataire:** Email du client
- **Contenu:** 
  - Récapitulatif de la commande
  - Détails des articles
  - Adresse de livraison
  - Facture PDF en pièce jointe

### Email Client - Expédition
- **Déclenché:** Ajout d'un numéro de suivi
- **Destinataire:** Email du client
- **Contenu:**
  - Numéro de suivi
  - Instructions de suivi

### Email Client - Livraison
- **Déclenché:** Passage du statut à "delivered"
- **Destinataire:** Email du client
- **Contenu:**
  - Confirmation de livraison
  - Remerciement

### Email Admin - Nouvelle Commande
- **Déclenché:** Création d'une commande
- **Destinataires:** Définis dans `settings.ADMIN_NOTIFICATION_EMAILS`
- **Contenu:**
  - Détails complets de la commande
  - Informations du client
  - Lien d'accès au backoffice

---

## 📝 Notes Importantes

1. **Montants en centimes:**
   - Tous les montants sont en **centimes** (ex: 2500 = 25,00€)
   - Les propriétés `*_euros` convertissent automatiquement

2. **Stock:**
   - Décrémenté automatiquement lors de la création
   - Vérification avant création
   - Incrémentation du compteur de ventes

3. **Adresse:**
   - La propriété `full_address` formate automatiquement
   - Format: `{numero_voie} {voie}, {complement_adresse}, {code_postal} {ville}, {country}`

4. **Facture PDF:**
   - Générée automatiquement à la création
   - Envoyée par email au client
   - Disponible au téléchargement

5. **Frais de Port:**
   - Définis au niveau du pays
   - Ajoutés automatiquement au total
   - Inclus dans `total_euros`

6. **Numéro de Suivi:**
   - Optionnel pour créer une commande
   - Requis pour passer au statut "delivered"
   - Utilisé pour notifier le client

7. **Dates:**
   - `created_at`: Automatique à la création
   - `delivered_at`: Défini au passage à "delivered"
   - `updated_at`: Automatique à chaque modification

---

## 🔄 Authentification

Pour les endpoints protégés, utilisez un token Bearer dans le header:

```
Authorization: Bearer <access_token>
```

Le token est obtenu via l'endpoint d'authentification `/api/v1/auth/`.
