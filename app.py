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
    
    file = request.files['file']
    img_path = "raw.png"
    processed_path = "processed.png"
    file.save(img_path)

    try:
        # --- 画像の前処理 (V1.50) ---
        with Image.open(img_path) as img:
            img = img.convert('L')
            # ノイズ除去と、数字のセグメント（棒）を繋げる処理
            img = img.filter(ImageFilter.MedianFilter(size=3))
            img = img.filter(ImageFilter.MaxFilter(size=3))
            # 再度2値化して輪郭をはっきりさせる
            img = img.point(lambda x: 255 if x > 128 else 0)
            img.save(processed_path)

        # --- SSOCR実行 (厳格設定) ---
        # -d -1: 桁数自動判定
        # -S: 数字を結合
        # omit_decimal: 小数点を無視
        # -t 25: 内部スキャンの感度を調整
        # ignore_at_least 1: 1ピクセル以下のゴミを無視
        process = subprocess.run(
            [
                'ssocr', 
                '-d', '-1', 
                '-S', 
                '-t', '25',
                'omit_decimal', 
                'ignore_at_least', '1', 
                processed_path
            ],
            capture_output=True,
            text=True
        )
        
        # SSOCRの生の出力を取得
        raw_output = process.stdout.strip()
        
        # デバッグ用ログ (RenderのLogsで見れます)
        print(f"SSOCR Raw Output: '{raw_output}'")
        
        # 数字だけを抽出（記号が含まれていても数字のみ取り出す）
        number_str = "".join(filter(str.isdigit, raw_output))
        
        # もし数字が空なら None を返す
        if not number_str:
            return jsonify({"number": None, "raw": raw_output, "status": "no_digits"}), 200
            
        return jsonify({
            "number": number_str,
            "raw": raw_output
        })
        
    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Renderの環境変数PORTに対応
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
