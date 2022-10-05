FROM python:3.10.7-slim

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "main.py", "nomenu"]
