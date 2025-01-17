from aiogram.dispatcher.filters.state import StatesGroup, State

class AddButtonState(StatesGroup):
    button_key = State()
    button_text = State()

class EditButtonState(StatesGroup):
    url = State()