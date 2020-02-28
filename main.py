import logging
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
    # text = update.message.text
    # update.message.reply_text(text)
    # keyboard =[[InlineKeyboardButton("記帳", url=os.environ['HEROKU_URL'] + 'add/'),
    #         InlineKeyboardButton("顯示", url='')]]

    # add_url=os.environ['HEROKU_URL'] + 'add/'
    # keyboard = [[InlineKeyboardButton("近期交易", callback_data='1'),
    #         InlineKeyboardButton("顯示餘額", callback_data='2')],
    #     [InlineKeyboardButton("記帳", url=add_url)]]

    # reply_markup = InlineKeyboardMarkup(keyboard)

    def reply_with_keyboard(reply_text, reply_keyboard):
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard = True)
        update.message.reply_text(reply_text, reply_markup = reply_markup)  
    
    # def reply_text(reply_text):
    #     update.message.reply_text(reply_text)  
    
    main_keyboard = [['記帳'], ['近期交易', '顯示餘額']]
    category_keyboard = [['生活', '娛樂', '教育'], ['儲蓄', '投資', '贈與']]
    cancel_keyboard = [['取消']]

    input_text = update.message.text

    # Return to home
    if input_text in ['取消']:
        reply_with_keyboard('請選擇動作：', main_keyboard)
    # Show actions 
    elif input_text in main_keyboard:
        if input_text == '記帳':
            reply_with_keyboard('記帳種類：', category_keyboard)
        else:
            reply_with_keyboard(main_reply_text, main_keyboard)
    # Choose category
    elif input_text in category_keyboard:
        reply_with_keyboard('請輸入數字', cancel_keyboard)
    # Enter price
    elif input_text.isnumeric():
        price = int(input_text)
        reply_with_keyboard('記入一筆：' + str(price), cancel_keyboard)
    else:
        reply_with_keyboard('請輸入數字', cancel_keyboard)

# @app.route('/add')
# def reply_methods(bot, update):
#     """Reply message."""
#     text = update.message.text
#     update.message.reply_text(text)
#     keyboard =[[InlineKeyboardButton("生活", callback_data='1'),
#             InlineKeyboardButton("娛樂", callback_data='1'),
#             InlineKeyboardButton("教育", callback_data='1')],[
#             InlineKeyboardButton("儲蓄", callback_data='1'),
#             InlineKeyboardButton("投資", callback_data='1'),
#             InlineKeyboardButton("贈與", callback_data='1')]]

#     reply_markup = InlineKeyboardMarkup(keyboard)

#     update.message.reply_text('請選擇種類：', reply_markup=reply_markup)

# New a dispatcher for bot
dispatcher = Dispatcher(bot, None)

# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))

if __name__ == "__main__":
    # Running server
    app.run(debug=True)