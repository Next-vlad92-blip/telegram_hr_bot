import os
from telebot import TeleBot, types
from config import TELEGRAM_TOKEN, ADMIN_IDS

bot = TeleBot(TELEGRAM_TOKEN)

# Корневая папка с документами
DOCS_DIR = "documents"

# Категории: id -> отображение
category_ids = {
    "zayavleniya": "Заявления",
    "sots_politika": "Социальная политика",
    "zarplata": "Зарплата"
}

# Эмодзи для кнопок
emoji_map = {
    "zayavleniya": "📝",
    "sots_politika": "📄",
    "zarplata": "💰"
}

# Создаем папки, если их нет
for cat_id, cat_name in category_ids.items():
    path = os.path.join(DOCS_DIR, cat_name)
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Создана папка: {path}")

# Функция для сканирования папок и файлов
def get_categories():
    cats = {}
    for cat_name in category_ids.values():
        path = os.path.join(DOCS_DIR, cat_name)
        if os.path.exists(path):
            files = os.listdir(path)
            cats[cat_name] = files
    return cats

# Глобальная переменная для хранения файлов
files_dict = get_categories()

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    for cat_id, cat_name in category_ids.items():
        markup.add(types.InlineKeyboardButton(
            text=f"{emoji_map.get(cat_id,'📁')} {cat_name}",
            callback_data=f"cat_{cat_id}"
        ))
    # Кнопка FAQ
    markup.add(types.InlineKeyboardButton(text="❓ FAQ", callback_data="faq"))
    bot.send_message(message.chat.id, "Привет! Выберите категорию документов:", reply_markup=markup)

# Обработка нажатий
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data

    if data.startswith("cat_"):
        cat_id = data[4:]
        cat_name = category_ids.get(cat_id)
        if not cat_name:
            bot.send_message(call.message.chat.id, "Неизвестная категория 😢")
            return

        files = files_dict.get(cat_name, [])
        markup = types.InlineKeyboardMarkup()
        if files:
            for i, f in enumerate(files):
                markup.add(types.InlineKeyboardButton(
                    text=f, callback_data=f"file_{cat_id}_{i}"
                ))
        else:
            bot.send_message(call.message.chat.id, "В этой категории пока нет файлов 😢")
            return

        markup.add(types.InlineKeyboardButton(text="🔙 Назад", callback_data="back"))
        bot.send_message(call.message.chat.id, f"Файлы в категории '{cat_name}':", reply_markup=markup)

    elif data.startswith("file_"):
        _, cat_id, index_str = data.split("_", 2)
        cat_name = category_ids.get(cat_id)
        files = files_dict.get(cat_name, [])
        try:
            index = int(index_str)
            file_name = files[index]
        except (ValueError, IndexError):
            bot.send_message(call.message.chat.id, "Файл не найден 😢")
            return

        file_path = os.path.join(DOCS_DIR, cat_name, file_name)
        if os.path.exists(file_path):
            with open(file_path, "rb") as doc:
                bot.send_document(call.message.chat.id, doc)
        else:
            bot.send_message(call.message.chat.id, "Файл не найден 😢")

    elif data == "back":
        start(call.message)

    elif data == "faq":
        bot.send_message(call.message.chat.id, "В разработке ⚙️")

# Команда админа для обновления списка файлов
@bot.message_handler(commands=['reload'])
def reload_docs(message):
    if message.from_user.id in ADMIN_IDS:
        global files_dict
        files_dict = get_categories()
        bot.send_message(message.chat.id, "Список документов обновлен ✅")
    else:
        bot.send_message(message.chat.id, "У вас нет прав на эту команду 🚫")

print("Бот с документами и русскими папками запущен...")
bot.infinity_polling()
