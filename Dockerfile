FROM python:3.11.3-slim

# Install Google Chrome
# https://stackoverflow.com/questions/70955307/how-to-install-google-chrome-in-a-docker-container
ENV DEBIAN_FRONTEND noninteractive
RUN apt install -y wget
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
RUN apt update && apt -y install google-chrome-stable

# Virtual Display
# https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/743#issuecomment-1366847803
ENV DISPLAY :1
RUN apt install xvfb -y && Xvfb $DISPLAY -screen $DISPLAY 1280x1024x16 &

# Setup app
WORKDIR /app
COPY ./src .
RUN pip3 install -r requirements.txt

CMD ["python", "main.py", "--nomenu", "--nowait", "--profiles", "default"]
