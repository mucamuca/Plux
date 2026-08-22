FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# ffmpeg para juntar video+audio e converter MP3; node para o gerador de PO Token
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg git curl ca-certificates gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# O yt-dlp usa Deno para resolver o desafio "n" das assinaturas do YouTube.
# Sem ele os formatos de midia sao descartados.
RUN curl -fsSL https://deno.land/install.sh | DENO_INSTALL=/usr/local sh -s -- --yes \
    && deno --version

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Servidor que gera o Proof of Origin Token exigido pelo YouTube.
# O plugin bgutil no yt-dlp consulta http://127.0.0.1:4416 por padrao.
RUN git clone --depth 1 https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git /opt/bgutil \
    && cd /opt/bgutil/server \
    && npm install --no-audit --no-fund \
    && npx tsc \
    && npm cache clean --force

COPY . .

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
