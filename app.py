import os
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageFilter, ImageOps

app = Flask(__name__)
CORS(app)

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    
    file = request.files['file']
    img_path = "raw.png"
    processed_path = "processed.png"
    file.save(img_path)

    try:
        # --- 画像の前処理 ---
        with Image.open(img_path) as img:
            img = img.convert('L')  # グレースケール
            # 少しぼかして、2値化し直すことで「棒の隙間」を埋める
            img = img.filter(ImageFilter.MaxFilter(3)) # 白い部分(数字)を広げる
            img.save(processed_path)

        # SSOCR実行
        # -t 50: 内部しきい値を下げて認識しやすくする
        # -I: 反転が必要な場合のため（今回はフロントで2値化済みなのですぐ読めるはず）
        process = subprocess.run(
            ['ssocr', '-d', '-1', '-S', 'omit_decimal', 'processed.png'],
            capture_output=True,
            text=True
        )
        
        number_str = "".join(filter(str.isdigit, process.stdout.strip()))
        
        # デバッグ用に出力をログに出す
        print(f"SSOCR Raw Output: {process.stdout.strip()}")
        
        if not number_str:
            return jsonify({"number": None, "status": "not_found"}), 200
            
        return jsonify({"number": number_str})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
