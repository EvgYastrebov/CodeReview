FROM python:3.8

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8888

CMD ["python", "app.py", "--ip", "0.0.0.0", "--port", "8888", "--no-browser"]