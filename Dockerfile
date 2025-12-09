# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements et installer les dépendances Python
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système pour le runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copier les dépendances Python depuis le builder
COPY --from=builder /root/.local /root/.local

# Copier le projet
COPY . .

# Créer les dossiers nécessaires
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Exposer le port
EXPOSE 8000

# Variables d'environnement
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Commande de démarrage
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "zoonova.wsgi:application"]
