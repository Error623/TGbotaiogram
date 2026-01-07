from aiogram.fsm.state import State, StatesGroup

class Funnel(StatesGroup):
    waiting_decision = State()
    waiting_name = State()


class Survey(StatesGroup):
    name = State()
    phone = State()