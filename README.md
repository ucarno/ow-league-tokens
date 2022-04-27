# Overwatch League Token Farmer Bot
This is a command line bot which "watches" league streams for you, 24/7, without the need to worry about missing some.
**No password or other sort of authentication needed. Just your username.**

![demo](https://i.ibb.co/P90V5pk/image.png)

## Installation
1. Download zip archive from [releases page](https://github.com/ucarno/ow-league-tokens/releases).
2. Extract `OverwatchTokenFarmer` directory wherever you want.
3. Optionally create desktop link to executable.

## Usage
1. Open `OverwatchTokenFarmer.exe` located in app directory.
2. Write your username and press Enter.
3. If there are more than one person with your username, select right one.
4. Done! Bot is now working and next time it will remember your username.

## Building executable
* Install necessary libs from `requirements.txt`
* Build using command `pyinstaller --noconfirm --name OverwatchTokenFarmer main.py`
