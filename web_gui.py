from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import hashlib
from datetime import datetime
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

STORAGE_DIR = 'storage'
CONFIG_FILE = 'config.json'
METADATA_FILE = 'metadata.json'

os.makedirs(STORAGE_DIR, exist_ok=True)

# Load configuration
def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"nodes": []}
    with open(CONFIG_FILE) as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def calculate_hash(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/files')
def get_files():
    """Get list of all files"""
    files_info = []
    metadata = load_metadata()
    
    for filename in os.listdir(STORAGE_DIR):
        filepath = os.path.join(STORAGE_DIR, filename)
        if os.path.isfile(filepath):
            stat = os.stat(filepath)
            file_meta = metadata.get(filename, {})
            
            files_info.append({
                'name': filename,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'hash': file_meta.get('hash', calculate_hash(filepath)[:8])
            })
    
    return jsonify(files_info)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(STORAGE_DIR, filename)
    file.save(filepath)
    
    # Update metadata
    file_hash = calculate_hash(filepath)
    metadata = load_metadata()
    metadata[filename] = {
        'hash': file_hash,
        'size': os.path.getsize(filepath),
        'uploaded': datetime.now().isoformat()
    }
    
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return jsonify({
        'message': 'File uploaded successfully',
        'filename': filename,
        'hash': file_hash
    })

@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete a file"""
    filepath = os.path.join(STORAGE_DIR, secure_filename(filename))
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    os.remove(filepath)
    
    # Update metadata
    metadata = load_metadata()
    if filename in metadata:
        del metadata[filename]
        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    return jsonify({'message': 'File deleted successfully'})

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download a file"""
    filepath = os.path.join(STORAGE_DIR, secure_filename(filename))
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(filepath, as_attachment=True)

@app.route('/api/sync', methods=['POST'])
def sync_files():
    """Sync files with all nodes"""
    config = load_config()
    nodes = config.get('nodes', [])
    
    if not nodes:
        return jsonify({'error': 'No nodes configured'}), 400
    
    local_files = set(os.listdir(STORAGE_DIR))
    results = []
    
    for node in nodes:
        try:
            # Get their file list
            r = requests.get(f"http://{node}/files", timeout=5)
            if r.status_code != 200:
                results.append({'node': node, 'status': 'unreachable'})
                continue
            
            remote_files_data = r.json()
            remote_files = {f['name'] if isinstance(f, dict) else f 
                          for f in remote_files_data}
            
            # Send missing files
            missing = local_files - remote_files
            sent = []
            
            for filename in missing:
                filepath = os.path.join(STORAGE_DIR, filename)
                with open(filepath, 'rb') as f:
                    headers = {'Filename': filename}
                    resp = requests.post(
                        f"http://{node}/upload",
                        data=f.read(),
                        headers=headers,
                        timeout=30
                    )
                    if resp.status_code == 200:
                        sent.append(filename)
            
            results.append({
                'node': node,
                'status': 'success',
                'files_sent': len(sent),
                'files': sent
            })
            
        except Exception as e:
            results.append({
                'node': node,
                'status': 'error',
                'error': str(e)
            })
    
    return jsonify({'results': results})

@app.route('/api/nodes')
def get_nodes():
    """Get configured nodes"""
    config = load_config()
    return jsonify({'nodes': config.get('nodes', [])})

@app.route('/api/nodes', methods=['POST'])
def update_nodes():
    """Update node configuration"""
    data = request.json
    nodes = data.get('nodes', [])
    
    config = load_config()
    config['nodes'] = nodes
    save_config(config)
    
    return jsonify({'message': 'Nodes updated', 'nodes': nodes})

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    files = os.listdir(STORAGE_DIR)
    total_size = sum(os.path.getsize(os.path.join(STORAGE_DIR, f)) 
                    for f in files if os.path.isfile(os.path.join(STORAGE_DIR, f)))
    
    config = load_config()
    
    # Check node status
    online_nodes = 0
    for node in config.get('nodes', []):
        try:
            r = requests.get(f"http://{node}/health", timeout=2)
            if r.status_code == 200:
                online_nodes += 1
        except:
            pass
    
    return jsonify({
        'total_files': len(files),
        'total_size': total_size,
        'nodes_total': len(config.get('nodes', [])),
        'nodes_online': online_nodes
    })

if __name__ == '__main__':
    print("🌐 Starting Web GUI on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
