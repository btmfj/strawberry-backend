import os
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  // フロントエンド(GitHub Pages)からのアクセスを許可

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    
    file = request.files['file']
    img_path = "temp.png"
    file.save(img_path)

    try:
        # SSOCRコマンドの実行 (2値化済み画像を送る想定なので -d -1 を推奨)
        # -d -1: 自動判別, -D: デバッグ表示なし
        result = subprocess.check_output(
            ['ssocr', 'threshold', '128', img_path], 
            stderr=subprocess.STDOUT
        )
        number = result.decode().strip()
        return jsonify({"number": number})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
