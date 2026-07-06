import os
import math
from datetime import datetime

print("Kutubxona tekshirilmoqda...")
os.system("pip install pyTelegramBotAPI")
print("Tayyor!")

import telebot
from telebot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID  = int(os.environ.get("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)

ICE_CREAMS = [
    {"id":  1, "name": "БаблГам",  "dona": 15,  "box": 1200},
    {"id":  2, "name": "О эскимо",              "dona": 15,  "box": 1200},
    {"id":  3, "name": "О эскимо шоколад",              "dona": 25,  "box": 1750},
    {"id":  4, "name": "Каракум",               "dona": 16,  "box": 1280},
    {"id":  5, "name": "Дыня",            "dona": 15,  "box": 1200},
    {"id":  6, "name": "Анар",            "dona": 15,  "box": 1200},
    {"id":  7, "name": "Малина",               "dona": 15,  "box": 1200},
    {"id":  8, "name": "БигБум",               "dona": 33,  "box": 825},
    {"id":  9, "name": "Ягодка",               "dona": 15,  "box": 1080},
    {"id": 10, "name": "Мега",               "dona": 27,  "box": 1890},
    {"id": 11, "name": "Мишаня",               "dona": 25,  "box": 1750},
    {"id": 12, "name": "Московский",              "dona": 21,  "box": 1470},
    {"id": 13, "name": "Бест",               "dona": 25,  "box": 1750},
    {"id": 14, "name": "ЛедКола",                  "dona": 7.5,  "box": 900},
    {"id": 15, "name": "ЛедАнар",               "dona": 7.5,  "box": 900},
    {"id": 16, "name": "ЛедСветафор",           "dona": 7.5,  "box": 900},
    {"id": 17, "name": "ЛедЭнержи",                  "dona": 7.5,  "box": 900},
    {"id": 18, "name": "Снежинка",              "dona": 15,  "box": 1200},
    {"id": 19, "name": "Конус",               "dona": 7.5,  "box": 750},
    {"id": 20, "name": "Гномик",               "dona": 7.5,  "box": 630},
    {"id": 21, "name": "Малина",       "dona": 15,  "box": 1200},
    {"id": 22, "name": "КаракумУМУТ",          "dona": 30,  "box": 2100},
    {"id": 23, "name": "ДенНочУМУТ",           "dona": 30,  "box": 2100},
    {"id": 24, "name": "Шакир УМУТ",       "dona": 28,  "box": 2016},
    {"id": 25, "name": "ЛенинградУМУТ",       "dona": 20,  "box": 1440},
    {"id": 26, "name": "ЛенинградКИЛОЛИК",       "dona": 250,  "box": 250},
    {"id": 27, "name": "999",       "dona": 250,  "box": 250},
    {"id": 28, "name": "Газета",       "dona": 35,  "box": 700},
    {"id": 29, "name": "СмакУМУТ",       "dona": 30,  "box": 2100},
    {"id": 30, "name": "Брикет",           "dona": 25,  "box": 1400},
]

users = {}
all_orders = []
is_open = True  # Savdo holati

def get_user(uid):
    if uid not in users:
        users[uid] = {"cart": [], "step": "catalog", "page": 0, "phone": "", "address": ""}
    return users[uid]

def get_ic(ic_id):
    return next((x for x in ICE_CREAMS if x["id"] == ic_id), None)

def catalog_kb(page=0):
    per_page = 7
    start = page * per_page
    total_products = len(ICE_CREAMS)
    end = min(start + per_page, total_products)
    
    total_pages = math.ceil(total_products / per_page)
    
    kb = InlineKeyboardMarkup(row_width=1)
    for ic in ICE_CREAMS[start:end]:
        kb.add(InlineKeyboardButton("🍦 " + ic["name"], callback_data="ic|" + str(ic["id"])))
        
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data="pg|" + str(page-1)))
        
    nav.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="noop"))
    
    if end < total_products:
        nav.append(InlineKeyboardButton("➡️", callback_data="pg|" + str(page+1)))
        
    kb.row(*nav)
    kb.add(InlineKeyboardButton("🛒 Корзина", callback_data="cart"))
    return kb

def type_kb(ic_id):
    ic = get_ic(ic_id)
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🍦 1 штука — " + str(ic["dona"]) + " сом", callback_data="add|" + str(ic_id) + "|dona"))
    kb.add(InlineKeyboardButton("📦 1 коробка — " + str(ic["box"]) + " сом", callback_data="add|" + str(ic_id) + "|box"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="back"))
    return kb

def cart_kb(cart):
    kb = InlineKeyboardMarkup(row_width=1)
    for i, item in enumerate(cart):
        ic = get_ic(item["id"])
        t = "шт." if item["type"] == "dona" else "кор."
        kb.add(InlineKeyboardButton("❌ " + ic["name"] + " (" + t + ")", callback_data="del|" + str(i)))
    if cart:
        kb.add(InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout"))
    kb.add(InlineKeyboardButton("🍦 Продолжить покупки", callback_data="back"))
    return kb

def payment_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("💵 Наличные", callback_data="pay|cash"),
        InlineKeyboardButton("💳 Рассрочка", callback_data="pay|credit")
    )
    return kb

def phone_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("📱 Отправить мой номер", request_contact=True))
    return kb

def format_cart(cart):
    if not cart:
        return "🛒 Корзина пуста"
    lines = ["🛒 Ваша корзина:\n"]
    total = 0
    for i, item in enumerate(cart, 1):
        ic = get_ic(item["id"])
        price = ic["dona"] if item["type"] == "dona" else ic["box"]
        t = "шт." if item["type"] == "dona" else "кор."
        lines.append(str(i) + ". " + ic["name"] + " (" + t + ") — " + str(price) + " сом")
        total += price
    lines.append("\nИтого: " + str(total) + " сом")
    return "\n".join(lines)

@bot.message_handler(commands=["start"])
def cmd_start(msg):
    global is_open
    uid = msg.from_user.id
    if uid == ADMIN_ID:
        is_open = True
        bot.send_message(uid, "✅ Савдо очилди.")
        return
    if not is_open:
        bot.send_message(uid, "🔒 Савдо ёпилди буюртмалар кейинрок уриниб коринг!")
        return
    user = get_user(uid)
    user["cart"] = []
    user["step"] = "catalog"
    user["page"] = 0
    
    total_products = len(ICE_CREAMS)
    bot.send_message(uid,
        f"👋 Добро пожаловать в магазин мороженого!\n\n"
        f"У нас {total_products} видов вкуснейшего мороженого 🍦\n"
        "Выберите понравившийся вкус 👇",
        reply_markup=catalog_kb(0))

@bot.message_handler(commands=["close"])
def cmd_close(msg):
    global is_open
    if msg.from_user.id != ADMIN_ID:
        bot.send_message(msg.chat.id, "⛔ Нет доступа.")
        return
    is_open = False
    today = datetime.now().strftime("%d.%m.%Y")
    todayos = [o for o in all_orders if o["date"] == today]
    if not todayos:
        bot.send_message(msg.chat.id, "🔒 Savdo yopildi.\n\n📊 Bugun buyurtma yo'q.")
        return
    total_sum = sum(o["total"] for o in todayos)
    cash_sum = sum(o["total"] for o in todayos if o["payment"] == "Наличные")
    credit_sum = sum(o["total"] for o in todayos if o["payment"] == "Рассрочка")
    text = ("🔒 Savdo yopildi!\n\n"
        "📊 Kunlik hisobot — " + today + "\n\n"
        "📦 Buyurtmalar: " + str(len(todayos)) + "\n"
        "💵 Naqd: " + str(cash_sum) + " сом\n"
        "💳 Nasiya: " + str(credit_sum) + " сом\n"
        "💰 Jami: " + str(total_sum) + " сом\n\n")
    for idx, o in enumerate(todayos, 1):
        items_str = ", ".join(
            get_ic(i["id"])["name"] + " (" + ("шт." if i["type"]=="dona" else "кор.") + ")"
            for i in o["cart"])
        text += ("Buyurtma #" + str(idx) + " [" + o["time"] + "]\n"
            + o["username"] + " | " + o["phone"] + "\n"
            + o["address"] + "\n"
            + items_str + "\n"
            + str(o["total"]) + " сом (" + o["payment"] + ")\n\n")
    bot.send_message(msg.chat.id, text)

@bot.message_handler(commands=["report"])
def cmd_report(msg):
    if msg.from_user.id != ADMIN_ID:
        bot.send_message(msg.chat.id, "⛔ Нет доступа.")
        return
    today = datetime.now().strftime("%d.%m.%Y")
    todayos = [o for o in all_orders if o["date"] == today]
    if not todayos:
        bot.send_message(msg.chat.id, "📊 Bugun buyurtma yo'q.")
        return
    total_sum = sum(o["total"] for o in todayos)
    cash_sum = sum(o["total"] for o in todayos if o["payment"] == "Наличные")
    credit_sum = sum(o["total"] for o in todayos if o["payment"] == "Рассрочка")
    text = ("📊 Hisobot — " + today + "\n\n"
        "📦 Buyurtmalar: " + str(len(todayos)) + "\n"
        "💵 Naqd: " + str(cash_sum) + " сом\n"
        "💳 Nasiya: " + str(credit_sum) + " сом\n"
        "💰 Jami: " + str(total_sum) + " сом\n\n")
    for idx, o in enumerate(todayos, 1):
        items_str = ", ".join(
            get_ic(i["id"])["name"] + " (" + ("шт." if i["type"]=="dona" else "кор.") + ")"
            for i in o["cart"])
        text += ("Buyurtma #" + str(idx) + " [" + o["time"] + "]\n"
            + o["username"] + " | " + o["phone"] + "\n"
            + o["address"] + "\n"
            + items_str + "\n"
            + str(o["total"]) + " сом (" + o["payment"] + ")\n\n")
    bot.send_message(msg.chat.id, text)

@bot.callback_query_handler(func=lambda c: True)
def on_callback(call):
    global is_open
    uid = call.from_user.id
    user = get_user(uid)
    data = call.data

    if not is_open and uid != ADMIN_ID:
        bot.answer_callback_query(call.id, "🔒 Savdo yopiq!", show_alert=True)
        return

    if data.startswith("pg|"):
        page = int(data.split("|")[1])
        user["page"] = page
        bot.edit_message_text("🍦 Каталог — выберите вкус:",
            uid, call.message.message_id, reply_markup=catalog_kb(page))

    elif data.startswith("ic|"):
        ic_id = int(data.split("|")[1])
        ic = get_ic(ic_id)
        bot.edit_message_text(
            "🍦 " + ic["name"] + "\n\n"
            "• 1 штука — " + str(ic["dona"]) + " сом\n"
            "• 1 коробка — " + str(ic["box"]) + " сом\n\n"
            "Как хотите купить?",
            uid, call.message.message_id, reply_markup=type_kb(ic_id))

    elif data.startswith("add|"):
        parts = data.split("|")
        ic_id = int(parts[1])
        buy_type = parts[2]
        user["cart"].append({"id": ic_id, "type": buy_type})
        ic = get_ic(ic_id)
        t = "штука" if buy_type == "dona" else "коробка"
        bot.edit_message_text(
            "✅ " + ic["name"] + " (" + t + ") добавлено!\n\n"
            + format_cart(user["cart"]) + "\n\nПродолжить или оформить?",
            uid, call.message.message_id, reply_markup=cart_kb(user["cart"]))

    elif data == "cart":
        bot.edit_message_text(format_cart(user["cart"]),
            uid, call.message.message_id, reply_markup=cart_kb(user["cart"]))

    elif data.startswith("del|"):
        idx = int(data.split("|")[1])
        if 0 <= idx < len(user["cart"]):
            removed = user["cart"].pop(idx)
            ic = get_ic(removed["id"])
            note = "❌ " + ic["name"] + " удалено.\n\n"
        else:
            note = ""
        bot.edit_message_text(note + format_cart(user["cart"]),
            uid, call.message.message_id, reply_markup=cart_kb(user["cart"]))

    elif data == "back":
        page = user.get("page", 0)
        bot.edit_message_text("🍦 Каталог — выберите вкус:",
            uid, call.message.message_id, reply_markup=catalog_kb(page))

    elif data == "checkout":
        if not user["cart"]:
            bot.answer_callback_query(call.id, "Корзина пуста!", show_alert=True)
            return
        user["step"] = "phone"
        bot.send_message(uid, "📱 Поделитесь номером телефона:", reply_markup=phone_kb())

    elif data.startswith("pay|"):
        pay_type = "Наличные" if data == "pay|cash" else "Рассрочка"
        finish_order(uid, call, pay_type)

    elif data == "noop":
        pass

    bot.answer_callback_query(call.id)

@bot.message_handler(content_types=["contact", "text"])
def on_message(msg):
    uid = msg.from_user.id
    user = get_user(uid)
    if user["step"] == "phone":
        if msg.content_type == "contact":
            user["phone"] = msg.contact.phone_number
        else:
            user["phone"] = msg.text.strip()
        user["step"] = "address"
        bot.send_message(uid, "📍 Введите адрес доставки:", reply_markup=ReplyKeyboardRemove())
    elif user["step"] == "address":
        user["address"] = msg.text.strip()
        user["step"] = "payment"
        bot.send_message(uid, "💰 Выберите способ оплаты:", reply_markup=payment_kb())

def finish_order(uid, call, payment):
    user = get_user(uid)
    cart = user["cart"]
    phone = user["phone"]
    addr = user["address"]
    total = sum(
        get_ic(i["id"])["dona"] if i["type"] == "dona" else get_ic(i["id"])["box"]
        for i in cart)
    now = datetime.now()
    order = {
        "date": now.strftime("%d.%m.%Y"),
        "time": now.strftime("%H:%M"),
        "phone": phone,
        "address": addr,
        "payment": payment,
        "cart": list(cart),
        "total": total,
        "username": call.from_user.full_name,
    }
    all_orders.append(order)
    bot.send_message(uid,
        "✅ Заказ оформлен!\n\n"
        + format_cart(cart) + "\n\n"
        "📱 Тел.: " + phone + "\n"
        "📍 Адрес: " + addr + "\n"
        "💰 Оплата: " + payment + "\n\n"
        "Спасибо! Скоро свяжемся 🍦")
    items_str = "\n".join(
        "  • " + get_ic(i["id"])["name"] + " (" + ("шт." if i["type"]=="dona" else "кор.") + ")"
        for i in cart)
    bot.send_message(ADMIN_ID,
        "🔔 Yangi buyurtma!\n\n"
        "👤 " + order["username"] + "\n"
        "📱 " + phone + "\n"
        "📍 " + addr + "\n"
        "💰 " + payment + " | 🕐 " + order["time"] + "\n\n"
        "🛒 Mahsulotlar:\n" + items_str + "\n\n"
        "💵 Jami: " + str(total) + " сом")
    user["cart"] = []
    user["step"] = "catalog"

print("✅ Бот запущен!")
bot.infinity_polling()
