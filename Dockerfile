FROM python:3.9-slim

# SSOCRに必要な依存ライブラリをインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    libimlib2-dev \
    libx11-dev \
    make \
    wget \
    && rm -rf /var/lib/apt/lists/*

# SSOCRのソースコードをダウンロードしてビルド
RUN wget https://www.unix-ag.uni-kl.de/~auerswal/ssocr/ssocr-2.23.1.tar.bz2 \
    && tar xjf ssocr-2.23.1.tar.bz2 \
    && cd ssocr-2.23.1 \
    && make \
    && make install

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# サーバー起動 (gunicornを使用)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
