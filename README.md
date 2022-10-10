# OWL Tokens and Contenders Skins farmer bot
This is a command line bot that "watches" league and contenders streams for you, without the need to worry about
missing some.
**No password or other sort of authentication required. Just your username.**

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)

---

![demo](https://i.ibb.co/7YCrt1x/demo.gif)

## Installation
1. Download zip archive from [releases page](https://github.com/ucarno/ow-league-tokens/releases/latest).
2. Extract `OverwatchTokenFarmer` directory wherever you want.

## Usage
1. Open `OverwatchTokenFarmer.exe` located in app directory.
2. Add an account.
3. Start bot.
4. Done! Bot is now working and next time it will remember your username.

## Command line arguments
Program can be started without menu using `python main.py nomenu`. But to do this you need to
configure program using menu or use arguments.

### Arguments
Arguments can be used only when starting program using `nomenu` command:
* `--owl` | `--no-owl` - either earn OWL Tokens or not - default is config value or `true` if not specified
* `--owc` | `--no-owc` - either earn Contenders Skins or not - default is config value or `true` if not specified
* `--ids` - list of integer IDs that will be used instead of IDs from config
(you can get your ID from this API: https://playoverwatch.com/en-us/search/account-by-name/username/) or [manually](#manually-getting-the-account-id).

### Examples
* `python main.py nomenu --owl --no-owc` - earn OWL Tokens, do not earn Contenders Skins, IDs from config
* `python main.py nomenu --ids 1234 4567 8910` - `owl` and `owc` values from config, IDs from command line

### Manually getting the Account-ID
* The official Overwatch-League-Website is saving the account_id in a cookie with the same name. To access the cookie's data, use the following steps:
1. Go to [https://overwatchleague.com/en-us](https://overwatchleague.com/en-us) and login with your Battle.Net-Account
2. Open your browser's development tools (usually CTRL + Shift + i)
3. Depending on your browser, use one of the following options:
* Chrome: Go to the Application Tab --> Cookies --> https://overwatchleague.com --> Name: account_id
* Firefox: Go to the Storage Tab --> Cookies --> https://overwatchleague.com --> Name: account_id

## Docker
This application supports Docker! You can either build it by using the supplied docker-compose.yml or Dockerfile!
To use, just clone this repository to your Docker Host.

### Docker Compose (Recommended way if using Docker)
1. Make sure Docker Compose is installed on your machine! More info here: [Docker Compose](https://docs.docker.com/compose/).
2. Edit docker-compose.yml to include your IDs! Remove owl / owc options if required (see [above](#arguments)).
3. `docker compose up -d` - The container is build by [Docker Compose](https://docs.docker.com/compose/) using the Dockerfile.
4. `docker compose ps` - verify the container is running!
5. `docker compose logs -f` - If you want to view the container's log.

### Dockerfile
1. Edit the Dockerfile to include your IDs. Remove owl / owc options if required (see [above](#arguments)).
2. `docker build -t ow-league-tokens .` - Will build the container using the Dockerfile. 
3. `docker run -d ow-league-tokens:latest` - You can now start a new container using the image.
4. `docker container ls` - To check if the container is running. 
5. `docker logs ow-league-tokens` - If you want to view the container's log.
