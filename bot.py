from telegram.ext import Updater, CallbackQueryHandler, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from deepl import DeepL


source = 'EN'
target = 'FR'
global message_id_to

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

    keyboard = [[KeyboardButton('From'), KeyboardButton('To'), KeyboardButton('ℹ️')]]

    reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    update.message.reply_text('Hello! I am DeepL translator bot. Select language you want to translate into, '
                              'send me your message and I will translate it.',
                              reply_markup=reply_markup)
    info(bot, update)


def button(bot, update):

    global source, target

    query = update.callback_query

    if 'from' in query.data:
        source = query.data[:2]

        bot.edit_message_text(text="Translating from: {}".format(meaning[source]),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
    else:
        target = query.data

        bot.edit_message_text(text="Translating to: {}".format(meaning[target]),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)


def translate_from(bot, update):
    buttons = [[InlineKeyboardButton(text=f, callback_data=flags[f] + ' from') for f in flags]]
    reply_markup = InlineKeyboardMarkup(buttons)
    update.message.reply_text('Please choose language to translate from:', reply_markup=reply_markup)


def translate_to(bot, update):
    buttons = [[InlineKeyboardButton(text=f, callback_data=flags[f]) for f in flags if flags[f] != source]]
    reply_markup = InlineKeyboardMarkup(buttons)
    update.message.reply_text('Please choose language to translate into:', reply_markup=reply_markup)


def info(bot, update):
    global source, target
    update.message.reply_text('Currently translating from {0} to {1}'.format(meaning[source], meaning[target]))


def translate(bot, update):

    global source, target

    text = update.message.text

    if text == 'From':
        translate_from(bot, update)
        return

    elif text == 'To':
        translate_to(bot, update)
        return

    elif text == 'ℹ️':
        info(bot, update)
        return

    result, data = d.translate(text, source=source, target=target)
    update.message.reply_text(result, quote=True)


if __name__ == '__main__':

    import sys
    up = Updater(sys.argv[1])

    d = DeepL()

    up.dispatcher.add_handler(CommandHandler('start', start))
    up.dispatcher.add_handler(MessageHandler(Filters.text, translate))
    up.dispatcher.add_handler(CallbackQueryHandler(button))

    up.start_polling()
    up.idle()
