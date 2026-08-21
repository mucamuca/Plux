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

## 🛠️ Tecnologias

<div align="center">

| Frontend | Backend |
|:--------:|:-------:|
| HTML5 | Python 3.11 |
| CSS3 | Flask |
| JavaScript | yt-dlp |

</div>

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE).

---

<div align="center">

**Feito por [mucamuca](https://github.com/mucamuca)**

</div>
