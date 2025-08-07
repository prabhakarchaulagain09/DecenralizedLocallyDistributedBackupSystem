import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from threading import Thread
import requests
import time

STORAGE_DIR = 'storage'
CONFIG_FILE = 'config.json'
SYNC_INTERVAL = 24 * 60 * 60  # once per day

os.makedirs(STORAGE_DIR, exist_ok=True)

# Load list of nodes
with open(CONFIG_FILE) as f:
    NODES = json.load(f)['nodes']

class BackupHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/files':
            # Return list of files
            files = os.listdir(STORAGE_DIR)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(files).encode())

        elif parsed.path == '/download':
            query = parse_qs(parsed.query)
            filename = query.get('filename', [None])[0]
            if not filename:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing filename")
                return
            filepath = os.path.join(STORAGE_DIR, filename)
            if not os.path.exists(filepath):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"File not found")
                return
            with open(filepath, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    def do_POST(self):
        if self.path == '/upload':
            length = int(self.headers['Content-Length'])
            filename = self.headers['Filename']
            data = self.rfile.read(length)
            filepath = os.path.join(STORAGE_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(data)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Stored successfully")

# 🔁 Sync thread
def sync_loop():
    while True:
        try:
            local_files = set(os.listdir(STORAGE_DIR))
            for node in NODES:
                try:
                    r = requests.get(f"http://{node}/files", timeout=5)
                    if r.status_code == 200:
                        their_files = set(json.loads(r.text))
                        missing = local_files - their_files
                        for file in missing:
                            with open(os.path.join(STORAGE_DIR, file), 'rb') as f:
                                print(f"Sending '{file}' to {node}")
                                headers = {'Filename': file}
                                requests.post(f"http://{node}/upload", data=f.read(), headers=headers, timeout=10)
                except Exception as e:
                    print(f"Could not connect to {node}: {e}")
        except Exception as e:
            print("Sync failed:", e)
        time.sleep(SYNC_INTERVAL)

if __name__ == '__main__':
    Thread(target=sync_loop, daemon=True).start()
    server = HTTPServer(('0.0.0.0', 8000), BackupHandler)
    print("Node server running with daily sync...")
    server.serve_forever()

