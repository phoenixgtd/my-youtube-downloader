FROM python:3.10-slim

# تحديث النظام وتثبيت ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
