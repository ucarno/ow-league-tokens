FROM python:3.10.7-slim

WORKDIR /app

COPY . .

RUN pip install -r ./requirements.txt

CMD [ "python", "./main.py", "nomenu", "--owl", "--owc", "--ids", "id1", "and so on" ]
