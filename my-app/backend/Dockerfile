FROM python:3.10

# Install espeak system dependency
RUN apt-get update && apt-get install -y espeak

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=autodialer.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["python", "autodialer.py"]
