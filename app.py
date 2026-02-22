import os
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageFilter

app = Flask(__name__)
CORS(app)

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    
    # 秤の種類を取得 (integer or decimal)
    scale_type = request.form.get('scale_type', 'integer')
    file = request.files['file']
    img_path = "raw.png"
    processed_path = "processed.png"
    file.save(img_path)

    try:
        # 画像の前処理
        with Image.open(img_path) as img:
            img = img.convert('L')
            img = img.filter(ImageFilter.MedianFilter(size=3))
            img = img.filter(ImageFilter.MaxFilter(size=3))
            img = img.point(lambda x: 255 if x > 128 else 0)
            img.save(processed_path)

        # SSOCR実行
        process = subprocess.run(
            ['ssocr', '-d', '-1', '-S', '-t', '25', 'omit_decimal', 'ignore_at_least', '1', processed_path],
            capture_output=True, text=True
        )
        
        raw_output = process.stdout.strip()
        number_str = "".join(filter(str.isdigit, raw_output))
        
        if not number_str:
            return jsonify({"number": None, "raw": raw_output}), 200
        
        # 数値変換ロジック
        val = float(number_str)
        if scale_type == 'decimal':
            val = val / 10.0  # 431 -> 43.1
        else:
            val = int(val)    # 整数として扱う

        return jsonify({
            "number": val,
            "raw": raw_output,
            "scale_type": scale_type
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
