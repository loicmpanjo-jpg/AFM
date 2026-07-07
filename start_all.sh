#!/bin/bash

# Lancer les migrations de base de données
echo "Running migrations..."
alembic upgrade head

# Lancer le Worker en arrière-plan
echo "Starting background worker..."
python -m event_bus.worker &

# Lancer l'API Gateway au premier plan
echo "Starting API Gateway..."
uvicorn api_gateway.main:app --host 0.0.0.0 --port $PORT
