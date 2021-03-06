# -*- coding: utf-8 -*-
# ! /usr/bin/env python

import logging
# import requests
import sys
import random

from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters)

from config import config
from simphaty import analyze

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


chatbot = None

chat_history = {}


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='¡¿te rieh?! Que estoy muy loco...')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text="""Te Rieh Bot v1.0:
No tiene sentido lo que digo... iré endrogao...
                    """)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def randomchat(bot, update):
    global chatbot
    msg = update.message.text.lower()
    user_name = update.message.from_user.username.lower()
    if not user_name or user_name == '':
        user_name = 'humano'

    if "te rieh" in msg:
        # Si hablan al bot, charla
        if random.randint(0, 100) <= 25:
            reply = analyze(msg)

        else:
            statement = chatbot.get_response(msg)
            reply = statement.text

            if "te rieh" in reply:
                reply = reply.replace("te rieh", user_name)

            else:
                reply = user_name + ": " + reply

        bot.sendMessage(update.message.chat_id, text=reply)

    else:
        # Si no, aprende, en silencio
        prev = chat_history.get(update.message.chat_id)

        if not prev:
            chat_history[update.message.chat_id] = msg

        else:
            chatbot.set_trainer(ListTrainer)
            chatbot.train([prev, msg])


def initial_training(bot, update):
    chatbot.set_trainer(ChatterBotCorpusTrainer)
    chatbot.train("chatterbot.corpus.spanish")

    bot.sendMessage(update.message.chat_id, text="Entrenamiento inicial completado.")


def main():
    global chatbot
    token = config.get('TOKEN')

    if token is None:
        print("Please, configure your token first")
        sys.exit(1)

    updater = Updater(token)
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("init", initial_training))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler([Filters.text], randomchat))

    # log all errors
    dispatcher.add_error_handler(error)

    # Start the chat bot system
    chatbot = ChatBot('Te Rieh',
                      trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
                      storage_adapter='chatterbot.storage.MongoDatabaseAdapter',
                      logic_adapters=[
                          'chatterbot.logic.BestMatch'
                      ],
                      filters=[
                          'chatterbot.filters.RepetitiveResponseFilter'
                      ],
                      database='terieh',
                      database_uri=config.get('database'))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    print("Starting TeRiehBot")
    main()
