# 📚 API Catalogue Livres - Documentation Complète

## Base URL
```
http://127.0.0.1:8000/api/v1/books/
```

---

## 📖 Endpoints Livres

### 1. Lister les Livres
**GET** `/`

Récupère la liste paginée de tous les livres actifs.

**Query Parameters (optionnels):**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `is_featured` | boolean | Filtrer les livres mis en avant |
| `langue` | string | Filtrer par langue |
| `editeur` | string | Filtrer par éditeur |
| `search` | string | Recherche dans titre, nom, description, légende |
| `ordering` | string | Trier: `-created_at`, `prix`, `-prix`, `views_count`, `sales_count` |
| `min_price` | integer | Prix minimum (en centimes) |
| `max_price` | integer | Prix maximum (en centimes) |
| `in_stock` | boolean | Filtrer les livres en stock |

**Exemples:**
```
GET /?search=python&in_stock=true&ordering=-sales_count
GET /?is_featured=true&langue=Français
GET /?min_price=1000&max_price=5000
```

**Permissions:** Public (lecture)

**Réponse (200 OK):**
```json
{
  "count": 15,
  "next": "http://127.0.0.1:8000/api/v1/books/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "titre": "Python pour les débutants",
      "nom": "Jean Dupont",
      "legende": "Apprenez la programmation facilement",
      "slug": "python-pour-les-debutants",
      "prix": 2500,
      "prix_euros": "25.00",
      "quantites": 15,
      "in_stock": true,
      "main_image": "http://127.0.0.1:8000/media/books/python/images/cover.jpg",
      "is_featured": true,
      "views_count": 150,
      "sales_count": 45
    }
  ]
}
```

---

### 2. Détails d'un Livre
**GET** `/{id}/`

Récupère les détails complets d'un livre. Incrémente automatiquement le compteur de vues.

**Permissions:** Public

**Réponse (200 OK):**
```json
{
  "id": 1,
  "titre": "Python pour les débutants",
  "nom": "Jean Dupont",
  "description": "Un guide complet pour apprendre Python...",
  "legende": "Apprenez la programmation facilement",
  "prix": 2500,
  "prix_euros": "25.00",
  "code_bare": "9782123456789",
  "nombre_pages": 350,
  "largeur_cm": "15.00",
  "hauteur_cm": "21.00",
  "epaisseur_cm": "2.50",
  "poids_grammes": 450,
  "dimensions": "15.00 × 21.00 × 2.50 cm",
  "date_publication": "2024-01-15",
  "editeur": "Éditions Tech",
  "langue": "Français",
  "quantites": 15,
  "in_stock": true,
  "slug": "python-pour-les-debutants",
  "seo_title": "Python pour débutants - Guide complet",
  "seo_description": "Apprenez Python facilement avec ce guide...",
  "views_count": 151,
  "sales_count": 45,
  "is_active": true,
  "is_featured": true,
  "images": [
    {
      "id": 1,
      "book": 1,
      "image": "/media/books/python/images/cover.jpg",
      "image_url": "http://127.0.0.1:8000/media/books/python/images/cover.jpg",
      "type": "cover_front",
      "type_display": "Couverture (1ère page)",
      "is_main_cover": true,
      "order": 0,
      "alt_text": "Couverture du livre Python",
      "created_at": "2024-01-10T10:00:00Z",
      "updated_at": "2024-01-10T10:00:00Z"
    }
  ],
  "videos": [
    {
      "id": 1,
      "book": 1,
      "video_url": "https://www.youtube.com/watch?v=abc123",
      "title": "Présentation du livre",
      "description": "Découvrez le contenu...",
      "order": 0,
      "created_at": "2024-01-10T10:00:00Z",
      "updated_at": "2024-01-10T10:00:00Z"
    }
  ],
  "created_at": "2024-01-10T10:00:00Z",
  "updated_at": "2024-01-15T14:30:00Z"
}
```

---

### 3. Créer un Livre
**POST** `/`

Crée un nouveau livre dans le catalogue.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Payload:**
```json
{
  "titre": "Django Avancé",
  "nom": "Marie Martin",
  "description": "Techniques avancées de Django...",
  "legende": "Pour développeurs expérimentés",
  "prix": 3500,
  "code_bare": "9782987654321",
  "nombre_pages": 450,
  "largeur_cm": "16.00",
  "hauteur_cm": "24.00",
  "epaisseur_cm": "3.00",
  "poids_grammes": 600,
  "date_publication": "2024-02-01",
  "editeur": "Éditions Web",
  "langue": "Français",
  "quantites": 20,
  "seo_title": "Django Avancé - Maîtrisez le framework",
  "seo_description": "Guide complet Django pour experts",
  "is_active": true,
  "is_featured": false
}
```

**Réponse (201 CREATED):**
```json
{
  "id": 2,
  "titre": "Django Avancé",
  "slug": "django-avance",
  "nom": "Marie Martin",
  "description": "Techniques avancées de Django...",
  "prix": 3500,
  ...
}
```

---

### 4. Mettre à Jour un Livre (Complet)
**PUT** `/{id}/`

Met à jour complètement un livre (tous les champs requis).

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Payload:** Même structure que POST (tous les champs requis)

**Réponse (200 OK):** Même format que GET `/{id}/`

---

### 5. Mettre à Jour un Livre (Partiel)
**PATCH** `/{id}/`

Met à jour partiellement un livre.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Payload (exemple):**
```json
{
  "prix": 2990,
  "quantites": 25,
  "is_featured": true
}
```

**Réponse (200 OK):** Même format que GET `/{id}/`

---

### 6. Supprimer un Livre
**DELETE** `/{id}/`

Supprime complètement un livre du catalogue.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Réponse (204 NO CONTENT):** Pas de contenu

---

### 7. Mettre à Jour le Stock
**PATCH** `/{id}/update_stock/`

Endpoint dédié pour mettre à jour uniquement le stock.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Payload:**
```json
{
  "quantites": 50
}
```

**Réponse (200 OK):**
```json
{
  "message": "Stock mis à jour",
  "book": {
    "id": 1,
    "titre": "Python pour les débutants",
    "quantites": 50,
    "in_stock": true
  }
}
```

---

### 8. Activer/Désactiver la Mise en Avant
**POST** `/{id}/toggle_featured/`

Active ou désactive la mise en avant d'un livre.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Réponse (200 OK):**
```json
{
  "message": "Livre mis en avant",
  "is_featured": true
}
```

---

### 9. Activer/Désactiver le Livre
**POST** `/{id}/toggle_active/`

Active ou désactive la visibilité publique d'un livre.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Réponse (200 OK):**
```json
{
  "message": "Livre activé",
  "is_active": true
}
```

---

## 🖼️ Endpoints Images

### 10. Lister les Images d'un Livre
**GET** `/{id}/images/`

Récupère toutes les images d'un livre spécifique.

**Permissions:** Public

**Réponse (200 OK):**
```json
[
  {
    "id": 1,
    "book": 1,
    "image": "/media/books/python-pour-les-debutants/images/cover.jpg",
    "image_url": "http://127.0.0.1:8000/media/books/python-pour-les-debutants/images/cover.jpg",
    "type": "cover_front",
    "type_display": "Couverture (1ère page)",
    "is_main_cover": true,
    "order": 0,
    "alt_text": "Couverture principale",
    "created_at": "2024-01-10T10:00:00Z",
    "updated_at": "2024-01-10T10:00:00Z"
  }
]
```

---

### 11. Ajouter une Image à un Livre
**POST** `/{id}/add_image/`

Ajoute une nouvelle image à un livre.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Payload (FormData):**
| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `image` | File | ✅ | Fichier image |
| `type` | string | ✅ | `cover_front`, `cover_back`, `content`, `other` |
| `is_main_cover` | boolean | ❌ | Définir comme couverture principale (défaut: false) |
| `order` | integer | ❌ | Ordre d'affichage (défaut: 0) |
| `alt_text` | string | ❌ | Texte alternatif pour l'accessibilité |

**Réponse (201 CREATED):**
```json
{
  "message": "Image ajoutée",
  "image": {
    "id": 5,
    "book": 1,
    "image": "/media/books/python-pour-les-debutants/images/new-image.jpg",
    "image_url": "http://127.0.0.1:8000/media/books/python-pour-les-debutants/images/new-image.jpg",
    "type": "cover_front",
    "type_display": "Couverture (1ère page)",
    "is_main_cover": true,
    "order": 0,
    "alt_text": "Couverture principale",
    "created_at": "2024-01-20T15:30:00Z",
    "updated_at": "2024-01-20T15:30:00Z"
  }
}
```

---

### 12. Supprimer une Image
**DELETE** `/{id}/images/{image_id}/`

Supprime une image spécifique d'un livre.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Réponse (204 NO CONTENT):**
```json
{
  "message": "Image supprimée"
}
```

**Erreur - Image non trouvée (404):**
```json
{
  "error": "Image non trouvée"
}
```

---

## 🎥 Endpoints Vidéos

### 13. Lister les Vidéos d'un Livre
**GET** `/{id}/videos/`

Récupère toutes les vidéos associées à un livre.

**Permissions:** Public

**Réponse (200 OK):**
```json
[
  {
    "id": 1,
    "book": 1,
    "video_url": "https://www.youtube.com/watch?v=abc123",
    "title": "Présentation du livre",
    "description": "Découvrez le contenu du livre...",
    "order": 0,
    "created_at": "2024-01-10T10:00:00Z",
    "updated_at": "2024-01-10T10:00:00Z"
  }
]
```

---

### 14. Ajouter une Vidéo à un Livre
**POST** `/{id}/add_video/`

Ajoute une vidéo YouTube ou Vimeo à un livre.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Payload:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=xyz789",
  "title": "Tutoriel chapitre 1",
  "description": "Explication détaillée du premier chapitre",
  "order": 1
}
```

**Réponse (201 CREATED):**
```json
{
  "message": "Vidéo ajoutée",
  "video": {
    "id": 2,
    "book": 1,
    "video_url": "https://www.youtube.com/watch?v=xyz789",
    "title": "Tutoriel chapitre 1",
    "description": "Explication détaillée du premier chapitre",
    "order": 1,
    "created_at": "2024-01-20T15:30:00Z",
    "updated_at": "2024-01-20T15:30:00Z"
  }
}
```

**Erreur - URL invalide (400):**
```json
{
  "video_url": ["L'URL doit être YouTube ou Vimeo"]
}
```

---

### 15. Supprimer une Vidéo
**DELETE** `/{id}/videos/{video_id}/`

Supprime une vidéo d'un livre.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Réponse (204 NO CONTENT):**
```json
{
  "message": "Vidéo supprimée"
}
```

**Erreur - Vidéo non trouvée (404):**
```json
{
  "error": "Vidéo non trouvée"
}
```

---

## 🖼️ Gestion Directe des Images (BookImageViewSet)

> **Note:** Ces endpoints permettent une gestion directe des images sans passer par un livre spécifique.

### 16. Lister Toutes les Images
**GET** `/images/`

Récupère la liste de toutes les images de tous les livres.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Réponse (200 OK):**
```json
{
  "count": 45,
  "next": "http://127.0.0.1:8000/api/v1/books/images/?page=2",
  "previous": null,
  "results": [...]
}
```

---

### 17. Créer une Image Directement
**POST** `/images/`

Crée une image directement sans passer par un livre.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Payload (FormData):**
| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `book` | integer | ✅ | ID du livre |
| `image` | File | ✅ | Fichier image |
| `type` | string | ✅ | Type d'image |
| `is_main_cover` | boolean | ❌ | Couverture principale |
| `order` | integer | ❌ | Ordre d'affichage |
| `alt_text` | string | ❌ | Texte alternatif |

**Réponse (201 CREATED):** Même format que endpoint 11

---

### 18. Récupérer une Image
**GET** `/images/{image_id}/`

Obtient les détails d'une image spécifique.

**Permissions:** Authentifié (Admin seulement)

**Réponse (200 OK):** Même format que endpoint 10

---

### 19. Mettre à Jour une Image (Complète)
**PUT** `/images/{image_id}/`

Met à jour complètement une image.

**Permissions:** Authentifié (Admin seulement)

**Payload:** Même structure que POST (avec `book` requis)

---

### 20. Mettre à Jour une Image (Partielle)
**PATCH** `/images/{image_id}/`

Met à jour partiellement une image.

**Permissions:** Authentifié (Admin seulement)

**Payload (exemple):**
```json
{
  "is_main_cover": true,
  "order": 2
}
```

---

### 21. Supprimer une Image
**DELETE** `/images/{image_id}/`

Supprime une image complètement.

**Permissions:** Authentifié (Admin seulement)

**Réponse (204 NO CONTENT)**

---

### 22. Définir comme Couverture Principale
**POST** `/images/{image_id}/set_main_cover/`

Définit une image comme couverture principale du livre. Les autres images du même livre perdent ce statut automatiquement.

**Permissions:** Authentifié (Admin seulement)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Réponse (200 OK):**
```json
{
  "message": "Image définie comme couverture principale",
  "image": {
    "id": 3,
    "book": 1,
    "image_url": "http://127.0.0.1:8000/media/books/python-pour-les-debutants/images/cover.jpg",
    "type": "cover_front",
    "is_main_cover": true,
    "order": 0,
    "alt_text": "Couverture principale",
    "created_at": "2024-01-10T10:00:00Z",
    "updated_at": "2024-01-20T16:00:00Z"
  }
}
```

---

## 🎥 Gestion Directe des Vidéos (BookVideoViewSet)

> **Note:** Opérations CRUD complètes sur les vidéos sans passer par un livre.

### 23. Lister Toutes les Vidéos
**GET** `/videos/`

Récupère la liste de toutes les vidéos.

**Permissions:** Authentifié (Admin seulement)

---

### 24. Créer une Vidéo Directement
**POST** `/videos/`

Crée une vidéo directement.

**Permissions:** Authentifié (Admin seulement)

**Payload:**
```json
{
  "book": 1,
  "video_url": "https://www.youtube.com/watch?v=test",
  "title": "Vidéo de présentation",
  "description": "Présentation du livre",
  "order": 0
}
```

---

### 25. Récupérer une Vidéo
**GET** `/videos/{video_id}/`

Obtient les détails d'une vidéo spécifique.

**Permissions:** Authentifié (Admin seulement)

---

### 26. Mettre à Jour une Vidéo
**PUT/PATCH** `/videos/{video_id}/`

Met à jour une vidéo.

**Permissions:** Authentifié (Admin seulement)

---

### 27. Supprimer une Vidéo
**DELETE** `/videos/{video_id}/`

Supprime une vidéo complètement.

**Permissions:** Authentifié (Admin seulement)

---

## 🔐 Résumé des Permissions

| Endpoint | Méthode | Permission |
|----------|---------|------------|
| Lister/Détails livres | GET | Public |
| Créer/Modifier/Supprimer livres | POST/PUT/PATCH/DELETE | Admin ✅ |
| Lister/Détails images (par livre) | GET | Public |
| Ajouter/Supprimer images (par livre) | POST/DELETE | Admin ✅ |
| Gestion directe images | CRUD | Admin ✅ |
| Lister/Détails vidéos (par livre) | GET | Public |
| Ajouter/Supprimer vidéos (par livre) | POST/DELETE | Admin ✅ |
| Gestion directe vidéos | CRUD | Admin ✅ |

---

## 💡 Exemples cURL

### Lister les livres
```bash
curl -X GET http://127.0.0.1:8000/api/v1/books/ \
  -H "Content-Type: application/json"
```

### Lister les livres avec filtres
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/books/?search=python&in_stock=true&ordering=-sales_count" \
  -H "Content-Type: application/json"
```

### Récupérer un livre
```bash
curl -X GET http://127.0.0.1:8000/api/v1/books/1/ \
  -H "Content-Type: application/json"
```

### Créer un livre
```bash
curl -X POST http://127.0.0.1:8000/api/v1/books/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "titre": "Django Avancé",
    "nom": "Marie Martin",
    "description": "Techniques avancées de Django...",
    "legende": "Pour développeurs expérimentés",
    "prix": 3500,
    "code_bare": "9782987654321",
    "nombre_pages": 450,
    "largeur_cm": "16.00",
    "hauteur_cm": "24.00",
    "epaisseur_cm": "3.00",
    "poids_grammes": 600,
    "date_publication": "2024-02-01",
    "editeur": "Éditions Web",
    "langue": "Français",
    "quantites": 20,
    "seo_title": "Django Avancé - Maîtrisez le framework",
    "seo_description": "Guide complet Django pour experts",
    "is_active": true,
    "is_featured": false
  }'
```

### Mettre à jour le stock
```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/books/1/update_stock/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "quantites": 50
  }'
```

### Ajouter une image
```bash
curl -X POST http://127.0.0.1:8000/api/v1/books/1/add_image/ \
  -H "Authorization: Bearer <access_token>" \
  -F "image=@/path/to/image.jpg" \
  -F "type=cover_front" \
  -F "is_main_cover=true" \
  -F "alt_text=Couverture principale"
```

### Ajouter une vidéo
```bash
curl -X POST http://127.0.0.1:8000/api/v1/books/1/add_video/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=abc123",
    "title": "Présentation du livre",
    "description": "Découvrez le contenu...",
    "order": 0
  }'
```

### Lister les images d'un livre
```bash
curl -X GET http://127.0.0.1:8000/api/v1/books/1/images/ \
  -H "Content-Type: application/json"
```

### Définir une image comme couverture principale
```bash
curl -X POST http://127.0.0.1:8000/api/v1/books/images/5/set_main_cover/ \
  -H "Authorization: Bearer <access_token>"
```

---

## 📋 Notes Importantes

1. **Prix:** Toujours en centimes (ex: 2500 = 25,00€)
   - Propriété `prix_euros` convertit automatiquement

2. **Slug:** Généré automatiquement depuis le titre
   - Format: `slugify(titre)`
   - Unique et indexé pour les performances

3. **Vues:** Compteur incrémenté automatiquement
   - Seulement pour les utilisateurs non-authentifiés ou non-staff
   - Incrémenté à chaque appel `GET /{id}/`

4. **Couverture Principale:** Une seule par livre
   - Gestion automatique lors de la création/modification
   - Les anciennes sont automatiquement désactivées

5. **Vidéos:** Uniquement YouTube et Vimeo
   - Validation sur `video_url`
   - Domaines acceptés: `youtube.com`, `youtu.be`, `vimeo.com`

6. **Stock:** `in_stock` calculé automatiquement
   - `in_stock = quantites > 0`

7. **Images:** Stockage hiérarchisé
   - Chemin: `books/{slug}/images/{filename}`
   - Permet une organisation claire des fichiers

---

## 🚨 Codes de Statut HTTP

| Code | Description |
|------|-------------|
| 200 | Requête réussie |
| 201 | Ressource créée |
| 204 | Succès sans contenu (DELETE) |
| 400 | Erreur de validation |
| 401 | Non authentifié |
| 403 | Authentifié mais permissions insuffisantes |
| 404 | Ressource non trouvée |
| 500 | Erreur serveur |
