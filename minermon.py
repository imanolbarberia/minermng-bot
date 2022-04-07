#!/usr/bin/env python3

import telebot
import os
import sys
from MinerData import MinerData

CFG_BOTTOKEN_FILE = ".telegram/bot_token"
CFG_USERID_FILE = ".telegram/user_id"

md = MinerData("miners.db")


def init_bot():
    """
    Initialize bot
    :return: Tuple with the bot handler and the user ID
    """
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


def cmd_start(bot: telebot.TeleBot, msg: telebot.types.Message):
    """
    START command
    :param bot:
    :param msg:
    :return:
    """
    bot.reply_to(msg, "START command executed")


def cmd_help(bot: telebot.TeleBot, msg: telebot.types.Message):
    """
    HELP command
    :param bot:
    :param msg:
    :return:
    """
    pass


def cmd_list(bot: telebot.TeleBot, msg: telebot.types.Message):
    """
    LIST command
    :param bot:
    :param msg:
    :return:
    """
    global md
    mlist = md.get_miners()
    lst = ""
    for row in mlist:
        lst += "\U0001F538 {} ({})\n".format(row[1], row[3])

    bot.reply_to(msg, lst)


def handle_commands(bot: telebot.TeleBot, msg: telebot.types.Message):
    """
    Handle commands in a generic way. Specific command functions are called from this one.
    :param bot: Bot handler
    :param msg: Message
    """
    cmd = msg.text.split(" ")[0][1:]

    if cmd == "start":
        cmd_start(bot, msg)
    elif cmd == "help":
        cmd_help(bot, msg)
    elif cmd == "list":
        cmd_list(bot, msg)
    else:
        bot.reply_to(msg, "Unknown command {}".format(cmd))


def main():
    """
    Main function
    :return:
    """
    available_commands = [
        'start',
        'help',
        'list'
    ]

    (bot, usr) = init_bot()

    @bot.message_handler(commands=available_commands)
    def hndl_cmds(message: telebot.types.Message):
        handle_commands(bot, message)

    @bot.message_handler(commands=['terminate'])
    def terminate_bot(message: telebot.types.Message):
        bot.reply_to(message, "[LOG] Terminating bot!")
        bot.stop_bot()

    # ToDo: find a better way to terminate the bot
    bot.infinity_polling()


if __name__ == '__main__':
    main()
