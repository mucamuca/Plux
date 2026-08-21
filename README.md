<div align="center">

# 🎬 Plux

**Downloader de vídeos multiplataforma**

[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](#)
[![TikTok](https://img.shields.io/badge/TikTok-00F2EA?style=for-the-badge&logo=tiktok&logoColor=black)](#)
[![Instagram](https://img.shields.io/badge/Instagram-E1306C?style=for-the-badge&logo=instagram&logoColor=white)](#)

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](#)
[![Flask](https://img.shields.io/badge/Flask-API-000000?style=flat-square&logo=flask&logoColor=white)](#)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](#licença)

<img src="plux-frontend/plux-cat.gif" width="120" alt="Plux mascot">

*Baixe vídeos do YouTube, TikTok e Instagram (incluindo Stories) com seleção de qualidade de 360p até 4K.*

---

</div>

## ⚡ Funcionalidades

| Recurso | Descrição |
|---------|-----------|
| 🎥 **Multi-plataforma** | YouTube, TikTok e Instagram em um só lugar |
| 📸 **Instagram Stories** | Baixe Stories direto pela URL |
| 🎚️ **Qualidade** | Escolha entre 360p, 480p, 720p, 1080p e 4K |
| 🔍 **Detecção automática** | Reconhece a plataforma pela URL colada |
| 📊 **Estatísticas** | Contador de downloads por plataforma |
| 📋 **Histórico** | Últimos 20 downloads salvos no navegador |
| 🌙 **Tema escuro** | Interface dark mode |

## 🏗️ Arquitetura

```
┌──────────────────┐         fetch /api/*         ┌──────────────────┐
│                  │  ──────────────────────────►  │                  │
│  plux-frontend   │                               │    plux-api      │
│  (Vercel)        │  ◄──────────────────────────  │    (Render)      │
│                  │         JSON response         │                  │
│  HTML/CSS/JS     │                               │  Flask + yt-dlp  │
└──────────────────┘                               └──────────────────┘
```

O frontend envia a URL do vídeo para a API → a API extrai o link direto com **yt-dlp** → o navegador inicia o download.

## 📁 Estrutura

```
Plux/
├── plux-frontend/          # Interface web (Vercel)
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   ├── plux-cat.gif
│   └── vercel.json
│
├── plux-api/               # API Python (Render)
│   ├── app.py
│   ├── requirements.txt
│   ├── render.yaml
│   └── .gitignore
│
├── README.md
└── LICENSE
```

## 🚀 Deploy

### 1. Backend no Render

1. Acesse [render.com](https://render.com) e faça login com o GitHub
2. **New +** → **Web Service** → conecte este repositório
3. **Root Directory:** `plux-api`
4. O `render.yaml` configura tudo automaticamente — escolha o plano **Free**
5. Após o deploy, copie a URL gerada (ex: `https://plux-api-xxxx.onrender.com`)

### 2. Frontend no Vercel

1. Acesse [vercel.com](https://vercel.com) e faça login com o GitHub
2. **Add New...** → **Project** → importe este repositório
3. **Root Directory:** `plux-frontend`
4. **Framework Preset:** Other
5. Clique em **Deploy**

### 3. Conectando os dois

| Onde | Variável | Valor |
|:----:|:--------:|:-----:|
| `plux-frontend/script.js` (linha 7) | `API_URL` | URL do Render |
| Render → Environment | `FRONTEND_URL` | URL do Vercel |

> ⚠️ **Sem configurar o `FRONTEND_URL` no Render**, o navegador vai bloquear as requisições (erro de CORS).

> 💤 **Primeira requisição pode demorar ~30s** no plano gratuito do Render — o servidor dorme após 15 min sem uso.

## 🛠️ Tecnologias

<div align="center">

| Frontend | Backend | Hospedagem |
|:--------:|:-------:|:----------:|
| HTML5 | Python 3.11 | Vercel |
| CSS3 | Flask | Render |
| JavaScript | yt-dlp | — |
| — | Gunicorn | — |

</div>

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE).

---

<div align="center">

**Feito por [mucamuca](https://github.com/mucamuca)**

</div>
