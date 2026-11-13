# VideoGrab AI — starter web app

A responsive Flask + yt-dlp MVP for public/authorized video URLs on domains you configure.

## Run locally
1. Install Python 3.10+.
2. Install FFmpeg and make sure `ffmpeg` is on PATH (recommended for merging formats).
3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate
   # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   python app.py
   ```
5. Open http://127.0.0.1:5000

## Configure allowed sites
By default, only Instagram domains are enabled. To add domains you own or have permission to process:
- macOS/Linux: `export ALLOWED_DOMAINS="instagram.com,example.com"`
- PowerShell: `$env:ALLOWED_DOMAINS="instagram.com,example.com"`

Restart the server after changing the setting. Do not add a domain unless you have checked its terms and have rights to download the content. xHamster is deliberately not enabled in this starter: verify its current terms and obtain permission before enabling any integration. This app does not bypass logins, paywalls, DRM, or access controls.

## Production notes
This is a starter, not yet hardened for public multi-user deployment. Before publishing, add authentication/rate limits, a job queue, disk quotas, malware scanning, structured logging, HTTPS, and stricter network egress controls. Run behind a production WSGI server (for example Gunicorn) and a reverse proxy. Review each target site's terms and applicable copyright/privacy law.


## Free deployment on Render
1. Create a GitHub repository and upload all files in this folder.
2. Sign in to https://render.com and choose **New + → Blueprint** (or Web Service).
3. Connect the GitHub repository. If using Web Service manually:
   - Runtime: Python
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 300`
   - Instance type: Free
4. Wait for the build. Render provides a public `*.onrender.com` URL.

Free Render web services sleep after 15 minutes without traffic and may take about a minute to wake up. Large video downloads can exceed free CPU, memory, bandwidth, or timeout limits; this is suitable for a light demo, not reliable high-volume video processing.
