"""English locale — bot messages and LLM prompts."""

LANG = "en"
LANG_NAME = "English"

# --- Onboarding ---
START_WELCOME = (
    "👋 Hi, {name}! I'm <b>DiaBot</b> — your personal assistant "
    "for counting carbs and calories from food photos.\n\n"
    "I'm here to help you keep track of your meals — "
    "just send a food photo and I'll recognize the items "
    "and calculate carbs and bread units.\n\n"
    "⚠️ I'm not a medical device. Always consult "
    "your doctor about insulin dosing.\n\n"
    "To work, I need to send your food photos "
    "to an AI service. Details: /privacy"
)
CONSENT_AGREE = "✅ I agree, let's start"
CONSENT_DETAILS = "📄 Details"
CONSENT_DETAILS_TEXT = (
    "🔒 <b>What I do with your data:</b>\n"
    "• Photos are sent to AI for recognition\n"
    "• Results are stored on the bot's server\n"
    "• Data is not shared with third parties\n"
    "• You can export or delete your data anytime\n\n"
    "Details: /privacy"
)
ONBOARDING_TIMEZONE = "🌍 What's your timezone?"
TZ_MOSCOW = "🇷🇺 Moscow"
TZ_EUROPE = "🇪🇺 Europe"
TZ_OTHER = "Other"
ONBOARDING_HE = (
    "⚙️ How many grams of carbs per 1 bread unit (BU)?\n"
    "(standard in Russia — 12 g, in some countries 10 g)"
)
HE_12 = "12 g (standard)"
HE_10 = "10 g"
HE_OTHER = "Other"
ONBOARDING_COMPLETE = (
    "✅ All set, {name}! Here's what I can do:\n\n"
    "📸 Send a food photo — I'll recognize and calculate nutrition\n"
    "✏️ Or type what you ate\n"
    "💉 \"Sugar\" — log a glucose reading\n"
    "📊 \"Today\" — daily diary\n\n"
    "Try it — send a food photo!"
)
ONBOARDING_HE_CUSTOM = "Enter grams of carbs per 1 bread unit (number):"
ONBOARDING_TZ_CUSTOM = "Enter your timezone (e.g. Europe/Berlin):"

# --- Main menu buttons ---
BTN_TODAY = "📊 Today"
BTN_WEEK = "📅 Week"
BTN_SUGAR = "💉 Sugar"
BTN_MENU = "⚙️ Menu"
BTN_HISTORY = "📋 History"
BTN_UNDO = "↩️ Undo"
BTN_PRIVACY = "🔒 Privacy"
BTN_HELP = "❓ Help"
BTN_BACK = "◀️ Back"

# --- Inline buttons ---
BTN_CONFIRM = "✅ Correct"
BTN_CANCEL = "❌ Cancel"

# --- Recognition ---
ANALYZING = "⏳ One moment, {name}, let me take a look..."
RECOGNITION_HEADER = "🔍 {name}, I see:"
RECOGNITION_HEADER_TEXT = "🔍 {name}, I think:"
RECOGNITION_CONFIRM = "All correct? Tap ✅ or tell me what to fix."
RECOGNITION_UPDATED = "🔍 Updated list:"
RECOGNITION_NO_FOOD = "🤔 {name}, I don't see food in the photo. Send a photo of a plate or describe what you ate."
RECOGNITION_FAILED = "⚠️ Couldn't recognize the food, try another photo or describe it in text."

# --- Calculation ---
CALCULATION_HEADER = "🍽 Nutrition breakdown:"
CALCULATION_SAVED = "📝 Saved, {name}!"
CALCULATION_TODAY_SUMMARY = "Today: {calories} kcal | {he} BU"

# --- Diary ---
DIARY_HEADER = "📊 Diary for {date}:"
DIARY_EMPTY = "📭 No entries for {date}."
DIARY_TOTAL = "TOTAL for the day:"
WEEK_HEADER = "📅 Weekly stats:"
WEEK_EMPTY = "📭 No entries for the past week."
HISTORY_HEADER = "📋 Last {n} entries:"
HISTORY_EMPTY = "📭 No entries yet."
UNDO_SUCCESS = "↩️ Last entry deleted."
UNDO_NOTHING = "📭 {name}, nothing to undo."

# --- Glucose ---
GLUCOSE_PROMPT = "💉 {name}, enter your blood sugar reading (mmol/L):"
GLUCOSE_SAVED = "💉 Saved: {value} mmol/L 👍"
GLUCOSE_INVALID = "⚠️ Enter a number, e.g.: 5.8"

# --- Privacy ---
PRIVACY_TEXT = (
    "🔒 <b>Privacy</b>\n\n"
    "• Food photos are sent to an AI service for recognition\n"
    "• Results are stored on the bot's server\n"
    "• Photos are NOT saved to disk\n"
    "• Data is not shared with third parties\n\n"
    "<b>Commands:</b>\n"
    "/export — download all your data\n"
    "/delete_my_data — delete all your data"
)
EXPORT_EMPTY = "📭 No data to export."
DELETE_CONFIRM = "⚠️ Are you sure? This will permanently delete ALL your data."
DELETE_YES = "Yes, delete"
DELETE_NO = "No, cancel"
DELETE_DONE = "✅ All data deleted."

# --- Admin ---
ADMIN_USER_ADDED = "✅ User {user_id} added."
ADMIN_USER_REMOVED = "✅ User {user_id} removed."
ADMIN_USER_LIST = "👥 Allowed users:\n{users}"
ADMIN_USER_LIST_EMPTY = "📭 List is empty (admins only)."
ADMIN_ONLY = "🔒 This command is for administrators only."
ADMIN_BTN_ADD_USER = "➕ Add user"
ADMIN_BTN_LIST_USERS = "👥 Users"
ADMIN_ADD_PROMPT = "Enter Telegram user ID to add:"
ADMIN_REMOVE_PROMPT = "Enter Telegram user ID to remove:"

# --- Access requests ---
ACCESS_REQUEST_WELCOME = (
    "👋 Hi, {name}! I'm <b>DiaBot</b> — a helper for counting "
    "carbs and calories from food photos.\n\n"
    "This is a personal bot. You need admin approval to use it."
)
ACCESS_REQUEST_BTN = "📨 Request access"
ACCESS_REQUEST_SENT = "📨 Request sent! The admin will review it shortly."
ACCESS_REQUEST_PENDING = "⏳ Your request is already pending. Please wait for admin approval."
ACCESS_REQUEST_APPROVED = "🎉 {name}, your request has been approved! Type /start to begin."
ACCESS_REQUEST_REJECTED = "😔 Unfortunately, your request has been declined."
ADMIN_NEW_REQUEST = (
    "📨 <b>New access request</b>\n\n"
    "👤 Name: {first_name}\n"
    "📝 Username: @{username}\n"
    "🆔 ID: <code>{user_id}</code>"
)
ADMIN_APPROVE = "✅ Approve"
ADMIN_REJECT = "❌ Reject"
ADMIN_REQUEST_APPROVED = "✅ Request from {first_name} (ID: {user_id}) approved."
ADMIN_REQUEST_REJECTED = "❌ Request from {first_name} (ID: {user_id}) rejected."
ADMIN_REQUEST_ALREADY_HANDLED = "⚠️ This request has already been handled."
ADMIN_BTN_PENDING = "📨 Requests ({count})"
ADMIN_PENDING_HEADER = "📨 <b>Pending requests:</b>\n"
ADMIN_PENDING_EMPTY = "📭 No pending requests."
ADMIN_USERS_HEADER = "👥 <b>Users with access:</b>\n"

# --- Errors ---
SERVICE_UNAVAILABLE = "⚠️ Service temporarily unavailable, try again in a minute."
RATE_LIMITED = "⏳ Too many requests. Try again in {minutes} min."
ACCESS_DENIED = "🔒 This is a personal bot. Ask the admin to add you."
UNSUPPORTED_MESSAGE = "📸 Send a food photo or type what you ate."
CANCELLED = "❌ Cancelled. I'm here if you need me."

# --- Help ---
HELP_TEXT = (
    "❓ <b>{name}, here's what I can do:</b>\n\n"
    "<b>Basics:</b>\n"
    "📸 Send a food photo — I'll recognize and calculate nutrition\n"
    "✏️ Type it out: \"pasta with chicken and salad\"\n"
    "📸+✏️ Photo with a caption works too\n\n"
    "<b>Commands:</b>\n"
    "/today — today's diary\n"
    "/week — weekly stats\n"
    "/history — recent entries\n"
    "/sugar — log blood sugar\n"
    "/undo — delete last entry\n"
    "/privacy — privacy and data\n"
    "/help — this help"
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

IMPORTANT: All text values (name, note) MUST be in English language."""

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

IMPORTANT: All text values (name) MUST be in English language."""

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

IMPORTANT: All text values (name, note) MUST be in English language."""

# --- Onboarding profile ---
ONBOARDING_GENDER = "👤 {name}, what's your gender?"
GENDER_FEMALE = "👩 Female"
GENDER_MALE = "👨 Male"
ONBOARDING_HEIGHT = "📏 What's your height (cm)?"
HEIGHT_155 = "155"
HEIGHT_160 = "160"
HEIGHT_165 = "165"
HEIGHT_170 = "170"
HEIGHT_175 = "175"
HEIGHT_OTHER = "Other"
ONBOARDING_WEIGHT = "⚖️ {name}, enter your weight in kg:"
ONBOARDING_AGE = "🎂 How old are you?"
ONBOARDING_TARGETS_SHOW = (
    "📊 {name}, based on your data, your daily targets:\n\n"
    "  Calories: {calories} kcal\n"
    "  Protein: {protein} g\n"
    "  Fat: {fat} g\n"
    "  Carbs: {carbs} g ({he} XE)\n\n"
    "All correct?"
)
TARGETS_CONFIRM = "✅ Confirm"
TARGETS_EDIT = "✏️ Edit"
ONBOARDING_TARGETS_EDIT = (
    "Enter your targets in format:\n"
    "<code>calories protein fat carbs</code>\n"
    "Example: <code>1800 65 60 225</code>"
)
ONBOARDING_TARGETS_INVALID = "⚠️ Enter 4 numbers separated by spaces: calories protein fat carbs"
ONBOARDING_HEIGHT_CUSTOM = "Enter your height in cm (number):"
ONBOARDING_WEIGHT_INVALID = "⚠️ Enter weight as a number, e.g.: 58 or 58.5"
ONBOARDING_AGE_INVALID = "⚠️ Enter age as a number, e.g.: 27"

# --- Settings ---
BTN_SETTINGS = "⚙️ Settings"
SETTINGS_HEADER = (
    "⚙️ <b>Settings</b>\n\n"
    "Timezone: {timezone}\n"
    "XE: {he_grams} g\n"
    "Gender: {gender} | Height: {height} | Weight: {weight} | Age: {age}\n\n"
    "<b>Daily targets:</b>\n"
    "  Calories: {calories} kcal\n"
    "  Protein: {protein} g\n"
    "  Fat: {fat} g\n"
    "  Carbs: {carbs} g"
)
SETTINGS_EDIT_TARGETS = "✏️ Edit targets"
SETTINGS_EDIT_PROFILE = "📏 Edit profile"
SETTINGS_SAVED = "✅ Settings saved!"
GENDER_DISPLAY_MALE = "Male"
GENDER_DISPLAY_FEMALE = "Female"
GENDER_DISPLAY_NONE = "—"

# --- Migration prompt ---
TARGETS_SETUP_PROMPT = (
    "{name}, I've added daily target tracking!\n"
    "Want to set up? Takes a minute."
)
TARGETS_SETUP_NOW = "📏 Set up"
TARGETS_SETUP_LATER = "⏭ Later"

# --- Progress labels ---
PROGRESS_LABELS_COMPACT = {"carbs": "C", "cal": "Cal", "protein": "P", "fat": "F", "xe": "XE", "g": "g"}
PROGRESS_LABELS_FULL = {"carbs": "Carbs", "xe": "XE", "cal": "Calories", "protein": "Protein", "fat": "Fat", "g": "g"}
