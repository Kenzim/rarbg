FROM python:3.9.6-slim-buster
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 ca-certificates tesseract-ocr -y \
    && rm -rf /var/lib/apt/lists/* && update-ca-certificates
WORKDIR /app/src
COPY requirements.txt /app/src/
RUN pip install -r requirements.txt
COPY api.py /app/src/
COPY rarbg.py /app/src/
CMD ["python3", "api.py"]