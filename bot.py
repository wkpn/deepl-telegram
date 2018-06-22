from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler, CommandHandler, MessageHandler, Filters
from db import setup_db, add_to_db, get_from_db, update_in_db
from settings import flags, meaning, DOMAIN
from api import DeepL
import sys


def start(bot, update):
    add_to_db(update.message.chat_id, 'EN', 'FR')

    keyboard = [[KeyboardButton('Setup'), KeyboardButton('ℹ️')]]
    reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    update.message.reply_text('Hello! I am DeepL translator bot. Send me your message and I will translate it.')
    update.message.reply_text('Press Setup button to select your languages (from -> to)')
    update.message.reply_text('Press ℹ️ button to view current setup', reply_markup=reply_markup)

    info(bot, update)


def from_callback(bot, update):
    query = update.callback_query
    source = query.data[4:]

    update_in_db(query.message.chat_id, source=source)

    buttons = [[InlineKeyboardButton(text=f, callback_data='to' + flags[f]) for f in flags if flags[f] != source]]
    reply_markup = InlineKeyboardMarkup(buttons)

    bot.edit_message_text(text='Please choose language to translate into:',
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          reply_markup=reply_markup)


def to_callback(bot, update):
    query = update.callback_query
    target = query.data[2:]

    update_in_db(query.message.chat_id, target=target, is_selected=1)
    source = get_from_db(query.message.chat_id, source=True)

    bot.edit_message_text(text="Currently translating from {} to {}".format(meaning[source], meaning[target]),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


def setup(bot, update):
    is_selected = get_from_db(update.message.chat_id, is_selected=True)

    if is_selected == (1,):
        update.message.reply_text('You have to choose languages in the message above')
        return

    update_in_db(update.message.chat_id, is_selected=True)

    buttons = [[InlineKeyboardButton(text=f, callback_data='from' + flags[f]) for f in flags]]
    reply_markup = InlineKeyboardMarkup(buttons)
    update.message.reply_text('Please choose language to translate from:', reply_markup=reply_markup)


def info(bot, update):
    source, target = get_from_db(chat_id=update.message.chat_id, source=True, target=True)
    update.message.reply_text('Currently translating from {0} to {1}'.format(meaning[source], meaning[target]))


def translate(bot, update):
    text = update.message.text

    if text == 'ℹ️':
        info(bot, update)
        return
    elif text == 'Setup':
        setup(bot, update)
        return

    source, target = get_from_db(chat_id=update.message.chat_id, source=True, target=True)

    result, data = d.translate(text, source=source, target=target)
    update.message.reply_text(result, quote=True)


if __name__ == '__main__':
    TOKEN = sys.argv[1]
    PORT = 5000

    up = Updater(TOKEN)
    setup_db()
    d = DeepL()

    up.dispatcher.add_handler(CommandHandler('start', start))
    up.dispatcher.add_handler(MessageHandler(Filters.text, translate))

    up.dispatcher.add_handler(CallbackQueryHandler(from_callback, pattern='^from'))
    up.dispatcher.add_handler(CallbackQueryHandler(to_callback, pattern='^to'))

    up.start_webhook(listen='127.0.0.1',
                     url_path=f'{TOKEN}',
                     port=PORT)
    up.bot.set_webhook(url=f'https://{DOMAIN}/{TOKEN}')
    up.idle()

