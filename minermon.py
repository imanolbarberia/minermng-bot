#!/usr/bin/env python3

import telebot
import os
import sys

CFG_BOTTOKEN_FILE = ".telegram/bot_token"
CFG_USERID_FILE = ".telegram/user_id"


def init_bot():
    if not os.path.exists(CFG_USERID_FILE):
        print("[ERROR]: File '%s' does not exist. Make sure you create this file and write your user ID there." %
              CFG_USERID_FILE, file=sys.stderr)
        exit(1)

    f_user = open(CFG_USERID_FILE)
    user_id = f_user.read()
    f_user.close()

    if user_id == "":
        print("[ERROR]: Invalid Telegram user ID. Make sure you write a valid one", file=sys.stderr)
        exit(1)

    if not os.path.exists(CFG_BOTTOKEN_FILE):
        print("[ERROR]: File '%s' does not exist. Make this file and write your bot token there." % CFG_BOTTOKEN_FILE,
              file=sys.stderr)
        exit(2)

    f_token = open(CFG_BOTTOKEN_FILE)
    bot_token = f_token.read()
    f_token.close()

    if bot_token == "":
        print("[ERROR]: Invalid Telegram bot token. Make sure you write a valid one.", file=sys.stderr)
        exit(2)

    bot = telebot.TeleBot(bot_token, parse_mode=None)
    try:
        bot.send_message(user_id, "[LOG]: Initializing bot...")
    except telebot.apihelper.ApiTelegramException:
        print("[ERROR]: There was an error initializing the bot. Check that the bot token is correctly defined.")
        exit(2)

    return bot, user_id


def main():
    (bot, usr) = init_bot()
    bot.send_message(usr, "[LOG]: Bot initialized")

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message: telebot.types.Message):
        bot.reply_to(message, "Testing basic commands... Command used: '%s'" % message.text)

    @bot.message_handler(commands=['terminate'])
    def terminate_bot(message: telebot.types.Message):
        bot.reply_to(message, "[LOG] Terminating bot!")
        bot.stop_bot()

    bot.infinity_polling()


if __name__ == '__main__':
    main()
