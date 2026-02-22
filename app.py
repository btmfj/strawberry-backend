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
        with Image.open(img_path) as img:
            img = img.convert('L')
            # 1. 小さなノイズを消す (MedianFilter)
            img = img.filter(ImageFilter.MedianFilter(size=3))
            # 2. 数字の隙間を埋めるために少し太らせる (MaxFilter)
            img = img.filter(ImageFilter.MaxFilter(size=3))
            # 3. 境界をはっきりさせる
            img = img.point(lambda x: 255 if x > 128 else 0)
            img.save(processed_path)

        # SSOCR実行オプションをさらに厳選
        # -S -S : 数字を可能な限り結合
        # -d -1 : 桁数自動
        # omit_decimal : 小数点を無視
        process = subprocess.run(
            ['ssocr', '-d', '-1', '-S', '-S', 'omit_decimal', processed_path],
            capture_output=True,
            text=True
        )
        
        # 取得した文字列から数字だけを抜き出す
        raw_output = process.stdout.strip()
        number_str = "".join(filter(str.isdigit, raw_output))
        
        # デバッグ：何が読み取れたかを標準出力に出す
        print(f"Server recognized: {number_str} (Raw: {raw_output})")
        
        return jsonify({"number": number_str if number_str else None})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
