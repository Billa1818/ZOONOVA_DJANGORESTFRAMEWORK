# Guide de Déploiement ZOONOVA sur VPS

## 📋 Prérequis

- VPS Linux (Ubuntu 20.04+ recommandé)
- Accès SSH en tant qu'utilisateur avec sudo
- Domaine `api.zoonova.fr` configuré
- Port 80 disponible

## 🚀 Installation Rapide

### 1. Connectez-vous au VPS

```bash
ssh user@your-vps-ip
```

### 2. Téléchargez et exécutez le script de déploiement

```bash
curl -O https://raw.githubusercontent.com/Billa1818/ZOONOVA_DJANGORESTFRAMEWORK/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

### 3. Configurez les variables d'environnement

Le script crée `/home/zoonova/zoonova/.env`. Éditez-le:

```bash
nano /home/zoonova/zoonova/.env
```

**Éléments à configurer:**

```env
# ⚠️ IMPORTANT - Générer une nouvelle clé secrète
SECRET_KEY=your-unique-secret-key

# Domaine
ALLOWED_HOSTS=api.zoonova.fr,localhost

# CORS - Domaines autorisés
CORS_ALLOWED_ORIGINS=https://zoonova.fr,http://zoonova.fr

# Email SMTP
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=app-specific-password

# Stripe (optionnel)
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
```

### 4. Générez une SECRET_KEY sécurisée

```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 5. Démarrez les services

```bash
cd /home/zoonova/zoonova
sudo docker-compose up -d
```

## 🔧 Configuration du Domaine

### Option 1: Avec DNS (recommandé)

1. Allez chez votre registrar de domaine
2. Créez un enregistrement A:
   - Host: `api`
   - Value: `VPS_IP_ADDRESS`

### Option 2: Sans DNS (test local)

Ajoutez au fichier `/etc/hosts` sur votre machine locale:
```
VPS_IP api.zoonova.fr
```

## 🔐 Configuration SSL/TLS (HTTPS)

⚠️ Actuellement configuré en HTTP. Pour HTTPS, installez Certbot:

```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Générez un certificat (remplacez par votre email)
sudo certbot certonly --standalone -d api.zoonova.fr -d zoonova.fr --email zoonova@outlook.fr
```

Puis modifiez `nginx.conf`:

```nginx
server {
    listen 80; 
    server_name api.zoonova.fr;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.zoonova.fr;
    
    ssl_certificate /etc/letsencrypt/live/api.zoonova.fr/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.zoonova.fr/privkey.pem;
    
    # ... reste de la config ...
}
```

Redémarrez nginx:
```bash
sudo docker-compose restart nginx
```

## 📊 Gestion des Services

### Voir les logs

```bash
# Tous les services
sudo docker-compose logs -f

# Django uniquement
sudo docker-compose logs -f web

# Nginx uniquement
sudo docker-compose logs -f nginx
```

### Redémarrer

```bash
sudo docker-compose restart
```

### Arrêter

```bash
sudo docker-compose down
```

### Voir le statut

```bash
sudo docker-compose ps
```

## 🗄️ Base de Données SQLite

La base de données SQLite est stockée dans:
```
/home/zoonova/zoonova/db.sqlite3
```

**Sauvegarde:**
```bash
sudo cp /home/zoonova/zoonova/db.sqlite3 /home/zoonova/zoonova/db.sqlite3.backup
```

**Restauration:**
```bash
sudo cp /home/zoonova/zoonova/db.sqlite3.backup /home/zoonova/zoonova/db.sqlite3
sudo docker-compose restart web
```

## 📁 Structure des Fichiers

```
/home/zoonova/
└── zoonova/
    ├── .env              # Variables d'environnement (production)
    ├── docker-compose.yml
    ├── Dockerfile
    ├── nginx.conf
    ├── db.sqlite3        # Base de données
    ├── staticfiles/      # Fichiers CSS/JS compilés
    ├── media/            # Uploads utilisateurs
    ├── logs/             # Logs application
    └── ... (code source)
```

## 🧪 Tester l'API

```bash
# Health check
curl http://api.zoonova.fr/

# Voir les logs temps réel
sudo docker-compose logs -f web
```

## ⚙️ Migration des Données

Les migrations sont exécutées automatiquement au démarrage. Pour les exécuter manuellement:

```bash
sudo docker-compose exec web python manage.py migrate
```

## 📈 Performance

### Autoscaling (Workers Gunicorn)

Modifiez `Dockerfile`:
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "8", "--timeout", "120", "zoonova.wsgi:application"]
```

Nombre de workers recommandé: `2 × CPU_COUNT + 1`

### Limite de Taille des Uploads

Modifiez `nginx.conf`:
```nginx
client_max_body_size 100M;  # Par défaut: 50M
```

## 🚨 Troubleshooting

### L'API ne répond pas

```bash
# Vérifier les erreurs
sudo docker-compose logs web

# Redémarrer
sudo docker-compose restart web
```

### Erreur 502 (Bad Gateway)

```bash
# Vérifier la connexion Django
sudo docker-compose logs web

# Vérifier Nginx
sudo docker-compose logs nginx

# Redémarrer tout
sudo docker-compose down
sudo docker-compose up -d
```

### Fichiers statiques manquants

```bash
# Régénérer
sudo docker-compose exec web python manage.py collectstatic --noinput

# Redémarrer nginx
sudo docker-compose restart nginx
```

### Erreur de permission

```bash
# Corriger les permissions
sudo chown -R 1000:1000 /home/zoonova/zoonova/staticfiles
sudo chown -R 1000:1000 /home/zoonova/zoonova/media
```

## 🔄 Mise à Jour du Code

```bash
cd /home/zoonova/zoonova
git pull origin main
sudo docker-compose build
sudo docker-compose up -d
```

## 📞 Support

Pour les problèmes, consultez les logs:
```bash
sudo docker-compose logs -f
```

## ✅ Checklist Déploiement

- [ ] VPS configuré avec Docker et Docker Compose
- [ ] Code cloné du repository
- [ ] Fichier `.env` configuré avec SECRET_KEY
- [ ] Paramètres email configurés
- [ ] Domaine `api.zoonova.fr` pointant vers le VPS
- [ ] Conteneurs Docker en cours d'exécution
- [ ] API accessible sur `http://api.zoonova.fr`
- [ ] Certificat SSL configuré (optionnel pour HTTPS)
- [ ] Sauvegardes de la base de données en place
