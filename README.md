# Game Alert

## FAQ:
### What is this?
> This is a bot that will notify you for free games
### What stores does it support?
> It's supports Steam and Epic Games at the moment.

## How to start the bot notifying?
> Simply use `/set_channel` slash command and set channel where you want to be notified.

## Installation for Windows:
1. Download and install [Python](https://www.python.org/downloads/).
2. Download and unarchive repo.
3. Open CMD and change the directory to folder you just unarchived.
4. Open `.env` file and replace `TOKEN` with your bot token ([guide to how create bot](https://discord.com/developers/docs/getting-started#creating-an-app))
5. Type in CMD:
    ```
    pip install -r requirements.txt
    ```
    ```
    python main.py
    ```
    And you're done!
## Installation for Linux
1. Open CMD and type:
    ```
    sudo apt install python3 python-pip
    ```
    ```
    git clone https://github.com/qwixck/game-alert.git
    ```
    ```
    cd game-alert
    ```
2. Open `.env` file and replace `TOKEN` with your bot token ([guide to how create bot](https://discord.com/developers/docs/getting-started#creating-an-app))
3. Type in CMD:
    ```
    pip install -r requirements.txt
    ```
    ```
    python3 main.py
    ```
    And you're done!