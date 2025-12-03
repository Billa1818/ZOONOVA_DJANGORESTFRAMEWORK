# 📚 API Authentification - Comptes Administrateurs

## Base URL
```
http://127.0.0.1:8000/api/v1/auth/
```

---

## 🔐 Endpoints d'Authentification

### 1. Login (Connexion)
**POST** `/login/`

Authentifier un administrateur et obtenir les tokens JWT.

**Payload:**
```json
{
  "email": "admin@example.com",
  "password": "password123"
}
```

**Réponse (200 OK):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_superuser": true
  }
}
```

**Erreur - Première connexion (403):**
```json
{
  "error": "first_login",
  "message": "Première connexion. Veuillez définir votre mot de passe.",
  "email": "admin@example.com"
}
```

**Erreur - Identifiants invalides (401):**
```json
{
  "error": "invalid_credentials",
  "message": "Email ou mot de passe incorrect"
}
```

---

### 2. Rafraîchir le Token
**POST** `/token/refresh/`

Obtenir un nouveau token d'accès avec le refresh token.

**Payload:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Réponse (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 🔑 Endpoints Gestion du Mot de Passe

### 3. Définir le Mot de Passe Initial
**POST** `/set-password/`

Définir le mot de passe lors de la première connexion.
> ⚠️ Endpoint Public (pas d'authentification requise)

**Payload:**
```json
{
  "email": "admin@example.com",
  "password": "SecurePassword123!",
  "password_confirm": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Réponse (200 OK):**
```json
{
  "message": "Mot de passe défini avec succès",
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "is_staff": true,
    "is_superuser": true,
    "date_joined": "2024-01-15T10:30:00Z",
    "last_login": null
  }
}
```

**Erreur - Mot de passe déjà défini (400):**
```json
{
  "error": "password_already_set",
  "message": "Le mot de passe a déjà été défini"
}
```

---

### 4. Demander Réinitialisation de Mot de Passe
**POST** `/password-reset/request/`

Envoyer un email avec un lien de réinitialisation.
> ⚠️ Endpoint Public (pas d'authentification requise)

**Payload:**
```json
{
  "email": "admin@example.com"
}
```

**Réponse (200 OK):**
```json
{
  "message": "Email de réinitialisation envoyé"
}
```

> Note: Pour des raisons de sécurité, le même message est retourné que l'email existe ou non.

---

### 5. Confirmer Réinitialisation de Mot de Passe
**POST** `/password-reset/confirm/`

Réinitialiser le mot de passe avec le token reçu par email.
> ⚠️ Endpoint Public (pas d'authentification requise)
> ⏱️ Le token expire après 1 heure

**Payload:**
```json
{
  "token": "nGHzr2FmKpL9xQ5vW8yT3bJ0cDqS1aE4...",
  "password": "NewSecurePassword456!",
  "password_confirm": "NewSecurePassword456!"
}
```

**Réponse (200 OK):**
```json
{
  "message": "Mot de passe réinitialisé avec succès"
}
```

**Erreur - Token expiré (400):**
```json
{
  "error": "token_expired",
  "message": "Le lien de réinitialisation a expiré"
}
```

**Erreur - Token invalide (400):**
```json
{
  "error": "invalid_token",
  "message": "Lien de réinitialisation invalide"
}
```

---

## 👥 Endpoints Gestion des Administrateurs

Tous les endpoints ci-dessous requièrent l'authentification JWT et le statut **Superuser**.

### 6. Lister les Administrateurs
**GET** `/admins/`

Récupérer la liste des administrateurs.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters (optionnels):**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `is_active` | boolean | Filtrer par statut actif/inactif |
| `is_superuser` | boolean | Filtrer par statut superuser |

**Exemples:**
```
/admins/?is_active=true
/admins/?is_superuser=false
```

**Réponse (200 OK):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "email": "superadmin@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true
    },
    {
      "id": 2,
      "email": "admin@example.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "is_active": true
    }
  ]
}
```

---

### 7. Récupérer les Informations de l'Admin Connecté
**GET** `/admins/me/`

Obtenir les détails de l'administrateur actuellement connecté.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Réponse (200 OK):**
```json
{
  "id": 1,
  "email": "admin@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "is_active": true,
  "is_staff": true,
  "is_superuser": true,
  "date_joined": "2024-01-15T10:30:00Z",
  "last_login": "2024-01-20T14:25:00Z"
}
```

---

### 8. Créer un Administrateur
**POST** `/admins/`

Créer un nouvel administrateur (sans mot de passe, invite par email).

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Payload:**
```json
{
  "email": "newadmin@example.com",
  "first_name": "Marie",
  "last_name": "Dupont",
  "is_staff": true,
  "is_superuser": false
}
```

**Réponse (201 CREATED):**
```json
{
  "message": "Administrateur créé avec succès. Un email d'invitation a été envoyé.",
  "admin": {
    "id": 3,
    "email": "newadmin@example.com",
    "first_name": "Marie",
    "last_name": "Dupont",
    "full_name": "Marie Dupont",
    "is_active": true,
    "is_staff": true,
    "is_superuser": false,
    "date_joined": "2024-01-21T09:15:00Z",
    "last_login": null
  }
}
```

**Erreur - Permissions insuffisantes (403):**
```json
{
  "error": "permission_denied",
  "message": "Seuls les superusers peuvent créer des administrateurs"
}
```

---

### 9. Récupérer un Administrateur
**GET** `/admins/{id}/`

Obtenir les détails d'un administrateur spécifique.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Réponse (200 OK):**
```json
{
  "id": 2,
  "email": "admin@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "full_name": "Jane Smith",
  "is_active": true,
  "is_staff": true,
  "is_superuser": false,
  "date_joined": "2024-01-16T11:45:00Z",
  "last_login": "2024-01-20T09:30:00Z"
}
```

---

### 10. Modifier un Administrateur
**PUT** `/admins/{id}/`

Mettre à jour complètement un administrateur.

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
  "last_name": "Martin",
  "is_active": true,
  "is_staff": true,
  "is_superuser": false
}
```

**Réponse (200 OK):** Même format que GET `/admins/{id}/`

---

### 11. Modification Partielle d'un Administrateur
**PATCH** `/admins/{id}/`

Mettre à jour partiellement un administrateur.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Payload (exemple):**
```json
{
  "first_name": "Jean"
}
```

**Réponse (200 OK):** Même format que GET `/admins/{id}/`

---

### 12. Activer/Désactiver un Administrateur
**POST** `/admins/{id}/toggle_active/`

Basculer l'état actif/inactif d'un administrateur.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Réponse (200 OK):**
```json
{
  "message": "Compte activé",
  "admin": {
    "id": 2,
    "email": "admin@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "full_name": "Jane Smith",
    "is_active": true,
    "is_staff": true,
    "is_superuser": false,
    "date_joined": "2024-01-16T11:45:00Z",
    "last_login": "2024-01-20T09:30:00Z"
  }
}
```

**Erreur - Impossible de se désactiver soi-même (400):**
```json
{
  "error": "cannot_deactivate_self",
  "message": "Vous ne pouvez pas désactiver votre propre compte"
}
```

**Erreur - Permissions insuffisantes (403):**
```json
{
  "error": "permission_denied",
  "message": "Seuls les superusers peuvent modifier le statut"
}
```

---

### 13. Changer son Propre Mot de Passe
**POST** `/admins/change_password/`

Modifier le mot de passe de l'administrateur connecté.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Payload:**
```json
{
  "old_password": "CurrentPassword123!",
  "new_password": "NewSecurePassword456!"
}
```

**Réponse (200 OK):**
```json
{
  "message": "Mot de passe modifié avec succès"
}
```

**Erreur - Ancien mot de passe incorrect (400):**
```json
{
  "error": "invalid_password",
  "message": "Mot de passe actuel incorrect"
}
```

**Erreur - Champs manquants (400):**
```json
{
  "error": "missing_fields",
  "message": "Ancien et nouveau mot de passe requis"
}
```

---

### 14. Supprimer un Administrateur
**DELETE** `/admins/{id}/`

Supprimer complètement un administrateur.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Réponse (204 NO CONTENT):** Pas de contenu

---

## 📋 Flux d'Authentification Complet

### Première Connexion d'un Admin
1. **Admin créé par Superuser**
   - Endpoint: `POST /admins/`
   - Email d'invitation reçu automatiquement

2. **Admin définit son mot de passe**
   - Endpoint: `POST /set-password/`
   - Reçoit les tokens JWT

3. **Admin se connecte**
   - Endpoint: `POST /login/`
   - Utilise email et mot de passe défini

### Réinitialisation de Mot de Passe
1. **Admin demande réinitialisation**
   - Endpoint: `POST /password-reset/request/`
   - Email avec token reçu

2. **Admin confirme réinitialisation**
   - Endpoint: `POST /password-reset/confirm/`
   - Utilise le token reçu par email

3. **Admin se reconnecte**
   - Endpoint: `POST /login/`
   - Avec le nouveau mot de passe

---

## 🔒 Permissions & Authentification

| Endpoint | Public | Authentifié | Superuser |
|----------|--------|-------------|-----------|
| `POST /login/` | ✅ | - | - |
| `POST /token/refresh/` | ✅ | - | - |
| `POST /set-password/` | ✅ | - | - |
| `POST /password-reset/request/` | ✅ | - | - |
| `POST /password-reset/confirm/` | ✅ | - | - |
| `GET /admins/` | ❌ | ✅ | ✅ |
| `POST /admins/` | ❌ | ✅ | ✅ |
| `GET /admins/{id}/` | ❌ | ✅ | ✅ |
| `PUT /admins/{id}/` | ❌ | ✅ | ✅ |
| `PATCH /admins/{id}/` | ❌ | ✅ | ✅ |
| `POST /admins/{id}/toggle_active/` | ❌ | ✅ | ✅ |
| `POST /admins/me/` | ❌ | ✅ | - |
| `POST /admins/change_password/` | ❌ | ✅ | - |
| `DELETE /admins/{id}/` | ❌ | ✅ | ✅ |

---

## 💡 Exemples avec cURL

### Login
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "password123"
  }'
```

### Rafraîchir le token
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

### Lister les admins (authentifié)
```bash
curl -X GET http://127.0.0.1:8000/api/v1/auth/admins/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Créer un admin
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/admins/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newadmin@example.com",
    "first_name": "Marie",
    "last_name": "Dupont",
    "is_staff": true,
    "is_superuser": false
  }'
```

### Changer son mot de passe
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/admins/change_password/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "CurrentPassword123!",
    "new_password": "NewSecurePassword456!"
  }'
```

---

## 🚨 Codes de Statut HTTP

| Code | Description |
|------|-------------|
| 200 | Requête réussie |
| 201 | Ressource créée |
| 204 | Ressource supprimée / Succès sans contenu |
| 400 | Erreur de validation ou logique métier |
| 401 | Non authentifié (token manquant/invalide) |
| 403 | Authentifié mais permissions insuffisantes |
| 404 | Ressource non trouvée |
| 500 | Erreur serveur |
