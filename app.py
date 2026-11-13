import os, re, socket, ipaddress, tempfile, shutil
from urllib.parse import urlparse
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

# Instagram is enabled as a public/authorized source. Add domains you own or
# have permission to process via ALLOWED_DOMAINS in the environment.
DEFAULT_DOMAINS = {"instagram.com", "www.instagram.com"}
ALLOWED_DOMAINS = {
    d.strip().lower()
    for d in os.getenv("ALLOWED_DOMAINS", ",".join(DEFAULT_DOMAINS)).split(",")
    if d.strip()
}
MAX_FILE_MB = int(os.getenv("MAX_FILE_MB", "800"))

def validate_url(raw):
    if not raw or len(raw) > 2048:
        raise ValueError("Please paste a valid video URL.")
    parsed = urlparse(raw.strip())
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Only http:// and https:// links are accepted.")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing embedded credentials are not accepted.")
    host = parsed.hostname.lower().rstrip(".")
    if not any(host == d or host.endswith("." + d) for d in ALLOWED_DOMAINS):
        raise ValueError("This website is not enabled. Ask the site owner to add its domain to ALLOWED_DOMAINS.")
    try:
        addresses = socket.getaddrinfo(host, None)
        for item in addresses:
            ip = ipaddress.ip_address(item[4][0])
            if not ip.is_global:
                raise ValueError("This host is not publicly routable.")
    except socket.gaierror:
        raise ValueError("Could not resolve this website.")
    return raw.strip()

def ydl_options():
    return {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "socket_timeout": 20,
        "retries": 1,
        "nocheckcertificate": False,
        "restrictfilenames": True,
    }

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/info")
def info():
    try:
        url = validate_url(request.json.get("url", ""))
        with yt_dlp.YoutubeDL(ydl_options()) as ydl:
            data = ydl.extract_info(url, download=False)
        formats = []
        seen = set()
        for f in data.get("formats", []):
            if not f.get("url") or f.get("vcodec") == "none":
                continue
            height = f.get("height")
            label = f"{height}p" if height else f.get("format_note") or "Available"
            if label not in seen:
                formats.append({"format_id": f.get("format_id"), "label": label})
                seen.add(label)
        return jsonify({
            "title": data.get("title") or "Video",
            "thumbnail": data.get("thumbnail"),
            "duration": data.get("duration"),
            "formats": formats[-12:],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.post("/api/download")
def download():
    try:
        body = request.json or {}
        url = validate_url(body.get("url", ""))
        fmt = str(body.get("format_id", "best"))
        if not re.fullmatch(r"[A-Za-z0-9_+.-]{1,80}", fmt):
            raise ValueError("Invalid format selection.")
        tempdir = tempfile.mkdtemp(prefix="videograb_")
        opts = ydl_options()
        opts.update({
            "format": fmt if fmt != "best" else "best[ext=mp4]/best",
            "outtmpl": os.path.join(tempdir, "%(title).80s.%(ext)s"),
            "max_filesize": MAX_FILE_MB * 1024 * 1024,
        })
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            candidates = [os.path.join(tempdir, f) for f in os.listdir(tempdir)]
            candidates = [p for p in candidates if os.path.isfile(p)]
            if not candidates:
                raise ValueError("No downloadable file was produced.")
            path = max(candidates, key=os.path.getsize)
            response = send_file(path, as_attachment=True, download_name=os.path.basename(path),
                                 mimetype="application/octet-stream")
            response.call_on_close(lambda: shutil.rmtree(tempdir, ignore_errors=True))
            return response
        except Exception:
            shutil.rmtree(tempdir, ignore_errors=True)
            raise
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
