import logging
import itertools
import requests
import time
import os
import configparser

import telegram
from flask import Flask, request, session
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Dispatcher, MessageHandler, Filters, Updater

# Load data from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# TELEGRAM_ACCESS_TOKEN = os.environ['TELEGRAM_ACCESS_TOKEN']
# IAN_SPREADSHEET_URL = os.environ['IAN_SPREADSHEET_URL']

TELEGRAM_ACCESS_TOKEN = config['TELEGRAM']['TELEGRAM_ACCESS_TOKEN']
IAN_SPREADSHEET_URL = config['TELEGRAM']['IAN_SPREADSHEET_URL']

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initial Flask app
app = Flask(__name__)

# Initial bot by Telegram access token
bot = telegram.Bot(token = TELEGRAM_ACCESS_TOKEN)

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Set route /hook with POST method will trigger this method."""
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
    return 'ok'

def reply_handler(update, context):
    """Reply message."""

    input_text = update.message.text
    user = update.message.from_user

    def update_param(params):
        for key, value in params.items():
            context.user_data[key] = value

    def reply_with_keyboard(reply_text, reply_keyboard):
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard = True)
        update.message.reply_text(reply_text, reply_markup = reply_markup)  
    
    def reply_text(reply_text):
        update.message.reply_text(reply_text)  
    
    main_keyboard = [['開始記帳'], ['近期交易', '顯示餘額']]
    category_keyboard = [['生活', '娛樂', '教育'], ['儲蓄', '投資', '贈與'], ['取消']]
    cancel_keyboard = [['取消']]

    if context.user_data == {}:
        update_param({'state': 'main', 'debugmode': True})
    
    state = context.user_data['state']

    if input_text == '/debugmode':
        update_param({'debugmode': True})
    elif input_text == '/debugmodeoff':
        update_param({'debugmode': False})
    # Return to home
    elif input_text in ['取消']:
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
        if input_text.isnumeric():
            price = int(input_text)
            update_param({'state': 'main', 'price': str(price)})
            t = time.localtime(time.time())
            result = requests.post(IAN_SPREADSHEET_URL, data = {
                'action': 'add',
                'date': '{}/{}/{}'.format(t.tm_year, t.tm_mon, t.tm_mday),
                'month': t.tm_mon,
                'time': '{}:{}:{}'.format(t.tm_hour, t.tm_min, t.tm_sec),
                'category': context.user_data['category'],
                'name': context.user_data['name'],
                'price': context.user_data['price']
            })
            # TODO
            if result.ok:
                reply_with_keyboard('記入一筆：\n\n種類：{}\n項目：{}\n價格：{}\n'.format(
                    context.user_data['category'],
                    context.user_data['name'],
                    context.user_data['price']
                ), main_keyboard)
                update_param({'state': 'main', 'category':'', 'name':'', 'price': ''})
            else:
                reply_with_keyboard('上傳失敗' + str(price), main_keyboard)
            update_param({'state': 'main', 'category':'', 'name':'', 'price': ''})
        else:
            reply_with_keyboard('您輸入的不是數字\n請再次輸入價格', cancel_keyboard)
    else:
        update_param({'state': 'main'})
        reply_with_keyboard('請選擇動作：', main_keyboard)

    if context.user_data['debugmode'] == True:
        reply_text('{}'.format(str(context.user_data)))

# Dispatcher
dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))

if __name__ == "__main__":
    # Running server
    app.run(debug=True)