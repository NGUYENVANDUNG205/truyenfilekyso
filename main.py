
from flask import Flask, render_template_string, request, jsonify, send_file
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
import base64
import os
import hashlib
import json
from datetime import datetime
import io

app = Flask(__name__)

# Lưu trữ keys và files tạm thời
storage = {
    'private_key': None,
    'public_key': None,
    'signed_files': {},
    'uploaded_files': {}
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ứng dụng Truyền File với Chữ Ký Số</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            padding: 20px;
            color: #fff;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            overflow: hidden;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .header {
            background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-bottom: 3px solid #fbbf24;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .tabs {
            display: flex;
            background: rgba(0,0,0,0.2);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .tab-btn {
            flex: 1;
            padding: 20px;
            border: none;
            background: transparent;
            cursor: pointer;
            font-size: 1.1em;
            font-weight: 500;
            color: #cbd5e1;
            transition: all 0.3s ease;
            border-bottom: 3px solid transparent;
        }
        
        .tab-btn.active {
            background: rgba(139, 92, 246, 0.3);
            color: #fbbf24;
            border-bottom: 3px solid #fbbf24;
        }
        
        .tab-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
        }
        
        .tab-content {
            display: none;
            padding: 40px;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #fbbf24;
        }
        
        .form-control {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            font-size: 1em;
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            transition: border-color 0.3s ease;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #8b5cf6;
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.3);
        }
        
        .form-control::placeholder {
            color: #94a3b8;
        }
        
        .btn {
            background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-right: 10px;
            margin-bottom: 10px;
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
        }
        
        .btn-success:hover {
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6);
        }
        
        .alert {
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            font-weight: 500;
        }
        
        .alert-success {
            background: rgba(16, 185, 129, 0.2);
            border: 1px solid #10b981;
            color: #6ee7b7;
        }
        
        .alert-danger {
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid #ef4444;
            color: #fca5a5;
        }
        
        .file-info {
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid #3b82f6;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .info-label {
            font-weight: 600;
            color: #fbbf24;
        }
        
        .info-value {
            color: #cbd5e1;
            word-break: break-all;
        }
        
        .key-display {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0 15px 0;
            word-break: break-all;
            font-family: 'Courier New', monospace;
            font-size: 0.8em;
            max-height: 150px;
            overflow-y: auto;
            color: #94a3b8;
        }
        
        .signature-display {
            background: rgba(251, 191, 36, 0.1);
            border: 1px solid #fbbf24;
            border-radius: 10px;
            padding: 15px;
            margin-top: 15px;
            word-break: break-all;
            font-family: 'Courier New', monospace;
            font-size: 0.8em;
            max-height: 150px;
            overflow-y: auto;
            color: #fcd34d;
        }
        
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 20px;
        }
        
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
            
            .tabs {
                flex-direction: column;
            }
            
            .container {
                margin: 10px;
            }
        }
        
        .loading {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }
        
        .spinner {
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-top: 4px solid #8b5cf6;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 2s linear infinite;
            margin-bottom: 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .spooky-text {
            color: #fbbf24;
            text-shadow: 0 0 10px #fbbf24;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 <span class="spooky-text">Ứng dụng Ma Quái</span> - Ký Số File</h1>
            <p>Bảo mật file với chữ ký số RSA trong không gian siêu nhiên 👻</p>
        </div>
        
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('keys')">🔑 Quản lý Keys</button>
            <button class="tab-btn" onclick="switchTab('sender')">📤 Người gửi</button>
            <button class="tab-btn" onclick="switchTab('receiver')">📥 Người nhận</button>
        </div>
        
        <!-- Tab Quản lý Keys -->
        <div id="keys" class="tab-content active">
            <h2>🔑 Quản lý Keys RSA Ma Quái</h2>
            <div class="grid">
                <div>
                    <h3>Tạo cặp Key ma thuật mới</h3>
                    <button class="btn" onclick="generateKeys()">🎲 Tạo Keys RSA</button>
                    <div id="keysResult"></div>
                </div>
                <div>
                    <h3>Import Keys từ file ma quái</h3>
                    <div class="form-group">
                        <label>Private Key (PEM)</label>
                        <input type="file" class="form-control" id="privateKeyFile" accept=".pem,.key">
                        <button class="btn" onclick="loadPrivateKey()">📁 Load Private Key</button>
                    </div>
                    <div class="form-group">
                        <label>Public Key (PEM)</label>
                        <input type="file" class="form-control" id="publicKeyFile" accept=".pem,.key">
                        <button class="btn" onclick="loadPublicKey()">📁 Load Public Key</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Tab Người gửi -->
        <div id="sender" class="tab-content">
            <h2>📤 Người gửi ma quái - Ký file và gửi</h2>
            <div class="form-group">
                <label>Nhập nội dung văn bản ma thuật</label>
                <textarea class="form-control" id="textContent" rows="6" placeholder="Nhập nội dung văn bản cần ký với ma thuật..."></textarea>
            </div>
            <div class="form-group">
                <label>Hoặc chọn file ma quái</label>
                <input type="file" class="form-control" id="fileToSign">
            </div>
            <button class="btn" onclick="signFile()">✍️ Ký file với ma thuật</button>
            <div id="signingResult"></div>
        </div>
        
        <!-- Tab Người nhận -->
        <div id="receiver" class="tab-content">
            <h2>📥 Người nhận ma quái - Xác thực chữ ký</h2>
            <div class="form-group">
                <label>Upload gói file đã ký ma thuật</label>
                <input type="file" class="form-control" id="signedPackage" accept=".json">
            </div>
            <button class="btn" onclick="verifySignature()">🔍 Xác thực chữ ký ma thuật</button>
            <div id="verificationResult"></div>
        </div>
    </div>
    
    <div id="loading" class="loading">
        <div class="spinner"></div>
        <p style="color: #fbbf24;">Đang xử lý ma thuật...</p>
    </div>

    <script>
        let currentKeys = {
            private: null,
            public: null
        };

        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }

        function showLoading() {
            document.getElementById('loading').style.display = 'flex';
        }

        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
        }

        async function generateKeys() {
            showLoading();
            try {
                const response = await fetch('/generate_keys', {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (data.success) {
                    currentKeys.private = data.private_key;
                    currentKeys.public = data.public_key;
                    
                    document.getElementById('keysResult').innerHTML = `
                        <div class="alert alert-success">
                            <strong>✅ Keys ma thuật đã được tạo thành công!</strong>
                        </div>
                        <div class="file-info">
                            <h4>🔐 Private Key Ma Quái</h4>
                            <div class="key-display">${data.private_key}</div>
                            <button class="btn btn-success" onclick="downloadKey('private', \`${data.private_key.replace(/\`/g, '\\`')}\`)">💾 Tải Private Key</button>
                            
                            <h4 style="margin-top: 20px;">🔓 Public Key Ma Quái</h4>
                            <div class="key-display">${data.public_key}</div>
                            <button class="btn btn-success" onclick="downloadKey('public', \`${data.public_key.replace(/\`/g, '\\`')}\`)">💾 Tải Public Key</button>
                        </div>
                    `;
                } else {
                    document.getElementById('keysResult').innerHTML = `
                        <div class="alert alert-danger">❌ ${data.error}</div>
                    `;
                }
            } catch (error) {
                document.getElementById('keysResult').innerHTML = `
                    <div class="alert alert-danger">❌ Lỗi: ${error.message}</div>
                `;
            }
            hideLoading();
        }

        function downloadKey(type, keyData) {
            const blob = new Blob([keyData], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${type}_key.pem`;
            a.click();
            window.URL.revokeObjectURL(url);
        }

        async function loadPrivateKey() {
            const file = document.getElementById('privateKeyFile').files[0];
            if (!file) {
                alert('Vui lòng chọn file private key');
                return;
            }
            
            try {
                const text = await file.text();
                currentKeys.private = text;
                alert('Private key đã được load thành công!');
            } catch (error) {
                alert('Lỗi khi đọc file: ' + error.message);
            }
        }

        async function loadPublicKey() {
            const file = document.getElementById('publicKeyFile').files[0];
            if (!file) {
                alert('Vui lòng chọn file public key');
                return;
            }
            
            try {
                const text = await file.text();
                currentKeys.public = text;
                alert('Public key đã được load thành công!');
            } catch (error) {
                alert('Lỗi khi đọc file: ' + error.message);
            }
        }

        async function signFile() {
            const textContent = document.getElementById('textContent').value;
            const fileInput = document.getElementById('fileToSign');
            
            if (!textContent && !fileInput.files[0]) {
                alert('Vui lòng nhập văn bản hoặc chọn file!');
                return;
            }
            
            if (!currentKeys.private) {
                alert('Vui lòng tạo hoặc load private key trước!');
                return;
            }

            showLoading();
            try {
                const formData = new FormData();
                formData.append('private_key', currentKeys.private);
                
                if (textContent) {
                    formData.append('text_content', textContent);
                } else {
                    formData.append('file', fileInput.files[0]);
                }

                const response = await fetch('/sign_file', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('signingResult').innerHTML = `
                        <div class="alert alert-success">
                            <strong>✅ File đã được ký ma thuật thành công!</strong>
                        </div>
                        <div class="file-info">
                            <h4>📋 Thông tin file đã ký</h4>
                            <div class="info-item">
                                <span class="info-label">Tên file:</span>
                                <span class="info-value">${data.filename}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Kích thước:</span>
                                <span class="info-value">${data.file_size} bytes</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Hash SHA-256:</span>
                                <span class="info-value">${data.file_hash}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Thời gian ký:</span>
                                <span class="info-value">${data.timestamp}</span>
                            </div>
                            
                            <h4 style="margin-top: 20px;">🔏 Chữ ký số ma thuật</h4>
                            <div class="signature-display">${data.signature}</div>
                            
                            <div style="margin-top: 20px;">
                                <button class="btn btn-success" onclick="downloadSignedPackage('${data.package_id}')">
                                    📦 Tải gói file đã ký
                                </button>
                            </div>
                        </div>
                    `;
                } else {
                    document.getElementById('signingResult').innerHTML = `
                        <div class="alert alert-danger">❌ ${data.error}</div>
                    `;
                }
            } catch (error) {
                document.getElementById('signingResult').innerHTML = `
                    <div class="alert alert-danger">❌ Lỗi: ${error.message}</div>
                `;
            }
            hideLoading();
        }

        async function downloadSignedPackage(packageId) {
            try {
                const response = await fetch(`/download_package/${packageId}`);
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `signed_package_${packageId}.json`;
                a.click();
                window.URL.revokeObjectURL(url);
            } catch (error) {
                alert('Lỗi khi tải file: ' + error.message);
            }
        }

        async function verifySignature() {
            const fileInput = document.getElementById('signedPackage');
            if (!fileInput.files[0]) {
                alert('Vui lòng chọn gói file đã ký!');
                return;
            }
            
            if (!currentKeys.public) {
                alert('Vui lòng load public key trước!');
                return;
            }

            showLoading();
            try {
                const formData = new FormData();
                formData.append('public_key', currentKeys.public);
                formData.append('package_file', fileInput.files[0]);

                const response = await fetch('/verify_signature', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                
                if (data.success) {
                    if (data.valid) {
                        document.getElementById('verificationResult').innerHTML = `
                            <div class="alert alert-success">
                                <strong>✅ Chữ ký ma thuật hợp lệ!</strong>
                            </div>
                            <div class="file-info">
                                <h4>📋 Thông tin file đã xác thực</h4>
                                <div class="info-item">
                                    <span class="info-label">Tên file:</span>
                                    <span class="info-value">${data.filename}</span>
                                </div>
                                <div class="info-item">
                                    <span class="info-label">Kích thước:</span>
                                    <span class="info-value">${data.file_size} bytes</span>
                                </div>
                                <div class="info-item">
                                    <span class="info-label">Hash SHA-256:</span>
                                    <span class="info-value">${data.file_hash}</span>
                                </div>
                                <div class="info-item">
                                    <span class="info-label">Thời gian ký:</span>
                                    <span class="info-value">${data.timestamp}</span>
                                </div>
                                
                                <div style="margin-top: 20px;">
                                    <button class="btn btn-success" onclick="downloadOriginalFile('${data.filename}', \`${data.content.replace(/\`/g, '\\`')}\`)">
                                        📄 Tải file gốc
                                    </button>
                                </div>
                            </div>
                        `;
                    } else {
                        document.getElementById('verificationResult').innerHTML = `
                            <div class="alert alert-danger">
                                <strong>❌ Chữ ký không hợp lệ hoặc file đã bị thay đổi!</strong>
                            </div>
                        `;
                    }
                } else {
                    document.getElementById('verificationResult').innerHTML = `
                        <div class="alert alert-danger">❌ ${data.error}</div>
                    `;
                }
            } catch (error) {
                document.getElementById('verificationResult').innerHTML = `
                    <div class="alert alert-danger">❌ Lỗi: ${error.message}</div>
                `;
            }
            hideLoading();
        }

        function downloadOriginalFile(filename, content) {
            const blob = new Blob([content], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename || 'original_file.txt';
            a.click();
            window.URL.revokeObjectURL(url);
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate_keys', methods=['POST'])
def generate_keys():
    try:
        # Tạo private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        # Lấy public key
        public_key = private_key.public_key()
        
        # Serialize keys thành PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        # Lưu vào storage
        storage['private_key'] = private_key
        storage['public_key'] = public_key
        
        return jsonify({
            'success': True,
            'private_key': private_pem,
            'public_key': public_pem
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/sign_file', methods=['POST'])
def sign_file():
    try:
        private_key_pem = request.form.get('private_key')
        text_content = request.form.get('text_content')
        file = request.files.get('file')
        
        # Load private key
        private_key = load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None
        )
        
        # Lấy nội dung file
        if text_content:
            content = text_content
            filename = f"text_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        elif file:
            content = file.read().decode('utf-8')
            filename = file.filename
        else:
            return jsonify({
                'success': False,
                'error': 'Không có nội dung để ký'
            })
        
        # Tính hash của nội dung
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        # Ký hash
        signature = private_key.sign(
            content.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Encode signature thành base64
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        # Tạo package ID
        package_id = hashlib.md5(f"{filename}{datetime.now()}".encode()).hexdigest()[:8]
        
        # Lưu signed package
        package_data = {
            'filename': filename,
            'content': content,
            'signature': signature_b64,
            'file_hash': content_hash,
            'file_size': len(content.encode('utf-8')),
            'timestamp': datetime.now().isoformat()
        }
        
        storage['signed_files'][package_id] = package_data
        
        return jsonify({
            'success': True,
            'package_id': package_id,
            'filename': filename,
            'signature': signature_b64,
            'file_hash': content_hash,
            'file_size': len(content.encode('utf-8')),
            'timestamp': package_data['timestamp']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/download_package/<package_id>')
def download_package(package_id):
    try:
        if package_id not in storage['signed_files']:
            return jsonify({'error': 'Package không tồn tại'}), 404
            
        package_data = storage['signed_files'][package_id]
        
        # Tạo file JSON để tải
        json_data = json.dumps(package_data, indent=2, ensure_ascii=False)
        
        return send_file(
            io.BytesIO(json_data.encode('utf-8')),
            as_attachment=True,
            download_name=f'signed_package_{package_id}.json',
            mimetype='application/json'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verify_signature', methods=['POST'])
def verify_signature():
    try:
        public_key_pem = request.form.get('public_key')
        package_file = request.files.get('package_file')
        
        if not package_file:
            return jsonify({
                'success': False,
                'error': 'Không có file package'
            })
        
        # Load public key
        public_key = load_pem_public_key(public_key_pem.encode('utf-8'))
        
        # Đọc package data
        package_data = json.loads(package_file.read().decode('utf-8'))
        
        content = package_data['content']
        signature_b64 = package_data['signature']
        
        # Decode signature
        signature = base64.b64decode(signature_b64)
        
        # Xác thực chữ ký
        try:
            public_key.verify(
                signature,
                content.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return jsonify({
                'success': True,
                'valid': True,
                'filename': package_data['filename'],
                'content': content,
                'file_hash': package_data['file_hash'],
                'file_size': package_data['file_size'],
                'timestamp': package_data['timestamp']
            })
            
        except Exception:
            return jsonify({
                'success': True,
                'valid': False
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
