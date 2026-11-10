#!/usr/bin/env python3
"""J.A.R.V.I.S. — servidor leve: estáticos com gzip/cache + APIs de notícias e clima.

Sem dependências externas. Foco em resposta rápida: keep-alive, compressão,
cache com dados stale em falha e timeouts curtos para não travar a interface.
"""
import gzip
import html
import io
import json
import os
import threading
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

os.chdir(os.path.dirname(os.path.abspath(__file__)))

FEED = "https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419"
NEWS_TTL = 300
CLIMA_TTL = 180
NEG_TTL = 20
TIMEOUT = 6

CACHE = {}
LOCKS = {}
LOCKS_GUARD = threading.Lock()
STATIC_CACHE = {}
STATIC_LOCK = threading.Lock()
TEXT_MIME = {
    "text/html", "text/css", "text/plain", "text/javascript", "text/markdown",
    "text/xml", "application/javascript", "application/json", "application/xml",
    "image/svg+xml",
}


def key_lock(key):
    """Um lock por recurso: evita duas buscas externas iguais ao mesmo tempo."""
    with LOCKS_GUARD:
        if key not in LOCKS:
            LOCKS[key] = threading.Lock()
        return LOCKS[key]


def cached(key, ttl, loader):
    """Cache positivo, cache negativo curto e stale-on-error."""
    now = time.time()
    with key_lock(key):
        item = CACHE.get(key)
        if item and item.get("data") and now - item["t"] < ttl:
            return item["data"]
        if item and item.get("err") and now - item["err"] < NEG_TTL:
            if item.get("data"):
                return dict(item["data"], stale=True)
            raise RuntimeError("upstream indisponível (cache negativo)")
        try:
            data = loader()
            CACHE[key] = {"t": time.time(), "err": 0, "data": data}
            return data
        except Exception:  # pylint: disable=broad-exception-caught
            stale = item.get("data") if item else None
            CACHE[key] = {
                "t": item.get("t", 0) if item else 0,
                "err": time.time(),
                "data": stale,
            }
            if stale:
                return dict(stale, stale=True)
            raise


def load_news():
    """Busca e normaliza até 25 manchetes do Google News Brasil."""
    req = urllib.request.Request(FEED, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
        "Accept-Encoding": "identity",
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        root = ET.fromstring(r.read())
    items = []
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        src = it.find("{https://news.google.com/rss}source")
        if src is None:
            src = it.find("source")
        source = src.text.strip() if src is not None and src.text else ""
        if title:
            items.append({"title": html.unescape(title), "link": link, "source": source})
        if len(items) >= 25:
            break
    if not items:
        raise ValueError("feed vazio")
    return {"news": items, "updated": time.strftime("%H:%M")}


def load_clima(cidade):
    """Busca o clima atual de uma cidade no wttr.in."""
    url = "https://wttr.in/" + urllib.parse.quote(cidade) + "?format=j1&lang=pt"
    req = urllib.request.Request(url, headers={
        "User-Agent": "curl/8.0",
        "Accept": "application/json",
        "Accept-Encoding": "identity",
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        j = json.loads(r.read().decode("utf-8"))
    cur = (j.get("current_condition") or [{}])[0]
    hoje = (j.get("weather") or [{}])[0]
    lang_pt = cur.get("lang_pt") or []
    weather_desc = cur.get("weatherDesc") or [{}]
    desc = ""
    if lang_pt and isinstance(lang_pt[0], dict):
        desc = lang_pt[0].get("value", "")
    if not desc and weather_desc and isinstance(weather_desc[0], dict):
        desc = weather_desc[0].get("value", "")
    area_name = ((j.get("nearest_area") or [{}])[0].get("areaName") or [{}])
    area = area_name[0].get("value") if area_name and isinstance(area_name[0], dict) else ""
    return {
        "cidade": area or cidade,
        "temp": cur.get("temp_C"),
        "sensacao": cur.get("FeelsLikeC"),
        "desc": desc,
        "umidade": cur.get("humidity"),
        "vento": cur.get("windspeedKmph"),
        "max": hoje.get("maxtempC"),
        "min": hoje.get("mintempC"),
    }


def news():
    """Retorna notícias com cache de 5 minutos."""
    return cached(("news",), NEWS_TTL, load_news)


def clima(cidade):
    """Retorna clima com cache de 3 minutos por cidade."""
    return cached(("clima", cidade.strip().lower()), CLIMA_TTL,
                  lambda: load_clima(cidade))


class H(SimpleHTTPRequestHandler):
    """Handler HTTP: estáticos compactados + endpoints /api."""

    protocol_version = "HTTP/1.1"

    def end_headers(self):
        """Adiciona cabeçalho de segurança antes de fechar os headers."""
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def send_json(self, obj, status=200, max_age=60):
        """Envia JSON, com gzip quando o corpo compensa."""
        raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        gz = "gzip" in self.headers.get("Accept-Encoding", "").lower() and len(raw) > 512
        body = gzip.compress(raw, compresslevel=6) if gz else raw
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        cc = "public, max-age=" + str(max_age) if status == 200 else "no-store"
        self.send_header("Cache-Control", cc)
        self.send_header("Vary", "Accept-Encoding")
        if gz:
            self.send_header("Content-Encoding", "gzip")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def send_head(self):
        """Serve HTML/CSS/JS/JSON compactados, com cache em memória por mtime."""
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            # A raiz "/" aponta para a pasta: resolve o index antes de compactar.
            for index in ("index.html", "index.htm"):
                candidate = os.path.join(path, index)
                if os.path.isfile(candidate):
                    path = candidate
                    break
            else:
                return super().send_head()
        ctype = self.guess_type(path).split(";")[0].strip()
        if ctype not in TEXT_MIME:
            return super().send_head()
        try:
            st = os.stat(path)
            with open(path, "rb") as f:
                raw = f.read()
        except OSError:
            return super().send_head()
        gz = "gzip" in self.headers.get("Accept-Encoding", "").lower()
        key = (path, int(st.st_mtime), st.st_size, gz)
        with STATIC_LOCK:
            body = STATIC_CACHE.get(key)
            if body is None:
                body = gzip.compress(raw, compresslevel=6) if gz else raw
                if len(STATIC_CACHE) > 24:
                    STATIC_CACHE.clear()
                STATIC_CACHE[key] = body
        self.send_response(200)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Vary", "Accept-Encoding")
        if gz:
            self.send_header("Content-Encoding", "gzip")
        cache = "no-store" if os.path.basename(path) == "index.html" else "public, max-age=3600"
        self.send_header("Cache-Control", cache)
        self.end_headers()
        return io.BytesIO(body)

    def do_GET(self):
        """Roteia /api/health, /api/news e /api/clima; o resto é estático."""
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/health":
            self.send_json({"ok": True, "ts": int(time.time())}, max_age=0)
            return
        if parsed.path == "/api/news":
            try:
                self.send_json(news())
            except Exception as e:  # pylint: disable=broad-exception-caught
                self.send_json({"error": str(e), "news": []}, status=502, max_age=0)
            return
        if parsed.path == "/api/clima":
            q = urllib.parse.parse_qs(parsed.query)
            cidade = (q.get("c", ["Guarulhos"])[0] or "Guarulhos").strip()[:60]
            try:
                self.send_json(clima(cidade))
            except Exception as e:  # pylint: disable=broad-exception-caught
                self.send_json({"error": str(e)}, status=502, max_age=0)
            return
        super().do_GET()

    def log_message(self, fmt, *args):  # pylint: disable=arguments-differ
        """Loga requisições com o prefixo [jarvis]."""
        print("[jarvis]", fmt % args)


class Server(ThreadingHTTPServer):
    """Servidor HTTP com threads daemon e porta reutilizável."""

    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    print("J.A.R.V.I.S. turbo online na porta 8100")
    Server(("0.0.0.0", 8100), H).serve_forever()
