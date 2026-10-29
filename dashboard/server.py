import http.server
import socketserver
import socket
import os

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Cari IP lokal laptop agar bisa diakses dari perangkat lain dalam satu WiFi
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

local_ip = get_local_ip()

print("=" * 60)
print("  VaultSafe Pro - Local Dashboard Server Berjalan")
print(f"  • Akses dari laptop ini  : http://localhost:{PORT}")
print(f"  • Akses dari HP/satu WiFi : http://{local_ip}:{PORT}")
print("=" * 60)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer dihentikan.")