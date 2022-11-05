# OWL Tokens and Contenders Skins farmer bot
This is a command line bot that "watches" league and contenders streams for you, without the need to worry about
missing some.
**No password or other sort of authentication required. Just your username.**

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)

---

![demo](https://i.ibb.co/7YCrt1x/demo.gif)

## How does this work?
This bot works by sending same tracking requests as a browser when you
watch league streams on an official Overwatch League website.

## Installation
1. Download zip archive from [releases page](https://github.com/ucarno/ow-league-tokens/releases/latest).
2. Extract `OverwatchTokenFarmer` directory wherever you want.

## Usage
1. Open `OverwatchTokenFarmer.exe` located in app directory.
2. Add an account.
3. Start bot.
4. Done! Bot is now working and next time it will remember your username.

## How to update
1. Download new release from [releases page](https://github.com/ucarno/ow-league-tokens/releases/latest).
2. Extract `OverwatchTokenFarmer` directory wherever you want.
3. Move your `config.json` file from old location to new location.

## Issues
Feel free to [create new issue](https://github.com/ucarno/ow-league-tokens/issues/new) if something is not working for you.
Please note that getting your tokens can take up to 48 hours and getting extra rewards could take even more time.

## Command line arguments
Program can be started without menu using `python main.py nomenu` command. But to do this you need to
configure program using menu or use arguments.

### Arguments
Arguments can be used only when starting program using `nomenu` command:
* `--owl` | `--no-owl` - either earn OWL Tokens or not - default is config value or `true` if not specified
* `--owc` | `--no-owc` - either earn Contenders Skins or not - default is config value or `true` if not specified
* `--ids` - list of integer IDs that will be used instead of IDs from config
(you can get your ID from [this API](https://playoverwatch.com/en-us/search/account-by-name/username/) 
or [manually](#manually-getting-your-account-id)).
* `--debug` | `--no-debug` - either enable or disable debug messages - default is config value or disabled if not specified

### Examples
* `python main.py nomenu --owl --no-owc` - earn OWL Tokens, do not earn Contenders Skins, IDs from config
* `python main.py nomenu --ids 1234 4567 8910` - `owl` and `owc` values from config, IDs from command line

### Manually getting your account ID
* The official Overwatch League website is storing account ID in a cookie named `account_id`. 
To get cookie's value, follow these steps:
1. Go to [https://overwatchleague.com/en-us](https://overwatchleague.com/en-us) and login using your Battle.net account
2. Open your browser's development tools (usually CTRL + Shift + I)
3. Depending on your browser, use one of the following options:
   * Chrome: Go to the Application tab -> Cookies -> `https://overwatchleague.com` -> Name: account_id
   * Firefox: Go to the Storage tab -> Cookies -> `https://overwatchleague.com` -> Name: account_id

## Docker
This application supports Docker! You can either build it by using the supplied `docker-compose.yml` or `Dockerfile`!
To use it, just clone this repository to your Docker Host.

### Docker Compose (recommended way if using Docker)
1. Make sure Docker Compose is installed on your machine! More info here: [Docker Compose](https://docs.docker.com/compose/).
2. Edit `docker-compose.yml` to include your IDs! Remove `owl`/`owc` options if needed (see [above](#arguments)).
3. `docker compose up -d` - the container is built by [Docker Compose](https://docs.docker.com/compose/) using the Dockerfile.
   * `docker compose ps` to verify if container is running!
   * `docker compose logs -f` to view container's logs.

### Dockerfile
1. Edit Dockerfile to include your IDs. Remove `owl`/`owc` options if needed (see [above](#arguments)).
2. `docker build -t ow-league-tokens .` to build container using the Dockerfile. 
3. `docker run -d ow-league-tokens:latest` to start new container using the image.
   * `docker container ls` to check if container is running
   * `docker logs ow-league-tokens` to view container's logs

## Contribution
Feel free to contribute!
* Thanks, [@nipser](https://github.com/nipser) and [@probablypablito](https://github.com/probablypablito) for Docker support!
* Also thanks to everyone for using this bot or leaving feedback!
