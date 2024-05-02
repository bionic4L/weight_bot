import telebot
from telebot import types
from datetime import datetime
import time
import pytz
import sqlite3
import random
import os
from dotenv import load_dotenv
load_dotenv()

import random_tips as rt

TOKEN = os.environ['TELEGRAM_TOKEN']

bot = telebot.TeleBot(token=TOKEN)
chat_id = None
name = None

moscow_tz = pytz.timezone('Europe/Moscow')
current_time = datetime.now(moscow_tz)

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
    random_figure = random.randint(1, 100)

    if random_figure % 3 == 0:
        tip_week_gain = rt.gain_tip_week
        tip_week_loss = rt.loss_tip_week
    else:
        tip_week_gain = ''
        tip_week_loss = ''
    
    # Результаты недели
    if (message.text == 'Результаты недели 🥇'):
        conn = sqlite3.connect('mutibot_database.sql')

        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM users WHERE chat_id = ? ORDER BY date DESC LIMIT 7',
            (chat_id,)
        )
        print_week_results = cur.fetchall()
        print_week_results_list = [list(print_week_result) for print_week_result in print_week_results]
        beautiful_output = '\n'.join(
            [f"➤ {row[5]} - {row[3]} кг." for row in print_week_results_list]
        )
        bot.send_message(
                message.chat.id,
                text=f'Ваш вес за последние 7 дней:\n{beautiful_output}'
        )

        cur.execute(
            'SELECT * FROM users WHERE chat_id = ? ORDER BY date DESC LIMIT 7',
            (chat_id,)
        )
        rows = cur.fetchall()
        if len(rows) >= 7:
            latest_record = rows[0]
            previous_record = rows[6]


            if latest_record[3] > previous_record[3]:
                bot.send_message(
                    message.chat.id,
                    text=f'За неделю вы набрали {round(float(latest_record[3]) - float(previous_record[3]), 1) * 1000} грамм.\nКруто это или нет - зависит от ваших целей 🎯\n\n{tip_week_gain}'
                    )
            else:
                bot.send_message(
                    message.chat.id,
                    text=f'За неделю вы сбросили {round(float(previous_record[3]) - float(latest_record[3]), 1) * 1000} грамм.\nКруто это или нет - зависит от ваших целей 🎯\n\n{tip_week_loss}'
                    )
        else:
                bot.send_message(
                    message.chat.id,
                    text=f"Недостаточно записей для вывода результатов 🥶\nПрисылайте Ваш вес еще {7 - len(rows)} дней подряд!"
                )
        cur.close()
        conn.close()

    # Результаты месяца
    elif (message.text == 'Результаты месяца 🏆'):
        random_figure = random.randint(1, 100)

        if random_figure % 2 == 0:
            tip_month_gain = rt.gain_tip_month
            tip_month_loss = rt.loss_tip_month
        else:
            tip_month_gain = ''
            tip_month_loss = ''

        conn = sqlite3.connect('mutibot_database.sql')

        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM users WHERE chat_id = ? ORDER BY date DESC LIMIT 30',
            (chat_id,)
        )
        print_week_results = cur.fetchall()
        print_week_results_list = [list(print_week_result) for print_week_result in print_week_results]
        beautiful_output = '\n'.join(
            [f"➤ {row[5]} - {row[3]} кг." for row in print_week_results_list]
        )
        bot.send_message(
                message.chat.id,
                text=f'Ваш вес за последние 30 дней:\n{beautiful_output}'
            )

        cur.execute(
            'SELECT * FROM users WHERE chat_id = ? ORDER BY date DESC LIMIT 7',
            (chat_id,)
        )
        rows = cur.fetchall()
        if len(rows) >= 30:
            latest_record = rows[0]
            previous_record = rows[29]

            if latest_record[3] > previous_record[3]:
                bot.send_message(
                    message.chat.id,
                    text=f'За месяц вы набрали {round(float(latest_record[3]) - float(previous_record[3]), 1) * 1000} грамм.\nКруто это или нет - зависит от ваших целей 🎯\n\n{tip_month_gain}'
                )
            else:
                bot.send_message(
                    message.chat.id,
                    text=f'За месяц вы сбросили {round(float(previous_record[3]) - float(latest_record[3]), 1) * 1000} грамм.\nКруто это или нет - зависит от ваших целей 🎯\n\n{tip_month_loss}'
                )
        else:
                bot.send_message(
                    message.chat.id,
                    text=f"Недостаточно записей для вывода результатов 🥶\nПрисылайте Ваш вес еще {30 - len(rows)} дней подряд!"
                )

        cur.close()
        conn.close()

    elif (message.text == 'Ежедневное ♻'):
        bot.send_message(message.chat.id, text='Сколько Вы весите сегодня?')
        bot.register_next_step_handler(message, get_user_weight)
    
# Обработка ежедневного взвешивания
def get_user_weight(message):
    try:
        weight = round(float(message.text), 1)
        date = time.strftime("%Y %m %d", time.localtime(message.date))
        beautiful_date = time.strftime(
            "%d.%m.%Y",
            time.localtime(message.date)
        )

        conn = sqlite3.connect('mutibot_database.sql')

        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM users WHERE chat_id = ? AND date = ?',
            (chat_id, date,)
        )

        already_exists_date = cur.fetchone()
        if not already_exists_date:
            cur.execute(
                f'INSERT INTO users (chat_id, name, weight, date, beautiful_date) VALUES ("{chat_id}", "{name}", "{weight}", "{date}", "{beautiful_date}")'
            )
            conn.commit()
            bot.send_message(
                message.chat.id,
                text=f'Отлично! Сегодня Вы весите - {weight} кг.'
            )

            cur.execute(
                'SELECT * FROM users WHERE chat_id = ? ORDER BY date DESC LIMIT 2',
                (chat_id,)
            )
            rows = cur.fetchall()
            if len(rows) >= 2:
                latest_record = rows[0]
                previous_record = rows[1]
                random_figure_motivation = random.randint(0, 9)
                if latest_record[3] > previous_record[3]:
                    bot.send_message(
                        message.chat.id,
                        text=f'Вы набрали {round(float(latest_record[3]) - float(previous_record[3]), 1) * 1000} грамм.\nКруто это или нет - зависит от ваших целей 🎯\n\n{rt.random_tips_list[random_figure_motivation]}'
                    )
                else:
                    bot.send_message(
                        message.chat.id,
                        text=f'Вы сбросили {round(float(previous_record[3]) - float(latest_record[3]), 1) * 1000} грамм.\nКруто это или нет - зависит от ваших целей 🎯\n\n{rt.random_tips_list[random_figure_motivation]}'
                    )
            else:
                print("Недостаточно записей 🥶\nПрисылайте вес завтра и все заработает!")
        else:
            bot.send_message(
                message.chat.id,
                text='Сегодня Вы уже присылали свой вес 🤨'
            )

        cur.close()
        conn.close()

    except ValueError:
        try:
            weight = int(str(message.text)[:3])
            date = time.strftime(
                "%Y %m %d",
                time.localtime(message.date)
            )
            beautiful_date = time.strftime(
                "%d.%m.%Y",
                time.localtime(message.date)
            )

            conn = sqlite3.connect('mutibot_database.sql')

            cur = conn.cursor()
            cur.execute(
                'SELECT * FROM users WHERE chat_id = ? AND date = ?',
                (chat_id, date,)
            )

            already_exists_date = cur.fetchone()
            if not already_exists_date:
                cur.execute(
                    f'INSERT INTO users (chat_id, name, weight, date, beautiful_date) VALUES ("{chat_id}", "{name}", "{weight}", "{date}", "{beautiful_date}")'
                )
                conn.commit()
                bot.send_message(
                    message.chat.id,
                    text=f'Отлично! Сегодня Вы весите - {weight} кг.'
                )

                cur.execute(
                    'SELECT * FROM users WHERE chat_id = ? ORDER BY date DESC LIMIT 2',
                    (chat_id,)
                )
                rows = cur.fetchall()
                if len(rows) >= 2:
                    latest_record = rows[0]
                    previous_record = rows[1]

                    if latest_record[3] > previous_record[3]:
                        bot.send_message(
                            message.chat.id,
                            text=f'Вы набрали {round(float(latest_record[3]) - float(previous_record[3]), 1) * 1000} грамм.\nКруто это или нет - зависит от ваших целей 🎯\n\n{rt.random_tips_list[random_figure_motivation]}'
                        )
                    else:
                        bot.send_message(
                            message.chat.id,
                            text=f'Вы сбросили {round(float(previous_record[3]) - float(latest_record[3]), 1) * 1000} .\nКруто это или нет - зависит от ваших целей 🎯\n\n{rt.random_tips_list[random_figure_motivation]}'
                        )
                else:
                    bot.send_message(
                        message.chat.id,
                        text="Недостаточно записей 🥶\nПрисылайте вес завтра и все заработает!"
                    )

            else:
                bot.send_message(
                    message.chat.id,
                    text='Сегодня Вы уже присылали свой вес 🤨'
                )
            cur.close()
            conn.close()
        except ValueError:
            bot.send_message(
                message.chat.id,
                text='Введите только число (целое, либо с десятичной частью через точку)'
            )
    

bot.polling(none_stop=True)