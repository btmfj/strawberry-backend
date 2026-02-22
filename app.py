import os
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    img_path = "temp.png"
    file.save(img_path)

    try:
        # 修正: subprocess.run を使い、終了コードを無視して出力を取得する
        # -d -1 は桁数を自動認識させる
        process = subprocess.run(
            ['ssocr', '-d', '-1', 'threshold', '128', img_path],
            capture_output=True,
            text=True
        )
        
        # 標準出力から読み取った数字を取得
        number_str = process.stdout.strip()
        
        # SSOCRが何も出力しなかった場合
        if not number_str:
            return jsonify({"number": None, "status": "no_digits_found"}), 200
            
        return jsonify({"number": number_str})
        
    except Exception as e:
        # システムエラー（ssocr未インストール等）
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Renderのポート指定に対応
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
