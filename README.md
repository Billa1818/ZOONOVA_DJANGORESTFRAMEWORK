# ZOONOVA_DJANGORESTFRAMEWORK
# Guide d'Installation - zoonova API

## 📋 Structure du Projet

```
zoonova/
├── zoonova/              # Configuration principale
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── utils.py
├── accounts/              # Gestion des admins & Auth JWT
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── books/                 # Catalogue de livres
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── media/                 # Images et vidéos des livres
│   ├── models.py
│   ├── serializers.py
│   └── (gestion via books/)
├── orders/                # Commandes
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── utils.py           # Génération PDF
├── payments/              # Intégration Stripe
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── contact/               # Messages de contact
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── templates/
│   └── emails/            # Templates d'emails
│       ├── base.html
│       ├── order_confirmation.html
│       ├── admin_new_order.html
│       ├── password_reset.html
│       └── admin_invitation.html
├── static/
├── media/
├── logs/
├── manage.py
├── requirements.txt
└── .env
```

## 🚀 Installation

### 1. Cloner et créer l'environnement virtuel

```bash
# Créer le dossier projet
mkdir zoonova && cd zoonova

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Sur Windows
venv\Scripts\activate
# Sur Mac/Linux
source venv/bin/activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configuration de stipe 

```text
  install stripe-cli  sur votre machin et lancer cette commande : -> 
  
   stripe listen --forward-to 192.168.10.238:8000/api/v1/payments/webhook/
   
\q
```

### 4. Configuration des variables d'environnement

Créer un fichier `.env` à la racine :

```env
SECRET_KEY=votre-cle-secrete-django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
FRONTEND_URL=http://localhost:3000

DB_NAME=zoonova_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

EMAIL_HOST=localhost
EMAIL_PORT=1025
EMAIL_USE_TLS=False
DEFAULT_FROM_EMAIL=noreply@zoonova.com

ADMIN_NOTIFICATION_EMAILS=admin@zoonova.com

STRIPE_SECRET_KEY=sk_test_votre_cle
STRIPE_PUBLISHABLE_KEY=pk_test_votre_cle
STRIPE_WEBHOOK_SECRET=whsec_votre_secret
STRIPE_SUCCESS_URL=http://localhost:3000/success
STRIPE_CANCEL_URL=http://localhost:3000/cancel
```

### 5. Migrations et création du superuser

```bash
# Créer les migrations
python manage.py makemigrations accounts books media orders payments contact

# Appliquer les migrations
python manage.py migrate

# Créer le superuser
python manage.py createsuperuser
```

### 6. Installer et démarrer MailHog (pour les emails en local)

```bash
# Sur Mac avec Homebrew
brew install mailhog
mailhog

# Sur Linux
wget https://github.com/mailhog/MailHog/releases/download/v1.0.1/MailHog_linux_amd64
chmod +x MailHog_linux_amd64
./MailHog_linux_amd64

# Sur Windows - télécharger depuis
# https://github.com/mailhog/MailHog/releases

# MailHog sera accessible sur http://localhost:8025
```

### 7. Démarrer le serveur

```bash
python manage.py runserver
```

L'API sera accessible sur `http://localhost:8000`

## 📡 Endpoints API

### Authentication (JWT)

```
POST   /api/v1/auth/login/                    # Connexion (obtenir tokens)
POST   /api/v1/auth/token/refresh/            # Rafraîchir le token
POST   /api/v1/auth/set-password/             # Définir mot de passe (1ère connexion)
POST   /api/v1/auth/password-reset/request/   # Demander réinitialisation
POST   /api/v1/auth/password-reset/confirm/   # Confirmer réinitialisation
GET    /api/v1/auth/admins/me/                # Profil utilisateur connecté
POST   /api/v1/auth/admins/change_password/   # Changer son mot de passe
```

### Admins (superuser uniquement)

```
GET    /api/v1/auth/admins/                   # Liste des admins
POST   /api/v1/auth/admins/                   # Créer un admin
GET    /api/v1/auth/admins/{id}/              # Détails d'un admin
PATCH  /api/v1/auth/admins/{id}/              # Modifier un admin
DELETE /api/v1/auth/admins/{id}/              # Supprimer un admin
POST   /api/v1/auth/admins/{id}/toggle_active/ # Activer/désactiver
```

### Books (Public GET, Admin POST/PUT/DELETE)

```
GET    /api/v1/books/                         # Liste des livres
POST   /api/v1/books/                         # Créer un livre (admin)
GET    /api/v1/books/{id}/                    # Détails d'un livre
PATCH  /api/v1/books/{id}/                    # Modifier un livre (admin)
DELETE /api/v1/books/{id}/                    # Supprimer un livre (admin)
PATCH  /api/v1/books/{id}/update_stock/       # Mettre à jour le stock
POST   /api/v1/books/{id}/toggle_featured/    # Mise en avant
POST   /api/v1/books/{id}/toggle_active/      # Activer/désactiver
GET    /api/v1/books/{id}/images/             # Images du livre
POST   /api/v1/books/{id}/add_image/          # Ajouter une image
DELETE /api/v1/books/{id}/images/{image_id}/  # Supprimer une image
GET    /api/v1/books/{id}/videos/             # Vidéos du livre
POST   /api/v1/books/{id}/add_video/          # Ajouter une vidéo
DELETE /api/v1/books/{id}/videos/{video_id}/  # Supprimer une vidéo
```

### Orders

```
GET    /api/v1/orders/                        # Liste des commandes (admin)
POST   /api/v1/orders/                        # Créer une commande (public)
GET    /api/v1/orders/{id}/                   # Détails d'une commande
PATCH  /api/v1/orders/{id}/update_status/     # Mettre à jour le statut
GET    /api/v1/orders/{id}/invoice/           # Télécharger la facture PDF
GET    /api/v1/orders/statistics/             # Statistiques (admin)
GET    /api/v1/orders/countries/              # Liste des pays (public)
```

### Payments (Stripe)

```
POST   /api/v1/payments/create-checkout/      # Créer session Stripe Checkout
POST   /api/v1/payments/webhook/              # Webhook Stripe
GET    /api/v1/payments/verify/               # Vérifier statut paiement
GET    /api/v1/payments/stripe/               # Liste des paiements (admin)
```

### Contact

```
POST   /api/v1/contact/messages/              # Envoyer un message (public)
GET    /api/v1/contact/messages/              # Liste des messages (admin)
GET    /api/v1/contact/messages/{id}/         # Détails d'un message
POST   /api/v1/contact/messages/{id}/mark_as_read/     # Marquer comme lu
POST   /api/v1/contact/messages/{id}/mark_as_replied/  # Marquer comme répondu
GET    /api/v1/contact/messages/statistics/   # Statistiques
```

## 🔐 Flux d'Authentification

### 1. Création d'un Admin par le Superuser

```bash
POST /api/v1/auth/admins/
{
  "email": "nouvel.admin@zoonova.com",
  "first_name": "Jean",
  "last_name": "Dupont",
  "is_staff": true,
  "is_superuser": false
}
```

→ L'admin reçoit un email d'invitation

### 2. Première Connexion de l'Admin

```bash
POST /api/v1/auth/login/
{
  "email": "nouvel.admin@zoonova.com",
  "password": "any"
}
```

→ Retourne une erreur `first_login` demandant de définir le mot de passe

### 3. Définir le Mot de Passe

```bash
POST /api/v1/auth/set-password/
{
  "email": "nouvel.admin@zoonova.com",
  "password": "MonMotDePasse123!",
  "password_confirm": "MonMotDePasse123!",
  "first_name": "Jean",
  "last_name": "Dupont"
}
```

→ Retourne les tokens JWT

### 4. Connexions Suivantes

```bash
POST /api/v1/auth/login/
{
  "email": "nouvel.admin@zoonova.com",
  "password": "MonMotDePasse123!"
}
```

→ Retourne les tokens JWT

## 📧 Configuration Email (Production)

Pour la production, remplacer MailHog par un vrai service SMTP :

```env
# Exemple avec Gmail
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre.email@gmail.com
EMAIL_HOST_PASSWORD=votre_mot_de_passe_app
```

## 🔧 Commandes Utiles

```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superuser
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic

# Démarrer le serveur
python manage.py runserver

# Shell Django
python manage.py shell

# Lancer les tests
pytest
```

## 📦 Déploiement

### Checklist Production

1. ✅ Définir `DEBUG=False`
2. ✅ Configurer `ALLOWED_HOSTS`
3. ✅ Utiliser un vrai serveur SMTP
4. ✅ Configurer Stripe en mode production
5. ✅ Sécuriser les variables d'environnement
6. ✅ Configurer un serveur web (Nginx)
7. ✅ Utiliser Gunicorn comme serveur WSGI
8. ✅ Configurer les certificats SSL
9. ✅ Mettre en place les backups de la BDD

### Exemple Gunicorn

```bash
pip install gunicorn
gunicorn zoonova.wsgi:application --bind 0.0.0.0:8000
```

## 🐛 Dépannage

### Erreur de connexion PostgreSQL

```bash
# Vérifier que PostgreSQL est démarré
sudo service postgresql status

# Redémarrer PostgreSQL
sudo service postgresql restart
```

### Problème d'emails

```bash
# Vérifier que MailHog est démarré
# Accéder à http://localhost:8025

# Voir les logs Django pour les erreurs SMTP
tail -f logs/zoonova.log
```

### Erreur JWT

```bash
# Vérifier que simplejwt est bien installé
pip show djangorestframework-simplejwt

# Réinstaller si nécessaire
pip install --upgrade djangorestframework-simplejwt
```

## 📚 Documentation Supplémentaire

- Django REST Framework: https://www.django-rest-framework.org/
- Django Simple JWT: https://django-rest-framework-simplejwt.readthedocs.io/
- Stripe API: https://stripe.com/docs/api
- ReportLab: https://www.reportlab.com/documentation/

