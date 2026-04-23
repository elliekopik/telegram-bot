import telebot
from telebot import types
from flask import Flask, request
import os

bot = telebot.TeleBot('8444015997:AAG5fJECvwVJqbZmaehxr813VGFjWT9rvOA')
app = Flask(__name__)

# ЗАМЕНИТЕ НА ВАШ TELEGRAM ID
YOUR_TELEGRAM_ID = -5050212207

user_data = {}
user_step = {}  # Храним текущий шаг пользователя

# СТАРТ
@bot.message_handler(commands=['start'])
def send_welcome(message):
    knopka = types.InlineKeyboardMarkup()
    knopka.add(types.InlineKeyboardButton('Заполнить форму 📝', callback_data='form'))
    bot.send_message(message.chat.id, "Вас приветствует бот-турагент НиЭль-Тур!🌴 С ним вы сможете подобрать самый комфортный тур по вашим критериям.",
                     reply_markup=knopka)

# Проверка, не пытается ли пользователь нажать на старую кнопку
def check_step(call, expected_step, step_name):
    current_step = user_step.get(call.message.chat.id, None)
    if current_step != expected_step:
        bot.answer_callback_query(call.id)
        knopka = types.InlineKeyboardMarkup()
        knopka.add(types.InlineKeyboardButton('✅ Продолжить', callback_data='continue_filling'))
        knopka.add(types.InlineKeyboardButton('🔄 Заполнить заново', callback_data='restart_filling'))
        bot.send_message(call.message.chat.id, 
                         "❓ Вы нажали на кнопку из старого сообщения.\nПродолжим заполнение анкеты?",
                         reply_markup=knopka)
        return False
    return True

# Обработчик "Продолжить"
@bot.callback_query_handler(func=lambda call: call.data == 'continue_filling')
def continue_filling(call):
    bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    step = user_step.get(chat_id, 'city')
    
    if step == 'city':
        show_country_menu(call.message)
    elif step == 'date':
        bot.send_message(chat_id, 'Введите примерную дату вылета.')
        bot.register_next_step_handler(call.message, get_date)
    elif step == 'nights':
        bot.send_message(chat_id, 'Укажите примерное количество ночей.')
        bot.register_next_step_handler(call.message, get_nights)
    elif step == 'stars':
        ask_stars(call.message)
    elif step == 'adults':
        knopka = types.InlineKeyboardMarkup()
        for i in range(1, 5):
            knopka.add(types.InlineKeyboardButton(f'{i} взрослых', callback_data=f'adults_{i}'))
        bot.send_message(chat_id, 'Пожалуйста, выберите количество взрослых.', reply_markup=knopka)
    elif step == 'kids':
        knopka = types.InlineKeyboardMarkup()
        for i in range(0, 5):
            knopka.add(types.InlineKeyboardButton(f'{i} детей', callback_data=f'kids_{i}'))
        bot.send_message(chat_id, 'Выберите количество детей (Если без детей — ставьте 0).', reply_markup=knopka)
    elif step == 'budget':
        bot.send_message(chat_id, 'Примерный бюджет (в рублях).')
        bot.register_next_step_handler(call.message, get_budget)

# Обработчик "Заполнить заново"
@bot.callback_query_handler(func=lambda call: call.data == 'restart_filling')
def restart_filling(call):
    bot.answer_callback_query(call.id)
    if call.message.chat.id in user_data:
        del user_data[call.message.chat.id]
    if call.message.chat.id in user_step:
        del user_step[call.message.chat.id]
    send_welcome(call.message)

# ГОРОД ОТПРАВЛЕНИЯ
@bot.callback_query_handler(func=lambda call: call.data == 'form')
def callback_departure_city(call):
    knopka = types.InlineKeyboardMarkup()
    knopka.add(types.InlineKeyboardButton('Москва', callback_data='city_Москва'))
    knopka.add(types.InlineKeyboardButton('Санкт-Петербург', callback_data='city_Санкт-Петербург'))
    knopka.add(types.InlineKeyboardButton('Екатеринбург', callback_data='city_Екатеринбург'))
    knopka.add(types.InlineKeyboardButton('Новосибирск', callback_data='city_Новосибирск'))
    knopka.add(types.InlineKeyboardButton('Другой', callback_data='city_Другой'))
    bot.send_message(call.message.chat.id, 'Выберите город отправления.', reply_markup=knopka)

@bot.callback_query_handler(func=lambda call: call.data.startswith('city_'))
def callback_country_start(call):
    if not check_step(call, 'city', 'city'):
        return
    
    city = call.data.split('_')[1]
    
    if city == 'Другой':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, 'Введите название города отправления.')
        bot.register_next_step_handler(call.message, get_custom_city)
    else:
        user_data[call.message.chat.id] = {'city': city}
        user_step[call.message.chat.id] = 'country'
        bot.answer_callback_query(call.id)
        show_country_menu(call.message)

def get_custom_city(message):
    city = message.text
    user_data[message.chat.id] = {'city': city}
    user_step[message.chat.id] = 'country'
    bot.send_message(message.chat.id, f'Город отправления: {city}')
    show_country_menu(message)

def show_country_menu(message):
    knopka = types.InlineKeyboardMarkup(row_width=2)
    countries = ['Армения 🇦🇲', 'Вьетнам 🇻🇳', 'Грузия 🇬🇪', 'Египет 🇪🇬', 
                 'Индонезия(Бали) 🇮🇩', 'Китай 🇨🇳', 'Мальдивы 🇲🇻', 'ОАЭ 🇦🇪', 
                 'Россия 🇷🇺', 'Сейшелы 🇸🇨', 'Таиланд 🇹🇭', 'Турция 🇹🇷', 
                 'Узбекистан 🇺🇿', 'Шри-Ланка 🇱🇰', 'Другая']
    for country in countries:
        knopka.add(types.InlineKeyboardButton(country, callback_data=f'country_{country}'))
    bot.send_message(message.chat.id, 'Пожалуйста, выберите страну направления.', reply_markup=knopka)

@bot.callback_query_handler(func=lambda call: call.data.startswith('country_'))
def callback_date_start(call):
    if not check_step(call, 'country', 'country'):
        return
    
    country = call.data.split('_')[1]

    if country == 'Другая':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, 'Введите название страны.')
        bot.register_next_step_handler(call.message, get_custom_country)
    else:
        user_data[call.message.chat.id]['country'] = country
        user_step[call.message.chat.id] = 'date'
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, 'Введите примерную дату вылета.')
        bot.register_next_step_handler(call.message, get_date)

def get_custom_country(message):
    custom_country = message.text
    user_data[message.chat.id]['country'] = custom_country
    user_step[message.chat.id] = 'date'
    bot.send_message(message.chat.id, f'Страна: {custom_country}')
    bot.send_message(message.chat.id, 'Введите примерную дату вылета')
    bot.register_next_step_handler(message, get_date)

def get_date(message):
    date = message.text
    user_data[message.chat.id]['date'] = date
    user_step[message.chat.id] = 'nights'
    bot.send_message(message.chat.id, f'Примерная дата вылета: {date}')
    bot.send_message(message.chat.id, 'Укажите примерное количество ночей.')
    bot.register_next_step_handler(message, get_nights)

def get_nights(message):
    try:
        nights = int(message.text)
        user_data[message.chat.id]['nights'] = nights
        user_step[message.chat.id] = 'stars'
        bot.send_message(message.chat.id, f'Количество ночей: {nights}')
        ask_stars(message)
    except:
        bot.send_message(message.chat.id, 'Пожалуйста, введите число.')
        bot.register_next_step_handler(message, get_nights)

def ask_stars(message):
    knopka = types.InlineKeyboardMarkup()
    for i in range(3, 6):
        knopka.add(types.InlineKeyboardButton(f'от {i} звезд', callback_data=f'stars_{i}'))
    bot.send_message(message.chat.id, 'Пожалуйста, выберите категорию звёздности отеля.', reply_markup=knopka)

@bot.callback_query_handler(func=lambda call: call.data.startswith('stars_'))
def callback_adult(call):
    if not check_step(call, 'stars', 'stars'):
        return
    
    stars = call.data.split('_')[1]
    user_data[call.message.chat.id]['stars'] = stars
    user_step[call.message.chat.id] = 'adults'
    bot.answer_callback_query(call.id)
    knopka = types.InlineKeyboardMarkup()
    for i in range(1, 5):
        knopka.add(types.InlineKeyboardButton(f'{i} взрослых', callback_data=f'adults_{i}'))
    bot.send_message(call.message.chat.id, 'Пожалуйста, выберите количество взрослых.', reply_markup=knopka)

@bot.callback_query_handler(func=lambda call: call.data.startswith('adults_'))
def callback_kids(call):
    if not check_step(call, 'adults', 'adults'):
        return
    
    adults = call.data.split('_')[1]
    user_data[call.message.chat.id]['adults'] = adults
    user_step[call.message.chat.id] = 'kids'
    bot.answer_callback_query(call.id)
    knopka = types.InlineKeyboardMarkup()
    for i in range(0, 5):
        knopka.add(types.InlineKeyboardButton(f'{i} детей', callback_data=f'kids_{i}'))
    bot.send_message(call.message.chat.id, 'Выберите количество детей (Если без детей — ставьте 0).',
                     reply_markup=knopka)

@bot.callback_query_handler(func=lambda call: call.data.startswith('kids_'))
def callback_kidsage(call):
    if not check_step(call, 'kids', 'kids'):
        return
    
    kids_count = call.data.split('_')[1]
    user_data[call.message.chat.id]['kids_count'] = kids_count
    bot.answer_callback_query(call.id)
    
    if kids_count == '0':
        user_step[call.message.chat.id] = 'budget'
        ask_budget(call.message)
    else:
        user_step[call.message.chat.id] = 'kids_age'
        bot.send_message(call.message.chat.id,
                         'Введите возраст ребенка (Если несколько детей, запишите через запятую.)')
        bot.register_next_step_handler(call.message, get_kids_age)

def get_kids_age(message):
    kids_age = message.text
    user_data[message.chat.id]['kids_age'] = kids_age
    user_step[message.chat.id] = 'budget'
    bot.send_message(message.chat.id, f'Возраст детей: {kids_age}')
    ask_budget(message)

def ask_budget(message):
    bot.send_message(message.chat.id, 'Примерный бюджет (в рублях).')
    bot.register_next_step_handler(message, get_budget)

def get_budget(message):
    try:
        budget = int(message.text)
        user_data[message.chat.id]['budget'] = budget
        user_step[message.chat.id] = 'confirm'
        bot.send_message(message.chat.id, f'Бюджет до: {budget} руб.')

        data = user_data[message.chat.id]

        confirm_text = (f"📝 Проверьте правильность введенных данных:\n\n"
                        f"🏙️ Город отправления: {data['city']}\n"
                        f"🌍 Страна: {data['country']}\n"
                        f"📅 Дата вылета: {data['date']}\n"
                        f"🌙 Ночей: {data['nights']}\n"
                        f"⭐ Звезд: от {data['stars']}\n"
                        f"👨‍👩 Взрослых: {data['adults']}\n"
                        f"👶 Детей: {data.get('kids_count', '0')}\n"
                        f"🧩 Возраст детей: {data.get('kids_age', '-')}\n"
                        f"💰 Бюджет до: {data['budget']} руб.\n\n"
                        f"✅ Всё верно?")

        confirm_knopka = types.InlineKeyboardMarkup(row_width=2)
        confirm_knopka.add(
            types.InlineKeyboardButton('✅ Да, всё верно', callback_data='confirm_yes'),
            types.InlineKeyboardButton('❌ Нет, изменить', callback_data='confirm_no')
        )

        bot.send_message(message.chat.id, confirm_text, reply_markup=confirm_knopka, parse_mode='Markdown')
    except:
        bot.send_message(message.chat.id, 'Пожалуйста, введите число')
        bot.register_next_step_handler(message, get_budget)

@bot.callback_query_handler(func=lambda call: call.data == 'confirm_yes')
def confirm_yes(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    data = user_data[call.message.chat.id]

    new_order_knopka = types.InlineKeyboardMarkup()
    new_order_knopka.add(types.InlineKeyboardButton('🔄 Подать новую заявку', callback_data='new_order'))

    summary = (f"✅ Ваша заявка принята!\n\n"
               f"🏙️ Город отправления: {data['city']}\n"
               f"🌍 Страна: {data['country']}\n"
               f"📅 Дата вылета: {data['date']}\n"
               f"🌙 Ночей: {data['nights']}\n"
               f"⭐ Звезд: от {data['stars']}\n"
               f"👨‍👩 Взрослых: {data['adults']}\n"
               f"👶 Детей: {data.get('kids_count', '0')}\n"
               f"🧩 Возраст детей: {data.get('kids_age', '-')}\n"
               f"💰 Бюджет до: {data['budget']} руб.\n\n"
               f"✨ С вами свяжутся в течение получаса.")
    bot.send_message(call.message.chat.id, summary, reply_markup=new_order_knopka)

    client_name = call.from_user.first_name or call.from_user.username or "Клиент"
    client_username = f"@{call.from_user.username}" if call.from_user.username else "нет username"

    agent_summary = (f"📋 НОВАЯ ЗАЯВКА!\n\n"
                     f"👤 Клиент: {client_name}\n"
                     f"📱 Username: {client_username}\n"
                     f"🏙️ Город отправления: {data['city']}\n"
                     f"🌍 Страна: {data['country']}\n"
                     f"📅 Дата вылета: {data['date']}\n"
                     f"🌙 Ночей: {data['nights']}\n"
                     f"⭐ Звезд: от {data['stars']}\n"
                     f"👨‍👩 Взрослых: {data['adults']}\n"
                     f"👶 Детей: {data.get('kids_count', '0')}\n"
                     f"🧩 Возраст детей: {data.get('kids_age', '-')}\n"
                     f"💰 Бюджет до: {data['budget']} руб.\n\n"
                     f"✅ Чтобы ответить клиенту, напишите ему: @{call.from_user.username if call.from_user.username else 'username отсутствует'}")

    try:
        bot.send_message(YOUR_TELEGRAM_ID, agent_summary)
        bot.send_message(call.message.chat.id, "📨 Заявка отправлена турагенту!")
    except:
        bot.send_message(call.message.chat.id, "⚠️ Заявка сохранена, оператор свяжется с вами.")

    del user_data[call.message.chat.id]
    del user_step[call.message.chat.id]

@bot.callback_query_handler(func=lambda call: call.data == 'confirm_no')
def confirm_no(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    if call.message.chat.id in user_data:
        del user_data[call.message.chat.id]
    if call.message.chat.id in user_step:
        del user_step[call.message.chat.id]
    
    knopka = types.InlineKeyboardMarkup()
    knopka.add(types.InlineKeyboardButton('Москва', callback_data='city_Москва'))
    knopka.add(types.InlineKeyboardButton('Санкт-Петербург', callback_data='city_Санкт-Петербург'))
    knopka.add(types.InlineKeyboardButton('Екатеринбург', callback_data='city_Екатеринбург'))
    knopka.add(types.InlineKeyboardButton('Новосибирск', callback_data='city_Новосибирск'))
    knopka.add(types.InlineKeyboardButton('Другой', callback_data='city_Другой'))
    bot.send_message(call.message.chat.id, 'Выберите город отправления.', reply_markup=knopka)

@bot.callback_query_handler(func=lambda call: call.data == 'new_order')
def new_order(call):
    bot.answer_callback_query(call.id)
    if call.message.chat.id in user_data:
        del user_data[call.message.chat.id]
    if call.message.chat.id in user_step:
        del user_step[call.message.chat.id]
    send_welcome(call.message)

# ========== КОД ДЛЯ ВЕБХУКОВ ==========
def set_webhook():
    webhook_url = os.environ.get('RENDER_EXTERNAL_URL')
    if webhook_url:
        webhook_url = f"{webhook_url}/webhook"
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        print(f"Вебхук установлен: {webhook_url}")
    else:
        print("RENDER_EXTERNAL_URL не найден, проверьте настройки Render")

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        return 'Bad request', 400

@app.route('/health')
def health():
    return 'OK', 200

@app.route('/livez')
def livez():
    return 'OK', 200

if __name__ == '__main__':
    set_webhook()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
