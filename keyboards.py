from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup (
        inline_keyboard=[
            [InlineKeyboardButton(text="О проекте", callback_data="about")],
            [InlineKeyboardButton(text="Оставить заявку", callback_data="form")],
            [InlineKeyboardButton(text="Выход", callback_data="exit")]
        ]
    )

def yes_no():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data="yes")], 
            [InlineKeyboardButton(text="Нет", callback_data="no")]  
        ]
    )