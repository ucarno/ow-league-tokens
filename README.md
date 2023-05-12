# Overwatch League Tokens Bot

This is an app that watches League streams for you on YouTube!
Now less experimental, but [issues](#known-issues) may still occur.

Uses actual browser (Google Chrome or Brave) to watch streams.

**No Contenders skins support** as Contenders skins are earned via Twitch drops - not watching on YouTube.
To earn Contenders skins in the same automated fashion, try [this](https://github.com/DevilXD/TwitchDropsMiner) app.

<div align="center">

[![Support my work](https://i.imgur.com/NOoWZ8G.png)](https://ko-fi.com/ucarno)
[![Join Discord](https://i.imgur.com/dUQDNfo.png)](https://discord.gg/kkq2XY4cJM)
[![Hire Me on Upwork](https://i.imgur.com/3jnH5ln.png)](https://www.upwork.com/freelancers/~012888e364d51bc0b2)

</div>

## Features
* Automatic live broadcast detection — don't worry about "when" and "where"
* Multiple accounts support — you just need multiple Google accounts
* Headless mode — see only a console window ([as before](https://github.com/ucarno/ow-league-tokens/tree/legacy)) if extra Chrome window is bothering you
* No sound — Chrome will be muted entirely
* Easy setup on Windows, macOS and Linux (GUI)

## Planned Features
* Automatically set broadcast quality to 144p, so it doesn't consume a lot of bandwidth
_(current workaround: set stream quality by yourself, YouTube should remember your choice)_
* Script for updating
* ~~Mobile phones support~~

## You need a browser for this app to work!
This bot uses [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
under the hood that requires either Google Chrome or Brave to be installed.

To use Brave (or if your Google Chrome installation could not be found),
set `chromium_binary` field in `config.json` to your browser's executable path.

Firefox is not supported
(support can be technically implemented, but Google will be able to detect automation).

## Installation
### Windows, macOS, Linux (GUI)
1. Download the latest executable for your OS [here](https://github.com/ucarno/ow-league-tokens/releases/latest).
2. Unpack zip anywhere you want.
3. Run `ow-league-tokens` to open the app.
4. Windows: Ignore Windows Defender's complaints about "unknown publisher".
Also, you may need to add this app to your antivirus exceptions.

### Linux (no GUI)
**You need to have GUI to log into your Google account(s)!**
There is no good way to run this app without a GUI.
Best option would be to just install GUI on your Linux and [log in using GUI](#windows-macos-linux-gui).

**You have been warned!** If you want to play with it, then see instructions for [Docker](#docker).

## Usage
**Make sure you have connected Battle.net account(s) to Google account(s)
on [this](https://www.youtube.com/account_sharing) page!**

1. Start the bot using a first menu option.
You should see Chrome window(s) opening, with text in console guiding you.
2. When you see Google's login screen - log in to your account.
3. Then you should be redirected to the YouTube page, and bot will confirm that everything is OK by writing a success
message in console.

## Updating
Sometimes you may see "new version available" message in your console. It probably means that I've fixed something.

Bot can be updated without losing your profile(s) data (no need to login into Google again):
1. Download the latest version from [here](https://github.com/ucarno/ow-league-tokens/releases/latest).
2. Either:
   * Unpack it anywhere you want and move `config.json` file and `profiles` directory from an old version to new one...
   * or move new files to old directory, replacing old files with new ones.

## Command-line Arguments
* Use `--nomenu` (or `Start_Without_Menu.bat` on Windows) to run the app without a menu using your `config.json` file.
* Use `--nowait` for a script to close immediately after an error
(without `--nowait` you have to manually press Enter for script to close after an error) 
* Use `--profiles` to specify profiles you want this app to use (works only with `--nomenu` argument).
Usage: `--nomenu --profiles my-main friends-acc`
* There is also a specific flag for Docker that may solve some issues under Linux: `--docker`
  (includes some Chromium flags, works only with `--nomenu` flag)

## Docker
This application supports Docker (sort of, I couldn't make profiles reusable),
track progress on Docker support [here](https://github.com/ucarno/ow-league-tokens/issues/63)!
You can either build it by using the supplied `docker-compose.yml` or `Dockerfile`.

1. Clone this repository using `git clone https://github.com/ucarno/ow-league-tokens`
2. Go to app's directory using `cd ow-league-tokens`
3. Edit `docker-entrypoint.sh` to include your profile names if needed.

### Docker Compose (recommended way if using Docker)
1. Make sure Docker Compose is installed on your machine! More info [here](https://docs.docker.com/compose/).
2. `docker compose up -d` - build container using the Dockerfile
   * `docker compose ps` to verify if container is running
   * `docker compose logs -f` to view container's logs

### Dockerfile
1. `docker build -t ow-league-tokens .` to build container using the Dockerfile. 
2. `docker run -d -v ./src/profiles:/profiles ow-league-tokens:latest` to start new container using the image.
   * `docker container ls` to verify if container is running
   * `docker logs ow-league-tokens` to view container's logs

## Known Issues
### Google may log you out of an account
It just may happen to you.
If you restart the app and see green "Authentication check has been passed" text, then everything is OK.

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
Thanks to everyone for using this bot, contributing, leaving feedback and
helping other people in [our Discord](https://discord.gg/kkq2XY4cJM)!

## Update History
### v2.0.4
* Fixed stuck Brave browser headless windows not closing on app start
* "Fixed" some weird non-descriptive errors from crashing app by restarting the entire app when it crashes.
_Probably need to migrate to Playwright to actually solve these issues._
* Finally added Docker support (good luck)
* Added build scripts for Windows, Linux and macOS
* Disabled `HardwareMediaKeyHandling` feature which captured hardware media key presses
  (you need to delete your `config.json` file for this to take effect).
* Executables now ship with new sick icon: ![Overwatch League Tokens](assets/icon.ico)

### v2.0.3
* _(Probably)_ Fixed a crash when trying to run multiple headless profiles
* Fixed an issue when app would not start if there are headless Chrome windows left from previous run (Windows only)
* Now showing better error when browser executable can't be found
([related](https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/497))

### v2.0.2
* App now waits for `Enter` key press after exception (can be disabled via `--nowait` argument)
* Fixed issue with app crashing when Chrome is not the last version
* Stream will now be refreshed every 15 minutes in case it crashes
* Added experimental support of other Chromium-based browsers (via `chromium_binary` field in `config.json`)
* Chromium flags can be now modified using `chromium_flags` field in `config.json`

### v2.0.1
* Improved menu experience
* Minor fixes

### v2.0.0 — The "YouTube" Update
* Bot now works through YouTube

### v1.x.x
* [Legacy version](https://github.com/ucarno/ow-league-tokens/tree/legacy) worked using OWL website

## Disclaimer
This app is not affiliated with Blizzard Entertainment, Inc. All trademarks are the properties of their respective owners.

2023 Blizzard Entertainment, Inc. All rights reserved.
