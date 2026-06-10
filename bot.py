import os
import sys
import time
import datetime
import random
import telebot
from telebot import types
import nest_asyncio
import g4f

# Применяем асинхронный патч, чтобы g4f работал в Termux без зависаний
nest_asyncio.apply()

# --- НАСТРОЙКА ТОКЕНА ---
TOKEN = "8959837695:AAFidKkO90ASeRCgjyxYXU4dUrcFCVxICYc"
bot = telebot.TeleBot(TOKEN)

# Настройка таймаутов
telebot.apihelper.CONNECT_TIMEOUT = 5
telebot.apihelper.READ_TIMEOUT = 10

# Глобальные настройки
TODAY_ACTIVITY = 0
LAST_DATE = datetime.date.today()
AI_MODE = False  # По умолчанию ИИ выключен

# --- ANSI ЦВЕТА ---
BOLD = "\033[1m"
RESET = "\033[0m"
RED = "\033[38;5;196m"
GREEN = "\033[38;5;46m"
YELLOW = "\033[38;5;226m"
BLUE = "\033[38;5;27m"
PURPLE = "\033[38;5;129m"
CYAN = "\033[38;5;51m"
WHITE = "\033[38;5;15m"
GRAY = "\033[38;5;244m"
ORANGE = "\033[38;5;208m"
PINK = "\033[38;5;201m"

def clear_screen():
    os.system("clear")

def get_users_list():
    if not os.path.exists("users.txt"):
        return []
    with open("users.txt", "r", encoding="utf-8") as f:
        return [line for line in f.read().splitlines() if line.strip()]

def get_blacklist():
    if not os.path.exists("blacklist.txt"):
        return []
    with open("blacklist.txt", "r", encoding="utf-8") as f:
        return f.read().splitlines()

def get_welcome_text():
    if os.path.exists("welcome.txt"):
        with open("welcome.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    return "Привет! 👋 Ты успешно зарегистрирован в системе ULTRA BOT."

# --- НАДЕЖНАЯ ФУНКЦИЯ ДЛЯ ОТВЕТА ИИ ---
def ask_ai(user_message):
    try:
        # Используем стабильную дефолтную модель g4f
        response = g4f.ChatCompletion.create(
            model=g4f.models.default,
            messages=[
                {"role": "system", "content": "Ты крутой, дружелюбный ИИ-ассистент. Отвечай кратко, используй эмодзи."},
                {"role": "user", "content": user_message}
            ],
        )
        if response:
            return response
        return "Хмм, не смог подобрать слова. Напиши еще раз! 🤔"
    except Exception as e:
        return "Извини, мой ИИ-мозг сейчас обновляет базы данных. Скоро вернусь! 🧠⏳"

# --- ХЭНДЛЕР TELEGRAM ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    global TODAY_ACTIVITY, LAST_DATE, AI_MODE
    chat_id = str(message.chat.id)
    username = message.from_user.username or "no_nick"
    first_name = message.from_user.first_name or "User"
    text = message.text or "[Медиа/Стикер]"
    time_now = datetime.datetime.now().strftime("%H:%M:%S")

    if datetime.date.today() != LAST_DATE:
        TODAY_ACTIVITY = 0
        LAST_DATE = datetime.date.today()

    TODAY_ACTIVITY += 1

    # Чёрный список
    if chat_id in get_blacklist():
        print(f" {RED}[BANNED]{RESET} {GRAY}[{time_now}]{RESET} ID: {chat_id} | {CYAN}@{username}{RESET}: {WHITE}{text}{RESET}")
        return

    # База пользователей
    users = get_users_list()
    user_exists = any(line.startswith(chat_id + "|") for line in users)
    if not user_exists:
        with open("users.txt", "a", encoding="utf-8") as f:
            f.write(f"{chat_id}|{username}|{first_name}\n")

    # Режим ИИ-собеседника
    if AI_MODE and text != "/start" and not text.startswith("/"):
        print(f" {GRAY}➔{RESET} {PINK}[{time_now}]{RESET} {GREEN}ID: {chat_id[:4]}...{chat_id[-3:]}{RESET} | {CYAN}@{username:<12}{RESET} | {YELLOW}[Генерация ИИ...]{RESET}")
        
        ai_reply = ask_ai(text)
        try:
            bot.reply_to(message, ai_reply) # Бот отвечает прямо на сообщение пользователя
            print(f" {GREEN}[✓] ИИ успешно ответил юзеру @{username}{RESET}")
        except:
            pass
        return

    # Команда /start
    if text == "/start":
        try:
            welcome_txt = get_welcome_text().replace("{name}", first_name)
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("🌐 Наш Канал", url="https://t.me/telegram")
            btn2 = types.InlineKeyboardButton("🛠️ Поддержка", url="https://t.me/telegram")
            markup.add(btn1, btn2)
            bot.send_message(int(chat_id), welcome_txt, reply_markup=markup)
        except:
            pass

    # Обычный лог
    print(f" {GRAY}➔{RESET} {PINK}[{time_now}]{RESET} {GREEN}ID: {chat_id[:4]}...{chat_id[-3:]}{RESET} | {CYAN}@{username:<12}{RESET} | {WHITE}{text}{RESET}")

# --- ГЛАВНЫЙ ЦИКЛ МЕНЮ ---
while True:
    clear_screen()
    all_users = get_users_list()
    banned_count = len(get_blacklist())
    ai_status = f"{GREEN}АКТИВЕН (GPT){RESET}" if AI_MODE else f"{RED}ВЫКЛЮЧЕН (Обычный){RESET}"
    
    print(f"{BOLD}{PURPLE}╔═════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{PURPLE}║{RESET}         {BOLD}{PINK}⚡ ULTRA BOT SYSTEM v8.0 PRO AI KING ⚡{RESET}        {BOLD}{PURPLE}║{RESET}")
    print(f"{BOLD}{PURPLE}╠═════════════════════════════════════════════════════════╣{RESET}")
    print(f"{BOLD}{PURPLE}║{RESET} {BOLD}{WHITE}СЕТЬ: OK{RESET} │ {ORANGE}БАЗА: {len(all_users):<3}{RESET} │ {RED}ЧС: {banned_count:<2}{RESET} │ {CYAN}АВТООТВЕТЧИК ИИ: {ai_status:<10}{RESET} {BOLD}{PURPLE}║{RESET}")
    print(f"{BOLD}{PURPLE}╠═════════════════════════════════════════════════════════╣{RESET}")
    print(f"{BOLD}{PURPLE}║{RESET}  {BOLD}{GREEN}[1]{RESET} {WHITE}📡 Включить живой мониторинг эфира            {RESET}{BOLD}{PURPLE}║{RESET}")
    print(f"{BOLD}{PURPLE}║{RESET}  {BOLD}{GREEN}[2]{RESET} {WHITE}💬 Отправить прямое сообщение по ID           {RESET}{BOLD}{PURPLE}║{RESET}")
    print(f"{BOLD}{PURPLE}║{RESET}  {BOLD}{GREEN}[3]{RESET} {WHITE}📢 Запустить глобальную рассылку (минуя ЧС)   {RESET}{BOLD}{PURPLE}║{RESET}")
    print(f"{BOLD}{PURPLE}║{RESET}  {BOLD}{GREEN}[4]{RESET} {WHITE}📊 Посмотреть расширенную статистику          {RESET}{BOLD}{PURPLE}║{RESET}")
    print(f"{BOLD}{PURPLE}║{RESET}  {BOLD}{GREEN}[5]{RESET} {WHITE}⛔ Управление Чёрным Списком (БАН)            {RESET}{BOLD}{PURPLE}║{RESET}")
    print(f"{BOLD}{PURPLE}║{RESET}  {BOLD}{YELLOW}[6]{RESET} {YELLOW}📝 Настройка текста автоответчика (/start)    {RESET}{BOLD}{PURPLE}║{RESET}")
    print(f"{BOLD}{PURPLE}║{RESET}  {BOLD}{YELLOW}[7]{RESET} {YELLOW}🎁 Генератор промокодов для конкурсов         {RESET}{BOLD}{PURPLE}║{RESET}")
    print(f"{BOLD}{PURPLE}║{RESET}  {BOLD}{GRAY}[8]{RESET} {GRAY}🧹 Провести оптимизацию и очистку базы файлов {RESET}{BOLD}{PURPLE}║{RESET}")
    print(f"{BOLD}{PURPLE}║{RESET}  {BOLD}{PINK}[9]{RESET} {PINK}🤖 Переключить режим ИИ-собеседника (ВКЛ/ВЫКЛ) {RESET}{BOLD}{PURPLE}║{RESET}")
    print(f"{BOLD}{PURPLE}║{RESET}  {BOLD}{RED}[10]{RESET}{RED}🛑 Полное отключение ядра и выход             {RESET}{BOLD}{PURPLE}║{RESET}")
    print(f"{BOLD}{PURPLE}╚═════════════════════════════════════════════════════════╝{RESET}")

    c = input(f" {BOLD}{CYAN}root@ultrabot:~#{RESET} ").strip()

    if c == "1":
        clear_screen()
        print(f"{BOLD}{GREEN} 📡 МОНИТОРИНГ СЕТИ ЗАПУЩЕН...{RESET}")
        print(f"{GRAY} ┌──────────────────────────────────────────────────────┐{RESET}")
        print(f"{GRAY} │{RESET} {WHITE}ИИ-Режим сейчас:{RESET} {ai_status}                             {GRAY}│{RESET}")
        print(f"{GRAY} │{RESET} {YELLOW}Для безопасного выхода в меню: нажмите {BOLD}Ctrl + C{RESET}       {GRAY}│{RESET}")
        print(f"{GRAY} └──────────────────────────────────────────────────────┘{RESET}\n")
        try:
            bot.polling(non_stop=True, timeout=10, long_polling_timeout=5)
        except KeyboardInterrupt:
            bot.stop_polling()
            print(f"\n\n {ORANGE}[~] Соединение закрыто.{RESET}")
            time.sleep(1)
        except Exception as e:
            print(f"\n {RED}[X] Ошибка: {e}{RESET}"); time.sleep(2)

    elif c == "2":
        clear_screen()
        print(f"{BOLD}{CYAN} 💬 ОТПРАВКА СООБЩЕНИЯ{RESET}\n")
        tid = input(" ID получателя ➔ ").strip()
        txt = input(" Текст сообщения ➔ ").strip()
        if tid in get_blacklist():
            print(f" {RED}Пользователь в ЧС!{RESET}")
        elif tid.isdigit() and txt:
            try:
                bot.send_message(int(tid), txt)
                print(f" {GREEN}[✓] Доставлено!{RESET}")
            except Exception as e: print(f" Ошибка: {e}")
        input("\n Нажмите Enter...")

    elif c == "3":
        clear_screen()
        print(f"{BOLD}{ORANGE} 📢 ГЛОБАЛЬНАЯ РАССЫЛКА{RESET}\n")
        txt = input(" Введите текст рассылки ➔ ").strip()
        if txt:
            banned_users = get_blacklist()
            success, skipped = 0, 0
            for line in all_users:
                if not line: continue
                tid = line.split("|")[0]
                if tid in banned_users:
                    skipped += 1; continue
                try:
                    bot.send_message(int(tid), txt)
                    success += 1; time.sleep(0.1)
                except: pass
            print(f"\n {GREEN}Успешно отправлено: {success}, В ЧС пропущено: {skipped}{RESET}")
        input("\n Нажмите Enter...")

    elif c == "4":
        clear_screen()
        print(f"{BOLD}{BLUE} 📊 РАСШИРЕННАЯ СТАТИСТИКА{RESET}\n")
        with_nick, no_nick = 0, 0
        for line in all_users:
            if not line: continue
            parts = line.split("|")
            if len(parts) > 1 and parts[1] not in ["No_Username", "no_nick"]: with_nick += 1
            else: no_nick += 1
        print(f" Всего в базе: {GREEN}{len(all_users)}{RESET}")
        print(f" С юзернеймом (@): {CYAN}{with_nick}{RESET} | Без: {GRAY}{no_nick}{RESET}")
        print(f" Сообщений за сессию: {YELLOW}{TODAY_ACTIVITY}{RESET}\n")
        print(f" {BOLD}Последние активные юзеры:{RESET}")
        for u in reversed(all_users[-5:]):
            if not u: continue
            p = u.split("|")
            print(f"  • ID: {p[0]} | {CYAN}@{p[1]}{RESET}")
        input("\n Нажмите Enter...")

    elif c == "5":
        clear_screen()
        print(f"{BOLD}{RED} ⛔ УПРАВЛЕНИЕ ЧЁРНЫМ СПИСКОМ{RESET}\n")
        print(" 1. Забанить по ID   2. Разбанить по ID   3. Показать весь ЧС\n")
        choice = input(" Выберите подкоманду ➔ ").strip()
        if choice == "1":
            ban_id = input(" Введите ID ➔ ").strip()
            if ban_id.isdigit() and ban_id not in get_blacklist():
                with open("blacklist.txt", "a") as f: f.write(f"{ban_id}\n")
                print(" [✓] Забанен!")
        elif choice == "2":
            unban_id = input(" Введите ID ➔ ").strip()
            banned = get_blacklist()
            if unban_id in banned:
                banned.remove(unban_id)
                with open("blacklist.txt", "w") as f:
                    for b in banned: f.write(f"{b}\n")
                print(" [✓] Разбанен!")
        elif choice == "3":
            print("\n В Чёрном Списке:")
            for b in get_blacklist(): print(f"  ➔ ID: {b}")
        input("\n Нажмите Enter...")

    elif c == "6":
        clear_screen()
        print(f"{BOLD}{YELLOW} 📝 НАСТРОЙКА АВТООТВЕТЧИКА{RESET}\n")
        print(f" Текущий текст:\n {CYAN}{get_welcome_text()}{RESET}\n")
        new_welcome = input(" Введите новый текст приветствия ➔ ").strip()
        if new_welcome:
            with open("welcome.txt", "w", encoding="utf-8") as f: f.write(new_welcome)
            print(" [✓] Сохранено!")
        input("\n Нажмите Enter...")

    elif c == "7":
        clear_screen()
        print(f"{BOLD}{ORANGE} 🎁 ГЕНЕРАТОР ПРОМОКОДОВ{RESET}\n")
        promo = "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890") for _ in range(8))
        print(f" Сгенерирован код: {BOLD}{GREEN}{promo}{RESET}")
        input("\n Нажмите Enter...")

    elif c == "8":
        clear_screen()
        print(f"{BOLD}{GRAY} 🧹 ОПТИМИЗАЦИЯ ФАЙЛОВБАЗЫ{RESET}\n")
        if os.path.exists("users.txt"):
            filtered = get_users_list()
            with open("users.txt", "w", encoding="utf-8") as f:
                for line in filtered: f.write(f"{line}\n")
            print(" [✓] База данных успешно оптимизирована!")
        input("\n Нажмите Enter...")

    elif c == "9":
        AI_MODE = not AI_MODE
        print(f"\n {YELLOW}[~] Режим ИИ переключен!{RESET}")
        time.sleep(1)

    elif c == "10":
        clear_screen()
        print(f" {RED}🚨 Сессия закрыта.{RESET}\n")
        sys.exit()

