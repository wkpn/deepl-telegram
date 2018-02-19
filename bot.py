from telegram.ext import Updater, CallbackQueryHandler, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from api import DeepL
from time import sleep


source = 'EN'
target = 'FR'

flags = {
    '🇺🇸': 'EN',
    '🇫🇷': 'FR',
    '🇩🇪': 'DE',
    '🇮🇹': 'IT',
    '🇪🇸': 'ES',
    '🇱🇺': 'NL',
    '🇲🇨': 'PL'
}

meaning = {
    'EN': 'English',
    'FR': 'French',
    'DE': 'German',
    'IT': 'Italian',
    'ES': 'Spanish',
    'NL': 'Dutch',
    'PL': 'Polish'
}


def start(bot, update):
    keyboard = [[KeyboardButton('Setup'), KeyboardButton('ℹ️')]]

    reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    update.message.reply_text('Hello! I am DeepL translator bot. Send me your message and I will translate it.')
    update.message.reply_text('Press Setup button to select your languages (from -> to)')
    update.message.reply_text('Press ℹ️ button to view current setup',
                              reply_markup=reply_markup)

    info(bot, update)


def from_callback(bot, update):
    global source

    query = update.callback_query
    source = query.data[4:]

    buttons = [[InlineKeyboardButton(text=f, callback_data='to' + flags[f]) for f in flags if flags[f] != source]]
    reply_markup = InlineKeyboardMarkup(buttons)

    bot.edit_message_text(text='Please choose language to translate into:',
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          reply_markup=reply_markup)


def to_callback(bot, update):
    global source, target

    query = update.callback_query
    target = query.data[2:]

    bot.edit_message_text(text="Currently translating from {} to {}".format(meaning[source], meaning[target]),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


def setup(bot, update):
    buttons = [[InlineKeyboardButton(text=f, callback_data= 'from' + flags[f]) for f in flags]]
    reply_markup = InlineKeyboardMarkup(buttons)
    update.message.reply_text('Please choose language to translate from:', reply_markup=reply_markup)


def info(bot, update):
    global source, target
    update.message.reply_text('Currently translating from {0} to {1}'.format(meaning[source], meaning[target]))


def translate(bot, update):
    text = update.message.text

    if text == 'ℹ️':
        info(bot, update)
        return
    elif text == 'Setup':
        setup(bot, update)
        return

    global source, target

    result, data = d.translate(text, source=source, target=target)
    update.message.reply_text(result, quote=True)


if __name__ == '__main__':

    import sys
    up = Updater(sys.argv[1])

    d = DeepL()

    up.dispatcher.add_handler(CommandHandler('start', start))
    up.dispatcher.add_handler(MessageHandler(Filters.text, translate))

    up.dispatcher.add_handler(CallbackQueryHandler(from_callback, pattern='^from'))
    up.dispatcher.add_handler(CallbackQueryHandler(to_callback, pattern='^to'))

    up.start_polling()
    up.idle()
