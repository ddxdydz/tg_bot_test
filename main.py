import json

from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, \
    InlineKeyboardButton, InlineKeyboardMarkup


TOKEN = '1864577364:AAGVCPJbh00532SkfZ4fUhbfv4luCWnwt0g'
MODER_MAIL = 'zil10@inbox.ru'
ADMIN_ID = 1040804311

# Inline keyboards
inline_btn_1 = InlineKeyboardButton('OK!', callback_data='button1')
inline_btn_2 = InlineKeyboardButton('CLEAR ALL!', callback_data='button2')
inline_kb_full_ex = InlineKeyboardMarkup([[inline_btn_1, inline_btn_2]])


def admin_func(func):
    def saved_func(update, context):
        if update.message.from_user['id'] == ADMIN_ID:
            func(update, context)
        else:
            update.message.reply_text('Not found')
    return saved_func


def add_history_func(func):
    def saved_func(update, context):
        if update.message.from_user['id'] != ADMIN_ID:
            with open('history.txt', 'a', encoding='utf8') as file:
                from_user = update.message.from_user
                file.write(f"\nTIME: {update.message.date}  -  {from_user['username']}" +
                           f"\nFROM: {from_user}" +
                           f"\nTEXT: {update.message.text}" +
                           f"\n---")
        func(update, context)
    return saved_func


# Определяем функцию-обработчик сообщений.
@add_history_func
def echo(update, context):
    input_data = update.message.text.lower()

    with open('codes.json', 'r', encoding='utf8') as file:
        codes_file = file.read()
        data = json.loads(codes_file)

    found_items = list(filter(
        lambda el_name: input_data in el_name, data.keys()))

    if len(found_items) == 1:
        name = found_items[0]

        code_values = sorted(
            data[name].items(),
            key=lambda elem: elem[1],
            reverse=True
        )
        name_codes = \
            list(map(lambda elem: elem[0], code_values))

        keyboard_size = 7
        reply_keyboard = \
            [
                [InlineKeyboardButton(f'{name.upper()}', callback_data='none')]
            ] + \
            [
                [InlineKeyboardButton(elem, callback_data=elem)
                 for elem in name_codes[i:i + keyboard_size]]
                for i in range(0, len(name_codes), keyboard_size)
            ]

        inline_kb_full = InlineKeyboardMarkup(reply_keyboard)

        update.message.reply_text(
            f' Search result:',
            reply_markup=inline_kb_full
        )
    elif len(found_items):
        list_size = len(found_items) // 2 % 4
        reply_keyboard = [
            [elem.capitalize() for elem in found_items[i:i + list_size]]
            for i in range(0, len(found_items), list_size)
        ]
        markup = ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=False
        )
        update.message.reply_text(
            "Выберите подходящий элемент:",
            reply_markup=markup
        )
    else:
        update.message.reply_text(
            'Not found',
        )


# Функции команд
@add_history_func
def start(update, context):
    update.message.reply_text(
        "Привет! Я бот. Напишите мне тип устройства, и я пришлю код для универсального пульта!"
    )


@add_history_func
def bot_help(update, context):
    update.message.reply_text(
        "Доступные команды:\n" +
        "/help\n" +
        "/show_db\n" +
        "/add_codes <name> <code1>, <code2>..."
    )


@add_history_func
def show_db(update, context):
    with open('codes.json', 'r', encoding='utf8') as file:
        codes_file = file.read()
        data = json.loads(codes_file)
    for name, codes in data.items():
        update.message.reply_text(f'{name.capitalize()}: {", ".join(codes)}')


def clear_chat_messages(update, context):
    print(help(update))


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
        ["/show_added_codes", "/clear_added_codes"],
        ['/get_code_file', "/restart_code_file"]
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


@admin_func
def get_code_file(update, context):
    context.bot.send_document(
        update.message.chat_id,
        open('codes.json', 'rb')
    )


@admin_func
def restart_code_file(update, context):
    with open('codes.json', 'r', encoding='utf-8') as f:
        r_file = f.read()
        data = json.loads(r_file)
    for btn_elem_name in data.keys():
        for btn_code_name in data[btn_elem_name]:
            data[btn_elem_name][btn_code_name] = 0
    with open('codes.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, sort_keys=True, indent=4)
    update.message.reply_text(
        f'OK!'
    )


def ok_mess_func(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text=query.message['text'],
        reply_markup=InlineKeyboardMarkup([[]])
    )


def delete_mess_func(update, context):
    query = update.callback_query
    query.answer()
    query.delete_message()


def btn_code_add(update, context):
    query = update.callback_query
    btn_elem_name = update.callback_query.message[
        'reply_markup']['inline_keyboard'][0][0]['text'].lower()
    btn_code_name = query.data

    with open('codes.json', 'r', encoding='utf-8') as f:
        r_file = f.read()
        data = json.loads(r_file)
    data[btn_elem_name][btn_code_name] += 1
    with open('codes.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, sort_keys=True, indent=4)

    context.bot.answer_callback_query(
        callback_query_id=query.id,
        text='КОД ОТМЕЧЕН',
        show_alert=False
    )


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher  # Диспетчер сообщений.

    # Создаём обработчик сообщений типа Filters.text из описанной выше функции echo()
    # вызывается при получении сообщения с типом "текст"
    text_handler = MessageHandler(Filters.text, echo)

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", bot_help))
    dp.add_handler(CommandHandler("add_codes", add_codes))
    dp.add_handler(CommandHandler("show_db", show_db))
    # dp.add_handler(CommandHandler("clear", clear_chat_messages))

    dp.add_handler(CommandHandler("mod", mod_help))
    dp.add_handler(CommandHandler("close_mod", close_mod))
    dp.add_handler(CommandHandler("clear_history", clear_history))
    dp.add_handler(CommandHandler("show_history", show_history))
    dp.add_handler(CommandHandler("clear_added_codes", clear_added_codes))
    dp.add_handler(CommandHandler("show_added_codes", show_added_codes))
    dp.add_handler(CommandHandler("get_code_file", get_code_file))
    dp.add_handler(CommandHandler("restart_code_file", restart_code_file))

    # TODO TEST INLINE BUTTONS
    dp.add_handler(CallbackQueryHandler(ok_mess_func, pattern='button1'))
    dp.add_handler(CallbackQueryHandler(delete_mess_func, pattern='button2'))

    dp.add_handler(CallbackQueryHandler(btn_code_add))

    # Регистрируем обработчик в диспетчере.
    dp.add_handler(text_handler)

    updater.start_polling()  # Запускаем цикл приема и обработки сообщений.
    updater.idle()  # Ждём завершения приложения.


# heroku ps:scale worker=1
if __name__ == '__main__':
    main()
