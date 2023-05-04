# Overwatch League Tokens Bot
This is an app that watches League streams for you on YouTube! Still experimental, [issues](#possible-issues) may occur.

Also, no contenders skins support as Contenders skins are earned via Twitch drops - not watching on YouTube.
To earn Contenders skins in the same automated fashion, try [this](https://github.com/DevilXD/TwitchDropsMiner) app.

<div align="center">

[![Support my work](https://i.imgur.com/NOoWZ8G.png)](https://ko-fi.com/ucarno)

</div>

## Features
* Automatic live broadcast detection — don't worry about "when" and "where"
* Multiple accounts support — you just need multiple Google accounts
* Headless mode — see only a console window (as before) if an extra Chrome window is bothering you
* No sound — Chrome will be muted entirely

## Planned Features
* Automatically set broadcast quality to 144p, so it doesn't consume a lot of bandwidth

## Installation
### Windows
1. Download the latest version [here](https://github.com/ucarno/ow-league-tokens/releases/latest).
2. Unpack zip anywhere you want.
3. Run `ow-league-tokens.exe` to open the app.
4. Ignore Windows Defender's complaints about "unknown publisher".

### Linux
You need to have GUI to log into your Google account(s). If you don't have GUI and can't install/use it, then
do everything on another machine with GUI and copy `profiles/` directory to your Linux installation.
1. Install Python 3.10+ or make sure your Python version is at least 3.10 (`python --version`)
2. Clone this repository using `git clone https://github.com/ucarno/ow-league-tokens`
3. Go to app's directory using `cd ow-league-tokens`
4. Install dependencies via `pip3 install -r requirements.txt`
5. Run `python3 main.py`
6. Add the required number of profiles using a menu (single profile for single Battle.net/Google account).

## Usage
This bot uses [Chrome Driver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
under the hood that requires Google Chrome to be installed.

Make sure you have Google Chrome installed, and it is latest version;
you can check your Chrome version here: `chrome://version/`; and force Chrome update here: `chrome://settings/help`

Also make sure you have connected Battle.net account(s) to Google account(s)
on [this](https://www.youtube.com/account_sharing) page!

1. Start the bot using a first menu option.
You should see Chrome window(s) opening, with text in console guiding you.
2. When you see Google's login screen - log in to your account.
3. Then you should be redirected to the YouTube page, and the bot will confirm that everything is OK by writing a success
message in the console and redirecting you to the home screen.

## Updating
Sometimes you may see "new version available" message in your console. It probably means that I've fixed something.

Bot can be updated without losing your profile(s) data (no need to login into Google again):
1. Download the latest version from [here](https://github.com/ucarno/ow-league-tokens/releases/latest).
2. Unpack it anywhere you want.
3. Move `config.json` file and `profiles` directory from an old version to new one.
4. Done!

## Command-line Arguments
* Use `--nomenu` (or `Start_Without_Menu.bat` on Windows) to run the app without a menu using your `config.json` file.

## Possible Issues
If you encounter any problems, **make sure your Chrome is the latest version** —
you can force Chrome update here: `chrome://settings/help`!

### Stream window is randomly unloading
This may happen, for example, in non-headless mode when you collapse a Chrome window.
It will be fixed in later release.

### Google profile is not restored after logging into account and re-opening the bot
If this happens to you, then after logging into Google account, don't instantly close and re-open the bot.
Let Chrome be open for a few minutes, may be try browsing your gmail or open a YouTube video.

### Google randomly logs you out of an account
This may happen if Google thinks your activity is suspicious (automated). Didn't happen for me, but may happen for you.
You can check if everything is OK by restarting an app. If you see "Authentication check passed." Message then
everything is working as expected. I will look into this issue further and implement some fixes and checkers.

### Bot is watching ALL owl streams, not just those which give tokens
At the current state, bot will watch ALL streams on OWL channel, no matter if they give tokens or not.
I may implement watching only token-giving streams in the future.

### Anything else?
Then [open new issue](https://github.com/ucarno/ow-league-tokens/issues/new) and I will look into this.

## Contribution
Feel free to contribute by
[opening new issue](https://github.com/ucarno/ow-league-tokens/issues/new),
[making a pull request](https://github.com/ucarno/ow-league-tokens/pulls) or
[buying me a coffee](https://ko-fi.com/ucarno).
Thanks to everyone for using this bot, contributing and/or leaving feedback!

## Update History
### v2.0.1
* Improved menu experience
* Minor fixes

### v2.0.0 — The "YouTube" Update
* Bot now works through YouTube

## Disclaimer
This app is not affiliated with Blizzard Entertainment, Inc. All trademarks are the properties of their respective owners.

2023 Blizzard Entertainment, Inc. All rights reserved.
