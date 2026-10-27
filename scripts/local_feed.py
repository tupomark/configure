"""Минимальный HTTP-репозиторий NuGet V3 на локальных XML-файлах."""

import json
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from .checks import ROOT

FIXTURES = ROOT / "examples" / "nuget"
INDEX_PATH = "/v3/index.json"


class FeedHandler(SimpleHTTPRequestHandler):
    """Обслуживать статические nuspec и динамический индекс V3."""

    def do_GET(self):
        """Подставить реальный локальный порт в PackageBaseAddress."""
        if self.path != INDEX_PATH:
            super().do_GET()
            return
        port = self.server.server_port
        payload = json.dumps({"resources": [{
            "@type": "PackageBaseAddress/3.0.0",
            "@id": f"http://127.0.0.1:{port}/flat/",
        }]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format_string, *args):
        """Не смешивать служебный HTTP-журнал с результатами проверки."""


@contextmanager
def local_feed():
    """Запустить сервер на свободном порту и закрыть его после проверки."""
    handler = partial(FeedHandler, directory=str(FIXTURES))
    with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}{INDEX_PATH}"
        finally:
            server.shutdown()
            thread.join()
