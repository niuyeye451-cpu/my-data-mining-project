FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir \
    scikit-learn opencv-python-headless matplotlib pillow numpy

COPY train.py .

CMD ["python", "train.py"]
