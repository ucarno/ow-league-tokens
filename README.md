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
(you can get your ID from this API: https://playoverwatch.com/en-us/search/account-by-name/username/)

### Examples
* `python main.py nomenu --owl --no-owc` - earn OWL Tokens, do not earn Contenders Skins, IDs from config
* `python main.py nomenu --ids 1234 4567 8910` - `owl` and `owc` values from config, IDs from command line