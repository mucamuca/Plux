import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)

FRONTEND_URL = os.environ.get("FRONTEND_URL", "*")
CORS(app, origins=[FRONTEND_URL] if FRONTEND_URL != "*" else "*")

COOKIES_FILE = os.path.join(os.path.dirname(__file__), "cookies.txt")
if not os.path.exists(COOKIES_FILE):
    COOKIES_FILE = None

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


def base_opts():
    opts = {
        "quiet": True,
        "no_warnings": True,
        "user_agent": USER_AGENT,
        "extractor_args": {"youtube": {"player_client": ["tv", "web_safari", "web"]}},
    }
    if COOKIES_FILE:
        opts["cookiefile"] = COOKIES_FILE
    return opts

QUALITY_FORMATS = {
    "2160": "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best[height<=2160]",
    "1080": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]",
    "720":  "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]",
    "480":  "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]",
    "360":  "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]",
    "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
}

AUDIO_FORMATS = {
    "320": "bestaudio[ext=m4a]/bestaudio",
    "192": "bestaudio[ext=m4a]/bestaudio",
    "128": "bestaudio[ext=m4a]/bestaudio",
    "best": "bestaudio[ext=m4a]/bestaudio",
}


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


@app.route("/")
def health():
    return jsonify({"status": "ok", "service": "plux-api"})


@app.route("/api/info", methods=["POST"])
def video_info():
    data = request.get_json() or {}
    url = data.get("url", "")

    if not url:
        return jsonify({"error": "URL não fornecida"}), 400

    plataforma = detectar_plataforma(url)

    try:
        opts = base_opts()
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

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
                count = len(items)
                first = items[0] if items else info
                return jsonify({
                    "title": info.get("title") or first.get("title") or "Stories",
                    "channel": info.get("channel") or first.get("uploader") or first.get("creator"),
                    "duration": first.get("duration") or 0,
                    "thumbnail": first.get("thumbnail") or info.get("thumbnail"),
                    "views": first.get("view_count") or 0,
                    "platform": plataforma,
                    "type": tipo,
                    "count": count,
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
        return jsonify({"error": str(e)}), 400


@app.route("/api/download", methods=["POST"])
def download():
    data = request.get_json() or {}
    url = data.get("url", "")
    quality = data.get("quality", "best")
    mode = data.get("mode", "video")

    if not url:
        return jsonify({"error": "URL não fornecida"}), 400

    try:
        if mode == "audio":
            fmt = AUDIO_FORMATS.get(quality, AUDIO_FORMATS["best"])
        else:
            fmt = QUALITY_FORMATS.get(quality, QUALITY_FORMATS["best"])

        opts = base_opts()
        opts["format"] = fmt

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

            entries = info.get("entries")
            items = list(entries) if entries else [info]

            download_links = []
            for item in items:
                direct_url = item.get("url")
                if not direct_url:
                    requested = item.get("requested_formats")
                    if requested:
                        direct_url = requested[0].get("url")

                ext = "mp3" if mode == "audio" else (item.get("ext") or "mp4")
                download_links.append({
                    "title": item.get("title") or "video",
                    "url": direct_url,
                    "ext": ext,
                })

        return jsonify({"links": download_links})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
