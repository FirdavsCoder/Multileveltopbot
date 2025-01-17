from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton("📑 Real Exam Questions")
        ],
        [
            KeyboardButton("📽 General English Videos"),
            KeyboardButton("🖇 Grammar Lessons")
        ],
        [
            KeyboardButton("📚 Full Multi-Level Lessons"),
            KeyboardButton("🗄 Full IELTS Course")
        ],
        [
            KeyboardButton("📚 Useful Books"),
            KeyboardButton("📹 Reading Explanation Videos")
        ],
        [
            KeyboardButton("🎥 Recorded Video Lessons"),
            KeyboardButton("🗒 Topic Vocabulary")
        ],
        [
            KeyboardButton("🗃 Other Resources"),
            KeyboardButton("☎️ Contact Us")
        ]
    ]
)

real_exam_btn = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton("2023"),
            KeyboardButton("2024"),
            KeyboardButton("2025"),
        ],
        [
            KeyboardButton("🔙 Orqaga")
        ]
    ]
)

full_multilevel_btn = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton("Writing"),
            KeyboardButton("Speaking"),
        ],
        [
            KeyboardButton("Listening"),
            KeyboardButton("Reading"),
        ],
        [
            KeyboardButton("🔙 Orqaga")
        ]
    ]
)
