import logging
import itertools
import time
import os

import telegram
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
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

    def reply_with_keyboard(reply_text, reply_keyboard):
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard = True)
        update.message.reply_text(reply_text, reply_markup = reply_markup)  
    
    def reply_text(reply_text):
        update.message.reply_text(reply_text)  
    
    main_keyboard = [['記帳'], ['近期交易', '顯示餘額']]
    category_keyboard = [['生活', '娛樂', '教育'], ['儲蓄', '投資', '贈與']]
    cancel_keyboard = [['取消']]

    input_text = update.message.text

    # Return to home
    if input_text in ['取消']:
        reply_with_keyboard('請選擇動作：', main_keyboard)
    # Show actions 
    elif input_text in list(itertools.chain(*main_keyboard)):
        if input_text == '記帳':
            reply_with_keyboard('記帳種類：', category_keyboard)
        else:
            reply_with_keyboard(main_reply_text, main_keyboard)
    # Choose category
    elif input_text in list(itertools.chain(*category_keyboard)):
        reply_with_keyboard('請輸入數字', cancel_keyboard)
    # Enter price
    elif input_text.isnumeric():
        price = int(input_text)
        reply_with_keyboard('記入一筆：' + str(price), main_keyboard)
    else:
        reply_with_keyboard('請輸入數字', cancel_keyboard)
    
    t = time.localtime(time.time())
    date = '{}/{}/{}'.format(t.tm_year, t.tm_mon, t.tm_mday)
    timestamp = '{}:{}:{}'.format(t.tm_hour, t.tm_min, t.tm_sec)
    reply_text(date + timestamp)

# New a dispatcher for bot
dispatcher = Dispatcher(bot, None)

# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))

if __name__ == "__main__":
    # Running server
    app.run(debug=True)