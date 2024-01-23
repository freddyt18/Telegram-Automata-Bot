# Automata Telegram Bot

Automata Telegram Bot is a small application that runs entirely within the Telegram app. It allows users to create and manipulate finite automata machines using simple commands. Users can design, edit, delete, and view their own machines, as well as convert them between different types and perform operations on them. For example, users can check if a string belongs to a language recognized by a machine, transform a nondeterministic finite automaton (NFA) into a deterministic one (DFA), or minimize a DFA. Automata Telegram Bot is an educational and fun tool for anyone interested in learning more about finite automata theory and practice.

- Watch this video: https://clipchamp.com/watch/NC3j3ON1flp

- Bot Usage: https://t.me/automata_cs_gen7_bot

- Technical Report: https://confluence.external-share.com/content/63123/technical_report_telegram_automata

## Prerequisites

To use Automata Telegram Bot, you need to have:

- A Telegram account and A Bot ([Learn how to create a bot here](https://core.telegram.org/bots#how-do-i-create-a-bot:~:text=contact%20%40BotSupport.-,How%20Do%20I%20Create%20a%20Bot%3F,-Creating%20Telegram%20bots))
- A Database Server with __MySQL Driver__
- Python 3.10 or higher

## Installation

There are three ways to install and run Automata Telegram Bot:

### Option 1: Clone the repository

1. Clone this repository: `git clone https://github.com/freddyt18/Telegram-Automata-Bot.git`
2. Add your bot token and database credentials to the `.env` file (See Option 2)
3. Install the requirements: `pip install -r requirements.txt`
4. Run the main script: `python main.py`

### Option 2: Pull the image from Docker Hub

1. Pull the image from Docker Hub: 
```docker
docker pull freddyt18/cadt_cs_gen7_telegram_automata
```
2. Run the image with your bot token and the database credentials as environment variables: 
```docker
docker run --name automata_telegram_bot \
-e Telegram_Dev="<your_telegram_api_token>" \
-e DATABASE_HOST="<your_database_host>" \
-e DATABASE_USER="<your_database_username>" \
-e DATABASE_PASS="<your_database_password>" \
-e DATABASE_NAME="<your_database>" \
-d freddyt18/cadt_cs_gen7_automata_telegram
```

### Option 3: Docker Compose

1. Store this in a __docker-compose.yml__ file and edit variable __Telegram_Dev__ with your telegram token in the __app.environment__
```
version: "3.9"
services:
  db:
    container_name: mysql_for_automata
    image: mysql
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: "default"
      MYSQL_DATABASE: "automata"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 15
    networks:
      automata_network:
        aliases:
          - db
  app:
    container_name: telegram_automata
    image: freddyt18/cadt_cs_gen7_telegram_automata
    depends_on:
      db:
        condition: service_healthy
    environment:
      - Telegram_Dev=default_value
      - DATABASE_HOST=db
      - DATABASE_USER=root
      - DATABASE_PASS=default
      - DATABASE_NAME=automata
    restart: always
    networks:
      automata_network:

networks:
  automata_network:
```
2. Run the compose command
```
docker compose up -d
```

## Usage

To use Automata Telegram Bot, you need to start a conversation with your bot on Telegram. You can use the following commands:

- `/start` - Start the bot and show the welcome message
- `/help` - Show the help message with all available commands
- `/design` - Design and create a new finite automaton
- `/edit` - Edit existing finite automata - (*Command is still in development*)
- `/delete` - Delete existing finite automata
- `/my_machines` - View all designed finite automata
- `/type` - Check the type of any finite automaton
- `/check_string` - Check any string's (or multiple) acceptance by one or more finite automata
- `/nfa_to_dfa` - Convert existing NFA to DFA
- `/minimize_dfa` - Perform a minimization on the chosen DFA

For more details on how to use each command, please refer to the help message.

## Contributors
- 🚀 Keopitou Doung - Product Manager
  - [GitHub](https://github.com/freddyt18)
  - [LinkedIn](https://www.linkedin.com/in/keopitou-doung-62a02023a/)
- 🐍 Samedy Phin - Python Developer 
  - [GitHub](https://github.com/Samedy1)
  - [Facebook](https://www.facebook.com/samedy.phin.5?mibextid=ZbWKwL)
- 🐍 Sereysothirich Peang - Python Developer
  - [GitHub](https://github.com/Sothirich)
  - [Facebook](https://web.facebook.com/sothirich)
- 🐍 Raksa Kun - Python Developer
  - [GitHub](https://github.com/ahRakSasa)
  - [Facebook](https://web.facebook.com/kun.raksa.50)

##  Contribution
This project is not open for pull requests at the moment. However, you can still contribute by creating issues on GitHub if you find any bugs or have any suggestions for improvement. Please follow these steps:

1. Go to the [Issues](https://github.com/freddyt18/Telegram-Automata-Bot/issues) tab on GitHub
2. Click on the [New issue](https://github.com/freddyt18/Telegram-Automata-Bot/issues/new) button
3. Choose a template (bug report or feature request) and fill in the required information
4. Submit your issue and wait for a response from the project leader
Thank you for your interest in this project!

## License

This project is licensed under [GPL License](https://github.com/freddyt18/Telegram-Automata-Bot/blob/master/LICENSE.md).
