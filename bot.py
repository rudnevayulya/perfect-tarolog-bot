import logging
import os
import random
from dataclasses import dataclass, field

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

# Starter deck: all 78 cards. Meanings are concise reflection prompts,
# not predictions or substitutes for verified information.
MAJOR = [
    ("Шут", "новый опыт, открытость, шаг в неизвестность"),
    ("Маг", "инициатива, навыки, способность действовать"),
    ("Верховная Жрица", "интуиция, наблюдение, скрытая информация"),
    ("Императрица", "забота, рост, творчество, изобилие"),
    ("Император", "структура, ответственность, границы"),
    ("Иерофант", "традиции, обучение, ценности"),
    ("Влюблённые", "выбор, близость, согласие с ценностями"),
    ("Колесница", "цель, дисциплина, движение"),
    ("Сила", "мягкая смелость, терпение, самообладание"),
    ("Отшельник", "уединение, поиск смысла, внутренняя опора"),
    ("Колесо Фортуны", "перемены, циклы, гибкость"),
    ("Справедливость", "честность, последствия, взвешенное решение"),
    ("Повешенный", "пауза, новый взгляд, отпускание контроля"),
    ("Смерть", "завершение этапа, трансформация, обновление"),
    ("Умеренность", "баланс, восстановление, постепенность"),
    ("Дьявол", "привязанности, искушения, возвращение выбора"),
    ("Башня", "слом старой конструкции, неожиданные перемены"),
    ("Звезда", "надежда, вдохновение, бережное восстановление"),
    ("Луна", "неопределённость, тревога, необходимость проверки фактов"),
    ("Солнце", "ясность, жизненная энергия, открытость"),
    ("Суд", "переоценка, пробуждение, важный вывод"),
    ("Мир", "завершение, целостность, интеграция опыта"),
]

SUITS = {
    "Жезлы": [
        "Туз Жезлов", "Двойка Жезлов", "Тройка Жезлов", "Четвёрка Жезлов",
        "Пятёрка Жезлов", "Шестёрка Жезлов", "Семёрка Жезлов", "Восьмёрка Жезлов",
        "Девятка Жезлов", "Десятка Жезлов", "Паж Жезлов", "Рыцарь Жезлов",
        "Королева Жезлов", "Король Жезлов",
    ],
    "Кубки": [
        "Туз Кубков", "Двойка Кубков", "Тройка Кубков", "Четвёрка Кубков",
        "Пятёрка Кубков", "Шестёрка Кубков", "Семёрка Кубков", "Восьмёрка Кубков",
        "Девятка Кубков", "Десятка Кубков", "Паж Кубков", "Рыцарь Кубков",
        "Королева Кубков", "Король Кубков",
    ],
    "Мечи": [
        "Туз Мечей", "Двойка Мечей", "Тройка Мечей", "Четвёрка Мечей",
        "Пятёрка Мечей", "Шестёрка Мечей", "Семёрка Мечей", "Восьмёрка Мечей",
        "Девятка Мечей", "Десятка Мечей", "Паж Мечей", "Рыцарь Мечей",
        "Королева Мечей", "Король Мечей",
    ],
    "Пентакли": [
        "Туз Пентаклей", "Двойка Пентаклей", "Тройка Пентаклей", "Четвёрка Пентаклей",
        "Пятёрка Пентаклей", "Шестёрка Пентаклей", "Семёрка Пентаклей", "Восьмёрка Пентаклей",
        "Девятка Пентаклей", "Десятка Пентаклей", "Паж Пентаклей", "Рыцарь Пентаклей",
        "Королева Пентаклей", "Король Пентаклей",
    ],
}

SUIT_MEANINGS = {
    "Жезлы": "энергия, инициатива, творчество и действие",
    "Кубки": "чувства, отношения, эмпатия и эмоциональные потребности",
    "Мечи": "мысли, решения, коммуникация и ясность",
    "Пентакли": "практические дела, ресурсы, устойчивость и работа",
}

DECK = [(name, meaning, False) for name, meaning in MAJOR]
for suit, names in SUITS.items():
    for name in names:
        DECK.append((name, SUIT_MEANINGS[suit], True))
assert len(DECK) == 78

SPREADS = {
    "one": ("Карта дня", ["Главная тема дня"]),
    "three": ("Три карты", ["Что влияет", "На что обратить внимание", "Полезное направление"]),
    "horseshoe": (
        "Подкова — 7 карт",
        [
            "Текущая ситуация", "Влияние прошлого", "Скрытый фактор",
            "Главное препятствие", "Внешние обстоятельства",
            "Рекомендуемый подход", "Возможное направление развития",
        ],
    ),
}

@dataclass
class Session:
    spread_key: str
    question: str
    cards: list = field(default_factory=list)
    picked: list = field(default_factory=list)

sessions: dict[int, Session] = {}

def card_meaning(card_name: str, base: str, is_minor: bool, reversed_: bool) -> str:
    if is_minor:
        return base + ("; перевёрнутое положение предлагает пересмотреть привычный способ действовать в этой сфере." if reversed_ else ".")
    return base + ("; перевёрнутое положение приглашает обратить внимание на внутренние или невыраженные стороны этой темы." if reversed_ else ".")

def menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌙 Карта дня", callback_data="spread:one")],
        [InlineKeyboardButton("🔮 Расклад на 3 карты", callback_data="spread:three")],
        [InlineKeyboardButton("✨ Подкова — 7 карт", callback_data="spread:horseshoe")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sessions.pop(update.effective_user.id, None)
    await update.message.reply_text(
        "Добро пожаловать в Perfect Tarolog 🔮\n\n"
        "Здесь вы можете сделать символический расклад Таро, самостоятельно открыть карты "
        "и получить вдумчивые подсказки для саморефлексии.\n\n"
        "Выберите формат расклада:",
        reply_markup=menu_keyboard(),
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sessions.pop(update.effective_user.id, None)
    await update.message.reply_text("Текущий расклад отменён. Начнём заново?", reply_markup=menu_keyboard())

async def choose_spread(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split(":", 1)[1]
    if key not in SPREADS:
        return
    sessions[query.from_user.id] = Session(spread_key=key, question="")
    title, labels = SPREADS[key]
    await query.edit_message_text(
        f"Вы выбрали: {title}.\n\n"
        "Сформулируйте вопрос одним сообщением. Можно оставить его общим — например, "
        "«На что мне сейчас важно обратить внимание?»\n\n"
        "После этого вы самостоятельно выберете карты."
    )

async def receive_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = sessions.get(user_id)
    if not session or session.cards:
        await update.message.reply_text("Чтобы начать расклад, выберите формат:", reply_markup=menu_keyboard())
        return
    session.question = update.message.text.strip()[:1000]
    _, labels = SPREADS[session.spread_key]
    session.cards = random.sample(DECK, len(labels))
    session.picked = []
    await update.message.reply_text(
        "Вопрос принят.\n\n"
        "Сосредоточьтесь на нём и выберите закрытые карты по одной. "
        "Порядок позиций соответствует выбранному раскладу.",
        reply_markup=card_picker(session),
    )

def card_picker(session: Session):
    _, labels = SPREADS[session.spread_key]
    buttons = []
    for i, label in enumerate(labels):
        if i in session.picked:
            continue
        buttons.append(InlineKeyboardButton(f"🂠 {i + 1}. {label}", callback_data=f"pick:{i}"))
    return InlineKeyboardMarkup([buttons[i:i+1] for i in range(len(buttons))])

async def pick_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    session = sessions.get(user_id)
    if not session:
        await query.answer("Начните новый расклад через /start.", show_alert=True)
        return
    try:
        position = int(query.data.split(":", 1)[1])
    except (ValueError, IndexError):
        await query.answer()
        return
    _, labels = SPREADS[session.spread_key]
    if position < 0 or position >= len(labels) or position in session.picked:
        await query.answer("Эта карта уже открыта.", show_alert=True)
        return
    session.picked.append(position)
    name, base, is_minor = session.cards[position]
    reversed_ = random.choice([False, True])
    orientation = "перевёрнутое положение" if reversed_ else "прямое положение"
    meaning = card_meaning(name, base, is_minor, reversed_)
    await query.answer("Карта открыта")
    await query.message.reply_text(
        f"**Позиция {position + 1}: {labels[position]}**\n"
        f"🃏 *{name}* — {orientation}.\n\n{meaning}",
        parse_mode="Markdown",
    )
    if len(session.picked) == len(labels):
        await query.message.reply_text(
            "Расклад завершён. ✨\n\n"
            f"Ваш вопрос: «{session.question}»\n\n"
            "Общая тема: карты предлагают рассмотреть ситуацию с разных сторон, "
            "отделить факты от предположений и выбрать следующий небольшой, реалистичный шаг.\n\n"
            "Это символическая практика для размышления, а не достоверное предсказание. "
            "Карты не могут установить факты о здоровье, безопасности, местонахождении или будущем другого человека.",
            reply_markup=menu_keyboard(),
        )
        sessions.pop(user_id, None)
    else:
        await query.message.reply_text(
            f"Открыто {len(session.picked)} из {len(labels)} карт. Выберите следующую:",
            reply_markup=card_picker(session),
        )

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Не задан секрет TELEGRAM_BOT_TOKEN. Добавьте его в переменные окружения хостинга.")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(choose_spread, pattern=r"^spread:"))
    app.add_handler(CallbackQueryHandler(pick_card, pattern=r"^pick:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_question))
    log.info("PerfectTarologBot is starting")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
