# Railway Menu Bot (Telegram)

## Env vars
- MENU_BOT_TOKEN=... (token from BotFather)
- TARGET_CHAT_ID=... (group chat id where OpenClaw bot is present)

## How it works
The menu bot posts messages into a shared Telegram group with the OpenClaw bot.
OpenClaw responds in the same group, acting as the "brain".

## Setup steps
1) Create a Telegram group (e.g., "Family Hub").
2) Add both bots (Menu Bot + OpenClaw bot) to the group.
3) Find group chat_id (send /id to menu bot inside the group).
4) Set TARGET_CHAT_ID to that value in Railway Variables.
5) Deploy.
