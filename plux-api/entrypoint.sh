#!/usr/bin/env bash
set -u

# Sobe o gerador de PO Token antes da API. Sem ele o YouTube devolve
# metadados mas retem as URLs de midia.
MAIN=$(find /opt/bgutil/server -name "main.js" -path "*build*" 2>/dev/null | head -1)

if [ -n "$MAIN" ]; then
  echo "[plux] PO Token provider: $MAIN"
  node "$MAIN" --port 4416 &
else
  echo "[plux] AVISO: PO Token provider nao encontrado; YouTube pode falhar"
fi

exec gunicorn app:app \
  --bind "0.0.0.0:${PORT:-10000}" \
  --workers 1 \
  --threads 8 \
  --timeout 600
