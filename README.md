# DiaBot

Персональный Telegram-бот для подсчёта углеводов и КБЖУ по фото еды. Создан для человека с диабетом 1 типа.

**Как работает:** отправляешь фото еды → бот распознаёт продукты через Gemini AI → уточняет правильность → считает КБЖУ и хлебные единицы → ведёт дневник питания.

## Стек

- Python 3.11+ (async)
- python-telegram-bot
- Google Gemini 2.5 Flash (vision + text)
- SQLite (aiosqlite)

## Установка

```bash
git clone https://github.com/creatman-og/diabot.git
cd diabot
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или: venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
# Заполни .env своими токенами
python main.py
```

## Переменные окружения

| Переменная | Описание |
|-----------|----------|
| `TELEGRAM_TOKEN` | Токен бота от @BotFather |
| `GEMINI_API_KEY` | API ключ Google Gemini |
| `ALLOWED_USER_ID` | Telegram user ID (защита от посторонних) |
| `TIMEZONE` | Часовой пояс (по умолчанию Europe/Moscow) |
| `HE_GRAMS` | Граммов углеводов в 1 ХЕ (по умолчанию 12) |

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Приветствие и инструкция |
| `/help` | Подробная справка |
| `/today` | Дневник за сегодня |
| `/week` | Статистика за неделю |
| `/history N` | Последние N записей |
| `/undo` | Удалить последнюю запись |
| `/cancel` | Отменить текущее распознавание |

## Деплой (systemd)

```bash
sudo cp diabot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable diabot
sudo systemctl start diabot
```

---
<sub>*Сделано с заботой и вниманием к внутреннему миру человека.*</sub>
