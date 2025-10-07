import os
import json
import hashlib
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from threading import Thread
import requests
import time
import socket

# Configuration
STORAGE_DIR = 'storage'
METADATA_FILE = 'metadata.json'
CONFIG_FILE = 'config.json'
SYNC_INTERVAL = 24 * 60 * 60  # once per day
PORT = 8000

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('node.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ensure directories exist
os.makedirs(STORAGE_DIR, exist_ok=True)

# Metadata storage
def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_metadata(metadata):
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

metadata = load_metadata()

# Load nodes configuration
def load_config():
    if not os.path.exists(CONFIG_FILE):
        logger.warning(f"{CONFIG_FILE} not found. Creating default config.")
        default_config = {"nodes": []}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=2)
        return default_config
    
    with open(CONFIG_FILE) as f:
        return json.load(f)

config = load_config()
NODES = config.get('nodes', [])

# Get local IP
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()
LOCAL_ADDRESS = f"{LOCAL_IP}:{PORT}"

# Filter out self from nodes
NODES = [node for node in NODES if node != LOCAL_ADDRESS]

logger.info(f"Starting node at {LOCAL_ADDRESS}")
logger.info(f"Connected nodes: {NODES}")

def calculate_hash(filepath):
    """Calculate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def sanitize_filename(filename):
    """Sanitize filename to prevent path traversal"""
    return os.path.basename(filename)

class BackupHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info("%s - %s" % (self.address_string(), format % args))
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/files':
            # Return list of files with metadata
            files_info = []
            for filename in os.listdir(STORAGE_DIR):
                filepath = os.path.join(STORAGE_DIR, filename)
                if os.path.isfile(filepath):
                    file_meta = metadata.get(filename, {})
                    files_info.append({
                        'name': filename,
                        'size': os.path.getsize(filepath),
                        'hash': file_meta.get('hash', ''),
                        'uploaded': file_meta.get('uploaded', ''),
                        'modified': file_meta.get('modified', '')
                    })
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(files_info).encode())

        elif parsed.path == '/download':
            query = parse_qs(parsed.query)
            filename = query.get('filename', [None])[0]
            
            if not filename:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing filename")
                return
            
            filename = sanitize_filename(filename)
            filepath = os.path.join(STORAGE_DIR, filename)
            
            if not os.path.exists(filepath):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"File not found")
                return
            
            try:
                with open(filepath, 'rb') as f:
                    data = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                logger.info(f"Served file: {filename}")
            except Exception as e:
                logger.error(f"Error serving file {filename}: {e}")
                self.send_response(500)
                self.end_headers()

        elif parsed.path == '/health':
            # Health check endpoint
            health = {
                'status': 'healthy',
                'storage_files': len(os.listdir(STORAGE_DIR)),
                'nodes_configured': len(NODES),
                'local_address': LOCAL_ADDRESS
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(health).encode())
        
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/upload':
            try:
                length = int(self.headers['Content-Length'])
                filename = self.headers.get('Filename', 'unnamed_file')
                filename = sanitize_filename(filename)
                
                data = self.rfile.read(length)
                filepath = os.path.join(STORAGE_DIR, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(data)
                
                # Update metadata
                file_hash = calculate_hash(filepath)
                metadata[filename] = {
                    'hash': file_hash,
                    'size': len(data),
                    'uploaded': datetime.now().isoformat(),
                    'modified': datetime.now().isoformat()
                }
                save_metadata(metadata)
                
                logger.info(f"Stored file: {filename} ({len(data)} bytes, hash: {file_hash})")
                
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    'message': 'Stored successfully',
                    'filename': filename,
                    'size': len(data),
                    'hash': file_hash
                }).encode())
            except Exception as e:
                logger.error(f"Upload error: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode())
        
        elif self.path == '/delete':
            try:
                length = int(self.headers['Content-Length'])
                data = json.loads(self.rfile.read(length).decode())
                filename = sanitize_filename(data.get('filename', ''))
                
                if not filename:
                    self.send_response(400)
                    self.end_headers()
                    return
                
                filepath = os.path.join(STORAGE_DIR, filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
                    if filename in metadata:
                        del metadata[filename]
                        save_metadata(metadata)
                    logger.info(f"Deleted file: {filename}")
                    self.send_response(200)
                else:
                    self.send_response(404)
                
                self.end_headers()
            except Exception as e:
                logger.error(f"Delete error: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

# Enhanced sync with bidirectional support
def sync_loop():
    """Automatic sync loop - both push and pull"""
    while True:
        try:
            logger.info("Starting sync cycle...")
            local_files = {}
            
            # Build local file list with hashes
            for filename in os.listdir(STORAGE_DIR):
                filepath = os.path.join(STORAGE_DIR, filename)
                if os.path.isfile(filepath):
                    file_meta = metadata.get(filename, {})
                    if not file_meta.get('hash'):
                        file_hash = calculate_hash(filepath)
                        metadata[filename] = {
                            'hash': file_hash,
                            'size': os.path.getsize(filepath),
                            'uploaded': datetime.now().isoformat(),
                            'modified': datetime.now().isoformat()
                        }
                        save_metadata(metadata)
                    local_files[filename] = metadata[filename].get('hash', '')
            
            # Sync with each node
            for node in NODES:
                try:
                    # Get their file list
                    r = requests.get(f"http://{node}/files", timeout=5)
                    if r.status_code != 200:
                        logger.warning(f"Could not get file list from {node}")
                        continue
                    
                    remote_files = {f['name']: f.get('hash', '') for f in r.json()}
                    
                    # Push files they don't have
                    for filename, file_hash in local_files.items():
                        if filename not in remote_files or remote_files[filename] != file_hash:
                            filepath = os.path.join(STORAGE_DIR, filename)
                            try:
                                with open(filepath, 'rb') as f:
                                    headers = {'Filename': filename}
                                    resp = requests.post(
                                        f"http://{node}/upload",
                                        data=f.read(),
                                        headers=headers,
                                        timeout=30
                                    )
                                    if resp.status_code == 200:
                                        logger.info(f"✓ Pushed '{filename}' to {node}")
                                    else:
                                        logger.warning(f"Failed to push '{filename}' to {node}")
                            except Exception as e:
                                logger.error(f"Error pushing '{filename}' to {node}: {e}")
                    
                    # Pull files we don't have
                    for filename, file_hash in remote_files.items():
                        if filename not in local_files or local_files[filename] != file_hash:
                            try:
                                resp = requests.get(
                                    f"http://{node}/download?filename={filename}",
                                    timeout=30
                                )
                                if resp.status_code == 200:
                                    filepath = os.path.join(STORAGE_DIR, filename)
                                    with open(filepath, 'wb') as f:
                                        f.write(resp.content)
                                    
                                    # Update metadata
                                    new_hash = calculate_hash(filepath)
                                    metadata[filename] = {
                                        'hash': new_hash,
                                        'size': len(resp.content),
                                        'uploaded': datetime.now().isoformat(),
                                        'modified': datetime.now().isoformat()
                                    }
                                    save_metadata(metadata)
                                    logger.info(f"✓ Pulled '{filename}' from {node}")
                            except Exception as e:
                                logger.error(f"Error pulling '{filename}' from {node}: {e}")
                
                except requests.exceptions.Timeout:
                    logger.warning(f"Timeout connecting to {node}")
                except requests.exceptions.ConnectionError:
                    logger.warning(f"Could not connect to {node}")
                except Exception as e:
                    logger.error(f"Sync error with {node}: {e}")
            
            logger.info("Sync cycle completed")
        except Exception as e:
            logger.error(f"Sync loop error: {e}")
        
        time.sleep(SYNC_INTERVAL)

if __name__ == '__main__':
    # Start sync thread
    sync_thread = Thread(target=sync_loop, daemon=True)
    sync_thread.start()
    
    # Start HTTP server
    try:
        server = HTTPServer(('0.0.0.0', PORT), BackupHandler)
        logger.info(f"🚀 Node server running at {LOCAL_ADDRESS} with bidirectional sync")
        logger.info(f"📁 Storage directory: {os.path.abspath(STORAGE_DIR)}")
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
    except Exception as e:
        logger.error(f"Server error: {e}")
