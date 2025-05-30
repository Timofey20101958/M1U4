import telebot
import random
import time, threading, schedule
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TELEGRAM_TOKEN = '8087350032:AAHV5WaR4Vk_WENxfstsX7zJ6HzfEgzaSlk'

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['info'])
def info(message):
    bot.reply_to(message, "Доступные команды:\n"\
        "/hello - выдаёт рандомное приветствие\n"\
        "/dice - команда выдающая случайное число от 1 до 6\n"\
        "/set [sec] - команда задающая время для таймера\n"
        "/unset - команда абнуляющая таймер"
        "или вы можете написать текст и ответить на вопрос"   )

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, "привет! используй /set <seconds> для создания таймера")


def beep(chat_id) -> None:
    """Send the beep message."""
    bot.send_message(chat_id, text='Beep!')


@bot.message_handler(commands=['set'])
def set_timer(message):
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        sec = int(args[1])
        schedule.every(sec).seconds.do(beep, message.chat.id).tag(message.chat.id)
    else:
        bot.reply_to(message, 'Usage: /set <seconds>')


@bot.message_handler(commands=['unset'])
def unset_timer(message):
    schedule.clear(message.chat.id)


if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    while True:
        schedule.run_pending()
        time.sleep(1)

@bot.message_handler(commands=['hello'])
def hello(message):
    random_hello = random.choice(['Привет',"здарова","Добро пожаловать"])
    bot.reply_to(message,random_hello)

@bot.message_handler(commands=['dice'])
def dice(message):
    random_hello = random.choice(['Привет',"здарова","Добро пожаловать"])
    bot.reply_to(message,random.randint(1,6))

def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("10", callback_data="cb_yes"),
                               InlineKeyboardButton("не 10", callback_data="cb_no"))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cb_yes":
        bot.answer_callback_query(call.id, "Answer is 10")
    elif call.data == "cb_no":
        bot.answer_callback_query(call.id, "Answer is не 10")
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cb_yes":
        bot.answer_callback_query(call.id, "Вы ответили верно!")
    elif call.data == "cb_no":
        bot.answer_callback_query(call.id, "Вы ошиблись")

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    bot.send_message(message.chat.id, "Если ты родился 10 лет назат, то сколько тебе сейчас?", reply_markup=gen_markup())

bot.infinity_polling()