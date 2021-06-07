import json

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler


TOKEN = '1864577364:AAGVCPJbh00532SkfZ4fUhbfv4luCWnwt0g'
MODER_MAIL = 'zil10@inbox.ru'
ADMIN_ID = 1040804311


def admin_func(func):
    def saved_func(update, context):
        if update.message.from_user['id'] == ADMIN_ID:
            func(update, context)
        else:
            update.message.reply_text('Not found')
    return saved_func


def add_history_func(func):
    def saved_func(update, context):
        if update.message.from_user['id'] == ADMIN_ID:
            with open('history.txt', 'a', encoding='utf8') as file:
                file.write(f"\nTIME: {update.message.date}" +
                           f"\nFROM: {update.message.from_user}" +
                           f"\nTEXT: {update.message.text}" +
                           f"\n---")
        func(update, context)
    return saved_func


# Определяем функцию-обработчик сообщений.
@add_history_func
def echo(update, context):
    input_data = update.message.text

    with open('codes.json', 'r', encoding='utf8') as file:
        codes_file = file.read()
        data = json.loads(codes_file)

    found_items = list(filter(
        lambda elem: input_data.lower() in elem, data.keys()))

    if len(found_items) == 1:
        name = found_items[0]
        update.message.reply_text(
            f'{name.capitalize()}: {", ".join(data[name])}',
            reply_markup=ReplyKeyboardRemove()
        )
    elif len(found_items):
        list_size = len(found_items) // 2 % 4
        reply_keyboard = [
            [elem.capitalize() for elem in found_items[i:i + list_size]]
            for i in range(0, len(found_items), list_size)
        ]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        update.message.reply_text(
            "Выберите подходящий элемент:",
            reply_markup=markup
        )
    else:
        update.message.reply_text(
            'Not found',
            reply_markup=ReplyKeyboardRemove()
        )


# Функции команд
@add_history_func
def start(update, context):
    update.message.reply_text(
        "Привет! Я бот. Напишите мне тип устройства, и я пришлю код для универсального пульта!")


@add_history_func
def bot_help(update, context):
    update.message.reply_text(
        """
        Доступные команды: 
        /help 
        /show_db 
        /add_codes <name> <code1>, <code2>...
        """
    )


@add_history_func
def show_db(update, context):
    with open('codes.json', 'r', encoding='utf8') as file:
        codes_file = file.read()
        data = json.loads(codes_file)
    for name, codes in data.items():
        update.message.reply_text(f'{name.capitalize()}: {", ".join(codes)}')


@add_history_func
def add_codes(update, context):
    try:
        data = update.message.text.split(maxsplit=2)
        cmd, name, nums = data
        if not name.isdigit() and all(map(lambda elem: elem.isdigit(), nums.split(', '))):
            code = {name: nums.split(', ')}
            with open('added_codes.txt', 'a', encoding='utf8') as file:
                file.write(f'\n{name.lower()} {", ".join(code[name])}' + '\n---')
            update.message.reply_text('Принято в обработку')
        else:
            update.message.reply_text('Ошибка в введённых данных')
    except Exception:
        update.message.reply_text('Ошибка в введённых данных')


@admin_func
def mod_help(update, context):
    reply_keyboard = [
        ["/close_mod"],
        ["/show_history", "/clear_history"],
        ["/show_added_codes", "/clear_added_codes"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        f'Администраторская панель открыта',
        reply_markup=markup
    )


@admin_func
def close_mod(update, context):
    update.message.reply_text(
        'OK!',
        reply_markup=ReplyKeyboardRemove()
    )


@admin_func
def clear_history(update, context):
    with open('history.txt', 'w', encoding='utf8') as file:
        file.write('---')
    update.message.reply_text(
        f'OK!'
    )


@admin_func
def show_history(update, context):
    with open('history.txt', 'rt', encoding='utf8') as file:
        data = file.read()
        if data == '---':
            update.message.reply_text("Empty")
        else:
            for elem in data.split('---'):
                if elem:
                    update.message.reply_text(
                        elem
                    )


@admin_func
def clear_added_codes(update, context):
    with open('added_codes.txt', 'w', encoding='utf8') as file:
        file.write('---')
    update.message.reply_text(
        f'OK!'
    )


@admin_func
def show_added_codes(update, context):
    with open('added_codes.txt', 'rt', encoding='utf8') as file:
        data = file.read()
        if data == '---':
            update.message.reply_text("Empty")
        else:
            for elem in data.split('---'):
                if elem:
                    update.message.reply_text(
                        elem
                    )


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher  # Пдиспетчер сообщений.

    # Создаём обработчик сообщений типа Filters.text из описанной выше функции echo()
    # вызывается при получении сообщения с типом "текст"
    text_handler = MessageHandler(Filters.text, echo)

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", bot_help))
    dp.add_handler(CommandHandler("add_codes", add_codes))
    dp.add_handler(CommandHandler("show_db", show_db))

    dp.add_handler(CommandHandler("mod", mod_help))
    dp.add_handler(CommandHandler("close_mod", close_mod))
    dp.add_handler(CommandHandler("clear_history", clear_history))
    dp.add_handler(CommandHandler("show_history", show_history))
    dp.add_handler(CommandHandler("clear_added_codes", clear_added_codes))
    dp.add_handler(CommandHandler("show_added_codes", show_added_codes))

    # Регистрируем обработчик в диспетчере.
    dp.add_handler(text_handler)

    updater.start_polling()  # Запускаем цикл приема и обработки сообщений.

    updater.idle()  # Ждём завершения приложения.
    # (например, получения сигнала SIG_TERM при нажатии клавиш Ctrl+C)


if __name__ == '__main__':
    main()  # heroku ps:scale worker=1
