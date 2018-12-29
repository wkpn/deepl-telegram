from telegram.ext import Updater, CallbackQueryHandler, CommandHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from db import setup_db, add_user_to_db, get_from_db, update_in_db
from settings import flags, meaning, TOKEN, DOMAIN, PORT
from deepl import DeepL


def start(bot, update):
    add_user_to_db(update.message.chat_id, 'EN', 'FR')

    update.message.reply_text('Hello! I am DeepL translator bot. Send me your message and I will translate it.')
    update.message.reply_text('Use /setup command to select your languages (from -> to)')
    update.message.reply_text('Use /info command to view your current translation setup')


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

    update_in_db(query.message.chat_id, target=target, lock='0')
    source = get_from_db(query.message.chat_id, source=True)

    bot.edit_message_text(text="Currently translating from {} to {}".format(meaning[source], meaning[target]),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


def setup(bot, update):
    lock = get_from_db(update.message.chat_id, lock=True)

    if lock == '1':
        update.message.reply_text('You have to choose languages in the message above')
        return

    update_in_db(update.message.chat_id, lock='1')

    buttons = [[InlineKeyboardButton(text=f, callback_data='from' + flags[f]) for f in flags]]
    reply_markup = InlineKeyboardMarkup(buttons)

    update.message.reply_text('Please choose language to translate from:', reply_markup=reply_markup)


def info(bot, update):
    source, target = get_from_db(chat_id=update.message.chat_id, source=True, target=True)
    update.message.reply_text(f'Currently translating from {meaning[source]} to {meaning[target]}')


def translate(bot, update):
    lock = get_from_db(update.message.chat_id, lock=True)

    if lock == '1':
        update.message.reply_text('You have to choose languages in the message above')
        return

    text = update.message.text
    source, target = get_from_db(chat_id=update.message.chat_id, source=True, target=True)
    result, data = deepl.translate(text, source=source, target=target)
    update.message.reply_text(result, quote=True)


if __name__ == '__main__':
    up = Updater(TOKEN)
    deepl = DeepL()
    setup_db()

    up.dispatcher.add_handler(CommandHandler('start', start))
    up.dispatcher.add_handler(CommandHandler('setup', setup))
    up.dispatcher.add_handler(CommandHandler('info', info))
    up.dispatcher.add_handler(MessageHandler(Filters.text, translate))
    up.dispatcher.add_handler(CallbackQueryHandler(from_callback, pattern='^from'))
    up.dispatcher.add_handler(CallbackQueryHandler(to_callback, pattern='^to'))

    #up.start_webhook(listen='127.0.0.1',
    #                 url_path=f'{TOKEN}',  # should be the same as in your server.conf file (TOKEN is preferred)
    #                 port=PORT)
    #up.bot.set_webhook(url=f'{DOMAIN}/{TOKEN}')
    up.start_polling()
    up.idle()
