#!/usr/bin/env python3
"""J.A.R.V.I.S. — servidor: arquivos estáticos + API de notícias (Google News Brasil)."""
import json, time, html, os
import urllib.request, urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import xml.etree.ElementTree as ET

os.chdir(os.path.dirname(os.path.abspath(__file__)))

CACHE = {"t": 0, "data": None}
FEED = "https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419"

def fetch_news():
    now = time.time()
    if CACHE["data"] and now - CACHE["t"] < 180:
        return CACHE["data"]
    req = urllib.request.Request(FEED, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
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
    data = {"news": items, "updated": time.strftime("%H:%M")}
    CACHE["t"], CACHE["data"] = now, data
    return data

def fetch_clima(cidade):
    url = "https://wttr.in/" + urllib.parse.quote(cidade) + "?format=j1&lang=pt"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        j = json.loads(r.read().decode())
    cur = j["current_condition"][0]
    hoje = j["weather"][0]
    desc = cur.get("lang_pt", [{"value": cur["weatherDesc"][0]["value"]}])[0]["value"]
    area = j.get("nearest_area", [{}])[0].get("areaName", [{"value": cidade}])[0]["value"]
    return {"cidade": area, "temp": cur["temp_C"], "sensacao": cur["FeelsLikeC"],
            "desc": desc, "umidade": cur["humidity"],
            "vento": cur["windspeedKmph"],
            "max": hoje["maxtempC"], "min": hoje["mintempC"]}

class H(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/clima"):
            from urllib.parse import urlparse, parse_qs, unquote
            q = parse_qs(urlparse(self.path).query)
            cidade = unquote(q.get("c", ["Guarulhos"])[0])
            try:
                body = json.dumps(fetch_clima(cidade)).encode()
                self.send_response(200)
            except Exception as e:
                body = json.dumps({"error": str(e)}).encode()
                self.send_response(502)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/api/news"):
            try:
                body = json.dumps(fetch_news()).encode()
                self.send_response(200)
            except Exception as e:
                body = json.dumps({"error": str(e), "news": []}).encode()
                self.send_response(502)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def log_message(self, fmt, *args):
        print("[jarvis]", fmt % args)

if __name__ == "__main__":
    print("J.A.R.V.I.S. online na porta 8100")
    ThreadingHTTPServer(("0.0.0.0", 8100), H).serve_forever()
