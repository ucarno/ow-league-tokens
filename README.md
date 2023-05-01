# Overwatch League Tokens Bot
This is an app that watches League streams for you on YouTube! Still experimental, [issues](#possible-issues) may occur.

Also, no contenders skins support as contenders skins are earned via Twitch drops - not watching on YouTube.
To earn contenders skins in the same automated fashion, use [this](https://github.com/DevilXD/TwitchDropsMiner).

<div align="center">

[![Buy me a coffee](https://i.imgur.com/NOoWZ8G.png)](https://ko-fi.com/ucarno)

</div>

## Features
* Automatic live broadcast detection - don't worry about "when" and "where"
* Multiple accounts support - you just need multiple Google accounts
* Headless mode - see only console window (as before) if extra Chrome window is bothering you
* No sound - Chrome will be muted entirely

## Planned Features
* Automatically set broadcast quality to 144p, so it does not consume a lot of bandwidth

## Installation
### Windows
1. Download latest version [here](https://github.com/ucarno/ow-league-tokens/releases/latest).
2. Unpack zip anywhere you want.
3. Run `ow-league-tokens.exe` to open the app.
4. Ignore Window Defender's complaints about "unknown publisher".

### Linux
You need to have GUI to log into your Google account(s). If you don't have GUI and can't install/use it, then
do everything on another machine with GUI and copy `profiles/` directory to your Linux installation.
1. Install Python 3.10+ or make sure your Python version is at least 3.10 (`python --version`)
2. Clone this repository using `git clone https://github.com/ucarno/ow-league-tokens`
3. Go to app's directory using `cd ow-league-tokens`
4. Install dependencies via `pip3 install -r requirements.txt`
5. Run `python3 main.py`
6. Add required amount of profiles using menu (single profile for single Battle.net/Google account).

## Usage
Make sure you have Google Chrome installed.
This bot uses [Chrome Driver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
under the hood that requires Google Chrome to be installed.

Also make sure you have connected Battle.net account(s) to Google account(s)
on [this](https://www.youtube.com/account_sharing) page!

1. Start the bot using first menu option.
You should see Chrome window(s) opening, with text in console guiding you.
2. When you see Google's login screen - log in to your account.
3. Then you should be redirected to YouTube page and the bot will confirm that everything is OK by writing a success
message in console and redirecting you to home screen.

## Updating
Sometimes you may see "new version available" message in your console. It probably means that I have fixed something.

Bot can be updated without losing your profile(s) data (no need to login into Google again):
1. Download latest version from [here](https://github.com/ucarno/ow-league-tokens/releases/latest).
2. Unpack it anywhere you want.
3. Move `config.json` file and `profiles` directory from old version to new one.
4. Done!

## Command-line Arguments
* Use `--nomenu` (or `Start_Without_Menu.bat` on Windows) to run the app without menu using your `config.json` file.

## Possible Issues
### Stream window randomly unloading
This may happen for example in non-headless mode when you collapse Chrome window.
Will be fixed in later release.

### Google can log you out of account
This may happen if Google thinks your activity is suspicious (automated). Didn't happen for me, but may happen for you.
You can check if everything is OK by restarting an app. If you see "Authentication check passed." message then
everything is working as expected. I will look into this issue further and implement some fixes and checkers.

### Anything else?
Then [open new issue](https://github.com/ucarno/ow-league-tokens/issues/new) and I will look into this.

## Contribution
Feel free to contribute by
[opening new issue](https://github.com/ucarno/ow-league-tokens/issues/new),
[making a pull request](https://github.com/ucarno/ow-league-tokens/pulls) or
[buying me a coffee](https://ko-fi.com/ucarno).
Also thanks to everyone for using this bot and leaving feedback!

## Disclaimer
This app is not affiliated with Blizzard Entertainment, Inc. All trademarks are the properties of their respective owners.

2023 Blizzard Entertainment, Inc. All rights reserved.