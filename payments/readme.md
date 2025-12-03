# 💳 API Paiements Stripe - Documentation Complète

## Base URL
```
http://127.0.0.1:8000/api/v1/payments/
```

---

## 💰 Endpoints Paiements

### 1. Créer une Session Checkout
**POST** `/create-checkout/`

Crée une session Stripe Checkout pour une commande. Cette session contient tous les articles de la commande et les frais de port.

**Permissions:** Public (pas d'authentification requise)

**Headers:**
```
Content-Type: application/json
```

**Payload:**
```json
{
  "order_id": 1
}
```

**Validations:**
- `order_id`: requis, doit être un entier
- La commande doit exister
- La commande ne doit pas avoir déjà un paiement effectué

**Réponse (200 OK):**
```json
{
  "checkout_url": "https://checkout.stripe.com/pay/cs_test_a1b2c3d4e5f6g7h8i9j0...",
  "session_id": "cs_test_a1b2c3d4e5f6g7h8i9j0"
}
```

**Erreur - order_id manquant (400):**
```json
{
  "error": "order_id requis"
}
```

**Erreur - Commande introuvable (404):**
```json
{
  "error": "Commande introuvable"
}
```

**Erreur - Commande déjà payée (400):**
```json
{
  "error": "Commande déjà payée"
}
```

**Erreur - Erreur Stripe (400):**
```json
{
  "error": "Message d'erreur Stripe détaillé"
}
```

**Erreur - Erreur serveur (500):**
```json
{
  "error": "Erreur lors de la création de la session",
  "details": "Description de l'erreur"
}
```

**Actions automatiques:**
- 📌 Enregistrement du `stripe_checkout_session_id` dans la commande
- 🔗 URLs de succès/annulation générées avec `order_id` en paramètre
- 📧 Email du client transmis à Stripe
- 📝 Métadonnées incluent l'`order_id`

**Notes:**
- Tous les articles de la commande sont inclus
- Les frais de port sont ajoutés comme un article séparé
- Le montant total doit correspondre au total de la commande

---

### 2. Webhook Stripe
**POST** `/webhook/`

Reçoit et traite les événements webhooks envoyés par Stripe. Ce endpoint est sécurisé par vérification de signature Stripe.

**Permissions:** Public (sécurisé par signature)

**Headers:**
```
Stripe-Signature: <signature_générée_par_stripe>
Content-Type: application/json
```

**Payload:** Événement JSON envoyé par Stripe

**Événements Gérés:**

#### `checkout.session.completed`
Déclenché quand une session checkout est complétée avec succès.

**Actions:**
- Met à jour `stripe_payment_intent_id` et `stripe_checkout_session_id` de la commande
- Crée un enregistrement `StripePayment` avec status "succeeded"
- Enregistre les données complètes du webhook

#### `payment_intent.succeeded`
Déclenché quand un paiement réussit.

**Actions:**
- Crée ou met à jour l'enregistrement `StripePayment`
- Marque le statut comme "succeeded"
- Enregistre les métadonnées et données du webhook

#### `payment_intent.payment_failed`
Déclenché quand un paiement échoue.

**Actions:**
- Crée ou met à jour l'enregistrement `StripePayment`
- Marque le statut comme "failed"
- Enregistre les données d'erreur du webhook

**Réponse (200 OK):** Pas de contenu (HTTP 200)

**Erreur (400):**
- Payload invalide ou signature incorrecte
- Type d'événement non supporté

**Notes:**
- Endpoint exempt de protection CSRF car Stripe ne peut pas fournir de token CSRF
- Signature vérifiée avec `STRIPE_WEBHOOK_SECRET`
- Les métadonnées doivent contenir `order_id` pour lier le paiement à la commande
- Les événements non gérés sont ignorés silencieusement

---

### 3. Vérifier le Statut d'un Paiement
**GET** `/verify/`

Vérifie le statut d'un paiement en interrogeant directement l'API Stripe.

**Permissions:** Public (pas d'authentification requise)

**Headers:**
```
Content-Type: application/json
```

**Query Parameters:**
| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `order_id` | integer | ✅ | ID de la commande |

**Exemple:**
```
GET /verify/?order_id=1
```

**Réponse (200 OK) - Paiement effectué:**
```json
{
  "paid": true,
  "status": "succeeded",
  "order": {
    "id": 1,
    "email": "client@example.com",
    "total": 25.00
  }
}
```

**Réponse (200 OK) - Paiement non initié:**
```json
{
  "paid": false,
  "message": "Paiement non initié"
}
```

**Réponse (200 OK) - Paiement échoué ou en attente:**
```json
{
  "paid": false,
  "status": "failed",
  "order": {
    "id": 1,
    "email": "client@example.com",
    "total": 25.00
  }
}
```

**Erreur - order_id manquant (400):**
```json
{
  "error": "order_id requis"
}
```

**Erreur - Commande introuvable (404):**
```json
{
  "error": "Commande introuvable"
}
```

**Erreur - Erreur Stripe (400):**
```json
{
  "error": "Message d'erreur Stripe"
}
```

**Notes:**
- Interroge directement l'API Stripe pour obtenir le statut le plus récent
- Montant retourné en euros (division par 100)
- Utile pour vérifier l'état après redirection depuis Stripe
- Statut peut être: `succeeded`, `failed`, `processing`, `requires_payment_method`, `canceled`

---

## 📊 Endpoints Administration

### 4. Lister les Paiements
**GET** `/stripe/`

Récupère la liste paginée de tous les paiements Stripe enregistrés.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Query Parameters (optionnels):**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `page` | integer | Numéro de page (défaut: 1) |
| `page_size` | integer | Taille de la page |

**Exemple:**
```
GET /stripe/?page=1&page_size=20
```

**Réponse (200 OK):**
```json
{
  "count": 50,
  "next": "http://127.0.0.1:8000/api/v1/payments/stripe/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "order": 1,
      "order_id": 1,
      "order_email": "client@example.com",
      "payment_intent_id": "pi_1234567890abcdef",
      "checkout_session_id": "cs_test_a1b2c3d4e5f6g7h8",
      "amount": 2500,
      "amount_euros": "25.00",
      "currency": "eur",
      "status": "succeeded",
      "metadata": {
        "order_id": 1
      },
      "webhook_received": true,
      "webhook_data": {
        "id": "cs_test_a1b2c3d4e5f6g7h8",
        "amount_total": 2500,
        "currency": "eur",
        "customer_email": "client@example.com",
        "payment_intent": "pi_1234567890abcdef",
        "status": "complete"
      },
      "webhook_received_at": "2025-11-29T10:30:00Z",
      "created_at": "2025-11-29T10:25:00Z",
      "updated_at": "2025-11-29T10:30:00Z"
    }
  ]
}
```

**Tri par défaut:** `-created_at` (plus récents en premier)

---

### 5. Récupérer un Paiement
**GET** `/stripe/{id}/`

Obtient les détails complets d'un paiement spécifique.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Réponse (200 OK):**
```json
{
  "id": 1,
  "order": 1,
  "order_id": 1,
  "order_email": "client@example.com",
  "payment_intent_id": "pi_1234567890abcdef",
  "checkout_session_id": "cs_test_a1b2c3d4e5f6g7h8",
  "amount": 2500,
  "amount_euros": "25.00",
  "currency": "eur",
  "status": "succeeded",
  "metadata": {
    "order_id": 1
  },
  "webhook_received": true,
  "webhook_data": {
    "id": "cs_test_a1b2c3d4e5f6g7h8",
    "amount_total": 2500,
    "currency": "eur",
    "customer_email": "client@example.com",
    "payment_intent": "pi_1234567890abcdef",
    "status": "complete"
  },
  "webhook_received_at": "2025-11-29T10:30:00Z",
  "created_at": "2025-11-29T10:25:00Z",
  "updated_at": "2025-11-29T10:30:00Z"
}
```

**Erreur - Paiement non trouvé (404):**
```json
{
  "detail": "Pas trouvé."
}
```

---

## 🔐 Résumé des Permissions

| Endpoint | Méthode | Permission |
|----------|---------|------------|
| Créer session checkout | POST | Public ✅ |
| Webhook Stripe | POST | Public (signature) ✅ |
| Vérifier paiement | GET | Public ✅ |
| Lister paiements | GET | Authentifié ✅ |
| Récupérer paiement | GET | Authentifié ✅ |

---

## 💡 Exemples cURL

### Créer une session checkout
```bash
curl -X POST http://127.0.0.1:8000/api/v1/payments/create-checkout/ \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1
  }'
```

### Vérifier un paiement
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/payments/verify/?order_id=1" \
  -H "Content-Type: application/json"
```

### Lister les paiements (authentifié)
```bash
curl -X GET http://127.0.0.1:8000/api/v1/payments/stripe/ \
  -H "Authorization: Bearer <access_token>"
```

### Lister les paiements avec pagination
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/payments/stripe/?page=2&page_size=10" \
  -H "Authorization: Bearer <access_token>"
```

### Récupérer un paiement spécifique
```bash
curl -X GET http://127.0.0.1:8000/api/v1/payments/stripe/1/ \
  -H "Authorization: Bearer <access_token>"
```

---

## 📋 Flux de Paiement Complet

### Étape 1: Client crée une commande
```
POST /api/v1/orders/
→ Reçoit: order_id
```

### Étape 2: Client demande une session Checkout
```
POST /api/v1/payments/create-checkout/
Body: { "order_id": 1 }
→ Reçoit: checkout_url et session_id
```

### Étape 3: Client accède à Stripe Checkout
```
Redirection vers checkout_url
→ Client effectue le paiement
```

### Étape 4: Stripe envoie webhook
```
POST /api/v1/payments/webhook/ (événement checkout.session.completed)
→ Commande mise à jour automatiquement
→ StripePayment créé
```

### Étape 5: Client est redirigé
```
Vers STRIPE_SUCCESS_URL ou STRIPE_CANCEL_URL
Inclut: ?order_id=1
```

### Étape 6: Client vérifie le paiement
```
GET /api/v1/payments/verify/?order_id=1
→ Reçoit: paid=true/false, status, détails commande
```

---

## 📊 Statuts Stripe

| Statut | Description |
|--------|-------------|
| `succeeded` | Paiement réussi |
| `failed` | Paiement échoué |
| `processing` | Paiement en cours de traitement |
| `requires_payment_method` | Nécessite un moyen de paiement |
| `canceled` | Paiement annulé par le client |

---

## 🔒 Sécurité

### Webhook Stripe
- ✅ Sécurisé par **vérification de signature Stripe**
- ✅ Signature vérifiée avec `STRIPE_WEBHOOK_SECRET`
- ✅ Exempt de protection CSRF (Stripe ne peut pas fournir de token)
- ✅ Seuls les webhooks Stripe authentifiés sont traités

### Montants
- ✅ Toujours stockés en **centimes** pour éviter les erreurs d'arrondi
- ✅ Conversion automatique en euros via propriété `amount_euros`
- ✅ Cohérence garantie entre commande et paiement

### API Stripe
- ✅ Clé secrète stockée dans les settings Django
- ✅ Clé secrète webhook protégée
- ✅ Aucune donnée sensible exposée dans les réponses

---

## 📧 Notifications

### Paiement Réussi
- Stripe envoie email au client (automatique)
- Admin notifié via webhook

### Paiement Échoué
- Stripe envoie email au client (automatique)
- Webhook enregistre l'échec
- TODO: Notification admin + relance client

---

## 📝 Notes Importantes

1. **Clé API:**
   - Variable d'environnement: `STRIPE_SECRET_KEY` (format `sk_test_...`)
   - À configurer dans `settings.py`

2. **Secret Webhook:**
   - Variable d'environnement: `STRIPE_WEBHOOK_SECRET` (format `whsec_...`)
   - À obtenir du dashboard Stripe
   - À configurer dans `settings.py`

3. **URLs de Redirection:**
   - `STRIPE_SUCCESS_URL`: URL après paiement réussi
   - `STRIPE_CANCEL_URL`: URL après annulation du paiement
   - Inclure `?order_id={order_id}` dans les paramètres de requête

4. **Montants:**
   - Stockés en centimes (ex: 2500 = 25,00€)
   - Conversion automatique en euros via `amount_euros`

5. **Métadonnées:**
   - Contiennent toujours `order_id` pour tracer la commande
   - Utilisées pour router les événements webhook

6. **Commande Déjà Payée:**
   - Vérification via `stripe_payment_intent_id`
   - Empêche les paiements multiples sur la même commande

7. **Validation Webhook:**
   - Signature obligatoire pour sécurité
   - Événements non reconnus ignorés silencieusement

---

## 🚨 Codes de Statut HTTP

| Code | Description |
|------|-------------|
| 200 | Requête réussie |
| 400 | Validation échouée (order_id manquant, commande déjà payée, erreur Stripe) |
| 404 | Commande non trouvée |
| 401 | Non authentifié (pour endpoints admin) |
| 500 | Erreur serveur |

---

## 🔧 Configuration Django Requise

### settings.py

```python
# Clés Stripe (à obtenir du dashboard Stripe)
STRIPE_SECRET_KEY = 'sk_test_...'  # Clé secrète
STRIPE_WEBHOOK_SECRET = 'whsec_...'  # Secret webhook

# URLs de redirection après paiement
STRIPE_SUCCESS_URL = 'https://votresite.com/success'
STRIPE_CANCEL_URL = 'https://votresite.com/cancel'

# Email admin pour notifications
ADMIN_NOTIFICATION_EMAILS = [
    'admin@example.com',
    'support@example.com'
]

# Configuration email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre-email@gmail.com'
EMAIL_HOST_PASSWORD = 'votre-mot-de-passe'
DEFAULT_FROM_EMAIL = 'noreply@example.com'
```

### Webhook Stripe Dashboard

1. Aller dans: **Webhooks** → **Add endpoint**
2. URL: `https://votreapi.com/api/v1/payments/webhook/`
3. Événements à écouter:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
4. Copier le **Signing Secret** (`whsec_...`) dans `STRIPE_WEBHOOK_SECRET`

### Installation

```bash
pip install stripe
```

---

## 🧪 Test Webhook Localement

Utiliser la CLI Stripe pour écouter les webhooks en développement:

```bash
stripe listen --forward-to localhost:8000/api/v1/payments/webhook/
```

Cela retournera un `STRIPE_WEBHOOK_SECRET` à utiliser en développement.

---

## 📚 Ressources Stripe

- [Documentation Stripe API](https://stripe.com/docs/api)
- [Stripe Checkout](https://stripe.com/docs/payments/checkout)
- [Webhook Events](https://stripe.com/docs/webhooks)
- [Test Cards](https://stripe.com/docs/testing)
