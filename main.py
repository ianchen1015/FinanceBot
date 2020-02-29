import logging
import itertools
import requests
import time
import os

import telegram
from flask import Flask, request, session
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Dispatcher, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initial Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Initial bot by Telegram access token
bot = telegram.Bot(token=(os.environ['TELEGRAM_ACCESS_TOKEN']))

# Temp params for users
data = {}

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

    input_text = update.message.text
    user = update.message.from_user
    user_id = str(user.id)

    # data = {}
    # data[user.id] = {'category': '', 'name': '', 'price': ''}
    # global data
    # if user.id not in data:
    #     data[user.id] = {'state': 'main'}
    #     print("========== ", data[user.id])
    if session.get(user_id) == True:
        session[user_id] = {'state': 'main'}

    def update_param(params):
        # global data
        # user_data = data[user.id]
        # user_data = user_data.update(params)
        session[user_id] = session[user_id].update({'state': 'main'})

    def reply_with_keyboard(reply_text, reply_keyboard):
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard = True)
        update.message.reply_text(reply_text, reply_markup = reply_markup)  
    
    def reply_text(reply_text):
        update.message.reply_text(reply_text)  
    
    main_keyboard = [['開始記帳'], ['近期交易', '顯示餘額']]
    category_keyboard = [['生活', '娛樂', '教育'], ['儲蓄', '投資', '贈與'], ['取消']]
    cancel_keyboard = [['取消']]

    # State routing
    # state = data[user.id]['state']
    state = session[user_id]['state']

    # Return to home
    if input_text in ['取消']:
        update_param({'state': 'main'})
        reply_with_keyboard('請選擇動作：', main_keyboard)
        update_param({'state': 'main', 'category':'', 'name':'', 'price': ''})
    # Choosing actions 
    elif input_text in list(itertools.chain(*main_keyboard)):
        if input_text == '開始記帳':
            update_param({'state': 'category'})
            reply_with_keyboard('請輸入種類', category_keyboard)
        else:
            update_param({'state': 'main'})
            reply_with_keyboard('請選擇動作：', main_keyboard)
    # Choosing category
    elif state == 'category':#input_text in list(itertools.chain(*category_keyboard)):
        update_param({'state': 'name', 'category': input_text})
        reply_with_keyboard('請輸入項目', cancel_keyboard)
    # Entering name
    elif state == 'name':
        update_param({'state': 'price', 'name': input_text})
        reply_with_keyboard('請輸入價格', cancel_keyboard)
    # Entering price
    elif state == 'price':
        price = int(input_text)
        update_param({'state': 'main', 'price': str(price)})
        t = time.localtime(time.time())
        result = requests.post(os.environ['IAN_SPREADSHEET_URL'], data = {
            'action': 'add',
            'date': '{}/{}/{}'.format(t.tm_year, t.tm_mon, t.tm_mday),
            'month': t.tm_mon,
            'time': '{}:{}:{}'.format(t.tm_hour, t.tm_min, t.tm_sec),
            'category': data[user_id]['category'],
            'name': data[user_id]['name'],
            'price': data[user_id]['price']
        })
        reply_with_keyboard('記入一筆：' + str(price), main_keyboard)
        update_param({'state': 'main', 'category':'', 'name':'', 'price': ''})
    else:
        update_param({'state': 'main'})
        reply_with_keyboard('請選擇動作：', main_keyboard)

    reply_text('User: {}\n{}'.format(user_id, str(session[user_id])))

# New a dispatcher for bot
dispatcher = Dispatcher(bot, None)

# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))

if __name__ == "__main__":
    # Running server
    app.run(debug=True)