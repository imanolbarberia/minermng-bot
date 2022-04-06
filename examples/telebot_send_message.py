# pip install pytelegrambotapi

import telebot

# Telegram bot token (from @botfather)
api_key = "TYPEHERETELEGRAMBOTTOKEN"

# User id, not tag (from @userinfobot)
user_id = "USERID"

bot = telebot.TeleBot(api_key, parse_mode=None)
bot.send_message(user_id, "This is a test with an emoji: \U0001F605")

