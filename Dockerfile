FROM python:3.10-slim
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0
WORKDIR /app
COPY . .
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 5000
CMD ["gunicorn", "backend.app:app", "--bind", "0.0.0.0:5000"]