import http.server, os, sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

print(f"MTG 自由桌面 → http://localhost:{PORT}/tabletop.html")
http.server.HTTPServer(("", PORT), Handler).serve_forever()
