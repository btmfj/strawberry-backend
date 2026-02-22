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
        # 修正ポイント: 
        # -m 1: 膨張処理（文字を太らせて隙間を埋める）
        # -T: 反転（2値化後の白黒が逆の場合の保険、今回は不要ですが指定を安定させます）
        # -S: 数字のみ結合
        process = subprocess.run(
            ['ssocr', '-d', '-1', '-S', 'omit_decimal', '-m', '1', 'threshold', '128', img_path],
            capture_output=True,
            text=True
        )
        
        # 不要な文字を除去して数字だけ抽出
        raw_output = process.stdout.strip()
        number_str = "".join(filter(str.isdigit, raw_output))
        
        if not number_str:
            return jsonify({"number": None, "status": "no_digits"}), 200
            
        return jsonify({"number": number_str})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
