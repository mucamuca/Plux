# Plux

Downloader de vídeos com suporte a **YouTube**, **TikTok** e **Instagram** (incluindo Stories).

Interface web com tema escuro, seleção de qualidade (360p até 4K), histórico de downloads e estatísticas.

## Como funciona

O projeto é dividido em duas partes:

- **`plux-frontend/`** — Interface web (HTML, CSS, JS) hospedada no [Vercel](https://vercel.com)
- **`plux-api/`** — API Python com Flask + yt-dlp hospedada no [Render](https://render.com)

O frontend envia a URL do vídeo para a API. A API usa o yt-dlp para extrair o link direto do vídeo e devolve para o navegador, que inicia o download automaticamente.

## Funcionalidades

- Download de vídeos do YouTube, TikTok e Instagram
- Download de Stories do Instagram
- Seleção de qualidade (360p, 480p, 720p, 1080p, 4K)
- Detecção automática da plataforma pela URL
- Histórico de downloads (salvo no navegador)
- Contador de downloads por plataforma

## Deploy

### Backend (Render)

1. No [Render](https://render.com), crie um **Web Service** conectado a este repositório
2. Defina o **Root Directory** como `plux-api`
3. O Render vai detectar o `render.yaml` e configurar tudo automaticamente
4. Após o deploy, copie a URL gerada (ex: `https://plux-api-xxxx.onrender.com`)
5. Adicione a variável de ambiente `FRONTEND_URL` com a URL do Vercel (passo seguinte)

### Frontend (Vercel)

1. No [Vercel](https://vercel.com), importe este repositório
2. Defina o **Root Directory** como `plux-frontend`
3. Framework Preset: **Other**
4. Antes do deploy, edite `plux-frontend/script.js` e coloque a URL do Render na variável `API_URL` (linha 7)
5. Faça o deploy

### Conectando os dois

| Onde | Variável | Valor |
|------|----------|-------|
| `plux-frontend/script.js` | `API_URL` | URL do Render |
| Render (Environment) | `FRONTEND_URL` | URL do Vercel |

## Tecnologias

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask, yt-dlp, Gunicorn
- **Hospedagem:** Vercel (frontend) + Render (backend)

## Licença

[MIT](LICENSE)
