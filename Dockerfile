# ベースイメージ
FROM python:3.12-slim

# 作業ディレクトリ
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    # 不要なキャッシュを削除
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app/app.py", "--server.address=0.0.0.0", "--server.port=8501"]

# 日本語フォントのインストール
RUN apt update && apt install -y fonts-ipafont fonts-ipaexfont && apt-get clean