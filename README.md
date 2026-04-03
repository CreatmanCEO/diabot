# DiaBot

[Русский](#русский) | [English](#english)

---

## Русский

Telegram-бот для подсчёта углеводов и КБЖУ по фото еды. Создан для людей с диабетом 1 типа.

**Как работает:** отправляешь фото еды → бот распознаёт продукты через AI → уточняет правильность → считает КБЖУ и хлебные единицы → ведёт дневник питания.

### Возможности

- Распознавание еды по фото (Gemini AI)
- Подсчёт КБЖУ и хлебных единиц (ХЕ)
- Текстовое описание еды
- Дневник питания с дневной/недельной статистикой
- Запись показаний глюкозы
- Мульти-провайдер AI с автоматическим fallback (litellm)
- Мультипользовательский режим (self-hosted)
- Поддержка русского и английского языков

### Стек

- Python 3.11+ (async)
- python-telegram-bot 21+
- litellm (Gemini → OpenRouter → Groq fallback)
- SQLite (aiosqlite)

### Установка

```bash
git clone https://github.com/CreatmanCEO/diabot.git
cd diabot
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cp .env.example .env
# Заполни .env своими токенами
python main.py
```

### Переменные окружения

| Переменная | Описание | Обязательно |
|-----------|----------|:-----------:|
| `TELEGRAM_TOKEN` | Токен бота от @BotFather | да |
| `ADMIN_IDS` | Telegram ID админов через запятую | да |
| `GEMINI_API_KEY` | API ключ Google AI Studio | * |
| `OPENROUTER_API_KEY` | API ключ OpenRouter | * |
| `GROQ_API_KEY` | API ключ Groq | * |
| `DEFAULT_TIMEZONE` | Часовой пояс по умолчанию | нет |
| `DEFAULT_HE_GRAMS` | Граммов углеводов в 1 ХЕ (12) | нет |
| `DEFAULT_LANGUAGE` | Язык по умолчанию (ru) | нет |
| `RATE_LIMIT_REQUESTS` | Лимит запросов в час (30) | нет |
| `DB_PATH` | Путь к SQLite базе | нет |

\* Нужен хотя бы один LLM API ключ. Для распознавания фото нужен GEMINI или OPENROUTER.

### Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Приветствие и онбординг |
| `/help` | Подробная справка |
| `/today` | Дневник за сегодня |
| `/week` | Статистика за неделю |
| `/history N` | Последние N записей |
| `/sugar` | Записать показание глюкозы |
| `/undo` | Удалить последнюю запись |
| `/cancel` | Отменить текущее действие |
| `/privacy` | Приватность и данные |
| `/export` | Экспорт данных в JSON |
| `/delete_my_data` | Удалить все данные |
| `/adduser` | Добавить пользователя (админ) |
| `/removeuser` | Удалить пользователя (админ) |
| `/listusers` | Список пользователей (админ) |

### Деплой (systemd)

```bash
sudo useradd -r -s /bin/false diabot
sudo mkdir -p /opt/diabot
sudo git clone https://github.com/CreatmanCEO/diabot.git /opt/diabot
cd /opt/diabot
sudo python3 -m venv venv
sudo venv/bin/pip install -r requirements.txt
sudo cp .env.example .env
sudo nano .env  # заполнить токены
sudo cp diabot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable diabot
sudo systemctl start diabot
```

---

## English

Telegram bot for counting carbohydrates and KBJU (calories, protein, fat, carbs) from food photos. Built for people with type 1 diabetes.

**How it works:** send a food photo → bot recognizes products via AI → asks for confirmation → calculates nutrition and bread units (XE) → keeps a food diary.

### Features

- Food recognition from photos (Gemini AI)
- KBJU calculation with bread units (XE/HE)
- Text-based food description
- Food diary with daily/weekly stats
- Glucose readings tracking
- Multi-provider AI with automatic fallback (litellm)
- Multi-user self-hosted mode
- Russian and English language support

### Tech Stack

- Python 3.11+ (async)
- python-telegram-bot 21+
- litellm (Gemini → OpenRouter → Groq fallback)
- SQLite (aiosqlite)

### Installation

```bash
git clone https://github.com/CreatmanCEO/diabot.git
cd diabot
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cp .env.example .env
# Fill in your tokens in .env
python main.py
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|:--------:|
| `TELEGRAM_TOKEN` | Bot token from @BotFather | yes |
| `ADMIN_IDS` | Comma-separated admin Telegram IDs | yes |
| `GEMINI_API_KEY` | Google AI Studio API key | * |
| `OPENROUTER_API_KEY` | OpenRouter API key | * |
| `GROQ_API_KEY` | Groq API key | * |
| `DEFAULT_TIMEZONE` | Default timezone | no |
| `DEFAULT_HE_GRAMS` | Grams of carbs per 1 XE (12) | no |
| `DEFAULT_LANGUAGE` | Default language (ru) | no |
| `RATE_LIMIT_REQUESTS` | Requests per hour limit (30) | no |
| `DB_PATH` | Path to SQLite database | no |

\* At least one LLM API key required. Photo recognition needs GEMINI or OPENROUTER.

### Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome and onboarding |
| `/help` | Detailed help |
| `/today` | Today's diary |
| `/week` | Weekly stats |
| `/history N` | Last N entries |
| `/sugar` | Log glucose reading |
| `/undo` | Delete last entry |
| `/cancel` | Cancel current action |
| `/privacy` | Privacy and data info |
| `/export` | Export data as JSON |
| `/delete_my_data` | Delete all your data |
| `/adduser` | Add user (admin) |
| `/removeuser` | Remove user (admin) |
| `/listusers` | List users (admin) |

### Deploy (systemd)

```bash
sudo useradd -r -s /bin/false diabot
sudo mkdir -p /opt/diabot
sudo git clone https://github.com/CreatmanCEO/diabot.git /opt/diabot
cd /opt/diabot
sudo python3 -m venv venv
sudo venv/bin/pip install -r requirements.txt
sudo cp .env.example .env
sudo nano .env  # fill in tokens
sudo cp diabot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable diabot
sudo systemctl start diabot
```

---

## License

MIT License. Copyright (c) 2026 Creatman.

---
<sub>*Made with care and attention to the inner world of a person.*</sub>
