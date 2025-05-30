import telebot
import random
import time
import threading
import schedule
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import api_token

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Хранение балансов пользователей
user_balances = {}

@bot.message_handler(commands=['info'])
def info(message):
    bot.reply_to(message, "Доступные команды:\n"
                 "/hello - выдаёт рандомное приветствие\n"
                 "/dice - команда выдающая случайное число от 1 до 6\n"
                 "/set [sec] - команда задающая время для таймера\n"
                 "/unset - команда отменяющая таймер\n"
                 "/bal - проверить баланс\n"
                 "/dep [amount] - пополнить баланс\n"
                 "/roulett [amount] - играть в рулетку\n"
                 "или вы можете написать текст и ответить на вопрос")

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id not in user_balances:
        user_balances[user_id] = 100  # Начальный баланс
    bot.reply_to(message, "Привет! Используй /set <seconds> для создания таймера или /info для списка команд")

def beep(chat_id) -> None:
    """Send the beep message."""
    bot.send_message(chat_id, text='Beep!')

@bot.message_handler(commands=['set'])
def set_timer(message):
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        sec = int(args[1])
        schedule.every(sec).seconds.do(beep, message.chat.id).tag(message.chat.id)
        bot.reply_to(message, f'Таймер установлен на {sec} секунд')
    else:
        bot.reply_to(message, 'Использование: /set <секунды>')

@bot.message_handler(commands=['unset'])
def unset_timer(message):
    schedule.clear(message.chat.id)
    bot.reply_to(message, 'Таймер отменён')

@bot.message_handler(commands=['hello'])
def hello(message):
    random_hello = random.choice(['Привет', "Здарова", "Добро пожаловать", "Хай", "Приветствую"])
    bot.reply_to(message, random_hello)

@bot.message_handler(commands=['dice'])
def dice(message):
    bot.reply_to(message, f"Выпало: {random.randint(1, 6)}")

# Казино функции
@bot.message_handler(commands=['bal'])
def check_balance(message):
    user_id = message.from_user.id
    if user_id not in user_balances:
        user_balances[user_id] = 100
    bot.reply_to(message, f"Ваш баланс: {user_balances[user_id]} монет")

@bot.message_handler(commands=['dep'])
def deposit(message):
    user_id = message.from_user.id
    args = message.text.split()
    
    if len(args) > 1 and args[1].isdigit():
        amount = int(args[1])
        if amount > 0:
            if user_id not in user_balances:
                user_balances[user_id] = 0
            user_balances[user_id] += amount
            bot.reply_to(message, f"Вы успешно пополнили баланс на {amount} монет. Текущий баланс: {user_balances[user_id]}")
        else:
            bot.reply_to(message, "Сумма должна быть положительной")
    else:
        bot.reply_to(message, "Использование: /dep <сумма>")

@bot.message_handler(commands=['roulett'])
def roulette(message):
    user_id = message.from_user.id
    args = message.text.split()
    
    if user_id not in user_balances:
        user_balances[user_id] = 100
    
    if len(args) > 1 and args[1].isdigit():
        bet = int(args[1])
        if bet <= 0:
            bot.reply_to(message, "Ставка должна быть положительной")
            return
        if bet > user_balances[user_id]:
            bot.reply_to(message, "Недостаточно средств")
            return
        
        # Игра в рулетку
        number = random.randint(0, 36)
        if number == 0:
            win = 0  # зеро - казино забирает всё
            user_balances[user_id] -= bet
            result = f"Выпало зеро (0)! Вы проиграли {bet} монет"
        elif number % 2 == 0:
            win = bet * 2  # красное - x2
            user_balances[user_id] += bet
            result = f"Выпало красное ({number})! Вы выиграли {bet} монет. Ваш выигрыш: {win} монет"
        else:
win = 0  # чёрное - проигрыш
            user_balances[user_id] -= bet
            result = f"Выпало чёрное ({number})! Вы проиграли {bet} монет"
        
        bot.reply_to(message, f"Рулетка: {result}\nТекущий баланс: {user_balances[user_id]}")
    else:
        bot.reply_to(message, "Использование: /roulett <ставка>")

def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("10", callback_data="cb_yes"),
               InlineKeyboardButton("не 10", callback_data="cb_no"))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cb_yes":
        bot.answer_callback_query(call.id, "Вы ответили верно!")
    elif call.data == "cb_no":
        bot.answer_callback_query(call.id, "Вы ошиблись")

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    if message.text.lower() == "сколько тебе лет?" or "сколько тебе сейчас?" in message.text.lower():
        bot.send_message(message.chat.id, "Если ты родился 10 лет назад, то сколько тебе сейчас?", reply_markup=gen_markup())
    else:
        bot.send_message(message.chat.id, "Я не понимаю. Используйте /info для списка команд")

if name == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    while True:
        schedule.run_pending()
        time.sleep(1)
