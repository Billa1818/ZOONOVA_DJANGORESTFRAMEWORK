# 📧 API Contact - Documentation Complète

## Base URL
```
http://127.0.0.1:8000/api/v1/contact/messages/
```

---

## 📨 Endpoints Messages de Contact

### 1. Créer un Message de Contact
**POST** `/`

Crée un nouveau message de contact. Endpoint public, envoie des emails de notification et de confirmation automatiquement.

**Permissions:** Public (pas d'authentification requise)

**Headers:**
```
Content-Type: application/json
```

**Payload:**
```json
{
  "first_name": "Jean",
  "last_name": "Dupont",
  "email": "jean.dupont@example.com",
  "subject": "Demande d'information",
  "message": "Bonjour, je souhaiterais avoir des informations sur votre catalogue de livres..."
}
```

**Validations:**
- `first_name`: requis, max 255 caractères
- `last_name`: requis, max 255 caractères
- `email`: requis, format email valide
- `subject`: optionnel, max 255 caractères
- `message`: requis, minimum 10 caractères

**Réponse (201 CREATED):**
```json
{
  "message": "Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.",
  "data": {
    "id": 1,
    "first_name": "Jean",
    "last_name": "Dupont",
    "full_name": "Jean Dupont",
    "email": "jean.dupont@example.com",
    "subject": "Demande d'information",
    "message": "Bonjour, je souhaiterais avoir des informations sur votre catalogue de livres...",
    "is_read": false,
    "replied_at": null,
    "admin_notes": "",
    "created_at": "2025-11-29T10:30:00Z",
    "updated_at": "2025-11-29T10:30:00Z"
  }
}
```

**Erreur - Message trop court (400):**
```json
{
  "message": ["Le message doit contenir au moins 10 caractères"]
}
```

**Erreur - Email invalide (400):**
```json
{
  "email": ["Entrez une adresse e-mail valide."]
}
```

**Actions automatiques:**
- ✉️ Email de notification envoyé à l'admin
- ✉️ Email de confirmation envoyé au client
- 📊 Statut: `is_read = false`, `replied_at = null`

---

### 2. Lister les Messages
**GET** `/`

Récupère la liste paginée de tous les messages de contact.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters (optionnels):**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `unread_only` | boolean | Filtrer uniquement les messages non lus (`true`/`false`) |
| `is_read` | boolean | Filtrer par statut de lecture |
| `search` | string | Recherche dans prénom, nom, email, sujet, message |
| `ordering` | string | Tri: `-created_at` (défaut), `created_at` |

**Exemples:**
```
GET /?unread_only=true
GET /?is_read=false
GET /?search=jean&ordering=-created_at
GET /?is_read=true&search=question
```

**Réponse (200 OK):**
```json
{
  "count": 42,
  "next": "http://127.0.0.1:8000/api/v1/contact/messages/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "first_name": "Jean",
      "last_name": "Dupont",
      "full_name": "Jean Dupont",
      "email": "jean.dupont@example.com",
      "subject": "Demande d'information",
      "message": "Bonjour, je souhaiterais avoir des informations sur votre catalogue de livres...",
      "is_read": false,
      "replied_at": null,
      "admin_notes": "",
      "created_at": "2025-11-29T10:30:00Z",
      "updated_at": "2025-11-29T10:30:00Z"
    },
    {
      "id": 2,
      "first_name": "Marie",
      "last_name": "Martin",
      "full_name": "Marie Martin",
      "email": "marie.martin@example.com",
      "subject": "Problème de commande",
      "message": "Bonjour, je n'ai pas reçu ma commande du 25 novembre...",
      "is_read": true,
      "replied_at": "2025-11-29T14:00:00Z",
      "admin_notes": "Contactée par email, envoi d'un lien de suivi",
      "created_at": "2025-11-28T15:45:00Z",
      "updated_at": "2025-11-29T14:00:00Z"
    }
  ]
}
```

---

### 3. Récupérer un Message
**GET** `/{id}/`

Obtient les détails complets d'un message spécifique.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Réponse (200 OK):**
```json
{
  "id": 1,
  "first_name": "Jean",
  "last_name": "Dupont",
  "full_name": "Jean Dupont",
  "email": "jean.dupont@example.com",
  "subject": "Demande d'information",
  "message": "Bonjour, je souhaiterais avoir des informations sur votre catalogue de livres...",
  "is_read": false,
  "replied_at": null,
  "admin_notes": "",
  "created_at": "2025-11-29T10:30:00Z",
  "updated_at": "2025-11-29T10:30:00Z"
}
```

**Erreur - Message non trouvé (404):**
```json
{
  "detail": "Pas trouvé."
}
```

---

### 4. Mettre à Jour un Message (Complet)
**PUT** `/{id}/`

Met à jour complètement un message. Utilisé pour modifier les notes admin ou le statut.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Payload:**
```json
{
  "first_name": "Jean",
  "last_name": "Dupont",
  "email": "jean.dupont@example.com",
  "subject": "Demande d'information",
  "message": "Bonjour, je souhaiterais avoir des informations sur votre catalogue...",
  "is_read": true,
  "replied_at": "2025-11-29T14:00:00Z",
  "admin_notes": "Client contacté par email le 29/11/2025"
}
```

**Réponse (200 OK):** Même format que GET `/{id}/`

---

### 5. Mettre à Jour un Message (Partiel)
**PATCH** `/{id}/`

Met à jour partiellement un message. Utilisé pour modifier certains champs uniquement.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Payload (exemple):**
```json
{
  "is_read": true,
  "admin_notes": "Client contacté par email le 29/11/2025"
}
```

**Réponse (200 OK):** Même format que GET `/{id}/`

---

### 6. Supprimer un Message
**DELETE** `/{id}/`

Supprime complètement un message de la base de données.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Réponse (204 NO CONTENT):** Pas de contenu

---

## 🏷️ Actions Spéciales

### 7. Marquer comme Lu
**POST** `/{id}/mark_as_read/`

Marque un message comme lu par l'admin.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Body:** Aucun body requis (POST vide)

**Réponse (200 OK):**
```json
{
  "message": "Message marqué comme lu",
  "data": {
    "id": 1,
    "first_name": "Jean",
    "last_name": "Dupont",
    "full_name": "Jean Dupont",
    "email": "jean.dupont@example.com",
    "subject": "Demande d'information",
    "message": "Bonjour, je souhaiterais avoir des informations...",
    "is_read": true,
    "replied_at": null,
    "admin_notes": "",
    "created_at": "2025-11-29T10:30:00Z",
    "updated_at": "2025-11-29T10:35:00Z"
  }
}
```

---

### 8. Marquer comme Non Lu
**POST** `/{id}/mark_as_unread/`

Marque un message comme non lu.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Body:** Aucun body requis (POST vide)

**Réponse (200 OK):**
```json
{
  "message": "Message marqué comme non lu",
  "data": {
    "id": 1,
    "is_read": false,
    ...
  }
}
```

---

### 9. Marquer comme Répondu
**POST** `/{id}/mark_as_replied/`

Marque un message comme ayant reçu une réponse. Définit automatiquement:
- `replied_at` = date/heure actuelle
- `is_read` = true

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Payload (optionnel):**
```json
{
  "admin_notes": "Répondu par email avec les informations demandées"
}
```

**Réponse (200 OK):**
```json
{
  "message": "Message marqué comme répondu",
  "data": {
    "id": 1,
    "first_name": "Jean",
    "last_name": "Dupont",
    "full_name": "Jean Dupont",
    "email": "jean.dupont@example.com",
    "subject": "Demande d'information",
    "message": "Bonjour, je souhaiterais avoir des informations...",
    "is_read": true,
    "replied_at": "2025-11-29T14:30:00Z",
    "admin_notes": "Répondu par email avec les informations demandées",
    "created_at": "2025-11-29T10:30:00Z",
    "updated_at": "2025-11-29T14:30:00Z"
  }
}
```

---

### 10. Obtenir les Statistiques
**GET** `/statistics/`

Récupère les statistiques globales des messages de contact.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Réponse (200 OK):**
```json
{
  "total_messages": 150,
  "unread_messages": 23,
  "replied_messages": 95,
  "pending_messages": 55
}
```

**Description des champs:**
- `total_messages`: Nombre total de messages reçus
- `unread_messages`: Nombre de messages non lus
- `replied_messages`: Nombre de messages ayant reçu une réponse
- `pending_messages`: Nombre de messages en attente (`total - replied`)

---

### 11. Marquer Plusieurs Messages comme Lus
**POST** `/bulk_mark_as_read/`

Marque plusieurs messages comme lus en une seule requête.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Payload:**
```json
{
  "message_ids": [1, 5, 12, 23, 45]
}
```

**Réponse (200 OK):**
```json
{
  "message": "5 message(s) marqué(s) comme lu(s)",
  "updated_count": 5
}
```

**Erreur - Champ manquant (400):**
```json
{
  "error": "message_ids requis"
}
```

---

## 🔐 Résumé des Permissions

| Endpoint | Méthode | Permission |
|----------|---------|------------|
| Créer message | POST | Public ✅ |
| Lister messages | GET | Authentifié ✅ |
| Récupérer message | GET | Authentifié ✅ |
| Modifier message | PUT/PATCH | Authentifié ✅ |
| Supprimer message | DELETE | Authentifié ✅ |
| Marquer comme lu | POST | Authentifié ✅ |
| Marquer comme non lu | POST | Authentifié ✅ |
| Marquer comme répondu | POST | Authentifié ✅ |
| Statistiques | GET | Authentifié ✅ |
| Marquage groupé | POST | Authentifié ✅ |

---

## 💡 Exemples cURL

### Créer un message (Public)
```bash
curl -X POST http://127.0.0.1:8000/api/v1/contact/messages/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jean",
    "last_name": "Dupont",
    "email": "jean.dupont@example.com",
    "subject": "Demande d'information",
    "message": "Bonjour, je souhaiterais avoir des informations sur votre catalogue..."
  }'
```

### Lister les messages non lus
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/contact/messages/?unread_only=true" \
  -H "Authorization: Bearer <access_token>"
```

### Rechercher les messages d'un client
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/contact/messages/?search=jean@example.com" \
  -H "Authorization: Bearer <access_token>"
```

### Récupérer un message
```bash
curl -X GET http://127.0.0.1:8000/api/v1/contact/messages/1/ \
  -H "Authorization: Bearer <access_token>"
```

### Marquer un message comme lu
```bash
curl -X POST http://127.0.0.1:8000/api/v1/contact/messages/1/mark_as_read/ \
  -H "Authorization: Bearer <access_token>"
```

### Marquer un message comme répondu avec notes
```bash
curl -X POST http://127.0.0.1:8000/api/v1/contact/messages/1/mark_as_replied/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "admin_notes": "Répondu par email avec les informations demandées"
  }'
```

### Obtenir les statistiques
```bash
curl -X GET http://127.0.0.1:8000/api/v1/contact/messages/statistics/ \
  -H "Authorization: Bearer <access_token>"
```

### Marquer plusieurs messages comme lus
```bash
curl -X POST http://127.0.0.1:8000/api/v1/contact/messages/bulk_mark_as_read/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message_ids": [1, 5, 12, 23, 45]
  }'
```

### Mettre à jour un message (PATCH)
```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/contact/messages/1/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "is_read": true,
    "admin_notes": "Client contacté par téléphone"
  }'
```

### Supprimer un message
```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/contact/messages/1/ \
  -H "Authorization: Bearer <access_token>"
```

---

## 📧 Notifications Email

### Email Admin
- **Déclenché:** Création d'un nouveau message
- **Destinataires:** Définis dans `settings.ADMIN_NOTIFICATION_EMAILS`
- **Contenu:** Détails complets du message et lien d'accès au backoffice

### Email Client
- **Déclenché:** Création d'un nouveau message
- **Destinataire:** Email du client
- **Contenu:** Confirmation de réception et assurance de suivi

### Gestion des Erreurs Email
- Les erreurs d'envoi d'email n'empêchent pas la création du message
- Les tentatives d'envoi sont loggées en cas d'erreur
- La requête retourne toujours 201 CREATED même si les emails échouent

---

## 📋 Notes Importantes

1. **Sécurité:**
   - Seul l'endpoint POST est public
   - Tous les autres endpoints nécessitent l'authentification JWT
   - Les utilisateurs authentifiés voient tous les messages (admin)

2. **Validation du Message:**
   - Minimum 10 caractères (espaces inclus)
   - Trimé avant validation (espaces supprimés)
   - Erreur explicite si validation échoue

3. **Recherche:**
   - S'effectue sur: `first_name`, `last_name`, `email`, `subject`, `message`
   - Insensible à la casse
   - Supporte les recherches partielles

4. **Tri par Défaut:**
   - `-created_at` (messages les plus récents en premier)
   - Modifiable via paramètre `ordering`

5. **Statut des Messages:**
   - `is_read`: true/false, utilisé pour filtrer les messages à traiter
   - `replied_at`: null si pas de réponse, timestamp sinon
   - `admin_notes`: Champ libre pour notes internes

6. **Pagination:**
   - Activée par défaut
   - Taille par page: configurable dans les settings
   - Format: `count`, `next`, `previous`, `results`

---

## 🚨 Codes de Statut HTTP

| Code | Description |
|------|-------------|
| 200 | Requête réussie |
| 201 | Message créé |
| 204 | Suppression réussie (pas de contenu) |
| 400 | Validation échouée (données invalides) |
| 401 | Non authentifié (token manquant/invalide) |
| 403 | Authentifié mais permissions insuffisantes |
| 404 | Message non trouvé |
| 500 | Erreur serveur |

---

## 🔧 Configuration Django Requise

```python
# settings.py

# Emails admin pour notifications
ADMIN_NOTIFICATION_EMAILS = [
    'admin@example.com',
    'support@example.com'
]

# Configuration email (SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # ou votre serveur SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre-email@gmail.com'
EMAIL_HOST_PASSWORD = 'votre-mot-de-passe'
DEFAULT_FROM_EMAIL = 'noreply@example.com'

# URL du site pour les liens
SITE_URL = 'http://127.0.0.1:8000'
```
