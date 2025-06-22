FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y \
    ffmpeg libsm6 libxext6 libgl1 git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

docker build -t smart-traffic-app .
docker run -p 8501:8501 smart-traffic-app
