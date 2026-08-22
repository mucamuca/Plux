#!/usr/bin/env bash
set -u

LOG=/tmp/pot.log
: > "$LOG"

# Sobe o gerador de PO Token antes da API. Sem ele o YouTube devolve
# metadados mas retem as URLs de midia.
{
  echo "== procurando o servidor do provider =="
  find /opt/bgutil -name "*.js" -path "*server*" \
       \( -path "*build*" -o -path "*dist*" \) 2>/dev/null | head -20
  echo "== conteudo de /opt/bgutil/server =="
  ls -la /opt/bgutil/server 2>&1 | head -20
} >> "$LOG" 2>&1

MAIN=""
for p in \
  /opt/bgutil/server/build/main.js \
  /opt/bgutil/server/dist/main.js \
  /opt/bgutil/server/build/index.js \
  /opt/bgutil/server/dist/index.js
do
  if [ -f "$p" ]; then MAIN="$p"; break; fi
done

if [ -z "$MAIN" ]; then
  MAIN=$(find /opt/bgutil -name "main.js" \( -path "*build*" -o -path "*dist*" \) 2>/dev/null | head -1)
fi

if [ -n "$MAIN" ]; then
  echo "== iniciando: node $MAIN ==" >> "$LOG"
  node "$MAIN" >> "$LOG" 2>&1 &
  sleep 5
  if curl -s -m 3 http://127.0.0.1:4416/ping > /dev/null 2>&1; then
    echo "== provider respondendo na 4416 ==" >> "$LOG"
  else
    echo "== provider NAO respondeu na 4416 ==" >> "$LOG"
  fi
else
  echo "== nenhum main.js encontrado ==" >> "$LOG"
fi

exec gunicorn app:app \
  --bind "0.0.0.0:${PORT:-10000}" \
  --workers 1 \
  --threads 8 \
  --timeout 600
