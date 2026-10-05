import telebot
import requests
from telebot import types
TOKEN = '8434411728:AAHklgLfR110yNJ3A4gW0LdzwAOw0uxMG_s'
bot = telebot.TeleBot(TOKEN)
currencies = {
    "USD": "dollar",
    "CNY": "yuan",
    "JPY": "yen",
    "KZT": "tenge",
    "EUR": "euro",
    "RUB": "rub",
}
user_data = {}

def get_rate(from_currency, to_currency):
    url = (
        f"https://open.er-api.com/v6/latest/{from_currency}"
    )
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    return data["rates"].get(to_currency)
def currency_keyboard():
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=3,
    )
    buttons = []
    for currency in currencies:
        buttons.append(types.KeyboardButton(currency))
    keyboard.add(*buttons)
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {}
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    ru_button = types.KeyboardButton("русский")
    en_button = types.KeyboardButton("английский")
    keyboard.add(ru_button, en_button)
    bot.send_message(message.chat.id,"Привет! Я бот для конвертации валют", reply_markup=keyboard)
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "Как пользоватся ботом?\n\n"
        "1.Выбери валюту кнопкой\n"
        "2.Или напиши валюту и сумму\n"
        "Пример:\n"
        "USD KZT 100\n"
        "Это означает перевести 100 долларов в тенге"
    )
@bot.message_handler(commands=['rate'])
def rate_command(message):
    user_data[message.chat.id] = {
        "step": "from_currency"
    }
    bot.send_message(
        message.chat.id,
        "Выберите валюту из которой хотите перевести",
        reply_markup=currency_keyboard()
    )
@bot.message_handler(func=lambda message: message.text in["русский", "английский"])
def choose_language(message):
    if message.text == "русский":
        bot.send_message(
            message.chat.id,
            "язык изменен на русский"
        )
    else:
        bot.send_message(
            message.chat.id,
            "language changed to english"
        )
@bot.message_handler(func=lambda message: message.text in currencies)
def choose_currency(message):
    chat_id = message.chat.id
    currency = message.text
    if chat_id not in user_data:
        user_data[chat_id] = {"step": "from_currency"}
    if user_data[chat_id].get("step") == "from_currency":
        user_data[chat_id]["from_currency"] = currency
        user_data[chat_id]["step"] = "to_currency"
        bot.send_message(
            chat_id,
            f"Вы выбрали {currency}\n\n"
            "Теперь выберите валюту,  в которую хотели перевести",
            reply_markup = currency_keyboard()
        )
    elif user_data[chat_id].get("step") == "to_currency":
        user_data[chat_id]["to_currency"] = currency
        user_data[chat_id]["step"] = "amount"
        from_currency = user_data[chat_id]["from_currency"]
        bot.send_message(
            chat_id,
            f"{from_currency}>{currency}\n\n"
            "Теперь введите сумму"

        )
    else:
        bot.send_message(
            chat_id,
            "Сначала используйте /rate или выберите валюту через /start"
        )
@bot.message_handler(func=lambda message: True)
def convert_currency(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        bot.send_message(
            chat_id,
            "Начните с команды /start"
        )
        return

    if user_data[chat_id].get("step") != "amount":

        bot.send_message(
            chat_id,
            "Чтобы начать конвертацию, используйте /rate"
        )
        return

    from_currency = user_data[chat_id]["from_currency"]
    to_currency = user_data[chat_id]["to_currency"]

    try:
        amount = float(message.text.replace(".", ","))
    except ValueError:
        bot.send_message(
            chat_id,
            "Сумма должна быть числом \n\n"
            "Например: 100"
        )
        return
    rate = get_rate(from_currency, to_currency)
    if rate is None:
        bot.send_message(
            chat_id,
            "Не удалось получить курс валют"
        )
        return


    result = amount * rate
    bot.send_message(
        chat_id,
        f"Конвертация \n\n"
        f"{amount} {from_currency} = "
        f"{result:.2f} {to_currency}\n\n"
        f"Курс: \n"
        f"1 {from_currency} ="
        f"{rate:.4f} {to_currency}\n\n"
        "Чтобы сделать новую конвертацию, используйте /rate"
    )
    user_data[chat_id] = {}
bot.polling()

