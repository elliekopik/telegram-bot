import telebot
from telebot import types
from flask import Flask, request
import os

bot = telebot.TeleBot('8444015997:AAG5fJECvwVJqbZmaehxr813VGFjWT9rvOA')
app = Flask(__name__)

# ЗАМЕНИТЕ НА ВАШ TELEGRAM ID
YOUR_TELEGRAM_ID = -5050212207

user_data = {}

# ========== ВСЕ ФУНКЦИИ ==========

# СТАРТ
@bot.message_handler(commands=['start'])
def send_welcome(message):
    knopka = types.InlineKeyboardMarkup()
    knopka.add(types.InlineKeyboardButton('Заполнить форму 📝', callback_data='form'))
    bot.send_message(message.chat.id, "Вас приветствует бот-турагент НиЭль-Тур!🌴 С ним вы сможете подобрать самый комфортный тур по вашим критериям.",
                     reply_markup=knopka)

# ГОРОД ОТПРАВЛЕНИЯ - 0
@bot.callback_query_handler(func=lambda call: call.data == 'form')
def callback_departure_city(call):
    knopka = types.InlineKeyboardMarkup()
    knopka.add(types.InlineKeyboardButton('Москва', callback_data='city_Москва'))
    knopka.add(types.InlineKeyboardButton('Санкт-Петербург', callback_data='city_Санкт-ПетерБург'))
    knopka.add(types.InlineKeyboardButton('Екатеринбург', callback_data='city_Екатеринбург'))
    knopka.add(types.InlineKeyboardButton('Новосибирск', callback_data='city_Новосибирск'))
    knopka.add(types.InlineKeyboardButton('Другой', callback_data='city_Другой'))
    bot.send_message(call.message.chat.id, 'Выберите город отправления.', reply_markup=knopka)

# ОБРАБОТКА ВЫБОРА ГОРОДА
@bot.callback_query_handler(func=lambda call: call.data.startswith('city_'))
def callback_country_start(call):
    city = call.data.split('_')[1]
    
    if city == 'Другой':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, 'Введите название города отправления.')
        bot.register_next_step_handler(call.message, get_custom_city)
    else:
        user_data[call.message.chat.id] = {'city': city}
        bot.answer_callback_query(call.id)
        show_country_menu(call.message)

def get_custom_city(message):
    city = message.text
    user_data[message.chat.id] = {'city': city}
    bot.send_message(message.chat.id, f'Город отправления: {city}')
    show_country_menu(message)

def show_country_menu(message):
    knopka = types.InlineKeyboardMarkup(row_width=2)
    knopka.add(types.InlineKeyboardButton('Армения 🇦🇲', callback_data='country_Армения'))
    knopka.add(types.InlineKeyboardButton('Вьетнам 🇻🇳', callback_data='country_Вьетнам'))
    knopka.add(types.InlineKeyboardButton('Грузия 🇬🇪', callback_data='country_Грузия'))
    knopka.add(types.InlineKeyboardButton('Египет 🇪🇬', callback_data='country_Египет'))
    knopka.add(types.InlineKeyboardButton('Индонезия(Бали) 🇮🇩', callback_data='country_Индонезия(Бали)'))
    knopka.add(types.InlineKeyboardButton('Китай 🇨🇳', callback_data='country_Китай'))
    knopka.add(types.InlineKeyboardButton('Мальдивы 🇲🇻', callback_data='country_Мальдивы'))
    knopka.add(types.InlineKeyboardButton('ОАЭ 🇦🇪', callback_data='country_ОАЭ'))
    knopka.add(types.InlineKeyboardButton('Россия 🇷🇺', callback_data='country_Россия'))
    knopka.add(types.InlineKeyboardButton('Сейшелы 🇸🇨', callback_data='country_Сейшелы'))
    knopka.add(types.InlineKeyboardButton('Таиланд 🇹🇭', callback_data='country_Таиланд'))
    knopka.add(types.InlineKeyboardButton('Турция 🇹🇷', callback_data='country_Турция'))
    knopka.add(types.InlineKeyboardButton('Узбекистан 🇺🇿', callback_data='country_Узбекистан'))
    knopka.add(types.InlineKeyboardButton('Шри-Ланка 🇱🇰', callback_data='country_Шри-Ланка'))
    knopka.add(types.InlineKeyboardButton('Другая', callback_data='country_Другая'))
    bot.send_message(message.chat.id, 'Пожалуйста, выберите страну направления.', reply_markup=knopka)

# СТРАНА
@bot.callback_query_handler(func=lambda call: call.data.startswith('country_'))
def callback_date(call):
    country = call.data.split('_')[1]

    if country == 'Другая':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, 'Введите название страны.')
        bot.register_next_step_handler(call.message, get_custom_country)
    else:
        user_data[call.message.chat.id]['country'] = country
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, 'Введите примерную дату вылета.')
        bot.register_next_step_handler(call.message, get_date)

def get_custom_country(message):
    custom_country = message.text
    user_data[message.chat.id]['country'] = custom_country
    bot.send_message(message.chat.id, f'Страна: {custom_country}')
    bot.send_message(message.chat.id, 'Введите примерную дату вылета')
    bot.register_next_step_handler(message, get_date)

def get_date(message):
    date = message.text
    user_data[message.chat.id]['date'] = date
    bot.send_message(message.chat.id, f'Примерная дата вылета: {date}')
    bot.send_message(message.chat.id, 'Укажите примерное количество ночей.')
    bot.register_next_step_handler(message, get_nights)

# КОЛИЧЕСТВО НОЧЕЙ
def get_nights(message):
    try:
        nights = int(message.text)
        user_data[message.chat.id]['nights'] = nights
        bot.send_message(message.chat.id, f'Количество ночей: {nights}')
        ask_stars(message)
    except:
        bot.send_message(message.chat.id, 'Пожалуйста, введите число.')
        bot.register_next_step_handler(message, get_nights)

# ЗВЕЗДЫ ОТЕЛЯ
def ask_stars(message):
    knopka = types.InlineKeyboardMarkup()
    for i in range(3, 6):
        knopka.add(types.InlineKeyboardButton(f'от {i} звезд', callback_data=f'stars_{i}'))
    bot.send_message(message.chat.id, 'Пожалуйста, выберите категорию звёздности отеля.', reply_markup=knopka)

@bot.callback_query_handler(func=lambda call: call.data.startswith('stars_'))
def callback_adult(call):
    stars = call.data.split('_')[1]
    user_data[call.message.chat.id]['stars'] = stars
    bot.answer_callback_query(call.id)
    knopka = types.InlineKeyboardMarkup()
    for i in range(1, 5):
        knopka.add(types.InlineKeyboardButton(f'{i} взрослых', callback_data=f'adults_{i}'))
    bot.send_message(call.message.chat.id, 'Пожалуйста, выберите количество взрослых.', reply_markup=knopka)

# ВЗРОСЛЫЕ
@bot.callback_query_handler(func=lambda call: call.data.startswith('adults_'))
def callback_kids(call):
    adults = call.data.split('_')[1]
    user_data[call.message.chat.id]['adults'] = adults
    bot.answer_callback_query(call.id)
    knopka = types.InlineKeyboardMarkup()
    for i in range(0, 5):
        knopka.add(types.InlineKeyboardButton(f'{i} детей', callback_data=f'kids_{i}'))
    bot.send_message(call.message.chat.id, 'Выберите количество детей (Если без детей — ставьте 0).',
                     reply_markup=knopka)

# ДЕТИ КОЛИЧЕСТВО
@bot.callback_query_handler(func=lambda call: call.data.startswith('kids_'))
def callback_kidsage(call):
    kids_count = call.data.split('_')[1]
    user_data[call.message.chat.id]['kids_count'] = kids_count
    bot.answer_callback_query(call.id)
    if kids_count == '0':
        ask_budget(call.message)
    else:
        bot.send_message(call.message.chat.id,
                         'Введите возраст ребенка (Если несколько детей, запишите через запятую.)')
        bot.register_next_step_handler(call.message, get_kids_age)

# ВОЗРАСТ ДЕТЕЙ
def get_kids_age(message):
    kids_age = message.text
    user_data[message.chat.id]['kids_age'] = kids_age
    bot.send_message(message.chat.id, f'Возраст детей: {kids_age}')
    ask_budget(message)

def ask_budget(message):
    bot.send_message(message.chat.id, 'Примерный бюджет (в рублях).')
    bot.register_next_step_handler(message, get_budget)

# БЮДЖЕТ
def get_budget(message):
    try:
        budget = int(message.text)
        user_data[message.chat.id]['budget'] = budget
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

        bot.send_message(message.chat.id, confirm_text, reply_markup=confirm_knopka)

    except:
        bot.send_message(message.chat.id, 'Пожалуйста, введите число')
        bot.register_next_step_handler(message, get_budget)

# ПОДТВЕРЖДЕНИЕ - ДА
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

# ПОДТВЕРЖДЕНИЕ - НЕТ
@bot.callback_query_handler(func=lambda call: call.data == 'confirm_no')
def confirm_no(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    if call.message.chat.id in user_data:
        del user_data[call.message.chat.id]
    
    knopka = types.InlineKeyboardMarkup()
    knopka.add(types.InlineKeyboardButton('Москва', callback_data='city_Москва'))
    knopka.add(types.InlineKeyboardButton('Санкт-Петербург', callback_data='city_Санкт-Петербург'))
    knopka.add(types.InlineKeyboardButton('Екатеринбург', callback_data='city_Екатеринбург'))
    knopka.add(types.InlineKeyboardButton('Новосибирск', callback_data='city_Новосибирск'))
    knopka.add(types.InlineKeyboardButton('Другой', callback_data='city_Другой'))
    bot.send_message(call.message.chat.id, 'Выберите город отправления.', reply_markup=knopka)

# ОБРАБОТЧИК КНОПКИ "Подать новую заявку"
@bot.callback_query_handler(func=lambda call: call.data == 'new_order')
def new_order(call):
    bot.answer_callback_query(call.id)
    if call.message.chat.id in user_data:
        del user_data[call.message.chat.id]
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
