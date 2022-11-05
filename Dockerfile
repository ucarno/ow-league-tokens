FROM python:3.10.7-slim

WORKDIR /app

COPY . .

RUN pip install -r ./requirements.txt

CMD [ "python", "./src/main.py", "nomenu", "--owl", "--owc", "--ids", "1123", "2432", "and so on..." ]
