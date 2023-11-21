from config import *
from messages import *
from work_generator import CourseWorkFactory, CourseWork
import telebot
from telebot import types
from utils import *

bot = telebot.TeleBot(TOKEN)
users_works_count = {}  # user's id: count of works
current_works = []  # users' requests in (chat_id: int, message_id: int, text: str) type
decorating = {}  # link between moderator and work. moderator_id: chat_id: int
factory = CourseWorkFactory(bot=bot)


@bot.message_handler(commands=['start', 'help'])
def start(message):
    if message.from_user.id not in users_works_count:
        users_works_count[message.from_user.id] = 0
        bot.send_message(ADMIN, f"User @{message.from_user.username} started a bot.")
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Сгенерировать ТЗ', callback_data='generate')
    btn2 = types.InlineKeyboardButton(text='Узнать о Scribo', callback_data='info')
    btn3 = types.InlineKeyboardButton(text='Связаться с командой', callback_data='connect')
    btn4 = types.InlineKeyboardButton(text='Отправить донат', url=DONATE_URL)
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    if message.from_user.id in MODERATORS:
        btn5 = types.InlineKeyboardButton(text='Список доступных работ', callback_data='list')
        markup.add(btn5)
    bot.send_message(message.from_user.id, START_MESSAGE, reply_markup=markup, parse_mode='html')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    req = call.data.split('_')
    markup = types.InlineKeyboardMarkup()
    if req[0] == 'info':
        btn1 = types.InlineKeyboardButton(text='Канал проекта', url='https://t.me/scribo_project')
        btn2 = types.InlineKeyboardButton(text='Главное меню', callback_data='menu')
        markup.add(btn1)
        markup.add(btn2)
        bot.edit_message_text(
            ABOUT_MESSAGE,
            reply_markup=markup,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
        )
    elif req[0] == 'generate':
        bot.edit_message_text(
            GENERATE_MESSAGE,
            reply_markup=markup,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='Markdown',
        )
    elif req[0] == 'menu':
        btn1 = types.InlineKeyboardButton(text='Сгенерировать работу', callback_data='generate')
        btn2 = types.InlineKeyboardButton(text='Узнать о Scribo', callback_data='info')
        btn3 = types.InlineKeyboardButton(text='Связаться с командой', callback_data='connect')
        btn4 = types.InlineKeyboardButton(text='Отправить донат', url=DONATE_URL)
        markup.add(btn1, btn2)
        markup.add(btn3, btn4)
        if call.message.chat.id in MODERATORS:
            btn5 = types.InlineKeyboardButton(text='Список доступных работ', callback_data='list')
            markup.add(btn5)
        bot.edit_message_text(
            MENU_MESSAGE,
            reply_markup=markup,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='html',
        )
    elif req[0] == 'connect':
        btn1 = types.InlineKeyboardButton(text='Представитель Scribo', url='https://t.me/nikpeg')
        btn2 = types.InlineKeyboardButton(text='Канал проекта', url='https://t.me/scribo_project')
        btn3 = types.InlineKeyboardButton(text='Главное меню', callback_data='menu')
        markup.add(btn1, btn2)
        markup.add(btn3)
        bot.edit_message_text(
            CONNECT_MESSAGE,
            reply_markup=markup,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
        )
    elif req[0] == 'work':
        btn1 = types.InlineKeyboardButton(text='Главное меню', callback_data='menu')
        markup.add(btn1)
        if call.message.chat.id not in decorating:
            bot.edit_message_text(
                WORK_MESSAGE,
                reply_markup=markup,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
            )
            chat_id = int(req[1])
            message_id = int(req[2])
            file_unique_id = req[3]
            decorating[call.message.chat.id] = chat_id
            current_works.remove((chat_id, message_id, file_unique_id))
        else:
            bot.edit_message_text(
                WRONG_WORK_MESSAGE,
                reply_markup=markup,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
            )
    elif req[0] == 'list':
        btn1 = types.InlineKeyboardButton(text='Главное меню', callback_data='menu')
        markup.add(btn1)
        if len(current_works):
            bot.edit_message_text(
                LIST_MESSAGE,
                reply_markup=markup,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
            )
            for work_chat_id, work_message_id, work_text in current_works:
                bot.send_message(call.message.chat.id, f"{work_chat_id}\n{work_text}")
        else:
            bot.edit_message_text(
                EMPTY_LIST_MESSAGE,
                reply_markup=markup,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
            )


@bot.message_handler(content_types=['document'])
def get_document(message):
    if message.from_user.id in MODERATORS:
        if message.from_user.id in decorating:
            moderator_id = message.from_user.id
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(text='Главное меню', callback_data='menu')
            markup.add(btn1)
            bot.send_message(moderator_id, GOOD_WORK_MESSAGE, reply_markup=markup)
            bot.copy_message(decorating[moderator_id], moderator_id, message.id)
            bot.send_message(decorating[moderator_id], READY_MESSAGE, reply_markup=markup)
            del decorating[moderator_id]
        else:
            bot.send_message(message.from_user.id, NO_WORKS_MESSAGE, parse_mode='Markdown')
    else:
        bot.send_message(message.from_user.id, IDK_MESSAGE)


@bot.message_handler(content_types=['photo'])
def get_photo(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Главное меню', callback_data='menu')
    markup.add(btn1)
    bot.send_message(message.from_user.id, PAID_MESSAGE, reply_markup=markup)
    bot.send_message(ADMIN, f"User @{message.from_user.username} paid!")


def remove_work(work_name):
    for work in current_works:
        if work[2] == work_name:
            current_works.remove(work)
            break


def send_work(cw: CourseWork, moderator: int, user: int, free: bool = False) -> None:
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Главное меню', callback_data='menu')
    markup.add(btn1)
    bot.send_document(moderator, open(cw.file_name("pdf", free), 'rb'))
    bot.send_document(moderator, open(cw.file_name("tex", free), 'rb'))
    bot.send_document(user, open(cw.file_name("pdf", free), 'rb'))
    bot.send_document(user, open(cw.file_name("tex", free), 'rb'))
    bot.send_message(moderator, READY_MESSAGE, reply_markup=markup)
    bot.send_message(user, READY_MESSAGE, reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_message(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Главное меню', callback_data='menu')
    markup.add(btn1)
    if message.from_user.id in MODERATORS and message.text.lower() == "беру":
        if message.from_user.id in decorating:
            bot.send_message(message.from_user.id, WRONG_WORK_MESSAGE, reply_markup=markup)
        elif message.reply_to_message:
            bot.send_message(message.from_user.id, WORK_MESSAGE, reply_markup=markup)
            reply_chat_id = int(message.reply_to_message.text.split("\n")[0])
            decorating[message.from_user.id] = reply_chat_id
            remove_work(message.reply_to_message.text.partition("\n")[2])
        else:
            bot.send_message(message.from_user.id, WRONG_REPLY_MESSAGE, reply_markup=markup)
    if message.from_user.id in MODERATORS and message.text.lower() == "сгенерировать":
        if message.reply_to_message:
            bot.send_message(message.from_user.id, GENERATING_MESSAGE, reply_markup=markup)
            reply_chat_id = int(message.reply_to_message.text.split("\n")[0])
            for i in range(TRIES_COUNT):
                bot.send_message(message.from_user.id, ATTEMPT_MESSAGE.format(i), reply_markup=markup)
                cw = factory.generate_coursework(message.reply_to_message.text.split("\n")[1])
                try:
                    if cw.save(free=False):
                        send_work(cw, message.from_user.id, reply_chat_id, free=False)
                        remove_work(cw.name)
                        cw.delete()
                        break
                except Exception as e:
                    log(f"Exception while saving: {e}")
                finally:
                    cw.delete(i < TRIES_COUNT - 1)
            else:
                bot.send_message(message.from_user.id,
                                 PROBLEM_MESSAGE.format(message.reply_to_message.text.split("\n")[1]),
                                 reply_markup=markup)
        else:
            bot.send_message(message.from_user.id, WRONG_REPLY_MESSAGE, reply_markup=markup)
    elif message.from_user.id not in MODERATORS:
        users_works_count[message.from_user.id] = users_works_count.get(message.from_user.id, 0) + 1
        bot.send_message(
            message.from_user.id,
            WORK_DOWNLOADED_MESSAGE,
            parse_mode='Markdown',
            reply_markup=markup,
        )
        current_works.append((message.from_user.id, message.id, message.text))
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(
            text='Взять в работу',
            callback_data=f'work_{message.from_user.id}_{message.id}_{message.text}',
        )
        btn2 = types.InlineKeyboardButton(text='Главное меню', callback_data='menu')
        markup.add(btn1)
        markup.add(btn2)
        for moderator_id in MODERATORS:
            try:
                bot.send_message(moderator_id, f"{message.from_user.id}\n{message.text}")
                bot.send_message(moderator_id, NEW_WORK_MESSAGE, reply_markup=markup)
            except telebot.apihelper.ApiTelegramException:
                print(f"Moderator {moderator_id} has not started the bot yet")

        for i in range(TRIES_COUNT):
            bot.send_message(ADMIN, ATTEMPT_MESSAGE.format(i))
            cw = factory.generate_coursework(message.text)
            try:
                if cw.save(free=True):
                    send_work(cw, ADMIN, message.from_user.id, free=True)
                    remove_work(message.text)
                    cw.delete()
                    break
            except Exception as e:
                log(f"Exception while saving: {e}")
            finally:
                cw.delete(i < TRIES_COUNT - 1)
        else:
            bot.send_message(ADMIN,
                             PROBLEM_MESSAGE.format(message.text.split("\n")[1]),
                             reply_markup=markup)


log("Bot is running!", bot)
bot.infinity_polling()
