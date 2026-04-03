"""Russian locale — bot messages and LLM prompts."""

LANG = "ru"
LANG_NAME = "Русский"

# --- Onboarding ---
START_WELCOME = (
    "👋 Привет, {name}!\n\n"
    "Я <b>DiaBot</b> — твой персональный помощник по питанию.\n\n"
    "Что я умею:\n"
    "📸 Распознаю еду по фото и считаю калории, белки, жиры, углеводы\n"
    "🔢 Считаю хлебные единицы для контроля диабета\n"
    "📊 Веду дневник питания с суточными нормами\n"
    "💉 Записываю показания сахара\n\n"
    "Чтобы всё работало точнее, давай быстро настроимся — "
    "это займёт меньше минуты!\n\n"
    "<i>Продолжая, ты соглашаешься с отправкой фото еды в AI-сервис "
    "для распознавания. Подробнее: /privacy</i>"
)
CONSENT_AGREE = "👌 Давай настроимся!"
CONSENT_DETAILS = "📄 Подробнее"
CONSENT_DETAILS_TEXT = (
    "🔒 <b>Что я делаю с данными:</b>\n"
    "• Фото отправляются в AI для распознавания\n"
    "• Результаты хранятся на сервере бота\n"
    "• Данные не передаются третьим лицам\n"
    "• Ты можешь экспортировать или удалить свои данные\n\n"
    "Подробнее: /privacy"
)
ONBOARDING_TIMEZONE = "🌍 Какой у тебя часовой пояс?"
TZ_MOSCOW = "🇷🇺 Москва"
TZ_EUROPE = "🇪🇺 Европа"
TZ_OTHER = "Другой"
ONBOARDING_HE = (
    "⚙️ Сколько граммов углеводов в 1 ХЕ?\n"
    "(стандарт РФ — 12 г, в некоторых странах 10 г)"
)
HE_12 = "12 г (РФ)"
HE_10 = "10 г"
HE_OTHER = "Другое"
ONBOARDING_COMPLETE = (
    "🎉 {name}, всё готово!\n\n"
    "Вот что можешь сделать прямо сейчас:\n"
    "📸 Отправь фото еды — я распознаю и посчитаю КБЖУ\n"
    "✏️ Или просто напиши что ела\n\n"
    "Кнопки внизу помогут с дневником и другими функциями.\n"
    "Настройки всегда доступны через ⚙️ Меню."
)
ONBOARDING_HE_CUSTOM = "Введи количество граммов углеводов в 1 ХЕ (число):"
ONBOARDING_TZ_CUSTOM = "Введи часовой пояс (например Europe/Berlin):"

# --- Main menu buttons ---
BTN_TODAY = "📊 Сегодня"
BTN_WEEK = "📅 Неделя"
BTN_SUGAR = "💉 Сахар"
BTN_MENU = "⚙️ Меню"
BTN_HISTORY = "📋 История"
BTN_UNDO = "↩️ Отменить"
BTN_PRIVACY = "🔒 Приватность"
BTN_HELP = "❓ Помощь"
BTN_BACK = "◀️ Назад"

# --- Inline buttons ---
BTN_CONFIRM = "✅ Верно"
BTN_CANCEL = "❌ Отмена"

# --- Recognition ---
ANALYZING = "⏳ Секундочку, {name}, смотрю что тут у нас..."
RECOGNITION_HEADER = "🔍 {name}, я вижу:"
RECOGNITION_HEADER_TEXT = "🔍 {name}, предполагаю:"
RECOGNITION_CONFIRM = "Всё верно? Нажми ✅ или напиши что исправить."
RECOGNITION_UPDATED = "🔍 Обновлённый список:"
RECOGNITION_NO_FOOD = "🤔 {name}, не вижу еды на фото. Отправь фото тарелки или опиши что ела."
RECOGNITION_FAILED = "⚠️ Не удалось распознать, попробуй другое фото или опиши текстом."

# --- Calculation ---
CALCULATION_HEADER = "🍽 Расчёт КБЖУ:"
CALCULATION_SAVED = "📝 Записано, {name}!"
CALCULATION_TODAY_SUMMARY = "За сегодня: {calories} ккал | {he} ХЕ"

# --- Diary ---
DIARY_HEADER = "📊 Дневник за {date}:"
DIARY_EMPTY = "📭 За {date} записей нет."
DIARY_TOTAL = "ИТОГО за день:"
WEEK_HEADER = "📅 Статистика за неделю:"
WEEK_EMPTY = "📭 За последнюю неделю записей нет."
HISTORY_HEADER = "📋 Последние {n} записей:"
HISTORY_EMPTY = "📭 Записей пока нет."
UNDO_SUCCESS = "↩️ Готово, последняя запись удалена."
UNDO_NOTHING = "📭 {name}, нечего отменять."

# --- Glucose ---
GLUCOSE_PROMPT = "💉 {name}, введи показание сахара (ммоль/л):"
GLUCOSE_SAVED = "💉 Записано: {value} ммоль/л 👍"
GLUCOSE_INVALID = "⚠️ Введи число, например: 5.8"

# --- Privacy ---
PRIVACY_TEXT = (
    "🔒 <b>Приватность</b>\n\n"
    "• Фото еды отправляются в AI-сервис для распознавания\n"
    "• Результаты хранятся на сервере бота\n"
    "• Фото НЕ сохраняются на диск\n"
    "• Данные не передаются третьим лицам\n\n"
    "<b>Команды:</b>\n"
    "/export — скачать все свои данные\n"
    "/delete_my_data — удалить все данные"
)
EXPORT_EMPTY = "📭 Нет данных для экспорта."
DELETE_CONFIRM = "⚠️ Ты уверен? Это удалит ВСЕ твои данные безвозвратно."
DELETE_YES = "Да, удалить"
DELETE_NO = "Нет, отмена"
DELETE_DONE = "✅ Все данные удалены."

# --- Admin ---
ADMIN_USER_ADDED = "✅ Пользователь {user_id} добавлен."
ADMIN_USER_REMOVED = "✅ Пользователь {user_id} удалён."
ADMIN_USER_LIST = "👥 Разрешённые пользователи:\n{users}"
ADMIN_USER_LIST_EMPTY = "📭 Список пуст (только админы)."
ADMIN_ONLY = "🔒 Команда только для администраторов."
ADMIN_BTN_ADD_USER = "➕ Добавить"
ADMIN_BTN_LIST_USERS = "👥 Пользователи"
ADMIN_ADD_PROMPT = "Введи Telegram ID пользователя для добавления:"
ADMIN_REMOVE_PROMPT = "Введи Telegram ID пользователя для удаления:"

# --- Access requests ---
ACCESS_REQUEST_WELCOME = (
    "👋 Привет, {name}! Я <b>DiaBot</b> — помощник для подсчёта "
    "углеводов и КБЖУ по фото еды.\n\n"
    "Этот бот персональный. Для доступа нужно одобрение администратора."
)
ACCESS_REQUEST_BTN = "📨 Запросить доступ"
ACCESS_REQUEST_SENT = "📨 Заявка отправлена! Администратор рассмотрит её в ближайшее время."
ACCESS_REQUEST_PENDING = "⏳ Твоя заявка уже отправлена. Ожидай ответа администратора."
ACCESS_REQUEST_APPROVED = "🎉 {name}, твоя заявка одобрена! Напиши /start чтобы начать."
ACCESS_REQUEST_REJECTED = "😔 К сожалению, твоя заявка отклонена."
ADMIN_NEW_REQUEST = (
    "📨 <b>Новая заявка на доступ</b>\n\n"
    "👤 Имя: {first_name}\n"
    "📝 Username: @{username}\n"
    "🆔 ID: <code>{user_id}</code>"
)
ADMIN_APPROVE = "✅ Одобрить"
ADMIN_REJECT = "❌ Отклонить"
ADMIN_REQUEST_APPROVED = "✅ Заявка пользователя {first_name} (ID: {user_id}) одобрена."
ADMIN_REQUEST_REJECTED = "❌ Заявка пользователя {first_name} (ID: {user_id}) отклонена."
ADMIN_REQUEST_ALREADY_HANDLED = "⚠️ Эта заявка уже рассмотрена."
ADMIN_BTN_PENDING = "📨 Заявки ({count})"
ADMIN_PENDING_HEADER = "📨 <b>Нерассмотренные заявки:</b>\n"
ADMIN_PENDING_EMPTY = "📭 Нет нерассмотренных заявок."
ADMIN_USERS_HEADER = "👥 <b>Пользователи с доступом:</b>\n"

# --- Errors ---
SERVICE_UNAVAILABLE = "⚠️ Сервис временно недоступен, попробуй через минуту."
RATE_LIMITED = "⏳ Слишком много запросов. Попробуй через {minutes} мин."
ACCESS_DENIED = "🔒 Этот бот персональный. Попроси админа добавить тебя."
UNSUPPORTED_MESSAGE = "📸 Отправь фото еды или напиши что ела."
CANCELLED = "❌ Отменено. Если что — я рядом."

# --- Help ---
HELP_TEXT = (
    "❓ <b>{name}, вот что я умею:</b>\n\n"
    "<b>Основное:</b>\n"
    "📸 Отправь фото еды — я распознаю и посчитаю КБЖУ\n"
    "✏️ Напиши текстом: «борщ с хлебом и компот»\n"
    "📸+✏️ Фото с подписью тоже работает\n\n"
    "<b>Команды:</b>\n"
    "/today — дневник за сегодня\n"
    "/week — статистика за неделю\n"
    "/history — последние записи\n"
    "/sugar — записать сахар\n"
    "/undo — удалить последнюю запись\n"
    "/privacy — приватность и данные\n"
    "/help — эта справка"
)

# --- LLM Prompts ---
RECOGNITION_PROMPT = """You are a nutritionist assistant for a person with type 1 diabetes.
Your task is to accurately recognize food in the photo (or from text description) and estimate portion sizes.

RULES:
1. List EACH visible product/dish on a separate line
2. Estimate weight in grams or volume in ml
3. If a dish is composite (e.g., soup, salad) — break it down into main components relevant for carbohydrates
4. If hard to determine precisely — indicate the most likely option
5. Do NOT calculate calories at this step, only recognition and weight
6. If the photo shows no food — report this politely
7. If the product is branded/packaged — specify exact product name and brand
8. If user provided a caption with the photo, use it as additional context for recognition

RESPONSE FORMAT (strictly JSON):
{
  "items": [
    {"name": "product name", "weight_g": 200, "note": ""},
    {"name": "product name", "weight_g": 150, "note": "additional detail"}
  ],
  "is_food": true,
  "confidence": "high"
}

confidence: "high" / "medium" / "low"
note: additional details if needed (cooking method, sauce, etc.)
If is_food = false, items must be empty.

IMPORTANT: All text values (name, note) MUST be in Русский language."""

CALCULATION_PROMPT = """You are a nutritionist calculator for a person with type 1 diabetes.
Calculate precise KBJU values for the given list of products.

RULES:
1. Use standard calorie tables (USDA, Russian FIC nutrition databases)
2. Account for cooking method (boiled, fried, raw)
3. For carbohydrates: specify TOTAL carbs and FIBER separately
4. Calculate bread units (XE/HE) using formula: (carbs_g - fiber_g) / {he_grams}
5. Estimate glycemic index (GI) of each product: low (<55), medium (55-70), high (>70)
6. Estimate overall GI of the meal
7. Be maximally accurate — insulin dosing depends on these numbers
8. If the product is branded/packaged — use exact KBJU values from packaging data in your knowledge

RESPONSE FORMAT (strictly JSON):
{
  "items": [
    {
      "name": "product name",
      "weight_g": 200,
      "calories": 264,
      "protein": 9.5,
      "fat": 2.3,
      "carbs": 54.0,
      "fiber": 3.7,
      "gi": "medium",
      "source": ""
    }
  ],
  "totals": {
    "calories": 0,
    "protein": 0.0,
    "fat": 0.0,
    "carbs": 0.0,
    "fiber": 0.0,
    "net_carbs": 0.0,
    "he": 0.0,
    "gi_overall": "medium"
  }
}

net_carbs = carbs - fiber
he = net_carbs / {he_grams}
Round all values to 1 decimal place.
source: "manufacturer data" if branded, empty string otherwise.

IMPORTANT: All text values (name) MUST be in Русский language."""

CORRECTION_PROMPT = """You are a nutritionist assistant for a person with type 1 diabetes.
The user previously received a food recognition result and wants to make corrections.

Previous recognition result:
{previous_items}

User's correction: {correction_text}

Apply the user's correction to the list. Add, remove, or modify items as requested.
Keep unchanged items as they are. Re-estimate weights if the correction implies a change.

RESPONSE FORMAT (strictly JSON):
{
  "items": [
    {"name": "product name", "weight_g": 200, "note": ""}
  ],
  "is_food": true,
  "confidence": "high"
}

IMPORTANT: All text values (name, note) MUST be in Русский language."""

# --- Onboarding profile ---
ONBOARDING_GENDER = "👤 {name}, какой у тебя пол?"
GENDER_FEMALE = "👩 Женский"
GENDER_MALE = "👨 Мужской"
ONBOARDING_HEIGHT = "📏 Какой у тебя рост (см)?"
HEIGHT_155 = "155"
HEIGHT_160 = "160"
HEIGHT_165 = "165"
HEIGHT_170 = "170"
HEIGHT_175 = "175"
HEIGHT_OTHER = "Другой"
ONBOARDING_WEIGHT = "⚖️ {name}, введи свой вес в кг:"
ONBOARDING_AGE = "🎂 Сколько тебе лет?"
ONBOARDING_TARGETS_SHOW = (
    "📊 {name}, на основе твоих данных, твои суточные нормы:\n\n"
    "  Калории: {calories} ккал\n"
    "  Белок: {protein} г\n"
    "  Жиры: {fat} г\n"
    "  Углеводы: {carbs} г ({he} ХЕ)\n\n"
    "Всё верно?"
)
TARGETS_CONFIRM = "✅ Подтвердить"
TARGETS_EDIT = "✏️ Изменить"
ONBOARDING_TARGETS_EDIT = (
    "Введи свои нормы в формате:\n"
    "<code>калории белок жиры углеводы</code>\n"
    "Например: <code>1800 65 60 225</code>"
)
ONBOARDING_TARGETS_INVALID = "⚠️ Введи 4 числа через пробел: калории белок жиры углеводы"
ONBOARDING_HEIGHT_CUSTOM = "Введи свой рост в см (число):"
ONBOARDING_WEIGHT_INVALID = "⚠️ Введи вес числом, например: 58 или 58.5"
ONBOARDING_AGE_INVALID = "⚠️ Введи возраст числом, например: 27"

# --- Settings ---
BTN_SETTINGS = "⚙️ Настройки"
SETTINGS_HEADER = (
    "⚙️ <b>Настройки</b>\n\n"
    "Часовой пояс: {timezone}\n"
    "ХЕ: {he_grams} г\n"
    "Пол: {gender} | Рост: {height} | Вес: {weight} | Возраст: {age}\n\n"
    "<b>Суточные нормы:</b>\n"
    "  Калории: {calories} ккал\n"
    "  Белок: {protein} г\n"
    "  Жиры: {fat} г\n"
    "  Углеводы: {carbs} г"
)
SETTINGS_EDIT_TARGETS = "✏️ Изменить нормы"
SETTINGS_EDIT_PROFILE = "📏 Изменить данные"
SETTINGS_SAVED = "✅ Настройки сохранены!"
GENDER_DISPLAY_MALE = "Муж"
GENDER_DISPLAY_FEMALE = "Жен"
GENDER_DISPLAY_NONE = "—"

# --- Migration prompt ---
TARGETS_SETUP_PROMPT = (
    "{name}, я добавил отслеживание суточных норм!\n"
    "Хочешь настроить? Это займёт минуту."
)
TARGETS_SETUP_NOW = "📏 Настроить"
TARGETS_SETUP_LATER = "⏭ Потом"

# --- Progress labels ---
PROGRESS_LABELS_COMPACT = {"carbs": "У", "cal": "К", "protein": "Б", "fat": "Ж", "xe": "ХЕ", "g": "г"}
PROGRESS_LABELS_FULL = {"carbs": "Углеводы", "xe": "ХЕ", "cal": "Калории", "protein": "Белок", "fat": "Жиры", "g": "г"}
