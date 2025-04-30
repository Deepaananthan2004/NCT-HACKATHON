import os
import uuid
import hashlib
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
import firebase_admin
from firebase_admin import credentials, firestore
import requests
from flask_cors import CORS

# Blockchain setup
class Block:
    def __init__(self, index, data, previous_hash):
        self.index = index
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        return hashlib.sha256((str(self.index) + str(self.data) + self.previous_hash).encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "Genesis Block", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        latest_block = self.get_latest_block()
        new_block = Block(len(self.chain), data, latest_block.hash)
        self.chain.append(new_block)

blockchain = Blockchain()

# Flask app setup
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Firebase setup
cred = credentials.Certificate("D:/NCT HACKATHON/blockchaindatashare-firebase-adminsdk-fbsvc-5865add3ce.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Pinata API for IPFS
PINATA_API_KEY = "5211a52676fc504d5a6e"
PINATA_SECRET_API_KEY = "2387732948162f4adf6a25dc2b1fcfb32c287f211d9a9bbeb1224da0765a9c4f"

def save_keys(pub, priv):
    db.collection("keys").document(pub).set({"private_key": priv})

def get_private_key(pub):
    doc = db.collection("keys").document(pub).get()
    return doc.to_dict()["private_key"] if doc.exists else None

def upload_to_ipfs(filepath):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY
    }
    with open(filepath, 'rb') as file:
        response = requests.post(url, files={"file": file}, headers=headers)
        response_json = response.json()
        return f"https://gateway.pinata.cloud/ipfs/{response_json['IpfsHash']}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_keys', methods=['GET'])
def generate_keys():
    pub = str(uuid.uuid4())[:8]
    priv = str(uuid.uuid4())[:8]
    save_keys(pub, priv)
    return jsonify({'public_key': pub, 'private_key': priv})

@app.route('/upload', methods=['POST'])
def upload_file():
    pub = request.form['public_key']
    file = request.files['file']
    if not file:
        return jsonify({'error': 'No file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    ipfs_url = upload_to_ipfs(filepath)
    file_hash = hashlib.sha256(open(filepath, 'rb').read()).hexdigest()

    blockchain.add_block({
        'public_key': pub,
        'filename': filename,
        'file_hash': file_hash,
        'ipfs_url': ipfs_url
    })

    os.remove(filepath)
    return jsonify({'message': 'File uploaded', 'ipfs_url': ipfs_url})

@app.route('/download', methods=['POST'])
def download_file():
    priv_key = request.form['private_key']
    # Find matching block
    for block in blockchain.chain:
        if isinstance(block.data, dict):
            pub_key = block.data.get('public_key')
            stored_priv = get_private_key(pub_key)
            if stored_priv == priv_key:
                return jsonify({'filename': block.data['filename'], 'ipfs_url': block.data['ipfs_url']})
    return jsonify({'error': 'Invalid private key'}), 404

if __name__ == '__main__':
    app.run(debug=True)
