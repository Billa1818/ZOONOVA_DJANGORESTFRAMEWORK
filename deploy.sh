#!/bin/bash

# Script de déploiement ZOONOVA sur VPS
# À exécuter une fois connecté au VPS

set -e

echo "🚀 Déploiement ZOONOVA sur VPS"
echo "================================"

# Variables
REPO_URL="https://github.com/Billa1818/ZOONOVA_DJANGORESTFRAMEWORK"
DEPLOY_DIR="/home/zoonova"
PROJECT_DIR="$DEPLOY_DIR/zoonova"

# Vérifications préalables
echo "✅ Vérification des prérequis..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Installation en cours..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Installation en cours..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Créer le répertoire de déploiement
echo "📁 Création des répertoires..."
sudo mkdir -p $DEPLOY_DIR
sudo chown $USER:$USER $DEPLOY_DIR

# Cloner ou mettre à jour le repo
echo "📥 Téléchargement du projet..."
if [ -d "$PROJECT_DIR" ]; then
    cd $PROJECT_DIR
    git pull origin main
else
    git clone $REPO_URL $PROJECT_DIR
    cd $PROJECT_DIR
fi

# Copier le fichier .env
echo "⚙️  Configuration des variables d'environnement..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    cp $PROJECT_DIR/.env.production $PROJECT_DIR/.env
    echo "⚠️  Veuillez éditer $PROJECT_DIR/.env et configurer:"
    echo "   - SECRET_KEY (générez une clé secrète)"
    echo "   - Paramètres email"
    echo "   - Clés Stripe (optionnel)"
    read -p "Appuyez sur Entrée après configuration..."
fi

# Générer une SECRET_KEY si nécessaire
if grep -q "your-secret-key-here" "$PROJECT_DIR/.env"; then
    echo "🔐 Génération de la SECRET_KEY..."
    SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    sed -i "s/SECRET_KEY=your-secret-key-here-change-this/SECRET_KEY=$SECRET_KEY/" "$PROJECT_DIR/.env"
fi

# Démarrer les conteneurs
echo "🐳 Démarrage des conteneurs Docker..."
cd $PROJECT_DIR
sudo docker-compose down 2>/dev/null || true
sudo docker-compose build
sudo docker-compose up -d

# Vérifier le statut
echo ""
echo "✅ Déploiement terminé!"
echo ""
echo "📊 Statut des conteneurs:"
sudo docker-compose ps

echo ""
echo "📝 Informations importantes:"
echo "   - API accessible sur: http://api.zoonova.fr"
echo "   - Statut des logs: sudo docker-compose logs -f"
echo "   - Redémarrer: sudo docker-compose restart"
echo "   - Arrêter: sudo docker-compose down"
echo ""
echo "⚠️  IMPORTANT - À faire manuellement:"
echo "   1. Configurer le domaine DNS pour api.zoonova.fr"
echo "   2. Configurer un certificat SSL avec Certbot (pour HTTPS)"
echo "   3. Configurer le firewall pour ouvrir le port 80"
echo ""
