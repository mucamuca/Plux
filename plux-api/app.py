import os
import re
import shutil
import tempfile
import threading
import time
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)

FRONTEND_URL = os.environ.get("FRONTEND_URL", "*")
CORS(app, origins=[FRONTEND_URL] if FRONTEND_URL != "*" else "*")

def _resolver_cookies():
    """Cookies vêm da variável YT_COOKIES; o arquivo local é só fallback local."""
    conteudo = os.environ.get("YT_COOKIES", "").strip()
    if conteudo:
        if not conteudo.startswith("# Netscape"):
            conteudo = "# Netscape HTTP Cookie File\n" + conteudo
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8", newline="\n"
        )
        tmp.write(conteudo.replace("\r\n", "\n").rstrip("\n") + "\n")
        tmp.close()
        return tmp.name

    local = os.path.join(os.path.dirname(__file__), "cookies.txt")
    return local if os.path.exists(local) else None


COOKIES_FILE = _resolver_cookies()

try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_PATH = None

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


# O YouTube derruba clientes de player de tempos em tempos, e qual deles
# funciona muda conforme o IP do servidor. Tentamos em cascata.
PLAYER_CLIENTS = [
    ["web_safari"],
    ["mweb"],
    ["tv"],
    ["web"],
    ["web_embedded"],
    ["tv_embedded"],
]


def base_opts(clients=None):
    opts = {
        "quiet": True,
        "no_warnings": True,
        "user_agent": USER_AGENT,
    }
    if clients:
        opts["extractor_args"] = {"youtube": {"player_client": list(clients)}}
    if COOKIES_FILE:
        opts["cookiefile"] = COOKIES_FILE
    if FFMPEG_PATH:
        opts["ffmpeg_location"] = FFMPEG_PATH
    return opts


QUALITY_FORMATS = {
    "2160": "bestvideo[height<=2160]+bestaudio/best[height<=2160]",
    "1080": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "720":  "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "480":  "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "360":  "bestvideo[height<=360]+bestaudio/best[height<=360]",
    "best": "bestvideo+bestaudio/best",
}

AUDIO_BITRATES = {"320": "320", "192": "192", "128": "128", "best": "320"}


def extrair(url, download=False, extra=None):
    """Extrai info do vídeo. No YouTube, tenta cada cliente até um responder."""
    if detectar_plataforma(url) != "youtube":
        opts = base_opts()
        if extra:
            opts.update(extra)
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=download)

    ultimo_erro = None
    for clients in PLAYER_CLIENTS:
        opts = base_opts(clients)
        if extra:
            opts.update(extra)
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=download)
            if info:
                return info
        except Exception as e:
            ultimo_erro = e

    raise ultimo_erro or Exception("Não foi possível extrair o vídeo")


def detectar_plataforma(url):
    url_lower = url.lower()
    if "tiktok.com" in url_lower:
        return "tiktok"
    if "instagram.com" in url_lower:
        return "instagram"
    return "youtube"


def detectar_tipo_instagram(url):
    url_lower = url.lower()
    if "/stories/" in url_lower:
        return "story"
    if "/reel" in url_lower:
        return "reel"
    return "post"


def limpar_erro(msg):
    """Deixa a mensagem de erro do yt-dlp legível pro usuário."""
    if "Sign in to confirm" in msg or "not a bot" in msg:
        return ("O YouTube bloqueou o servidor. Os cookies precisam ser "
                "reexportados de uma janela anônima.")
    if "Private video" in msg or "private" in msg.lower():
        return "Esse vídeo é privado."
    if "Video unavailable" in msg:
        return "Vídeo indisponível."
    if "needs to be reloaded" in msg:
        return "O YouTube recusou a sessão do servidor. Tente novamente."
    msg = re.sub(r"^ERROR:\s*", "", msg)
    msg = re.sub(r"\[[a-zA-Z:]+\]\s*[\w-]+:\s*", "", msg)
    return msg.split(". See ")[0].split(". Use ")[0]


def limpar_nome(nome):
    nome = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", nome)
    nome = re.sub(r"\s+", " ", nome).strip()
    return nome[:120] or "video"


def apagar_depois(caminho, atraso=300):
    def run():
        time.sleep(atraso)
        shutil.rmtree(caminho, ignore_errors=True)
    threading.Thread(target=run, daemon=True).start()


@app.route("/")
def health():
    return jsonify({
        "status": "ok",
        "service": "plux-api",
        "ffmpeg": bool(FFMPEG_PATH),
        "cookies": bool(COOKIES_FILE),
        "yt_dlp": getattr(yt_dlp.version, "__version__", "?"),
        "clients": [c[0] for c in PLAYER_CLIENTS],
    })


@app.route("/api/info", methods=["POST"])
def video_info():
    data = request.get_json() or {}
    url = data.get("url", "")

    if not url:
        return jsonify({"error": "URL não fornecida"}), 400

    plataforma = detectar_plataforma(url)

    try:
        info = extrair(url, download=False)

        formats = info.get("formats") or []
        resolutions = sorted(set(
            f.get("height") for f in formats
            if f.get("height") and f.get("vcodec", "none") != "none"
        ), reverse=True)

        tipo = ""
        if plataforma == "instagram":
            tipo = detectar_tipo_instagram(url)

        entries = info.get("entries")
        if entries:
            items = list(entries)
            first = items[0] if items else info
            return jsonify({
                "title": info.get("title") or first.get("title") or "Stories",
                "channel": info.get("channel") or first.get("uploader") or first.get("creator"),
                "duration": first.get("duration") or 0,
                "thumbnail": first.get("thumbnail") or info.get("thumbnail"),
                "views": first.get("view_count") or 0,
                "platform": plataforma,
                "type": tipo,
                "count": len(items),
                "resolutions": resolutions,
            })

        return jsonify({
            "title": info.get("title") or info.get("description", "")[:80] or "Sem título",
            "channel": info.get("channel") or info.get("uploader") or info.get("creator"),
            "duration": info.get("duration") or 0,
            "thumbnail": info.get("thumbnail"),
            "views": info.get("view_count") or 0,
            "platform": plataforma,
            "type": tipo,
            "count": 1,
            "resolutions": resolutions,
        })

    except Exception as e:
        return jsonify({"error": limpar_erro(str(e))}), 400


@app.route("/api/file")
def baixar_arquivo():
    """Baixa no servidor e entrega o arquivo pronto pro navegador."""
    url = request.args.get("url", "")
    quality = request.args.get("quality", "best")
    mode = request.args.get("mode", "video")
    index = request.args.get("index", type=int)

    if not url:
        return jsonify({"error": "URL não fornecida"}), 400

    pasta = tempfile.mkdtemp(prefix="plux-")

    try:
        extra = {
            "outtmpl": os.path.join(pasta, "%(title).100s.%(ext)s"),
            "restrictfilenames": False,
        }

        if index:
            extra["playlist_items"] = str(index)
        else:
            extra["noplaylist"] = True

        if mode == "audio":
            extra["format"] = "bestaudio/best"
            if FFMPEG_PATH:
                extra["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": AUDIO_BITRATES.get(quality, "320"),
                }]
        else:
            extra["format"] = QUALITY_FORMATS.get(quality, QUALITY_FORMATS["best"])
            if FFMPEG_PATH:
                extra["merge_output_format"] = "mp4"

        info = extrair(url, download=True, extra=extra)

        arquivos = []
        for raiz, _, nomes in os.walk(pasta):
            for n in nomes:
                if n.endswith((".part", ".ytdl")):
                    continue
                arquivos.append(os.path.join(raiz, n))

        if not arquivos:
            shutil.rmtree(pasta, ignore_errors=True)
            return jsonify({"error": "Não foi possível baixar o arquivo"}), 400

        caminho = max(arquivos, key=os.path.getsize)
        ext = os.path.splitext(caminho)[1] or (".mp3" if mode == "audio" else ".mp4")

        titulo = info.get("title") or "video"
        if info.get("entries"):
            entradas = list(info["entries"])
            if entradas:
                titulo = entradas[0].get("title") or titulo

        nome = limpar_nome(titulo) + ext
        apagar_depois(pasta)

        return send_file(
            caminho,
            as_attachment=True,
            download_name=nome,
            mimetype="audio/mpeg" if ext == ".mp3" else "video/mp4",
        )

    except Exception as e:
        shutil.rmtree(pasta, ignore_errors=True)
        return jsonify({"error": limpar_erro(str(e))}), 400


@app.route("/api/download", methods=["POST"])
def download():
    """Valida o link antes do download e informa quantos itens existem."""
    data = request.get_json() or {}
    url = data.get("url", "")

    if not url:
        return jsonify({"error": "URL não fornecida"}), 400

    try:
        info = extrair(url, download=False)

        entries = info.get("entries")
        items = list(entries) if entries else [info]

        links = []
        for i, item in enumerate(items, start=1):
            links.append({
                "title": item.get("title") or "video",
                "index": i if entries else None,
            })

        return jsonify({"links": links})

    except Exception as e:
        return jsonify({"error": limpar_erro(str(e))}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
