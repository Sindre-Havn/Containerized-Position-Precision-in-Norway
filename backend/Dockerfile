# Build app (frontend)
#FROM node:16-alpine
#WORKDIR /app
#COPY . /app
#RUN npm install
#RUN npm start


# Build the api (backend)
FROM python:3.10-slim-buster

WORKDIR /api
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["gunicorn", "-w", "1", "-t", "0", "-b", "0.0.0.0:5000", "app:app"]