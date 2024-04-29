import telebot
from telebot import types
import time
import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.environ['TELEGRAM_TOKEN']

bot = telebot.TeleBot(token=TOKEN)
chat_id = None
name = None

@bot.message_handler(commands=['start'])
def start_message(message):

    conn = sqlite3.connect('mutibot_database.sql')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, chat_id int, name varchar(50), weight real, date date, beautiful_date text)')
    conn.commit()

    cur.close()
    conn.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_diff_today = types.KeyboardButton('Ежедневное ♻')
    button_diff_month = types.KeyboardButton('Результаты месяца 🏆')
    button_diff_week = types.KeyboardButton('Результаты недели 🥇')
    markup.add(button_diff_today, button_diff_week, button_diff_month)
    bot.send_message(
        message.chat.id,
        text=f'Привет, {message.from_user.first_name}!',
        reply_markup=markup
    )

@bot.message_handler(content_types=['text'])
def weight_analytic(message):
    global chat_id, name
    chat_id = message.chat.id
    name = message.from_user.first_name
    if (message.text == 'Результаты недели 🥇'):
        conn = sqlite3.connect('mutibot_database.sql')

        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE chat_id = ? ORDER BY date DESC LIMIT 7', (chat_id,))
        print_week_results = cur.fetchall()
        print_week_results_list = [list(print_week_result) for print_week_result in print_week_results]
        beautiful_output = '\n'.join([f"{row[5]} - {row[3]} кг." for row in print_week_results_list])
        bot.send_message(
                message.chat.id,
                text=f'Ваш вес за последние 7 дней:\n {beautiful_output}'
            )

        cur.close()
        conn.close()

    elif (message.text == 'Результаты месяца 🏆'):
        conn = sqlite3.connect('mutibot_database.sql')

        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE chat_id = ? ORDER BY date DESC LIMIT 30', (chat_id,))
        print_week_results = cur.fetchall()
        print_week_results_list = [list(print_week_result) for print_week_result in print_week_results]
        beautiful_output = '\n'.join([f"{row[5]} - {row[3]} кг." for row in print_week_results_list])
        bot.send_message(
                message.chat.id,
                text=f'Ваш вес за последние 30 дней:\n {beautiful_output}'
            )

        cur.close()
        conn.close()
    elif (message.text == 'Ежедневное ♻'):
        bot.send_message(message.chat.id, text='Сколько Вы весите сегодня?')
        bot.register_next_step_handler(message, get_user_weight)
    

def get_user_weight(message):
    try:
        weight = round(float(message.text), 1)
        date = time.strftime("%Y %m %d", time.localtime(message.date))
        beautiful_date = time.strftime("%d.%m.%Y", time.localtime(message.date))

        conn = sqlite3.connect('mutibot_database.sql')

        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE chat_id = ? AND date = ?', (chat_id, date,))

        already_exists_date = cur.fetchone()
        if not already_exists_date:
            cur.execute(f'INSERT INTO users (chat_id, name, weight, date, beautiful_date) VALUES ("{chat_id}", "{name}", "{weight}", "{date}", "{beautiful_date}")')
            conn.commit()
            bot.send_message(message.chat.id, text=f'Отлично! Сегодня Вы весите - {weight} кг.')
        else:
            bot.send_message(message.chat.id, text='Сегодня Вы уже присылали свой вес 🤨')
        cur.close()
        conn.close()

    except ValueError:
        try:
            weight = int(str(message.text)[:3])
            date = time.strftime("%Y %m %d", time.localtime(message.date))
            beautiful_date = time.strftime("%d.%m.%Y", time.localtime(message.date))

            conn = sqlite3.connect('mutibot_database.sql')

            cur = conn.cursor()
            cur.execute('SELECT * FROM users WHERE chat_id = ? AND date = ?', (chat_id, date,))

            already_exists_date = cur.fetchone()
            if not already_exists_date:
                cur.execute(f'INSERT INTO users (chat_id, name, weight, date, beautiful_date) VALUES ("{chat_id}", "{name}", "{weight}", "{date}", "{beautiful_date}")')
                conn.commit()
                bot.send_message(message.chat.id, text=f'Отлично! Сегодня Вы весите - {weight} кг.')
            else:
                bot.send_message(message.chat.id, text='Сегодня Вы уже присылали свой вес 🤨')
            cur.close()
            conn.close()
        except ValueError:
            bot.send_message(message.chat.id, text='Введите только число (целое, либо с десятичной частью через точку)')
    

bot.polling(none_stop=True)