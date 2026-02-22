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
        # SSOCRのオプションを調整：
        # -d -1: 桁数自動
        # -D: 行全体のデバッグ表示を抑制
        # -f white: 黒背景に白文字として処理（2値化済みなので）
        # -S: 数字のみ（小数点やカンマをスキップして結合）
        # omit_decimal: 小数点を無視する（秤の0.1gのドット対策）
        process = subprocess.run(
            ['ssocr', '-d', '-1', '-S', 'omit_decimal', 'threshold', '128', img_path],
            capture_output=True,
            text=True
        )
        
        # 読み取った文字列から数字以外（もしあれば）を除去
        raw_output = process.stdout.strip()
        number_str = "".join(filter(str.isdigit, raw_output))
        
        # 小数点以下の桁がある秤（0.0g表記）の場合は、ここで調整が必要です。
        # 今回は整数（g単位）として処理します。
        
        if not number_str:
            return jsonify({"number": None, "status": "no_digits"}), 200
            
        return jsonify({"number": number_str})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
