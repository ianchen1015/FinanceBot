import logging
import os

import telegram
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initial Flask app
app = Flask(__name__)

# Initial bot by Telegram access token
bot = telegram.Bot(token=(os.environ['TELEGRAM_ACCESS_TOKEN']))


@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Set route /hook with POST method will trigger this method."""
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
        print(os.environ['TELEGRAM_ACCESS_TOKEN'])
    return 'ok'


def reply_handler(bot, update):
    """Reply message."""
    # text = update.message.text
    # update.message.reply_text(text)
    keyboard =[[InlineKeyboardButton("記帳", url=os.environ['HEROKU_URL'] + 'add/'),
            InlineKeyboardButton("顯示", url='')],[]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('請選擇動作：', reply_markup=reply_markup)


@app.route('/add')
def reply_methods(bot, update):
    """Reply message."""
    # text = update.message.text
    # update.message.reply_text(text)
    # keyboard =[[InlineKeyboardButton("生活", url=''),
    #         InlineKeyboardButton("娛樂", url=''),
    #         InlineKeyboardButton("教育", url=''),
    #         InlineKeyboardButton("儲蓄", url=''),
    #         InlineKeyboardButton("投資", url=''),
    #         InlineKeyboardButton("贈與", url='')],[]]

    # reply_markup = InlineKeyboardMarkup(keyboard)

    # update.message.reply_text('請選擇種類：', reply_markup=reply_markup)
    keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
                InlineKeyboardButton("Option 2", callback_data='2')],

            [InlineKeyboardButton("Option 3", callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)

# New a dispatcher for bot
dispatcher = Dispatcher(bot, None)

# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))

if __name__ == "__main__":
    # Running server
    app.run(debug=True)