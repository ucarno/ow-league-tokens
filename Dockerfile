FROM python:3.11.3-slim

# Install Google Chrome and xvfb
# https://stackoverflow.com/questions/70955307/how-to-install-google-chrome-in-a-docker-container
RUN DEBIAN_FRONTEND=nointeractive && apt update -y && apt install -y wget xvfb gnupg2 && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && apt update && apt -y install google-chrome-stable

# Setup app
WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt

RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["/bin/sh", "-c", "./docker-entrypoint.sh"]
